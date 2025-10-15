#!/usr/bin/env python3

from app import app, db
from models import StockData
from stock_service import get_stock_history
from datetime import datetime, timedelta
import logging

def populate_historical_data():
    """Populate historical stock data if none exists"""
    with app.app_context():
        # Check if we have any stock data
        existing_data = StockData.query.count()
        print(f'Existing stock data records: {existing_data}')
        
        if existing_data == 0:
            print('No historical data found. Fetching from yfinance...')
            
            # Get historical data
            hist_data = get_stock_history('5d')
            if hist_data is not None and not hist_data.empty:
                for date, row in hist_data.iterrows():
                    stock_data = StockData(
                        date=date.date(),
                        open_price=float(row['Open']),
                        close_price=float(row['Close']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        volume=int(row['Volume'])
                    )
                    db.session.add(stock_data)
                
                db.session.commit()
                print(f'Added {len(hist_data)} historical records')
            else:
                print('Failed to fetch historical data')
        
        # Show recent data for chart
        recent_data = StockData.query.order_by(StockData.date.desc()).limit(5).all()
        print(f'Recent data for chart: {len(recent_data)} records')
        for stock in recent_data:
            print(f'{stock.date}: Close=${stock.close_price}')

if __name__ == '__main__':
    populate_historical_data()