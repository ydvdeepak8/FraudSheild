from flask import Flask, request, jsonify
import joblib
import pandas as pd
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template
import datetime
from pymongo import MongoClient
from pymongo import MongoClient
from fpdf import FPDF
import tempfile
from flask import send_file



# Connect to local MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['fraud_detection']
collection = db['predictions']

app = Flask(__name__)
CORS(app)

# Load trained components
model = joblib.load("model/batch_model.pkl")
scaler = joblib.load("model/batch_scaler.pkl")
encoder = joblib.load("model/batch_encoder.pkl")

expected_features = ['step', 'type', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
fraud_reason_explanations = {
    "high_amount": "The transaction amount is unusually high compared to the user's regular spending.",
    "foreign_location": "The transaction was initiated from an unusual or foreign location.",
    "odd_hour": "The transaction was made at an unusual time of day.",
    "new_device": "The transaction was made from a previously unseen device.",
    "multiple_failed_attempts": "There were several failed transaction attempts before this one.",
    "mismatch_details": "The transaction details do not match the user's registered information."
}

@app.route('/')
def home():
    return "🚀 FraudShieldAI is up and running! Use POST /predict to detect fraudulent transactions."

def send_fraud_alert_email(transaction_data, fraud_reasons, receiver_email):
    sender_email = "divyanshusharma3305@gmail.com"
    password = "vokn--"  # App password

    subject = "🚨 Fraud Alert Detected in Transaction"
    
    # Dynamically generate reason descriptions
    detailed_reasons = [
        fraud_reason_explanations.get(reason, reason) for reason in fraud_reasons
    ]

    description = (
        "This transaction has been identified as potentially fraudulent based on a combination "
        "of unusual patterns such as high transaction amount, irregular timing, or suspicious location/activity. "
        "Below are the specific reasons why this transaction was flagged:"
    )
  
    body = f"""
    <h3>🚨 Fraudulent Transaction Detected</h3>
    <p>{description}</p>
    <ul>
        {''.join([f"<li>{explanation}</li>" for explanation in detailed_reasons])}
    </ul>
    <h4>Transaction Details:</h4>
    <ul>
        {''.join([f"<li><strong>{key}:</strong> {value}</li>" for key, value in transaction_data.items()])}
    </ul>
    """
     
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        print(f"✅ Fraud alert email sent to {receiver_email}")
    except Exception as e:
        print("❌ Failed to send email:", e)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        df = pd.DataFrame([data])

        # Extract receiver email
        receiver_email = data.get("email")
        if not receiver_email:
            return jsonify({"error": "Receiver email not provided"}), 400

        # Encode 'type'
        df['type'] = encoder.transform([[data['type']]])

        # Convert numeric fields
        numeric_cols = ['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

        # Scale the features
        X_scaled = scaler.transform(df[expected_features])

        # Model prediction
        proba = model.predict_proba(X_scaled)[0][1]
        pred = int(proba >= 0.5)

        # Rule-based conditions
        fraud_conditions = []

        step = float(data['step'])
        amount = float(data['amount'])
        oldbalanceOrg = float(data['oldbalanceOrg'])
        newbalanceOrig = float(data['newbalanceOrig'])
        oldbalanceDest = float(data['oldbalanceDest'])
        newbalanceDest = float(data['newbalanceDest'])
        tx_type = data['type']

       # 1. 💸 Transfer from Zero Balance:
        if oldbalanceOrg == 0 and amount > 0:
            fraud_conditions.append("💸 Transfer from Zero Balance")
        # 2. 💰 No Change in Receiver Balance:
        if oldbalanceDest > 0 and newbalanceDest == 0:
            fraud_conditions.append("💰 No Change in Receiver Balance")
        # 3. 🔁 New Orig Balance Incorrect:
        if round(oldbalanceOrg - amount, 2) != round(newbalanceOrig, 2):
            fraud_conditions.append("🔁 New Orig Balance Incorrect")
        # 4. 🪙 Large Amounts (> 200K):
        if amount > 200000:
            fraud_conditions.append("🪙 Large Amount (> 200K)")
        # 5. 🕐 Odd Hour Transactions (early morning):
        if step % 24 < 4:
            fraud_conditions.append("🕐 Odd Hour Transaction")
        # 6. ⚠️ High Amount, Zero Dest. Growth:
        if amount > 200000 and newbalanceDest == 0:
            fraud_conditions.append("⚠️ High Amount, Zero Dest. Growth")
        # 7. 🔐 TRANSFER but Receiver is Empty:
        if data['type'] == 'TRANSFER' and newbalanceDest == 0 and oldbalanceDest > 0:
            fraud_conditions.append("🔐 TRANSFER but Receiver is Empty")

        # ------------------- ADDITIONAL RULE-BASED CONDITIONS -------------------
        # 8. Sender Unexpected Balance Increase:
        # For CASH_OUT transactions, sender’s new balance should be less than (or equal to) the old balance.
        if data['type'] == 'CASH_OUT' and newbalanceOrig > oldbalanceOrg:
            fraud_conditions.append("🚩 Sender Balance Increased on CASH_OUT")
        # 9. Mismatch in Deduction Amount:
        # The deducted amount from sender should equal the transaction amount.
        if round(oldbalanceOrg - newbalanceOrig, 2) != round(amount, 2):
            fraud_conditions.append("🚩 Deduction Amount Mismatch (Sender)")
        # 10. Mismatch in Deposit Amount (for TRANSFER):
        # For TRANSFER, the increase in receiver's balance should equal the transaction amount.
        if data['type'] == 'TRANSFER' and round(newbalanceDest - oldbalanceDest, 2) != round(amount, 2):
            fraud_conditions.append("🚩 Deposit Amount Mismatch (Receiver)")
        # 11. Negative New Balances:
        # Negative balances are typically not expected.
        if newbalanceOrig < 0 or newbalanceDest < 0:
            fraud_conditions.append("🚩 Negative New Balance")
        # 12. No Change Despite Positive Amount:
        # If the transaction amount is positive but none of the balances change, something is wrong.
        if amount > 0 and oldbalanceOrg == newbalanceOrig and oldbalanceDest == newbalanceDest:
            fraud_conditions.append("🚩 No Balance Change Detected")
        # 13. Extremely High Transaction Amount:
        # Transactions above a very high threshold might be fraud.
        if amount > 1e6:
            fraud_conditions.append("🚩 Extremely High Transaction Amount")
        # Final decision
        is_fraud = False
        if pred == 1 or fraud_conditions:
            result = "🚨 Possibly Fraudulent"
            is_fraud = True
            send_fraud_alert_email(data, fraud_conditions, receiver_email)
        else:
            result = "✅ Likely Legitimate"

        # Save prediction to MongoDB
        prediction_data = {
            "email": receiver_email,
            "amount": amount,
            "location": data.get("location", "Unknown"),
            "device": data.get("device", "Unknown"),
            "ml_prediction": "Fraud" if pred == 0 else "Legitimate",
            "rule_based_flags": fraud_conditions,
            "overall_risk": "Fraud" if is_fraud else "Legitimate",
            "time": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "probability": round(proba, 4)
        }

        collection.insert_one(prediction_data)

        # Return result to frontend
        return jsonify({
            "prediction": pred,
            "probability": round(proba, 4),
            "result": result,
            "rule_based_flags": fraud_conditions,
            "sender_info": {
                "old_balance": oldbalanceOrg,
                "new_balance": newbalanceOrig
            },
            "receiver_info": {
                "old_balance": oldbalanceDest,
                "new_balance": newbalanceDest
            }
        })



    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
@app.route('/get-fraud-transactions', methods=['GET'])
def get_fraud_transactions():
    data = list(collection.find({}, {"_id": 0}))  # Exclude Mongo's _id field
    return jsonify(data)

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    try:
        file = request.files.get('file')
        email = request.form.get('email', '')

        if not file or not email:
            return jsonify({"error": "Missing file or email"}), 400

        df = pd.read_csv(file)
        transactions = df.to_dict(orient='records')


        results = []

        for tx in transactions:
            df = pd.DataFrame([tx])
            df['type'] = encoder.transform([[tx['type']]])
            df[expected_features] = df[expected_features].apply(pd.to_numeric)

            X_scaled = scaler.transform(df[expected_features])
            proba = model.predict_proba(X_scaled)[0][1]
            pred = int(proba >= 0.5)

            is_fraud = False
            fraud_conditions = []

            # Add any rule-based checks here (you can refactor from single predict route)
            if tx.get("amount", 0) > 1e6:
                fraud_conditions.append("🚩 Extremely High Transaction Amount")
                is_fraud = True

            result_label = "🚨 Possibly Fraudulent" if pred == 1 or is_fraud else "✅ Likely Legitimate"

            result = {
                "transaction": tx,
                "prediction": pred,
                "probability": round(proba, 4),
                "result": result_label,
                "rule_based_flags": fraud_conditions
            }

            results.append(result)

            # Save each prediction to MongoDB
            collection.insert_one({
                **result,
                "email": email,
                "time": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            })

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for i, res in enumerate(results):
            pdf.cell(200, 10, txt=f"Transaction {i+1}: {res['result']}", ln=True)
            for key, value in res["transaction"].items():
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
            pdf.cell(200, 10, txt=f"ML Prediction: {res['prediction']} | Probability: {res['probability']}", ln=True)
            pdf.cell(200, 10, txt=f"Flags: {', '.join(res['rule_based_flags'])}", ln=True)
            pdf.cell(200, 10, txt="-"*60, ln=True)

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp.name)

        # Optionally email the PDF as attachment
        send_pdf_to_email(email, temp.name)

        return send_file(temp.name, as_attachment=True)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def send_pdf_to_email(receiver_email, pdf_path):
    sender_email = "divyanshusharma3305@gmail.com"
    password = "voknqgnlgavwblst"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "🚨 Batch Fraud Prediction Report"

    body = "Please find the attached fraud prediction report."
    msg.attach(MIMEText(body, "plain"))

    with open(pdf_path, "rb") as f:
        part = MIMEText(f.read(), "base64", "utf-8")
        part.add_header('Content-Disposition', 'attachment', filename="fraud_report.pdf")
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        print(f"✅ PDF report sent to {receiver_email}")
    except Exception as e:
        print("❌ Email error:", e)

if __name__ == '__main__':
    app.run(debug=True)
