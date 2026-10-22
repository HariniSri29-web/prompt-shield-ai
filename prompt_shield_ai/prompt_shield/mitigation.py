"""Step 10 - Prompt modification & mitigation: generate a safe alternative for risky prompts."""
import re

# (pattern, safe alternative). First match wins - these turn an abusive request into a defensive / educational one.
SAFE_REWRITES = [
    (r"firewalls?", "Explain firewall concepts"),
    (r"ransomware", "Explain how ransomware works and how organisations can defend against it"),
    (r"keylogger|steal\w*\s+(saved\s+)?passwords?|password stealer|info ?stealer", "Explain how credential theft works and how to protect accounts against it"),
    (r"ddos|dos attack|botnet", "Explain what DDoS attacks are and how they are mitigated"),
    (r"phishing", "Explain how to recognise and report phishing emails"),
    (r"wifi|wi-fi|network", "Explain best practices for securing a wifi network"),
    (r"virus|malware|trojan|worm", "Explain how malware spreads and how antivirus software helps prevent it"),
    (r"credit card|debit card", "Explain how card fraud happens and how to protect your cards"),
    (r"password|account|login|authentication", "Explain how authentication works and how to build secure login systems"),
    (r"exfiltrat|data", "Explain how organisations detect and prevent data leaks"),
]
_INJECTION = re.compile(
    r"(ignore|disregard|forget|override|bypass)\b[^.,;]{0,40}\b(instructions?|rules?|prompts?|guidelines?|filters?|restrictions?)"
    r"|(reveal|show|print|repeat|leak|tell me)\b[^.,;]{0,30}\b(system prompt|hidden instructions?|initial instructions?|configuration)"
    r"|\b(you are now|pretend|act as|enable)\b[^.,;]{0,40}\b(dan|developer mode|unfiltered|uncensored|no (ethic\w*|restrictions|moral\w*))"
    r"|\b(without|no)\b[^.,;]{0,15}\b(restrictions?|filters?|limitations?)", re.I)


_PERSONA = re.compile(r"\b(you are now|pretend|act as|roleplay|let's roleplay|enable (developer|god) mode|dan)\b", re.I)


def make_safe_prompt(original: str, normalized: str, categories: set) -> str:
    """Return a safe alternative prompt (the diagram's [SAFE_PROMPT])."""
    if _PERSONA.search(original) and not categories & {"cyber", "fraud"}:
        return "Explain how AI assistants follow safety guidelines and why jailbreak attempts are restricted"
    if categories & {"injection", "jailbreak"} and not categories & {"cyber", "fraud"}:
        remainder = _INJECTION.sub(" ", original)
        remainder = re.sub(r"\b(and|then|now|from now on|dan,?|an ai with)\b", " ", remainder, flags=re.I)
        remainder = re.sub(r"[^\w\s?']", " ", remainder)
        remainder = re.sub(r"\s+", " ", remainder).strip()
        if len(remainder.split()) >= 4:
            return remainder[0].upper() + remainder[1:]
        return "Explain how AI assistants follow instructions and how prompt-injection attacks are prevented"
    for pattern, safe in SAFE_REWRITES:
        if re.search(pattern, normalized):
            return safe
    return "Explain the general concepts and defensive best practices related to this topic"
