from flask import Flask, render_template, request
import psycopg2
import os
import json

app = Flask(__name__)

# =========================
# DATABASE CONNECTION
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)


# =========================
# INIT DB
# =========================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            ref_id BIGSERIAL UNIQUE,
            ref_number TEXT,

            mobile TEXT,
            name TEXT,
            address TEXT,
            address1 TEXT,
            city TEXT,
            pincode TEXT,
            state TEXT,
            remarks TEXT,

            email TEXT,
            gstin TEXT,

            product TEXT,
            qty INTEGER,
            problem TEXT,
            serial TEXT,
            bill TEXT,
            date DATE,
            warranty TEXT,

            search_mobile TEXT,
            customer_type TEXT
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

    with open('states.json') as s:
        states = json.load(s)

    return render_template('form.html', products=products, states=states)


# =========================
# SUBMIT (MULTI PRODUCT)
# =========================
@app.route('/submit', methods=['POST'])
def submit():

    conn = get_conn()
    cur = conn.cursor()

    # ---------------- CUSTOMER DATA ----------------
    search_mobile = request.form.get('search_mobile')
    customer_type = request.form.get('customer_type')

    mobile = request.form['mobile']
    name = request.form['name'].upper()
    address = request.form['address'].upper()

    email = request.form.get('email')
    gstin = request.form.get('gstin')

    address1 = request.form.get('address1')
    city = request.form.get('city')
    pincode = request.form.get('pincode')
    state = request.form.get('state')
    remarks = request.form.get('remarks')

    # ---------------- MULTI PRODUCT DATA ----------------
    products = request.form.getlist('product[]')
    qtys = request.form.getlist('qty[]')
    problems = request.form.getlist('problem[]')
    serials = request.form.getlist('serial[]')
    bills = request.form.getlist('bill[]')
    dates = request.form.getlist('date[]')
    warranties = request.form.getlist('warranty[]')

    # ---------------- INSERT FIRST ROW TO GET ref_id ----------------
    cur.execute("""
        INSERT INTO customers
        (mobile, name, address, address1, city, pincode, state, remarks,
         email, gstin, product, qty, problem, serial, bill, date,
         warranty, search_mobile, customer_type)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING ref_id
    """, (
        mobile,
        name,
        address,
        address1,
        city,
        pincode,
        state,
        remarks,

        email,
        gstin,

        products[0],
        qtys[0],
        problems[0],
        serials[0],
        bills[0],
        dates[0],
        warranties[0],

        search_mobile,
        customer_type
    ))

    ref_id = cur.fetchone()[0]
    ref_number = f"REF-{ref_id}"

    # ---------------- UPDATE FIRST ROW ----------------
    cur.execute(
        "UPDATE customers SET ref_number=%s WHERE ref_id=%s",
        (ref_number, ref_id)
    )

    # ---------------- INSERT REMAINING PRODUCTS ----------------
    for i in range(1, len(products)):

        cur.execute("""
            INSERT INTO customers
            (ref_id, ref_number,
             mobile, name, address, address1, city, pincode, state, remarks,
             email, gstin,
             product, qty, problem, serial, bill, date, warranty,
             search_mobile, customer_type)
            VALUES (%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,
                    %s,%s,%s,%s,%s,%s,%s,
                    %s,%s)
        """, (
            ref_id,
            ref_number,

            mobile,
            name,
            address,
            address1,
            city,
            pincode,
            state,
            remarks,

            email,
            gstin,

            products[i],
            qtys[i],
            problems[i],
            serials[i],
            bills[i],
            dates[i],
            warranties[i],

            search_mobile,
            customer_type
        ))

    conn.commit()
    cur.close()
    conn.close()

    return f"✅ Submitted Successfully! Ref No: <b>{ref_number}</b>"


# =========================
# ADMIN PANEL
# =========================
@app.route('/admin')
def admin():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, ref_number, mobile, name, address, address1, city, pincode, state,
               remarks, email, gstin, product, qty, problem, serial, bill, date,
               warranty, search_mobile, customer_type
        FROM customers
        ORDER BY id DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    html = """
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial; background: #f5f5f5; padding:20px; }
            table { border-collapse: collapse; width: 100%; background: white; font-size: 13px; }
            th, td { border: 1px solid #ddd; padding: 6px; }
            th { background: #28a745; color: white; }
            tr:nth-child(even) { background: #f2f2f2; }
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
            <th>Addr1</th>
            <th>City</th>
            <th>Pincode</th>
            <th>State</th>
            <th>Remarks</th>
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


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True)
