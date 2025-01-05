import csv, io

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from utils.image_fix import process_updated_images

from db_files.standard.score_db import (
    score_read_all, 
    update_score_card, 
    score_advanced_search,
)

scores_bp = Blueprint('scores', __name__, template_folder='templates', static_folder='static')


@scores_bp.route('/collections/big', methods=['GET'])
def score():
    score = score_read_all()

    name = request.args.get('name', '').strip()
    collected = request.args.get('collected', '').strip()
    set_code = request.args.get('full_set', '').strip()

    score = score_advanced_search(name, collected, set_code)

    score_data = [
        {
            'name': row[0],
            'collected': row[1],
            'collector_number': row[3],
            'image_url': row[4],
            'greyscale': not row[1],  # True if not collected, for grayscale filtering
            'price':row[5]
        }
        for row in score
    ]
    return render_template('score/score.html', score=score_data, show_search_tab=True, show_update_button=True, update_url='/update_score')
     

@scores_bp.route('/update_score', methods=['GET'])
@login_required
def update_score():
    score = score_read_all()
    # print(outlaws)
  # Replace with your DB fetch logic
    return render_template('score/update_score.html', score=score)



@scores_bp.route('/process_update_score', methods=['POST'])
@login_required
def process_update_score():
    try:
        updates = request.form.to_dict(flat=True)  # Convert form data to dictionary
        # print(updates)  # Debugging: Check structure of form data

        # Iterate over the form data and update each card in the database
        for collector_number, collected_count in updates.items():
            update_score_card(collector_number, int(collected_count))  # Use collector_number to update database

        flash("Score collection updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating score: {str(e)}", "danger")
    return redirect(url_for('update_score'))

