 # seances.py
import sqlite3
from flask import request, jsonify, render_template
from datetime import datetime, timedelta
from app import app  # ⬅️ on importe ton application Flask existante

# ----------------------------
# Classe Seance
# ----------------------------
class Seance:
    def __init__(self, film_id, salle, horaire):
        self.film_id = film_id
        self.salle = salle
        self.horaire = horaire  # attendu au format "YYYY-MM-DD HH:MM"

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

        # Vérifier que le film existe et récupérer sa durée
        cursor.execute('SELECT * FROM films WHERE id = ?', (self.film_id,))
        film = cursor.fetchone()
        if not film:
            conn.close()
            raise Exception(f"Film avec ID {self.film_id} inexistant.")

        duree_film_minutes = film[2]  # supposons que la colonne durée est à l'index 2

        # Conversion horaire en datetime
        horaire_dt = datetime.strptime(self.horaire, "%Y-%m-%d %H:%M")
        fin_horaire_dt = horaire_dt + timedelta(minutes=duree_film_minutes)

        # Vérifier chevauchement avec d'autres séances dans la même salle
        cursor.execute('''
            SELECT seances.horaire, films.duree
            FROM seances
            JOIN films ON seances.film_id = films.id
            WHERE seances.salle = ?
        ''', (self.salle,))
        autres_seances = cursor.fetchall()

        for row in autres_seances:
            horaire_existante_dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M")
            fin_existante_dt = horaire_existante_dt + timedelta(minutes=row[1])

            # Condition de chevauchement
            if (horaire_dt < fin_existante_dt) and (fin_horaire_dt > horaire_existante_dt):
                conn.close()
                raise Exception(
                    f"La salle {self.salle} est déjà occupée entre "
                    f"{horaire_existante_dt.strftime('%H:%M')} et {fin_existante_dt.strftime('%H:%M')}."
                )

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
