import pandas as pd
import joblib
from sklearn.metrics import classification_report, accuracy_score

# Load tools
model = joblib.load("batch_model.pkl")
scaler = joblib.load("batch_scaler.pkl")
le = joblib.load("batch_encoder.pkl")

# Load test data safely
filename = "D:/FraudShieldAI/dataset/PS_20174392719_1491204439457_log.csv"
test_data = pd.read_csv(filename, skiprows=range(1, 1000000), nrows=10000)

# Check columns
print("🧾 Columns in test_data:", test_data.columns.tolist())

# Make sure 'type' exists
if 'type' not in test_data.columns:
    raise ValueError("❌ 'type' column not found. Try a smaller skiprows value.")

# Preprocess
test_data['type'] = le.transform(test_data['type'])
test_data.drop(['nameOrig', 'nameDest', 'isFlaggedFraud'], axis=1, inplace=True)

X_test = test_data.drop("isFraud", axis=1)
y_test = test_data["isFraud"]
X_scaled = scaler.transform(X_test)

# Predict & Evaluate
y_pred = model.predict(X_scaled)
print("✅ Evaluation Results:")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))
