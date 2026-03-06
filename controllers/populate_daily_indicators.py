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
    """Save to daily tables."""
    latest_date = df['date'].max()
    
    # Prices (upsert latest)
    existing_dates = {p.date for p in session.query(Price.date).filter(Price.stock_id == stock_id).all()}
    for _, row in df.iterrows():
        if row['date'] not in existing_dates:
            price = Price(stock_id=stock_id, date=row['date'],
                         open_price=float(row['open']), high_price=float(row['high']),
                         low_price=float(row['low']), close_price=float(row['close']),
                         volume=float(row['volume']))
            session.add(price)
    
    # Indicators (latest only)
    def safe_add(model_cls, **kwargs):
        obj = model_cls(stock_id=stock_id, date=latest_date, **kwargs)
        session.add(obj)
    
    # MACD
    safe_add(MACDDaily,
            macd_line=float(indicators['macd_line'].iloc[-1]),
            signal_line=float(indicators['macd_signal'].iloc[-1]),
            histogram=float(indicators['macd_hist'].iloc[-1]))
    
    # BB
    safe_add(BollingerDaily,
            upper_band=float(indicators['bb_upper'].iloc[-1]),
            middle_band=float(indicators['bb_middle'].iloc[-1]),
            lower_band=float(indicators['bb_lower'].iloc[-1]))
    
    # ADX
    safe_add(ADXDaily,
            adx_value=float(indicators['adx'].iloc[-1]),
            plus_di=float(indicators['plus_di'].iloc[-1]),
            minus_di=float(indicators['minus_di'].iloc[-1]))
    
    # MAs
    for period in [10,20,50,200]:
        val = indicators[f'ma_{period}'].iloc[-1]
        if pd.notna(val):
            safe_add(MovingAverageDaily, period=period, ma_value=float(val))
    
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
