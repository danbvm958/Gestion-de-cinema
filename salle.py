import sqlite3
from flask import request, jsonify, render_template
from app import app 

class Room:
    def __init__(self, number, capacity):
        self.number = number
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

@app.route('/add_room', methods=['POST'])
def add_room():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400

    required = ['number', 'capacity']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant : {key}"}), 400

    try:
        number = int(data['number'])
        capacity = int(data['capacity'])
    except ValueError:
        return jsonify({'message': 'number et capacity doivent être des entiers.'}), 400

    try:
        with sqlite3.connect('cinema.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS salles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number INTEGER UNIQUE,
                    capacity INTEGER
                )
            ''')
            cursor.execute("SELECT * FROM salles WHERE number = ?", (number,))
            if cursor.fetchone():
                return jsonify({'message': f"La salle numéro {number} existe déjà."}), 409

            cursor.execute("INSERT INTO salles (number, capacity) VALUES (?, ?)", (number, capacity))
            conn.commit()

        return jsonify({'message': 'Salle ajoutée avec succès', 'number': number, 'capacity': capacity}), 201

    except sqlite3.Error as e:
        return jsonify({'message': 'Erreur base de données', 'error': str(e)}), 500

@app.route('/salles', methods=['GET'])
def get_salles():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, number, capacity
        FROM salles
        ORDER BY number
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    salles = [
        {
            'id': row[0],
            'number': row[1],
            'capacity': row[2]
        }
        for row in rows
    ]
    return jsonify(salles), 200
