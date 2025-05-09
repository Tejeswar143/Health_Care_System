# predict_cli.py

import joblib
import numpy as np

# Step 1: Load the saved model and LabelEncoder
print("Loading model and label encoder...")
clf = joblib.load("decision_tree_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

print("\n🩺 Health Prediction CLI Started 🩺")
print("Type 'exit' anytime to stop.\n")

while True:
    try:
        # Step 2: Take heart rate input
        heart_rate_input = input("Enter Heart Rate (or 'exit' to quit): ")
        if heart_rate_input.lower() == 'exit':
            print("Exiting...")
            break
        heart_rate = float(heart_rate_input)

        # Step 3: Take body temperature input
        body_temp_input = input("Enter Body Temperature (or 'exit' to quit): ")
        if body_temp_input.lower() == 'exit':
            print("Exiting...")
            break
        body_temperature = float(body_temp_input)

        # Step 4: Prepare input and predict
        new_data = np.array([[heart_rate, body_temperature]])
        predicted_class_encoded = clf.predict(new_data)
        predicted_label = label_encoder.inverse_transform(predicted_class_encoded)

        print(f"🩺 Predicted Health Status: {predicted_label[0]}\n")

    except ValueError:
        print("⚠️ Invalid input. Please enter numeric values for heart rate and body temperature.\n")
