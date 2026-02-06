# 🎲 Quest Log — DnD Campaign Note Taker

Un sistema web colaborativo para que Dungeon Masters y jugadores gestionen notas de campañas de D&D en tiempo real. Construido con Flask y desplegado en Railway.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)
![Railway](https://img.shields.io/badge/deployment-railway-purple.svg)
![Status](https://img.shields.io/badge/status-production-green.svg)

## 🎯 Funcionalidades Principales

### 🔐 Sistema de Autenticación
- **Registro e Inicio de Sesión** — Autenticación segura con hashing de contraseñas
- **Gestión de Sesiones** — Sesiones persistentes con Flask-Login
- **Control de Acceso** — Verificación de permisos en todas las operaciones

### 🏰 Gestión de Mesas de Juego
- **Crear Campañas** — Cada mesa obtiene un código hash único de 6 caracteres
- **Unirse con Código** — Los jugadores pueden unirse usando el código secreto
- **Roles Diferenciados** — Dungeon Master (DM) con permisos especiales vs Jugadores
- **Gestión de Miembros** — Invitar/expulsar jugadores y controlar accesos

### 📝 Sistema Avanzado de Notas
- **Editor Markdown Rico** — Editor completo con vista previa en tiempo real
- **Personalización Visual** — Colores de fondo, texto y tamaño de fuente por nota
- **Campos Múltiples** — Título, descripción y contenido principal separados
- **Duplicación Inteligente** — Clonado rápido de notas con títulos personalizables
- **Acciones Rápidas** — Interfaz intuitiva con overlays hover para eficiencia

### ⚡ **Sistema de Permisos Granulares** (Funcionalidad Principal)
- **Permisos por Nota** — Control individual de acceso ver/editar para cada nota
- **Jerarquía de Acceso** — Autor > DM > Permisos Específicos > Configuración de Mesa
- **Gestión Visual** — Interfaz clara para asignar permisos por usuario
- **Filtrado Inteligente** — Los usuarios solo ven las notas que tienen permitidas
- **Control Total del DM** — Los DMs pueden gestionar todos los accesos en sus mesas

### 🚀 Despliegue en Producción
- **Railway Ready** — Auto-despliegue desde GitHub con PostgreSQL
- **Configuración por Variables** — Setup fácil con variables de entorno
- **Migraciones Automáticas** — Gestión automatizada del esquema con Flask-Migrate
- **Estado: PRODUCCIÓN ESTABLE** — Sistema completamente funcional y desplegado

## 🏗️ Stack Tecnológico

- **Backend**: Flask 3.1.0, SQLAlchemy, Flask-Migrate
- **Autenticación**: Flask-Login, Flask-Bcrypt
- **Frontend**: Jinja2 templates, CSS personalizado (tema oscuro)
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Despliegue**: Gunicorn + Railway

## 🔧 Configuración de Desarrollo

### Prerrequisitos
- Python 3.12+
- Git
- PostgreSQL (opcional para desarrollo)

### Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/Facunchos/note-taker.git
   cd note-taker
   
   # ⚠️ IMPORTANTE: Siempre trabajar en rama dev
   git checkout dev
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # En Windows: .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   # ⚠️ VERIFICAR requirements.txt antes de instalar
   cat requirements.txt
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   ```bash
   flask db upgrade
   ```

5. **Ejecutar aplicación**
   ```bash
   flask run
   # App disponible en: http://localhost:5000
   ```

### Variables de Entorno

Para desarrollo local:
```bash
export SECRET_KEY="tu-clave-secreta-super-segura"
```

Para producción (Railway):
```bash
SECRET_KEY=tu-clave-secreta
DATABASE_URL=postgresql://usuario:password@host:puerto/database
```

## 🎮 Cómo Usar el Sistema

### Para Dungeon Masters
1. **Crear Mesa** — Registrarse y crear una nueva mesa de campaña
2. **Compartir Código** — Enviar el código hash de 6 caracteres a los jugadores  
3. **Gestionar Notas** — Crear notas con información de campaña
4. **Configurar Permisos** — Asignar accesos específicos por nota y jugador
5. **Duplicar Contenido** — Clonar notas para diferentes sesiones/escenarios

### Para Jugadores
1. **Unirse a Mesa** — Usar el código hash proporcionado por el DM
2. **Ver Notas Permitidas** — Acceder solo a las notas con permisos asignados
3. **Crear Notas Propias** — Añadir notas de personajes o información personal
4. **Colaborar** — Editar notas donde tengan permisos de escritura

## 🏗️ Estructura del Proyecto

```
note-taker/
├── app.py                    # Factory de la aplicación Flask
├── models.py                # Modelos SQLAlchemy + lógica de permisos
├── requirements.txt         # Dependencias del proyecto
├── railway.json            # Configuración de despliegue Railway  
├── PROJECT_CONTEXT.md      # ⭐ CONTEXTO COMPLETO PARA IA
├── DEVELOPMENT_GUIDELINES.md # 🛠️ REGLAS DE DESARROLLO
├── routes/                 # Blueprints organizados por funcionalidad
│   ├── auth.py            # Rutas de autenticación
│   ├── tables.py          # Gestión de mesas de juego
│   └── notes.py           # CRUD notas + sistema de permisos
├── templates/             # Templates Jinja2
│   ├── base.html          # Template base con navegación
│   ├── auth/              # Login, registro, perfil
│   ├── tables/            # Lista, detalle, gestión de mesas
│   └── notes/             # Editor, vista, permisos de notas
├── static/css/
│   └── style.css          # Estilos personalizados (tema oscuro D&D)
└── migrations/            # Migraciones de base de datos
```

## 🚂 Despliegue en Railway

### Deploy con Un Click

1. **Fork this repository** to your GitHub account

2. **Create new Railway project** from GitHub repo

3. **Add PostgreSQL database** to your Railway project

4. **Set environment variables**:
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=${Postgres.DATABASE_URL}
   ```

5. **Run migrations** in Railway console:
   ```bash
   python -m flask db upgrade
   ```

6. **Generate domain** and access your app!

1. **Fork este repositorio** a tu cuenta de GitHub

2. **Crear proyecto Railway** desde el repositorio GitHub

3. **Agregar base de datos PostgreSQL** al proyecto Railway

4. **Configurar variables de entorno**:
   ```
   SECRET_KEY=tu-clave-secreta-super-segura
   DATABASE_URL=${Postgres.DATABASE_URL}
   ```

5. **Migraciones automáticas** — Se ejecutan automáticamente via `railway.json`

6. **Generar dominio** ¡y acceder a tu aplicación!

### Estado Actual: ✅ **DESPLEGADO EN PRODUCCIÓN**

La aplicación está completamente funcional y desplegada. Railway maneja automáticamente:
- ✅ Migraciones de base de datos
- ✅ Variables de entorno  
- ✅ Auto-deploy desde `main` branch
- ✅ Escalabilidad automática

## 🔐 Sistema de Permisos (Funcionalidad Principal)

### Jerarquía de Acceso
```
1. 👑 Autor de la Nota    → Control total (view/edit/delete)
2. 🎭 Dungeon Master     → Control total en su mesa
3. ⚙️ Permisos Específicos → Configuración individual por nota
4. 🏰 Permisos de Mesa    → Configuración base para miembros
```

### Casos de Uso Comunes
- **Información Pública** — Todos los miembros pueden ver/editar
- **Notas del DM** — Solo DM y usuarios específicos autorizados
- **Notas de Jugadores** — Autor + DM + permisos granulares
- **Secretos de Campaña** — Solo DM o usuarios cuidadosamente seleccionados

### Gestión Visual de Permisos
- **Botones Claros** — Interfaz intuitiva para asignar accesos
- **Indicadores Visuales** — Estados de permisos fácilmente identificables  
- **Acciones Rápidas** — Overlays hover para gestión eficiente
- **Filtrado Inteligente** — Solo se muestran notas con permisos apropiados

## 🎨 Características de Diseño

### Tema Visual D&D
- **Paleta Oscura** — Inspirada en la estética de mazmorras
- **Colores Personalizables** — Cada nota puede tener su estilo único
- **Tipografía Variable** — Diferentes fuentes para diferentes tipos de contenido
- **Responsive Design** — Optimizado para móvil y escritorio

### Experiencia de Usuario
- **Navegación Intuitiva** — Flujo lógico entre mesas y notas
- **Modales Eficientes** — Gestión rápida sin pérdida de contexto
- **Feedback Visual** — Estados claros para todas las acciones
- **Accesibilidad** — Contraste apropiado y navegación por teclado

## ⚠️ Flujo de Desarrollo

### IMPORTANTE para Colaboradores/IA

```bash
# ✅ SIEMPRE trabajar en rama dev
git checkout dev

# ✅ Verificar requirements antes de features
cat requirements.txt

# ✅ Commits descriptivos 
git commit -m "feat: descripción clara de la funcionalidad"

# ❌ NUNCA push directo a main
# git push origin main  ← PROHIBIDO
```

**📖 Documentación Completa**: Ver [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) para contexto técnico detallado y [`DEVELOPMENT_GUIDELINES.md`](DEVELOPMENT_GUIDELINES.md) para reglas de desarrollo.

## 📚 Próximas Funcionalidades Potenciales

### Corto Plazo
- 🔍 **Sistema de Búsqueda** — Filtros avanzados para notas
- ⚡ **Optimizaciones** — Rendimiento para mesas con muchas notas
- 🛡️ **Rate Limiting** — Protección contra abuse

### Mediano Plazo  
- 🔄 **Colaboración en Tiempo Real** — WebSockets para edición simultánea
- 📋 **Hojas de Personaje** — Integración con datos de personajes
- 🎲 **Sistema de Dados** — Tiradas integradas en notas

### Largo Plazo
- 📱 **Aplicación Móvil** — App nativa para Android/iOS
- 🔌 **Sistema de Plugins** — Extensiones de terceros
- 📊 **Rastreador de Iniciativa** — Gestión de combate integrada

## 🤝 Contribución y Soporte

### Para Desarrolladores
- **Código Abierto** — Contribuciones bienvenidas via PRs a `dev`
- **Documentación Detallada** — Contexto completo en archivos MD
- **Testing Local** — Setup rápido con instrucciones claras

### Para Usuarios  
- **Aplicación Estable** — Funcionalidad core completamente probada
- **Soporte Continuo** — Actualizaciones regulares y mejoras
- **Feedback Bienvenido** — Sugerencias para futuras funcionalidades

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para detalles completos.

## 📞 Contacto

**Desarrollador**: Facundo  
**Estado del Proyecto**: ✅ Producción Estable  
**Última Actualización**: Febrero 2026

---

⚔️ *"En cada campaña, las mejores historias vienen de las mejores notas..."*

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | Database connection string | Auto-injected by Railway |

## 📁 Project Structure

```
note-taker/
├── app.py                 # Flask application factory
├── models.py              # SQLAlchemy database models
├── requirements.txt       # Python dependencies
├── railway.json          # Railway deployment config
├── routes/               # Blueprint route handlers
│   ├── auth.py          # Authentication routes
│   ├── tables.py        # Game table management
│   └── notes.py         # Note CRUD operations
├── templates/           # Jinja2 HTML templates
│   ├── base.html       # Base layout template
│   ├── auth/           # Login/signup pages
│   ├── tables/         # Table management pages
│   └── notes/          # Note editor/viewer
├── static/
│   └── css/style.css   # Custom styling
└── migrations/         # Database migration files
```

## 🗄️ Database Schema

### Users
- `id`, `username`, `email`, `password_hash`, `created_at`

### Game Tables
- `id`, `name`, `description`, `hash_code`, `owner_id`, `created_at`

### Table Members (Join Table)
- `id`, `user_id`, `table_id`, `role`, `can_view_notes`, `joined_at`

### Notes
- `id`, `table_id`, `author_id`, `title`, `content`, `bg_color`, `text_color`, `font_size`, `created_at`, `updated_at`

## 🎯 Usage Flow

1. **Register** a new account or **login**
2. **Create a table** (becomes owner) or **join existing** with hash code
3. **Invite players** by sharing the 6-character table code
4. **Create notes** with markdown, custom colors, and styling
5. **Collaborate** — all members can edit notes (if permitted)
6. **Manage access** — owners control who can view/edit notes

## 🔧 Development

### Running Tests
```bash
# TODO: Add pytest configuration
pytest
```

### Code Style
```bash
# Format with black
black .

# Lint with flake8
flake8 .
```

### Database Operations
```bash
# Create new migration
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Downgrade migration
flask db downgrade
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for D&D campaigns and collaborative storytelling
- Inspired by the need for simple, real-time note sharing
- Designed with Railway deployment in mind
