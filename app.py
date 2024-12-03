from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import bcrypt
from functools import wraps
import os

app = Flask(__name__)

db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'plataforma_educacional')
}

app.secret_key = 'testeteste123'

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Erro ao conectar no banco: {e}")
        return None
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        if session['user_type'] == 'admin':
            return render_template('index.html')
        elif session['user_type'] == 'professor':
            return redirect(url_for('listar_alunos')) 
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        print("Email recebido:", email)
        print("Senha recebida:", senha)

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            print("Resultado da consulta:", user)

            if user:
                senha_hash = user['senha_hash']
                print("Hash armazenado no banco:", senha_hash)

                if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                    session['user_id'] = user['id']
                    session['user_type'] = user['tipo']
                    print("Login bem-sucedido!")
                    return redirect(url_for('listar_alunos')) if user['tipo'] == 'professor' else redirect(url_for('index'))
                else:
                    print("Senha incorreta!")
                    return render_template('login.html', error="Senha incorreta.")
            else:
                print("Usuário não encontrado!")
                return render_template('login.html', error="Usuário não encontrado.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    tipo = request.form['tipo']

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (%s, %s, %s, %s)",
            (nome, email, senha_hash.decode('utf-8'), tipo)
        )
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_aluno():
    try:
        connection = get_db_connection()
        if connection:
            if request.method == 'GET':
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, nome FROM salas")
                salas = cursor.fetchall()
                cursor.execute("SELECT id, nome FROM aulas")
                aulas = cursor.fetchall()
                cursor.close()
                connection.close()
                return render_template('cadastro_aluno.html', salas=salas, aulas=aulas)

            if request.method == 'POST':
                nome_completo = request.form.get('nome_completo')
                ra = request.form.get('ra')
                idade = request.form.get('idade')
                sala = request.form.get('sala')
                aula_id = request.form.get('aula') 

                if not nome_completo or not ra or not idade or not sala:
                    return "Todos os campos são obrigatórios.", 400

                connection = get_db_connection() 
                cursor = connection.cursor()
                query = """
                    INSERT INTO alunos (nome, ra, idade, sala, aula_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (nome_completo, ra, idade, sala, aula_id if aula_id else None))
                connection.commit()
                cursor.close()
                connection.close()
                return redirect(url_for('listar_alunos'))
        else:
            return "Erro ao conectar no banco de dados.", 500
    except Error as e:
        print(f"Erro ao salvar no banco: {e}")
        return f"Erro ao salvar no banco de dados: {str(e)}", 500
    
@app.route('/alunos')
@login_required
def listar_alunos():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = "SELECT * FROM alunos"
            cursor.execute(query)
            alunos = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('alunos.html', alunos=alunos)
        else:
            return "Erro ao conectar no banco de dados.", 500
    except Error as e:
        print(f"Erro ao buscar alunos: {e}")
        return f"Erro ao buscar alunos: {str(e)}", 500

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_aluno(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alunos WHERE id = %s", (id,))
        aluno = cursor.fetchone()

        if not aluno:
            return "Aluno não encontrado.", 404

        if request.method == 'POST':
            nome_completo = request.form.get('nome_completo')
            ra = request.form.get('ra')
            idade = request.form.get('idade')
            sala = request.form.get('sala')

            cursor.execute("UPDATE alunos SET nome = %s, ra = %s, idade = %s, sala = %s WHERE id = %s",
                           (nome_completo, ra, idade, sala, id))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('listar_alunos'))

        cursor.close()
        connection.close()
        return render_template('edit_aluno.html', aluno=aluno)
    return "Erro ao conectar no banco de dados", 500

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_aluno(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM alunos WHERE id = %s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('listar_alunos'))
    return "Erro ao conectar no banco de dados", 500
    
@app.route('/professores', methods=['GET'])
@login_required
def listar_professores():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE tipo = 'professor'")
        professores = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('professores.html', professores=professores)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/usuarios/cadastro/professor', methods=['GET', 'POST'])
@login_required
def cadastrar_professor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not nome or not email or not senha:
            return "Todos os campos são obrigatórios.", 400

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (%s, %s, %s, %s)",
                    (nome, email, senha_hash.decode('utf-8'), 'professor')
                )
                connection.commit()
            except mysql.connector.Error as err:
                print(f"Erro ao inserir dados: {err}")
                connection.rollback()
                return "Erro ao cadastrar professor. Verifique se o email já está em uso.", 400
            finally:
                cursor.close()
                connection.close()

            return redirect(url_for('listar_professores'))

    return render_template('cadastro_professor.html')

@app.route('/professores/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_professor(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s AND tipo = 'professor'", (id,))
        professor = cursor.fetchone()
        if not professor:
            return "Professor não encontrado", 404

        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')

            cursor.execute("UPDATE usuarios SET nome = %s, email = %s WHERE id = %s", (nome, email, id))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('listar_professores'))

        cursor.close()
        connection.close()
        return render_template('edit_professor.html', professor=professor)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/professores/delete/<int:id>', methods=['POST'])
@login_required
def deletar_professor(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s and tipo like 'professor'", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('listar_professores'))
    return "Erro ao conectar ao banco de dados", 500

@app.route('/salas', methods=['GET'])
@login_required
def listar_salas():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM salas")
        salas = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('salas.html', salas=salas)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/salas/cadastro', methods=['GET', 'POST'])
@login_required
def cadastrar_sala():
    if request.method == 'POST':
        nome = request.form['nome']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO salas (nome) VALUES (%s)", (nome,))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('listar_salas'))
    return render_template('cadastro_sala.html')

@app.route('/salas/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_sala(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM salas WHERE id = %s", (id,))
        sala = cursor.fetchone()
        if not sala:
            return "Sala não encontrada", 404

        if request.method == 'POST':
            nome = request.form['nome']
            cursor.execute("UPDATE salas SET nome = %s WHERE id = %s", (nome, id))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('listar_salas'))

        cursor.close()
        connection.close()
        return render_template('edit_sala.html', sala=sala)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/salas/delete/<int:id>', methods=['POST'])
@login_required
def deletar_sala(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM salas WHERE id = %s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('listar_salas'))
    return "Erro ao conectar ao banco de dados", 500

@app.route('/aulas', methods=['GET'])
@login_required
def listar_aulas():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT aulas.id, aulas.nome AS aula_nome, aulas.horario, salas.nome AS sala_nome, usuarios.nome AS professor_nome
            FROM aulas
            LEFT JOIN salas ON aulas.sala_id = salas.id
            LEFT JOIN usuarios ON aulas.professor_id = usuarios.id AND usuarios.tipo = 'professor'
        """
        cursor.execute(query)
        aulas = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('aulas.html', aulas=aulas)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/aulas/cadastro', methods=['GET', 'POST'])
