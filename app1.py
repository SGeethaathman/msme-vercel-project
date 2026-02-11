import os
import sqlite3
import uuid
from flask import Flask, request, render_template_string, send_file

app = Flask(__name__)

# ================================
# PATH SETTINGS
# ================================
UPLOAD_FOLDER = r"C:\Users\S.Geethaathman\Desktop\DataNetra\Image uploads"
DB_NAME = r"C:\Users\S.Geethaathman\Desktop\DataNetra\app.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("DB USED BY FLASK:", os.path.abspath(DB_NAME))

# ================================
# DATABASE INIT
# ================================
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            job_title TEXT NOT NULL,
            image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

init_db()

# ================================
# HOME PAGE
# ================================
@app.route("/")
def home():
    return render_template_string("""
        <h2>Upload Details + Image</h2>

        <form action="/upload" method="POST" enctype="multipart/form-data">
            
            Name:<br>
            <input type="text" name="name" required><br><br>

            Location:<br>
            <input type="text" name="location" required><br><br>

            Job Title:<br>
            <input type="text" name="job_title" required><br><br>

            Image:<br>
            <input type="file" name="image" required><br><br>

            <button type="submit">Upload</button>
        </form>
    """)

# ================================
# UPLOAD ROUTE
# ================================
@app.route("/upload", methods=["POST"])
def upload():

    try:
        name = request.form.get("name")
        location = request.form.get("location")
        job_title = request.form.get("job_title")
        image = request.files.get("image")

        if not image or image.filename == "":
            return "No image uploaded"

        # Unique filename
        ext = os.path.splitext(image.filename)[1]
        filename = str(uuid.uuid4()) + ext
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        image.save(file_path)

        # Save to DB
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO user_inputs
                (name, location, job_title, image_path)
                VALUES (?, ?, ?, ?)
            """, (name, location, job_title, file_path))

            conn.commit()

        # =========================
        # SUCCESS PAGE WITH BUTTON
        # =========================
        return """
        <h2>✅ Data Stored Successfully!</h2>

        <br>

        <a href="/view_data">
            <button style="
                padding:12px 25px;
                font-size:18px;
                background-color:green;
                color:white;
                border:none;
                border-radius:5px;
                cursor:pointer;">
                View Data
            </button>
        </a>

        <br><br>

        <a href="/">
            <button style="
                padding:10px 20px;
                font-size:16px;">
                Upload More Data
            </button>
        </a>
        """

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return str(e)

# ================================
# VIEW DATABASE PAGE
# ================================
@app.route("/view_data")
def view_data():

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_inputs ORDER BY id DESC")
        rows = cursor.fetchall()

    html = "<h2>📊 Database Records</h2>"
    html += f"<h3>Total Records: {len(rows)}</h3>"

    html += """
    <table border="1" cellpadding="10">
    <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Location</th>
        <th>Job Title</th>
        <th>Image</th>
        <th>Created Time</th>
    </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td><img src="/image/{r[0]}" width="120"></td>
            <td>{r[5]}</td>
        </tr>
        """

    html += "</table>"
    html += '<br><br><a href="/">⬅ Go Home</a>'

    return html

# ================================
# IMAGE DISPLAY ROUTE
# ================================
@app.route("/image/<int:id>")
def get_image(id):

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT image_path FROM user_inputs WHERE id=?", (id,))
        result = cursor.fetchone()

    if result and os.path.exists(result[0]):
        return send_file(result[0])
    else:
        return "Image Not Found"

# ================================
# RUN APP
# ================================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
