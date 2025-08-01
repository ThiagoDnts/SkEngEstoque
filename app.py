import shutil
import os
from flask import Flask, render_template, redirect, request, session, url_for, send_file, send_from_directory
import sqlite3
import pandas as pd
import io


from models import init_db, get_user, add_entry, add_exit, get_stock, get_history

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Inicializa o banco (cria tabelas se não existirem)
init_db()

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM movimentacoes ORDER BY data DESC')
    historico = c.fetchall()
    conn.close()

    return render_template('dashboard.html', historico=historico)

@app.route('/relatorio/excel')
def relatorio_excel():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM movimentacoes ORDER BY data DESC")
    dados = c.fetchall()
    colunas = [description[0] for description in c.description]
    conn.close()

    output = io.StringIO()
    import csv
    writer = csv.writer(output)
    writer.writerow(colunas)
    writer.writerows(dados)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='relatorio_estoque.csv'
    )

@app.route('/backup')
def backup():
    if 'user' not in session:
        return redirect(url_for('login'))

    db_path = os.path.join(os.getcwd(), 'database.db')
    if os.path.exists(db_path):
        # envia o arquivo database.db como anexo para download
        return send_from_directory(directory=os.getcwd(),
                                   path='database.db',
                                   as_attachment=True)
    else:
        return "Arquivo de banco de dados não encontrado.", 404


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        if get_user(nome, senha):
            session['user'] = nome
            return redirect(url_for('index'))
        else:
            erro = "Usuário ou senha inválidos."
    return render_template('login.html', erro=erro)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensagem = None
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        from models import create_user
        if create_user(nome, senha):
            mensagem = 'Usuário criado com sucesso!'
        else:
            mensagem = 'Usuário já existe.'
    return render_template('registro.html', mensagem=mensagem)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/entrada', methods=['GET', 'POST'])
def entrada():
    if request.method == 'POST':
        data = request.form
        add_entry(data)
        return redirect(url_for('index'))
    return render_template('entrada.html')

@app.route('/saida', methods=['GET', 'POST'])
def saida():
    if request.method == 'POST':
        data = request.form
        add_exit(data)
        return redirect(url_for('index'))
    return render_template('saida.html')

@app.route('/historico')
def historico():
    return render_template('historico.html', historico=get_history())

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_movimentacao(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        tipo = request.form['tipo']
        material = request.form['material']
        quantidade = int(request.form['quantidade'])
        valor = float(request.form['valor'])
        data = request.form['data']
        quem_colocou = request.form.get('quem_colocou', '')
        quem_retirou = request.form.get('quem_retirou', '')
        equipe = request.form['equipe']

        c.execute('''
            UPDATE movimentacoes
            SET tipo=?, material=?, quantidade=?, valor=?, data=?, quem_colocou=?, quem_retirou=?, equipe=?
            WHERE id=?
        ''', (tipo, material, quantidade, valor, data, quem_colocou, quem_retirou, equipe, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    c.execute('SELECT * FROM movimentacoes WHERE id=?', (id,))
    mov = c.fetchone()
    conn.close()

    if not mov:
        return "Movimentação não encontrada", 404

    return render_template('editar.html', mov=mov)

@app.route('/excluir/<int:id>', methods=['GET'])
def excluir_movimentacao(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM movimentacoes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

