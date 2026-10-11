from contextlib import contextmanager
from Backend.config.settings import settings

# Supabase imports
try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None

# MySQL imports
try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:
    pymysql = None

@contextmanager
def get_db_connection():
    engine = settings.DB_ENGINE

    if engine == "mysql":
        if pymysql is None:
            raise RuntimeError("pymysql is required for MySQL connection.")
        conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False
        )
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        # Default: Supabase (PostgreSQL)
        if psycopg is None:
            raise RuntimeError("psycopg is required for Supabase connection.")
        conn = psycopg.connect(
            host=settings.SUPABASE_PG_HOST,
            port=settings.SUPABASE_PG_PORT,
            dbname=settings.SUPABASE_PG_DATABASE,
            user=settings.SUPABASE_PG_USER,
            password=settings.SUPABASE_PG_PASSWORD,
            row_factory=dict_row,
            options=f"-c search_path={settings.SUPABASE_PG_SCHEMA},public"
        )
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

@contextmanager
def get_db_cursor(commit=True):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            yield cur
            if commit:
                conn.commit()
