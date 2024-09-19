from database import conectar
import sqlite3

# Função para listar todas as reservas
def listar_reservas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Reserva')
    reservas = cursor.fetchall()
    conn.close()
    return reservas

# Função para cadastrar uma nova reserva
def cadastrar_reserva(nome, matricula, setor, sala_id, data, periodo, equipamentos=None):
    conn = conectar()
    cursor = conn.cursor()

    # Verificar se já existe uma reserva para o mesmo dia e período
    cursor.execute('''
        SELECT periodo FROM Reserva 
        WHERE sala_id = ? AND data = ?
    ''', (sala_id, data))
    
    reservas_existentes = cursor.fetchall()

    # Verificar conflitos com o período "integral"
    for reserva in reservas_existentes:
        if periodo == "integral" or reserva[0] == "integral":
            print(f"A sala já está reservada para o período {reserva[0]} no dia {data}.")
            return False

        if (periodo == "matutino" and reserva[0] == "vespertino") or (periodo == "vespertino" and reserva[0] == "matutino"):
            print(f"A sala já está reservada para o período {reserva[0]} no dia {data}.")
            return False

    # Se "equipamentos" não for fornecido, definir como uma string vazia
    equipamentos = equipamentos if equipamentos else ""

    # Inserir a nova reserva
    cursor.execute('''
        INSERT INTO Reserva (nome, matricula, setor, sala_id, data, periodo, equipamentos)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nome, matricula, setor, sala_id, data, periodo, equipamentos))

    conn.commit()
    conn.close()
    print(f"Reserva feita para {nome} na sala {sala_id} no dia {data} no período {periodo}.")
    return True

# Função para alterar uma reserva
def alterar_reserva(id, nome=None, matricula=None, setor=None, data=None, periodo=None, equipamentos=None):
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Buscar a reserva existente
        cursor.execute('SELECT nome, matricula, setor, data, periodo, equipamentos FROM Reserva WHERE id = ?', (id,))
        reserva_atual = cursor.fetchone()

        if not reserva_atual:
            print(f"Reserva com id {id} não encontrada.")
            return False

        # Manter os dados atuais se não forem fornecidos novos valores
        nome = nome if nome else reserva_atual[0]
        matricula = matricula if matricula else reserva_atual[1]
        setor = setor if setor else reserva_atual[2]
        data = data if data else reserva_atual[3]
        periodo = periodo if periodo else reserva_atual[4]
        equipamentos = equipamentos if equipamentos else reserva_atual[5]

        # Imprimir os valores para depuração
        print(f"Atualizando reserva {id}: nome={nome}, matricula={matricula}, setor={setor}, data={data}, periodo={periodo}, equipamentos={equipamentos}")

        # Atualizar a reserva
        cursor.execute('''
            UPDATE Reserva 
            SET nome = ?, matricula = ?, setor = ?, data = ?, periodo = ?, equipamentos = ? 
            WHERE id = ?
        ''', (nome, matricula, setor, data, periodo, equipamentos, id))

        conn.commit()
        conn.close()
        print(f"Reserva {id} alterada com sucesso!")
        return True

    except sqlite3.OperationalError as e:
        print(f"Erro operacional: {e}")
        return False

# Função para deletar uma reserva
def deletar_reserva(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Reserva WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    print(f"Reserva {id} excluída com sucesso!")
