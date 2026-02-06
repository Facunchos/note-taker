from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, InitiativeSession, InitiativeEntry, GameTable, TableMember, User

initiative_bp = Blueprint("initiative", __name__, url_prefix="/initiative")


def check_dm_access(table_id):
    """Check if current user is DM of the table."""
    membership = TableMember.query.filter_by(
        table_id=table_id, user_id=current_user.id
    ).first()
    return membership and membership.role == 'dm'


@initiative_bp.route("/table/<int:table_id>")
@login_required
def table_initiative(table_id):
    """Show initiative tracker for a table (DM only)."""
    table = GameTable.query.get_or_404(table_id)
    
    # Check if user is DM
    if not check_dm_access(table_id):
        flash("Only the Dungeon Master can access the initiative tracker", "error")
        return redirect(url_for("tables.detail", table_id=table_id))
    
    # Get active session for this table
    active_session = InitiativeSession.query.filter_by(
        table_id=table_id, is_active=True
    ).first()
    
    # Get table members for quick adding
    table_members = db.session.query(User, TableMember).join(
        TableMember, User.id == TableMember.user_id
    ).filter(TableMember.table_id == table_id).all()
    
    return render_template(
        "initiative/tracker.html", 
        table=table, 
        session=active_session,
        table_members=table_members
    )


@initiative_bp.route("/session/create", methods=["POST"])
@login_required
def create_session():
    """Create new initiative session."""
    try:
        data = request.get_json() if request.is_json else request.form
        table_id = int(data.get("table_id"))
        session_name = data.get("name", "Combat Session").strip()
        
        if not check_dm_access(table_id):
            raise ValueError("Only the DM can create initiative sessions")
        
        # Deactivate any existing sessions
        InitiativeSession.query.filter_by(
            table_id=table_id, is_active=True
        ).update({"is_active": False})
        
        # Create new session
        session = InitiativeSession(
            table_id=table_id,
            name=session_name,
            is_active=True,
            current_turn=0,
            round_number=1
        )
        
        db.session.add(session)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                "success": True, 
                "session": {
                    "id": session.id,
                    "name": session.name,
                    "round": session.round_number
                }
            })
        else:
            flash(f"Started new initiative: {session_name}", "success")
            return redirect(url_for("initiative.table_initiative", table_id=table_id))
            
    except ValueError as e:
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        else:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.referrer or url_for("tables.my_tables"))


@initiative_bp.route("/session/<int:session_id>/add_character", methods=["POST"])
@login_required
def add_character(session_id):
    """Add character to initiative session."""
    try:
        session = InitiativeSession.query.get_or_404(session_id)
        
        if not check_dm_access(session.table_id):
            raise ValueError("Only the DM can add characters to initiative")
        
        data = request.get_json() if request.is_json else request.form
        character_name = data.get("name", "").strip()
        initiative_score = int(data.get("initiative", 0))
        custom_field = data.get("custom_field", "").strip()
        user_id = data.get("user_id")  # Optional - for player characters
        is_npc = data.get("is_npc", False) in [True, "true", "on"]
        
        if not character_name:
            raise ValueError("Character name is required")
        
        if initiative_score < 0 or initiative_score > 50:
            raise ValueError("Initiative score must be between 0 and 50")
        
        # Create entry
        entry = InitiativeEntry(
            session_id=session_id,
            character_name=character_name,
            initiative_score=initiative_score,
            user_id=int(user_id) if user_id and user_id != "null" else None,
            custom_field=custom_field,
            is_npc=is_npc
        )
        
        db.session.add(entry)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                "success": True,
                "entry": {
                    "id": entry.id,
                    "name": character_name,
                    "initiative": initiative_score,
                    "custom_field": custom_field,
                    "is_npc": is_npc
                }
            })
        else:
            flash(f"Added {character_name} to initiative", "success")
            return redirect(url_for("initiative.table_initiative", table_id=session.table_id))
            
    except ValueError as e:
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        else:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.referrer)


