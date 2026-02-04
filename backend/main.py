from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from backend.database import (
    init_db, save_leads, create_run, update_run, get_latest_leads, 
    get_all_leads_for_report, get_recent_runs, get_existing_seia_projects,
    update_lead_estado, save_estado_change, get_recent_estado_changes,
    get_all_leads_for_markdown, clear_all_data
)
from datetime import datetime
from backend.auth import AuthMiddleware, verify_credentials, create_access_token, verify_token
from backend.report import generate_report_with_ai, send_email_report
from backend.config import EMAIL_TO, JWT_EXPIRATION_HOURS
from backend.scoring import get_top_proyectos
from backend.category_rules import CATEGORIAS, CATEGORIA_DEFAULT, CATEGORIA_DEFAULT_COLOR, CATEGORIA_DEFAULT_COLOR_NAME
import traceback
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import os

# Modelo para login
class LoginRequest(BaseModel):
    username: str
    password: str

# Importar scrapers explícitamente
from scrapers.seia.scraper import run_seia
from scrapers.hechos_esenciales.scraper import run_hechos_esenciales

# Definir dict de scrapers en main.py para legibilidad y debugging
SCRAPERS = {
    'seia': run_seia,
    'hechos_esenciales': run_hechos_esenciales,
}

# Variable global para almacenar el progreso de scrapers activos
scraper_progress = {}
# Variable global para controlar cancelación
scraper_cancel = {}
# Variable global para almacenar resultados de scrapers
scraper_results = {}
# Thread pool para ejecutar scrapers
executor = ThreadPoolExecutor(max_workers=2)

app = FastAPI(title="Master Scraper API")

