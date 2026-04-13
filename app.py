from flask import Flask, render_template, request
import psycopg2
import os
import uuid
import json

app = Flask(__name__)

# =========================
# DATABASE CONNECTION
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# =========================
# CREATE TABLE (RUN ON START)
# =========================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
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
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()

# =========================
# FORM PAGE
# =========================
@app.route('/')
def form():
    with open('products.json') as f:
        products = json.load(f)

    return render_template('form.html', products=products)

# =========================
# SUBMIT DATA
# =========================
@app.route('/submit', methods=['POST'])
def submit():
    ref_number = "REF-" + str(uuid.uuid4())[:8]
    
    search_mobile = request.form.get('search_mobile')
    customer_type = request.form.get('customer_type')
    mobile = request.form['mobile']
    name = request.form['name'].upper()
    address = request.form['address'].upper()
    email = request.form['email']
    gstin = request.form['gstin'].upper()
    product = request.form['product']
    qty = int(request.form['qty'])
    problem = request.form['problem'].upper()
    serial = request.form['serial'].upper()
    bill = request.form['bill']
    date = request.form['date']
    warranty = request.form['warranty']

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO customers
        (ref_number, mobile, name, address, email, gstin,
         product, qty, problem, serial, bill, date, warranty,search_mobile,customer_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        ref_number, mobile, name, address, email, gstin,
        product, qty, problem, serial, bill, date, warranty, search_mobile, customer_type
    ))

    conn.commit()
    cur.close()
    conn.close()

    return f"✅ Submitted! Your Ref Number: <b>{ref_number}</b>"

# =========================
# ADMIN PANEL
# =========================
@app.route('/admin')
def admin():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM customers ORDER BY id DESC")
    data = cur.fetchall()

    cur.close()
    conn.close()

    html = """
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial; background: #f5f5f5; padding:20px; }
            h2 { text-align:center; }

            table {
                border-collapse: collapse;
                width: 100%;
                background: white;
                font-size: 14px;
            }

            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }

            th {
                background: #28a745;
                color: white;
            }

            tr:nth-child(even) { background: #f2f2f2; }
            tr:hover { background: #ddd; }
        </style>
    </head>
    <body>
    <h2>Product Complaint Report</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Ref No</th>
            <th>Mobile</th>
            <th>Name</th>
            <th>Address</th>
            <th>Email</th>
            <th>GSTIN</th>
            <th>Product</th>
            <th>Qty</th>
            <th>Problem</th>
            <th>Serial</th>
            <th>Bill</th>
            <th>Date</th>
            <th>Warranty</th>
            <th>Search Mobile</th>
            <th>Customer Type</th>
        </tr>
    """

    for row in data:
        html += "<tr>"
        for col in row:
            html += f"<td>{col}</td>"
        html += "</tr>"

    html += "</table></body></html>"

    return html


if __name__ == '__main__':
    app.run(debug=True)
