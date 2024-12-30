from db_files.standard_db import 

def outlaws():
    outlaws = outlaws_read_all()

    name = request.args.get('name', '').strip()
    collected = request.args.get('collected', '').strip()
    set_code = request.args.get('full_set', '').strip()
    rarity = request.args.get('rarity', '').strip()

    # Build search query
    outlaws = outlaws_advanced_search(name, collected, set_code, rarity)

    outlaws_data = [
        {
            'name': row[0],
            'collected': row[1],
            'collector_number': row[3],
            'image_url': row[4],
            'rarity': row[5],
            'greyscale': not row[1]  # True if not collected, for grayscale filtering
        }
        for row in outlaws
    ]
    return render_template('outlaws.html', outlaws=outlaws_data)
