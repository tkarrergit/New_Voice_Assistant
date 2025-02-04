from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Definition der Spalten (Schema der Datenbank)
DB_SCHEMA = {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "persona": "TEXT NOT NULL",
    "Beispiel": "TEXT NOT NULL",
    "prompt": "TEXT NOT NULL"
}

# Datenbank initialisieren
def init_db():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Tabelle erstellen basierend auf DB_SCHEMA
    columns = ", ".join([f"{col} {definition}" for col, definition in DB_SCHEMA.items()])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS entries ({columns})")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("chat_editor.html", schema=DB_SCHEMA)

@app.route("/api/entries", methods=["GET", "POST"])
def manage_entries():
    if request.method == "POST":
        data = request.json
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()

        # Dynamische Einfügeoperation basierend auf DB_SCHEMA
        columns = ", ".join(DB_SCHEMA.keys())
        placeholders = ", ".join(["?"] * len(DB_SCHEMA))
        values = [data[col] for col in DB_SCHEMA.keys()]
        cursor.execute(f"INSERT OR REPLACE INTO entries ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        return jsonify({"message": "Entry saved successfully"}), 201

    # GET: Alle Daten laden
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM entries")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows), 200

@app.route("/api/entry/<int:entry_id>", methods=["GET", "DELETE"])
def manage_entry(entry_id):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    if request.method == "DELETE":
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Entry deleted successfully"}), 200

    cursor.execute(f"SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    print(row)
    conn.close()
    if row:
        return jsonify(row), 200
    return jsonify({"message": "Entry not found"}), 404

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)


"""
# Beispiel für Tabellen und Schemata
DB_SCHEMAS = {
    "Chat_Editor": {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "persona": "TEXT NOT NULL",
        "Beispiel": "TEXT NOT NULL",
        "prompt": "TEXT NOT NULL"
    },
    "App_Editor": {
        "id": "INTEGER PRIMARY KEY",
        "name2": "TEXT NOT NULL",
        "App_name": "TEXT NOT NULL",
        "Beispiel2": "TEXT NOT NULL",
        "prompt2": "TEXT NOT NULL"
    },
    "Tapo_Editor": {
        "id": "INTEGER PRIMARY KEY",
        "name3": "TEXT NOT NULL",
        "Tapo_lampe": "TEXT NOT NULL",
        "Beispiel3": "TEXT NOT NULL",
        "prompt3": "TEXT NOT NULL"
    }
}

@app.route("/api/entries/<table_name>", methods=["GET", "POST"])
def manage_entries(table_name):
    if table_name not in DB_SCHEMAS:
        return jsonify({"error": f"Unknown table: {table_name}"}), 400

    schema = DB_SCHEMAS[table_name]

    if request.method == "POST":
        data = request.json
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()

        # Dynamische Einfügeoperation basierend auf dem Schema
        columns = ", ".join(schema.keys())
        placeholders = ", ".join(["?"] * len(schema))
        values = [data.get(col) for col in schema.keys()]

        try:
            cursor.execute(
                f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})",
                values
            )
            conn.commit()
        except Exception as e:
            conn.close()
            return jsonify({"error": str(e)}), 500

        conn.close()
        return jsonify({"message": f"Entry saved successfully in {table_name}"}), 201

    # GET: Alle Daten aus der angegebenen Tabelle laden
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

    conn.close()
    return jsonify(rows), 200
"""

"""
# Definition der Spalten (Schema der Datenbank)
DB_SCHEMA = [{
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "persona": "TEXT NOT NULL",
    "Beispiel": "TEXT NOT NULL",
    "prompt": "TEXT NOT NULL"
},{
    "id": "INTEGER PRIMARY KEY",
    "name2": "TEXT NOT NULL",
    "App_name": "TEXT NOT NULL",
    "Beispiel2": "TEXT NOT NULL",
    "prompt2": "TEXT NOT NULL"
},{
    "id": "INTEGER PRIMARY KEY",
    "name3": "TEXT NOT NULL",
    "Tapo_lampe": "TEXT NOT NULL",
    "Beispiel3": "TEXT NOT NULL",
    "prompt3": "TEXT NOT NULL"
}]

db_table_names = ["Chat_Editor", "App_Editor", "Tapo_Editor"]

# Datenbank initialisieren
def init_db(table_names, schemas):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    
    for table, schema in zip(table_names, schemas):
        # Tabelle erstellen basierend auf Schema
        columns = ", ".join([f"{col} {definition}" for col, definition in schema.items()])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns})")
        print(f"Tabelle '{table}' mit Schema erstellt: {columns}")
    
    conn.commit()
    conn.close()





"""