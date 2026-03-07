from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class BollingerDaily(Base):
    __tablename__ = 'bollinger_bands_daily'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    upper_band = Column(Float)
    middle_band = Column(Float)
    lower_band = Column(Float)
    
    stock = relationship("Stock", back_populates="bollinger_daily")
    
    __table_args__ = (
        UniqueConstraint('stock_id', 'date', name='uq_bollinger_daily_stock_date'),
    )
