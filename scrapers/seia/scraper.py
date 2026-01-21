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
    """
    Parsea el formato de inversión del SEIA a millones de dólares.
    El SEIA usa formato chileno/europeo: punto para miles, coma para decimales.
    Ejemplos: "10.000" = 10 millones, "1.300" = 1300 millones, "339,594" = 339.594 millones
    """
    if not inversion_str or not isinstance(inversion_str, str):
        return None
    
    try:
        inversion_limpia = inversion_str.strip()
        
        # El SEIA usa formato chileno: punto para miles, coma para decimales
        # "10.000" significa 10 (diez millones), no 10000
        # "1.300" significa 1300 (mil trescientos millones)
        # "339,594" significa 339.594 millones
        
        if ',' in inversion_limpia and '.' in inversion_limpia:
            # Formato completo: "1.300,50" -> 1300.50
            inversion_limpia = inversion_limpia.replace('.', '').replace(',', '.')
        elif ',' in inversion_limpia:
            # Solo coma = decimal: "339,594" -> 339.594
            inversion_limpia = inversion_limpia.replace(',', '.')
        elif '.' in inversion_limpia:
            # Solo punto = separador de miles chileno: "10.000" -> 10
            # Remover todos los puntos (son separadores de miles)
            inversion_limpia = inversion_limpia.replace('.', '')
        
        valor = float(inversion_limpia)
        return valor if valor > 0 else None
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


