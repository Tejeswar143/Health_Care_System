import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.auth.transport import requests
from google.cloud import firestore
import datetime
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './gcp_credentials.json'

app = FastAPI()

db = firestore.Client()


firebase_request_adapter = requests.Request()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/data")
async def read_users():
    try:
        users_ref = db.collection("sensors")
        docs = users_ref.stream()

        users = []
        for doc in docs:
            user = doc.to_dict()
            user['id'] = doc.id
            users.append(user)

        return JSONResponse(content={"status": "success", "data": users})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)



@app.post("/add-random-sensor")
async def add_random_sensor():
    try:
        sensor_data = {
            "temperature": round(random.uniform(20.0, 35.0), 2),  # Celsius
            "humidity": round(random.uniform(30.0, 70.0), 2),     # Percent
            "status": random.choice(["OK", "ALERT", "WARNING"]),
            # "timestamp": datetime.now().isoformat()
        }

        doc_ref = db.collection("sensors").add(sensor_data)

        return JSONResponse(content={"status": "success", "message": "Sensor data added", "data": sensor_data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    try:
       uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(e)