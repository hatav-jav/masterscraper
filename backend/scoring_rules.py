"""
Reglas de scoring para selección de Top 20 proyectos.
Fácilmente modificable para ajustar filtros y puntajes.
"""

# ==================================================
# 1. FILTROS DUROS (GATEKEEPERS)
# ==================================================

# Estados válidos (incluir solo estos)
ESTADOS_VALIDOS = [
    "En Calificación",
    "Admitido a Tramitación",
    "Aprobado"
]

# Estados excluidos (excluir automáticamente)
ESTADOS_EXCLUIDOS = [
    "Desistido",
    "No Admitido a Tramitación",
    "Rechazado"
]

# ==================================================
# 2. REGLA DE INVERSIÓN MÍNIMA
# ==================================================

# Monto mínimo general (USD MM)
MONTO_MINIMO_USD_MM = 25

# Industrias estratégicas con monto mínimo reducido
INDUSTRIAS_ESTRATEGICAS = ["BESS", "Infraestructura Eléctrica", "Minería"]

# Monto mínimo para industrias estratégicas (USD MM)
MONTO_MINIMO_ESTRATEGICAS_USD_MM = 10

# ==================================================
# 3. SCORING POR INVERSIÓN
# ==================================================

# Formato: (monto_minimo, puntos)
# Se aplica el primer rango que cumple (de mayor a menor)
SCORE_INVERSION = [
    (1000, 30),  # >= 1000 MM → 30 puntos
    (500, 25),   # >= 500 MM → 25 puntos
    (200, 20),   # >= 200 MM → 20 puntos
    (100, 15),   # >= 100 MM → 15 puntos
    (50, 10),    # >= 50 MM → 10 puntos
    (0, 0),      # < 50 MM → 0 puntos
]

# ==================================================
# 4. SCORING POR ESTADO
# ==================================================

SCORE_ESTADO = {
    "En Calificación": 25,
    "Admitido a Tramitación": 20,
    "Aprobado": 25,
}

# ==================================================
# 5. CONFIGURACIÓN DE SELECCIÓN
# ==================================================

# Cantidad de proyectos a seleccionar
TOP_N_PROYECTOS = 20
