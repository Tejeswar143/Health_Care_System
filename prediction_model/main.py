import firebase_admin
from firebase_admin import credentials, db
from alert import send_alert_email
import numpy as np
import pandas as pd
import joblib
from dotenv import load_dotenv
import os

load_dotenv()

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
firebase_db_url = os.getenv("FIREBASE_DATABASE_URL")
to_email = os.getenv("EMAIL_RECEIVER")

# Initialize Firebase Admin SDK
def initialize_firebase():
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_db_url
    })

# Fetch the latest temperature from Firebase
def fetch_latest_temperature():
    try:
        data = db.reference('temperature').get()
        if not data:
            print("No data found in temperature.")
            return None
        return max(data.values(), key=lambda x: x['timestamp'])['temp']
    except Exception as e:
        print(f"Error fetching temperature: {e}")
        return None

# Fetch the latest heart rate and SpO2 data from Firebase
def fetch_latest_spo2_data():
    try:
        data = db.reference('spo2_data').get()
        if not data:
            print("No data found in spo2_data.")
            return None, None
        latest_entry = max(data.values(), key=lambda x: x['timestamp'])
        return int(latest_entry.get('heartRate', 0)), latest_entry.get('spo2', None)
    except Exception as e:
        print(f"Error fetching SpO2 data: {e}")
        return None, None

# Fetch the latest ECG data from Firebase
def fetch_latest_ecg_data():
    try:
        data = db.reference('ecg').get()
        if not data:
            print("No data found in ecg.")
            return None
        return max(data.values(), key=lambda x: x['timestamp']).get('ecg', None)
    except Exception as e:
        print(f"Error fetching ECG data: {e}")
        return None


if __name__ == "__main__":
    initialize_firebase()
    print("Firebase initialized.")

    # Fetch and print the latest ECG data
    resp_rate = fetch_latest_ecg_data()
    print(f"Latest ECG Data: {resp_rate}" if resp_rate else "Failed to fetch the latest ECG data.")

    # Fetch and print the latest heart rate and SpO2 data
    heart_rate, spo2 = fetch_latest_spo2_data()
    if heart_rate is not None and spo2 is not None:
        print(f"Latest Heart Rate: {heart_rate} BPM, SpO2: {spo2}%")
    else:
        print("Failed to fetch the latest SpO2 data.")

    # Fetch and print the latest temperature data
    temp = fetch_latest_temperature()
    print(f"Latest Temperature: {temp}°C" if temp else "Failed to fetch the latest temperature.")
    
    # # Check if the values are abnormal
    # if temp is not None and heart_rate is not None and spo2 is not None and resp_rate is not None:
    #     # Define normal ranges
    #     temp_range = (36.1, 37.5)  # Normal temperature range in °C
    #     heart_rate_range = (60, 100)  # Normal heart rate range in BPM
    #     spo2_range = (95, 100)  # Normal SpO2 range in %
    #     resp_rate_range = (12, 20)  # Normal respiratory rate range in breaths/min

    #     # Check if values are within normal ranges
    #     temp_status = "normal" if temp_range[0] <= temp <= temp_range[1] else "abnormal"
    #     heart_rate_status = "normal" if heart_rate_range[0] <= heart_rate <= heart_rate_range[1] else "abnormal"
    #     spo2_status = "normal" if spo2_range[0] <= spo2 <= spo2_range[1] else "abnormal"
    #     resp_rate_status = "normal" if resp_rate_range[0] <= resp_rate <= resp_rate_range[1] else "abnormal"

    #     # Print the status of each vital sign
    #     print(f"Temperature is {temp_status}.")
    #     print(f"Heart Rate is {heart_rate_status}.")
    #     print(f"SpO2 is {spo2_status}.")
    #     print(f"Respiratory Rate is {resp_rate_status}.")

    #     # Determine overall status
    #     overall_status = "abnormal" if "abnormal" in [temp_status, heart_rate_status, spo2_status, resp_rate_status] else "normal"
    #     print(f"Overall status: {overall_status}.")
    # else:
    #     print("One or more values are missing, cannot determine health status.")
    

    # Load model and preprocessing pipeline
    model = joblib.load("best_model.joblib")
    preprocess_pipeline = joblib.load("preprocess_pipeline.joblib")

    # Define feature names (ensure these match the feature names used during training)
    feature_names = ["Temperature_C", "Heart_Rate_BPM", "SpO2_Percent", "Resp_Rate_BPM"]
        
    # Sample input: [Temperature_C, Heart_Rate_BPM, SpO2_Percent, Resp_Rate_BPM]
    input_data = np.array([[temp, heart_rate, spo2, resp_rate]])  # Replace with your own values

    # Convert input_data to a DataFrame with feature names
    input_data_df = pd.DataFrame(input_data, columns=feature_names)

    # Preprocess input
    input_processed = preprocess_pipeline.transform(input_data_df)

    # Predict
    model_output = model.predict(input_processed)

    # Convert to anomaly format: 1 = anomaly, 0 = normal
    anomaly_result = int(model_output[0] == -1)

    if anomaly_result == 1:  # If anomaly is detected
        print("Anomaly Detected!")
        
        # Prepare email details
        subject = "Urgent Alert: Abnormal Vital Signs Detected"
        body = (
            f"This is an automated alert to notify you that abnormal vital signs have been detected.\n\n"
            f"Details:\n"
            f"- Temperature: {temp}°C\n"
            f"- Heart Rate: {heart_rate} BPM\n"
            f"- SpO2: {spo2}%\n"
            f"- ECG (Respiratory Rate): {resp_rate} breaths/min\n\n"
            "Please check the system immediately for further details and take necessary action."
        )
        to_email = to_email  # Replace with the recipient's email

        # Send the alert email
        # send_alert_email(subject, body, to_email)
    else:
        print("No anomaly detected. All vital signs are normal.")