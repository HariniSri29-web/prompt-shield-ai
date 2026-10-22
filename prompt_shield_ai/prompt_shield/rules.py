"""Step 5 - Rule-based detection (regex / keyword pattern matching)."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    name: str
    category: str
    pattern: re.Pattern
    severity: float          # 0..1 - how strongly a match indicates malicious intent


def _r(name, category, pattern, severity):
    return Rule(name, category, re.compile(pattern, re.I), severity)


RULES = [
    # --- prompt injection / instruction override
    _r("ignore_instructions", "injection", r"\b(ignore|disregard|forget|override|bypass)\b.{0,30}\b(previous|prior|above|earlier|all|your|system)\b.{0,30}\b(instructions?|rules?|prompts?|guidelines?|filters?|restrictions?|polic(y|ies))\b", 0.92),
    _r("reveal_system_prompt", "injection", r"\b(reveal|show|print|repeat|leak|tell me)\b.{0,30}\b(system prompt|hidden instructions?|initial instructions?|confidential (config\w*|instructions?))", 0.90),
    _r("answer_without_restrictions", "injection", r"\b(without|no|never)\b.{0,15}\b(restrictions?|limitations?|filters?|rules|censorship|refus\w+)\b", 0.60),
    # --- jailbreak personas
    _r("dan_persona", "jailbreak", r"\b(dan|do anything now|jailbreak(ed)?|developer mode|god mode)\b", 0.75),
    _r("no_ethics_persona", "jailbreak", r"\b(pretend|act as|you are now|roleplay)\b.{0,40}\b(no (ethic\w*|moral\w*|guidelines|restrictions)|unfiltered|uncensored|evil)\b", 0.85),
    # --- malware / cyber abuse
    _r("disable_security", "cyber", r"\b(disable|turn off|kill|evade|bypass)\b.{0,25}\b(firewalls?|antivirus|edr|security (software|controls?)|authentication|login)\b", 0.80),
    _r("ransomware", "cyber", r"\b(build|create|write|make|code)\b.{0,25}\b(ransomware|crypto ?locker)\b|\bencrypts? (all )?(the )?(victim|files)\b", 0.85),
    _r("keylogger_stealer", "cyber", r"\b(create|write|build|make|code|give|need|want|get)\b.{0,25}\b(keylogger|password stealer|info ?stealer)\b|\bsteal\w*\b.{0,25}\bpasswords?\b|\bcredential harvest\w*\b", 0.85),
    _r("ddos", "cyber", r"\b(launch|run|start|perform|carry out)\b.{0,15}\b(ddos|dos attack|botnet)\b", 0.85),
    _r("hacking_unauthorised", "cyber", r"\b(hack|break|crack|get) (into|someone'?s|my neighbou?r'?s|their)\b", 0.75),
    _r("phishing_creation", "fraud", r"\b(write|create|draft|make)\b.{0,25}\bphishing\b|\bphishing (email|page|site)\b.{0,25}\b(steal|bank|credentials?)\b", 0.85),
    _r("malware_spread", "cyber", r"\b(spread|distribute|deploy)\b.{0,25}\b(virus|malware|trojan|worm)\b", 0.85),
    _r("evade_detection", "cyber", r"\b(avoid|evade|bypass|hide from|undetected by)\w*\b.{0,20}\b(detection|antivirus|edr|security)\b", 0.55),
    _r("exfiltration", "cyber", r"\bexfiltrat\w+\b|\bwithout (being )?(detect\w*|caught|noticed)\b", 0.65),
    # --- fraud
    _r("card_fraud", "fraud", r"\b(clone|skim|forge|fake)\b.{0,20}\b(credit card|debit card|id|passport)\b", 0.88),
    # --- weak signals (raise suspicion but are common in educational prompts)
    _r("weak_attack_terms", "weak", r"\b(exploit|payload|malware|backdoor|sql injection|reverse shell|zero[- ]day)\b", 0.30),
    _r("step_by_step_harm", "weak", r"\bstep[- ]by[- ]step\b.{0,30}\b(attack|hack|steal|break)\b", 0.40),
]


def detect(text: str) -> dict:
    """Return matched rules and a rule score in [0, 1] (noisy-OR combination of matched severities)."""
    hits = [r for r in RULES if r.pattern.search(text)]
    miss = 1.0
    for r in hits:
        miss *= (1.0 - r.severity)
    return {
        "rule_score": round(1.0 - miss, 4),
        "max_severity": max((r.severity for r in hits), default=0.0),
        "matches": [{"rule": r.name, "category": r.category, "severity": r.severity} for r in hits],
    }
