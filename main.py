
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3, os
from datetime import datetime

app = Flask(__name__, template_folder='plantillas')
DB = 'agenda.db'

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS entradas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descripcion TEXT,
        categoria TEXT,
        fecha TEXT,
        prioridad TEXT,
        hecho INTEGER DEFAULT 0,
        creado TEXT
    )''')
    con.commit()
    con.close()

init_db()

@app.route('/')
def index():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = request.args.get('q','')
    cat = request.args.get('cat','')
    sql = 'SELECT * FROM entradas WHERE 1=1'
    params=[]
    if q:
        sql += ' AND (titulo LIKE ? OR descripcion LIKE ?)'
        params.extend([f'%{q}%', f'%{q}%'])
    if cat:
        sql += ' AND categoria=?'
        params.append(cat)
    sql += ' ORDER BY hecho ASC, fecha DESC, id DESC'
    cur.execute(sql, params)
    entradas = cur.fetchall()
    con.close()
    return render_template('index.html', entradas=entradas, q=q, cat=cat)

@app.route('/agregar', methods=['POST'])
def agregar():
    data = request.form
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('INSERT INTO entradas (titulo, descripcion, categoria, fecha, prioridad, creado) VALUES (?,?,?,?,?,?)',
                (data['titulo'], data['descripcion'], data['categoria'], data['fecha'], data['prioridad'], datetime.now().isoformat()))
    con.commit()
    con.close()
    return redirect(url_for('index'))

@app.route('/toggle/<int:id>')
def toggle(id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('UPDATE entradas SET hecho = 1 - hecho WHERE id=?', (id,))
    con.commit()
    con.close()
    return redirect(url_for('index'))

@app.route('/borrar/<int:id>')
def borrar(id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('DELETE FROM entradas WHERE id=?', (id,))
    con.commit()
    con.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
