from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class ADXWeekly(Base):
    __tablename__ = 'adx_weekly'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    adx_value = Column(Float)
    plus_di = Column(Float)
    minus_di = Column(Float)
    
    stock = relationship("Stock", back_populates="adx_weekly")
