import queue
import threading
from app.rules import RuleEngine
from app.storage.db import save_result
from app.notify.sender import send_alert_if_needed
import logging

MAX_QUEUE_SIZE = 10_000
transaction_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)

def enqueue_transaction(tx: dict, correlation_id: str):
    try:
        transaction_queue.put_nowait({"tx": tx, "correlationId": correlation_id})
    except queue.Full:
        raise

def worker():
    engine = RuleEngine()
    while True:
        try:
            item = transaction_queue.get(timeout=1)
            correlation_id = item["correlationId"]
            tx = item["tx"]
            result = engine.evaluate(tx, correlation_id)
            save_result(tx, result, correlation_id)
            if result["alerted"]:
                send_alert_if_needed(tx, result, correlation_id)
            transaction_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logging.error("Worker error", extra={"error": str(e)})

threading.Thread(target=worker, daemon=True).start()
