"""
Fundamental data model for Techno-Funda trading system.
Stores financial metrics and fundamental analysis data.
"""

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class FundamentalData(BaseModel):
    """
    Fundamental data for stocks.
    Stores financial metrics and fundamental analysis indicators.
    One-to-one relationship with ModelStock.
    """
    __tablename__ = 'fundamental_data'
    
    model_stock_id = Column(Integer, ForeignKey('model_stocks.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # Valuation metrics
    pe_ratio = Column(Float, nullable=True, comment='Price-to-Earnings ratio')
    pb_ratio = Column(Float, nullable=True, comment='Price-to-Book ratio')
    price_to_sales = Column(Float, nullable=True, comment='Price-to-Sales ratio')
    peg_ratio = Column(Float, nullable=True, comment='PEG ratio (PE/Growth)')
    
    # Profitability metrics
    roe = Column(Float, nullable=True, comment='Return on Equity (%)')
    roa = Column(Float, nullable=True, comment='Return on Assets (%)')
    profit_margin = Column(Float, nullable=True, comment='Net Profit Margin (%)')
    operating_margin = Column(Float, nullable=True, comment='Operating Margin (%)')
    
    # Growth metrics
    revenue_growth = Column(Float, nullable=True, comment='Year-over-year revenue growth (%)')
    earnings_growth = Column(Float, nullable=True, comment='Year-over-year earnings growth (%)')
    
    # Debt and solvency
    debt_to_equity = Column(Float, nullable=True, comment='Debt-to-Equity ratio')
    current_ratio = Column(Float, nullable=True, comment='Current Ratio (Current Assets / Current Liabilities)')
    quick_ratio = Column(Float, nullable=True, comment='Quick Ratio')
    
    # Dividends
    dividend_yield = Column(Float, nullable=True, comment='Dividend Yield (%)')
    dividend_payout_ratio = Column(Float, nullable=True, comment='Dividend Payout Ratio (%)')
    
    # Other metrics
    market_cap = Column(Float, nullable=True, comment='Market Capitalization')
    eps = Column(Float, nullable=True, comment='Earnings Per Share')
    book_value_per_share = Column(Float, nullable=True, comment='Book Value Per Share')
    free_cash_flow = Column(Float, nullable=True, comment='Free Cash Flow')
    
    # Data timestamp
    data_date = Column(DateTime, nullable=True, comment='Date when this fundamental data was recorded')
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    model_stock = relationship(
        'ModelStock',
        back_populates='fundamental_data',
        foreign_keys=[model_stock_id]
    )
    
    def __repr__(self):
        return f"<FundamentalData(id={{self.id}}, model_stock_id={{self.model_stock_id}}, pe={{self.pe_ratio}})>"