@initiative_bp.route("/entry/<int:entry_id>/update", methods=["POST"])
@login_required
def update_entry(entry_id):
    """Update initiative entry."""
    try:
        entry = InitiativeEntry.query.get_or_404(entry_id)
        session = entry.session
        
        if not check_dm_access(session.table_id):
            raise ValueError("Only the DM can update initiative entries")
        
        data = request.get_json() if request.is_json else request.form
        
        if "custom_field" in data:
            entry.custom_field = data.get("custom_field", "").strip()
        
        if "initiative" in data:
            new_init = int(data.get("initiative"))
            if new_init < 0 or new_init > 50:
                raise ValueError("Initiative score must be between 0 and 50")
            entry.initiative_score = new_init
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({"success": True})
        else:
            flash("Entry updated successfully", "success")
            return redirect(url_for("initiative.table_initiative", table_id=session.table_id))
            
    except ValueError as e:
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        else:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.referrer)


@initiative_bp.route("/entry/<int:entry_id>/delete", methods=["POST", "DELETE"])
@login_required
def delete_entry(entry_id):
    """Delete initiative entry."""
    try:
        entry = InitiativeEntry.query.get_or_404(entry_id)
        session = entry.session
        
        if not check_dm_access(session.table_id):
            raise ValueError("Only the DM can delete initiative entries")
        
        db.session.delete(entry)
        db.session.commit()
        
        if request.is_json:
            return jsonify({"success": True})
        else:
            flash("Character removed from initiative", "success")
            return redirect(url_for("initiative.table_initiative", table_id=session.table_id))
            
    except Exception as e:
        if request.is_json:
            return jsonify({"success": False, "error": "An error occurred"}), 500
        else:
            flash("An error occurred", "error")
            return redirect(request.referrer)


@initiative_bp.route("/session/<int:session_id>/sort")
@login_required
def sort_initiative(session_id):
    """Sort initiative entries by score (highest first)."""
    try:
        session = InitiativeSession.query.get_or_404(session_id)
        
        if not check_dm_access(session.table_id):
            raise ValueError("Only the DM can sort initiative")
        
        # Get sorted entries for display purposes
        sorted_entries = session.get_sorted_entries()
        
        if request.is_json:
            entries_data = [{
                "id": entry.id,
                "name": entry.character_name,
                "initiative": entry.initiative_score,
                "custom_field": entry.custom_field,
                "is_npc": entry.is_npc,
                "is_current": i == session.current_turn
            } for i, entry in enumerate(sorted_entries)]
            
            return jsonify({"success": True, "entries": entries_data})
        else:
            flash("Initiative order updated", "success")
            return redirect(url_for("initiative.table_initiative", table_id=session.table_id))
            
    except ValueError as e:
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        else:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.referrer)


@initiative_bp.route("/session/<int:session_id>/next_turn", methods=["POST"])
@login_required
def next_turn(session_id):
    """Advance to next character's turn."""
    try:
        session = InitiativeSession.query.get_or_404(session_id)
        
        if not check_dm_access(session.table_id):
            raise ValueError("Only the DM can advance turns")
        
        session.next_turn()
        db.session.commit()
        
        current_character = session.get_current_character()
        
        if request.is_json:
            return jsonify({
                "success": True,
                "current_turn": session.current_turn,
                "round": session.round_number,
                "current_character": {
                    "name": current_character.character_name if current_character else None,
                    "initiative": current_character.initiative_score if current_character else None
                } if current_character else None
            })
        else:
            if current_character:
                flash(f"It's now {current_character.character_name}'s turn (Round {session.round_number})", "info")
            else:
                flash(f"Round {session.round_number} started", "info")
            return redirect(url_for("initiative.table_initiative", table_id=session.table_id))
            
    except ValueError as e:
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        else:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.referrer)


@initiative_bp.route("/session/<int:session_id>/end", methods=["POST"])
@login_required
def end_session(session_id):
    """End initiative session."""
    try:
        session = InitiativeSession.query.get_or_404(session_id)
        
        if not check_dm_access(session.table_id):
            raise ValueError("Only the DM can end initiative sessions")
        
        session.is_active = False
        db.session.commit()
        
        if request.is_json:
            return jsonify({"success": True})
        else:
            flash("Initiative session ended", "success")
            return redirect(url_for("initiative.table_initiative", table_id=session.table_id))
            
    except ValueError as e:
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        else:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.referrer)