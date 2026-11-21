import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI(
    title="HESSE SMART TRADER",
    description="MT5 Trading Management API",
    version="2.1.0"
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


DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg2.connect(DATABASE_URL)


class Account(BaseModel):
    broker: str
    label: str
    account_type: str = "DEMO"
    server: Optional[str] = None


@app.on_event("startup")
def create_database_table():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY,
                    broker TEXT NOT NULL,
                    label TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    server TEXT,
                    status TEXT NOT NULL,
                    trading_enabled BOOLEAN NOT NULL
                )
            """)


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
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM accounts
                    ORDER BY id
                """)
                saved_accounts = cursor.fetchall()

        return {
            "total": len(saved_accounts),
            "accounts": saved_accounts
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve accounts"
        )


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

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO accounts (
                        id, broker, label, account_type,
                        server, status, trading_enabled
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    new_account["id"],
                    new_account["broker"],
                    new_account["label"],
                    new_account["account_type"],
                    new_account["server"],
                    new_account["status"],
                    new_account["trading_enabled"]
                ))

        return {
            "message": "Demo account added",
            "account": new_account
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to save account"
        )


@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: str):

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM accounts
                    WHERE id = %s
                """, (account_id,))

                if cursor.rowcount == 0:
                    raise HTTPException(
                        status_code=404,
                        detail="Account not found"
                    )

        return {"message": "Account removed"}

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to delete account"
        )
