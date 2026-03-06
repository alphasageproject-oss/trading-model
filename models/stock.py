from .base import Base, Column, Integer, String, DateTime, relationship

class Stock(Base):
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime, default=lambda: datetime.now(IST))
    
    # Relationships (add all daily/weekly)
    prices = relationship("Price", back_populates="stock")
    fundamentals = relationship("Fundamental", back_populates="stock")
    macd_daily = relationship("MACDDaily", back_populates="stock")
    macd_weekly = relationship("MACDWeekly", back_populates="stock")
    adx_daily = relationship("ADXDaily", back_populates="stock")
    adx_weekly = relationship("ADXWeekly", back_populates="stock")
    bollinger_bands_daily = relationship("BollingerDaily", back_populates="stock")
    bollinger_bands_weekly = relationship("BollingerWeekly", back_populates="stock")
    moving_averages_daily = relationship("MovingAverageDaily", back_populates="stock")
    moving_averages_weekly = relationship("MovingAverageWeekly", back_populates="stock")
