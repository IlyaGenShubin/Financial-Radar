from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.storage.db import SessionLocal, RuleDB, TransactionResult
from app.rules import RuleEngine
import json

router = APIRouter()

def render_template(name, **kwargs):
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(name)
    return template.render(**kwargs)

@router.get("/", response_class=HTMLResponse)
def admin_home(request: Request):
    db = SessionLocal()
    try:
        stats = {
            "processed": db.query(TransactionResult).count(),
            "alerted": db.query(TransactionResult).filter(TransactionResult.alerted == True).count(),
            "reviewed": db.query(TransactionResult).filter(TransactionResult.reviewed == True).count(),
        }
        txs = db.query(TransactionResult).order_by(TransactionResult.id.desc()).limit(20).all()
    finally:
        db.close()
    return HTMLResponse(render_template("index.html", stats=stats, transactions=txs))

@router.get("/rules", response_class=HTMLResponse)
def rules_list():
    db = SessionLocal()
    try:
        rules = db.query(RuleDB).all()
    finally:
        db.close()
    return HTMLResponse(render_template("rules.html", rules=rules))

@router.post("/rules")
def create_rule(
    id: str = Form(...),
    type: str = Form(...),
    params: str = Form(...),
    enabled: bool = Form(False),
    priority: int = Form(0)
):
    db = SessionLocal()
    try:
        rule = RuleDB(
            id=id,
            type=type,
            enabled=enabled,
            priority=priority,
            params=json.loads(params),
            version=1
        )
        db.add(rule)
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/admin/rules", status_code=303)
