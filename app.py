from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_PATH = 'users.db'
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
LOG_FILE = 'logs/ingresos.txt'

# Ensure necessary directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


import sqlite3
import os # Importar os para manejar rutas si es necesario

# Define la ruta de la base de datos
# Asegúrate de que esta ruta sea accesible y donde quieres guardar tu DB
DB_PATH = 'your_database.db' # <--- Define esta variable

# Asegúrate de que el directorio para la DB exista si no está en la raíz
# db_dir = os.path.dirname(DB_PATH)
# if db_dir and not os.path.exists(db_dir):
#     os.makedirs(db_dir)


# @app.before_first_request # Asegúrate de que 'app' esté definido en tu aplicación Flask/otro framework
def create_tables():
    # Usa un bloque 'with' para asegurar que la conexión se cierre
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL)''')
        conn.commit()
    # La conexión se cierra automáticamente al salir del bloque 'with'


@app.route('/')
def index():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        # Use 'with' statement for database connection
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
        except sqlite3.IntegrityError:
            return "Usuario ya existe"
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Use 'with' statement for database connection
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = c.fetchone()

        if row and check_password_hash(row[0], password):
            session['user'] = username
            # Write to log file with correct newline
            with open(LOG_FILE, 'a') as f:
                f.write("User: {} - Login at {}\n".format(username, datetime.now()))
            return redirect(url_for('index'))
        return "Credenciales incorrectas"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    converted_path = os.path.join(CONVERTED_FOLDER, f"{filename}.converted.txt")
    with open(filepath, 'rb') as fin, open(converted_path, 'wb') as fout:
        fout.write(fin.read())  # Simula conversión
    return send_file(converted_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)
