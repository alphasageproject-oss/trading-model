from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class MovingAverageWeekly(Base):
    __tablename__ = 'moving_averages_weekly'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    ma10_value = Column(Float)
    ma50_value = Column(Float)
    ma200_value = Column(Float)
    
    stock = relationship("Stock", back_populates="ma_weekly")
    
    __table_args__ = (
        UniqueConstraint('stock_id', 'date', name='uq_macd_weekly_stock_date'),
    )
