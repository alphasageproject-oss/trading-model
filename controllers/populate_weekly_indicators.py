"""
Batch populate WEEKLY technical indicators for all stocks.
Usage: python -m controllers.populate_weekly_indicators
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
from ..models.price import Price  # Weekly prices also go here
from ..models.macd_weekly import MACDWeekly
from ..models.bollinger_weekly import BollingerWeekly
from ..models.adx_weekly import ADXWeekly
from ..models.moving_average_weekly import MovingAverageWeekly
from .base import Session, IST

# 🔥 CHANGE 1: interval="1wk"
def fetch_historical(symbol: str, period: str = "2y") -> pd.DataFrame:
    """Your Yahoo API fetch for WEEKLY data."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval=1wk"
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

# 🔥 NO CHANGE: Same compute function works for weekly
def compute_daily_indicators(df: pd.DataFrame) -> Dict[str, pd.Series]:  # Keep name for consistency
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

# 🔥 CHANGE 2: Use week_ending + Weekly models
def save_weekly_data(session, stock_id: int, df: pd.DataFrame, indicators: Dict):
    """Save ALL historical weeks with 1 entry per stock+week."""
    
    for idx, row in df.iterrows():
        current_week = row['date']  # 🔥 Week ending date
        
        # Skip if price exists
        existing_price = session.query(Price).filter(
            Price.stock_id == stock_id, 
            Price.date == current_week
        ).first()
        if not existing_price:
            price = Price(
                stock_id=stock_id, date=current_week,
                open_price=float(row['open']), high_price=float(row['high']),
                low_price=float(row['low']), close_price=float(row['close']),
                volume=float(row['volume'])
            )
            session.add(price)

        # Weekly indicators for this week
        try:
            # 🔥 MACD Weekly
            macd_weekly = session.query(MACDWeekly).filter(
                MACDWeekly.stock_id == stock_id, 
                MACDWeekly.week_ending == current_week
            ).first()
            if not macd_weekly:
                macd_weekly = MACDWeekly(
                    stock_id=stock_id, week_ending=current_week,
                    macd_line=float(indicators['macd_line'].iloc[idx]),
                    signal_line=float(indicators['macd_signal'].iloc[idx]),
                    histogram=float(indicators['macd_hist'].iloc[idx])
                )
                session.add(macd_weekly)
            
            # 🔥 Bollinger Weekly
            bb_weekly = session.query(BollingerWeekly).filter(
                BollingerWeekly.stock_id == stock_id, 
                BollingerWeekly.week_ending == current_week
            ).first()
            if not bb_weekly:
                bb_weekly = BollingerWeekly(
                    stock_id=stock_id, week_ending=current_week,
                    upper_band=float(indicators['bb_upper'].iloc[idx]),
                    middle_band=float(indicators['bb_middle'].iloc[idx]),
                    lower_band=float(indicators['bb_lower'].iloc[idx])
                )
                session.add(bb_weekly)
            
            # 🔥 ADX Weekly
            adx_weekly = session.query(ADXWeekly).filter(
                ADXWeekly.stock_id == stock_id, 
                ADXWeekly.week_ending == current_week
            ).first()
            if not adx_weekly:
                adx_weekly = ADXWeekly(
                    stock_id=stock_id, week_ending=current_week,
                    adx_value=float(indicators['adx'].iloc[idx]),
                    plus_di=float(indicators['plus_di'].iloc[idx]),
                    minus_di=float(indicators['minus_di'].iloc[idx])
                )
                session.add(adx_weekly)
            
            # 🔥 MovingAverageWeekly (your new format)
            ma_weekly = session.query(MovingAverageWeekly).filter(
                MovingAverageWeekly.stock_id == stock_id,
                MovingAverageWeekly.week_ending == current_week
            ).first()
            if not ma_weekly:
                ma_weekly = MovingAverageWeekly(
                    stock_id=stock_id, week_ending=current_week,
                    ma10_value=float(indicators['ma_10'].iloc[idx]) if pd.notna(indicators['ma_10'].iloc[idx]) else None,
                    ma50_value=float(indicators['ma_50'].iloc[idx]) if pd.notna(indicators['ma_50'].iloc[idx]) else None,
                    ma200_value=float(indicators['ma_200'].iloc[idx]) if pd.notna(indicators['ma_200'].iloc[idx]) else None
                )
                session.add(ma_weekly)
                        
        except Exception as e:
            print(f"Error saving weekly {stock_id}:{current_week}: {e}")
            continue
    
    session.commit()

# 🔥 CHANGE 3: Weekly runner
def populate_weekly_indicators(limit: int = None):
    """Main WEEKLY runner."""
    session = Session()
    try:
        stocks = session.query(Stock.symbol).limit(limit or 1000).all()
        for (symbol,) in stocks:
            full_symbol = symbol + '.NS' if not symbol.endswith('.NS') else symbol
            stock = session.query(Stock).filter(Stock.symbol == symbol).one()
            
            print(f"Weekly: {full_symbol}")
            df = fetch_historical(full_symbol)  # 🔥 Gets weekly data
            indicators = compute_daily_indicators(df)  # Same function
            save_weekly_data(session, stock.id, df, indicators)
    finally:
        session.close()

if __name__ == "__main__":
    populate_weekly_indicators(limit=5)  # Test mode
