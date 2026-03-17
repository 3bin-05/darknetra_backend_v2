from fastapi import FastAPI
from app.routes import predict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DarkNetra API")

# 🔥 ADD THIS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for hackathon)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(predict.router)

@app.get("/")
def home():
    return {"message": "DarkNetra is running 🚀"}