import ast
import operator as op
from app.rules.base import BaseRule, RuleResult

operators = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Gt: op.gt, ast.Lt: op.lt, ast.GtE: op.ge, ast.LtE: op.le, ast.Eq: op.eq, ast.NotEq: op.ne,
    ast.And: lambda a, b: a and b,
    ast.Or: lambda a, b: a or b,
    ast.Not: lambda a: not a,
}

def eval_node(node, tx, context):
    if isinstance(node, ast.BoolOp):
        values = [eval_node(v, tx, context) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        elif isinstance(node.op, ast.Or):
            return any(values)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not eval_node(node.operand, tx, context)
    elif isinstance(node, ast.Compare):
        left = eval_node(node.left, tx, context)
        for op_node, comparator in zip(node.ops, node.comparators):
            right = eval_node(comparator, tx, context)
            if not operators[type(op_node)](left, right):
                return False
            left = right
        return True
    elif isinstance(node, ast.Name):
        return tx.get(node.id, context.get(node.id, 0))
    elif isinstance(node, ast.Constant):
        return node.value
    else:
        raise ValueError(f"Unsupported node: {type(node)}")

class CompositeRule(BaseRule):
    def __init__(self, rule_id, params, version=1):
        super().__init__(rule_id, params, version)
        self.expr_tree = ast.parse(self.params["expr"], mode='eval').body

    def evaluate(self, tx, context):
        try:
            result = eval_node(self.expr_tree, tx, context)
            reason = self.params["expr"] if result else ""
            return RuleResult(triggered=bool(result), reason=reason, rule_id=self.rule_id, version=self.version)
        except Exception:
            return RuleResult(rule_id=self.rule_id, version=self.version)
