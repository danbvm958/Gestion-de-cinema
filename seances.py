# seances.py
import sqlite3
from flask import request, jsonify, render_template, session
from datetime import datetime, timedelta
from app import app  # on importe ton application Flask

# Classe Seance

class Seance:
    def __init__(self, film_id, salle, horaire):
        self.film_id = film_id
        self.salle = salle

        # --- Acceptation du format "HH:MM" ---
        # on ajoute automatiquement la date du jour
        if len(horaire) == 5:  # ex : "21:00"
            date = datetime.today().strftime("%Y-%m-%d")
            self.horaire = f"{date} {horaire}"
        else:
            self.horaire = horaire

    def save_to_db(self):
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()

        # Création de la table si elle n'existe pas
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
        cursor.execute('SELECT title, duration FROM films WHERE id = ?', (self.film_id,))
        film = cursor.fetchone()
        if not film:
            conn.close()
            raise Exception(f"Film ID {self.film_id} inexistant.")

        duree_film = film[1]  # colonne duration

        # Calcul du début/fin de la séance
        debut = datetime.strptime(self.horaire, "%Y-%m-%d %H:%M")
        fin = debut + timedelta(minutes=duree_film)

        # On récupère les autres séances de la même salle
        cursor.execute('''
            SELECT seances.horaire, films.duration
            FROM seances
            JOIN films ON seances.film_id = films.id
            WHERE seances.salle = ?
        ''', (self.salle,))
        autres_seances = cursor.fetchall()

        # Vérification des chevauchements
        for h_existante, duree_existante in autres_seances:
            debut2 = datetime.strptime(h_existante, "%Y-%m-%d %H:%M")
            fin2 = debut2 + timedelta(minutes=duree_existante)

            # Condition de chevauchement
            if debut < fin2 and fin > debut2:
                conn.close()
                raise Exception(
                    f"Chevauchement détecté : séance existante "
                    f"{debut2.strftime('%H:%M')}–{fin2.strftime('%H:%M')}."
                )

        # Enregistrer la séance
        cursor.execute('''
            INSERT INTO seances (film_id, salle, horaire)
            VALUES (?, ?, ?)
        ''', (self.film_id, self.salle, self.horaire))

        conn.commit()
        conn.close()



# Route Flask : ajout d’une séance

@app.route('/add_seance', methods=['POST'])
def add_seance():
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Accès refusé. Réservé aux administrateurs.'}), 403
    
    data = request.get_json()

    if not data:
        return jsonify({'message': 'JSON manquant.'}), 400

    required = ['film_id', 'salle']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant : {key}"}), 400

    salle = data['salle']
    if salle < 1 or salle > 5:
        return jsonify({'message': 'La salle doit être entre 1 et 5.'}), 400

    # Construire l'horaire complet à partir de date et horaire
    if 'date' in data and 'horaire' in data:
        horaire_complet = f"{data['date']} {data['horaire']}"
    elif 'horaire' in data:
        horaire_complet = data['horaire']
    else:
        return jsonify({'message': 'Champ manquant : horaire ou (date + horaire)'}), 400

    try:
        seance = Seance(
            film_id=data['film_id'],
            salle=salle,
            horaire=horaire_complet
        )
        seance.save_to_db()
        return jsonify({'message': 'Séance créée avec succès ✅'}), 201

    except Exception as e:
        return jsonify({'message': str(e)}), 400



# Route Flask : liste des séances (API JSON)

@app.route('/api/seances', methods=['GET'])
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



# Page HTML 

@app.route('/ajoutseance')
def ajout_seance_page():
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return render_template('error.html', message='Accès refusé. Réservé aux administrateurs.'), 403
    return render_template('ajoutseance.html')

# Page de visualisation des séances (accessible à tous les connectés)
@app.route('/seances')
def seances_page():
    if 'username' not in session:
        return render_template('error.html', message='Veuillez vous connecter pour accéder aux séances.'), 403
    return render_template('seances.html')
