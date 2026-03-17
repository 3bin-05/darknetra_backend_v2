from fastapi import FastAPI
from app.routes import predict

app = FastAPI(title="DarkNetra API")

app.include_router(predict.router)

@app.get("/")
def home():
    return {"message": "DarkNetra is running 🚀"}