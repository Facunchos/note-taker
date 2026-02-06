from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, GameTable, TableMember, User

tables_bp = Blueprint("tables", __name__, url_prefix="/tables")


@tables_bp.route("/")
@login_required
def my_tables():
    """List all tables the user owns or is a member of."""
    owned = GameTable.query.filter_by(owner_id=current_user.id).all()
    memberships = (
        TableMember.query.filter_by(user_id=current_user.id)
        .join(GameTable)
        .filter(GameTable.owner_id != current_user.id)
        .all()
    )
    joined = [m.table for m in memberships]
    return render_template("tables/list.html", owned=owned, joined=joined)


@tables_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new game table."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Table name is required.", "danger")
            return render_template("tables/create.html")

        table = GameTable(
            name=name,
            description=description,
            hash_code=GameTable.generate_hash_code(),
            owner_id=current_user.id,
        )
        db.session.add(table)
        db.session.flush()

        # Owner auto-joins as DM
        member = TableMember(
            user_id=current_user.id, table_id=table.id, role="dm", can_view_notes=True
        )
        db.session.add(member)
        db.session.commit()

        flash(
            f"Table '{name}' created! Share code: {table.hash_code}",
            "success",
        )
        return redirect(url_for("tables.detail", table_id=table.id))

    return render_template("tables/create.html")


@tables_bp.route("/join", methods=["GET", "POST"])
@login_required
def join():
    """Join a table using a hash code."""
    if request.method == "POST":
        code = request.form.get("hash_code", "").strip().upper()

        if not code:
            flash("Please enter a table code.", "danger")
            return render_template("tables/join.html")

        table = GameTable.query.filter_by(hash_code=code).first()
        if not table:
            flash("No table found with that code.", "danger")
            return render_template("tables/join.html", hash_code=code)

        if table.is_member(current_user):
            flash("You are already a member of this table.", "warning")
            return redirect(url_for("tables.detail", table_id=table.id))

        member = TableMember(
            user_id=current_user.id,
            table_id=table.id,
            role="player",
            can_view_notes=True,
        )
        db.session.add(member)
        db.session.commit()

        flash(f"You joined '{table.name}'!", "success")
        return redirect(url_for("tables.detail", table_id=table.id))

    return render_template("tables/join.html")


@tables_bp.route("/<int:table_id>")
@login_required
def detail(table_id):
    """View table details and its notes."""
    table = GameTable.query.get_or_404(table_id)

    if not table.is_member(current_user):
        flash("You are not a member of this table.", "danger")
        return redirect(url_for("tables.my_tables"))

    membership = TableMember.query.filter_by(
        user_id=current_user.id, table_id=table.id
    ).first()

    members = (
        TableMember.query.filter_by(table_id=table.id)
        .join(User)
        .all()
    )

    # Get all notes and filter by permissions
    all_notes = table.notes
    visible_notes = [note for note in all_notes if note.user_can_view(current_user)]

    return render_template(
        "tables/detail.html",
        table=table,
        members=members,
        notes=visible_notes,
        membership=membership,
        is_owner=table.is_owner(current_user),
    )


@tables_bp.route("/<int:table_id>/members/<int:member_id>/toggle-notes", methods=["POST"])
@login_required
def toggle_notes_access(table_id, member_id):
    """Owner toggles a member's ability to view notes."""
    table = GameTable.query.get_or_404(table_id)

    if not table.is_owner(current_user):
        flash("Only the table owner can manage members.", "danger")
        return redirect(url_for("tables.detail", table_id=table_id))

    member = TableMember.query.get_or_404(member_id)
    if member.table_id != table.id:
        flash("Member not found in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table_id))

    # Don't allow toggling own access
    if member.user_id == current_user.id:
        flash("You cannot change your own access.", "warning")
        return redirect(url_for("tables.detail", table_id=table_id))

    member.can_view_notes = not member.can_view_notes
    db.session.commit()

    status = "granted" if member.can_view_notes else "revoked"
    flash(f"Notes access {status} for {member.user.username}.", "info")
    return redirect(url_for("tables.detail", table_id=table_id))


@tables_bp.route("/<int:table_id>/members/<int:member_id>/kick", methods=["POST"])
@login_required
def kick_member(table_id, member_id):
    """Owner kicks a member from the table."""
    table = GameTable.query.get_or_404(table_id)

    if not table.is_owner(current_user):
        flash("Only the table owner can kick members.", "danger")
        return redirect(url_for("tables.detail", table_id=table_id))

    member = TableMember.query.get_or_404(member_id)
    if member.table_id != table.id:
        flash("Member not found in this table.", "danger")
        return redirect(url_for("tables.detail", table_id=table_id))

    if member.user_id == current_user.id:
        flash("You cannot kick yourself.", "warning")
        return redirect(url_for("tables.detail", table_id=table_id))

    username = member.user.username
    db.session.delete(member)
    db.session.commit()

    flash(f"{username} has been removed from the table.", "info")
    return redirect(url_for("tables.detail", table_id=table_id))


@tables_bp.route("/<int:table_id>/leave", methods=["POST"])
@login_required
def leave(table_id):
    """Player leaves a table voluntarily."""
    table = GameTable.query.get_or_404(table_id)

    if table.is_owner(current_user):
        flash("The owner cannot leave. Delete the table instead.", "warning")
        return redirect(url_for("tables.detail", table_id=table_id))

    member = TableMember.query.filter_by(
        user_id=current_user.id, table_id=table.id
    ).first()

    if not member:
        flash("You are not a member of this table.", "danger")
        return redirect(url_for("tables.my_tables"))

    db.session.delete(member)
    db.session.commit()

    flash(f"You left '{table.name}'.", "info")
    return redirect(url_for("tables.my_tables"))


@tables_bp.route("/<int:table_id>/delete", methods=["POST"])
@login_required
def delete(table_id):
    """Owner deletes the table."""
    table = GameTable.query.get_or_404(table_id)

    if not table.is_owner(current_user):
        flash("Only the table owner can delete it.", "danger")
        return redirect(url_for("tables.detail", table_id=table_id))

    name = table.name
    db.session.delete(table)
    db.session.commit()

    flash(f"Table '{name}' has been deleted.", "info")
    return redirect(url_for("tables.my_tables"))
