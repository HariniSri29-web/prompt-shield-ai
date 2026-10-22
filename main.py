"""Command line interface for Prompt Shield AI."""
import argparse
import json
from prompt_shield import PromptShield

ICON = {"ALLOW": "[ALLOW]", "WARN": "[WARN] ", "BLOCK": "[BLOCK]"}


def show(r, verbose=False):
    print(f"{ICON[r['action']]} risk={r['risk_score']:.2f} ({r['risk_level']}) ml={r['ml_score']:.2f} rules={r['rule_score']:.2f}")
    if r["matched_rules"]:
        print("   rules:", ", ".join(m["rule"] for m in r["matched_rules"]))
    if r["action"] != "ALLOW":
        print("  ", r["message"])
    if verbose:
        print(json.dumps(r, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Prompt Shield AI")
    ap.add_argument("--prompt", help="analyze one prompt and exit")
    ap.add_argument("--model", choices=["logreg", "svm"], default="logreg")
    ap.add_argument("--json", action="store_true", help="print full JSON result")
    ap.add_argument("--logs", action="store_true", help="show recent log entries")
    args = ap.parse_args()
    shield = PromptShield(args.model)
    if args.logs:
        for row in shield.db.recent(20):
            print(row["timestamp"], row["action"], row["risk_score"], "|", row["original_prompt"][:70])
    elif args.prompt:
        show(shield.analyze(args.prompt), args.json)
    else:
        print("Prompt Shield AI - type a prompt (empty line to quit)")
        while True:
            p = input("\n> ").strip()
            if not p:
                break
            show(shield.analyze(p), args.json)
