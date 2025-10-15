from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import Settings, NotificationLog, StockData
from stock_service import get_current_stock_price, get_stock_history
from sms_service import send_stock_notification
from werkzeug.security import generate_password_hash, check_password_hash
import logging

@app.route('/')
def index():
    """Homepage showing current stock data and recent notifications"""
    try:
        # Get current stock price
        current_price = get_current_stock_price()
        
        # Get recent notifications
        recent_notifications = NotificationLog.query.order_by(
            NotificationLog.sent_at.desc()
        ).limit(10).all()
        
        # Get recent stock data
        recent_stock_data = StockData.query.order_by(
            StockData.date.desc()
        ).limit(5).all()
        
        # Calculate daily percentage change
        daily_change_percent = None
        if recent_stock_data and len(recent_stock_data) >= 2 and current_price:
            # Get yesterday's close price
            yesterday_close = recent_stock_data[1].close_price if len(recent_stock_data) > 1 else None
            if yesterday_close:
                daily_change_percent = ((current_price - yesterday_close) / yesterday_close) * 100
        
        settings = Settings.get_settings()
        
        return render_template('index.html', 
                             current_price=current_price,
                             daily_change_percent=daily_change_percent,
                             recent_notifications=recent_notifications,
                             recent_stock_data=recent_stock_data,
                             settings=settings)
    except Exception as e:
        logging.error(f"Error loading homepage: {e}")
        flash('Error loading stock data. Please try again later.', 'error')
        return render_template('index.html', 
                             current_price=None,
                             daily_change_percent=None,
                             recent_notifications=[],
                             recent_stock_data=[],
                             settings=Settings.get_settings())

def check_settings_access():
    """Check if user has access to settings"""
    settings_obj = Settings.get_settings()
    if settings_obj.has_password_protection():
        return session.get('settings_authenticated', False)
    return True

@app.route('/settings/login', methods=['GET', 'POST'])
def settings_login():
    """Login page for password-protected settings"""
    settings_obj = Settings.get_settings()
    
    if not settings_obj.has_password_protection():
        return redirect(url_for('settings'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_password_hash(settings_obj.settings_password_hash, password):
            session['settings_authenticated'] = True
            flash('Access granted!', 'success')
            return redirect(url_for('settings'))
        else:
            flash('Incorrect password. Please try again.', 'error')
    
    return render_template('settings_login.html')

@app.route('/settings/logout')
def settings_logout():
    """Logout from settings"""
    session.pop('settings_authenticated', None)
    flash('Logged out from settings.', 'info')
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Settings page for configuring phone numbers and notification preferences"""
    settings_obj = Settings.get_settings()
    
    # Check access if password protection is enabled
    if not check_settings_access():
        return redirect(url_for('settings_login'))
    
    if request.method == 'POST':
        try:
            # Handle password setup/change
            if 'new_password' in request.form:
                new_password = request.form.get('new_password', '').strip()
                confirm_password = request.form.get('confirm_password', '').strip()
                
                if new_password:
                    if new_password == confirm_password:
                        settings_obj.settings_password_hash = generate_password_hash(new_password)
                        flash('Password protection enabled!', 'success')
                    else:
                        flash('Passwords do not match.', 'error')
                        return render_template('settings.html', settings=settings_obj)
                else:
                    # Remove password protection
                    settings_obj.settings_password_hash = None
                    session.pop('settings_authenticated', None)
                    flash('Password protection disabled.', 'info')
            
            # Update phone numbers
            settings_obj.phone_number_1 = request.form.get('phone_number_1', '').strip()
            settings_obj.phone_number_2 = request.form.get('phone_number_2', '').strip()
            settings_obj.phone_number_3 = request.form.get('phone_number_3', '').strip()
            settings_obj.phone_number_4 = request.form.get('phone_number_4', '').strip()
            
            # Update notification settings
            settings_obj.notifications_enabled = 'notifications_enabled' in request.form
            settings_obj.market_open_time = request.form.get('market_open_time', '09:30')
            settings_obj.market_close_time = request.form.get('market_close_time', '16:00')
            
            db.session.commit()
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('settings'))
            
        except Exception as e:
            logging.error(f"Error updating settings: {e}")
            db.session.rollback()
            flash('Error updating settings. Please try again.', 'error')
    
    return render_template('settings.html', settings=settings_obj)

@app.route('/test-notification', methods=['POST'])
def test_notification():
    """Send a test notification to verify SMS functionality"""
    try:
        settings_obj = Settings.get_settings()
        
        phone_numbers = settings_obj.get_phone_numbers()
        if not phone_numbers:
            flash('Please configure at least one phone number first.', 'error')
            return redirect(url_for('settings'))
        
        # Get current stock price for test
        current_price = get_current_stock_price()
        if current_price is None:
            flash('Unable to fetch current stock price for test.', 'error')
            return redirect(url_for('settings'))
        
        # Send test notifications to all configured numbers
        sent_count = 0
        for phone_number in phone_numbers:
            try:
                send_stock_notification(phone_number, 'test', current_price)
                sent_count += 1
            except Exception as e:
                logging.error(f"Failed to send test notification to {phone_number}: {e}")
        
        if sent_count > 0:
            flash(f'Test notification sent to {sent_count} number(s)!', 'success')
        else:
            flash('Failed to send test notifications. Please check your Twilio configuration.', 'error')
            
    except Exception as e:
        logging.error(f"Error sending test notification: {e}")
        flash('Error sending test notification.', 'error')
    
    return redirect(url_for('settings'))

@app.route('/api/stock-data')
def api_stock_data():
    """API endpoint for current stock data"""
    try:
        current_price = get_current_stock_price()
        return jsonify({
            'success': True,
            'current_price': current_price,
            'symbol': 'CRWV'
        })
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/logs')
def logs():
    """View notification logs"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = NotificationLog.query.order_by(
        NotificationLog.sent_at.desc()
    ).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('logs.html', notifications=notifications)
