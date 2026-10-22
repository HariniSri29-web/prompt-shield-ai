"""Central configuration (thresholds, weights, paths)."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "prompts.csv"
MODEL_PATH = BASE_DIR / "models" / "classifier.joblib"
DB_PATH = BASE_DIR / "logs" / "prompt_shield.db"

# Step 7 - threshold based decision
T1 = 0.25   # score <= T1        -> LOW risk    (allow)
T2 = 0.70   # T1 < score < T2    -> MEDIUM risk (warn)
            # score >= T2        -> HIGH risk   (block)

# Step 6 - risk scoring: weighted blend of ML probability and rule score
W_ML = 0.55
W_RULE = 0.45
# If a rule of at least this severity fires, the final score is floored at HARD_RULE_FLOOR
HARD_RULE_SEVERITY = 0.90
HARD_RULE_FLOOR = 0.85

DEFAULT_MODEL = "logreg"   # "logreg" or "svm"
RANDOM_STATE = 42
