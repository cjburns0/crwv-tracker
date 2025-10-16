from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import Settings, NotificationLog, StockData, User
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
        
        # Check if market is open
        from stock_service import is_market_open
        market_open = is_market_open()
        
        # Get current Eastern time and market countdown
        import pytz
        from datetime import datetime, timedelta
        
        eastern = pytz.timezone('US/Eastern')
        now_eastern = datetime.now(eastern)
        current_time_est = now_eastern.strftime('%I:%M %p ET')
        
        # Calculate time until market opens
        market_open_time = None
        hours_until_open = None
        
        if not market_open:
            # Find next market open time
            next_open = now_eastern.replace(hour=9, minute=30, second=0, microsecond=0)
            
            # If it's past 4 PM today, market opens tomorrow
            if now_eastern.hour >= 16:
                next_open += timedelta(days=1)
            
            # Skip weekends
            while next_open.weekday() >= 5:  # Saturday = 5, Sunday = 6
                next_open += timedelta(days=1)
            
            # Calculate hours until market opens
            time_diff = next_open - now_eastern
            hours_until_open = time_diff.total_seconds() / 3600
            market_open_time = next_open.strftime('%I:%M %p ET')
        
        # Get recent notifications
        recent_notifications = NotificationLog.query.order_by(
            NotificationLog.sent_at.desc()
        ).limit(10).all()
        
        # Get recent stock data
        recent_stock_data = StockData.query.order_by(
            StockData.date.desc()
        ).limit(5).all()
        
        # Calculate daily percentage change vs yesterday's close
        daily_change_percent = None
        yesterday_close = None
        
        # Calculate 7-day percentage change
        weekly_change_percent = None
        week_ago_close = None
        
        if current_price:
            from datetime import date, timedelta
            from stock_service import get_daily_stock_data
            
            # Get today's close price (use current price if market is open, or today's close if market is closed)
            today_close = current_price
            if not market_open:
                # Market is closed, try to get today's close price from database or fetch it
                today_data = StockData.query.filter_by(date=date.today()).first()
                if today_data and today_data.close_price:
                    today_close = today_data.close_price
                else:
                    # Fetch today's close price
                    today_stock_data = get_daily_stock_data()
                    if today_stock_data and today_stock_data.get('close'):
                        today_close = today_stock_data['close']
            
            # Daily change calculation
            yesterday = date.today() - timedelta(days=1)
            
            # Skip weekends - get last trading day
            while yesterday.weekday() >= 5:  # Saturday = 5, Sunday = 6
                yesterday -= timedelta(days=1)
            
            yesterday_data = StockData.query.filter_by(date=yesterday).first()
            
            if yesterday_data and yesterday_data.close_price:
                yesterday_close = yesterday_data.close_price
            elif recent_stock_data and len(recent_stock_data) >= 2:
                # Fallback to most recent close price
                yesterday_close = recent_stock_data[1].close_price
            
            if yesterday_close:
                daily_change_percent = ((today_close - yesterday_close) / yesterday_close) * 100
                logging.info(f"Daily change calculated: {daily_change_percent:.2f}% (today close: {today_close}, yesterday close: {yesterday_close})")
            else:
                logging.warning(f"No yesterday close price found for daily change calculation")
            
            # Weekly change calculation (7 trading days ago)
            week_ago = date.today() - timedelta(days=7)
            
            # Skip weekends to get 7 trading days ago
            trading_days_back = 0
            while trading_days_back < 7:
                if week_ago.weekday() < 5:  # Monday-Friday
                    trading_days_back += 1
                if trading_days_back < 7:
                    week_ago -= timedelta(days=1)
            
            week_ago_data = StockData.query.filter_by(date=week_ago).first()
            
            if week_ago_data and week_ago_data.close_price:
                week_ago_close = week_ago_data.close_price
            elif recent_stock_data and len(recent_stock_data) >= 7:
                # Fallback to 7th most recent close price
                week_ago_close = recent_stock_data[6].close_price
            
            if week_ago_close:
                weekly_change_percent = ((current_price - week_ago_close) / week_ago_close) * 100
        
        settings = Settings.get_settings()
        
        return render_template('index.html', 
                             current_price=current_price,
                             daily_change_percent=daily_change_percent,
                             weekly_change_percent=weekly_change_percent,
                             market_open=market_open,
                             current_time_est=current_time_est,
                             market_open_time=market_open_time,
                             hours_until_open=hours_until_open,
                             recent_notifications=recent_notifications,
                             recent_stock_data=recent_stock_data,
                             settings=settings)
    except Exception as e:
        logging.error(f"Error loading homepage: {e}")
        flash('Error loading stock data. Please try again later.', 'error')
        return render_template('index.html', 
                             current_price=None,
                             daily_change_percent=None,
                             weekly_change_percent=None,
                             market_open=False,
                             current_time_est="Unknown",
                             market_open_time=None,
                             hours_until_open=None,
                             recent_notifications=[],
                             recent_stock_data=[],
                             settings=Settings.get_settings())