def run_seia(obtener_descripcion: bool = True, existing_projects: dict = None, progress_callback=None, cancel_callback=None) -> Dict:
    """
    Ejecuta el scraper de SEIA.
    Retorna dict con: {new_leads: [...], estado_changes: [...]}
    
    Args:
        obtener_descripcion: Si es True, obtiene la descripción completa de cada proyecto (más lento pero más info)
        existing_projects: Dict {codigo_seia: {lead_id, estado, project_name, raw_data}} de proyectos existentes
        progress_callback: Función para reportar progreso (recibe porcentaje y mensaje)
        cancel_callback: Función para verificar si se debe cancelar (retorna True para cancelar)
    """
    print("🔄 Iniciando scraper SEIA...")
    
    proyectos_nuevos = []
    estado_changes = []  # Lista de cambios de estado detectados
    pagina = 1
    max_proyectos = 50  # Máximo de proyectos nuevos a obtener
    registros_por_pagina = 100  # 100 proyectos por página para mayor eficiencia
    duplicados_consecutivos = 0
    max_duplicados_consecutivos = 10  # Detener después de 10 duplicados seguidos
    
    if existing_projects is None:
        existing_projects = {}
    
    existing_codes = set(existing_projects.keys())
    
    def is_cancelled():
        return cancel_callback and cancel_callback()
    
    def report_progress(percent, msg):
        print(msg)
        if progress_callback:
            progress_callback(percent, msg)
    
    try:
        # Fase 1: Obtener listado y detectar cambios de estado (40% del progreso)
        report_progress(0, "Obteniendo proyectos...")
        
        while len(proyectos_nuevos) < max_proyectos:
            # Verificar cancelación
            if is_cancelled():
                report_progress(0, "Cancelado")
                return {'new_leads': [], 'estado_changes': estado_changes}
            
            progress_fase1 = min(40, int((len(proyectos_nuevos) / max_proyectos) * 40))
            report_progress(progress_fase1, f"Página {pagina}...")
            
            datos = fetch_datos_listado(pagina=pagina, registros_por_pagina=registros_por_pagina)
            proyectos_pagina = parse_listado_json(datos)
            
            if not proyectos_pagina:
                report_progress(40, "Sin más proyectos")
                break
            
            # Procesar cada proyecto
            for proyecto in proyectos_pagina:
                codigo = str(proyecto.get('codigo_seia', ''))
                estado_actual = proyecto.get('estado', '')
                
                if codigo and codigo in existing_codes:
                    # Proyecto existente - verificar si cambió el estado
                    proyecto_guardado = existing_projects.get(codigo, {})
                    estado_anterior = proyecto_guardado.get('estado', '')
                    
                    # Comparar estados (normalizar para comparación)
                    if estado_anterior and estado_actual and estado_anterior.strip().lower() != estado_actual.strip().lower():
                        # ¡Cambio de estado detectado!
                        print(f"  🔄 CAMBIO DE ESTADO: {proyecto.get('nombre', 'N/A')}")
                        print(f"      Antes: {estado_anterior} -> Ahora: {estado_actual}")
                        
                        estado_changes.append({
                            'lead_id': proyecto_guardado.get('lead_id'),
                            'codigo_seia': codigo,
                            'project_name': proyecto.get('nombre', ''),
                            'estado_anterior': estado_anterior,
                            'estado_nuevo': estado_actual,
                            'raw_data': proyecto_guardado.get('raw_data', {})
                        })
                    
                    duplicados_consecutivos += 1
                    if duplicados_consecutivos >= max_duplicados_consecutivos:
                        report_progress(40, "Duplicados detectados, deteniendo...")
                        break
                else:
                    # Proyecto nuevo
                    duplicados_consecutivos = 0
                    proyectos_nuevos.append(proyecto)
            
            # Si alcanzamos el límite de duplicados, salir del loop
            if duplicados_consecutivos >= max_duplicados_consecutivos:
                break
            
            report_progress(progress_fase1, f"Página {pagina}: {len(proyectos_nuevos)} nuevos")
            
            # Si obtuvimos menos de lo esperado, ya no hay más páginas
            if len(proyectos_pagina) < registros_por_pagina:
                break
            
            # Si ya tenemos suficientes, detener
            if len(proyectos_nuevos) >= max_proyectos:
                proyectos_nuevos = proyectos_nuevos[:max_proyectos]
                break
            
            pagina += 1
            time.sleep(0.5)  # Pausa entre páginas
        
        cambios_msg = f", {len(estado_changes)} cambios de estado" if estado_changes else ""
        report_progress(40, f"{len(proyectos_nuevos)} nuevos{cambios_msg}")
        
        # Fase 2: Obtener descripciones de proyectos NUEVOS (40% al 95% del progreso)
        if obtener_descripcion and proyectos_nuevos:
            report_progress(40, "Obteniendo descripciones...")
            total_proyectos = len(proyectos_nuevos)
            for i, proyecto in enumerate(proyectos_nuevos):
                # Verificar cancelación
                if is_cancelled():
                    report_progress(0, "Cancelado")
                    return {'new_leads': [], 'estado_changes': estado_changes}
                
                if proyecto.get('link_ficha'):
                    progress_fase2 = 40 + int(((i + 1) / total_proyectos) * 55)
                    report_progress(progress_fase2, f"Descripción {i+1}/{total_proyectos}")
                    descripcion = fetch_descripcion_proyecto(proyecto['link_ficha'])
                    proyecto['descripcion_completa'] = descripcion
                    time.sleep(0.3)  # Pausa entre requests
        
        report_progress(95, "Finalizando...")
        
        # Fase 3: Normalizar datos (95% al 100%)
        leads = []
        for proyecto in proyectos_nuevos:
            lead = {
                'source': 'SEIA',
                'project_name': proyecto.get('nombre', 'Sin nombre'),
                'date': proyecto.get('fecha_presentacion', ''),
                'sector': proyecto.get('tipo_proyecto', proyecto.get('tipo', '')),
                'description': f"Titular: {proyecto.get('titular', 'N/A')}. Región: {proyecto.get('region', 'N/A')}, {proyecto.get('comuna', 'N/A')}. Inversión: {proyecto.get('inversion_formato', 'N/A')}. Estado: {proyecto.get('estado', 'N/A')}.",
                'raw_data': proyecto
            }
            leads.append(lead)
        
        report_progress(100, f"Completado: {len(leads)} nuevos{cambios_msg}")
        
        return {
            'new_leads': leads,
            'estado_changes': estado_changes
        }
        
    except Exception as e:
        print(f"❌ Error en scraper SEIA: {e}")
        raise
