from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class Fundamental(Base):
    __tablename__ = 'fundamentals'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quarter_ended = Column(Date)
    roce = Column(Float)
    roe = Column(Float)
    revenue = Column(Float)
    net_profit = Column(Float)
    debt_to_equity = Column(Float)
    
    stock = relationship("Stock", back_populates="fundamentals")
