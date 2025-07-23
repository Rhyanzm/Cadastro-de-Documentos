from flask import Flask, render_template, request, redirect, url_for, flash, session
from templates.database import init_db, get_db_connection
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui' # Mude para uma string longa e complexa

# Inicializa o banco de dados na primeira execução
init_db()

# --- Funções Auxiliares ---
def get_status_validade(data_validade):
    if not data_validade:
        return {'status': 'N/A', 'cor': 'gray'}

    hoje = datetime.now().date()
    validade_dt = datetime.strptime(data_validade, '%Y-%m-%d').date()

    if validade_dt < hoje:
        return {'status': 'Vencido', 'cor': 'red'}
    elif validade_dt - hoje <= timedelta(days=60): # 60 dias para "próximo a vencer"
        return {'status': 'Próximo a Vencer', 'cor': 'orange'}
    else:
        return {'status': 'Em Dia', 'cor': 'green'}

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rotas (URLs do seu site) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar_colaborador', methods=['POST'])
def consultar_colaborador():
    codigo = request.form['codigo_registro']
    if len(codigo) != 6 or not codigo.isdigit():
        flash('O código de registro deve ter 6 dígitos.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    colaborador = conn.execute('SELECT * FROM colaboradores WHERE codigo_registro = ?', (codigo,)).fetchone()
    conn.close()

    if colaborador:
        # Preparar os dados para exibição
        colaborador_dict = dict(colaborador)
        colaborador_dict['nr33_status'] = get_status_validade(colaborador_dict['nr33_validade'])
        colaborador_dict['nr18_status'] = get_status_validade(colaborador_dict['nr18_validade'])
        colaborador_dict['nr35_status'] = get_status_validade(colaborador_dict['nr35_validade'])
        colaborador_dict['nr10_status'] = get_status_validade(colaborador_dict['nr10_validade'])
        colaborador_dict['aso_status'] = get_status_validade(colaborador_dict['aso_validade'])

        return render_template('detalhes_colaborador.html', colaborador=colaborador_dict)
    else:
        flash('Colaborador não encontrado.', 'danger')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios_administrativos WHERE username = ?', (username,)).fetchone()
        conn.close()

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
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    conn = get_db_connection()
    colaboradores = conn.execute('SELECT * FROM colaboradores').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', colaboradores=colaboradores)

@app.route('/add_edit_colaborador', methods=['GET', 'POST'])
@login_required
def add_edit_colaborador():
    colaborador = None
    if request.args.get('id'):
        colaborador_id = request.args.get('id')
        conn = get_db_connection()
        colaborador = conn.execute('SELECT * FROM colaboradores WHERE id = ?', (colaborador_id,)).fetchone()
        conn.close()
        if not colaborador:
            flash('Colaborador não encontrado.', 'danger')
            return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        codigo_registro = request.form['codigo_registro']
        nr33_validade = request.form['nr33_validade'] if request.form['nr33_validade'] else None
        nr18_validade = request.form['nr18_validade'] if request.form['nr18_validade'] else None
        nr35_validade = request.form['nr35_validade'] if request.form['nr35_validade'] else None
        nr10_aplicavel = 'nr10_aplicavel' in request.form
        nr10_validade = request.form['nr10_validade'] if request.form['nr10_validade'] else None
        aso_validade = request.form['aso_validade'] if request.form['aso_validade'] else None
        observacoes = request.form['observacoes'] if request.form['observacoes'] else None

        if len(codigo_registro) != 6 or not codigo_registro.isdigit():
            flash('O código de registro deve ter 6 dígitos.', 'danger')
            return render_template('form_colaborador.html', colaborador=colaborador)

        conn = get_db_connection()
        try:
            if colaborador: # Edição
                conn.execute('''
                    UPDATE colaboradores SET
                    nome_completo = ?, codigo_registro = ?, nr33_validade = ?, nr18_validade = ?,
                    nr35_validade = ?, nr10_validade = ?, nr10_aplicavel = ?, aso_validade = ?, observacoes = ?
                    WHERE id = ?
                ''', (nome_completo, codigo_registro, nr33_validade, nr18_validade, nr35_validade,
                      nr10_validade, nr10_aplicavel, aso_validade, observacoes, colaborador['id']))
                flash('Colaborador atualizado com sucesso!', 'success')
            else: # Cadastro
                conn.execute('''
                    INSERT INTO colaboradores (nome_completo, codigo_registro, nr33_validade, nr18_validade,
                    nr35_validade, nr10_validade, nr10_aplicavel, aso_validade, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nome_completo, codigo_registro, nr33_validade, nr18_validade, nr35_validade,
                      nr10_validade, nr10_aplicavel, aso_validade, observacoes))
                flash('Colaborador cadastrado com sucesso!', 'success')
            conn.commit()
            return redirect(url_for('admin_dashboard'))
        except sqlite3.IntegrityError:
            flash('Código de registro já existe. Escolha outro.', 'danger')
        except Exception as e:
            flash(f'Erro ao salvar colaborador: {e}', 'danger')
        finally:
            conn.close()

    return render_template('form_colaborador.html', colaborador=colaborador)


@app.route('/delete_colaborador/<int:id>')
@login_required
def delete_colaborador(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM colaboradores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Colaborador excluído com sucesso!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True) # debug=True para desenvolvimento (reinicia o servidor em mudanças)

    import psycopg2

conn = psycopg2.connect(
    host="dpg-d1vto4fdiees73c1j9qg-a",
    database="colaboradores",
    user="admin",
    password="VhEMv8vC5zPW7HCuFc7waY8YGMAN60hn",
    port="5432"
)
cursor = conn.cursor()
from flask import Flask, request, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)

# Dados do Render (pegue da aba "DATABASE" na sua conta Render)
DB_HOST = 'dpg-d1vto4fdiees73c1j9qg-a'
DB_NAME = 'meu_banco_colaboradores'
DB_USER = 'admin'
DB_PASS = 'VhEMv8vC5zPW7HCuFc7waY8YGMAN60hn'
DB_PORT = '5432'

def conectar():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.json
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO colaboradores (
                nome, codigo_registro,
                nr6_aplicavel, nr6_validade,
                nr10_aplicavel, nr10_validade
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            dados['nome'], dados['codigo_registro'],
            dados['nr6_aplicavel'], dados['nr6_validade'],
            dados['nr10_aplicavel'], dados['nr10_validade']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensagem': 'Colaborador cadastrado com sucesso!'})
    except Exception as e:
        return jsonify({'erro': str(e)})

@app.route('/listar')
def listar():
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT * FROM colaboradores")
        resultado = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'erro': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
