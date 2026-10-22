"""Step 2 - Preprocessing (NLP techniques): normalization, tokenization, lowercasing, stop-word removal."""
import re
import unicodedata

# Negations and words that carry attack meaning (ignore, previous, all, without...) are deliberately NOT stop words.
STOP_WORDS = frozenset("""
a an the is are was were be been am to of in on at for and or with by from as it its this that these those
me my mine i we our us your yours please can could would will shall just so then than also
""".split())

_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "!": "i"})


def normalize(text: str) -> str:
    """Normalization: unicode folding, zero-width removal, leetspeak decoding, repeated-char and whitespace collapse."""
    text = unicodedata.normalize("NFKC", text).translate(_ZERO_WIDTH)
    text = text.lower()
    # decode leetspeak only inside words that mix letters and symbols/digits (keeps plain numbers like "2024" intact)
    def _fix(m):
        word = m.group(0)
        return word.translate(_LEET) if re.search(r"[a-z]", word) else word
    text = re.sub(r"[a-z0-9@$]+", _fix, text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)          # "pleeeease" -> "pleease"
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list:
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text)


def remove_stop_words(tokens: list) -> list:
    return [t for t in tokens if t not in STOP_WORDS]


def preprocess(text: str) -> dict:
    """Run the full pipeline and return every intermediate form (useful for logging / UI)."""
    normalized = normalize(text)
    tokens = tokenize(normalized)
    filtered = remove_stop_words(tokens)
    return {"normalized": normalized, "tokens": tokens, "filtered_tokens": filtered, "clean_text": " ".join(filtered)}
