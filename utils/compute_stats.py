#!/usr/bin/env python3
import json, math, re, sys
from collections import Counter, defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else "sentences.jsonl"
word_re = re.compile(r"\S+", re.UNICODE)
diacritics = set("áíóúýæøðÁÍÓÚÝÆØÐ")

# Overall statistics
n = 0
tok_count = 0
char_sum = 0
lengths = []
vocab = Counter()
seen = set()
dup = 0
diac_lines = 0

# Per-year statistics
year_stats = defaultdict(lambda: {
    'n': 0,
    'tok_count': 0,
    'char_sum': 0,
    'lengths': [],
    'vocab': Counter(),
    'seen': set(),
    'dup': 0,
    'diac_lines': 0
})

# Unknown year statistics
unknown_stats = {
    'n': 0,
    'tok_count': 0,
    'char_sum': 0,
    'lengths': [],
    'vocab': Counter(),
    'seen': set(),
    'dup': 0,
    'diac_lines': 0
}

# Per-decade statistics
decade_stats = defaultdict(lambda: {
    'n': 0,
    'tok_count': 0,
    'char_sum': 0,
    'lengths': [],
    'vocab': Counter(),
    'seen': set(),
    'dup': 0,
    'diac_lines': 0
})

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        text = obj["text"]
        year = obj.get("year")  # May be None

        # Overall stats
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

        # Per-year stats
        if year is not None:
            ys = year_stats[year]
            ys['n'] += 1
            if text in ys['seen']:
                ys['dup'] += 1
            else:
                ys['seen'].add(text)
            ys['tok_count'] += len(toks)
            ys['char_sum'] += len(text)
            ys['lengths'].append(len(toks))
            ys['vocab'].update(t.lower() for t in toks)
            if any(ch in diacritics for ch in text):
                ys['diac_lines'] += 1

            # Per-decade stats
            decade = (year // 10) * 10
            ds = decade_stats[decade]
            ds['n'] += 1
            if text in ds['seen']:
                ds['dup'] += 1
            else:
                ds['seen'].add(text)
            ds['tok_count'] += len(toks)
            ds['char_sum'] += len(text)
            ds['lengths'].append(len(toks))
            ds['vocab'].update(t.lower() for t in toks)
            if any(ch in diacritics for ch in text):
                ds['diac_lines'] += 1
        else:
            # Unknown year
            unknown_stats['n'] += 1
            if text in unknown_stats['seen']:
                unknown_stats['dup'] += 1
            else:
                unknown_stats['seen'].add(text)
            unknown_stats['tok_count'] += len(toks)
            unknown_stats['char_sum'] += len(text)
            unknown_stats['lengths'].append(len(toks))
            unknown_stats['vocab'].update(t.lower() for t in toks)
            if any(ch in diacritics for ch in text):
                unknown_stats['diac_lines'] += 1

def pct(lengths_list, p):
    if not lengths_list: return 0
    k = (len(lengths_list)-1) * p
    s = sorted(lengths_list)
    i, j = math.floor(k), math.ceil(k)
    if i == j: return s[i]
    return s[i] + (s[j]-s[i])*(k-i)

# Overall statistics
avg_tok = tok_count / n if n else 0
med_tok = pct(lengths, 0.5)
p5, p95 = pct(lengths, 0.05), pct(lengths, 0.95)
avg_char = char_sum / n if n else 0
uniq_ratio = (1 - dup / n) * 100 if n else 0
diac_pct = (diac_lines / n) * 100 if n else 0

# add this later | Unique sentence ratio | {uniq_ratio:.2f}% |
# add this later | Sentences with Faroese diacritics | {diac_pct:.2f}% |

print("## Overall Statistics\n")
print(f"""| Metric | Value |
|---|---|
| Sentences | {n:,} |
| Tokens (space-split) | {tok_count:,} |
| Types (unique tokens, case-folded) | {len(vocab):,} |
| Avg. sentence length (tokens) | {avg_tok:.2f} |
| Median sentence length (tokens) | {med_tok:.0f} |
| 5-95% sentence length (tokens) | {int(p5)}-{int(p95)} |
| Avg. sentence length (characters) | {avg_char:.1f} |""")

# Per-year statistics
if year_stats or unknown_stats['n'] > 0:
    print("\n## Statistics by Year\n")
    print("| Year | Sentences | % of Total | Tokens | Types | Avg. Length (tokens) | Avg. Length (chars) |")
    print("|---|---|---|---|---|---|---|")

    for year in sorted(year_stats.keys()):
        ys = year_stats[year]
        y_avg_tok = ys['tok_count'] / ys['n'] if ys['n'] else 0
        y_avg_char = ys['char_sum'] / ys['n'] if ys['n'] else 0
        y_pct = (ys['n'] / n * 100) if n else 0
        print(f"| {year} | {ys['n']:,} | {y_pct:.2f}% | {ys['tok_count']:,} | {len(ys['vocab']):,} | {y_avg_tok:.2f} | {y_avg_char:.1f} |")

    # Add Unknown row if there are sentences without year
    if unknown_stats['n'] > 0:
        u_avg_tok = unknown_stats['tok_count'] / unknown_stats['n'] if unknown_stats['n'] else 0
        u_avg_char = unknown_stats['char_sum'] / unknown_stats['n'] if unknown_stats['n'] else 0
        u_pct = (unknown_stats['n'] / n * 100) if n else 0
        print(f"| Unknown | {unknown_stats['n']:,} | {u_pct:.2f}% | {unknown_stats['tok_count']:,} | {len(unknown_stats['vocab']):,} | {u_avg_tok:.2f} | {u_avg_char:.1f} |")

# Per-decade statistics
if decade_stats:
    print("\n## Statistics by Decade\n")
    print("| Decade | Sentences | % of Total | Tokens | Types | Avg. Length (tokens) | Avg. Length (chars) |")
    print("|---|---|---|---|---|---|---|")

    for decade in sorted(decade_stats.keys()):
        ds = decade_stats[decade]
        d_avg_tok = ds['tok_count'] / ds['n'] if ds['n'] else 0
        d_avg_char = ds['char_sum'] / ds['n'] if ds['n'] else 0
        d_pct = (ds['n'] / n * 100) if n else 0
        decade_label = f"{decade}s"
        print(f"| {decade_label} | {ds['n']:,} | {d_pct:.2f}% | {ds['tok_count']:,} | {len(ds['vocab']):,} | {d_avg_tok:.2f} | {d_avg_char:.1f} |")

    # Add Unknown row for decade table if there are sentences without year
    if unknown_stats['n'] > 0:
        u_avg_tok = unknown_stats['tok_count'] / unknown_stats['n'] if unknown_stats['n'] else 0
        u_avg_char = unknown_stats['char_sum'] / unknown_stats['n'] if unknown_stats['n'] else 0
        u_pct = (unknown_stats['n'] / n * 100) if n else 0
        print(f"| Unknown | {unknown_stats['n']:,} | {u_pct:.2f}% | {unknown_stats['tok_count']:,} | {len(unknown_stats['vocab']):,} | {u_avg_tok:.2f} | {u_avg_char:.1f} |")
