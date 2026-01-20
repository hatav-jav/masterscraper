# Guía de Workflow Git para Master Scraper

## Filosofía

Este proyecto prioriza simplicidad. Usamos branches principalmente para features grandes o cambios experimentales. Para cambios pequeños y directos, trabajamos directamente en `main`.

## Cuándo Crear un Branch

### ✅ Crear branch cuando:
- Agregas un nuevo scraper completo
- Refactorizas código importante del backend
- Cambios grandes en el frontend (nuevas páginas, reestructuración)
- Experimentas con nuevas funcionalidades
- Cambios que puedan romper funcionalidad existente

### ✅ Trabajar directamente en main cuando:
- Correcciones de bugs pequeños
- Mejoras de documentación
- Ajustes de configuración
- Cambios de texto/UI menores
- Agregar nuevos endpoints pequeños
- Correcciones de typos

## Flujo de Trabajo Recomendado

### Para cambios pequeños (directo en main):
```bash
# 1. Verificar estado
git status

# 2. Agregar cambios
git add .

# 3. Commit con mensaje descriptivo
git commit -m "tipo(scope): descripción breve"

# 4. Push (después de varios commits o al final del día)
git push origin main
```

### Para cambios grandes (usar branch):
```bash
# 1. Crear y cambiar a nuevo branch
git checkout -b feature/nombre-feature
# o
git checkout -b fix/nombre-fix

# 2. Hacer cambios y commits
git add .
git commit -m "feat(scraper): agregar nuevo scraper X"

# 3. Cuando esté listo, mergear a main
git checkout main
git merge feature/nombre-feature

# 4. Push
git push origin main

# 5. Eliminar branch local (opcional)
git branch -d feature/nombre-feature
```

## Convención de Mensajes de Commit

Formato: `tipo(scope): descripción breve`

### Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `refactor`: Refactorización de código
- `docs`: Cambios en documentación
- `style`: Cambios de formato (sin afectar lógica)
- `chore`: Tareas de mantenimiento
- `scraper`: Cambios específicos en scrapers
- `backend`: Cambios en backend
- `frontend`: Cambios en frontend

### Ejemplos:
```
feat(scraper): agregar scraper de Hechos Esenciales
fix(api): corregir endpoint de reporte
refactor(database): mejorar funciones de consulta
docs(readme): actualizar instrucciones de setup
chore(deps): actualizar dependencias
```

## Frecuencia de Push

### ✅ Push frecuente (cada 1-3 commits):
- Cuando agregas funcionalidad nueva
- Después de corregir un bug importante
- Al finalizar una sesión de trabajo

### ✅ Push al final del día:
- Si solo hiciste cambios menores
- Si trabajaste en varios commits relacionados

### ⚠️ Siempre hacer push antes de:
- Cambios grandes que puedan romper cosas
- Experimentar con algo nuevo
- Tomar un descanso largo

## Resolución de Conflictos

Si hay conflictos al hacer pull:
```bash
# 1. Hacer pull primero
git pull origin main

# 2. Resolver conflictos manualmente en los archivos

# 3. Agregar archivos resueltos
git add .

# 4. Completar merge
git commit -m "fix: resolver conflictos de merge"
```

## Mejores Prácticas

1. **Nunca hacer push de archivos sensibles**: Verifica que `.env` y `.env.local` estén en `.gitignore`
2. **Commits pequeños y frecuentes**: Es mejor muchos commits pequeños que uno enorme
3. **Mensajes descriptivos**: El commit message debe explicar QUÉ y POR QUÉ, no cómo
4. **Revisar cambios antes de commit**: `git diff` para ver qué vas a commitear
5. **Pull antes de push**: Siempre hacer `git pull` antes de `git push` si trabajas en equipo

## Comandos Útiles

```bash
# Ver estado actual
git status

# Ver cambios no agregados
git diff

# Ver historial
git log --oneline -10

# Deshacer cambios no commitados (CUIDADO)
git restore <archivo>

# Ver qué branch estás usando
git branch

# Ver diferencias entre branches
git diff main..feature/nombre
```
