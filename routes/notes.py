from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, GameTable, TableMember, Note
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
    """Verify user is a member of the table and has note access."""
    table = GameTable.query.get_or_404(table_id)
    membership = TableMember.query.filter_by(
        user_id=current_user.id, table_id=table.id
    ).first()

    if not membership:
        return None, None, "You are not a member of this table."

    if not membership.can_view_notes:
        return table, membership, "You don't have permission to view notes."

    return table, membership, None


@notes_bp.route("/create", methods=["GET", "POST"])
@login_required
def create(table_id):
    """Create a new note in a table."""
    table, membership, error = check_table_access(table_id)
    if error:
        flash(error, "danger")
        return redirect(url_for("tables.my_tables"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
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

    # Render markdown content safely
    raw_html = markdown.markdown(
        note.content, extensions=["tables", "fenced_code", "nl2br"]
    )
    rendered = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)

    return render_template(
        "notes/view.html", table=table, note=note, rendered_content=rendered
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

    if request.method == "POST":
        title = request.form.get("title", "").strip()
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
        content=note.content,
        bg_color=note.bg_color,
        text_color=note.text_color,
        font_size=str(note.font_size),
    )


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

    db.session.delete(note)
    db.session.commit()

    flash("Note deleted.", "info")
    return redirect(url_for("tables.detail", table_id=table.id))
