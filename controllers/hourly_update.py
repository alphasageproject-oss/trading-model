"""
HOURLY UPDATE: Reuses populatedailyindicators.py methods.
Fast (60 days data = ~2min/150 stocks). Updates only new data.
Usage: python -m controllers.hourly_update
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from populatedailyindicators import fetch_historical, compute_daily_indicators, save_daily_data
from .base import Session
from ..models.stock import Stock

def hourly_update_all(limit: int = None):
    """HOURLY runner - reuses existing functions exactly."""
    session = Session()
    try:
        stocks = session.query(Stock.symbol).limit(limit or 1000).all()
        updated_stocks = 0
        
        for (symbol,) in stocks:
            full_symbol = symbol + '.NS' if not symbol.endswith('.NS') else symbol
            stock = session.query(Stock).filter(Stock.symbol == symbol).one()
            stock_id = stock.id
            
            print(f"⏰ Hourly: {full_symbol}")
            
            # 🔥 REUSE 1: fetch_historical (60 days = fast)
            df = fetch_historical(full_symbol, period="60d")  # Short period for hourly
            
            # 🔥 REUSE 2: compute_daily_indicators (identical logic)
            indicators = compute_daily_indicators(df)
            
            # 🔥 REUSE 3: save_daily_data (upsert = only new data)
            save_daily_data(session, stock_id, df, indicators)
            
            updated_stocks += 1
        
        print(f"🎉 Hourly complete: {updated_stocks}/{len(stocks)} stocks")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    hourly_update_all(limit=5)  # Test mode