def check_settings_access():
    """Check if user has access to settings"""
    settings_obj = Settings.get_settings()
    if settings_obj.has_password_protection():
        return session.get('settings_authenticated', False)
    return True

def check_user_access(user_id):
    """Check if user has access to their specific settings"""
    return session.get('user_authenticated', {}).get(str(user_id), False)

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

@app.route('/user/login/<int:user_id>', methods=['GET', 'POST'])
def user_login(user_id):
    """Login page for individual user settings"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_password_hash(user.password_hash, password):
            if 'user_authenticated' not in session:
                session['user_authenticated'] = {}
            session['user_authenticated'][str(user_id)] = True
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('user_settings', user_id=user_id))
        else:
            flash('Incorrect password. Please try again.', 'error')
    
    return render_template('user_login.html', user=user)

@app.route('/user/logout/<int:user_id>')
def user_logout(user_id):
    """Logout from user settings"""
    if 'user_authenticated' in session:
        session['user_authenticated'].pop(str(user_id), None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/user/settings/<int:user_id>', methods=['GET', 'POST'])
def user_settings(user_id):
    """Individual user settings page"""
    user = User.query.get_or_404(user_id)
    
    # Check access
    if not check_user_access(user_id):
        return redirect(url_for('user_login', user_id=user_id))
    
    if request.method == 'POST':
        try:
            # Handle password change
            if 'new_password' in request.form:
                new_password = request.form.get('new_password', '').strip()
                confirm_password = request.form.get('confirm_password', '').strip()
                
                if new_password:
                    if new_password == confirm_password:
                        user.password_hash = generate_password_hash(new_password)
                        flash('Password updated successfully!', 'success')
                    else:
                        flash('Passwords do not match.', 'error')
                        return render_template('user_settings.html', user=user)
                else:
                    flash('Password cannot be empty.', 'error')
                    return render_template('user_settings.html', user=user)
            
            # Update phone number
            new_phone = request.form.get('phone_number', '').strip()
            if new_phone and new_phone != user.phone_number:
                # Check if phone number is already taken
                existing_user = User.query.filter_by(phone_number=new_phone).first()
                if existing_user and existing_user.id != user.id:
                    flash('This phone number is already registered to another user.', 'error')
                    return render_template('user_settings.html', user=user)
                user.phone_number = new_phone
            
            # Update name
            new_name = request.form.get('name', '').strip()
            if new_name:
                user.name = new_name
            
            db.session.commit()
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('user_settings', user_id=user_id))
            
        except Exception as e:
            logging.error(f"Error updating user settings: {e}")
            db.session.rollback()
            flash('Error updating settings. Please try again.', 'error')
    
    return render_template('user_settings.html', user=user)

@app.route('/users')
def users():
    """List all users"""
    users_list = User.query.filter_by(is_active=True).all()
    return render_template('users.html', users=users_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            phone_number = request.form.get('phone_number', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validation
            if not name or not phone_number or not password:
                flash('All fields are required.', 'error')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('register.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return render_template('register.html')
            
            # Check if phone number already exists
            existing_user = User.query.filter_by(phone_number=phone_number).first()
            if existing_user:
                flash('This phone number is already registered.', 'error')
                return render_template('register.html')
            
            # Create new user
            user = User(
                name=name,
                phone_number=phone_number,
                password_hash=generate_password_hash(password),
                is_active=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Welcome, {name}! Your account has been created successfully.', 'success')
            return redirect(url_for('user_login', user_id=user.id))
            
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            db.session.rollback()
            flash('Error creating account. Please try again.', 'error')
    
    return render_template('register.html')

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
            
            # Update phone numbers from users
            users = User.query.filter_by(is_active=True).order_by(User.id).all()
            phone_numbers = [user.phone_number for user in users if user.phone_number]
            
            # Update the settings with current user phone numbers
            settings_obj.phone_number_1 = phone_numbers[0] if len(phone_numbers) > 0 else None
            settings_obj.phone_number_2 = phone_numbers[1] if len(phone_numbers) > 1 else None
            settings_obj.phone_number_3 = phone_numbers[2] if len(phone_numbers) > 2 else None
            settings_obj.phone_number_4 = phone_numbers[3] if len(phone_numbers) > 3 else None
            
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
    
    # Get users for display
    users_list = User.query.filter_by(is_active=True).order_by(User.id).all()
    return render_template('settings.html', settings=settings_obj, users=users_list)

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
        
        # Calculate daily percentage change vs yesterday's close
        daily_change_percent = None
        yesterday_close = None
        
        # Calculate 7-day percentage change
        weekly_change_percent = None
        week_ago_close = None
        
        if current_price:
            from datetime import date, timedelta
            from stock_service import get_daily_stock_data, is_market_open
            
            # Check if market is open
            market_open = is_market_open()
            
            # Get today's close price (use current price if market is open, or today's close if market is closed)
            today_close = current_price
            if not market_open:
                # Market is closed, try to get today's close price from database or fetch it
                today_data = StockData.query.filter_by(date=date.today()).first()
                if today_data and today_data.close_price:
                    today_close = today_data.close_price
                else:
                    # Fetch today's close price
                    today_stock_data = get_daily_stock_data()
                    if today_stock_data and today_stock_data.get('close'):
                        today_close = today_stock_data['close']
            
            # Daily change calculation
            yesterday = date.today() - timedelta(days=1)
            
            # Skip weekends - get last trading day
            while yesterday.weekday() >= 5:  # Saturday = 5, Sunday = 6
                yesterday -= timedelta(days=1)
            
            yesterday_data = StockData.query.filter_by(date=yesterday).first()
            
            if yesterday_data and yesterday_data.close_price:
                yesterday_close = yesterday_data.close_price
            else:
                # Fallback to most recent close price
                recent_stock_data = StockData.query.order_by(StockData.date.desc()).limit(2).all()
                if recent_stock_data and len(recent_stock_data) >= 2:
                    yesterday_close = recent_stock_data[1].close_price
            
            if yesterday_close:
                daily_change_percent = ((today_close - yesterday_close) / yesterday_close) * 100
            
            # Weekly change calculation (7 trading days ago)
            week_ago = date.today() - timedelta(days=7)
            
            # Skip weekends to get 7 trading days ago
            trading_days_back = 0
            while trading_days_back < 7:
                if week_ago.weekday() < 5:  # Monday-Friday
                    trading_days_back += 1
                if trading_days_back < 7:
                    week_ago -= timedelta(days=1)
            
            week_ago_data = StockData.query.filter_by(date=week_ago).first()
            
            if week_ago_data and week_ago_data.close_price:
                week_ago_close = week_ago_data.close_price
            else:
                # Fallback to 7th most recent close price
                recent_stock_data = StockData.query.order_by(StockData.date.desc()).limit(7).all()
                if recent_stock_data and len(recent_stock_data) >= 7:
                    week_ago_close = recent_stock_data[6].close_price
            
            if week_ago_close:
                weekly_change_percent = ((current_price - week_ago_close) / week_ago_close) * 100
        
        return jsonify({
            'success': True,
            'current_price': current_price,
            'daily_change_percent': daily_change_percent,
            'weekly_change_percent': weekly_change_percent,
            'yesterday_close': yesterday_close,
            'week_ago_close': week_ago_close,
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
