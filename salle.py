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

    number = data['number']
    capacity = data['capacity']

    if not isinstance(number, int) or not isinstance(capacity, int):
        return jsonify({'message': 'number et capacity doivent être des entiers.'}), 400

    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS salles (id INTEGER PRIMARY KEY AUTOINCREMENT, number INTEGER, capacity INTEGER)")
    cursor.execute("SELECT * FROM salles WHERE number = ?", (number,))
    exists = cursor.fetchone()

    if exists:
        conn.close()
        return jsonify({'message': f"La salle numéro {number} existe déjà."}), 409

    # Sauvegarde en base
    try:
        new_room = Room(number, capacity)
        new_room.save_to_db()
    except Exception as e:
        conn.close()
        return jsonify({'message': 'Erreur lors de l\'ajout en base de données', 'error': str(e)}), 500

    conn.close()
    return jsonify({'message': 'Salle ajoutée avec succès', 'number': number, 'capacity': capacity}), 201
