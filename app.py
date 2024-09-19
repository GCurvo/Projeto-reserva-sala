from flask import Flask, render_template, request, redirect, url_for
from database import conectar, criar_tabelas

app = Flask(__name__)

criar_tabelas()  # Certifica que as tabelas são criadas ao iniciar o aplicativo

@app.route('/')
def index():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Reservas.nome, Reservas.data, Reservas.periodo, Sala.nome AS sala_nome, Reservas.equipamentos, Reservas.id
        FROM Reservas
        JOIN Sala ON Reservas.sala_id = Sala.id
    ''')
    reservas = cursor.fetchall()  # Buscar todas as reservas com os dados de sala
    conn.close()
    return render_template('index.html', reservas=reservas)

@app.route('/reservar', methods=['POST'])
def reservar():
    nome = request.form['nome']
    matricula = request.form['matricula']
    setor = request.form['setor']
    sala_id = request.form['sala_id']
    data = request.form['data']
    periodo = request.form['periodo']
    equipamentos = ', '.join(request.form.getlist('equipamentos')) if request.form.getlist('equipamentos') else ''

    conn = conectar()
    cursor = conn.cursor()

    # Verificar se já existe uma reserva para a mesma sala no mesmo dia e período
    cursor.execute('''
        SELECT periodo FROM Reservas 
        WHERE sala_id = ? AND data = ?
    ''', (sala_id, data))
    reservas_existentes = cursor.fetchall()

    # Verificar conflitos de período, incluindo o período "integral"
    conflito = False
    for reserva in reservas_existentes:
        periodo_existente = reserva[0]
        if periodo == "integral" or periodo_existente == "integral":
            conflito = True
        elif (periodo == "matutino" and periodo_existente == "vespertino") or (periodo == "vespertino" and periodo_existente == "matutino"):
            conflito = False
        else:
            conflito = True

    if conflito:
        conn.close()
        return "Erro: Esta sala já foi reservada para este período e data.", 400

    # Inserir a reserva se não houver conflito
    try:
        cursor.execute('''
            INSERT INTO Reservas (nome, matricula, setor, sala_id, data, periodo, equipamentos)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, matricula, setor, sala_id, data, periodo, equipamentos))
        conn.commit()
    except Exception as e:
        print(f"Erro ao inserir reserva: {e}")
        return f"Erro ao realizar a reserva: {e}"
    finally:
        conn.close()

    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar_reserva(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Reservas WHERE id = ?', (id,))
        conn.commit()
    except Exception as e:
        print(f"Erro ao deletar reserva: {e}")
        return f"Erro ao deletar a reserva: {e}"
    finally:
        conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
