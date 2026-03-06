from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class MACDDaily(Base):
    __tablename__ = 'macd_daily'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    macd_line = Column(Float)
    signal_line = Column(Float)
    histogram = Column(Float)
    
    stock = relationship("Stock", back_populates="macd_daily")
