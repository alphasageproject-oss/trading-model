from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class MovingAverageDaily(Base):
    __tablename__ = 'moving_averages_daily'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    period = Column(Integer, nullable=False)  # 10,50,200
    ma_value = Column(Float)
    
    stock = relationship("Stock", back_populates="ma_daily")
