from flask import Flask, render_template, request, redirect
import sqlite3
import uuid
import json

app = Flask(__name__)

# Create DB
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_number TEXT,
            mobile TEXT,
            name TEXT,
            address TEXT,
            email TEXT,
            gstin TEXT,
            product TEXT,
            qty INTEGER,
            problem TEXT,
            serial TEXT,
            bill TEXT,
            date DATE,
            warranty TEXT
            
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def form():
    with open('products.json') as f:
        products = json.load(f)

    return render_template('form.html', products=products)

@app.route('/submit', methods=['POST'])
def submit():
    ref_number = "REF-" + str(uuid.uuid4())[:8]

    mobile = request.form['mobile']
    name = request.form['name'].upper()
    address = request.form['address'].upper()
    email = request.form['email']
    gstin = request.form['gstin'].upper()
    product = request.form['product']
    qty = request.form['qty']
    problem = request.form['problem'].upper()
    serial = request.form['serial'].upper()
    bill = request.form['bill']
    date = request.form['date']
    warranty = request.form['warranty']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO customers 
        (ref_number, mobile, name, address, email, gstin, product, qty, problem, serial, bill, date, warranty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ref_number, mobile, name, address, email, gstin, product, qty, problem, serial, bill, date, warranty))

    conn.commit()
    conn.close()

    return f"✅ Submitted! Your Ref Number: <b>{ref_number}</b>"

@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    data = c.fetchall()
    conn.close()

    output = "<h2>Customer Entries</h2>"
    for row in data:
        output += f"<p>{row}</p>"

    return output

if __name__ == '__main__':
    app.run(debug=True)