@login_required
def cadastrar_aula():
    if request.method == 'POST':
        nome = request.form.get('nome')
        horario = request.form.get('horario')
        sala_id = request.form.get('sala_id')
        professor_id = request.form.get('professor_id')

        if not nome or not horario or not sala_id:
            return "Todos os campos obrigatórios devem ser preenchidos.", 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO aulas (nome, horario, sala_id, professor_id) VALUES (%s, %s, %s, %s)",
                (nome, horario, sala_id, professor_id or None)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('listar_aulas'))

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM salas")
        salas = cursor.fetchall()
        cursor.execute("SELECT id, nome FROM usuarios WHERE tipo = 'professor'")
        professores = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('cadastro_aula.html', salas=salas, professores=professores)

    return "Erro ao conectar ao banco de dados", 500

@app.route('/aulas/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_aula(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM aulas WHERE id = %s", (id,))
        aula = cursor.fetchone()
        if not aula:
            return "Aula não encontrada", 404

        if request.method == 'POST':
            nome = request.form['nome']
            horario = request.form['horario']
            sala_id = request.form['sala_id']
            professor_id = request.form.get('professor_id')

            cursor.execute(
                "UPDATE aulas SET nome = %s, horario = %s, sala_id = %s, professor_id = %s WHERE id = %s",
                (nome, horario, sala_id, professor_id or None, id)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('listar_aulas'))

        cursor.execute("SELECT * FROM salas")
        salas = cursor.fetchall()
        cursor.execute("SELECT * FROM usuarios WHERE tipo = 'professor'")
        professores = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('edit_aula.html', aula=aula, salas=salas, professores=professores)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/aulas/delete/<int:id>', methods=['POST'])
@login_required
def deletar_aula(id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM aulas WHERE id = %s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('listar_aulas'))
    return "Erro ao conectar ao banco de dados", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
