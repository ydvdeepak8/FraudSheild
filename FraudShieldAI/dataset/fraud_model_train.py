import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report
import numpy as np

# Parameters
batch_size = 10000
filename = "D:/FraudShieldAI/dataset/PS_20174392719_1491204439457_log.csv"

# Label encoder for 'type'
le = LabelEncoder()

# Scaler for online training
scaler = StandardScaler()

# Model for partial training
model = SGDClassifier(loss='log_loss', random_state=42)

# Track first batch separately for encoder/scaler fitting
first_batch = True

for chunk in pd.read_csv(filename, chunksize=batch_size):
    # Encode 'type'
    chunk['type'] = le.fit_transform(chunk['type']) if first_batch else le.transform(chunk['type'])

    # Drop unnecessary columns
    chunk.drop(['nameOrig', 'nameDest', 'isFlaggedFraud'], axis=1, inplace=True)

    # Features and labels
    X = chunk.drop("isFraud", axis=1)
    y = chunk["isFraud"]

    # Scale features (fit only once)
    if first_batch:
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = scaler.transform(X)

    # Train model incrementally
    if first_batch:
        model.partial_fit(X_scaled, y, classes=np.array([0, 1]))  # specify classes first time
        first_batch = False
    else:
        model.partial_fit(X_scaled, y)

print("✅ Model trained in batches successfully!")

# Save model and tools if needed
import joblib
joblib.dump(model, "batch_model.pkl")
joblib.dump(scaler, "batch_scaler.pkl")
joblib.dump(le, "batch_encoder.pkl")
