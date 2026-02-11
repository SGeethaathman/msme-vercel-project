# =====================================================
# IMPORT REQUIRED LIBRARIES
# =====================================================
import os                     # For file & folder operations
import psycopg2               # PostgreSQL connector
import uuid                   # For generating unique file names
from flask import Flask, request, send_file

# Create Flask application
app = Flask(__name__)


# =====================================================
# DATABASE CONFIGURATION
# =====================================================
# ⚠ Change password if needed
DB_CONFIG = {
    "host": "db",              # PostgreSQL server host
    "port": 5432,              # Default PostgreSQL port
    "database": "msme_db",     # Database name
    "user": "postgres",        # PostgreSQL username
    "password": "Moy31311"     # PostgreSQL password
}

# Folder to store uploaded certificate images
CERT_FOLDER = "certificate_uploads"

# Create folder if it doesn't exist
os.makedirs(CERT_FOLDER, exist_ok=True)


# =====================================================
# DATABASE CONNECTION FUNCTION
# =====================================================
def get_connection():
    """
    Creates and returns a new PostgreSQL connection
    """
    return psycopg2.connect(**DB_CONFIG)


# =====================================================
# DATABASE TABLE CREATION (RUNS ON STARTUP)
# =====================================================
def init_db():
    """
    Creates required tables if they do not exist
    """
    conn = get_connection()
    cur = conn.cursor()

    # -------------------------------
    # USERS TABLE
    # -------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        mobile_number VARCHAR(20) NOT NULL,
        role VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -------------------------------
    # MSME VERIFICATION TABLE
    # -------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS msme_verification (
        verification_id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(user_id),
        udyam_number VARCHAR(100) UNIQUE,
        certificate_path TEXT,
        status VARCHAR(50) DEFAULT 'Pending',
        verified_at TIMESTAMP
    )
    """)

    # -------------------------------
    # BUSINESS PROFILES TABLE
    # -------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS business_profiles (
        business_id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(user_id),
        company_name VARCHAR(150),
        business_type VARCHAR(100),
        years_of_operation INTEGER,
        annual_turnover NUMERIC,
        state VARCHAR(100),
        city VARCHAR(100)
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


# Initialize DB when app starts
init_db()


# =====================================================
# HOME PAGE
# =====================================================
@app.route("/")
def home():
    """
    Displays navigation links
    """
    return """
    <h2>MSME Management System</h2>

    <h3>Users</h3>
    <a href="/add_user_form">Add User</a> |
    <a href="/view_users">View Users</a><br><br>

    <h3>MSME Verification</h3>
    <a href="/add_msme_form">Add MSME</a> |
    <a href="/view_msme">View MSME</a><br><br>

    <h3>Business</h3>
    <a href="/add_business_form">Add Business</a> |
    <a href="/view_business">View Business</a>
    """


# =====================================================
# USERS MODULE
# =====================================================

# Show user form
@app.route("/add_user_form")
def add_user_form():
    return """
    <h2>Add User</h2>
    <form method="POST" action="/add_user">
        Name:<br><input name="full_name" required><br><br>
        Email:<br><input name="email" required><br><br>
        Mobile:<br><input name="mobile" required><br><br>

        Role:<br>
        <select name="role" required>
            <option value="">Select Role</option>
            <option>Cashier</option>
            <option>Sales Associates</option>
            <option>Store Managers</option>
        </select><br><br>

        <button type="submit">Save</button>
    </form>
    """


# Insert new user into database
@app.route("/add_user", methods=["POST"])
def add_user():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (full_name,email,mobile_number,role)
        VALUES (%s,%s,%s,%s)
    """, (
        request.form["full_name"],
        request.form["email"],
        request.form["mobile"],
        request.form["role"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return "<h3>User Added Successfully</h3><a href='/'>Home</a>"


# Display all users
@app.route("/view_users")
def view_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY user_id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    html = """
    <h2>Users Table</h2>
    <table border="1" cellpadding="10">
    <tr>
        <th>ID</th><th>Name</th><th>Email</th>
        <th>Mobile</th><th>Role</th><th>Created</th>
    </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td>{r[4]}</td>
            <td>{r[5]}</td>
        </tr>
        """

    html += "</table><br><a href='/'>Home</a>"
    return html


# =====================================================
# MSME MODULE
# =====================================================

# MSME Form
@app.route("/add_msme_form")
def add_msme_form():
    return """
    <h2>Add MSME Verification</h2>
    <form method="POST" action="/add_msme" enctype="multipart/form-data">
        User ID:<br><input name="user_id" required><br><br>
        Udyam Number:<br><input name="udyam" required><br><br>
        Certificate Image:<br><input type="file" name="certificate" required><br><br>
        Status:<br><input name="status" required><br><br>
        <button type="submit">Save</button>
    </form>
    """


# Insert MSME record
@app.route("/add_msme", methods=["POST"])
def add_msme():
    file = request.files["certificate"]

    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = str(uuid.uuid4()) + ext
    save_path = os.path.join(CERT_FOLDER, filename)

    # Save certificate image locally
    file.save(save_path)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO msme_verification
        (user_id,udyam_number,certificate_path,status)
        VALUES (%s,%s,%s,%s)
    """, (
        request.form["user_id"],
        request.form["udyam"],
        save_path,
        request.form["status"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return "<h3>MSME Record Added</h3><a href='/'>Home</a>"


# View MSME records
@app.route("/view_msme")
def view_msme():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM msme_verification ORDER BY verification_id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    html = """
    <h2>MSME Records</h2>
    <table border="1" cellpadding="10">
    <tr>
        <th>ID</th><th>User ID</th><th>Udyam</th>
        <th>Certificate</th><th>Status</th><th>Verified At</th>
    </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td><img src="/certificate/{r[0]}" width="120"></td>
            <td>{r[4]}</td>
            <td>{r[5]}</td>
        </tr>
        """

    html += "</table><br><a href='/'>Home</a>"
    return html


# Serve certificate image
@app.route("/certificate/<int:id>")
def certificate(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT certificate_path FROM msme_verification WHERE verification_id=%s",
        (id,)
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    if row and os.path.exists(row[0]):
        return send_file(row[0])

    return "Image Not Found"


# =====================================================
# BUSINESS MODULE
# =====================================================

@app.route("/add_business_form")
def add_business_form():
    return """
    <h2>Add Business</h2>
    <form method="POST" action="/add_business">
        User ID:<br><input name="user_id" required><br><br>
        Company Name:<br><input name="company" required><br><br>

        Company Type:<br>
        <select name="type" required>
            <option>Clothing</option>
            <option>FMCG</option>
            <option>Electronics</option>
            <option>Super Market</option>
        </select><br><br>

        Years:<br><input name="years" type="number"><br><br>
        Turnover:<br><input name="turnover" type="number" step="0.01"><br><br>

        State:<br>
        <select name="state" required>
            <option>Andhra Pradesh</option>
            <option>Karnataka</option>
            <option>Kerala</option>
            <option>Tamil Nadu</option>
            <option>Telangana</option>
        </select><br><br>

        City:<br><input name="city"><br><br>
        <button type="submit">Save</button>
    </form>
    """


@app.route("/add_business", methods=["POST"])
def add_business():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO business_profiles
        (user_id,company_name,business_type,
         years_of_operation,annual_turnover,state,city)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        request.form["user_id"],
        request.form["company"],
        request.form["type"],
        request.form["years"],
        request.form["turnover"],
        request.form["state"],
        request.form["city"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return "<h3>Business Added</h3><a href='/'>Home</a>"


@app.route("/view_business")
def view_business():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM business_profiles ORDER BY business_id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    html = """
    <h2>Business Profiles</h2>
    <table border="1" cellpadding="10">
    <tr>
        <th>ID</th><th>User ID</th><th>Company</th>
        <th>Type</th><th>Years</th><th>Turnover</th>
        <th>State</th><th>City</th>
    </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td>{r[4]}</td>
            <td>{r[5]}</td>
            <td>{r[6]}</td>
            <td>{r[7]}</td>
        </tr>
        """

    html += "</table><br><a href='/'>Home</a>"
    return html


# =====================================================
# RUN APPLICATION
# =====================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

