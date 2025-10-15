import os
import logging
from datetime import datetime
from twilio.rest import Client
from app import db
from models import NotificationLog

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def send_twilio_message(to_phone_number: str, message: str) -> str:
    """
    Send SMS message via Twilio
    Returns message SID on success, raises exception on failure
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_obj = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        
        logging.info(f"Message sent with SID: {message_obj.sid}")
        return message_obj.sid
        
    except Exception as e:
        logging.error(f"Failed to send SMS to {to_phone_number}: {e}")
        raise

def send_stock_notification(phone_number: str, notification_type: str, price: float) -> bool:
    """
    Send stock price notification
    notification_type: 'open', 'close', or 'test'
    Returns True on success, False on failure
    """
    try:
        # Format the message (simplified for better deliverability)
        if notification_type == 'open':
            message = f"CRWV opened at ${price:.2f} at {datetime.now().strftime('%I:%M %p ET')}"
        elif notification_type == 'close':
            message = f"CRWV closed at ${price:.2f} at {datetime.now().strftime('%I:%M %p ET')}"
        elif notification_type == 'test':
            message = f"Test: CRWV price is ${price:.2f} at {datetime.now().strftime('%I:%M %p ET')}. Notifications working."
        else:
            message = f"CRWV: ${price:.2f} at {datetime.now().strftime('%I:%M %p ET')}"
        
        # Send the message
        message_sid = send_twilio_message(phone_number, message)
        
        # Log the notification
        log_entry = NotificationLog(
            notification_type=notification_type,
            stock_price=price,
            phone_number=phone_number,
            message_sid=message_sid,
            status='sent'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        logging.info(f"Stock notification sent successfully to {phone_number}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send stock notification to {phone_number}: {e}")
        
        # Log the failed notification
        try:
            log_entry = NotificationLog(
                notification_type=notification_type,
                stock_price=price,
                phone_number=phone_number,
                status='failed',
                error_message=str(e)
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as log_error:
            logging.error(f"Failed to log notification error: {log_error}")
        
        return False

def send_daily_notifications(notification_type: str, price: float):
    """
    Send notifications to all configured phone numbers
    notification_type: 'open' or 'close'
    """
    from models import Settings
    
    try:
        settings = Settings.get_settings()
        
        if not settings.notifications_enabled:
            logging.info("Notifications are disabled")
            return
        
        phone_numbers = settings.get_phone_numbers()
        
        if not phone_numbers:
            logging.warning("No phone numbers configured for notifications")
            return
        
        success_count = 0
        for phone_number in phone_numbers:
            if send_stock_notification(phone_number, notification_type, price):
                success_count += 1
        
        logging.info(f"Daily {notification_type} notifications sent to {success_count}/{len(phone_numbers)} numbers")
        
    except Exception as e:
        logging.error(f"Error sending daily notifications: {e}")
