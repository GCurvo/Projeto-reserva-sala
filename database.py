import sqlite3

# Função para conectar ao banco de dados
def conectar():
    return sqlite3.connect('salas.db')  # Ajuste o nome do arquivo do banco de dados conforme necessário

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # Criar a tabela Sala, se ainda não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sala (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        capacidade INTEGER NOT NULL
    )
    ''')

    # Criar a tabela Reservas, se ainda não existir
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

    # Inserir salas, se ainda não existirem
    cursor.execute('SELECT COUNT(*) FROM Sala')
    if cursor.fetchone()[0] == 0:
        salas = [
            ('Sala 1', 40),
            ('Sala 2', 40),
            ('Sala 3', 40),
            ('Sala 4', 40),
            ('Sala 5', 40),
            ('Sala 6', 40),
            ('Sala 7', 40),
            ('Sala 8', 40),
            ('Auditório', 150)
        ]
        cursor.executemany('INSERT INTO Sala (nome, capacidade) VALUES (?, ?)', salas)
        conn.commit()

    conn.close()
