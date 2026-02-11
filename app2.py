import os  # For folder and file operations
import sqlite3  # For SQLite database connection
import uuid  # For generating unique file names
from flask import Flask, request, render_template_string, send_file  # Flask modules

app = Flask(__name__)  # Create Flask app

# ================================
# PATH SETTINGS
# ================================
BASE_FOLDER = r"C:\Users\S.Geethaathman\Desktop\DataNetra"  # Base project folder
DB_NAME = os.path.join(BASE_FOLDER, "msme_system.db")  # Database file path
CERT_FOLDER = os.path.join(BASE_FOLDER, "certificate_uploads")  # Certificate image folder

os.makedirs(BASE_FOLDER, exist_ok=True)  # Create base folder if not exists
os.makedirs(CERT_FOLDER, exist_ok=True)  # Create certificate folder if not exists

# ================================
# DATABASE INIT
# ================================
def init_db():
    with sqlite3.connect(DB_NAME) as conn:  # Connect to database
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        cursor = conn.cursor()  # Create cursor object

        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile_number TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create MSME verification table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS msme_verification (
            verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            udyam_number TEXT UNIQUE,
            certificate_path TEXT,
            status TEXT DEFAULT 'Pending',
            verified_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)

        # Create business profiles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_profiles (
            business_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            company_name TEXT,
            business_type TEXT,
            years_of_operation INTEGER,
            annual_turnover REAL,
            state TEXT,
            city TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)

        conn.commit()  # Save changes

init_db()  # Run DB creation

# ================================
# HOME PAGE
# ================================
@app.route("/")
def home():
    return render_template_string("""
    <h2>MSME Management System</h2>

    <h3>Users</h3>
    <a href="/add_user_form"><button>Add User</button></a>
    <a href="/view_users"><button>View Users</button></a>

    <h3>MSME Verification</h3>
    <a href="/add_msme_form"><button>Add MSME</button></a>
    <a href="/view_msme"><button>View MSME</button></a>

    <h3>Business</h3>
    <a href="/add_business_form"><button>Add Business</button></a>
    <a href="/view_business"><button>View Business</button></a>
    """)

# ================================
# USERS MODULE
# ================================
@app.route("/add_user_form")
def add_user_form():
    return render_template_string("""
    <h2>Add User</h2>
    <form method="POST" action="/add_user">

        Name:<br>
        <input name="full_name" required><br><br>

        Email:<br>
        <input name="email" required><br><br>

        Mobile:<br>
        <input name="mobile" required><br><br>

        Role:<br>
        <select name="role" required>
            <option value="">Select Role</option>
            <option>Cashier</option>
            <option>Sales Associates</option>
            <option>Store Managers</option>
        </select><br><br>

        <button type="submit">Save</button>
    </form>
    """)

@app.route("/add_user", methods=["POST"])
def add_user():
    with sqlite3.connect(DB_NAME) as conn:  # Open DB connection
        conn.execute(""" 
        INSERT INTO users (full_name,email,mobile_number,role)
        VALUES (?,?,?,?)
        """, (
            request.form["full_name"],
            request.form["email"],
            request.form["mobile"],
            request.form["role"]
        ))
        conn.commit()

    return "<h3>User Added</h3><a href='/'>Home</a>"

@app.route("/view_users")
def view_users():
    rows = sqlite3.connect(DB_NAME).execute("SELECT * FROM users").fetchall()  # Fetch all users

    html = """  
    <h2>Users Table</h2>
    <table border="1" cellpadding="10">
    <tr>
        <th>User ID</th>
        <th>Name</th>
        <th>Email</th>
        <th>Mobile</th>
        <th>Role</th>
        <th>Created At</th>
    </tr>
    """

    for r in rows:  # Loop through records
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

