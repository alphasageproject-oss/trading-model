from .stock import Stock
from .price import Price
from .fundamental import Fundamental
from .macd_daily import MACDDaily
from .macd_weekly import MACDWeekly
# Import all others...
__all__ = ['Stock', 'Price', ...]  # List all

from models import Base
engine = create_engine('mysql+pymysql://user:pass@localhost/trading_db')
Base.metadata.create_all(engine)
