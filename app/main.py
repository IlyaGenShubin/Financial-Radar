from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.transactions import router as tx_router
from app.admin.views import router as admin_router
from app.observability.logger import setup_logging

setup_logging()
app = FastAPI(title="Financial Radar")
app.include_router(tx_router, prefix="/api")
app.include_router(admin_router, prefix="/admin")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}
