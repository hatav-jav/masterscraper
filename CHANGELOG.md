# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.1.0] - 2026-01-XX

### Added
- **Paginación en Report Data Table**: Implementada paginación completa con selector de items por página (10, 20, 50, 100)
- **Sin límite de visualización**: La UI ahora puede mostrar todos los proyectos scrapeados (hasta 50,000)
- **Controles de paginación**: Botones Previous/Next y números de página con navegación inteligente
- **Contador de proyectos**: Muestra total filtrado y total general en el header

### Changed
- Backend: Aumentado límite de `/leads` de 1,000 a 50,000 proyectos
- Frontend: Carga inicial de 10,000 proyectos (sin límite práctico en UI)
- DataTable: Reset automático a página 1 cuando cambian filtros o sorting

### Fixed
- Ordenamiento de fechas DD/MM/YYYY ahora funciona correctamente (2026 antes que 2025)

---

## [1.0.0] - 2026-01-XX

### Added
- **UI Sidebar Redesign**: Panel lateral con navegación por secciones (General, SEIA, Hechos Esenciales)
- **Sección General**: Dashboard con stats, Run All Scrapers, Download Report, Clear All Data
- **Sección SEIA con Tabs**: 
  - Report Data (tabla paginada)
  - Top 20 Leads (proyectos más relevantes)
  - Status Changes (cambios de estado detectados)
  - Latest Runs (historial de ejecuciones)
- **Botón Run Scraper compacto**: Tarjeta pequeña debajo del título en sección SEIA
- **Clasificación mejorada**: Umbral bajado a 0.05 + keywords agregadas (eólico, minero, etc.)
- **Parseo de inversión corregido**: Maneja correctamente formatos chilenos (850.000 → 850, 1.300,50 → 1300.5)
- **Status changes en resultado**: Muestra cantidad de cambios de estado al terminar scraper

### Changed
- Layout principal: Sidebar fijo + contenido dinámico
- DataTable: Eliminada columna "Source" (ya no necesaria con secciones)
- ScraperButton: Modo compacto para sección SEIA
- LastRuns: Soporta filtro por source

### Fixed
- Sorting por Investment y Date ahora funciona correctamente
- Fechas ordenadas correctamente (DD/MM/YYYY parseado a Date)

---

## [0.9.0] - 2026-01-XX

### Added
- Top 20 Projects con scoring determinístico
- Sistema de clasificación por keywords con umbrales configurables
- Colores fijos por categoría (Energía Renovable, BESS, Minería, etc.)
- Botón Clear All Data con confirmación
- Export Markdown con sección Top 20
- Detección de cambios de estado en proyectos SEIA

### Changed
- Clasificación de proyectos: De heurísticas simples a sistema de keywords con scoring
- Scoring rules: Configurables en `scoring_rules.py` y `category_rules.py`

---

## [0.8.0] - 2026-01-XX

### Added
- Descripción completa de proyectos SEIA
- Detección de duplicados por código SEIA
- Progress bar con porcentaje real
- Botón Stop para cancelar scraper
- Latest Runs section con timezone Santiago
- Estado Changes section para cambios detectados

### Changed
- SEIA scraper: 100 proyectos por página (antes 10)
- Límite de proyectos: 500 por ejecución
- UI: Dark mode por defecto
- Tipografía: DM Sans (minimalista)

---

## [0.1.0] - 2026-01-XX

### Added
- Scraper SEIA básico
- Scraper Hechos Esenciales básico
- FastAPI backend
- Next.js frontend con Tailwind
- SQLite database
- Report generation con IA
- Markdown export
