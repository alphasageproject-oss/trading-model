import yfinance as yf
import pandas as pd
from typing import List
from .technical_indicators import *

def run_strategy_w(symbol: str) -> List[List[float]]:
    """Exact replica of your JS RUN_STRATEGY_W(symbol) - Weekly timeframe"""
    try:
        # Fetch 1y weekly data (identical to JS range="1y", interval=1wk)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y", interval="1wk")
        
        if hist.empty:
            return [["ERROR: No data"]]
        
        # Convert to your JS format [[date, open, high, low, close, volume]]
        data = []
        for idx, row in hist.iterrows():
            if all(row[['Open', 'High', 'Low', 'Close', 'Volume']] > 0):
                data.append([
                    idx.strftime('%Y-%m-%d'),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume'])
                ])
        
        if not data:
            return [["ERROR: No valid trading days"]]
        
        # Calculate all indicators (identical logic/order)
        dma50 = moving_avg(data, min(50, len(data)), 4)
        dma200 = moving_avg(data, min(200, len(data)), 4)
        dma20 = moving_avg(data, 20, 4)
        
        macd_line, macd_signal, macd_hist = macd(data, 4)
        bb_upper, bb_middle, bb_lower = boll_bands(data, 4, 20, 2.0)
        adx_results = calculate_adx(data, 14)
        
        # Current values (i = len(data)-1)
        i = len(data) - 1
        i_10 = max(i - 10, 0)
        
        price = data[i][4]
        ten_day_price = data[i_10][4]
        
        output_row = [
            price,
            ten_day_price,
            dma50[i] if pd.notna(dma50[i]) else np.nan,
            dma200[i] if pd.notna(dma200[i]) else np.nan,
            ((price - ten_day_price) / ten_day_price) * 100,
            ((price - dma50[i]) / dma50[i]) * 100 if pd.notna(dma50[i]) else np.nan,
            ((price - dma200[i]) / dma200[i]) * 100 if pd.notna(dma200[i]) else np.nan,
            ((dma50[i] - dma200[i]) / dma200[i]) * 100 if pd.notna(dma50[i]) and pd.notna(dma200[i]) else np.nan,
            macd_line[i] if pd.notna(macd_line[i]) else np.nan,
            macd_signal[i] if pd.notna(macd_signal[i]) else np.nan,
            macd_hist[i] if pd.notna(macd_hist[i]) else np.nan,
            bb_upper[i] if pd.notna(bb_upper[i]) else np.nan,
            bb_middle[i] if pd.notna(bb_middle[i]) else np.nan,
            bb_lower[i] if pd.notna(bb_lower[i]) else np.nan,
            adx_results['adx'],
            adx_results['plus_di'],
            adx_results['minus_di']
        ]
        
        return [output_row]
        
    except Exception as e:
        return [[f"ERROR: {str(e)}"]]
