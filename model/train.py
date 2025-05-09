# # train.py

# from datasets import load_dataset
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.preprocessing import LabelEncoder
# from sklearn.metrics import classification_report, accuracy_score
# import joblib

# # Step 1: Load the dataset
# print("Loading dataset...")
# dataset = load_dataset("Atulit23/HealthVitalSigns")

# # Step 2: Convert to DataFrame
# df = pd.DataFrame(dataset['train'])

# # Step 3: Drop unwanted columns
# print("Dropping 'blood_pressure' column...")
# df = df.drop(columns=['blood_pressure'])  # Drop the blood_pressure column

# # Step 4: Prepare features (X) and labels (y)
# X = df[['heart_rate', 'body_temperature']]  # Only using heart_rate and body_temperature
# y = df['label']  # Using the existing label

# # Step 5: Encode labels if they are strings
# print("Encoding labels...")
# label_encoder = LabelEncoder()
# y_encoded = label_encoder.fit_transform(y)

# # Step 6: Split into training and testing sets
# print("Splitting data into training and testing sets...")
# X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# # Step 7: Initialize and train the Decision Tree Classifier
# print("Training Decision Tree model...")
# clf = DecisionTreeClassifier(random_state=42)
# clf.fit(X_train, y_train)

# # Step 8: Evaluate the model
# print("Evaluating model...")
# y_pred = clf.predict(X_test)
# print("\nClassification Report:")
# print(classification_report(y_test, y_pred))
# print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# # Step 9: Save the model and the Label Encoder
# print("Saving model and label encoder...")
# joblib.dump(clf, "decision_tree_model.pkl")
# joblib.dump(label_encoder, "label_encoder.pkl")

# print("\n✅ Model and Label Encoder saved successfully as 'decision_tree_model.pkl' and 'label_encoder.pkl'")



# install required libraries first
# pip install pandas scikit-learn scipy requests tqdm datasets

# train.py

import os
import io
import zipfile
import requests
import pandas as pd
from datasets import load_dataset
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# 1. Load HuggingFace HealthVitalSigns Dataset
print("🔹 Loading HealthVitalSigns dataset...")
dataset = load_dataset("Atulit23/HealthVitalSigns")
df = pd.DataFrame(dataset['train'])

# Drop the unwanted column
print("🔹 Dropping 'blood_pressure' column...")
df = df.drop(columns=['blood_pressure'])

# 2. Download BIDMC Dataset (Correct Link!)
print("🔹 Downloading BIDMC dataset...")

bidmc_url = "https://physionet.org/static/published-projects/chfdb/chfdb-1.0.0.zip"
bidmc_zip_path = "bidmc_dataset.zip"
bidmc_extract_folder = "bidmc_data"

if not os.path.exists(bidmc_extract_folder):
    r = requests.get(bidmc_url)
    with open(bidmc_zip_path, 'wb') as f:
        f.write(r.content)
    print("🔹 Extracting BIDMC dataset...")
    with zipfile.ZipFile(bidmc_zip_path, 'r') as zip_ref:
        zip_ref.extractall(bidmc_extract_folder)
    os.remove(bidmc_zip_path)
else:
    print("🔹 BIDMC data already exists. Skipping download.")

# Note: You will still need wfdb library to fully read BIDMC signals later.

# 3. Preprocessing HealthVitalSigns dataset
print("🔹 Encoding labels...")

# For simplicity: Let's assume "label" is our target
le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['label'])

# Only keeping relevant features for now
features = ['heart_rate', 'body_temperature']
X = df[features]
y = df['label_encoded']

# 4. Train Test Split
print("🔹 Splitting data into training and testing sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train Model
print("🔹 Training Decision Tree model...")
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# 6. Evaluate Model
print("🔹 Evaluating model...")
y_pred = model.predict(X_test)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# 7. Save Model and LabelEncoder
print("\nSaving model and label encoder...")
joblib.dump(model, "decision_tree_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("\n✅ Model and Label Encoder saved successfully as 'decision_tree_model.pkl' and 'label_encoder.pkl'")
