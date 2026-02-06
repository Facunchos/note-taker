from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
import secrets
import string

db = SQLAlchemy()


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
    content = db.Column(db.Text, default="")
    bg_color = db.Column(db.String(7), default="#ffffff")
    text_color = db.Column(db.String(7), default="#1a1a2e")
    font_size = db.Column(db.Integer, default=16)  # in pixels
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Note {self.title}>"
