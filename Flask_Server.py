from flask import Flask, render_template, request, jsonify
import hugchat_function_new as hfn
import requests 
import sqlite3

#Testzugang
email="huggchat@proton.me"
passwd = "Huggchat55%"
new_conversation, chatbot = hfn.hugchat_initialize_no_assistant(email, passwd)

app = Flask(__name__)

 
# Globale Variablen für Eingaben
input_text = ""
input_sprache = ""

@app.route("/control", methods=["POST"])
def control():
    command = request.json.get("command")
    return jsonify({"command": command})

def send_command(command):
    # Server-URL
    url = "http://127.0.0.1:5000/control"
    
    # Überprüfen, ob der übergebene Befehl gültig ist
    valid_commands = ["play", "pause", "reset"]
    
    if command not in valid_commands:
        print(f"Ungültiger Befehl: {command}. Gültige Befehle sind: {', '.join(valid_commands)}")
        return
    
    # Senden des Befehls an den Flask-Server
    response = requests.post(url, json={"command": command})
    
    if response.ok:
        print(f"Befehl '{command}' erfolgreich gesendet.")
    else:
        print(f"Fehler beim Senden des Befehls '{command}': {response.status_code}")


def process_text_or_speech(content, input_type):
    """Verarbeitet den eingegebenen Text oder die Sprache."""
    if input_type == "text":
        result = f"Verarbeiteter Text: {content.upper()}"  # Beispielverarbeitung: Text in Großbuchstaben
    elif input_type == "speech":
        result = f"Verarbeitete Sprache: {content[::-1]}"  # Beispielverarbeitung: Text umkehren
    else:
        result = "Ungültiger Typ"
    return result

@app.route("/")
def index():
    """Rendert die Hauptseite."""
    return render_template("index.html")

@app.route("/settings")
def settings():
    """Zeigt die Einstellungsseite an."""
    return render_template("settings.html")

@app.route("/chat-editor")
def chat_editor():
    """Zeigt den Chat-Editor an."""
    return render_template("chat_editor.html", schema=DB_SCHEMA)

@app.route("/app-editor")
def app_editor():
    """Zeigt den App-Editor an."""
    return "App Editor Seite"

@app.route("/tapo-editor")
def tapo_editor():
    """Zeigt den Tapo-Editor an."""
    return "Tapo Editor Seite"


# Definition der Spalten (Schema der Datenbank)
DB_SCHEMA = {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "Wort": "TEXT NOT NULL",
    "und_Wort": "TEXT NOT NULL",
    "persona": "TEXT NOT NULL",
    "prompt": "TEXT NOT NULL"
}

# Datenbank initialisieren
# Datenbank initialisieren
def init_db():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Tabelle erstellen basierend auf DB_SCHEMA
    columns = ", ".join([f"{col} {definition}" for col, definition in DB_SCHEMA.items()])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS entries ({columns})")
    conn.commit()
    conn.close()


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
        print(f"Deleting entry with id: {entry_id}")
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        print(f"Rows affected: {conn.total_changes}")
        conn.close()
        return jsonify({"message": "Entry deleted successfully"}), 200


    cursor.execute(f"SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    print(row)
    conn.close()
    if row:
        return jsonify(row), 200
    return jsonify({"message": "Entry not found"}), 404

@app.route("/process", methods=["POST"])
def process():
    """Verarbeitet die Eingaben vom Frontend."""
    global input_text, input_sprache  # Globale Variablen für Weiterverarbeitung

    data = request.json
    input_type = data.get("type")  # "text" oder "speech"
    content = data.get("content")  # Der eigentliche Text/Sprache

    if not content:
        return jsonify({"status": "error", "message": "Kein Inhalt übermittelt"}), 400

    # Speichere Eingabe in den entsprechenden Variablen
    if input_type == "text":
        input_text = content
        antwort = hfn.hugchat_assistent(chatbot, input_text, new_conversation)
        result = str(antwort)
        send_command("play")  # Video abspielen
        return jsonify({
            "status": "success",
            "type": "text",
            "processed": result,
            "message": f"Text '{input_text}' wurde verarbeitet!",
            "play_video": True  # Signal zum Starten des Videos
        })

    elif input_type == "speech":
        input_sprache = content
        antwort = hfn.hugchat_assistent(chatbot, input_sprache, new_conversation)
        result = str(antwort)
        send_command("play")  # Video abspielen
        return jsonify({
            "status": "success",
            "type": "speech",
            "processed": result,
            "message": f"Sprache '{input_sprache}' wurde verarbeitet!",
            "play_video": True  # Signal zum Starten des Videos
        })

    else:
        return jsonify({"status": "error", "message": "Ungültiger Typ"}), 400


if __name__ == "__main__":
    init_db() 

    # Starte Flask
    
    app.run(host='0.0.0.0', port=5000, debug=True)

