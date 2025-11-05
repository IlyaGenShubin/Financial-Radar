from app.rules.base import BaseRule, RuleResult

class ThresholdRule(BaseRule):
    def evaluate(self, tx, context):
        field = self.params.get("field")
        op = self.params.get("op")
        value = self.params.get("value")
        actual = tx.get(field)
        if actual is None:
            return RuleResult(rule_id=self.rule_id, version=self.version)
        triggered = False
        if op == ">" and actual > value:
            triggered = True
        elif op == ">=" and actual >= value:
            triggered = True
        elif op == "<" and actual < value:
            triggered = True
        elif op == "<=" and actual <= value:
            triggered = True
        reason = f"{field} {op} {value}" if triggered else ""
        return RuleResult(triggered=triggered, reason=reason, rule_id=self.rule_id, version=self.version)
