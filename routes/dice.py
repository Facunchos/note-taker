import random
import re
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, DiceRoll, GameTable, TableMember

dice_bp = Blueprint("dice", __name__, url_prefix="/dice")


def parse_dice_expression(expression):
    """
    Parse dice expression like '2d6+3' or '1d20'.
    Returns: (num_dice, die_type, modifier)
    """
    # Clean the expression
    expression = expression.strip().lower().replace(" ", "")
    
    # Pattern for XdY+Z or XdY-Z or XdY
    pattern = r'^(\d+)d(\d+)([+-]\d+)?$'
    match = re.match(pattern, expression)
    
    if not match:
        raise ValueError("Invalid dice expression. Use format like '2d6+3' or '1d20'")
    
    num_dice = int(match.group(1))
    die_type = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    # Validate ranges
    if num_dice <= 0 or num_dice > 20:
        raise ValueError("Number of dice must be between 1 and 20")
    
    if die_type not in [4, 6, 8, 10, 12, 20, 100]:
        raise ValueError("Die type must be one of: d4, d6, d8, d10, d12, d20, d100")
    
    return num_dice, die_type, modifier


def roll_dice(num_dice, die_type, modifier=0, has_advantage=False, has_disadvantage=False):
    """
    Roll dice with optional advantage/disadvantage.
    Returns: (individual_rolls, total_result)
    """
    rolls = []
    
    for _ in range(num_dice):
        if has_advantage or has_disadvantage:
            # Roll twice for advantage/disadvantage
            roll1 = random.randint(1, die_type)
            roll2 = random.randint(1, die_type)
            
            if has_advantage:
                final_roll = max(roll1, roll2)
                rolls.append({"rolls": [roll1, roll2], "final": final_roll, "type": "advantage"})
            else:  # disadvantage
                final_roll = min(roll1, roll2)
                rolls.append({"rolls": [roll1, roll2], "final": final_roll, "type": "disadvantage"})
        else:
            roll = random.randint(1, die_type)
            rolls.append({"rolls": [roll], "final": roll, "type": "normal"})
    
    # Calculate total
    total = sum(roll["final"] for roll in rolls) + modifier
    
    return rolls, total


@dice_bp.route("/")
@login_required
def index():
    """Global dice roller interface."""
    return render_template("dice/interface.html")


@dice_bp.route("/roll", methods=["POST"])
@login_required
def roll():
    """Process a dice roll request."""
    try:
        data = request.get_json() if request.is_json else request.form
        
        expression = data.get("expression", "").strip()
        description = data.get("description", "").strip()
        has_advantage = data.get("advantage", False) in [True, "true", "on"]
        has_disadvantage = data.get("disadvantage", False) in [True, "true", "on"]
        table_id = data.get("table_id")  # Optional - for table-specific rolls
        
        if not expression:
            raise ValueError("Dice expression is required")
        
        # Parse and validate expression
        num_dice, die_type, modifier = parse_dice_expression(expression)
        
        # Roll the dice
        individual_rolls, result = roll_dice(
            num_dice, die_type, modifier, has_advantage, has_disadvantage
        )
        
        # Check table access if table_id provided
        if table_id:
            table = GameTable.query.get_or_404(table_id)
            membership = TableMember.query.filter_by(
                table_id=table_id, user_id=current_user.id
            ).first()
            if not membership:
                raise ValueError("You don't have access to this table")
        
        # Save roll to database
        dice_roll = DiceRoll(
            table_id=int(table_id) if table_id else None,
            user_id=current_user.id,
            dice_expression=expression,
            result=result,
            individual_rolls=individual_rolls,
            modifier=modifier,
            has_advantage=has_advantage,
            has_disadvantage=has_disadvantage,
            description=description
        )
        
        db.session.add(dice_roll)
        db.session.commit()
        
        # Return result
        roll_data = {
            "id": dice_roll.id,
            "expression": expression,
            "description": description,
            "individual_rolls": individual_rolls,
            "modifier": modifier,
            "result": result,
            "has_advantage": has_advantage,
            "has_disadvantage": has_disadvantage,
            "user": current_user.username,
            "created_at": dice_roll.created_at.isoformat()
        }
        
        if request.is_json:
            return jsonify({"success": True, "roll": roll_data})
        else:
            flash(f"🎲 {expression} = {result} ({current_user.username})", "success")
            return redirect(request.referrer or url_for("dice.index"))
            
    except ValueError as e:
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        else:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.referrer or url_for("dice.index"))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({"success": False, "error": "An unexpected error occurred"}), 500
        else:
            flash("An unexpected error occurred", "error")
            return redirect(request.referrer or url_for("dice.index"))


@dice_bp.route("/history")
@login_required
def history():
    """Show dice roll history (global for user)."""
    rolls = DiceRoll.query.filter_by(
        user_id=current_user.id, table_id=None
    ).order_by(DiceRoll.created_at.desc()).limit(50).all()
    
    return render_template("dice/history.html", rolls=rolls)


@dice_bp.route("/table/<int:table_id>/history")
@login_required
def table_history(table_id):
    """Show dice roll history for a specific table."""
    # Check table access
    table = GameTable.query.get_or_404(table_id)
    membership = TableMember.query.filter_by(
        table_id=table_id, user_id=current_user.id
    ).first()
    
    if not membership:
        flash("You don't have access to this table", "error")
        return redirect(url_for("tables.list"))
    
    # Get all rolls for this table
    rolls = DiceRoll.query.filter_by(table_id=table_id).order_by(
        DiceRoll.created_at.desc()
    ).limit(100).all()
    
    return render_template("dice/table_history.html", rolls=rolls, table=table)


@dice_bp.route("/quick/<dice_type>")
@login_required
def quick_roll(dice_type):
    """Quick roll for common dice types."""
    try:
        # Validate dice type
        if dice_type not in ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]:
            raise ValueError("Invalid dice type")
        
        expression = f"1{dice_type}"
        table_id = request.args.get("table_id")
        
        # Parse and roll
        num_dice, die_type, modifier = parse_dice_expression(expression)
        individual_rolls, result = roll_dice(num_dice, die_type, modifier)
        
        # Save to database
        dice_roll = DiceRoll(
            table_id=int(table_id) if table_id else None,
            user_id=current_user.id,
            dice_expression=expression,
            result=result,
            individual_rolls=individual_rolls,
            modifier=0,
            description=f"Quick {dice_type} roll"
        )
        
        db.session.add(dice_roll)
        db.session.commit()
        
        flash(f"🎲 {dice_type}: {result}", "success")
        return redirect(request.referrer or url_for("dice.index"))
        
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(request.referrer or url_for("dice.index"))