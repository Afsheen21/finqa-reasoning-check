# Can a small model get the right answer for the wrong reason? (FinQA pilot)

I wanted to know something simple: when a small language model answers a financial question correctly, is its reasoning actually correct too, or did it get lucky?

So I ran a small experiment. It is a pilot, not a finding, and I say below exactly what it does and doesn't show.

## What I did
- I took 50 questions at random (fixed seed) from the public FinQA test set.
- I ran `Qwen/Qwen2.5-1.5B-Instruct` once on each, with the table, the text and the question, and asked it to think step by step and then write `ANSWER: <number>`.
- I compared each final answer with the gold answer. My script did the first pass by pulling the last number after `ANSWER:`.
- I counted an answer as correct if it rounds to the gold answer at the gold answer's own precision. A wrong sign or wrong units counts as wrong.

## What I found
- The model got **14 of 50 right (28%)**. With only 50 questions that is a wide range: the 95% interval is about 17% to 42%.
- In **4 of those 14**, the model's own arithmetic was wrong, yet the final number still rounded to the gold answer. I recomputed each one myself (`check.py`):

| Question | Model wrote | Recomputed | Gold |
|---|---|---|---|
| 4 | 72.4% | 72.10% | 72% |
| 25 | 52.75% | 52.95% | 53% |
| 39 | 10.87% | 10.84% | 11% |
| 43 | 102.02% | 102.43% | 102% |

These slips were small, all under half a percentage point, so this is not about wild miscalculations. But it does show that matching the gold answer is not proof the reasoning was right. And 4 of 14 is too few to estimate a rate, so I report it as a count, not a percentage.

## What I did not do
- I did not check the reasoning of the other 10 correct answers, so I make no claim about them. They may well contain mistakes I missed.
- I could not check whether the model copied each number from the original table correctly, because the table is not in my labelling sheet. I judged the final answers and the arithmetic only.
- Some calls were judgment calls (signs, units, rounding). Someone else might mark a few differently.

## Limits
One small model, one prompt, one run, 50 questions. I picked a 1.5B model because it runs for free on a Colab T4; a larger model is the obvious next test. This says nothing about bigger models, and nothing about financial models such as Fin-R1. I am treating it as a first look and a question to study properly, not an answer.

## Files
- `generate.py`: runs the model and saves `generations.jsonl`
- `make_sheet.py`: builds `to_judge.csv` with the automatic answer check
- `report.py`: prints the counts and confidence intervals
- `check.py`: recomputes the four arithmetic cases

## Run it yourself
```
pip install torch transformers
python generate.py
python make_sheet.py
python report.py
```
On a laptop CPU the first step was far too slow for me, so I ran it on a free Colab T4 GPU instead.
