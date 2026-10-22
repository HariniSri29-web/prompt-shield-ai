"""Step 6 (risk scoring) and Step 7 (threshold based decision)."""
from .config import HARD_RULE_FLOOR, HARD_RULE_SEVERITY, T1, T2, W_ML, W_RULE


def risk_score(ml_prob: float, rule_result: dict) -> float:
    """Blend ML probability with rule score. A very severe rule match acts as a hard floor."""
    score = W_ML * ml_prob + W_RULE * rule_result["rule_score"]
    if rule_result["max_severity"] >= HARD_RULE_SEVERITY:
        score = max(score, HARD_RULE_FLOOR)
    return round(min(max(score, 0.0), 1.0), 4)


def decide(score: float, t1: float = T1, t2: float = T2) -> dict:
    if score <= t1:
        return {"level": "LOW", "label": "SAFE", "action": "ALLOW", "log_note": "Log only"}
    if score < t2:
        return {"level": "MEDIUM", "label": "SUSPICIOUS", "action": "WARN", "log_note": "Warn & Log"}
    return {"level": "HIGH", "label": "MALICIOUS", "action": "BLOCK", "log_note": "Block & Log"}
