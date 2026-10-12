import os
import uuid
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, g
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')

DB = 'agenda.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS evidencias (
                id TEXT PRIMARY KEY,
                description TEXT,
                filename TEXT,
                original_name TEXT,
                date TEXT,
                project TEXT,
                problem_type TEXT,
                tags TEXT,
                cloud_provider TEXT DEFAULT 'local'
            )
        ''')
        conn.commit()

init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No se envió imagen"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"success": False, "error": "Nombre vacío"}), 400

        description = request.form.get('description', 'Sin descripción')
        problem_type = request.form.get('problem_type', 'General')
        project = request.form.get('project', 'Personal')
        tags = request.form.get('tags', '')

        ext = os.path.splitext(secure_filename(file.filename))[1]
        evidencia_id = str(uuid.uuid4())
        filename = f"{evidencia_id}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        date_now = datetime.now().isoformat()

        db = get_db()
        db.execute('INSERT INTO evidencias (id, description, filename, original_name, date, project, problem_type, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (evidencia_id, description, filename, file.filename, date_now, project, problem_type, tags))
        db.commit()

        return jsonify({"success": True, "id": evidencia_id, "filename": filename})

    except Exception as e:
        print(f"Error upload: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/search')
def search():
    try:
        query = request.args.get('query', '').strip().lower()
        db = get_db()
        if query:
            cur = db.execute('SELECT * FROM evidencias WHERE lower(description) LIKE ? OR lower(tags) LIKE ? OR lower(project) LIKE ? ORDER BY date DESC', (f'%{query}%', f'%{query}%', f'%{query}%'))
        else:
            cur = db.execute('SELECT * FROM evidencias ORDER BY date DESC')
        
        rows = cur.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "description": r["description"],
                "filename": r["filename"],
                "date": r["date"],
                "project": r["project"],
                "problem_type": r["problem_type"],
                "tags": r["tags"],
                "cloud_provider": r["cloud_provider"] or "local"
            })
        
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "results": []}), 500

@app.route('/image/<evidencia_id>')
def get_image(evidencia_id):
    try:
        db = get_db()
        cur = db.execute('SELECT filename FROM evidencias WHERE id = ?', (evidencia_id,))
        row = cur.fetchone()
        if not row:
            return "Not found", 404
        return send_from_directory(UPLOAD_FOLDER, row["filename"])
    except Exception as e:
        return str(e), 500

@app.route('/stats')
def stats():
    try:
        db = get_db()
        cur = db.execute('SELECT COUNT(*) as total FROM evidencias')
        total = cur.fetchone()["total"]
        cur = db.execute('SELECT project, COUNT(*) as count FROM evidencias GROUP BY project')
        by_project = {r["project"]: r["count"] for r in cur.fetchall()}
        cur = db.execute('SELECT problem_type, COUNT(*) as count FROM evidencias GROUP BY problem_type')
        by_type = {r["problem_type"]: r["count"] for r in cur.fetchall()}

        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "by_project": by_project,
                "by_type": by_type
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/evidence/<evidencia_id>', methods=['DELETE'])
def delete_evidence(evidencia_id):
    try:
        db = get_db()
        cur = db.execute('SELECT filename FROM evidencias WHERE id = ?', (evidencia_id,))
        row = cur.fetchone()
        if row:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, row["filename"]))
            except:
                pass
            db.execute('DELETE FROM evidencias WHERE id = ?', (evidencia_id,))
            db.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "No encontrada"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
