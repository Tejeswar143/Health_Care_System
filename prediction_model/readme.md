# Health Monitoring System

This project is a health monitoring system that fetches vital signs (temperature, heart rate, SpO2, and respiratory rate) from Firebase Realtime Database, processes the data using a machine learning model, and sends alerts via email if abnormal values are detected.

## Features
- Fetches real-time data from Firebase Realtime Database.
- Processes data using a pre-trained machine learning model.
- Detects anomalies in vital signs.
- Sends email alerts when abnormal values are detected.

## Requirements
The project requires the following Python libraries, which are listed in the `requirements.txt` file:
- `firebase-admin`
- `numpy`
- `joblib`
- `scikit-learn`
- `imbalanced-learn`
- `pandas`
- `requests`
- And more (see `requirements.txt` for the full list).

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/health-monitoring-system.git
   cd health-monitoring-system

2. Install the required dependencies:
   pip install -r requirements.txt

3. Set up Firebase:

   Download your Firebase service account key JSON file from the Firebase Console.
   Replace the placeholder in the code with the path to your service account key file.

4. Update the email alert configuration:

Modify the send_alert_email function to include your SMTP server, email, and password.


Usage

1. Start the script:
    python main.py

2. The script will:

    Fetch the latest data from Firebase.
    Process the data using the machine learning model.
    Print the status of each vital sign (normal/abnormal).
    Send an email alert if any vital sign is abnormal.

Firebase Database Structure

Ensure your Firebase Realtime Database has the following structure:

{
    "temperature": {
        "-unique-id-1": {"temp": 37.2, "timestamp": "2025-05-14T19:33:35.967474"},
        "-unique-id-2": {"temp": 38.5, "timestamp": "2025-05-14T19:35:12.123456"}
    },
    "spo2_data": {
        "-unique-id-1": {"heartRate": 85, "spo2": 97, "timestamp": "2025-05-14T19:33:35.967474"}
    },
    "ecg": {
        "-unique-id-1": {"ecg": 18, "timestamp": "2025-05-14T19:33:35.967474"}
    }
}


File Structure

.
├── [main.py](http://_vscodecontentref_/0)               # Main script to fetch data, process it, and send alerts
├── [requirements.txt](http://_vscodecontentref_/1)      # List of required Python libraries
├── README.md             # Project documentation
├── [best_model.joblib](http://_vscodecontentref_/2)     # Pre-trained machine learning model
├── [preprocess_pipeline.joblib](http://_vscodecontentref_/3) # Preprocessing pipeline for input data


License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributing
Feel free to submit issues or pull requests to improve the project.

Contact
For any inquiries, please contact [your-email@example.com].