# ================================
# MSME MODULE
# ================================
@app.route("/add_msme_form")
def add_msme_form():
    return render_template_string("""
    <h2>Add MSME Verification</h2>
    <form method="POST" action="/add_msme" enctype="multipart/form-data">

        User ID:<br>
        <input name="user_id" required><br><br>

        Udyam Number:<br>
        <input name="udyam" required><br><br>

        Certificate Image:<br>
        <input type="file" name="certificate" required><br><br>

        Status:<br>
        <input name="status" required><br><br>

        <button type="submit">Save</button>
    </form>
    """)

@app.route("/add_msme", methods=["POST"])
def add_msme():
    file = request.files.get("certificate")  # Get uploaded file

    ext = os.path.splitext(file.filename)[1]  # Extract extension
    filename = str(uuid.uuid4()) + ext  # Unique file name
    save_path = os.path.join(CERT_FOLDER, filename)  # Full path
    file.save(save_path)  # Save file

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""  
        INSERT INTO msme_verification
        (user_id,udyam_number,certificate_path,status)
        VALUES (?,?,?,?)
        """, (
            request.form["user_id"],
            request.form["udyam"],
            save_path,
            request.form["status"]
        ))
        conn.commit()

    return "<h3>MSME Record Added</h3><a href='/'>Home</a>"

@app.route("/view_msme")
def view_msme():
    rows = sqlite3.connect(DB_NAME).execute("SELECT * FROM msme_verification").fetchall()

    html = """
    <h2>MSME Records</h2>
    <table border="1" cellpadding="10">
    <tr>
        <th>ID</th>
        <th>User ID</th>
        <th>Udyam</th>
        <th>Certificate</th>
        <th>Status</th>
        <th>Verified At</th>
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

@app.route("/certificate/<int:id>")
def certificate(id):
    row = sqlite3.connect(DB_NAME).execute(
        "SELECT certificate_path FROM msme_verification WHERE verification_id=?",
        (id,)
    ).fetchone()

    if row and os.path.exists(row[0]):  # Check if file exists
        return send_file(row[0])  # Send image file
    return "Not Found"

# ================================
# BUSINESS MODULE
# ================================
@app.route("/add_business_form")
def add_business_form():
    return render_template_string("""
    <h2>Add Business</h2>
    <form method="POST" action="/add_business">

        User ID:<br>
        <input name="user_id" required><br><br>

        Company Name:<br>
        <input name="company" required><br><br>

        Company Type:<br>
        <select name="type" required>
            <option value="">Select Type</option>
            <option>Supermarket</option>
            <option>FMCG</option>
            <option>Clothing</option>
            <option>Electronics</option>
        </select><br><br>

        Years:<br>
        <input name="years" type="number"><br><br>

        Turnover:<br>
        <input name="turnover" type="number" step="0.01"><br><br>

        State:<br>
        <select name="state" required>
            <option value="">Select State</option>
            <option>Andhra Pradesh</option>
            <option>Delhi</option>
            <option>Karnataka</option>
            <option>Kerala</option>
            <option>Tamil Nadu</option>
            <option>Telangana</option>
        </select><br><br>

        City:<br>
        <input name="city"><br><br>

        <button type="submit">Save</button>
    </form>
    """)

@app.route("/add_business", methods=["POST"])
def add_business():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
        INSERT INTO business_profiles
        VALUES (NULL,?,?,?,?,?,?,?)
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

    return "<h3>Business Added</h3><a href='/'>Home</a>"

@app.route("/view_business")
def view_business():
    rows = sqlite3.connect(DB_NAME).execute("SELECT * FROM business_profiles").fetchall()

    html = """
    <h2>Business Profiles</h2>
    <table border="1" cellpadding="10">
    <tr>
        <th>ID</th>
        <th>User ID</th>
        <th>Company</th>
        <th>Type</th>
        <th>Years</th>
        <th>Turnover</th>
        <th>State</th>
        <th>City</th>
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

# ================================
# RUN APP
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
  # Start Flask server
