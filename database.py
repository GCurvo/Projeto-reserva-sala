import sqlite3

def conectar():
    return sqlite3.connect('salas.db')

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    
    # Criar tabela de Salas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sala (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            capacidade INTEGER NOT NULL
        )
    ''')

    # Criar tabela de Reservas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL,
            setor TEXT NOT NULL,
            sala_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            periodo TEXT NOT NULL,
            equipamentos TEXT,
            FOREIGN KEY (sala_id) REFERENCES Sala(id)
        )
    ''')

    # Criar tabela de Equipamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
