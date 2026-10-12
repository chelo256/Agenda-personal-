import os
import uuid
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_from_directory, g, session, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import psycopg2
    import psycopg2.extras
    HAS_PG = True
except:
    HAS_PG = False

try:
    import cloudinary
    import cloudinary.uploader
    HAS_CLOUDINARY = True
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )
except:
    HAS_CLOUDINARY = False

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-cambia-esto-en-produccion-123456789')

DB_URL = os.getenv('DATABASE_URL')
SQLITE_DB = 'agenda.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USE_PG = bool(DB_URL and HAS_PG)
USE_CLOUDINARY = bool(HAS_CLOUDINARY and os.getenv('CLOUDINARY_CLOUD_NAME'))

def get_db():
    if USE_PG:
        if not hasattr(g, '_pg_conn'):
            g._pg_conn = psycopg2.connect(DB_URL)
        return g._pg_conn
    else:
        db = getattr(g, '_sqlite', None)
        if db is None:
            db = g._sqlite = sqlite3.connect(SQLITE_DB)
            db.row_factory = sqlite3.Row
        return db

def init_db():
    if USE_PG:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS evidencias (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id),
                description TEXT,
                filename TEXT,
                original_name TEXT,
                date TEXT,
                project TEXT,
                problem_type TEXT,
                tags TEXT,
                cloud_provider TEXT,
                cloud_url TEXT
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
    else:
        with sqlite3.connect(SQLITE_DB) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS evidencias (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    description TEXT,
                    filename TEXT,
                    original_name TEXT,
                    date TEXT,
                    project TEXT,
                    problem_type TEXT,
                    tags TEXT,
                    cloud_provider TEXT DEFAULT 'local',
                    cloud_url TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            # Migraciones suaves
            try:
                conn.execute('ALTER TABLE evidencias ADD COLUMN user_id TEXT')
            except:
                pass
            try:
                conn.execute('ALTER TABLE evidencias ADD COLUMN cloud_url TEXT')
            except:
                pass
            conn.commit()

init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_sqlite', None)
    if db is not None:
        db.close()
    pg = getattr(g, '_pg_conn', None)
    if pg is not None:
        try:
            pg.close()
        except:
            pass

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip().lower()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        password2 = request.form.get('password2','')

        if not username or not email or not password:
            return render_template('register.html', error="Completa todos los campos")
        if password != password2:
            return render_template('register.html', error="Las contraseñas no coinciden")
        if len(password) < 6:
            return render_template('register.html', error="La contraseña debe tener al menos 6 caracteres")

        # Verificar si existe
        if USE_PG:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT id FROM users WHERE username=%s OR email=%s', (username, email))
            if cur.fetchone():
                return render_template('register.html', error="Usuario o correo ya existe")
            user_id = str(uuid.uuid4())
            pwd_hash = generate_password_hash(password)
            cur.execute('INSERT INTO users (id, username, email, password_hash, created_at) VALUES (%s,%s,%s,%s,%s)',
                        (user_id, username, email, pwd_hash, datetime.now().isoformat()))
            conn.commit()
        else:
            db = get_db()
            cur = db.execute('SELECT id FROM users WHERE username=? OR email=?', (username, email))
            if cur.fetchone():
                return render_template('register.html', error="Usuario o correo ya existe")
            user_id = str(uuid.uuid4())
            pwd_hash = generate_password_hash(password)
            db.execute('INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?,?,?,?,?)',
                       (user_id, username, email, pwd_hash, datetime.now().isoformat()))
            db.commit()

        return render_template('login.html', ok="Cuenta creada! Ahora inicia sesión")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('username','').strip().lower()
        password = request.form.get('password','')

        if USE_PG:
            conn = get_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute('SELECT * FROM users WHERE username=%s OR email=%s', (login_input, login_input))
            user = cur.fetchone()
        else:
            db = get_db()
            cur = db.execute('SELECT * FROM users WHERE username=? OR email=?', (login_input, login_input))
            user = cur.fetchone()

        if not user:
            return render_template('login.html', error="Usuario no encontrado")

        pwd_hash = user['password_hash'] if isinstance(user, dict) else user['password_hash']
        if not check_password_hash(pwd_hash, password):
            return render_template('login.html', error="Contraseña incorrecta")

        session['user_id'] = user['id'] if isinstance(user, dict) else user['id']
        session['username'] = user['username'] if isinstance(user, dict) else user['username']
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
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

        evidencia_id = str(uuid.uuid4())
        original_name = secure_filename(file.filename)
        date_now = datetime.now().isoformat()
        cloud_url = None
        final_filename = ""
        cloud_provider = "local"

        if USE_CLOUDINARY:
            try:
                upload_res = cloudinary.uploader.upload(file, public_id=f"agenda/{evidencia_id}", folder="agenda_personal")
                cloud_url = upload_res.get('secure_url')
                final_filename = upload_res.get('public_id')
                cloud_provider = "cloudinary"
            except Exception as e:
                print(f"Cloudinary fallo: {e}")
                ext = os.path.splitext(original_name)[1]
                final_filename = f"{evidencia_id}{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, final_filename)
                file.seek(0)
                file.save(filepath)
        else:
            ext = os.path.splitext(original_name)[1]
            final_filename = f"{evidencia_id}{ext}"
            filepath = os.path.join(UPLOAD_FOLDER, final_filename)
            file.save(filepath)

        user_id = session.get('user_id')

        if USE_PG:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO evidencias (id, user_id, description, filename, original_name, date, project, problem_type, tags, cloud_provider, cloud_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (evidencia_id, user_id, description, final_filename, original_name, date_now, project, problem_type, tags, cloud_provider, cloud_url))
            conn.commit()
        else:
            db = get_db()
            db.execute('INSERT INTO evidencias (id, user_id, description, filename, original_name, date, project, problem_type, tags, cloud_provider, cloud_url) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                       (evidencia_id, user_id, description, final_filename, original_name, date_now, project, problem_type, tags, cloud_provider, cloud_url))
            db.commit()

        return jsonify({"success": True, "id": evidencia_id})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/search')
@login_required
def search():
    try:
        query = request.args.get('query', '').strip().lower()
        user_id = session.get('user_id')
        if USE_PG:
            conn = get_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            if query:
                cur.execute('SELECT * FROM evidencias WHERE user_id=%s AND (LOWER(description) LIKE %s OR LOWER(tags) LIKE %s OR LOWER(project) LIKE %s) ORDER BY date DESC', (user_id, f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                cur.execute('SELECT * FROM evidencias WHERE user_id=%s ORDER BY date DESC', (user_id,))
            rows = cur.fetchall()
            results = [{"id": r["id"], "description": r["description"], "filename": r["filename"], "date": r["date"], "project": r["project"], "problem_type": r["problem_type"], "tags": r["tags"], "cloud_provider": r["cloud_provider"] or "local", "cloud_url": r.get("cloud_url")} for r in rows]
            return jsonify({"success": True, "results": results})
        else:
            db = get_db()
            if query:
                cur = db.execute('SELECT * FROM evidencias WHERE user_id=? AND (lower(description) LIKE ? OR lower(tags) LIKE ? OR lower(project) LIKE ?) ORDER BY date DESC', (user_id, f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                cur = db.execute('SELECT * FROM evidencias WHERE user_id=? ORDER BY date DESC', (user_id,))
            results = [{"id": r["id"], "description": r["description"], "filename": r["filename"], "date": r["date"], "project": r["project"], "problem_type": r["problem_type"], "tags": r["tags"], "cloud_provider": r["cloud_provider"] or "local", "cloud_url": r["cloud_url"] if "cloud_url" in r.keys() else None} for r in cur.fetchall()]
            return jsonify({"success": True, "results": results})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"success": False, "error": str(e), "results": []}), 500

@app.route('/image/<evidencia_id>')
@login_required
def get_image(evidencia_id):
    try:
        user_id = session.get('user_id')
        if USE_PG:
            conn = get_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute('SELECT filename, cloud_url FROM evidencias WHERE id = %s AND user_id=%s', (evidencia_id, user_id))
            row = cur.fetchone()
        else:
            db = get_db()
            row = db.execute('SELECT filename, cloud_url FROM evidencias WHERE id = ? AND user_id=?', (evidencia_id, user_id)).fetchone()
        if not row:
            return "Not found", 404
        cloud_url = row["cloud_url"] if isinstance(row, dict) else (row["cloud_url"] if "cloud_url" in row.keys() else None)
        filename = row["filename"] if isinstance(row, dict) else row["filename"]
        if cloud_url:
            from flask import redirect
            return redirect(cloud_url)
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return str(e), 500

@app.route('/stats')
@login_required
def stats():
    try:
        user_id = session.get('user_id')
        if USE_PG:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM evidencias WHERE user_id=%s', (user_id,))
            total = cur.fetchone()[0]
        else:
            db = get_db()
            total = db.execute('SELECT COUNT(*) as total FROM evidencias WHERE user_id=?', (user_id,)).fetchone()["total"]
        return jsonify({"success": True, "stats": {"total": total, "storage": "cloudinary+postgres" if (USE_PG and USE_CLOUDINARY) else "local+sqlite", "user": session.get('username')}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/evidence/<evidencia_id>', methods=['DELETE'])
@login_required
def delete_evidence(evidencia_id):
    try:
        user_id = session.get('user_id')
        if USE_PG:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT filename, cloud_provider FROM evidencias WHERE id = %s AND user_id=%s', (evidencia_id, user_id))
            row = cur.fetchone()
            if row and row[1] == 'cloudinary' and USE_CLOUDINARY:
                try:
                    cloudinary.uploader.destroy(f"agenda/{evidencia_id}")
                except:
                    pass
            cur.execute('DELETE FROM evidencias WHERE id = %s AND user_id=%s', (evidencia_id, user_id))
            conn.commit()
            return jsonify({"success": True})
        else:
            db = get_db()
            row = db.execute('SELECT filename FROM evidencias WHERE id = ? AND user_id=?', (evidencia_id, user_id)).fetchone()
            if row:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, row["filename"]))
                except:
                    pass
                db.execute('DELETE FROM evidencias WHERE id = ? AND user_id=?', (evidencia_id, user_id))
                db.commit()
                return jsonify({"success": True})
        return jsonify({"success": False, "error": "No encontrada"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
