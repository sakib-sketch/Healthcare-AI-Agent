from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

# Neon PostgreSQL Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://neondb_owner:npg_VWc4ufmLobz6@ep-silent-base-apx54d38-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_connection():
    """
    Returns a standard psycopg2 connection for native SQL operations,
    using the configured DATABASE_URL.
    """
    return psycopg2.connect(DATABASE_URL)

def create_users_table():
    """
    Creates the required 'users' table if it does not already exist,
    and safely appends tracking columns if they are missing.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)
        # Safely add the required tracking columns if they are not already present in the remote Neon PostgreSQL DB
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_logout TIMESTAMP;")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_logged_in BOOLEAN DEFAULT FALSE;")
        conn.commit()
    finally:
        conn.close()