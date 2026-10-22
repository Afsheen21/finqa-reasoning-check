"""Step 1: run a small open model on 50 FinQA test questions and save its answers.
Usage:  python 01_generate.py            (downloads FinQA test.json from GitHub)
        python 01_generate.py --model Qwen/Qwen2.5-1.5B-Instruct --n 50
"""
import argparse, json, random, urllib.request, os, re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

URL = "https://raw.githubusercontent.com/czyssrs/FinQA/main/dataset/test.json"
ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
ap.add_argument("--n", type=int, default=50)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()

if not os.path.exists("finqa_test.json"):
    print("Downloading FinQA test set ...")
    urllib.request.urlretrieve(URL, "finqa_test.json")
data = json.load(open("finqa_test.json", encoding="utf-8"))
random.Random(a.seed).shuffle(data)          # fixed seed: same 50 questions every run
sample = data[: a.n]

def table_text(t):
    return "\n".join(" | ".join(str(c) for c in row) for row in t)

def build_prompt(ex):
    pre = " ".join(ex.get("pre_text", []))
    post = " ".join(ex.get("post_text", []))
    return (f"{pre}\n\nTable:\n{table_text(ex['table'])}\n\n{post}\n\n"
            f"Question: {ex['qa']['question']}\n\n"
            "Think step by step, showing each calculation. Then give the final answer "
            "on its own last line in the form:  ANSWER: <number>")

dev = "cuda" if torch.cuda.is_available() else "cpu"
print("Device:", dev, "| Model:", a.model)
tok = AutoTokenizer.from_pretrained(a.model)
model = AutoModelForCausalLM.from_pretrained(
    a.model, torch_dtype=torch.float16 if dev == "cuda" else torch.float32).to(dev)

out = open("generations.jsonl", "w", encoding="utf-8")
for i, ex in enumerate(sample):
    msgs = [{"role": "user", "content": build_prompt(ex)}]
    text_in = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = tok(text_in, return_tensors="pt").to(dev)
    with torch.no_grad():
        gen = model.generate(**inputs, max_new_tokens=450, do_sample=False)
    text = tok.decode(gen[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    rec = {"id": ex["id"], "question": ex["qa"]["question"],
           "gold_answer": ex["qa"].get("answer"), "gold_exe": ex["qa"].get("exe_ans"),
           "program": ex["qa"].get("program"), "output": text}
    out.write(json.dumps(rec) + "\n"); out.flush()
    print(f"{i+1}/{len(sample)} done")
print("Saved generations.jsonl")
