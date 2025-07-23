import sqlite3
from datetime import datetime

DATABASE = 'database.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_registro TEXT UNIQUE NOT NULL,
            nome_completo TEXT NOT NULL,
            nr33_validade DATE,
            nr18_validade DATE,
            nr35_validade DATE,
            nr10_validade DATE,
            nr10_aplicavel BOOLEAN,
            aso_validade DATE,
            observacoes TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_administrativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Isso permite acessar colunas por nome
    return conn

# Exemplo de como adicionar um usuário admin (você faria isso via um script inicial ou funcionalidade)
 # APENAS PARA TESTE. CRIE UMA SENHA FORTE!