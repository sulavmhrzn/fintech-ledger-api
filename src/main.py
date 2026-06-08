from fastapi import FastAPI

from src.api.middleware import StructuredLoggingMiddleware
from src.api.v1 import auth, ledger, users, wallets
from src.config.logger import setup_logging

setup_logging(is_production=False)

app = FastAPI(
    title="Fintech Ledger & Virtual Wallet API",
    description="A highly-secure, double-entry ledger system.",
    version="1.0.0",
)

app.add_middleware(StructuredLoggingMiddleware)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(wallets.router, prefix="/api/v1")
app.include_router(ledger.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "fintech-ledger"}
