from database import conectar

# Função para cadastrar uma nova sala
def cadastrar_sala(nome, capacidade):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Sala (nome, capacidade) 
        VALUES (?, ?)
    ''', (nome, capacidade))
    conn.commit()
    conn.close()

# Função para listar todas as salas cadastradas
def listar_salas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Sala')
    salas = cursor.fetchall()
    conn.close()
    return salas
