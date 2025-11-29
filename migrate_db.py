import sqlite3

def migrate_database():
    """Ajoute la colonne 'role' à la table users si elle n'existe pas"""
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    try:
        # Vérifier si la colonne role existe déjà
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'role' not in columns:
            print("Ajout de la colonne 'role' à la table users...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            conn.commit()
            print("✅ Colonne 'role' ajoutée avec succès!")
            
            # Créer un utilisateur admin par défaut si aucun admin n'existe
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                print("\nCréation d'un compte administrateur par défaut...")
                cursor.execute("""
                    INSERT INTO users (username, password, role) 
                    VALUES ('admin', 'admin123', 'admin')
                """)
                conn.commit()
                print("✅ Compte admin créé!")
                print("   Username: admin")
                print("   Password: admin123")
                print("   ⚠️  Changez ce mot de passe en production!")
        else:
            print("✓ La colonne 'role' existe déjà.")
            
    except sqlite3.Error as e:
        print(f"❌ Erreur lors de la migration: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
