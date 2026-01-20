"""
Scraper para SEIA (Sistema de Evaluación de Impacto Ambiental).
Reutiliza código del proyecto SEIA Scraper original.
"""
import time
from typing import List, Dict
import requests

# Variable global para controlar si ya esperamos los 15 segundos iniciales
_PRIMERA_EJECUCION = True


def fetch_datos_listado(pagina: int = 1, registros_por_pagina: int = 10) -> dict:
    """
    Obtiene los datos del listado de proyectos del SEIA desde el endpoint API.
    """
    global _PRIMERA_EJECUCION
    
    # ESPERA OBLIGATORIA DE 15 SEGUNDOS antes de la primera request
    if _PRIMERA_EJECUCION:
        print("⏳ Esperando 15 segundos para permitir renderizado completo del sitio...")
        time.sleep(15)
        _PRIMERA_EJECUCION = False
    
    url = "https://seia.sea.gob.cl/busqueda/buscarProyectoResumenAction.php"
    
    start = (pagina - 1) * registros_por_pagina
    offset = (start / 10) + 1
    
    data = {
        'nombre': '',
        'titular': '',
        'folio': '',
        'selectRegion': '',
        'selectComuna': '',
        'tipoPresentacion': '',
        'projectStatus': '',
        'PresentacionMin': '',
        'PresentacionMax': '',
        'CalificaMin': '',
        'CalificaMax': '',
        'sectores_economicos': '',
        'razoningreso': '',
        'id_tipoexpediente': '',
        'offset': offset,
        'limit': registros_por_pagina,
        'orderColumn': 'FECHA_PRESENTACION',
        'orderDir': 'DESC'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://seia.sea.gob.cl/busqueda/buscarProyectoResumen.php',
        'Origin': 'https://seia.sea.gob.cl'
    }
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al obtener datos del API: {e}")
    except ValueError as e:
        raise Exception(f"Error al parsear JSON: {e}. Respuesta: {response.text[:500]}")


def parse_listado_json(datos_json: dict) -> List[Dict[str, str]]:
    """
    Parsea los datos JSON del endpoint del SEIA y extrae información de proyectos.
    """
    proyectos = []
    
    if not datos_json or 'data' not in datos_json:
        return proyectos
    
    for proyecto_raw in datos_json['data']:
        proyecto = {
            'nombre': proyecto_raw.get('EXPEDIENTE_NOMBRE', ''),
            'link': proyecto_raw.get('EXPEDIENTE_URL_PPAL', ''),
            'titular': proyecto_raw.get('TITULAR', ''),
            'tipo': proyecto_raw.get('WORKFLOW_DESCRIPCION', ''),
            'region': proyecto_raw.get('REGION_NOMBRE', ''),
            'comuna': proyecto_raw.get('COMUNA_NOMBRE', ''),
            'inversion': proyecto_raw.get('INVERSION_MM', ''),
            'inversion_formato': proyecto_raw.get('INVERSION_MM_FORMAT', ''),
            'inversion_millones': _parse_inversion_millones(proyecto_raw.get('INVERSION_MM_FORMAT', '')),
            'fecha_presentacion': proyecto_raw.get('FECHA_PRESENTACION_FORMAT', '') or proyecto_raw.get('FECHA_PRESENTACION', ''),
            'fecha_ingreso': proyecto_raw.get('FECHA_INGRESO_FORMAT', '') or proyecto_raw.get('FECHA_INGRESO', ''),
            'fecha_presentacion_timestamp': proyecto_raw.get('FECHA_PRESENTACION', ''),
            'fecha_ingreso_timestamp': proyecto_raw.get('FECHA_INGRESO', ''),
            'link_ficha': proyecto_raw.get('EXPEDIENTE_URL_FICHA', ''),
            'estado': proyecto_raw.get('ESTADO_PROYECTO', ''),
            'tipo_proyecto': proyecto_raw.get('TIPO_PROYECTO', ''),
            'razon_ingreso': proyecto_raw.get('RAZON_INGRESO', ''),
            'codigo_seia': proyecto_raw.get('EXPEDIENTE_ID', '') or proyecto_raw.get('FOLIO', ''),
        }
        
        # Asegurar que el link sea absoluto
        if proyecto['link'] and not proyecto['link'].startswith('http'):
            if proyecto['link'].startswith('/'):
                proyecto['link'] = f"https://seia.sea.gob.cl{proyecto['link']}"
            else:
                proyecto['link'] = f"https://seia.sea.gob.cl/{proyecto['link']}"
        
        proyectos.append(proyecto)
    
    return proyectos


def _parse_inversion_millones(inversion_str: str):
    """Parsea el formato de inversión del SEIA a millones de dólares."""
    if not inversion_str or not isinstance(inversion_str, str):
        return None
    
    try:
        inversion_limpia = inversion_str.replace(',', '.')
        return float(inversion_limpia)
    except (ValueError, TypeError):
        return None


def run_seia() -> List[Dict]:
    """
    Ejecuta el scraper de SEIA.
    Retorna lista de dicts con campos: source, project_name, date, sector, description, raw_data
    """
    print("🔄 Iniciando scraper SEIA...")
    
    proyectos = []
    pagina = 1
    max_paginas = 10  # Limitar a 10 páginas para no tardar mucho
    
    try:
        while pagina <= max_paginas:
            print(f"📄 Obteniendo página {pagina}...")
            
            datos = fetch_datos_listado(pagina=pagina, registros_por_pagina=10)
            proyectos_pagina = parse_listado_json(datos)
            
            if not proyectos_pagina:
                print(f"⚠️  No se encontraron proyectos en la página {pagina}.")
                break
            
            proyectos.extend(proyectos_pagina)
            print(f"✅ Página {pagina}: {len(proyectos_pagina)} proyectos obtenidos")
            
            pagina += 1
            time.sleep(1)  # Pausa entre páginas
        
        print(f"✅ Scraping SEIA completado: {len(proyectos)} proyectos obtenidos")
        
        # Normalizar salida al formato estándar del hub
        leads = []
        for proyecto in proyectos:
            lead = {
                'source': 'SEIA',
                'project_name': proyecto.get('nombre', 'Sin nombre'),
                'date': proyecto.get('fecha_presentacion', ''),
                'sector': proyecto.get('tipo_proyecto', proyecto.get('tipo', '')),
                'description': f"Titular: {proyecto.get('titular', 'N/A')}. Región: {proyecto.get('region', 'N/A')}, {proyecto.get('comuna', 'N/A')}. Inversión: {proyecto.get('inversion_formato', 'N/A')}. Estado: {proyecto.get('estado', 'N/A')}.",
                'raw_data': proyecto  # Guardar todos los datos originales
            }
            leads.append(lead)
        
        return leads
        
    except Exception as e:
        print(f"❌ Error en scraper SEIA: {e}")
        raise

