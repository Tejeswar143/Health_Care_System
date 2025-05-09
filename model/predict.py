# predict.py

import joblib
import numpy as np

# Step 1: Load the saved model and LabelEncoder
print("Loading model and label encoder...")
clf = joblib.load("decision_tree_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# Step 2: Prepare your new input data
# Example: You have a patient with heart_rate=85, body_temperature=36.7
# (You can modify these numbers to whatever you want)
new_data = np.array([[85, 36.7]])

# Step 3: Predict using the loaded model
print("Predicting...")
predicted_class_encoded = clf.predict(new_data)

# Step 4: Decode the label back to original label (like "Normal", "Anomaly", etc.)
predicted_label = label_encoder.inverse_transform(predicted_class_encoded)

print(f"\n🩺 Predicted label: {predicted_label[0]}")
