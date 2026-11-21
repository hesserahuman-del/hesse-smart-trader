from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

app = FastAPI(
    title="HESSE SMART TRADER",
    description="MT5 Trading Management API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hesse-smart-trader.pages.dev"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

accounts = []

class Account(BaseModel):
    broker: str
    label: str
    account_type: str = "DEMO"
    server: Optional[str] = None

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

@app.get("/api/accounts")
def get_accounts():
    return {
        "total": len(accounts),
        "accounts": accounts
    }

@app.post("/api/accounts")
def add_account(account: Account):
    if not account.broker.strip() or not account.label.strip():
        raise HTTPException(
            status_code=400,
            detail="Broker and account label are required"
        )

    if account.account_type.upper() != "DEMO":
        raise HTTPException(
            status_code=400,
            detail="Only DEMO accounts are allowed"
        )

    new_account = {
        "id": str(uuid4()),
        "broker": account.broker.strip(),
        "label": account.label.strip(),
        "account_type": "DEMO",
        "server": account.server,
        "status": "NOT_CONNECTED",
        "trading_enabled": False
    }

    accounts.append(new_account)

    return {
        "message": "Demo account added",
        "account": new_account
    }

@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: str):
    for account in accounts:
        if account["id"] == account_id:
            accounts.remove(account)
            return {"message": "Account removed"}

    raise HTTPException(
        status_code=404,
        detail="Account not found"
)
