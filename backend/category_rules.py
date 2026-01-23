"""
Reglas de clasificación de proyectos por categorías.
Fácilmente modificable para ajustar keywords y umbrales.
"""

# Umbral mínimo para categoría principal
UMBRAL_CATEGORIA_PRINCIPAL = 0.10

# Umbral mínimo para categorías secundarias
UMBRAL_CATEGORIA_SECUNDARIA = 0.10

# Definición de categorías con keywords y colores
CATEGORIAS = {
    "Energía Renovable": {
        "keywords": [
            "fotovoltaico", "solar", "generación", "ernc", "mwp", "mwac", "gwh",
            "potencia nominal", "mw salida", "paneles", "módulos", "inversores",
            "transformación", "corriente continua", "corriente alterna", "sai",
            "silicio", "monocristalino", "bifacial"
        ],
        "color": "#22c55e",  # verde
        "color_name": "green"
    },
    "BESS": {
        "keywords": [
            "bess", "sae", "almacenamiento", "baterías", "batería", "litio",
            "ferrofosfato", "excedentes de energía", "descarga"
        ],
        "color": "#3b82f6",  # azul
        "color_name": "blue"
    },
    "Infraestructura Eléctrica": {
        "keywords": [
            "transmisión", "interconexión", "subestación", "elevadora", "línea",
            "circuito simple", "alta tensión", "media tensión", "220kv", "66kv",
            "cen", "sen"
        ],
        "color": "#f97316",  # naranja
        "color_name": "orange"
    },
    "Desarrollo de Proyectos": {
        "keywords": [
            "ampliación", "modificación", "extensión", "vida útil", "cierre",
            "post cierre", "punto conexión", "evacuación", "inyección"
        ],
        "color": "#a855f7",  # morado
        "color_name": "purple"
    },
    "Minería": {
        "keywords": [
            "minería", "mina", "extracción", "rajo", "estéril", "concentrados",
            "concentradora", "producción", "tasa", "ley mineral", "cobre",
            "molibdeno", "cátodos", "transporte terrestre", "cantera", "puertos"
        ],
        "color": "#374151",  # gris oscuro
        "color_name": "gray-dark"
    },
    "Agua": {
        "keywords": [
            "acueducto", "embalse", "tranque", "riego", "agua", "desaladora",
            "desalinización", "hídrico"
        ],
        "color": "#06b6d4",  # celeste
        "color_name": "cyan"
    },
    "Infraestructura y Construcción": {
        "keywords": [
            "construcción", "operación", "obras temporales", "obras permanentes",
            "estructuras", "longitud", "suministro"
        ],
        "color": "#92400e",  # marrón
        "color_name": "brown"
    },
}

# Categoría por defecto
CATEGORIA_DEFAULT = "Otros"
CATEGORIA_DEFAULT_COLOR = "#9ca3af"  # gris claro
CATEGORIA_DEFAULT_COLOR_NAME = "gray"


def clasificar_proyecto(nombre: str, descripcion: str = "") -> dict:
    """
    Clasifica un proyecto en base a keywords encontradas.
    
    Retorna:
    {
        'categoria_principal': str,
        'categorias_secundarias': list[str],
        'scores': dict[str, float],
        'color': str,
        'color_name': str
    }
    """
    # Texto a analizar (normalizado a minúsculas)
    texto = f"{nombre} {descripcion}".lower()
    
    # Calcular score para cada categoría
    scores = {}
    for categoria, config in CATEGORIAS.items():
        keywords = config["keywords"]
        matches = sum(1 for kw in keywords if kw.lower() in texto)
        score = matches / len(keywords) if keywords else 0
        scores[categoria] = score
    
    # Determinar categoría principal (mayor score >= umbral principal)
    categoria_principal = CATEGORIA_DEFAULT
    max_score = 0
    
    for categoria, score in scores.items():
        if score >= UMBRAL_CATEGORIA_PRINCIPAL and score > max_score:
            max_score = score
            categoria_principal = categoria
    
    # Determinar categorías secundarias (score >= umbral secundario, excluyendo principal)
    categorias_secundarias = [
        cat for cat, score in scores.items()
        if score >= UMBRAL_CATEGORIA_SECUNDARIA and cat != categoria_principal
    ]
    
    # Obtener color de la categoría principal
    if categoria_principal in CATEGORIAS:
        color = CATEGORIAS[categoria_principal]["color"]
        color_name = CATEGORIAS[categoria_principal]["color_name"]
    else:
        color = CATEGORIA_DEFAULT_COLOR
        color_name = CATEGORIA_DEFAULT_COLOR_NAME
    
    return {
        'categoria_principal': categoria_principal,
        'categorias_secundarias': categorias_secundarias,
        'scores': scores,
        'color': color,
        'color_name': color_name
    }


def get_categoria_color(categoria: str) -> tuple:
    """Obtiene el color de una categoría."""
    if categoria in CATEGORIAS:
        return CATEGORIAS[categoria]["color"], CATEGORIAS[categoria]["color_name"]
    return CATEGORIA_DEFAULT_COLOR, CATEGORIA_DEFAULT_COLOR_NAME


def get_all_categorias() -> list:
    """Retorna lista de todas las categorías disponibles."""
    return list(CATEGORIAS.keys()) + [CATEGORIA_DEFAULT]
