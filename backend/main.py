from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from backend.database import init_db, save_leads, create_run, update_run, get_latest_leads, get_all_leads_for_report, get_recent_runs, get_existing_seia_codes
from backend.auth import AuthMiddleware
from backend.report import generate_report_with_ai, send_email_report
from backend.config import EMAIL_TO
import traceback
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

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

# Configurar CORS para permitir frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
        
        if source == 'seia':
            # Obtener códigos existentes para evitar duplicados
            existing_codes = get_existing_seia_codes()
            print(f"📊 Encontrados {len(existing_codes)} proyectos SEIA existentes en BD")
            leads = scraper_func(existing_codes=existing_codes, progress_callback=update_progress, cancel_callback=check_cancel)
        else:
            leads = scraper_func()
        
        # Verificar si fue cancelado
        if scraper_cancel.get(source, False):
            update_run(run_id, 'cancelled', len(leads))
            scraper_progress[source] = {"percent": 0, "message": "Cancelado"}
            scraper_results[source] = {
                "status": "cancelled",
                "source": source,
                "total_leads": len(leads),
                "run_id": run_id
            }
            return
        
        # Guardar leads en BD
        total_leads = save_leads(source, leads)
        
        # Actualizar run
        update_run(run_id, 'completed', total_leads)
        
        # Limpiar progreso
        scraper_progress[source] = {"percent": 100, "message": "Completado"}
        
        scraper_results[source] = {
            "status": "success",
            "source": source,
            "total_leads": total_leads,
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
    limit: int = Query(500, ge=1, le=1000)
):
    """
    Obtiene los leads recientes.
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
