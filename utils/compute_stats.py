#!/usr/bin/env python3
import json, math, re, sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "sentences.jsonl"
word_re = re.compile(r"\S+", re.UNICODE)
diacritics = set("áíóúýæøðÁÍÓÚÝÆØÐ")

n = 0
tok_count = 0
char_sum = 0
lengths = []
vocab = Counter()
seen = set()
dup = 0
diac_lines = 0

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        text = obj["text"]
        n += 1
        if text in seen:
            dup += 1
        else:
            seen.add(text)
        toks = word_re.findall(text)
        tok_count += len(toks)
        char_sum += len(text)
        lengths.append(len(toks))
        vocab.update(t.lower() for t in toks)
        if any(ch in diacritics for ch in text):
            diac_lines += 1

def pct(p):
    if not lengths: return 0
    k = (len(lengths)-1) * p
    s = sorted(lengths)
    i, j = math.floor(k), math.ceil(k)
    if i == j: return s[i]
    return s[i] + (s[j]-s[i])*(k-i)

avg_tok = tok_count / n if n else 0
med_tok = pct(0.5)
p5, p95 = pct(0.05), pct(0.95)
avg_char = char_sum / n if n else 0
uniq_ratio = (1 - dup / n) * 100 if n else 0
diac_pct = (diac_lines / n) * 100 if n else 0

# add this later | Unique sentence ratio | {uniq_ratio:.2f}% |
# add this later | Sentences with Faroese diacritics | {diac_pct:.2f}% |

print(f"""| Metric | Value |
|---|---|
| Sentences | {n:,} |
| Tokens (space-split) | {tok_count:,} |
| Types (unique tokens, case-folded) | {len(vocab):,} |
| Avg. sentence length (tokens) | {avg_tok:.2f} |
| Median sentence length (tokens) | {med_tok:.0f} |
| 5-95% sentence length (tokens) | {int(p5)}-{int(p95)} |
| Avg. sentence length (characters) | {avg_char:.1f} |""")
