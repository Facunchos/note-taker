from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
import secrets
import string

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    owned_tables = db.relationship(
        "GameTable", backref="owner", lazy=True, foreign_keys="GameTable.owner_id"
    )
    memberships = db.relationship("TableMember", backref="user", lazy=True)
    notes = db.relationship("Note", backref="author", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class GameTable(db.Model):
    __tablename__ = "game_tables"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    hash_code = db.Column(db.String(8), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    members = db.relationship(
        "TableMember", backref="table", lazy=True, cascade="all, delete-orphan"
    )
    notes = db.relationship(
        "Note", backref="table", lazy=True, cascade="all, delete-orphan"
    )

    @staticmethod
    def generate_hash_code():
        """Generate a unique 6-character alphanumeric hash code."""
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(secrets.choice(alphabet) for _ in range(6))
            if not GameTable.query.filter_by(hash_code=code).first():
                return code

    def is_member(self, user):
        return TableMember.query.filter_by(
            table_id=self.id, user_id=user.id
        ).first() is not None

    def is_owner(self, user):
        return self.owner_id == user.id

    def __repr__(self):
        return f"<GameTable {self.name} [{self.hash_code}]>"


class TableMember(db.Model):
    __tablename__ = "table_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    table_id = db.Column(
        db.Integer, db.ForeignKey("game_tables.id"), nullable=False
    )
    role = db.Column(db.String(20), default="player")  # 'dm' or 'player'
    can_view_notes = db.Column(db.Boolean, default=True)
    joined_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "table_id", name="unique_membership"),
    )

    def __repr__(self):
        return f"<TableMember user={self.user_id} table={self.table_id}>"


class NotePermission(db.Model):
    __tablename__ = "note_permissions"

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey("notes.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    can_view = db.Column(db.Boolean, default=True)
    can_edit = db.Column(db.Boolean, default=True)
    granted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    granted_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint("note_id", "user_id", name="unique_note_user_permission"),
    )

    def __repr__(self):
        return f"<NotePermission note={self.note_id} user={self.user_id}>"


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(
        db.Integer, db.ForeignKey("game_tables.id"), nullable=False
    )
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    content = db.Column(db.Text, default="")
    bg_color = db.Column(db.String(7), default="#ffffff")
    text_color = db.Column(db.String(7), default="#1a1a2e")
    font_size = db.Column(db.Integer, default=16)  # in pixels
    is_template = db.Column(db.Boolean, default=False)  # for duplicated notes
    original_note_id = db.Column(db.Integer, db.ForeignKey("notes.id"), nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    permissions = db.relationship("NotePermission", backref="note", lazy=True, cascade="all, delete-orphan")
    original = db.relationship("Note", remote_side=[id], backref="duplicates")

    def user_can_view(self, user):
        """Check if user can view this note."""
        # Author can always view
        if self.author_id == user.id:
            return True
        
        # Check if user is table member
        membership = TableMember.query.filter_by(
            table_id=self.table_id, user_id=user.id
        ).first()
        if not membership:
            return False
        
        # DM can always view
        if membership.role == 'dm':
            return True
            
        # Check specific note permission
        permission = NotePermission.query.filter_by(
            note_id=self.id, user_id=user.id
        ).first()
        
        if permission:
            return permission.can_view
        
        # Default: table members can view if they have general note access
        return membership.can_view_notes

    def user_can_edit(self, user):
        """Check if user can edit this note."""
        # Author can always edit
        if self.author_id == user.id:
            return True
            
        # Check if user is table member
        membership = TableMember.query.filter_by(
            table_id=self.table_id, user_id=user.id
        ).first()
        if not membership:
            return False
        
        # DM can always edit
        if membership.role == 'dm':
            return True
            
        # Check specific note permission
        permission = NotePermission.query.filter_by(
            note_id=self.id, user_id=user.id
        ).first()
        
        if permission:
            return permission.can_edit and permission.can_view
        
        # Default: table members can edit if they have general note access
        return membership.can_view_notes

    def __repr__(self):
        return f"<Note {self.title}>"


class DiceRoll(db.Model):
    __tablename__ = "dice_rolls"

    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("game_tables.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    dice_expression = db.Column(db.String(100), nullable=False)  # "2d6+3", "1d20"
    result = db.Column(db.Integer, nullable=False)
    individual_rolls = db.Column(db.JSON, nullable=False)  # [4, 2] for 2d6
    modifier = db.Column(db.Integer, default=0)
    has_advantage = db.Column(db.Boolean, default=False)
    has_disadvantage = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, default="")  # "Attack roll", "Damage", etc.
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User", backref="dice_rolls")
    table = db.relationship("GameTable", backref="dice_rolls")

    def __repr__(self):
        return f"<DiceRoll {self.dice_expression} = {self.result}>"


class InitiativeSession(db.Model):
    __tablename__ = "initiative_sessions"

    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("game_tables.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False, default="Combat Session")
    is_active = db.Column(db.Boolean, default=True)
    current_turn = db.Column(db.Integer, default=0)  # Index in sorted entries
    round_number = db.Column(db.Integer, default=1)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    table = db.relationship("GameTable", backref="initiative_sessions")
    entries = db.relationship(
        "InitiativeEntry", backref="session", lazy=True, cascade="all, delete-orphan"
    )

    def get_sorted_entries(self):
        """Get initiative entries sorted by initiative score (highest first)."""
        return sorted(self.entries, key=lambda x: x.initiative_score, reverse=True)

    def get_current_character(self):
        """Get the character whose turn it is."""
        sorted_entries = self.get_sorted_entries()
        if not sorted_entries or self.current_turn >= len(sorted_entries):
            return None
        return sorted_entries[self.current_turn]

    def next_turn(self):
        """Advance to next character's turn."""
        sorted_entries = self.get_sorted_entries()
        if not sorted_entries:
            return
        
        self.current_turn = (self.current_turn + 1) % len(sorted_entries)
        if self.current_turn == 0:
            self.round_number += 1

    def __repr__(self):
        return f"<InitiativeSession {self.name} (Round {self.round_number})>"


class InitiativeEntry(db.Model):
    __tablename__ = "initiative_entries"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("initiative_sessions.id"), nullable=False
    )
    character_name = db.Column(db.String(100), nullable=False)
    initiative_score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # NULL for NPCs/enemies
    custom_field = db.Column(db.String(100), default="")  # HP, AC, or custom tracking
    is_npc = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="initiative_entries")

    def __repr__(self):
        return f"<InitiativeEntry {self.character_name} ({self.initiative_score})>"
