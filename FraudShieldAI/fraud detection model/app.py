import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import joblib
import os

# ✅ Must be first Streamlit command
st.set_page_config(page_title="Fraud Detection App", layout="centered")

# Debug: Show current directory
st.write(f"📂 Current Working Directory: `{os.getcwd()}`")

# Define file paths
model_path = 'C:/Users/deepa/Desktop/pro/fraud_detection_model.pkl'
scaler_path = 'C:/Users/deepa/Desktop/pro/scaler.pkl'

# Load model and scaler with proper error handling
try:
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    st.success("✅ Model and Scaler loaded successfully.")
except FileNotFoundError:
    st.error("❌ Model or Scaler file not found. Please ensure both `.pkl` files are in the correct folder.")
    st.stop()
except Exception as e:
    st.error(f"❌ An unexpected error occurred while loading files: {e}")
    st.stop()

# Sidebar navigation
with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Home", "Predict Fraud"],
        icons=["house", "shield-exclamation"],
        default_index=0
    )

# Home Page
if selected == "Home":
    st.title("💳 Fraud Detection App")
    st.markdown("""
        Welcome to the **Fraud Detection App**!  
        This tool lets you input transaction details and predicts whether it's **Legitimate** or **Fraudulent** using a trained Machine Learning model.

        👉 Use the **Predict Fraud** tab to test your transactions.
    """)

# Prediction Page
elif selected == "Predict Fraud":
    st.title("🔍 Predict Transaction Fraud")

    feature_names = [
        'Avg min between sent tnx', 'Avg min between received tnx', 'Time Diff between first and last (Mins)',
        'Sent tnx', 'Received Tnx', 'Number of Created Contracts', 'Unique Received From Addresses',
        'Unique Sent To Addresses', 'min value received', 'max value received', 'avg val received',
        'min val sent', 'max val sent', 'avg val sent', 'min value sent to contract',
        'max val sent to contract', 'avg value sent to contract',
        'total transactions (including tnx to create contract)', 'total Ether sent', 'total ether received',
        'total ether sent contracts', 'total ether balance', 'Total ERC20 tnxs',
        'ERC20 total Ether received', 'ERC20 total ether sent', 'ERC20 total Ether sent contract',
        'ERC20 uniq sent addr', 'ERC20 uniq rec addr', 'ERC20 uniq sent addr.1',
        'ERC20 uniq rec contract addr', 'ERC20 avg time between sent tnx',
        'ERC20 avg time between rec tnx', 'ERC20 avg time between rec 2 tnx',
        'ERC20 avg time between contract tnx', 'ERC20 min val rec', 'ERC20 max val rec',
        'ERC20 avg val rec', 'ERC20 min val sent', 'ERC20 max val sent', 'ERC20 avg val sent',
        'ERC20 min val sent contract', 'ERC20 max val sent contract', 'ERC20 avg val sent contract',
        'ERC20 uniq sent token name', 'ERC20 uniq rec token name', 'ERC20 most sent token type',
        'ERC20_most_rec_token_type'
]


    user_input = []
    for feature in feature_names:
        value = st.number_input(f"{feature}", step=0.1, format="%.2f")
        user_input.append(value)

    if st.button("🔎 Predict"):
        try:
            scaled_input = scaler.transform([user_input])
            prediction = model.predict(scaled_input)
            result = "🟢 Legitimate Transaction" if prediction[0] == 0 else "🔴 Fraudulent Transaction"
            st.success(f"Prediction: {result}")
        except Exception as e:
            st.error(f"⚠️ Error during prediction: {e}")
