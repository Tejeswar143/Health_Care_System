import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Load dataset
df = pd.read_csv(r"vital_signs_dataset.csv")

# Clean dirty values
df.replace(["", "N/A", "??", None], np.nan, inplace=True)
for col in ["Temperature_C", "Heart_Rate_BPM", "SpO2_Percent", "Resp_Rate_BPM"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Separate features and target
X = df.drop(columns=["Anomaly"])
y = df["Anomaly"]

# Preprocessing pipeline
preprocess_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="mean")),
    ("scaler", StandardScaler())
])

# Fit the preprocessing pipeline on the entire dataset
X_processed = preprocess_pipeline.fit_transform(X)

# Convert processed data back to DataFrame with feature names
X_processed_df = pd.DataFrame(X_processed, columns=X.columns)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_processed_df, y, test_size=0.2, random_state=42)

# Models to try
models = {
    "IsolationForest": IsolationForest(contamination=0.1, random_state=42),
    "OneClassSVM": OneClassSVM(nu=0.1, kernel="rbf", gamma='auto'),
    "Autoencoder": MLPRegressor(hidden_layer_sizes=(8, 4, 8), max_iter=500, random_state=42)
}

# Train and evaluate models
for name, model in models.items():
    print(f"\nModel: {name}")
    
    if name == "Autoencoder":
        model.fit(X_train, X_train)
        recon = model.predict(X_test)
        errors = np.mean((X_test - recon) ** 2, axis=1)
        threshold = np.percentile(errors, 90)
        y_pred = (errors > threshold).astype(int)
    else:
        model.fit(X_train)
        X_test_df = pd.DataFrame(X_test, columns=X_train.columns)
        y_pred = model.predict(X_test_df)
        y_pred = np.where(y_pred == -1, 1, 0)

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

# Save best model and preprocessing pipeline
joblib.dump(models["IsolationForest"], "best_model.joblib")
joblib.dump(preprocess_pipeline, "preprocess_pipeline.joblib")
print("Best model and preprocessing pipeline saved.")
