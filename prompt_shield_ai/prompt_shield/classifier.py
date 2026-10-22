"""Steps 3 & 4 - TF-IDF feature extraction + Machine Learning classifier (Logistic Regression / SVM)."""
import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from .config import DEFAULT_MODEL, MODEL_PATH, RANDOM_STATE
from .dataset import load_csv
from .preprocessing import preprocess


def build_pipeline(model_type: str = DEFAULT_MODEL) -> Pipeline:
    tfidf = TfidfVectorizer(token_pattern=r"\S+", ngram_range=(1, 2), sublinear_tf=True, min_df=1)   # Step 3
    if model_type == "svm":      # SVM + probability calibration so we can get a 0..1 score
        clf = CalibratedClassifierCV(LinearSVC(C=1.0, class_weight="balanced"), cv=3)
    else:
        clf = LogisticRegression(C=5.0, class_weight="balanced", max_iter=1000, random_state=RANDOM_STATE)
    return Pipeline([("tfidf", tfidf), ("clf", clf)])                                                  # Step 4


def train(model_type: str = DEFAULT_MODEL, save: bool = True, verbose: bool = True) -> dict:
    texts, labels = load_csv()
    clean = [preprocess(t)["clean_text"] for t in texts]
    X_tr, X_te, y_tr, y_te = train_test_split(clean, labels, test_size=0.25, stratify=labels, random_state=RANDOM_STATE)
    pipe = build_pipeline(model_type).fit(X_tr, y_tr)
    pred = pipe.predict(X_te)
    report = classification_report(y_te, pred, target_names=["safe", "malicious"], output_dict=True)
    if verbose:
        print(f"== {model_type.upper()} ==")
        print(classification_report(y_te, pred, target_names=["safe", "malicious"]))
        print("Confusion matrix [[TN FP],[FN TP]]:\n", confusion_matrix(y_te, pred))
    if save:
        pipe = build_pipeline(model_type).fit(clean, labels)       # final model uses all data
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipe, MODEL_PATH)
    return report


class PromptClassifier:
    def __init__(self, model_type: str = DEFAULT_MODEL):
        if not MODEL_PATH.exists():
            train(model_type, save=True, verbose=False)
        self.pipe = joblib.load(MODEL_PATH)

    def malicious_probability(self, clean_text: str) -> float:
        return float(self.pipe.predict_proba([clean_text])[0][1])
