import sqlite3
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'change'
CORS(app, supports_credentials=True)

class Films : 
    def __init__(self, title, year, genre, duration, classification):
        self.title = title
        self.year = year
        self.genre = genre
        self.duration = duration
        self.classification = classification
    def save_to_db(self):
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS films (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                year INTEGER,
                genre TEXT,
                duration INTEGER,
                classification TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO films (title, year, genre, duration, classification)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.title, self.year, self.genre, self.duration, self.classification))
        conn.commit()
        conn.close()

class Room :
    def __init__(self, number, capacity):
        self.number  = number
        self.capacity = capacity
    def save_to_db(self):
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER,
                capacity INTEGER
            )
        ''')
        cursor.execute('''
            INSERT INTO salles (number, capacity)
            VALUES (?, ?)
        ''', (self.number, self.capacity))
        conn.commit()
        conn.close()

class Users :
    def __init__(self, username, password, role='user'):
        self.username = username
        self.password = password
        self.role = role
    def save_to_db(self):
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', (self.username, self.password, self.role))
        conn.commit()
        conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400
    required = ['username', 'password']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant: {key}"}), 400
    
    # Par défaut, les nouveaux utilisateurs sont 'user', sauf si un rôle est spécifié
    role = data.get('role', 'user')
    if role not in ['admin', 'user']:
        role = 'user'
    
    try:
        new_user = Users(
            username=data['username'],
            password=data['password'],
            role=role
        )
        new_user.save_to_db()
        return jsonify({'message': 'Utilisateur enregistré avec succès', 'role': role}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Ce nom d\'utilisateur existe déjà'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400
    username = data['username']
    password = data['password']
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, password, role FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        session['username'] = result[1]
        session['role'] = result[3] if len(result) > 3 else 'user'
        return jsonify({
            'message': 'Connexion réussie',
            'username': result[1],
            'role': session['role']
        }), 200
    else:
        return jsonify({'message': 'Identifiants invalides'}), 401

@app.route('/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({
            'message': 'Session valide',
            'username': session['username'],
            'role': session.get('role', 'user')
        }), 200
    else:
        return jsonify({'message': 'Aucune session active'}), 401

@app.route('/add_film', methods=['POST'])
def add_film():
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Accès refusé. Réservé aux administrateurs.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400
    required = ['title', 'year', 'genre', 'duration', 'classification']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant: {key}"}), 400
    new_film = Films(
        title=data['title'],
        year=data['year'],
        genre=data['genre'],
        duration=data['duration'],
        classification=data['classification']
    )
    new_film.save_to_db()
    return jsonify({'message': 'Film added successfully'}), 201

@app.route('/films', methods=['GET'])
def get_films():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, year, genre, duration, classification
        FROM films
        ORDER BY title
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    films = [
        {
            'id': row[0],
            'title': row[1],
            'year': row[2],
            'genre': row[3],
            'duration': row[4],
            'classification': row[5]
        }
        for row in rows
    ]
    return jsonify(films), 200

@app.route('/add_room', methods=['POST'])
def add_room():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400
    required = ['number', 'capacity']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant: {key}"}), 400
    new_room = Room(
        number=data['number'],
        capacity=data['capacity']
    )
    new_room.save_to_db()
    return jsonify({'message': 'Room added successfully'}), 201

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/ajoutfilm')
def ajout_film():
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return render_template('error.html', message='Accès refusé. Réservé aux administrateurs.'), 403
    return render_template('ajoutfilm.html')

@app.route('/inscription')
def inscription():
    return render_template('inscription.html')

@app.route('/connection')
def connection():
    return render_template('connection.html')

@app.route('/ajoutsalle')
def ajout_salle():
    return render_template('ajoutsalle.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Déconnexion réussie'}), 200

import seances

if __name__ == '__main__':
    app.run(debug=True)