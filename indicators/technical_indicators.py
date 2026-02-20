import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

def moving_avg(data: List[List[float]], lookback: int, col_idx: int) -> List[float]:
    """Identical to your JS movingAvg()"""
    if not data or len(data) == 0:
        return []
    
    result = []
    for i in range(len(data)):
        if i < lookback - 1:
            result.append(np.nan)
        else:
            window = [float(data[j][col_idx]) for j in range(i - lookback + 1, i + 1) 
                     if j < len(data) and pd.notna(float(data[j][col_idx]))]
            result.append(np.mean(window) if window else np.nan)
    return result

def ema(data: List[List[float]], lookback: int, col_idx: int) -> List[float]:
    """Identical to your JS ema() with smoothing constant k=2/(N+1)"""
    if not data or len(data) == 0:
        return []
    
    result = []
    k = 2 / (lookback + 1)
    prev_ema = None
    
    for i in range(len(data)):
        if i < lookback - 1:
            result.append(np.nan)
        elif i == lookback - 1:
            window = [float(data[j][col_idx]) for j in range(i + 1) 
                     if pd.notna(float(data[j][col_idx]))]
            prev_ema = np.mean(window) if window else np.nan
            result.append(prev_ema)
        else:
            current = float(data[i][col_idx])
            if pd.notna(current) and pd.notna(prev_ema):
                prev_ema = current * k + prev_ema * (1 - k)
                result.append(prev_ema)
            else:
                result.append(np.nan)
    return result

def macd(data: List[List[float]], col_idx: int) -> Tuple[List[float], List[float], List[float]]:
    """Identical to your JS macd() - EMA12-EMA26, Signal=EMA9(MACD), Histogram"""
    ema12 = ema(data, 12, col_idx)
    ema26 = ema(data, 26, col_idx)
    
    macd_line = []
    for i in range(len(data)):
        if pd.notna(ema12[i]) and pd.notna(ema26[i]):
            macd_line.append(ema12[i] - ema26[i])
        else:
            macd_line.append(np.nan)
    
    # Signal line = EMA9 of MACD line
    signal_data = [[val] for val in macd_line]
    signal_line = ema(signal_data, 9, 0)
    
    histogram = []
    for i in range(len(data)):
        if pd.notna(macd_line[i]) and pd.notna(signal_line[i]):
            histogram.append(macd_line[i] - signal_line[i])
        else:
            histogram.append(np.nan)
    
    return macd_line, signal_line, histogram

def boll_bands(data: List[List[float]], col_idx: int, period: int = 20, std_dev: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
    """Identical to your JS bollBands() - SMA20 ± 2*STD20"""
    upper, middle, lower = [], [], []
    
    for i in range(len(data)):
        if i < period - 1:
            upper.append(np.nan); middle.append(np.nan); lower.append(np.nan)
        else:
            window = [float(data[j][col_idx]) for j in range(i - period + 1, i + 1)]
            window = [x for x in window if pd.notna(x)]
            
            if len(window) == 0:
                upper.append(np.nan); middle.append(np.nan); lower.append(np.nan)
                continue
                
            sma = np.mean(window)
            std = np.std(window)
            upper.append(sma + std * std_dev)
            middle.append(sma)
            lower.append(sma - std * std_dev)
    
    return upper, middle, lower

def calculate_adx(data: List[List[float]], period: int = 14) -> Dict[str, float]:
    """Identical to your JS calculateADX() - Wilder's smoothing, +DI/-DI, DX, ADX"""
    if len(data) < period + 1:
        return {'adx': np.nan, 'plus_di': np.nan, 'minus_di': np.nan}
    
    highs = [row[2] for row in data]
    lows = [row[3] for row in data]
    closes = [row[4] for row in data]
    
    true_ranges, plus_dm, minus_dm = [], [], []
    for i in range(1, len(highs)):
        high_diff = highs[i] - highs[i-1]
        low_diff = lows[i-1] - lows[i]
        
        plus_dm.append(max(high_diff, 0) if high_diff > low_diff else 0)
        minus_dm.append(max(low_diff, 0) if low_diff > high_diff else 0)
        true_ranges.append(max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        ))
    
    # Wilder's smoothing (identical to JS)
    def wilders_smooth(series: List[float], p: int) -> List[float]:
        smoothed = [np.nan] * len(series)
        if len(series) < p:
            return smoothed
        smoothed[p-1] = np.mean(series[:p])
        for i in range(p, len(series)):
            smoothed[i] = (smoothed[i-1] * (p - 1) + series[i]) / p
        return smoothed
    
    smooth_tr = wilders_smooth(true_ranges, period)
    smooth_pdm = wilders_smooth(plus_dm, period)
    smooth_mdm = wilders_smooth(minus_dm, period)
    
    plus_di, minus_di, dx = [], [], []
    for i in range(len(smooth_tr)):
        if pd.notna(smooth_tr[i]) and smooth_tr[i] != 0:
            plus_di.append((smooth_pdm[i] / smooth_tr[i]) * 100)
            minus_di.append((smooth_mdm[i] / smooth_tr[i]) * 100)
            sum_di = plus_di[-1] + minus_di[-1]
            dx.append(abs(plus_di[-1] - minus_di[-1]) / sum_di * 100 if sum_di != 0 else 0)
        else:
            plus_di.append(np.nan); minus_di.append(np.nan); dx.append(np.nan)
    
    adx_smooth = wilders_smooth(dx, period)
    last_idx = len(adx_smooth) - 1
    
    return {
        'adx': round(adx_smooth[last_idx], 2) if pd.notna(adx_smooth[last_idx]) else np.nan,
        'plus_di': round(plus_di[last_idx + period - 1], 2) if len(plus_di) > last_idx + period - 1 else np.nan,
        'minus_di': round(minus_di[last_idx + period - 1], 2) if len(minus_di) > last_idx + period - 1 else np.nan
    }
