import sqlite3
from flask import request, jsonify, render_template
from app import app 

class Room :
    def __init__(self, number, capacity):
        self.number = number
        self.capacity = capacity
    def save_to_db(self):
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Room (
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