import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
from database import get_connection  # usar sua função correta
from flask import Flask, render_template

app = Flask(__name__)  # NÃO precisa de template_folder se usar a pasta padrão 'templates'

@app.route('/')
def index():
    return render_template('index.html')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'troque_essa_chave')

# Conexão com PostgreSQL (usando DATABASE_URL padrão do Render)
DATABASE_URL = os.getenv('DATABASE_URL')
def conectar():
    return get_connection()

def get_status_validade(data_validade):
    if not data_validade:
        return {'status': 'N/A', 'cor': 'gray'}
    hoje = datetime.now().date()
    validade_dt = data_validade if isinstance(data_validade, datetime) else datetime.strptime(data_validade, '%Y-%m-%d').date()
    if validade_dt < hoje:
        return {'status': 'Vencido', 'cor': 'red'}
    elif validade_dt - hoje <= timedelta(days=60):
        return {'status': 'Próximo a Vencer', 'cor': 'orange'}
    else:
        return {'status': 'Em Dia', 'cor': 'green'}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar_colaborador', methods=['POST'])
def consultar_colaborador():
    codigo = request.form['codigo_registro']
    if len(codigo) != 6 or not codigo.isdigit():
        flash('O código de registro deve ter 6 dígitos.', 'danger')
        return redirect(url_for('index'))

    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute('SELECT * FROM colaboradores WHERE codigo_registro = %s', (codigo,))
        colaborador = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        flash(f'Erro ao consultar colaborador: {e}', 'danger')
        return redirect(url_for('index'))

    if colaborador:
        colaborador['nr33_status'] = get_status_validade(colaborador.get('nr33_validade'))
        colaborador['nr18_status'] = get_status_validade(colaborador.get('nr18_validade'))
        colaborador['nr35_status'] = get_status_validade(colaborador.get('nr35_validade'))
        colaborador['nr10_status'] = get_status_validade(colaborador.get('nr10_validade'))
        colaborador['aso_status'] = get_status_validade(colaborador.get('aso_validade'))
        return render_template('detalhes_colaborador.html', colaborador=colaborador)
    else:
        flash('Colaborador não encontrado.', 'danger')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = conectar()
            cur = conn.cursor()
            cur.execute('SELECT * FROM usuarios_administrativos WHERE username = %s', (username,))
            user = cur.fetchone()
            cur.close()
            conn.close()
        except Exception as e:
            flash(f'Erro no login: {e}', 'danger')
            return render_template('login.html')

        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute('SELECT * FROM colaboradores')
        colaboradores = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        flash(f'Erro ao carregar colaboradores: {e}', 'danger')
        colaboradores = []
    return render_template('admin_dashboard.html', colaboradores=colaboradores)

@app.route('/listar')
def listar():
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT codigo_registro, nome_completo, nr10_aplicavel, nr10_validade FROM colaboradores")
        dados = cur.fetchall()
        colaboradores = []
        for linha in dados:
            colaborador = {
                "codigo_registro": linha['codigo_registro'],
                "nome": linha['nome_completo'],
                "cargo": "N/A",  # campo cargo não existe no banco, adicione aqui se desejar
                "nr10_aplicavel": linha['nr10_aplicavel'],
                "nr10_validade": linha['nr10_validade'].isoformat() if linha['nr10_validade'] else None
            }
            colaboradores.append(colaborador)
        cur.close()
        conn.close()
        return jsonify(colaboradores)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
