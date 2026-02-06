# 📋 Project Context & Development Guidelines

## 🎲 Quest Log - DnD Campaign Note Taker

### **Project Overview**
Collaborative web application for Dungeon Masters and players to manage campaign notes in real-time. Built with Flask, deployed on Railway.

### **Current Status: ✅ PRODUCTION READY**
- ✅ **Deployed on Railway**: Live application with PostgreSQL
- ✅ **Core Features**: Complete authentication, tables, notes system
- ✅ **Advanced Permissions**: Granular per-note access control
- ✅ **Recent Features**: Note duplication, description fields, permission management

---

## 🏗️ **Architecture**

### **Tech Stack**
- **Backend**: Flask 3.1.0, SQLAlchemy, Flask-Migrate
- **Database**: PostgreSQL (Railway), SQLite (dev)
- **Auth**: Flask-Login, Flask-Bcrypt
- **Frontend**: Jinja2 templates, custom CSS (dark theme)
- **Deployment**: Railway with auto-migrations

### **Database Models**
```
User → owns/joins → GameTable → contains → Note
                      ↓                      ↓
                 TableMember            NotePermission
```

**Key Models:**
- `User`: username, email, password_hash
- `GameTable`: name, hash_code (6-char), owner_id
- `TableMember`: user_id, table_id, role (dm/player), can_view_notes
- `Note`: title, description, content, styling (colors/font), author_id
- `NotePermission`: note_id, user_id, can_view, can_edit (NEW FEATURE)

### **Permission System**
- **Table Level**: Members have general note access via `can_view_notes`
- **Note Level**: Individual permissions override table defaults
- **Hierarchy**: Author > DM > Specific Permissions > Table Defaults

---

## 🚀 **Current Features**

### **Core Functionality**
- ✅ User registration/authentication with sessions
- ✅ Create/join tables with 6-character hash codes
- ✅ Rich markdown notes with custom colors/fonts
- ✅ Table member management (kick, invite)

### **Advanced Features** (Recently Added)
- ✅ **Granular Permissions**: DM can set view/edit per note per user
- ✅ **Note Duplication**: Clone notes with custom titles
- ✅ **Description Field**: Separate summary from main content
- ✅ **Quick Actions**: Hover overlays for edit/permissions/duplicate
- ✅ **Smart Filtering**: Users see only permitted notes

### **UI/UX Highlights**
- 🎨 Dark fantasy theme with D&D aesthetics
- 📱 Responsive design for mobile/desktop
- ⚡ Quick actions and modals for efficiency
- 🔐 Clear permission indicators

---

## 🛠️ **Development Workflow**

### **CRITICAL RULES** ⚠️

#### **1. Always Work in `dev` Branch**
```bash
git checkout dev  # Before any changes
git add .
git commit -m "feat/fix: description"  # Commit to dev
# ❌ NEVER: git push origin main
```

#### **2. Check Requirements Before Features**
```bash
# Always verify current dependencies
cat requirements.txt
pip list  # Ensure compatibility
```

#### **3. Migration Pattern**
```bash
# For model changes
flask db migrate -m "description"
flask db upgrade  # Test locally first
```

### **Commit Message Convention**
- `feat:` New features
- `fix:` Bug fixes  
- `refactor:` Code restructuring
- `style:` UI/CSS changes
- `docs:` Documentation updates

### **Railway Deployment**
- **Auto-deploy**: Pushes to `main` trigger Railway deployment
- **Database**: Auto-migration via `railway.json` start command
- **Environment**: PostgreSQL + SECRET_KEY required
- **Logs**: Check Railway dashboard for deployment issues

---

## 🔧 **Known Issues & Solutions**

### **Fixed Issues**
- ✅ **Circular Import**: Moved bcrypt to models.py
- ✅ **Missing DB**: Added auto-migration in railway.json  
- ✅ **Login Errors**: Fixed bcrypt extension access
- ✅ **Permission Bugs**: Implemented proper checking

### **Current Considerations**
- **Performance**: Large tables with many notes may need pagination
- **Security**: Rate limiting not implemented yet
- **Real-time**: No WebSocket updates (future enhancement)

---

## 📝 **Recent Conversation History**

### **Session Topics Covered**
1. **Initial Setup**: Created full Flask app structure
2. **Railway Deployment**: Configured PostgreSQL, environment variables
3. **Debugging**: Fixed circular imports, database connection issues
4. **Permission System**: Implemented granular note-level access control
5. **UI Enhancements**: Added duplication, quick actions, modals

### **Key Decisions Made**
- **Granular over Global**: Individual note permissions vs table-wide
- **Author Privileges**: Authors always retain full control
- **DM Authority**: DMs can manage all notes in their tables
- **UX First**: Quick actions and clear visual feedback prioritized

### **Next Potential Features**
- Real-time collaboration (WebSockets)
- Note search and filtering
- Character sheet integration
- Initiative tracker
- Dice rolling integration
- Export functionality

---

## 📋 **Development Checklist**

### **Before Starting Work**
- [ ] `git checkout dev`
- [ ] `git pull origin dev`
- [ ] Check `requirements.txt` for dependency conflicts
- [ ] Verify current database state

### **During Development**
- [ ] Test locally before committing
- [ ] Check for migration needs (`flask db migrate`)
- [ ] Validate forms and error handling
- [ ] Test permission logic thoroughly

### **Before Requesting Merge**
- [ ] All features tested locally
- [ ] No console errors or warnings
- [ ] Responsive design verified
- [ ] Permission edge cases covered
- [ ] Commit messages are descriptive

### **Post-Merge to Main**
- [ ] Verify Railway deployment succeeds
- [ ] Check production logs for errors
- [ ] Test critical paths on live site
- [ ] Monitor for user feedback

---

## 🎯 **Project Goals**

### **Immediate (Current)**
- ✅ Stable production deployment
- ✅ Complete permission system
- ✅ Intuitive user experience

### **Short Term (Next 2-4 weeks)**
- Search and filtering for notes
- Performance optimizations
- Enhanced error handling
- User feedback integration

### **Long Term (1-3 months)**  
- Real-time collaborative editing
- Character management integration
- Mobile app consideration
- Plugin/extension system

---

## 🤝 **For Future AI Assistants**

### **Project Context**
This is a **production Flask application** for D&D campaign management. The user (Facundo) is an experienced developer who values:
- Clean, maintainable code
- Proper git workflow (dev → main)
- Thorough testing before deployment
- User-focused feature development

### **Development Style**
- **Gradual enhancement** over major rewrites
- **Permission-focused** security model
- **Mobile-first** responsive design
- **Dark theme** fantasy aesthetic

### **Communication Preferences**
- Be specific about changes and their impacts
- Always mention git branch and deployment considerations  
- Provide context for technical decisions
- Focus on user experience implications

### **Current Pain Points**
- Need better documentation for onboarding
- Permission system complexity requires careful testing
- Railway deployment can be finicky with migrations

---

**Last Updated**: February 6, 2026  
**Current Version**: Granular Permissions + Note Duplication  
**Next Session Goal**: Review this context and continue feature development