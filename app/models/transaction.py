from pydantic import BaseModel, validator
from datetime import datetime, timezone
from typing import Optional
import re
import ipaddress
class TransactionCreate(BaseModel):
    # Обязательные поля (согласно датасету и требованиям)
    timestamp: datetime
    sender_account: str
    receiver_account: str
    amount: float
    transaction_type: str
    location: str
    device_used: str
    payment_channel: str
    ip_address: str
    device_hash: str
    # Опциональные поля (могут отсутствовать в запросе)
    merchant_category: Optional[str] = None
    time_since_last_transaction: Optional[float] = None
    spending_deviation_score: Optional[float] = None
    velocity_score: Optional[int] = None
    geo_anomaly_score: Optional[float] = None
    # Валидации
    @validator('amount')
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError('amount must be > 0')
        if v > 1e9:
            raise ValueError('amount too large')
        return v
    @validator('sender_account', 'receiver_account')
    def account_format(cls, v):
        if not re.match(r'^ACC[A-Z0-9]{6,20}$', v):
            raise ValueError('Invalid account format. Expected: ACC + alphanumeric, 6–20 chars')
        return v
    @validator('transaction_type')
    def valid_type(cls, v):
        allowed = {'withdrawal', 'deposit', 'transfer', 'payment'}
        if v not in allowed:
            raise ValueError(f'transaction_type must be one of {allowed}')
        return v
    @validator('payment_channel')
    def valid_channel(cls, v):
        allowed = {'card', 'ACH', 'wire_transfer', 'online', 'pos'}
        if v not in allowed:
            raise ValueError(f'payment_channel must be one of {allowed}')
        return v
    @validator('timestamp')
    def timestamp_not_future(cls, v):
        # Убедимся, что v — timezone-aware
        if v.tzinfo is None:
            raise ValueError('timestamp must be timezone-aware (e.g., end with Z)')
        now = datetime.now(timezone.utc)
        if (v - now).total_seconds() > 86400:  # ±1 день
            raise ValueError('Timestamp too far in future')
        if (now - v).total_seconds() > 365 * 86400:  # не старше года
            raise ValueError('Timestamp too old')
        return v
    @validator('ip_address')
    def valid_ip(cls, v):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError('Invalid IP address')
        return v
