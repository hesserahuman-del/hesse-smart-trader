from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HESSE SMART TRADER",
    description="Trading management API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hesse-smart-trader.pages.dev"
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def home():
    return {
        "project": "HESSE SMART TRADER",
        "status": "online",
        "mode": "DEMO"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "trading_enabled": False
    }


@app.get("/api/status")
def system_status():
    return {
        "project": "HESSE SMART TRADER",
        "mode": "DEMO",
        "execution": "DISABLED",
        "broker_connected": False
}
