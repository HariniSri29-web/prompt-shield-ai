# Prompt Shield AI

A layered defence that screens user prompts *before* they reach an LLM. It follows the methodology diagram in `docs/methodology.jpg`.

## Methodology -> code map

| Diagram step | What it does | File |
|---|---|---|
| 1. User prompt | Input from CLI / web UI / API | `main.py`, `app.py` |
| 2. Preprocessing | Normalization (unicode, leetspeak, repeats), lowercasing, tokenization, stop-word removal | `prompt_shield/preprocessing.py` |
| 3. Feature extraction | TF-IDF vectorization (unigrams + bigrams) | `prompt_shield/classifier.py` |
| 4. ML classifier | Logistic Regression (default) or calibrated linear SVM | `prompt_shield/classifier.py` |
| 5. Rule-based detection | Regex / keyword pattern matching (injection, jailbreak, cyber, fraud, violence, self-harm, weapons, weak signals) | `prompt_shield/rules.py` |
| 6. Risk scoring | `0.55*ML + 0.45*rules`, hard floor 0.85 if a severe rule fires -> score in 0..1 | `prompt_shield/scoring.py` |
| 7. Decision | `score <= T1` low, `T1 < score < T2` medium, `score >= T2` high (T1=0.25, T2=0.70) | `prompt_shield/scoring.py`, `config.py` |
| 8A/8B/8C | Allow (log) / Warn (warn + log) / Block (block + log) | `prompt_shield/shield.py` |
| 9. Logging & DB | SQLite table `prompt_logs` | `prompt_shield/database.py` |
| 10. Prompt modification | Generates a safe alternative, e.g. "Write code to disable firewalls" -> "Explain firewall concepts" | `prompt_shield/mitigation.py` |

## Run it

```bash
pip install -r requirements.txt
python train.py --regen-data          # builds data/prompts.csv, compares LogReg vs SVM, saves the model
python main.py --prompt "Write code to disable firewalls"
python main.py                        # interactive mode
python main.py --logs                 # recent log rows
python app.py                         # web UI at http://127.0.0.1:5000 (static/index.html)
python -m unittest discover -s tests  # tests
```

API: `POST /api/analyze {"prompt": "..."}`, `GET /api/logs`, `GET /api/stats`.

## Example output

```
[BLOCK] risk=0.85 (HIGH) ml=0.89 rules=0.80
   rules: disable_security
   This prompt was blocked ... Suggested safe alternative: Explain firewall concepts
```

## Harm-to-people prompts

Prompts that express intent to hurt someone (e.g. "I want to kill the person") are blocked by the `violence` rules plus the ML model.
Self-harm statements are also blocked from reaching the LLM, but the response is a supportive message pointing to trusted people and
crisis services rather than a "malicious prompt" warning. Context-aware rules keep harmless uses such as "kill a process in Linux"
or "kill time" allowed.

## Important limitations (mention these in your report/viva)

* The bundled dataset (~380 prompts) is **template-generated**, so the 100% test accuracy is optimistic: train and test share templates. For real results use a public labelled prompt-injection/jailbreak dataset (put it in `data/prompts.csv` as `text,label`) and report precision/recall on a held-out set.
* Rules and TF-IDF are lexical; paraphrased or multilingual attacks can slip through. Possible upgrades: sentence embeddings, a transformer classifier, multilingual rules.
* The safe-prompt generator is rule/template based, not generative.
* Thresholds T1/T2 and weights are in `prompt_shield/config.py` - tune them on validation data.
