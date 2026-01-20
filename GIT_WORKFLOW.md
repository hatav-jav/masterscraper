# Guía de Workflow con Git y GitHub

## Estrategia de Versionado

### Commits Frecuentes (Trabajo en `main`)
Para desarrollo personal y cambios pequeños, puedes trabajar directamente en `main` y hacer commits frecuentes:

**Cuándo hacer commit:**
- ✅ Cada vez que agregas una funcionalidad nueva que funciona
- ✅ Cada vez que corriges un bug importante
- ✅ Después de refactorizar código
- ✅ Al completar una tarea del TODO

**Formato de commits:**
```
tipo(scope): descripción breve

- feat: Nueva funcionalidad
- fix: Corrección de bug
- refactor: Refactorización
- docs: Documentación
- style: Formato de código
- chore: Tareas de mantenimiento
```

**Ejemplos:**
```bash
git add .
git commit -m "feat(scraper): agregar scraper de Hechos Esenciales"
git push origin main
```

### Branches para Features Grandes
Para cambios grandes o experimentales, crea un branch:

**Cuándo crear branch:**
- 🔀 Nueva funcionalidad compleja (múltiples días de trabajo)
- 🔀 Experimentación con nuevas tecnologías
- 🔀 Refactorización mayor del código
- 🔀 Integración de servicios externos

**Workflow con branches:**
```bash
# Crear branch desde main
git checkout -b feature/nombre-feature

# Trabajar y hacer commits en el branch
git add .
git commit -m "feat: avance en feature X"

# Cuando esté listo, volver a main
git checkout main

# Mergear el branch
git merge feature/nombre-feature

# Eliminar branch local (opcional)
git branch -d feature/nombre-feature

# Push a GitHub
git push origin main
```

### Push a GitHub

**Cuándo hacer push:**
- 📤 **Siempre** después de hacer commits importantes
- 📤 Al finalizar una sesión de trabajo
- 📤 Antes de hacer cambios experimentales
- 📤 Después de completar una tarea completa

**Comando:**
```bash
git push origin main
```

### Estructura de Branches Recomendada

- `main`: Código estable y funcional
- `feature/nombre`: Para nuevas funcionalidades
- `fix/nombre`: Para correcciones específicas
- `experiment/nombre`: Para experimentos

## Checklist Antes de Push

Antes de hacer push a GitHub, verifica:

- [ ] El código funciona localmente
- [ ] No hay archivos sensibles (.env, passwords, etc.)
- [ ] Los commits tienen mensajes descriptivos
- [ ] No hay errores de sintaxis obvios

## Comandos Útiles

```bash
# Ver estado
git status

# Ver commits recientes
git log --oneline -10

# Ver diferencias
git diff

# Deshacer cambios no commiteados
git checkout -- archivo.py

# Ver ramas
git branch

# Ver ramas remotas
git branch -r
```

## Sugerencias Automáticas

Te sugeriré crear un branch cuando:
- La tarea tomará más de 1 día
- Involucra cambios en múltiples componentes
- Es una funcionalidad experimental
- Puede romper funcionalidad existente

Te sugeriré hacer push cuando:
- Completes una funcionalidad completa
- Corrijas un bug crítico
- Termines una sesión de trabajo
- Antes de hacer cambios grandes

