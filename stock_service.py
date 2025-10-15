import yfinance as yf
import logging
from datetime import datetime, date
from app import db
from models import StockData

STOCK_SYMBOL = "CRWV"

def get_current_stock_price():
    """
    Fetch current stock price for CRWV
    Returns the current price or None if failed
    """
    try:
        ticker = yf.Ticker(STOCK_SYMBOL)
        info = ticker.info
        
        # Try to get current price from different fields
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        
        if current_price:
            logging.info(f"Retrieved current price for {STOCK_SYMBOL}: ${current_price}")
            return float(current_price)
        else:
            logging.warning(f"No current price found for {STOCK_SYMBOL}")
            return None
            
    except Exception as e:
        logging.error(f"Error fetching current stock price for {STOCK_SYMBOL}: {e}")
        return None

def get_stock_history(period="5d"):
    """
    Fetch historical stock data for CRWV
    Returns DataFrame or None if failed
    """
    try:
        ticker = yf.Ticker(STOCK_SYMBOL)
        hist = ticker.history(period=period)
        
        if not hist.empty:
            logging.info(f"Retrieved {len(hist)} days of history for {STOCK_SYMBOL}")
            return hist
        else:
            logging.warning(f"No historical data found for {STOCK_SYMBOL}")
            return None
            
    except Exception as e:
        logging.error(f"Error fetching stock history for {STOCK_SYMBOL}: {e}")
        return None

def get_daily_stock_data(target_date=None):
    """
    Get opening and closing prices for a specific date
    Returns dict with open and close prices or None if failed
    """
    if target_date is None:
        target_date = date.today()
    
    try:
        # Check if we already have this data in our database
        existing_data = StockData.query.filter_by(date=target_date).first()
        
        # If we have recent data (within last hour), use it
        if existing_data and existing_data.last_updated:
            time_diff = datetime.utcnow() - existing_data.last_updated
            if time_diff.total_seconds() < 3600:  # 1 hour
                return {
                    'open': existing_data.open_price,
                    'close': existing_data.close_price,
                    'high': existing_data.high_price,
                    'low': existing_data.low_price,
                    'volume': existing_data.volume
                }
        
        # Fetch fresh data from yfinance
        ticker = yf.Ticker(STOCK_SYMBOL)
        
        # Get data for the specific date
        end_date = target_date + datetime.timedelta(days=1)
        hist = ticker.history(start=target_date, end=end_date)
        
        if not hist.empty:
            day_data = hist.iloc[0]
            
            stock_data = {
                'open': float(day_data['Open']),
                'close': float(day_data['Close']),
                'high': float(day_data['High']),
                'low': float(day_data['Low']),
                'volume': int(day_data['Volume'])
            }
            
            # Save to database
            if existing_data:
                existing_data.open_price = stock_data['open']
                existing_data.close_price = stock_data['close']
                existing_data.high_price = stock_data['high']
                existing_data.low_price = stock_data['low']
                existing_data.volume = stock_data['volume']
                existing_data.last_updated = datetime.utcnow()
            else:
                new_data = StockData(
                    date=target_date,
                    open_price=stock_data['open'],
                    close_price=stock_data['close'],
                    high_price=stock_data['high'],
                    low_price=stock_data['low'],
                    volume=stock_data['volume']
                )
                db.session.add(new_data)
            
            db.session.commit()
            logging.info(f"Retrieved daily stock data for {STOCK_SYMBOL} on {target_date}")
            return stock_data
        else:
            logging.warning(f"No stock data found for {STOCK_SYMBOL} on {target_date}")
            return None
            
    except Exception as e:
        logging.error(f"Error fetching daily stock data for {STOCK_SYMBOL} on {target_date}: {e}")
        return None

def is_market_open():
    """
    Check if the market is currently open
    Simplified check - assumes market is open Mon-Fri 9:30-16:00 EST
    """
    try:
        now = datetime.now()
        
        # Check if it's a weekday (0=Monday, 6=Sunday)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check time (this is simplified - doesn't account for holidays)
        current_time = now.time()
        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()
        
        return market_open <= current_time <= market_close
        
    except Exception as e:
        logging.error(f"Error checking market status: {e}")
        return False
