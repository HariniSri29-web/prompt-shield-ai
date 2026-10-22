"""Generate the dataset, compare Logistic Regression vs SVM, and save the chosen model."""
import argparse
from prompt_shield.dataset import write_csv
from prompt_shield.classifier import train

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["logreg", "svm"], default="logreg", help="model to save")
    ap.add_argument("--regen-data", action="store_true", help="regenerate data/prompts.csv")
    args = ap.parse_args()
    if args.regen_data:
        print("Wrote", write_csv(), "rows to data/prompts.csv")
    other = "svm" if args.model == "logreg" else "logreg"
    train(other, save=False)          # comparison only
    train(args.model, save=True)      # model that gets saved
    print(f"\nSaved {args.model} model.")
