from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>MSME Project Deployed on Vercel 🚀</h1>
    <p>Docker image built separately via CI.</p>
    """
