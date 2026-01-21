"""
Funciones de scoring para selección de Top 20 proyectos.
Implementación determinista y reproducible.
"""

from typing import List, Dict, Any
from backend.scoring_rules import (
    ESTADOS_VALIDOS, ESTADOS_EXCLUIDOS,
    MONTO_MINIMO_USD_MM, INDUSTRIAS_ESTRATEGICAS, MONTO_MINIMO_ESTRATEGICAS_USD_MM,
    SCORE_INVERSION, SCORE_ESTADO, TOP_N_PROYECTOS
)


def normalizar_estado(estado: str) -> str:
    """Normaliza el estado para comparación."""
    if not estado:
        return ""
    return estado.strip()


def es_estado_valido(estado: str) -> bool:
    """Verifica si el estado está en la lista de estados válidos."""
    estado_norm = normalizar_estado(estado).lower()
    return any(ev.lower() in estado_norm for ev in ESTADOS_VALIDOS)


def es_estado_excluido(estado: str) -> bool:
    """Verifica si el estado está en la lista de estados excluidos."""
    estado_norm = normalizar_estado(estado).lower()
    return any(ee.lower() in estado_norm for ee in ESTADOS_EXCLUIDOS)


def get_monto_minimo(categoria: str) -> float:
    """Obtiene el monto mínimo según la categoría del proyecto."""
    if categoria in INDUSTRIAS_ESTRATEGICAS:
        return MONTO_MINIMO_ESTRATEGICAS_USD_MM
    return MONTO_MINIMO_USD_MM


def calcular_score_inversion(inversion_mm: float) -> int:
    """Calcula el score por inversión."""
    if inversion_mm is None:
        return 0
    
    for monto_minimo, puntos in SCORE_INVERSION:
        if inversion_mm >= monto_minimo:
            return puntos
    return 0


def calcular_score_estado(estado: str) -> int:
    """Calcula el score por estado del proyecto."""
    estado_norm = normalizar_estado(estado).lower()
    
    for estado_key, puntos in SCORE_ESTADO.items():
        if estado_key.lower() in estado_norm:
            return puntos
    return 0


def calcular_score_total(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula el score total de un proyecto.
    
    Retorna el lead con campos adicionales:
    - score_inversion
    - score_estado
    - score_total
    - explicacion (línea explicativa del score)
    """
    raw_data = lead.get('raw_data', {})
    
    # Obtener datos del proyecto
    inversion_mm = raw_data.get('inversion_millones')
    estado = raw_data.get('estado', '')
    categoria = raw_data.get('industria', 'Otros')
    nombre = lead.get('project_name', '')
    
    # Calcular scores
    score_inv = calcular_score_inversion(inversion_mm)
    score_est = calcular_score_estado(estado)
    score_total = score_inv + score_est
    
    # Generar explicación
    explicacion_parts = []
    if categoria != 'Otros':
        explicacion_parts.append(categoria)
    if inversion_mm and inversion_mm >= 100:
        explicacion_parts.append("alta inversión")
    elif inversion_mm and inversion_mm >= 50:
        explicacion_parts.append("inversión media")
    
    estado_lower = estado.lower() if estado else ""
    if "calificación" in estado_lower:
        explicacion_parts.append("etapa temprana")
    elif "admitido" in estado_lower:
        explicacion_parts.append("en tramitación")
    elif "aprobado" in estado_lower:
        explicacion_parts.append("aprobado")
    
    explicacion = " + ".join(explicacion_parts) if explicacion_parts else "Sin características destacadas"
    
    return {
        **lead,
        'score_inversion': score_inv,
        'score_estado': score_est,
        'score_total': score_total,
        'explicacion': explicacion
    }


def filtrar_elegibles(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aplica filtros duros para determinar proyectos elegibles.
    
    Filtros:
    1. Estado válido (no excluido)
    2. Inversión >= monto mínimo (según categoría)
    """
    elegibles = []
    
    for lead in leads:
        raw_data = lead.get('raw_data', {})
        estado = raw_data.get('estado', '')
        inversion_mm = raw_data.get('inversion_millones')
        categoria = raw_data.get('industria', 'Otros')
        
        # Filtro 1: Estado
        if es_estado_excluido(estado):
            continue
        if not es_estado_valido(estado):
            continue
        
        # Filtro 2: Inversión mínima
        monto_minimo = get_monto_minimo(categoria)
        if inversion_mm is None or inversion_mm < monto_minimo:
            continue
        
        elegibles.append(lead)
    
    return elegibles


def get_top_proyectos(leads: List[Dict[str, Any]], limit: int = None) -> List[Dict[str, Any]]:
    """
    Obtiene los top N proyectos ordenados por score.
    
    1. Filtra proyectos elegibles
    2. Calcula score para cada uno
    3. Ordena por score descendente
    4. Retorna los primeros N
    """
    if limit is None:
        limit = TOP_N_PROYECTOS
    
    # Filtrar elegibles
    elegibles = filtrar_elegibles(leads)
    
    # Calcular scores
    con_score = [calcular_score_total(lead) for lead in elegibles]
    
    # Ordenar por score descendente
    ordenados = sorted(con_score, key=lambda x: x['score_total'], reverse=True)
    
    # Agregar ranking
    for i, proyecto in enumerate(ordenados[:limit], 1):
        proyecto['ranking'] = i
    
    return ordenados[:limit]


def generar_resumen_top_proyectos(top_proyectos: List[Dict[str, Any]]) -> str:
    """Genera un resumen en texto de los top proyectos."""
    if not top_proyectos:
        return "No hay proyectos que cumplan los criterios de selección."
    
    lineas = []
    for p in top_proyectos:
        raw = p.get('raw_data', {})
        lineas.append(
            f"{p['ranking']}. {p['project_name'][:50]}... "
            f"(Score: {p['score_total']}, Inv: {raw.get('inversion_millones', 'N/A')} MM)"
        )
    
    return "\n".join(lineas)
