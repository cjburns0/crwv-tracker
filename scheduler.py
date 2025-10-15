import logging
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from stock_service import get_current_stock_price, get_daily_stock_data, is_market_open
from sms_service import send_daily_notifications
from app import app

scheduler = None

def send_market_open_notification():
    """Send market open notification"""
    with app.app_context():
        try:
            logging.info("Sending market open notification")
            
            # Get current stock price
            current_price = get_current_stock_price()
            if current_price is None:
                logging.error("Could not fetch current stock price for market open notification")
                return
            
            # Send notifications
            send_daily_notifications('open', current_price)
            
        except Exception as e:
            logging.error(f"Error in market open notification: {e}")

def send_market_close_notification():
    """Send market close notification"""
    with app.app_context():
        try:
            logging.info("Sending market close notification")
            
            # Get daily stock data which should include closing price
            today_data = get_daily_stock_data()
            if today_data is None or today_data.get('close') is None:
                # Fallback to current price
                current_price = get_current_stock_price()
                if current_price is None:
                    logging.error("Could not fetch stock price for market close notification")
                    return
                close_price = current_price
            else:
                close_price = today_data['close']
            
            # Send notifications
            send_daily_notifications('close', close_price)
            
        except Exception as e:
            logging.error(f"Error in market close notification: {e}")

def init_scheduler():
    """Initialize the background scheduler"""
    global scheduler
    
    try:
        scheduler = BackgroundScheduler()
        
        # Schedule market open notification (Monday-Friday at 9:30 AM EST)
        scheduler.add_job(
            func=send_market_open_notification,
            trigger=CronTrigger(
                day_of_week='mon-fri',  # Monday through Friday
                hour=9,
                minute=30,
                timezone='US/Eastern'
            ),
            id='market_open_notification',
            name='Market Open Notification',
            replace_existing=True
        )
        
        # Schedule market close notification (Monday-Friday at 4:00 PM EST)
        scheduler.add_job(
            func=send_market_close_notification,
            trigger=CronTrigger(
                day_of_week='mon-fri',  # Monday through Friday
                hour=16,
                minute=0,
                timezone='US/Eastern'
            ),
            id='market_close_notification',
            name='Market Close Notification',
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        logging.info("Scheduler initialized and started successfully")
        
        # Register shutdown handler
        import atexit
        atexit.register(lambda: scheduler.shutdown())
        
    except Exception as e:
        logging.error(f"Failed to initialize scheduler: {e}")

def stop_scheduler():
    """Stop the scheduler"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logging.info("Scheduler stopped")
