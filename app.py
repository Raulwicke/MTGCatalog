from flask import Flask, render_template, redirect, request, url_for, flash
from database import planeswalker_read_all, planeswalker_update
from image_fix import process_updated_images

import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')

@app.route('/')
def catalog():
    # Retrieve all planeswalkers
    planeswalkers = planeswalker_read_all()
    
    # Format data for the template
    planeswalkers_data = [
        {
            'name': row[0],
            'collected': row[1],
            'image_url': row[4],
            'greyscale': not row[1]  # True if not collected, for grayscale filtering
        }
        for row in planeswalkers
    ]
    
    return render_template('catalog.html', planeswalkers=planeswalkers_data)

@app.route('/update_planeswalkers', methods=['GET', 'POST'])
def update_planeswalkers():
    if request.method == 'POST':
        name = request.form['name']
        collected = request.form['collected'] == 'true'
        collected_set = request.form['collected_set']
        planeswalker_update(name, collected, collected_set)
        # print(f"Name: {name}, Collected: {collected}, Set: {collected_set}")  # Debugging   
        process_updated_images(name, collected_set)
        flash(f'{name} updated successfully!', 'success')
        return redirect(url_for('update_planeswalkers'))
    
    planeswalkers = planeswalker_read_all()
    return render_template('update_planeswalkers.html', planeswalkers=planeswalkers)


if __name__ == '__main__':
    app.run(debug=False)
    
