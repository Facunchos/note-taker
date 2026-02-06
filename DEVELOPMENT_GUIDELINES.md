# 🛠️ Development Workflow Guidelines

## ⚠️ REGLAS CRÍTICAS DE DESARROLLO

### 🔄 **Flujo Git OBLIGATORIO**

```bash
# ✅ SIEMPRE hacer esto antes de empezar
git checkout dev
git pull origin dev

# ✅ Trabajo diario
git add .
git commit -m "feat/fix/refactor: descripción clara"
git push origin dev

# ❌ NUNCA hacer push directo a main
# ❌ git push origin main  # ← PROHIBIDO
```

### 📋 **Checklist Pre-Feature**

#### Antes de Implementar Cualquier Feature:

1. **Verificar Dependencies**
   ```bash
   cat requirements.txt  # Revisar dependencies actuales
   pip list              # Verificar compatibilidad
   ```

2. **Estado de la Base de Datos**
   ```bash
   flask db current      # Ver revisión actual
   flask db history      # Ver historial de migraciones
   ```

3. **Testing Local**
   ```bash
   flask run             # Probar que arranca correctamente
   # Probar rutas críticas manualmente
   ```

4. **Branch Status**
   ```bash
   git status            # Verificar estado limpio
   git branch            # Confirmar que estamos en dev
   ```

---

## 🎯 **Convenciones de Commits**

### Tipos de Commits
- **feat:** Nueva funcionalidad
- **fix:** Corrección de bugs
- **refactor:** Reestructuración de código
- **style:** Cambios de UI/CSS
- **docs:** Actualización de documentación
- **test:** Adición de tests
- **perf:** Mejoras de rendimiento

### Ejemplos de Commits Buenos
```bash
git commit -m "feat: add granular note permissions system"
git commit -m "fix: resolve circular import in auth routes"
git commit -m "refactor: move permission logic to models"
git commit -m "style: update note editor dark theme"
git commit -m "docs: add comprehensive project context"
```

### Ejemplos de Commits Malos ❌
```bash
git commit -m "updates"
git commit -m "fix stuff"
git commit -m "work in progress"
```

---

## 🚀 **Deployment Process**

### Development → Production Flow

```bash
# 1. Desarrollo completo en dev
git checkout dev
# ... desarrollo y testing ...
git add .
git commit -m "feat: nueva funcionalidad completa"
git push origin dev

# 2. Merge a main solo cuando esté listo para producción
git checkout main
git pull origin main
git merge dev
git push origin main  # ← Esto despliega en Railway automáticamente
```

### Post-Deployment Verification

1. **Railway Dashboard**
   - Verificar que el deploy fue exitoso
   - Revisar logs para errores
   - Confirmar que la base de datos migró correctamente

2. **Testing en Producción**
   ```bash
   # Probar rutas críticas:
   # - Login/registro
   # - Crear mesa
   # - Crear nota
   # - Gestión de permisos
   ```

---

## 📝 **Checklist de Features**

### Antes de Empezar una Feature

- [ ] `git checkout dev`
- [ ] `git pull origin dev`
- [ ] Verificar `requirements.txt` para conflicts potenciales
- [ ] Revisar estado actual de la base de datos
- [ ] Leer `PROJECT_CONTEXT.md` para contexto

### Durante el Desarrollo

- [ ] Testing incremental en local
- [ ] Commits frecuentes y descriptivos
- [ ] Verificar que no se rompen features existentes
- [ ] Considerar necesidad de migraciones de DB
- [ ] Validar formularios y manejo de errores

### Antes del Merge a Main

- [ ] Feature completamente implementada y testeada
- [ ] Sin errores de consola o warnings
- [ ] Responsive design verificado
- [ ] Casos edge de permisos cubiertos
- [ ] Documentación actualizada si es necesario

---

## 🔧 **Common Tasks & Commands**

### Database Operations
```bash
# Crear migración después de cambios en models.py
flask db migrate -m "descripción de los cambios"

# Aplicar migraciones
flask db upgrade

# Ver historial de migraciones
flask db history

# Rollback (solo en emergencias)
flask db downgrade
```

### Development Server
```bash
# Modo desarrollo con debug
export FLASK_ENV=development
flask run --debug

# Verificar logs detallados
flask run --debug > app.log 2>&1
```

### Dependency Management
```bash
# Agregar nueva dependencia
pip install nueva-libreria
pip freeze > requirements.txt

# Verificar actualizaciones
pip list --outdated
```

---

## 🎯 **Project-Specific Guidelines**

### Permission System Development
- **Siempre probar** jerarquía: Autor > DM > Específicos > Mesa
- **Verificar edge cases**: usuario sin permisos, mesa sin miembros
- **Testing manual**: crear notas como DM, asignar permisos, probar como jugador

### UI/UX Changes
- **Mobile first**: probar en responsive antes de commit
- **Dark theme consistency**: mantener estética D&D
- **Accessibility**: asegurar contraste y navegación por teclado

### Security Considerations
- **Validar permisos** en cada endpoint
- **Sanitizar inputs** especialmente en contenido markdown
- **No exponer información** de usuarios sin permisos

---

## 📚 **Para Asistentes de IA Futuros**

### Información de Contexto
- **Siempre leer** `PROJECT_CONTEXT.md` primero
- **Usuario preferido**: desarrollo incremental, no rewrites masivos
- **Estilo de código**: limpio, comentado, mantenible
- **Prioridad**: experiencia de usuario y seguridad

### Patrón de Trabajo
1. Entender request completamente
2. Verificar estado actual del proyecto
3. Proponer solución específica
4. Implementar con commits granulares
5. Verificar que no se rompe nada existente

### Comandos Prohibidos para IA
```bash
# ❌ NUNCA ejecutar estos comandos:
rm -rf .git
git push --force origin main
git reset --hard HEAD~10
pip install --upgrade --force-reinstall
```

---

**Última Actualización**: Febrero 6, 2026  
**Mantenedor**: Facundo  
**Estado**: Reglas activas para desarrollo continuo