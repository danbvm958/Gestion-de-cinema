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

class Users :
    def __init__(self, username, password):
        self.username = username
        self.password = password
    def save_to_db(self):
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (?, ?)
        ''', (self.username, self.password))
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
    new_user = Users(
        username=data['username'],
        password=data['password']
    )
    new_user.save_to_db()
    return jsonify({'message': 'Utilisateur enregistré avec succès'}), 201

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
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    result = cursor.fetchone()
    user = Users(username, password) if result else None
    conn.close()
    if user:
        session['username'] = user.username
        return jsonify({'message': 'Connexion réussie'}), 200
    else:
        return jsonify({'message': 'Identifiants invalides'}), 401

@app.route('/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({'message': 'Session valide', 'username': session['username']}), 200
    else:
        return jsonify({'message': 'Aucune session active'}), 401

@app.route('/add_film', methods=['POST'])
def add_film():
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

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/ajoutfilm')
def ajout_film():
    return render_template('ajoutfilm.html')

@app.route('/inscription')
def inscription():
    return render_template('inscription.html')

@app.route('/connection')
def connection():
    return render_template('connection.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Déconnexion réussie'}), 200

import seances  

if __name__ == '__main__':
    app.run(debug=True)