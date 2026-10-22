"""PromptShield - wires every step of the methodology diagram together."""
from .classifier import PromptClassifier
from .config import DEFAULT_MODEL, T1, T2
from .database import LogDB
from .mitigation import make_safe_prompt
from .preprocessing import preprocess
from .rules import detect
from .scoring import decide, risk_score

WARNING_TEXT = "This prompt looks suspicious. It was allowed to continue but has been logged for review."
SELF_HARM_TEXT = ("It sounds like you may be going through something very painful. You don't have to face it alone - please reach out "
                  "to someone you trust or contact a local crisis helpline or emergency services right now.")
VIOLENCE_TEXT = ("This prompt was blocked because it expresses an intent to harm another person. If you are feeling angry or "
                 "unsafe, consider talking to someone you trust or a counsellor. In an emergency, contact your local emergency number.")
BLOCK_TEXT = "This prompt was blocked because it appears to request harmful or policy-violating behaviour."


class PromptShield:
    def __init__(self, model_type: str = DEFAULT_MODEL, log: bool = True, t1: float = T1, t2: float = T2):
        self.classifier = PromptClassifier(model_type)
        self.db = LogDB() if log else None
        self.t1, self.t2 = t1, t2

    def analyze(self, prompt: str, user_id: str = "anonymous") -> dict:
        pre = preprocess(prompt)                                              # 2. preprocessing
        ml_prob = self.classifier.malicious_probability(pre["clean_text"])    # 3+4. TF-IDF -> classifier
        rules = detect(pre["normalized"])                                     # 5. rule-based detection
        score = risk_score(ml_prob, rules)                                    # 6. risk scoring
        decision = decide(score, self.t1, self.t2)                            # 7. thresholds -> 8A/8B/8C

        result = {
            "user_id": user_id,
            "original_prompt": prompt,
            "normalized_prompt": pre["normalized"],
            "tokens": pre["filtered_tokens"],
            "ml_score": round(ml_prob, 4),
            "rule_score": rules["rule_score"],
            "matched_rules": rules["matches"],
            "risk_score": score,
            "risk_level": decision["level"],
            "label": decision["label"],
            "action": decision["action"],
            "safe_prompt": None,
            "message": "Prompt allowed.",
        }
        if decision["action"] == "WARN":
            result["message"] = WARNING_TEXT
        elif decision["action"] == "BLOCK":
            cats = {m["category"] for m in rules["matches"]}
            result["safe_prompt"] = make_safe_prompt(prompt, pre["normalized"], cats)   # 10. mitigation
            if "self_harm" in cats:
                result["message"] = SELF_HARM_TEXT
            elif "violence" in cats:
                result["message"] = VIOLENCE_TEXT
            else:
                result["message"] = BLOCK_TEXT
            result["categories"] = sorted(cats)
        if self.db:
            result["log_id"] = self.db.log(result)                            # 9. logging & database
        return result
