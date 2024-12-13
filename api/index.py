from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__,
    static_folder='../static',
    template_folder='../templates')

# Conexão com MongoDB
client = MongoClient('sua_string_conexao_mongodb')
db = client.agenda_salas

@app.route('/')
def menu():
    return render_template('index.html')

@app.route('/agendar', methods=['GET', 'POST'])
def agendar_sala():
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        setor = request.form['setor']
        sala_id = request.form['sala_id']
        data = request.form['data']
        periodo = request.form['periodo']
        equipamentos = request.form.getlist('equipamentos')

        # Verificar conflitos
        reserva_existente = db.reservas.find_one({
            'sala_id': sala_id,
            'data': data,
            'periodo': periodo
        })

        if reserva_existente:
            flash('Erro: Esta sala já foi reservada para este período e data.')
            return redirect(url_for('agendar_sala'))

        nova_reserva = {
            'nome': nome,
            'matricula': matricula,
            'setor': setor,
            'sala_id': sala_id,
            'data': data,
            'periodo': periodo,
            'equipamentos': equipamentos
        }

        try:
            db.reservas.insert_one(nova_reserva)
            flash('Reserva efetuada com sucesso!')
        except Exception as e:
            print(f"Erro ao inserir reserva: {e}")
            return f"Erro ao realizar a reserva: {e}"

        return redirect(url_for('agenda'))

    equipamentos = list(db.equipamentos.find())
    salas = list(db.salas.find())
    return render_template('agendar_sala.html', 
                         equipamentos=equipamentos, 
                         salas=salas)

@app.route('/get_reservas')
def get_reservas():
    reservas = list(db.reservas.aggregate([
        {
            '$lookup': {
                'from': 'salas',
                'localField': 'sala_id',
                'foreignField': '_id',
                'as': 'sala'
            }
        }
    ]))

    eventos = []
    for reserva in reservas:
        periodo = reserva['periodo']
        
        if periodo == 'matutino':
            start_time = '08:00'
            end_time = '12:00'
        elif periodo == 'vespertino':
            start_time = '13:00'
            end_time = '17:00'
        else: # integral
            start_time = '08:00'
            end_time = '17:00'
        
        sala_nome = reserva['sala'][0]['nome'] if reserva['sala'] else ''
        
        evento = {
            'id': str(reserva['_id']),
            'title': f"{reserva['nome']} - {sala_nome}",
            'start': f"{reserva['data']}T{start_time}",
            'end': f"{reserva['data']}T{end_time}"
        }
        eventos.append(evento)

    return jsonify(eventos)

@app.route('/agenda')
def agenda():
    reservas = list(db.reservas.aggregate([
        {
            '$lookup': {
                'from': 'salas',
                'localField': 'sala_id',
                'foreignField': '_id',
                'as': 'sala'
            }
        },
        {
            '$sort': {'data': -1}
        }
    ]))
    return render_template('agenda.html', reservas=reservas)

@app.route('/equipamentos', methods=['GET', 'POST'])
def equipamentos():
    if request.method == 'POST':
        equipamento = {
            'nome': request.form['nome'],
            'quantidade': int(request.form['quantidade'])
        }

        try:
            db.equipamentos.insert_one(equipamento)
            flash('Equipamento cadastrado com sucesso!')
        except Exception as e:
            print(f"Erro ao cadastrar equipamento: {e}")
            flash('Erro ao cadastrar equipamento!')

        return redirect(url_for('equipamentos'))

    equipamentos = list(db.equipamentos.find().sort('nome'))
    return render_template('equipamentos.html', equipamentos=equipamentos)

@app.route('/deletar/<id>')
def deletar_reserva(id):
    try:
        from bson.objectid import ObjectId
        db.reservas.delete_one({'_id': ObjectId(id)})
        flash('Reserva excluída com sucesso!')
    except Exception as e:
        print(f"Erro ao deletar reserva: {e}")
        flash('Erro ao excluir reserva!')
    
    return redirect(url_for('agenda'))

@app.route('/editar/<id>', methods=['GET', 'POST'])
def editar_reserva(id):
    from bson.objectid import ObjectId
    
    if request.method == 'POST':
        try:
            db.reservas.update_one(
                {'_id': ObjectId(id)},
                {'$set': {
                    'nome': request.form['nome'],
                    'matricula': request.form['matricula'],
                    'setor': request.form['setor'],
                    'sala_id': request.form['sala_id'],
                    'data': request.form['data'],
                    'periodo': request.form['periodo'],
                    'equipamentos': request.form.getlist('equipamentos')
                }}
            )
            flash('Reserva alterada com sucesso!')
        except Exception as e:
            print(f"Erro ao atualizar reserva: {e}")
            flash('Erro ao atualizar reserva!')

        return redirect(url_for('agenda'))

    reserva = db.reservas.find_one({'_id': ObjectId(id)})
    equipamentos = list(db.equipamentos.find().sort('nome'))
    salas = list(db.salas.find().sort('nome'))

    return render_template('editar_reserva.html', 
                         reserva=reserva, 
                         equipamentos=equipamentos,
                         salas=salas)

if __name__ == '__main__':
    app.run(host='0.0.0.0')