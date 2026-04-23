import pymysql
from pymysql.cursors import DictCursor
from common_lib.config.settings import settings
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self):
        self.host = settings.database.host
        self.port = settings.database.port
        self.user = settings.database.user
        self.password = settings.database.password
        self.database = settings.database.name
        self.connection = None
    
    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=DictCursor
            )
            return self.connection
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
    
    def close(self):
        if self.connection:
            self.connection.close()

@contextmanager
def get_db_connection():
    db = DatabaseConnection()
    connection = db.connect()
    if not connection:
        yield None
    else:
        try:
            yield connection
        finally:
            connection.close()

def execute_query(query, params=None):
    with get_db_connection() as conn:
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor
        except Exception as e:
            print(f"Query execution failed: {e}")
            conn.rollback()
            return None

def fetch_all(query, params=None):
    with get_db_connection() as conn:
        if not conn:
            return []
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Fetch failed: {e}")
            return []

def fetch_one(query, params=None):
    with get_db_connection() as conn:
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            print(f"Fetch failed: {e}")
            return None
