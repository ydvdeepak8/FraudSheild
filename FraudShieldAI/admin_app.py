from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__, template_folder='templates')

@app.route('/')
def admin_dashboard():
    try:
        response = requests.get("http://localhost:5000/get-fraud-transactions")
        transactions = response.json()
    except Exception as e:
        transactions = []
        print("Error fetching data:", e)
    return render_template("admin.html", transactions=transactions)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
