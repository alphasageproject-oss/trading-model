"""
Batch populate DAILY technical indicators for all stocks.
Usage: python -m controllers.populate_daily_indicators
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict
from ..models.stock import Stock
from ..models.price import Price
from ..models.macd_daily import MACDDaily
from ..models.bollinger_daily import BollingerDaily
from ..models.adx_daily import ADXDaily
from ..models.moving_average_daily import MovingAverageDaily
from .base import Session, IST

def fetch_historical(symbol: str, period: str = "2y") -> pd.DataFrame:
    """Your Yahoo API fetch for daily."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval=1d"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    resp = requests.get(url, headers=headers, timeout=30).json()
    
    data = resp['chart']['result'][0]
    timestamps = data['timestamp']
    quotes = data['indicators']['quote'][0]
    
    df = pd.DataFrame({
        'date': pd.to_datetime([datetime.utcfromtimestamp(ts) for ts in timestamps], utc=True).dt.tz_convert(IST).dt.date,
        'open': quotes['open'], 'high': quotes['high'], 'low': quotes['low'],
        'close': quotes['close'], 'volume': quotes['volume']
    }).dropna()
    return df[df['close'] > 0]

def compute_daily_indicators(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Compute MACD, BB, ADX, MAs matching your run_strategy."""
    close = df['close']
    
    # MAs
    ma_periods = [10, 20, 50, 200]
    ma_dict = {f'ma_{p}': ta.sma(close, p) for p in ma_periods}
    
    # MACD
    macd_data = ta.macd(close)
    ma_dict.update({
        'macd_line': macd_data['MACD_12_26_9'],
        'macd_signal': macd_data['MACDs_12_26_9'],
        'macd_hist': macd_data['MACDh_12_26_9']
    })
    
    # BB
    bb = ta.bbands(close, length=20, std=2.0)
    ma_dict.update({
        'bb_upper': bb['BBU_20_2.0'], 'bb_middle': bb['BBM_20_2.0'], 'bb_lower': bb['BBL_20_2.0']
    })
    
    # ADX
    adx_data = ta.adx(df['high'], df['low'], close, length=14)
    ma_dict.update({
        'adx': adx_data['ADX_14'], 'plus_di': adx_data['DMP_14'], 'minus_di': adx_data['DMN_14']
    })
    
    return ma_dict

def save_daily_data(session, stock_id: int, df: pd.DataFrame, indicators: Dict):
    """Save ALL historical dates with 1 entry per stock+date."""
    
    # Process ALL dates (not just latest)
    for idx, row in df.iterrows():
        current_date = row['date']
        
        # Skip if exists (enforced by unique constraint)
        existing_price = session.query(Price).filter(
            Price.stock_id == stock_id, 
            Price.date == current_date
        ).first()
        if not existing_price:
            price = Price(
                stock_id=stock_id, date=current_date,
                open_price=float(row['open']), high_price=float(row['high']),
                low_price=float(row['low']), close_price=float(row['close']),
                volume=float(row['volume'])
            )
            session.add(price)
        
        # Indicators for this exact date
        try:
            # MACD for this date
            macd_daily = session.query(MACDDaily).filter(
                MACDDaily.stock_id == stock_id, 
                MACDDaily.date == current_date
            ).first()
            if not macd_daily:
                macd_daily = MACDDaily(
                    stock_id=stock_id, date=current_date,
                    macd_line=float(indicators['macd_line'].iloc[idx]),
                    signal_line=float(indicators['macd_signal'].iloc[idx]),
                    histogram=float(indicators['macd_hist'].iloc[idx])
                )
                session.add(macd_daily)
            
            # Bollinger
            bb_daily = session.query(BollingerDaily).filter(
                BollingerDaily.stock_id == stock_id, 
                BollingerDaily.date == current_date
            ).first()
            if not bb_daily:
                bb_daily = BollingerDaily(
                    stock_id=stock_id, date=current_date,
                    upper_band=float(indicators['bb_upper'].iloc[idx]),
                    middle_band=float(indicators['bb_middle'].iloc[idx]),
                    lower_band=float(indicators['bb_lower'].iloc[idx])
                )
                session.add(bb_daily)
            
            # ADX
            adx_daily = session.query(ADXDaily).filter(
                ADXDaily.stock_id == stock_id, 
                ADXDaily.date == current_date
            ).first()
            if not adx_daily:
                adx_daily = ADXDaily(
                    stock_id=stock_id, date=current_date,
                    adx_value=float(indicators['adx'].iloc[idx]),
                    plus_di=float(indicators['plus_di'].iloc[idx]),
                    minus_di=float(indicators['minus_di'].iloc[idx])
                )
                session.add(adx_daily)
            
            # Single MovingAverageDaily row per date (ma10, ma50, ma200)
            ma_daily = session.query(MovingAverageDaily).filter(
                MovingAverageDaily.stock_id == stock_id,
                MovingAverageDaily.date == current_date
            ).first()
            if not ma_daily:
                ma_daily = MovingAverageDaily(
                    stock_id=stock_id, date=current_date,
                    ma10_value=float(indicators['ma_10'].iloc[idx]) if pd.notna(indicators['ma_10'].iloc[idx]) else None,
                    ma50_value=float(indicators['ma_50'].iloc[idx]) if pd.notna(indicators['ma_50'].iloc[idx]) else None,
                    ma200_value=float(indicators['ma_200'].iloc[idx]) if pd.notna(indicators['ma_200'].iloc[idx]) else None
                )
                session.add(ma_daily)

                        
        except Exception as e:
            print(f"Error saving {stock_id}:{current_date}: {e}")
            continue
    
    session.commit()


def populate_daily_indicators(limit: int = None):
    """Main daily runner."""
    session = Session()
    try:
        stocks = session.query(Stock.symbol).limit(limit or 1000).all()
        for (symbol,) in stocks:
            full_symbol = symbol + '.NS' if not symbol.endswith('.NS') else symbol
            stock = session.query(Stock).filter(Stock.symbol == symbol).one()
            
            print(f"Daily: {full_symbol}")
            df = fetch_historical(full_symbol)
            indicators = compute_daily_indicators(df)
            save_daily_data(session, stock.id, df, indicators)
    finally:
        session.close()

if __name__ == "__main__":
    populate_daily_indicators(limit=5)  # Test mode
