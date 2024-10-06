from flask import Flask, request, render_template_string, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'  # Chave secreta para a sessão
db = SQLAlchemy(app)

# Modelo para Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Adicionando senha

# Função para inicializar o banco de dados
def init_db():
    db.create_all()
    if not User.query.first():
        users = [
            User(name='Alice', email='alice@example.com', password='password123'),
            User(name='Bob', email='bob@example.com', password='password123'),
            User(name='Charlie', email='charlie@example.com', password='password123')
        ]
        db.session.bulk_save_objects(users)
        db.session.commit()

# Redireciona a rota inicial para o login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Validação de credenciais (Consulta SQL direta para demonstração)
        query = text(f"SELECT * FROM user WHERE email='{email}' AND password='{password}'")
        user = db.session.execute(query).fetchone()
        
        if user:
            session['user_id'] = user[0]  # user[0] corresponde ao campo 'id'
            return redirect(url_for('search'))
        else:
            return "Credenciais inválidas. Tente novamente."

    return render_template_string("""
        <h1>Login</h1>
        <form method="post">
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Senha" required>
            <button type="submit">Entrar</button>
        </form>
        <nav>
            <a href="{{ url_for('login') }}">Login</a> |
            <a href="{{ url_for('search') }}">Pesquisa</a> |
            <a href="{{ url_for('logout') }}">Logout</a>
        </nav>
    """)

# Rota de Pesquisa (acessível apenas para usuários autenticados)
@app.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    query_str = request.args.get('query', '')
    try:
        query = text(f"SELECT * FROM user WHERE name LIKE '%{query_str}%'")
        results = db.session.execute(query)
        users = [f"{row[0]}: {row[1]} ({row[2]})" for row in results]  # Acessa as colunas por índice
    except Exception as e:
        error_message = "Ocorreu um erro ao processar sua solicitação. Tente novamente."
        return render_template_string("""
            <h1>Resultado da Pesquisa</h1>
            <form method="get">
                <input type="text" name="query" placeholder="Nome do Utilizador" value="{{ request.args.get('query', '') }}" required>
                <button type="submit">Pesquisar</button>
            </form>
            <p style="color: red;">{{ error_message }}</p>
            <nav>
                <a href="{{ url_for('login') }}">Login</a> |
                <a href="{{ url_for('search') }}">Pesquisa</a> |
                <a href="{{ url_for('logout') }}">Logout</a>
            </nav>
        """, error_message=error_message)
    
    return render_template_string("""
        <h1>Resultado da Pesquisa</h1>
        <form method="get">
            <input type="text" name="query" placeholder="Nome do Utilizador" value="{{ request.args.get('query', '') }}" required>
            <button type="submit">Pesquisar</button>
        </form>
        <ul>
            {% for user in users %}
                <li>{{ user }}</li>
            {% endfor %}
        </ul>
        <nav>
            <a href="{{ url_for('login') }}">Login</a> |
            <a href="{{ url_for('search') }}">Pesquisa</a> |
            <a href="{{ url_for('logout') }}">Logout</a>
        </nav>
    """, users=users)

# Rota de Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Inicializar o banco de dados
    with app.app_context():
        init_db()
    
    app.run(debug=True)


    '''
    NOTAS: 
    
    ##Página Login:
        alterar no DevTools o campo "email" do formulário para type="text" para não pedir o caracter "@"
        email: ' or '1'='1';--
        password: <inserir qualquer coisa>

        Resultado: faz login e Dá acesso a todos os users da BD

    ##Página Pesquisa
        após fazer o login, colocar no campo da pesquisa:
        %' OR '1'='1

        Resultado: vai retornar todos os utilizadores da BD

        NOTA: os descbribes podem mudar de tipo de BD (POstgers, MySql, etc)
        Mostrar o describe da tabela User

        MySQL:
        %' UNION SELECT 1, name, type, 4 FROM pragma_table_info('user') --

        Postgres:
        %' UNION SELECT 1, column_name, data_type, 4 FROM information_schema.columns WHERE table_name = 'user' --

    
    '''