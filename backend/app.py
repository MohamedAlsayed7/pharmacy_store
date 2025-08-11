from flask import Flask, request, jsonify, send_from_directory, g
import sqlite3, os, json, datetime
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'orders.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, address TEXT, items_json TEXT, created_at TEXT, status TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT)''')
    cur = db.execute('SELECT COUNT(*) as c FROM admin').fetchone()
    if cur['c']==0:
        from os import getenv
        pwd = getenv('ADMIN_PASSWORD', 'admin123')
        db.execute('INSERT INTO admin (id, username, password_hash) VALUES (1, ?, ?)', ('admin', generate_password_hash(pwd)))
    db.commit()

def check_auth(username, password):
    db = get_db()
    row = db.execute('SELECT * FROM admin WHERE username=?', (username,)).fetchone()
    if row:
        return check_password_hash(row['password_hash'], password)
    return False

def authenticate():
    return jsonify({'message':'Authentication required'}), 401

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')

@app.before_first_request
def setup():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    init_db()

@app.route('/backend/api/orders', methods=['POST'])
def create_order():
    data = request.get_json(force=True)
    name = data.get('name','')
    phone = data.get('phone','')
    address = data.get('address','')
    items = data.get('items',[])
    if not items:
        return jsonify({'message':'No items provided'}), 400
    db = get_db()
    db.execute('INSERT INTO orders (name,phone,address,items_json,created_at,status) VALUES (?,?,?,?,?,?)',
               (name, phone, address, json.dumps(items, ensure_ascii=False), datetime.datetime.utcnow().isoformat(), 'new'))
    db.commit()
    return jsonify({'message':'Order received'}), 201

@app.route('/backend/admin')
@requires_auth
def admin_panel():
    db = get_db()
    rows = db.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    orders = []
    for r in rows:
        orders.append({'id':r['id'],'name':r['name'],'phone':r['phone'],'address':r['address'],'items':json.loads(r['items_json']),'created_at':r['created_at'],'status':r['status']})
    html = '<h1>Admin — Orders</h1><p><a href="/">Go to Store</a></p><table border="1" cellpadding="6"><tr><th>ID</th><th>Name</th><th>Phone</th><th>Address</th><th>Items</th><th>Created</th><th>Status</th></tr>'
    for o in orders:
        html += f"<tr><td>{o['id']}</td><td>{o['name']}</td><td>{o['phone']}</td><td>{o['address']}</td><td>{len(o['items'])} items</td><td>{o['created_at']}</td><td>{o['status']}</td></tr>"
    html += '</table>'
    return html

@app.route('/backend/orders_csv')
@requires_auth
def orders_csv():
    db = get_db()
    rows = db.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    import csv, io
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','name','phone','address','items_json','created_at','status'])
    for r in rows:
        cw.writerow([r['id'],r['name'],r['phone'],r['address'],r['items_json'],r['created_at'],r['status']])
    return si.getvalue(), 200, {'Content-Type':'text/csv','Content-Disposition':'attachment; filename="orders.csv"'}

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/static/<path:p>')
def static_files(p):
    return send_from_directory('../frontend/static', p)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
