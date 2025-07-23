import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", 5432)
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS colaboradores (
            id SERIAL PRIMARY KEY,
            codigo_registro VARCHAR(6) UNIQUE NOT NULL,
            nome_completo VARCHAR(255) NOT NULL,
            nr33_validade DATE,
            nr18_validade DATE,
            nr35_validade DATE,
            nr10_validade DATE,
            nr10_aplicavel BOOLEAN,
            aso_validade DATE,
            observacoes TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_administrativos (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
