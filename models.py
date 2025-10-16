from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def get_masked_phone(self):
        """Return phone number with only last 4 digits visible"""
        if not self.phone_number:
            return "No phone number"
        
        phone = self.phone_number
        if len(phone) <= 4:
            return "*" * len(phone)
        
        # Show only last 4 digits, mask the rest
        masked_length = len(phone) - 4
        return "*" * masked_length + phone[-4:]
    
    def get_masked_name(self):
        """Return name with only first letter visible"""
        if not self.name:
            return "No name"
        
        name = self.name.strip()
        if len(name) <= 1:
            return name
        
        # Show first letter, mask the rest
        return name[0] + "*" * (len(name) - 1)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number_1 = db.Column(db.String(20), nullable=True)
    phone_number_2 = db.Column(db.String(20), nullable=True)
    phone_number_3 = db.Column(db.String(20), nullable=True)
    phone_number_4 = db.Column(db.String(20), nullable=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    market_open_time = db.Column(db.String(8), default="09:30")  # EST format HH:MM
    market_close_time = db.Column(db.String(8), default="16:00")  # EST format HH:MM
    settings_password_hash = db.Column(db.String(256), nullable=True)  # Password protection for settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_phone_numbers(self):
        """Get list of configured phone numbers"""
        numbers = []
        for i in range(1, 5):
            phone = getattr(self, f'phone_number_{i}')
            if phone:
                numbers.append(phone)
        return numbers

    def has_password_protection(self):
        """Check if settings are password protected"""
        return self.settings_password_hash is not None

    @classmethod
    def get_settings(cls):
        """Get the current settings, create default if none exist"""
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings

class NotificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_type = db.Column(db.String(20), nullable=False)  # 'open' or 'close'
    stock_price = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    message_sid = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')  # 'sent', 'failed', 'pending'
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    open_price = db.Column(db.Float, nullable=True)
    close_price = db.Column(db.Float, nullable=True)
    high_price = db.Column(db.Float, nullable=True)
    low_price = db.Column(db.Float, nullable=True)
    volume = db.Column(db.BigInteger, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
