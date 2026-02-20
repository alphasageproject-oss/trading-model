import requests
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any
from datetime import datetime
from technical_indicators import moving_avg, ema, macd, boll_bands, calculate_adx

def fetch_historical(symbol: str, range_period: str = "1y") -> List[List[Any]]:
    """
    Fetch historical data from Yahoo Finance API.
    Returns list of [date, open, high, low, close, volume]
    """
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_period}&interval=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code}")
        
        content = response.text
        if not content:
            raise Exception("Empty response")
        
        data = response.json()
        if not data.get('chart') or not data['chart'].get('result'):
            raise Exception("No chart.result")
        
        chart = data['chart']['result'][0]
        
        # Handle nested array structure
        if isinstance(chart, list):
            for item in chart:
                if isinstance(item, dict) and item.get('timestamp'):
                    chart = item
                    break
            if isinstance(chart, list):
                chart = chart[0]
        
        if not chart.get('timestamp') or not isinstance(chart['timestamp'], list) or len(chart['timestamp']) == 0:
            raise Exception("No timestamp")
        
        if not chart.get('indicators') or not chart['indicators'].get('quote'):
            raise Exception("No indicators.quote")
        
        quotes = chart['indicators']['quote'][0]
        
        # Handle nested array structure for quotes
        if isinstance(quotes, list):
            for item in quotes:
                if (isinstance(item, dict) and 
                    item.get('close') and item.get('open') and 
                    item.get('high') and item.get('low') and item.get('volume')):
                    quotes = item
                    break
            if isinstance(quotes, list):
                quotes = quotes[0]
        
        if not isinstance(quotes, dict):
            raise Exception("quotes not object")
        
        if not all(k in quotes for k in ['close', 'open', 'high', 'low', 'volume']):
            raise Exception("Missing OHLCV")
        
        timestamps = chart['timestamp']
        result = []
        
        # WORKDAY LOGIC: Only include valid trading days with all OHLCV values > 0
        for i in range(len(timestamps)):
            date = datetime.utcfromtimestamp(timestamps[i])
            formatted_date = date.strftime("%Y-%m-%d")
            
            open_price = quotes.get('open', [None])[i] if quotes.get('open') else 0
            high_price = quotes.get('high', [None])[i] if quotes.get('high') else 0
            low_price = quotes.get('low', [None])[i] if quotes.get('low') else 0
            close_price = quotes.get('close', [None])[i] if quotes.get('close') else 0
            volume = quotes.get('volume', [None])[i] if quotes.get('volume') else 0
            
            open_price = float(open_price) if open_price else 0
            high_price = float(high_price) if high_price else 0
            low_price = float(low_price) if low_price else 0
            close_price = float(close_price) if close_price else 0
            volume = float(volume) if volume else 0
            
            # WORKDAY CHECK: Skip if any OHLCV is 0 or invalid
            if open_price > 0 and high_price > 0 and low_price > 0 and close_price > 0 and volume > 0:
                result.append([
                    formatted_date,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume
                ])
        
        return result
    
    except Exception as e:
        raise Exception(f"Failed to fetch historical data: {str(e)}")

def run_strategy(symbol: str) -> List[List[Any]]:
    """
    Main strategy runner - calculates daily indicators for a given symbol.
    Returns list containing single row with calculated indicators.
    """
    try:
        range_period = "1y"
        
        # Fetch historical data
        hist = fetch_historical(symbol, range_period)
        if not hist or len(hist) == 0:
            raise Exception("No data")
        
        # Calculate moving averages
        dma50 = moving_avg(hist, min(50, len(hist)), 4)
        dma200 = moving_avg(hist, min(200, len(hist)), 4)
        dma20 = moving_avg(hist, 20, 4)
        
        # Calculate MACD
        macd_line, macd_signal, macd_hist = macd(hist, 4)
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = boll_bands(hist, 4, 20, 2)
        
        # Calculate ADX
        adx_results = calculate_adx(hist, 14)
        
        # Get current and historical indices
        i = len(hist) - 1
        i_10 = i - 10 if i - 10 >= 0 else 0
        
        # Extract values
        price = hist[i][4]
        ten_day_price = hist[i_10][4]
        
        # Calculate percentage changes
        price_ten_day_change = ((price - ten_day_price) / ten_day_price) * 100 if ten_day_price != 0 else 0
        price_50dma_change = ((price - dma50[i]) / dma50[i]) * 100 if pd.notna(dma50[i]) and dma50[i] != 0 else 0
        price_200dma_change = ((price - dma200[i]) / dma200[i]) * 100 if pd.notna(dma200[i]) and dma200[i] != 0 else 0
        dma50_200dma_change = ((dma50[i] - dma200[i]) / dma200[i]) * 100 if pd.notna(dma200[i]) and pd.notna(dma50[i]) and dma200[i] != 0 else 0
        
        # Build output row
        output_row = [
            round(price, 2) if not pd.isna(price) else None,
            round(ten_day_price, 2) if not pd.isna(ten_day_price) else None,
            round(dma50[i], 2) if pd.notna(dma50[i]) else None,
            round(dma200[i], 2) if pd.notna(dma200[i]) else None,
            round(price_ten_day_change, 2) if not pd.isna(price_ten_day_change) else None,
            round(price_50dma_change, 2) if not pd.isna(price_50dma_change) else None,
            round(price_200dma_change, 2) if not pd.isna(price_200dma_change) else None,
            round(dma50_200dma_change, 2) if not pd.isna(dma50_200dma_change) else None,
            round(macd_line[i], 2) if pd.notna(macd_line[i]) else None,
            round(macd_signal[i], 2) if pd.notna(macd_signal[i]) else None,
            round(macd_hist[i], 2) if pd.notna(macd_hist[i]) else None,
            round(bb_upper[i], 2) if pd.notna(bb_upper[i]) else None,
            round(bb_middle[i], 2) if pd.notna(bb_middle[i]) else None,
            round(bb_lower[i], 2) if pd.notna(bb_lower[i]) else None,
            round(adx_results['adx'], 2) if not pd.isna(adx_results['adx']) else None,
            round(adx_results['plus_di'], 2) if not pd.isna(adx_results['plus_di']) else None,
            round(adx_results['minus_di'], 2) if not pd.isna(adx_results['minus_di']) else None
        ]
        
        return [output_row]
    
    except Exception as e:
        return [[f"ERROR: {str(e)}"]]

# Example usage
if __name__ == "__main__":
    symbol = "AAPL"  # Example ticker
    result = run_strategy(symbol)
    print(result)