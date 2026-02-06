# ⚔️ Quest Log — DnD Campaign Note Taker

A collaborative note-taking web application designed for Dungeon Masters and players to manage campaign notes in real-time. Built with Flask and ready for Railway deployment.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🧙‍♂️ User Management
- **User Registration & Authentication** — Secure signup/login with password hashing
- **Session Management** — Persistent sessions with Flask-Login

### 🏰 Game Tables
- **Create Campaign Tables** — Each table gets a unique 6-character hash code
- **Join with Hash Code** — Players can join tables using the secret code
- **Member Management** — Table owners can kick players and control note access
- **Voluntary Leave** — Players can leave tables at any time

### 📝 Collaborative Notes
- **Rich Markdown Support** — Full markdown editor with live preview
- **Custom Styling** — Change background color, text color, and font size per note
- **Real-time Collaboration** — All table members can create, edit, and delete notes
- **Permission Control** — Owners can grant/revoke note access for individual members

### 🚀 Deployment Ready
- **Railway Compatible** — Auto-deploys from GitHub with PostgreSQL
- **Environment Configuration** — Easy setup with environment variables
- **Database Migrations** — Automated schema management with Flask-Migrate

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Migrate
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Frontend**: Jinja2 templates, Custom CSS
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Deployment**: Gunicorn + Railway

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.12+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Facunchos/note-taker.git
   cd note-taker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   flask db upgrade
   ```

5. **Run the application**
   ```bash
   flask run --debug
   ```

6. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

## 🚂 Railway Deployment

### One-Click Deploy

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

### Environment Variables

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
