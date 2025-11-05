from typing import List, Dict
from app.storage.db import load_rules_from_db
from app.rules.threshold import ThresholdRule
from app.rules.pattern import PatternRule
from app.rules.composite import CompositeRule
from app.rules.ml_rule import MLRule


class RuleEngine:
    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> List:
        """
        Загружает все включённые правила из БД и создаёт экземпляры соответствующих классов.
        Поддерживает типы: threshold, pattern, composite, ml.
        """
        rules = []
        for r in load_rules_from_db():
            rule_type = r["type"]
            rule_id = r["id"]
            params = r["params"]
            version = r["version"]

            if rule_type == "threshold":
                rules.append(ThresholdRule(rule_id, params, version))
            elif rule_type == "pattern":
                rules.append(PatternRule(rule_id, params, version))
            elif rule_type == "composite":
                rules.append(CompositeRule(rule_id, params, version))
            elif rule_type == "ml":
                rules.append(MLRule(rule_id, params, version))
            # новые типы можно добавить здесь

        # Сортировка по приоритету (по возрастанию: 0 — выше приоритет)
        return sorted(rules, key=lambda x: x.params.get("priority", 0))

    def evaluate(self, tx: Dict, correlation_id: str) -> Dict:
        """
        Применяет правила к транзакции по стратегии "first-match wins".
        Возвращает результат анализа с причинами, ML-скором и версией модели.
        """
        results = []
        ml_score = None
        model_version = None

        for rule in self.rules:
            try:
                res = rule.evaluate(tx, {})
                if res.triggered:
                    # Сохраняем информацию о срабатывании
                    result_entry = {
                        "rule_id": res.rule_id,
                        "reason": res.reason,
                        "version": res.version
                    }
                    results.append(result_entry)

                    # Если это ML-правило — извлекаем score и версию
                    if rule.__class__.__name__ == "MLRule":
                        # Предполагаем, что reason имеет вид: "ML score 0.85 >= 0.7"
                        try:
                            parts = res.reason.split()
                            if len(parts) >= 3:
                                ml_score = float(parts[2])
                        except (ValueError, IndexError):
                            ml_score = None
                        model_version = res.version

                    # Политика: first-match wins
                    return {
                        "alerted": True,
                        "reasons": results,
                        "ml_score": ml_score,
                        "model_version": f"v{model_version}" if model_version else None
                    }
            except Exception as e:
                # Логирование ошибки правила (в реальном коде — через logger)
                print(f"Error in rule {rule.rule_id}: {e}")
                continue

        # Ни одно правило не сработало
        return {
            "alerted": False,
            "reasons": [],
            "ml_score": ml_score,
            "model_version": f"v{model_version}" if model_version else None
        }
