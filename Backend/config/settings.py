import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

class Settings:
    # Database selection: "supabase" (default) or "mysql"
    DB_ENGINE = os.getenv("DB_ENGINE", "supabase").lower()

    # Supabase PostgreSQL Settings
    SUPABASE_PG_HOST = os.getenv("SUPABASE_PG_HOST", "aws-0-us-east-2.pooler.supabase.com")
    SUPABASE_PG_PORT = int(os.getenv("SUPABASE_PG_PORT", "6543"))
    SUPABASE_PG_DATABASE = os.getenv("SUPABASE_PG_DATABASE", "postgres")
    SUPABASE_PG_USER = os.getenv("SUPABASE_PG_USER", "postgres.nplfvbrquxcfpvrlgurw")
    SUPABASE_PG_PASSWORD = os.getenv("SUPABASE_PG_PASSWORD", "")
    SUPABASE_PG_SCHEMA = os.getenv("SUPABASE_PG_SCHEMA", "bi_pluraal")

    # MySQL Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "bi_pluraal")

    # JWT Settings
    JWT_SECRET = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24

    MIN_PASSWORD_LENGTH = 8
    TEMP_PASSWORD_LENGTH = 10

settings = Settings()
