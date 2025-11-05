from abc import ABC, abstractmethod

class RuleResult:
    def __init__(self, triggered: bool = False, reason: str = "", rule_id: str = "", version: int = 1):
        self.triggered = triggered
        self.reason = reason
        self.rule_id = rule_id
        self.version = version

class BaseRule(ABC):
    def __init__(self, rule_id: str, params: dict, version: int = 1):
        self.rule_id = rule_id
        self.params = params
        self.version = version

    @abstractmethod
    def evaluate(self, tx: dict, context: dict) -> RuleResult:
        pass
