from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, GameTable, TableMember, Note, NotePermission
import markdown
import bleach

notes_bp = Blueprint("notes", __name__, url_prefix="/tables/<int:table_id>/notes")

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "s", "del",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "code", "pre",
    "a", "hr", "img", "table", "thead", "tbody", "tr", "th", "td",
]
ALLOWED_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
}


def check_table_access(table_id):
    """Verify user is a member of the table."""
    table = GameTable.query.get_or_404(table_id)
    membership = TableMember.query.filter_by(
        user_id=current_user.id, table_id=table.id
    ).first()

    if not membership:
        return table, None, "You are not a member of this table."

    return table, membership, None


@notes_bp.route("/create", methods=["GET", "POST"])
@login_required
def create(table_id):
    """Create a new note in a table."""
    table, membership, error = check_table_access(table_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("tables.my_tables"))

    # Check if user can create notes (general table permission)
    if not membership.can_view_notes:
        flash("You don't have permission to create notes in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table_id))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        content = request.form.get("content", "")
        bg_color = request.form.get("bg_color", "#ffffff")
        text_color = request.form.get("text_color", "#1a1a2e")
        font_size = request.form.get("font_size", "16")

        if not title:
            flash("Note title is required.", "danger")
            return render_template(
                "notes/editor.html",
                table=table,
                mode="create",
                description=description,
                content=content,
                bg_color=bg_color,
                text_color=text_color,
                font_size=font_size,
            )

        try:
            font_size = max(10, min(32, int(font_size)))
        except (ValueError, TypeError):
            font_size = 16

        note = Note(
            table_id=table.id,
            author_id=current_user.id,
            title=title,
            description=description,
            content=content,
            bg_color=bg_color,
            text_color=text_color,
            font_size=font_size,
        )
        db.session.add(note)
        db.session.commit()

        flash("Note created!", "success")
        return redirect(url_for("tables.detail", table_id=table.id))

    return render_template(
        "notes/editor.html",
        table=table,
        mode="create",
        bg_color="#ffffff",
        text_color="#1a1a2e",
        font_size="16",
    )


@notes_bp.route("/<int:note_id>")
@login_required
def view(table_id, note_id):
    """View a single note with rendered markdown."""
    table, membership, error = check_table_access(table_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("tables.my_tables"))

    note = Note.query.get_or_404(note_id)
    if note.table_id != table.id:
        flash("Note not found in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table.id))

    # Check if user can view this note
    if not note.user_can_view(current_user):
        flash("You don't have permission to view this note.", "danger")
        return redirect(url_for("tables.detail", table_id=table.id))

    # Render markdown content safely
    raw_html = markdown.markdown(
        note.content, extensions=["tables", "fenced_code", "nl2br"]
    )
    rendered = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)

    # Check permissions for actions
    can_edit = note.user_can_edit(current_user)
    can_manage_permissions = (membership.role == 'dm' or note.author_id == current_user.id)

    return render_template(
        "notes/view.html", 
        table=table, 
        note=note, 
        rendered_content=rendered,
        can_edit=can_edit,
        can_manage_permissions=can_manage_permissions
    )


@notes_bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit(table_id, note_id):
    """Edit an existing note."""
    table, membership, error = check_table_access(table_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("tables.my_tables"))

    note = Note.query.get_or_404(note_id)
    if note.table_id != table.id:
        flash("Note not found in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table.id))

    # Check if user can edit this note
    if not note.user_can_edit(current_user):
        flash("You don't have permission to edit this note.", "danger")
        return redirect(url_for("notes.view", table_id=table.id, note_id=note.id))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        content = request.form.get("content", "")
        bg_color = request.form.get("bg_color", note.bg_color)
        text_color = request.form.get("text_color", note.text_color)
        font_size = request.form.get("font_size", str(note.font_size))

        if not title:
            flash("Note title is required.", "danger")
            return render_template(
                "notes/editor.html",
                table=table,
                note=note,
                mode="edit",
                description=description,
                content=content,
                bg_color=bg_color,
                text_color=text_color,
                font_size=font_size,
            )

        try:
            font_size = max(10, min(32, int(font_size)))
        except (ValueError, TypeError):
            font_size = note.font_size

        note.title = title
        note.description = description
        note.content = content
        note.bg_color = bg_color
        note.text_color = text_color
        note.font_size = font_size
        db.session.commit()

        flash("Note updated!", "success")
        return redirect(
            url_for("notes.view", table_id=table.id, note_id=note.id)
        )

    return render_template(
        "notes/editor.html",
        table=table,
        note=note,
        mode="edit",
        description=note.description,
        content=note.content,
        bg_color=note.bg_color,
        text_color=note.text_color,
        font_size=str(note.font_size),
    )


@notes_bp.route("/<int:note_id>/duplicate", methods=["POST"])
@login_required
def duplicate(table_id, note_id):
    """Duplicate a note with a new name."""
    table, membership, error = check_table_access(table_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("tables.my_tables"))

    original_note = Note.query.get_or_404(note_id)
    if original_note.table_id != table.id:
        flash("Note not found in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table.id))

    # Check if user can view the original note
    if not original_note.user_can_view(current_user):
        flash("You don't have permission to duplicate this note.", "danger")
        return redirect(url_for("tables.detail", table_id=table.id))

    new_title = request.form.get("new_title", "").strip()
    if not new_title:
        flash("New title is required for duplication.", "danger")
        return redirect(url_for("notes.view", table_id=table.id, note_id=note_id))

    # Create duplicate
    duplicate_note = Note(
        table_id=table.id,
        author_id=current_user.id,
        title=new_title,
        description=original_note.description,
        content=original_note.content,
        bg_color=original_note.bg_color,
        text_color=original_note.text_color,
        font_size=original_note.font_size,
        original_note_id=original_note.id,
    )
    db.session.add(duplicate_note)
    db.session.commit()

    flash(f"Note duplicated as '{new_title}'!", "success")
    return redirect(url_for("notes.view", table_id=table.id, note_id=duplicate_note.id))


@notes_bp.route("/<int:note_id>/permissions", methods=["GET", "POST"])
@login_required
def manage_permissions(table_id, note_id):
    """Manage permissions for a specific note (DM only)."""
    table, membership, error = check_table_access(table_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("tables.my_tables"))

    note = Note.query.get_or_404(note_id)
    if note.table_id != table.id:
        flash("Note not found in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table.id))

    # Only DM or note author can manage permissions
    if membership.role != 'dm' and note.author_id != current_user.id:
        flash("Only the DM or note author can manage permissions.", "danger")
        return redirect(url_for("notes.view", table_id=table.id, note_id=note.id))

    if request.method == "POST":
        user_id = request.form.get("user_id")
        can_view = request.form.get("can_view") == "on"
        can_edit = request.form.get("can_edit") == "on"

        if not user_id:
            flash("Please select a user.", "danger")
            return redirect(url_for("notes.manage_permissions", table_id=table.id, note_id=note.id))

        # Check if user is table member
        target_membership = TableMember.query.filter_by(
            table_id=table.id, user_id=user_id
        ).first()
        
        if not target_membership:
            flash("User is not a member of this table.", "danger")
            return redirect(url_for("notes.manage_permissions", table_id=table.id, note_id=note.id))

        # Get or create permission
        permission = NotePermission.query.filter_by(
            note_id=note.id, user_id=user_id
        ).first()

        if not permission:
            permission = NotePermission(
                note_id=note.id,
                user_id=user_id,
                granted_by=current_user.id
            )
            db.session.add(permission)

        permission.can_view = can_view
        permission.can_edit = can_edit and can_view  # Can't edit without view
        db.session.commit()

        flash("Permissions updated!", "success")
        return redirect(url_for("notes.manage_permissions", table_id=table.id, note_id=note.id))

    # Get table members and their current permissions
    members = TableMember.query.filter_by(table_id=table.id).join(
        TableMember.user
    ).all()
    
    # Get existing permissions for this note
    permissions = {p.user_id: p for p in note.permissions}

    return render_template(
        "notes/permissions.html",
        table=table,
        note=note,
        members=members,
        permissions=permissions,
    )


@notes_bp.route("/<int:note_id>/permissions/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_permission(table_id, note_id, user_id):
    """Remove specific permission and revert to default."""
    table, membership, error = check_table_access(table_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("tables.my_tables"))

    note = Note.query.get_or_404(note_id)
    if note.table_id != table.id:
        flash("Note not found in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table.id))

    # Only DM or note author can manage permissions
    if membership.role != 'dm' and note.author_id != current_user.id:
        flash("Only the DM or note author can manage permissions.", "danger")
        return redirect(url_for("notes.view", table_id=table.id, note_id=note.id))

    permission = NotePermission.query.filter_by(
        note_id=note.id, user_id=user_id
    ).first()

    if permission:
        db.session.delete(permission)
        db.session.commit()
        flash("Permission removed. User reverted to default table permissions.", "info")
    else:
        flash("No specific permission found for this user.", "warning")

    return redirect(url_for("notes.manage_permissions", table_id=table.id, note_id=note.id))


@notes_bp.route("/<int:note_id>/delete", methods=["POST"])
@login_required
def delete(table_id, note_id):
    """Delete a note."""
    table, membership, error = check_table_access(table_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("tables.my_tables"))

    note = Note.query.get_or_404(note_id)
    if note.table_id != table.id:
        flash("Note not found in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table.id))

    # Check if user can edit (required for delete)
    if not note.user_can_edit(current_user):
        flash("You don't have permission to delete this note.", "danger")
        return redirect(url_for("notes.view", table_id=table.id, note_id=note.id))

    db.session.delete(note)
    db.session.commit()

    flash("Note deleted.", "info")
    return redirect(url_for("tables.detail", table_id=table.id))
