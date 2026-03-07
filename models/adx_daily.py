from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class ADXDaily(Base):
    __tablename__ = 'adx_daily'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    adx_value = Column(Float)
    plus_di = Column(Float)
    minus_di = Column(Float)
    
    stock = relationship("Stock", back_populates="adx_daily")
    
    __table_args__ = (
        UniqueConstraint('stock_id', 'date', name='uq_adx_daily_stock_date'),
    )
