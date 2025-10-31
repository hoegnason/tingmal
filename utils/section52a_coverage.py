#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# --- your existing pieces (kept intact) ---------------------------------------
NUMBER_PATTERN = re.compile(r"52-(\d+)-\d+\.xml")

def match_number_part(string) -> Optional[int]:
    m = NUMBER_PATTERN.search(str(string))
    return int(m.group(1)) if m else None

# Official yearly totals (§52a)
SECTION_52A_QUESTION_STATS: Dict[int, int] = {
    2008: 39, 2009: 115, 2010: 85, 2011: 46, 2012: 60, 2013: 66,
    2014: 108, 2015: 71, 2016: 100, 2017: 86, 2018: 88, 2019: 120,
    2020: 169, 2021: 222, 2022: 135, 2023: 141, 2024: 119
}

YEARS = list(range(2008, 2025))

def xml_files(dirpath: str):
    # Minimal local implementation; replace with your `export_ids.xml_files` if preferred.
    root = Path(dirpath)
    if not root.exists():
        return []
    return sorted([str(p) for p in root.glob("*.xml")])

# --- stats & gaps --------------------------------------------------------------
def per_year_counts(base_dir: str = "parliamentary-questions") -> Dict[int, int]:
    results: Dict[int, int] = {}
    for y in YEARS:
        results[y] = len(list(xml_files(os.path.join(base_dir, str(y)))))
    return results

def find_gaps_for_year(year: int, base_dir: str = "parliamentary-questions") -> List[Tuple[int, int]]:
    files = xml_files(os.path.join(base_dir, str(year)))
    nums = sorted(filter(None, (match_number_part(f) for f in files)))
    gaps: List[Tuple[int, int]] = []
    if not nums:
        return gaps
    prev = nums[0]
    for n in nums[1:]:
        if n - prev > 1:
            gaps.append((prev + 1, n - 1))
        prev = n
    return gaps

def compute_coverage(base_dir: str = "parliamentary-questions"):
    per_year = per_year_counts(base_dir)
    rows = []
    total_official = sum(SECTION_52A_QUESTION_STATS[y] for y in YEARS)
    total_collected = 0
    for y in YEARS:
        collected = per_year.get(y, 0)
        official = SECTION_52A_QUESTION_STATS[y]
        coverage = (collected / official * 100) if official else 0.0
        missing = max(0, official - collected)
        total_collected += collected
        rows.append({
            "year": y,
            "collected": collected,
            "official": official,
            "coverage_pct": round(coverage, 1),
            "missing": missing,
            "gaps": find_gaps_for_year(y, base_dir),
        })
    overall_pct = round(total_collected / total_official * 100, 1) if total_official else 0.0
    return rows, total_collected, total_official, overall_pct

def render_markdown(rows, total_collected, total_official, overall_pct) -> str:
    header = (
        "| Year | Collected | Official total | Coverage | Missing |\n"
        "|:----:|----------:|---------------:|---------:|--------:|\n"
    )
    body = "\n".join(
        f"| {r['year']} | {r['collected']:>9} | {r['official']:>14} | {r['coverage_pct']:>7.1f}% | {r['missing']:>7} |"
        for r in rows
    )
    footer = f"\n\n**Totals:** Collected **{total_collected:,}** of **{total_official:,}** (overall coverage **{overall_pct:.1f}%**)\n"
    return header + body + footer

def main():
    rows, total_c, total_o, overall = compute_coverage()
    # Markdown table for README injection
    md = render_markdown(rows, total_c, total_o, overall)
    Path("PQ_STATS.md").write_text(md, encoding="utf-8")
    # Machine-readable JSON for downstream checks
    out = {
        "by_year": rows,
        "totals": {
            "collected": total_c,
            "official": total_o,
            "coverage_pct": overall
        }
    }
    Path("PQ_STATS.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    # Also log gaps to stdout for CI visibility
    for r in rows:
        if r["gaps"]:
            print(f"[GAPS] {r['year']}: missing ranges {r['gaps']}")

if __name__ == "__main__":
    main()
