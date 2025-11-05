from fastapi import APIRouter, HTTPException
from uuid import uuid4
from app.models.transaction import TransactionCreate
from app.queue.engine import enqueue_transaction
import logging

router = APIRouter()

@router.post("/transactions", status_code=202)
async def receive_transaction(tx: TransactionCreate):
    correlation_id = str(uuid4())
    logging.info("Received transaction", extra={
        "correlationId": correlation_id,
        "component": "ingest"
    })
    try:
        tx_dict = tx.dict()
        tx_dict["transaction_id"] = f"GEN-{correlation_id[:8]}"
        enqueue_transaction(tx_dict, correlation_id)
    except Exception:
        raise HTTPException(status_code=503, detail="Queue full")
    return {"status": "accepted", "correlationId": correlation_id}
