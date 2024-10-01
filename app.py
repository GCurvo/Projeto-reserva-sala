from flask import Flask, render_template, redirect, url_for, request, flash
from database import conectar, criar_tabelas

app = Flask(__name__)
app.secret_key = 'chave_secreta'

# Garantir que as tabelas sejam criadas ao iniciar o aplicativo
criar_tabelas()

# Rota para o menu principal
@app.route('/')
def menu():
    return render_template('index.html')

# Rota para agendar uma sala (página de agendamento de sala)
@app.route('/agendar', methods=['GET', 'POST'])
def agendar_sala():
    if request.method == 'POST':
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
        cursor.execute('SELECT periodo FROM Reservas WHERE sala_id = ? AND data = ?', (sala_id, data))
        reservas_existentes = cursor.fetchall()

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
            flash('Erro: Esta sala já foi reservada para este período e data.')
            return redirect(url_for('agendar_sala'))

        try:
            cursor.execute('''INSERT INTO Reservas (nome, matricula, setor, sala_id, data, periodo, equipamentos)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', (nome, matricula, setor, sala_id, data, periodo, equipamentos))
            conn.commit()
            flash('Reserva efetuada com sucesso!')
        except Exception as e:
            print(f"Erro ao inserir reserva: {e}")
            return f"Erro ao realizar a reserva: {e}"
        finally:
            conn.close()

        return redirect(url_for('agenda'))

    # Listar os equipamentos para o formulário
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Equipamentos')
    equipamentos = cursor.fetchall()
    conn.close()

    return render_template('agendar_sala.html', equipamentos=equipamentos)

# Rota para visualizar a agenda de reservas
@app.route('/agenda')
def agenda():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''SELECT Reservas.nome, Reservas.data, Reservas.periodo, Sala.nome AS sala_nome, Reservas.equipamentos, Reservas.id
                      FROM Reservas
                      JOIN Sala ON Reservas.sala_id = Sala.id''')
    reservas = cursor.fetchall()
    conn.close()
    return render_template('agenda.html', reservas=reservas)

# Rota para gerenciar os equipamentos (cadastrar, editar, excluir)
@app.route('/equipamentos', methods=['GET', 'POST'])
def equipamentos():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome_equip = request.form['nome']
        quantidade = request.form['quantidade']

        try:
            cursor.execute('INSERT INTO Equipamentos (nome, quantidade) VALUES (?, ?)', (nome_equip, quantidade))
            conn.commit()
            flash('Equipamento cadastrado com sucesso!')
        except Exception as e:
            print(f"Erro ao cadastrar equipamento: {e}")
            return f"Erro ao cadastrar o equipamento: {e}"
        finally:
            conn.close()

        return redirect(url_for('equipamentos'))

    cursor.execute('SELECT * FROM Equipamentos')
    equipamentos = cursor.fetchall()
    conn.close()

    return render_template('equipamentos.html', equipamentos=equipamentos)

# Rota para deletar reserva
@app.route('/deletar/<int:id>')
def deletar_reserva(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Reservas WHERE id = ?', (id,))
        conn.commit()
        flash('Reserva excluída com sucesso!')
    except Exception as e:
        print(f"Erro ao deletar reserva: {e}")
        return f"Erro ao deletar a reserva: {e}"
    finally:
        conn.close()
    
    return redirect(url_for('agenda'))

# Rota para editar reserva
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_reserva(id):
    conn = conectar()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        setor = request.form['setor']
        sala_id = request.form['sala_id']
        data = request.form['data']
        periodo = request.form['periodo']
        equipamentos = ', '.join(request.form.getlist('equipamentos'))

        try:
            cursor.execute('''UPDATE Reservas
                              SET nome = ?, matricula = ?, setor = ?, sala_id = ?, data = ?, periodo = ?, equipamentos = ?
                              WHERE id = ?''', (nome, matricula, setor, sala_id, data, periodo, equipamentos, id))
            conn.commit()
            flash('Reserva alterada com sucesso!')
        except Exception as e:
            print(f"Erro ao atualizar reserva: {e}")
            return f"Erro ao atualizar a reserva: {e}", 400
        finally:
            conn.close()

        return redirect(url_for('agenda'))

    # Carregar os dados existentes para serem editados
    cursor.execute('SELECT * FROM Reservas WHERE id = ?', (id,))
    reserva = cursor.fetchone()
    conn.close()

    return render_template('editar_reserva.html', reserva=reserva)

# Rota para deletar equipamentos
@app.route('/deletar_equipamento/<int:id>')
def deletar_equipamento(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Equipamentos WHERE id = ?', (id,))
        conn.commit()
        flash('Equipamento excluído com sucesso!')
    except Exception as e:
        print(f"Erro ao deletar equipamento: {e}")
        return f"Erro ao excluir o equipamento: {e}"
    finally:
        conn.close()
    
    return redirect(url_for('equipamentos'))

# Rota para editar equipamentos
@app.route('/editar_equipamento/<int:id>', methods=['GET', 'POST'])
def editar_equipamento(id):
    conn = conectar()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']

        try:
            cursor.execute('''UPDATE Equipamentos
                              SET nome = ?, quantidade = ?
                              WHERE id = ?''', (nome, quantidade, id))
            conn.commit()
            flash('Equipamento alterado com sucesso!')
        except Exception as e:
            print(f"Erro ao atualizar equipamento: {e}")
            return f"Erro ao atualizar o equipamento: {e}", 400
        finally:
            conn.close()

        return redirect(url_for('equipamentos'))

    # Carregar os dados existentes para serem editados
    cursor.execute('SELECT * FROM Equipamentos WHERE id = ?', (id,))
    equipamento = cursor.fetchone()
    conn.close()

    return render_template('editar_equipamento.html', equipamento=equipamento)

if __name__ == '__main__':
    app.run(debug=True)
