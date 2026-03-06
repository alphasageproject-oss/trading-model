import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz

DB_URL = os.getenv('DB_URL', 'mysql+pymysql://user:pass@localhost/trading_db')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
IST = pytz.timezone('Asia/Kolkata')
