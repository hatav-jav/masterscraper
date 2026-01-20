from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.database import init_db, save_leads, create_run, update_run, get_latest_leads, get_all_leads_for_report
from backend.auth import AuthMiddleware
from backend.report import generate_report_with_ai, send_email_report
from backend.config import EMAIL_TO
import traceback

# Importar scrapers explícitamente
from scrapers.seia.scraper import run_seia
from scrapers.hechos_esenciales.scraper import run_hechos_esenciales

# Definir dict de scrapers en main.py para legibilidad y debugging
SCRAPERS = {
    'seia': run_seia,
    'hechos_esenciales': run_hechos_esenciales,
}

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
def root():
    return {"message": "Master Scraper API", "version": "1.0.0"}

@app.post("/scrape/{source}")
async def scrape_source(source: str):
    """
    Ejecuta un scraper específico.
    """
    if source not in SCRAPERS:
        raise HTTPException(status_code=404, detail=f"Scraper '{source}' no encontrado")
    
    try:
        # Crear registro de run
        run_id = create_run(source)
        
        # Ejecutar scraper
        scraper_func = SCRAPERS[source]
        leads = scraper_func()
        
        # Guardar leads en BD
        total_leads = save_leads(source, leads)
        
        # Actualizar run
        update_run(run_id, 'completed', total_leads)
        
        return {
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
        
        error_detail = str(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al ejecutar scraper: {error_detail}")

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
async def get_leads(limit: int = 100):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

