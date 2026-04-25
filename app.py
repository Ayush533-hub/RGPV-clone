from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # allow frontend to connect

DB_NAME = "data.db"

# ---------- Serve HTML Files ----------
@app.route('/')
def index():
    return send_file('index.html')

@app.route('/<filename>')
def serve_html(filename):
    if filename.endswith('.html') or filename.endswith('.css') or filename.endswith('.js'):
        if os.path.exists(filename):
            return send_file(filename)
    return "<h2>File not found</h2>", 404

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS marksheets (
                    enrollment TEXT PRIMARY KEY,
                    data TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------- Save Marksheet ----------
@app.route("/save", methods=["POST"])
def save_marksheet():
    data = request.json
    enrollment = data.get("enrollment")
    content = data.get("data")

    if not enrollment or not content:
        return jsonify({"success": False, "message": "Missing enrollment or data"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO marksheets (enrollment, data) VALUES (?, ?)", (enrollment, content))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Marksheet saved successfully!"})

# ---------- Check Enrollment ----------
@app.route("/check")
def check_enrollment():
    enrollment = request.args.get("enrollment")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT data FROM marksheets WHERE enrollment=?", (enrollment,))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({"exists": True, "data": row[0]})
    else:
        return jsonify({"exists": False})

# ---------- Serve Saved Marksheet ----------
@app.route("/marksheet/<enrollment>")
def show_marksheet(enrollment):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT data FROM marksheets WHERE enrollment=?", (enrollment,))
    row = c.fetchone()
    conn.close()

    if row:
        return Response(row[0], mimetype="text/html")  # return saved HTML properly
    else:
        return "<h2>No record found</h2>"

if __name__ == "__main__":
    app.run(debug=True)
