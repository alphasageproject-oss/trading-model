"""
Database configuration and session management for Techno-Funda trading system.
Handles MySQL connection and SQLAlchemy ORM setup.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from typing import Optional

# Create declarative base for all models
Base = declarative_base()


class DatabaseManager:
    """
    Manages database connections and session lifecycle for the trading model system.
    Supports MySQL database with configurable connection parameters.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "techno_funda_trading",
        echo: bool = False,
    ):
        """
        Initialize database manager.
        
        Args:
            host: MySQL host address
            port: MySQL port number
            user: Database user
            password: Database password
            database: Database name
            echo: Enable SQLAlchemy echo for debugging
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.echo = echo
        self.engine = None
        self.SessionLocal = None
        
    def get_connection_string(self) -> str:
        """Generate MySQL connection string."""
        return (
            f"mysql+pymysql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )
    
    def connect(self):
        """Establish database connection and create engine."""
        connection_string = self.get_connection_string()
        self.engine = create_engine(connection_string, echo=self.echo)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables defined in Base metadata."""
        if self.engine is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables. Use with caution!"""
        if self.engine is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """Context manager for database sessions with automatic commit/rollback."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
        db_manager.connect()
    return db_manager
