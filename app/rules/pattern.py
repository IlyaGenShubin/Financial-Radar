from collections import defaultdict, deque
from datetime import datetime, timedelta
from app.rules.base import BaseRule, RuleResult

history_store = defaultdict(lambda: deque())

class PatternRule(BaseRule):
    def evaluate(self, tx, context):
        key = tx.get(self.params["by"])
        window_min = self.params["windowMin"]
        cutoff = datetime.utcnow() - timedelta(minutes=window_min)
        q = history_store[key]
        while q and q[0]["ts"] < cutoff:
            q.popleft()
        small_txs = sum(1 for t in q if t["amount"] <= self.params["maxAmount"])
        triggered = small_txs >= self.params["minCount"]
        q.append({"ts": tx["timestamp"], "amount": tx["amount"]})
        reason = f"{small_txs} small transfers in {window_min} min" if triggered else ""
        return RuleResult(triggered=triggered, reason=reason, rule_id=self.rule_id, version=self.version)
