"""
Technical indicator models for Techno-Funda trading system.
Includes MACD, ADX, Bollinger Bands, and Moving Averages.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class MACD(BaseModel):
    """
    MACD (Moving Average Convergence Divergence) indicator data.
    Stores MACD line, signal line, and histogram values.
    """
    __tablename__ = 'macd_indicators'
    
    model_stock_id = Column(Integer, ForeignKey('model_stocks.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # MACD values
    macd_line = Column(Float, nullable=False, comment='12-period EMA - 26-period EMA')
    signal_line = Column(Float, nullable=False, comment='9-period EMA of MACD line')
    histogram = Column(Float, nullable=False, comment='MACD line - Signal line')
    
    # Additional context
    close_price = Column(Float, nullable=True)
    
    # Relationships
    model_stock = relationship(
        'ModelStock',
        back_populates='macd_indicators',
        foreign_keys=[model_stock_id]
    )
    
    def __repr__(self):
        return f"<MACD(id={{self.id}}, macd_line={{self.macd_line}}, signal={{self.signal_line}})>"


class ADX(BaseModel):
    """
    ADX (Average Directional Index) indicator data.
    Measures trend strength without considering direction.
    """
    __tablename__ = 'adx_indicators'
    
    model_stock_id = Column(Integer, ForeignKey('model_stocks.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # ADX values
    adx_value = Column(Float, nullable=False, comment='ADX indicator (0-100)')
    plus_di = Column(Float, nullable=False, comment='Plus Directional Indicator')
    minus_di = Column(Float, nullable=False, comment='Minus Directional Indicator')
    
    # Additional context
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    
    # Relationships
    model_stock = relationship(
        'ModelStock',
        back_populates='adx_indicators',
        foreign_keys=[model_stock_id]
    )
    
    def __repr__(self):
        return f"<ADX(id={{self.id}}, adx_value={{self.adx_value}}, +DI={{self.plus_di}}, -DI={{self.minus_di}})>"


class BollingerBand(BaseModel):
    """
    Bollinger Bands indicator data.
    Tracks upper band, middle band (SMA), and lower band.
    """
    __tablename__ = 'bollinger_bands'
    
    model_stock_id = Column(Integer, ForeignKey('model_stocks.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Bollinger Band values
    upper_band = Column(Float, nullable=False, comment='Upper Bollinger Band (SMA + 2*StdDev)')
    middle_band = Column(Float, nullable=False, comment='Middle Band (20-period SMA)')
    lower_band = Column(Float, nullable=False, comment='Lower Bollinger Band (SMA - 2*StdDev)')
    
    # Additional context
    close_price = Column(Float, nullable=False)
    band_width = Column(Float, nullable=True, comment='Upper Band - Lower Band')
    percent_b = Column(Float, nullable=True, comment='(Close - Lower Band) / (Upper Band - Lower Band)')
    
    # Relationships
    model_stock = relationship(
        'ModelStock',
        back_populates='bollinger_bands',
        foreign_keys=[model_stock_id]
    )
    
    def __repr__(self):
        return f"<BollingerBand(id={{self.id}}, close={{self.close_price}}, upper={{self.upper_band}}, lower={{self.lower_band}})>"


class MovingAverage(BaseModel):
    """
    Moving Average data.
    Tracks different types (SMA, EMA) and periods.
    """
    __tablename__ = 'moving_averages'
    
    model_stock_id = Column(Integer, ForeignKey('model_stocks.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Moving Average configuration and value
    ma_type = Column(String(20), nullable=False, comment='SMA, EMA, WMA, etc.')
    period = Column(Integer, nullable=False, comment='Period for moving average calculation')
    value = Column(Float, nullable=False, comment='Calculated moving average value')
    
    # Additional context
    close_price = Column(Float, nullable=True)
    
    # Create composite index for fast lookups
    __table_args__ = (
        {'indexes': [
            'model_stock_id',
            'timestamp',
            'ma_type',
            'period'
        ]},
    )
    
    # Relationships
    model_stock = relationship(
        'ModelStock',
        back_populates='moving_averages',
        foreign_keys=[model_stock_id]
    )
    
    def __repr__(self):
        return f"<MovingAverage(id={{self.id}}, type={{self.ma_type}}, period={{self.period}}, value={{self.value}})>"
