from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://radar:radar@db:5432/radar")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class RuleDB(Base):
    __tablename__ = "rules"
    id = Column(String, primary_key=True)
    type = Column(String)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    params = Column(JSON)
    version = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow)

class TransactionResult(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, index=True)
    correlation_id = Column(String, index=True)
    timestamp = Column(DateTime)
    sender_account = Column(String)
    receiver_account = Column(String)
    amount = Column(Float)
    transaction_type = Column(String)
    merchant_category = Column(String, nullable=True)
    location = Column(String)
    device_used = Column(String)
    payment_channel = Column(String)
    ip_address = Column(String)
    device_hash = Column(String)
    time_since_last_transaction = Column(Float, nullable=True)
    spending_deviation_score = Column(Float, nullable=True)
    velocity_score = Column(Integer, nullable=True)
    geo_anomaly_score = Column(Float, nullable=True)
    alerted = Column(Boolean, default=False)
    rule_results = Column(JSON)
    ml_score = Column(Float, nullable=True)
    model_version = Column(String, nullable=True)
    reviewed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def load_rules_from_db():
    db = SessionLocal()
    try:
        return [r.__dict__ for r in db.query(RuleDB).filter(RuleDB.enabled == True).all()]
    finally:
        db.close()

def save_result(tx, result, correlation_id):
    db = SessionLocal()
    try:
        tr = TransactionResult(
            transaction_id=tx.get("transaction_id") or f"GEN-{correlation_id[:8]}",
            correlation_id=correlation_id,
            timestamp=tx["timestamp"],
            sender_account=tx["sender_account"],
            receiver_account=tx["receiver_account"],
            amount=tx["amount"],
            transaction_type=tx["transaction_type"],
            merchant_category=tx.get("merchant_category"),
            location=tx["location"],
            device_used=tx["device_used"],
            payment_channel=tx["payment_channel"],
            ip_address=tx["ip_address"],
            device_hash=tx["device_hash"],
            time_since_last_transaction=tx.get("time_since_last_transaction"),
            spending_deviation_score=tx.get("spending_deviation_score"),
            velocity_score=tx.get("velocity_score"),
            geo_anomaly_score=tx.get("geo_anomaly_score"),
            alerted=result.get("alerted", False),
            rule_results=result.get("reasons", []),
            ml_score=result.get("ml_score"),
            model_version=result.get("model_version"),
        )
        db.add(tr)
        db.commit()
    finally:
        db.close()