# Configurar CORS para permitir frontend Next.js (local y producción)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://controlgastosjero.xyz",
    "https://www.controlgastosjero.xyz",
]
# Permitir origen adicional desde variable de entorno
extra_origin = os.getenv("CORS_ORIGIN")
if extra_origin:
    ALLOWED_ORIGINS.append(extra_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middleware de autenticación
from backend.config import API_SECRET
if API_SECRET:
    app.add_middleware(AuthMiddleware)
else:
    print("⚠️  WARNING: API_SECRET no configurado. La API está sin protección.")

# Inicializar base de datos al iniciar
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
async def root():
    """Endpoint raíz - información de la API."""
    return {"message": "Master Scraper API", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check para Docker/monitoreo."""
    return {"status": "healthy"}

@app.post("/login")
async def login(request: LoginRequest):
    """
    Endpoint de login - retorna JWT token si las credenciales son válidas.
    """
    if not verify_credentials(request.username, request.password):
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )
    
    token = create_access_token(request.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_hours": JWT_EXPIRATION_HOURS
    }

@app.get("/verify-token")
async def verify_token_endpoint():
    """
    Verifica si el token actual es válido.
    Si llega aquí sin error del middleware, el token es válido.
    """
    return {"valid": True}

def run_scraper_thread(source: str, run_id: int):
    """Ejecuta el scraper en un thread separado."""
    global scraper_progress, scraper_cancel, scraper_results
    
    try:
        # Función callback para actualizar progreso
        def update_progress(percent, message):
            scraper_progress[source] = {"percent": percent, "message": message}
        
        # Función callback para verificar cancelación
        def check_cancel():
            return scraper_cancel.get(source, False)
        
        # Ejecutar scraper con parámetros adicionales según el tipo
        scraper_func = SCRAPERS[source]
        
        estado_changes_count = 0
        
        if source == 'seia':
            # Obtener proyectos existentes con su estado actual
            existing_projects = get_existing_seia_projects()
            print(f"📊 Encontrados {len(existing_projects)} proyectos SEIA existentes en BD")
            
            # El scraper SEIA retorna {new_leads: [...], estado_changes: [...]}
            result = scraper_func(existing_projects=existing_projects, progress_callback=update_progress, cancel_callback=check_cancel)
            leads = result.get('new_leads', [])
            estado_changes = result.get('estado_changes', [])
            
            # Procesar cambios de estado
            for change in estado_changes:
                # Actualizar el lead existente con el nuevo estado
                update_lead_estado(
                    change['lead_id'],
                    change['estado_nuevo'],
                    change['raw_data']
                )
                # Registrar el cambio
                save_estado_change(
                    change['lead_id'],
                    change['codigo_seia'],
                    change['project_name'],
                    change['estado_anterior'],
                    change['estado_nuevo']
                )
            
            estado_changes_count = len(estado_changes)
            if estado_changes_count > 0:
                print(f"🔄 Se detectaron {estado_changes_count} cambios de estado")
        else:
            leads = scraper_func()
        
        # Verificar si fue cancelado
        if scraper_cancel.get(source, False):
            update_run(run_id, 'cancelled', len(leads) if isinstance(leads, list) else 0)
            scraper_progress[source] = {"percent": 0, "message": "Cancelado"}
            scraper_results[source] = {
                "status": "cancelled",
                "source": source,
                "total_leads": len(leads) if isinstance(leads, list) else 0,
                "run_id": run_id
            }
            return
        
        # Guardar leads nuevos en BD
        total_leads = save_leads(source, leads) if leads else 0
        
        # Actualizar run
        update_run(run_id, 'completed', total_leads)
        
        # Limpiar progreso
        scraper_progress[source] = {"percent": 100, "message": "Completado"}
        
        scraper_results[source] = {
            "status": "success",
            "source": source,
            "total_leads": total_leads,
            "estado_changes": estado_changes_count,
            "run_id": run_id
        }
    except Exception as e:
        # Actualizar run con error
        try:
            update_run(run_id, 'error', 0)
        except:
            pass
        
        # Limpiar progreso con error
        scraper_progress[source] = {"percent": 0, "message": f"Error: {str(e)}"}
        traceback.print_exc()
        
        scraper_results[source] = {
            "status": "error",
            "source": source,
            "error": str(e),
            "run_id": run_id
        }


@app.post("/scrape/{source}")
async def scrape_source(source: str):
    """
    Ejecuta un scraper específico en background y retorna inmediatamente.
    El progreso se puede consultar con GET /scrape-progress/{source}
    """
    global scraper_progress, scraper_cancel, scraper_results
    
    if source not in SCRAPERS:
        raise HTTPException(status_code=404, detail=f"Scraper '{source}' no encontrado")
    
    # Verificar si ya hay un scraper corriendo para esta fuente
    if source in scraper_progress and scraper_progress[source].get("percent", 0) > 0 and scraper_progress[source].get("percent", 0) < 100:
        return {"status": "already_running", "source": source, "progress": scraper_progress[source]}
    
    # Inicializar progreso y resetear cancelación
    scraper_progress[source] = {"percent": 0, "message": "Iniciando..."}
    scraper_cancel[source] = False
    scraper_results[source] = None
    
    # Crear registro de run
    run_id = create_run(source)
    
    # Ejecutar scraper en thread separado
    executor.submit(run_scraper_thread, source, run_id)
    
    # Retornar inmediatamente
    return {
        "status": "started",
        "source": source,
        "run_id": run_id,
        "message": "Scraper iniciado. Consulta /scrape-progress/{source} para ver el progreso."
    }


@app.post("/scrape-all")
async def scrape_all():
    """
    Ejecuta todos los scrapers disponibles.
    """
    results = []
    total_leads_all = 0
    errors = []
    
    for source, scraper_func in SCRAPERS.items():
        try:
            # Crear registro de run
            run_id = create_run(source)
            
            # Ejecutar scraper
            leads = scraper_func()
            
            # Guardar leads en BD
            total_leads = save_leads(source, leads)
            total_leads_all += total_leads
            
            # Actualizar run
            update_run(run_id, 'completed', total_leads)
            
            results.append({
                "source": source,
                "status": "success",
                "total_leads": total_leads,
                "run_id": run_id
            })
        except Exception as e:
            try:
                update_run(run_id, 'error', 0)
            except:
                pass
            
            error_detail = str(e)
            traceback.print_exc()
            errors.append({
                "source": source,
                "error": error_detail
            })
            results.append({
                "source": source,
                "status": "error",
                "error": error_detail
            })
    
    return {
        "status": "success" if not errors else "partial",
        "results": results,
        "total_leads": total_leads_all,
        "errors": errors
    }


@app.post("/report")
async def generate_report():
    """
    Genera reporte con IA y lo envía por email.
    """
    try:
        # Obtener leads recientes
        leads = get_all_leads_for_report()
        
        if not leads:
            return {
                "status": "error",
                "message": "No hay leads disponibles para generar reporte"
            }
        
        # Generar reporte con IA
        report = generate_report_with_ai(leads)
        
        if report.startswith("Error"):
            return {
                "status": "error",
                "message": report
            }
        
        # Enviar por email
        email_sent = False
        if EMAIL_TO:
            email_sent = send_email_report(report, EMAIL_TO)
        
        return {
            "status": "success",
            "email_sent": email_sent,
            "report_preview": report[:500] + "..." if len(report) > 500 else report
        }
    except Exception as e:
        error_detail = str(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {error_detail}")


@app.get("/leads")
async def get_leads(
    limit: int = Query(10000, ge=1, le=50000)
):
    """
    Obtiene los leads recientes.
    Sin límite práctico (hasta 50,000 para evitar problemas de memoria).
    """
    try:
        leads = get_latest_leads(limit)
        return {
            "leads": leads,
            "total": len(leads)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener leads: {str(e)}")


@app.get("/runs")
async def get_runs(limit: int = Query(10, ge=1, le=100)):
    """
    Obtiene el historial de ejecuciones de scrapers.
    """
    try:
        runs = get_recent_runs(limit)
        return {
            "runs": runs,
            "total": len(runs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener runs: {str(e)}")


@app.get("/scrape-progress/{source}")
async def get_scrape_progress(source: str):
    """
    Obtiene el progreso actual de un scraper en ejecución.
    """
    progress = scraper_progress.get(source, {"percent": 0, "message": "No hay scraper en ejecución"})
    result = scraper_results.get(source)
    
    # Si hay resultado, incluirlo en la respuesta
    if result:
        return {**progress, "result": result}
    
    return progress


@app.post("/scrape-cancel/{source}")
async def cancel_scrape(source: str):
    """
    Cancela un scraper en ejecución.
    """
    global scraper_cancel
    scraper_cancel[source] = True
    return {"status": "cancelled", "source": source}


@app.get("/estado-changes")
async def get_estado_changes(limit: int = Query(20, ge=1, le=100)):
    """
    Obtiene los cambios de estado recientes de proyectos SEIA.
    """
    try:
        changes = get_recent_estado_changes(limit)
        return {
            "changes": changes,
            "total": len(changes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cambios de estado: {str(e)}")


@app.get("/export/markdown")
async def export_markdown():
    """
    Genera y retorna un reporte completo en formato Markdown para análisis con ChatGPT.
    """
    try:
        leads = get_all_leads_for_markdown()
        estado_changes = get_recent_estado_changes(50)
        top_projects = get_top_proyectos(leads, 20)
        
        # Generar el contenido Markdown
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"""# Reporte Master Scraper
**Generado:** {now}

---

## Resumen Ejecutivo

- **Total de proyectos:** {len(leads)}
- **Cambios de estado recientes:** {len(estado_changes)}
- **Top proyectos seleccionados:** {len(top_projects)}

"""
        
        # Sección TOP 20 PROYECTOS
        if top_projects:
            md_content += """---

## Top 20 Proyectos Más Relevantes

Proyectos seleccionados según criterios de:
- Estado del proyecto (En Calificación, Admitido a Tramitación, Aprobado)
- Monto de inversión (>= USD 25 MM, o >= USD 10 MM para BESS/Infra. Eléctrica/Minería)
- Scoring por inversión y estado

| # | Proyecto | Score | Inversión (USD MM) | Estado | Industria | Explicación |
|---|----------|-------|-------------------|--------|-----------|-------------|
"""
            for p in top_projects:
                raw = p.get('raw_data', {})
                inv = raw.get('inversion_millones', 'N/A')
                inv_str = f"{inv:,.1f}" if isinstance(inv, (int, float)) else str(inv)
                md_content += f"| {p['ranking']} | {p['project_name'][:40]}... | {p['score_total']} | {inv_str} | {raw.get('estado', 'N/A')[:20]} | {raw.get('industria', 'N/A')} | {p.get('explicacion', '')} |\n"
            
            md_content += "\n### Detalle de Top 20 Proyectos\n\n"
            
            for p in top_projects:
                raw = p.get('raw_data', {})
                md_content += f"""#### {p['ranking']}. {p['project_name']}

- **Score Total:** {p['score_total']} (Inversión: {p.get('score_inversion', 0)}, Estado: {p.get('score_estado', 0)})
- **Explicación:** {p.get('explicacion', 'N/A')}
"""
                if raw.get('titular'):
                    md_content += f"- **Titular:** {raw['titular']}\n"
                if raw.get('region'):
                    md_content += f"- **Región:** {raw['region']}"
                    if raw.get('comuna'):
                        md_content += f", {raw['comuna']}"
                    md_content += "\n"
                if raw.get('inversion_millones'):
                    md_content += f"- **Inversión:** US$ {raw['inversion_millones']:,.2f} MM\n"
                if raw.get('estado'):
                    md_content += f"- **Estado:** {raw['estado']}\n"
                if raw.get('industria'):
                    md_content += f"- **Industria:** {raw['industria']}\n"
                if raw.get('categorias_secundarias'):
                    md_content += f"- **Categorías secundarias:** {', '.join(raw['categorias_secundarias'])}\n"
                if raw.get('tipo'):
                    md_content += f"- **Tipo:** {raw['tipo']}\n"
                if raw.get('link_ficha'):
                    md_content += f"- **Link SEIA:** {raw['link_ficha']}\n"
                if raw.get('descripcion_completa'):
                    desc = raw['descripcion_completa'][:500] + "..." if len(raw.get('descripcion_completa', '')) > 500 else raw.get('descripcion_completa', '')
                    md_content += f"\n**Descripción:** {desc}\n"
                md_content += "\n"
        
        # Sección de cambios de estado
        if estado_changes:
            md_content += """---

## Cambios de Estado Recientes (Proyectos SEIA)

| Proyecto | Estado Anterior | Estado Nuevo | Fecha Detección |
|----------|-----------------|--------------|-----------------|
"""
            for change in estado_changes:
                is_aprobado = "✅ " if change.get('is_aprobado') else ""
                md_content += f"| {change['project_name'][:50]}... | {change['estado_anterior']} | {is_aprobado}{change['estado_nuevo']} | {change['detected_at']} |\n"
            
            md_content += "\n"
        
        # Agrupar leads por fuente
        leads_by_source = {}
        for lead in leads:
            source = lead['source'].upper()
            if source not in leads_by_source:
                leads_by_source[source] = []
            leads_by_source[source].append(lead)
        
        # Generar sección para cada fuente
        for source, source_leads in leads_by_source.items():
            md_content += f"""---

## Proyectos {source}

**Total:** {len(source_leads)} proyectos

"""
            for i, lead in enumerate(source_leads, 1):
                raw = lead.get('raw_data', {})
                
                md_content += f"""### {i}. {lead['project_name']}

"""
                
                # Información básica
                if raw.get('titular'):
                    md_content += f"- **Titular:** {raw['titular']}\n"
                if raw.get('region'):
                    md_content += f"- **Región:** {raw['region']}"
                    if raw.get('comuna'):
                        md_content += f", {raw['comuna']}"
                    md_content += "\n"
                if raw.get('inversion_millones'):
                    md_content += f"- **Inversión:** US$ {raw['inversion_millones']:,.2f} MM\n"
                if raw.get('estado'):
                    md_content += f"- **Estado:** {raw['estado']}\n"
                if raw.get('industria'):
                    md_content += f"- **Industria:** {raw['industria']}\n"
                if raw.get('categorias_secundarias'):
                    md_content += f"- **Categorías secundarias:** {', '.join(raw['categorias_secundarias'])}\n"
                if lead.get('date'):
                    md_content += f"- **Fecha Presentación:** {lead['date']}\n"
                if raw.get('tipo'):
                    md_content += f"- **Tipo:** {raw['tipo']}\n"
                if raw.get('codigo_seia'):
                    md_content += f"- **Código SEIA:** {raw['codigo_seia']}\n"
                if raw.get('link_ficha'):
                    md_content += f"- **Link SEIA:** {raw['link_ficha']}\n"
                
                # Descripción completa
                if raw.get('descripcion_completa'):
                    md_content += f"\n**Descripción del Proyecto:**\n\n{raw['descripcion_completa']}\n"
                
                md_content += "\n---\n\n"
        
        # Agregar instrucciones para ChatGPT al final
        md_content += """
## Instrucciones para Análisis

Este reporte contiene información de proyectos de inversión en Chile. Por favor analiza:

1. **Top 20 proyectos** más relevantes según el scoring automatizado
2. **Distribución por industria** (BESS, Energía Renovable, Minería, Infraestructura Eléctrica, etc.)
3. **Distribución geográfica** por región
4. **Cambios de estado** recientes, especialmente aprobaciones
5. **Tendencias** y patrones observados
6. **Oportunidades de negocio** potenciales

Genera un informe ejecutivo con los hallazgos más importantes.
"""
        
        # Retornar como archivo descargable
        filename = f"master_scraper_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        return StreamingResponse(
            iter([md_content]),
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/markdown; charset=utf-8"
            }
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")


@app.delete("/clear-all")
async def clear_all():
    """
    Elimina todos los datos de leads, runs y estado_changes.
    Requiere confirmación previa en el frontend.
    """
    try:
        result = clear_all_data()
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al limpiar datos: {str(e)}")


@app.get("/top-projects")
async def get_top_projects(limit: int = Query(20, ge=1, le=50)):
    """
    Obtiene los top N proyectos más relevantes según el scoring.
    """
    try:
        leads = get_all_leads_for_markdown()
        top_projects = get_top_proyectos(leads, limit)
        return {
            "projects": top_projects,
            "total": len(top_projects)
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener top proyectos: {str(e)}")


@app.get("/category-colors")
async def get_category_colors():
    """
    Obtiene los colores de todas las categorías para el frontend.
    """
    colors = {}
    for cat, config in CATEGORIAS.items():
        colors[cat] = {
            "color": config["color"],
            "color_name": config["color_name"]
        }
    colors[CATEGORIA_DEFAULT] = {
        "color": CATEGORIA_DEFAULT_COLOR,
        "color_name": CATEGORIA_DEFAULT_COLOR_NAME
    }
    return colors


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
