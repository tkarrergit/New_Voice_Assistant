import sqlite3

def fetch_data_from_table(db_name, table_name):
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # SQL-Abfrage, um alle Daten aus der Tabelle zu holen
    query = f"SELECT * FROM {table_name}"
    
    try:
        # Daten aus der Tabelle abrufen
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Ausgabe der Daten
        for row in rows:
            print(row)
    
    except sqlite3.Error as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
    
    finally:
        # Verbindung schließen
        conn.close()

# Beispielaufruf der Funktion
fetch_data_from_table('db.sqlite3', 'ChatEditor')