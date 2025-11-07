# seances.py
import sqlite3
from flask import request, jsonify, render_template
from app import app  # ⬅️ on importe ton application Flask existante

# ----------------------------
# Classe Seance
# ----------------------------
class Seance:
    def __init__(self, film_id, salle, horaire):
        self.film_id = film_id
        self.salle = salle
        self.horaire = horaire

    def save_to_db(self):
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()

        # Créer la table des séances si elle n'existe pas encore
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                film_id INTEGER,
                salle INTEGER,
                horaire TEXT,
                FOREIGN KEY(film_id) REFERENCES films(id)
            )
        ''')

        # Vérifier que la salle est libre à cet horaire
        cursor.execute('''
            SELECT * FROM seances WHERE salle = ? AND horaire = ?
        ''', (self.salle, self.horaire))
        salle_pris = cursor.fetchone()
        if salle_pris:
            conn.close()
            raise Exception(f"La salle {self.salle} est déjà occupée à {self.horaire}.")

        # Vérifier que le film existe
        cursor.execute('SELECT * FROM films WHERE id = ?', (self.film_id,))
        film = cursor.fetchone()
        if not film:
            conn.close()
            raise Exception(f"Film avec ID {self.film_id} inexistant.")

        # Enregistrer la séance
        cursor.execute('''
            INSERT INTO seances (film_id, salle, horaire)
            VALUES (?, ?, ?)
        ''', (self.film_id, self.salle, self.horaire))
        conn.commit()
        conn.close()


# ----------------------------
# Route Flask : ajout d’une séance
# ----------------------------
@app.route('/add_seance', methods=['POST'])
def add_seance():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400

    required = ['film_id', 'salle', 'horaire']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant: {key}"}), 400

    salle = data['salle']
    if salle < 1 or salle > 5:
        return jsonify({'message': 'Le numéro de salle doit être compris entre 1 et 5.'}), 400

    try:
        seance = Seance(
            film_id=data['film_id'],
            salle=salle,
            horaire=data['horaire']
        )
        seance.save_to_db()
        return jsonify({'message': 'Séance créée avec succès ✅'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400


# ----------------------------
# Route Flask : liste des séances
# ----------------------------
@app.route('/seances', methods=['GET'])
def get_seances():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT seances.id, films.title, seances.salle, seances.horaire
        FROM seances
        JOIN films ON seances.film_id = films.id
        ORDER BY seances.horaire
    ''')
    rows = cursor.fetchall()
    conn.close()

    seances = [
        {'id': row[0], 'film': row[1], 'salle': row[2], 'horaire': row[3]}
        for row in rows
    ]
    return jsonify(seances), 200



# ----------------------------
# Page HTML pour le gérant (optionnelle)
# ----------------------------
@app.route('/ajoutseance')
def ajout_seance_page():
    return render_template('ajoutseance.html')

