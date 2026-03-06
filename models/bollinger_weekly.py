from .base import Base, Column, Integer, Float, Date, ForeignKey, relationship

class BollingerWeekly(Base):
    __tablename__ = 'bollinger_bands_weekly'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    upper_band = Column(Float)
    middle_band = Column(Float)
    lower_band = Column(Float)
    
    stock = relationship("Stock", back_populates="bollinger_weekly")
