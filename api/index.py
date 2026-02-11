from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "Flask app deployed on Vercel (serverless)",
        "docker": "Docker image built separately via CI"
    })
