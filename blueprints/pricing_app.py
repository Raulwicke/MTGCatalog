from moneyed import Money, USD
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from flask_login import login_required

from db_files.standard.score_db import score_read_all
from db_files.standard.outlaws_db import outlaws_read_all
from db_files.standard.murders_db import murders_read_all
from db_files.standard.standard_db import batch_update_card_prices

pricing_bp = Blueprint('pricing', __name__, template_folder='templates', static_folder='static')

@login_required
@pricing_bp.route('/collections/pricing', methods=['GET'])
def pricing():
    try:
        big = score_read_all()
        mkm = murders_read_all()
        otj = outlaws_read_all()

        big_val = Money(0, USD)
        big_high_val = Money(0, USD)
        mkm_val = Money(0, USD)
        mkm_high_val = Money(0, USD)
        otj_val = Money(0, USD)
        otj_high_val = Money(0, USD)

        for row in big:
            price = row[6] if row[6] else 0  # Handle missing price
            try:
                price = Decimal(price)
            except Exception:
                price = Decimal(0)
            big_val += Money(row[1] * price, USD)
            if price > 2:
                big_high_val += Money(row[1] * price, USD)

        for row in mkm:
            price = row[6] if row[6] else 0
            try:
                price = Decimal(price)
            except Exception:
                price = Decimal(0)
            mkm_val += Money(row[1] * price, USD)
            if price > 2:
                mkm_high_val += Money(row[1] * price, USD)

        for row in otj:
            price = row[6] if row[6] else 0
            try:
                price = Decimal(price)
            except Exception:
                price = Decimal(0)
            otj_val += Money(row[1] * price, USD)
            if price > 2:
                otj_high_val += Money(row[1] * price, USD)

        # Debug Logging
        current_app.logger.debug(f"DEBUG: otj_val = {otj_val}, otj_high_val = {otj_high_val}")
        current_app.logger.debug(f"DEBUG: mkm_val = {mkm_val}, mkm_high_val = {mkm_high_val}")
        current_app.logger.debug(f"DEBUG: big_val = {big_val}, big_high_val = {big_high_val}")

        return render_template(
            'utils/pricing.html',
            otj_high_val=otj_high_val,
            otj_val=otj_val,
            mkm_high_val=mkm_high_val,
            mkm_val=mkm_val,
            big_high_val=big_high_val,
            big_val=big_val,
        )
    except Exception as e:
        current_app.logger.error(f"ERROR: {e}")
        return "An error occurred while rendering the pricing page.", 500

@pricing_bp.route('/process_update_pricing', methods=['POST'])
def process_update_pricing():
    batch_update_card_prices('outlaws')
    batch_update_card_prices('murders')
    batch_update_card_prices('score')
    
    return redirect(url_for('pricing'))
