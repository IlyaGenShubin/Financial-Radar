import joblib
import numpy as np
from datetime import datetime
from app.rules.base import BaseRule, RuleResult

model = joblib.load("resources/model.pkl")

def build_features(tx):
    hour = tx["timestamp"].hour
    is_night = 1 if hour in {22, 23, 0, 1, 2, 3, 4, 5} else 0
    tllt = tx.get("time_since_last_transaction", 0.0) or 0.0
    sds = tx.get("spending_deviation_score", 0.0) or 0.0
    vs = tx.get("velocity_score", 0) or 0
    gas = tx.get("geo_anomaly_score", 0.0) or 0.0
    is_mobile = 1 if tx.get("device_used") == "mobile" else 0
    is_card = 1 if tx.get("payment_channel") == "card" else 0
    is_withdrawal = 1 if tx.get("transaction_type") == "withdrawal" else 0
    return np.array([
        np.log1p(tx["amount"]),
        hour,
        is_night,
        tllt,
        sds,
        vs,
        gas,
        is_mobile,
        is_card,
        is_withdrawal
    ], dtype=np.float32).reshape(1, -1)

class MLRule(BaseRule):
    def evaluate(self, tx, context):
        try:
            features = build_features(tx)
            prob = model.predict_proba(features)[0][1]
            threshold = self.params.get("threshold", 0.7)
            triggered = prob >= threshold
            reason = f"ML score {prob:.2f} >= {threshold}" if triggered else ""
            return RuleResult(
                triggered=triggered,
                reason=reason,
                rule_id=self.rule_id,
                version=self.version
            )
        except Exception:
            return RuleResult(rule_id=self.rule_id, version=self.version)
