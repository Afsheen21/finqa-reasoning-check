"""Step 2: auto-check final answers and write a CSV for YOU to judge the reasoning by hand."""
import json, re, csv

def last_number(text):
    m = re.search(r"ANSWER:\s*(.*)", text, re.I | re.S)
    seg = m.group(1) if m else text.strip().splitlines()[-1] if text.strip() else ""
    nums = re.findall(r"-?\d[\d,]*\.?\d*", seg)
    if not nums: return None
    try: return float(nums[0].replace(",", ""))
    except ValueError: return None

def close(x, g):
    return abs(x - g) <= max(0.01 * abs(g), 0.005)

rows = []
for line in open("generations.jsonl", encoding="utf-8"):
    r = json.loads(line)
    pred = last_number(r["output"])
    g = r["gold_exe"]
    ok = ""
    if pred is not None and isinstance(g, (int, float)):
        ok = int(any(close(pred, v) for v in (g, g * 100, g / 100)))   # percent vs fraction
    rows.append({"id": r["id"], "question": r["question"], "gold_answer": r["gold_answer"],
                 "gold_number": g, "model_number": pred, "answer_correct_auto": ok,
                 "answer_correct_YOU_CHECK": "", "chain_ok_YOU_FILL": "",
                 "model_output": r["output"].replace("\n", " ⏎ ")})
with open("to_judge.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("Wrote to_judge.csv with", len(rows), "rows. Now open it and fill the two YOU columns.")
