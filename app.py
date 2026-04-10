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
            name TEXT,
            phone TEXT,
            product TEXT,
            issue TEXT
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
    name = request.form['name']
    phone = request.form['phone']
    product = request.form['product']
    issue = request.form['issue']

    ref_number = "REF-" + str(uuid.uuid4())[:8]

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO customers (ref_number, name, phone, product, issue) VALUES (?, ?, ?, ?, ?)",
              (ref_number, name, phone, product, issue))
    conn.commit()
    conn.close()

    return f"✅ Submitted successfully! Your Reference Number: <b>{ref_number}</b>"

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
