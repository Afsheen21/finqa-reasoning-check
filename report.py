"""Step 3: after you filled the sheet, compute the numbers with 95% Wilson confidence intervals."""
import csv, math
def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return c - h, c + h
rows = list(csv.DictReader(open("to_judge.csv", encoding="utf-8-sig")))
def val(r):  # your check overrides the automatic one
    v = r["answer_correct_YOU_CHECK"].strip() or r["answer_correct_auto"].strip()
    return v
judged = [r for r in rows if r["chain_ok_YOU_FILL"].strip() in ("0", "1")]
correct = [r for r in rows if val(r) == "1"]
cj = [r for r in correct if r["chain_ok_YOU_FILL"].strip() in ("0", "1")]
flawed = [r for r in cj if r["chain_ok_YOU_FILL"].strip() == "0"]
lo, hi = wilson(len(correct), len(rows))
print(f"Questions: {len(rows)}")
print(f"Final answer correct: {len(correct)}/{len(rows)} = {len(correct)/len(rows):.2f}  (95% CI {lo:.2f}-{hi:.2f})")
lo, hi = wilson(len(flawed), len(cj))
print(f"Of correct answers with chain judged: {len(flawed)}/{len(cj)} had a FLAWED chain = "
      f"{(len(flawed)/len(cj) if cj else float('nan')):.2f}  (95% CI {lo:.2f}-{hi:.2f})")
if len(cj) < len(correct): print("WARNING: you have not judged every correct answer's chain yet.")
