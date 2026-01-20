"""
Scraper para SEIA (Sistema de Evaluación de Impacto Ambiental).
Reutiliza código del proyecto SEIA Scraper original.
"""
import time
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

# Variable global para controlar si ya esperamos los 15 segundos iniciales
_PRIMERA_EJECUCION = True

# Mapeo de sectores económicos a industrias
SECTOR_TO_INDUSTRIA = {
    'ACUICULTURA': 'Acuicultura',
    'AGROINDUSTRIA': 'Agroindustria',
    'EQUIPAMIENTO': 'Infraestructura',
    'ENERGÍA': 'Energía',
    'FORESTAL': 'Forestal',
    'INFRAESTRUCTURA DE TRANSPORTE': 'Infraestructura',
    'INFRAESTRUCTURA HIDRÁULICA': 'Agua',
    'INFRAESTRUCTURA PORTUARIA': 'Puertos',
    'INSTALACIONES FABRILES': 'Industrial',
    'MINERÍA': 'Minería',
    'PESCA': 'Pesca',
    'SANEAMIENTO AMBIENTAL': 'Saneamiento',
    'OTROS': 'Otros',
}


def fetch_datos_listado(pagina: int = 1, registros_por_pagina: int = 100) -> dict:
    """
    Obtiene los datos del listado de proyectos del SEIA desde el endpoint API.
    Por defecto obtiene 100 registros por página para mayor eficiencia.
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


def fetch_descripcion_proyecto(url_ficha: str) -> str:
    """
    Obtiene la descripción completa del proyecto desde la ficha del SEIA.
    """
    if not url_ficha:
        return ""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(url_ficha, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        descripcion = ""
        
        # Método 1: Buscar en tablas con "Descripción del Proyecto" o similar
        for td in soup.find_all('td'):
            texto_td = td.get_text(strip=True).lower()
            if 'descripción del proyecto' in texto_td or 'descripcion del proyecto' in texto_td:
                # Buscar el siguiente td o el contenido después
                next_td = td.find_next_sibling('td')
                if next_td:
                    descripcion = next_td.get_text(strip=True)
                    break
                # O buscar en la siguiente fila
                parent_tr = td.find_parent('tr')
                if parent_tr:
                    next_tr = parent_tr.find_next_sibling('tr')
                    if next_tr:
                        descripcion = next_tr.get_text(strip=True)
                        break
        
        # Método 2: Buscar div o span con clase/id relacionado a descripción
        if not descripcion:
            for selector in ['#descripcion', '#descripcionProyecto', '.descripcion', '.descripcion-proyecto']:
                elem = soup.select_one(selector)
                if elem:
                    descripcion = elem.get_text(strip=True)
                    break
        
        # Método 3: Buscar por texto en headers
        if not descripcion:
            for header in soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'th']):
                header_text = header.get_text(strip=True).lower()
                if 'descripción' in header_text and 'proyecto' in header_text:
                    # Buscar el contenido que sigue
                    next_elem = header.find_next(['p', 'div', 'td', 'span'])
                    if next_elem:
                        descripcion = next_elem.get_text(strip=True)
                        break
        
        # Método 4: Buscar en cualquier elemento que contenga mucho texto después de "Descripción"
        if not descripcion:
            page_text = soup.get_text()
            if 'Descripción del Proyecto' in page_text:
                idx = page_text.find('Descripción del Proyecto')
                # Tomar el texto después del título
                texto_despues = page_text[idx + len('Descripción del Proyecto'):idx + 6000]
                # Limpiar y tomar hasta el siguiente título o sección
                lineas = texto_despues.strip().split('\n')
                descripcion_lineas = []
                for linea in lineas:
                    linea = linea.strip()
                    if linea and len(linea) > 10:
                        # Detener si encontramos otro título de sección
                        if any(titulo in linea for titulo in ['Ubicación', 'Localización', 'Titular', 'Inversión', 'Superficie']):
                            break
                        descripcion_lineas.append(linea)
                    if len(descripcion_lineas) >= 10:  # Máximo 10 líneas
                        break
                descripcion = ' '.join(descripcion_lineas)
        
        # Limpiar descripción
        if descripcion:
            # Remover espacios múltiples
            import re
            descripcion = re.sub(r'\s+', ' ', descripcion).strip()
        
        return descripcion[:5000] if descripcion else ""  # Limitar a 5000 caracteres
        
    except Exception as e:
        print(f"⚠️ Error al obtener descripción de {url_ficha}: {e}")
        return ""


def _parse_inversion_millones(inversion_str: str):
    """Parsea el formato de inversión del SEIA a millones de dólares."""
    if not inversion_str or not isinstance(inversion_str, str):
        return None
    
    try:
        inversion_limpia = inversion_str.replace(',', '.')
        return float(inversion_limpia)
    except (ValueError, TypeError):
        return None


def _determinar_industria(sector_economico: str, tipo_proyecto: str) -> str:
    """
    Determina la industria del proyecto basándose en el sector económico y tipo.
    """
    sector_upper = (sector_economico or '').upper()
    tipo_upper = (tipo_proyecto or '').upper()
    
    # Buscar en el mapeo de sectores
    for key, industria in SECTOR_TO_INDUSTRIA.items():
        if key in sector_upper or key in tipo_upper:
            return industria
    
    # Heurísticas adicionales basadas en palabras clave
    texto = f"{sector_economico} {tipo_proyecto}".upper()
    
    if any(word in texto for word in ['MINER', 'COBRE', 'ORO', 'LITIO', 'PLATA']):
        return 'Minería'
    if any(word in texto for word in ['ENERGIA', 'SOLAR', 'EÓLICO', 'HIDRO', 'TERMO', 'GAS']):
        return 'Energía'
    if any(word in texto for word in ['AGUA', 'DESALADORA', 'HIDRÁULICA', 'RIEGO']):
        return 'Agua'
    if any(word in texto for word in ['PUERTO', 'TERMINAL', 'MARITIMO', 'PORTUARIO']):
        return 'Puertos'
    if any(word in texto for word in ['CARRETERA', 'CAMINO', 'PUENTE', 'TÚNEL', 'VIAL']):
        return 'Infraestructura'
    if any(word in texto for word in ['INMOBILIARIO', 'VIVIENDA', 'EDIFICIO']):
        return 'Inmobiliario'
    
    return 'Otros'


def parse_listado_json(datos_json: dict) -> List[Dict[str, str]]:
    """
    Parsea los datos JSON del endpoint del SEIA y extrae información de proyectos.
    """
    proyectos = []
    
    if not datos_json or 'data' not in datos_json:
        return proyectos
    
    for proyecto_raw in datos_json['data']:
        sector_economico = proyecto_raw.get('SECTOR_ECONOMICO', '') or proyecto_raw.get('TIPO_PROYECTO', '')
        tipo_proyecto = proyecto_raw.get('TIPO_PROYECTO', '')
        
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
            'tipo_proyecto': tipo_proyecto,
            'sector_economico': sector_economico,
            'razon_ingreso': proyecto_raw.get('RAZON_INGRESO', ''),
            'codigo_seia': proyecto_raw.get('EXPEDIENTE_ID', '') or proyecto_raw.get('FOLIO', ''),
            'industria': _determinar_industria(sector_economico, tipo_proyecto),
        }
        
        # Asegurar que el link sea absoluto
        if proyecto['link'] and not proyecto['link'].startswith('http'):
            if proyecto['link'].startswith('/'):
                proyecto['link'] = f"https://seia.sea.gob.cl{proyecto['link']}"
            else:
                proyecto['link'] = f"https://seia.sea.gob.cl/{proyecto['link']}"
        
        proyectos.append(proyecto)
    
    return proyectos


def run_seia(obtener_descripcion: bool = True) -> List[Dict]:
    """
    Ejecuta el scraper de SEIA.
    Retorna lista de dicts con campos: source, project_name, date, sector, description, raw_data
    
    Args:
        obtener_descripcion: Si es True, obtiene la descripción completa de cada proyecto (más lento pero más info)
    """
    print("🔄 Iniciando scraper SEIA...")
    
    proyectos = []
    pagina = 1
    max_proyectos = 20  # Máximo de proyectos a obtener
    registros_por_pagina = 100  # 100 proyectos por página para mayor eficiencia
    
    try:
        while len(proyectos) < max_proyectos:
            print(f"📄 Obteniendo página {pagina} ({registros_por_pagina} proyectos por página)...")
            
            datos = fetch_datos_listado(pagina=pagina, registros_por_pagina=registros_por_pagina)
            proyectos_pagina = parse_listado_json(datos)
            
            if not proyectos_pagina:
                print(f"⚠️  No se encontraron proyectos en la página {pagina}.")
                break
            
            proyectos.extend(proyectos_pagina)
            print(f"✅ Página {pagina}: {len(proyectos_pagina)} proyectos obtenidos (total: {len(proyectos)})")
            
            # Si obtuvimos menos de lo esperado, ya no hay más páginas
            if len(proyectos_pagina) < registros_por_pagina:
                break
            
            # Si ya tenemos suficientes, detener
            if len(proyectos) >= max_proyectos:
                proyectos = proyectos[:max_proyectos]
                break
            
            pagina += 1
            time.sleep(0.5)  # Pausa entre páginas
        
        print(f"✅ Scraping SEIA completado: {len(proyectos)} proyectos obtenidos")
        
        # Opcionalmente obtener descripción completa de cada proyecto
        if obtener_descripcion:
            print("📝 Obteniendo descripciones detalladas de proyectos...")
            for i, proyecto in enumerate(proyectos):
                if proyecto.get('link_ficha'):
                    print(f"  📄 Obteniendo descripción {i+1}/{len(proyectos)}...")
                    descripcion = fetch_descripcion_proyecto(proyecto['link_ficha'])
                    proyecto['descripcion_completa'] = descripcion
                    time.sleep(0.3)  # Pausa entre requests
        
        # Normalizar salida al formato estándar del hub
        leads = []
        for proyecto in proyectos:
            lead = {
                'source': 'SEIA',
                'project_name': proyecto.get('nombre', 'Sin nombre'),
                'date': proyecto.get('fecha_presentacion', ''),
                'sector': proyecto.get('tipo_proyecto', proyecto.get('tipo', '')),
                'description': f"Titular: {proyecto.get('titular', 'N/A')}. Región: {proyecto.get('region', 'N/A')}, {proyecto.get('comuna', 'N/A')}. Inversión: {proyecto.get('inversion_formato', 'N/A')}. Estado: {proyecto.get('estado', 'N/A')}.",
                'raw_data': proyecto  # Guardar todos los datos originales incluyendo industria
            }
            leads.append(lead)
        
        return leads
        
    except Exception as e:
        print(f"❌ Error en scraper SEIA: {e}")
        raise
