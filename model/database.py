# Database Configuration and Connection Setup

import sqlite3

DATABASE_NAME = 'trading_model.db'

# Function to create a connection to the SQLite database.
def create_connection():
    """ create a database connection to the SQLite database """  
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        print(f'Connected to the database: {DATABASE_NAME}')
    except Error as e:
        print(e)
    return conn

# Example usage
if __name__ == '__main__':
    conn = create_connection()  
    # Don't forget to close the connection.
    if conn:
        conn.close()
