from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'pharmacy.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            medicines TEXT NOT NULL,
            total_price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")

# البديل لـ before_first_request
@app.before_request
def init_app():
    if not hasattr(app, 'db_initialized'):
        setup_database()
        app.db_initialized = True

@app.route('/order', methods=['POST'])
def place_order():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    medicines = data.get('medicines')
    total_price = data.get('total_price')

    conn = get_db_connection()
    conn.execute('INSERT INTO orders (name, phone, address, medicines, total_price) VALUES (?, ?, ?, ?, ?)',
                 (name, phone, address, medicines, total_price))
    conn.commit()
    conn.close()

    return jsonify({"message": "Order placed successfully!"}), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return jsonify([dict(order) for order in orders])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
