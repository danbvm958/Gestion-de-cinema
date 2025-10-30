import sqlite3

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

def load_data():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM films')
    films = cursor.fetchall()
    conn.close()
    return films

def main():
    option = 0
    while option != 8:
        print("Menu:")
        print("1. Add Film")
        print("2. Add a room ")
        print("3. Add a session")
        print("4. Login")
        print("5. Register")
        print("6. Book a session")
        print("7. Load Data")
        print("8. Exit")
        option = int(input("Choose an option: "))

        match option:
            case 1:
                title = input("Enter film title: ")
                year = int(input("Enter film year: "))
                genre = input("Enter film genre: ")
                duration = int(input("Enter film duration (in minutes): "))
                classification = input("Enter film classification: ")
                film = Films(title, year, genre, duration, classification)
                film.save_to_db()
                print("Film added successfully!")
            case 7:
                data = load_data()
                print(data)
                print("Data loaded successfully!")
            case _:
                print("Option non reconnue, veuillez réessayer.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterruption par l'utilisateur. Au revoir.")
    except Exception as e:
        print("Une erreur s'est produite :", e)