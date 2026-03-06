from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class Price(Base):  # Reuse for daily/weekly via interval param in queries
    __tablename__ = 'prices'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)
    
    stock = relationship("Stock", back_populates="prices")
