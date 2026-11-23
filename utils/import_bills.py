#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2026 Rani Høgnason Hansen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Copy bills extracted by bill_extractor into proposals/.

Every SOURCE/<YEAR>/*.xml is copied byte for byte to proposals/<YEAR>/, unless

  - a file with the same name is already somewhere under proposals/ (a bill
    that is in the corpus is never overwritten);
  - it has no <s> elements (a failed extraction);
  - it has more <s cert="low"> than --max-low, or more <s cert="medium"> than
    --max-medium.

Every bill is listed with what happens to it and why.

The copies are exactly what bill_extractor wrote. Stage them with git add
(after export_ids.py and add_person_refs.py, which rewrite them) before editing
by hand, and git diff shows only the edits.

Nothing is written unless --write is given.

usage: python3 utils/import_bills.py [--max-low N] [--max-medium N] [--write] [-s SOURCE] [YEAR ...]
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

PROPOSALS_PATH = REPO_ROOT / "proposals"
SOURCE_PATH = REPO_ROOT.parent / "bill_extractor" / "output"

S = "{http://www.tei-c.org/ns/1.0}s"


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy bills extracted by bill_extractor into proposals/.")
    parser.add_argument('--max-low', type=int, metavar='N', help='Skip bills with more than N <s cert="low">')
    parser.add_argument('--max-medium', type=int, metavar='N', help='Skip bills with more than N <s cert="medium">')
    parser.add_argument('-w', '--write', action='store_true', help='Copy the files (default: only show what would be copied)')
    parser.add_argument('-s', '--source', type=Path, default=SOURCE_PATH, help='bill_extractor output folder (default: ../bill_extractor/output)')
    parser.add_argument("years", nargs='*', metavar='YEAR', help='Only these year folders (default: all)')
    args = parser.parse_args()

    if not args.source.is_dir():
        sys.exit(f"error: {args.source} is not a folder")

    for year in args.years:
        if not year.isdigit() or not (args.source / year).is_dir():
            sys.exit(f"error: no year folder {year} in {args.source}")

    years = sorted(set(args.years)) or sorted(d.name for d in args.source.iterdir() if d.is_dir() and d.name.isdigit())
    limits = {"low": args.max_low, "medium": args.max_medium}

    # by file name, wherever it is filed: a bill under the wrong year folder is not imported a second time
    existing = {path.name: path for path in PROPOSALS_PATH.rglob("*.xml")}

    outcomes = Counter()

    for year in years:
        for path in sorted((args.source / year).glob("*.xml")):
            name = f"{year}/{path.name}"

            if path.name in existing:
                found = existing[path.name].relative_to(PROPOSALS_PATH).as_posix()
                print(f"exists  {name}" + ("" if found == name else f" (at proposals/{found})"))
                outcomes["exists"] += 1
                continue

            try:
                raw = path.read_bytes()
                counts = Counter(s.get("cert") for s in etree.fromstring(raw).iter(S))
            except (OSError, etree.XMLSyntaxError) as exc:
                print(f"skipped {name}: {exc}", file=sys.stderr)
                outcomes["unreadable"] += 1
                continue

            total = sum(counts.values())
            other = total - counts["high"] - counts["medium"] - counts["low"]
            detail = f"{total} sentences, {counts['low']} low, {counts['medium']} medium"

            if other:
                detail += f", {other} with other or no cert"

            over = [f"{cert} > {limit}" for cert, limit in limits.items() if limit is not None and counts[cert] > limit]

            if total == 0:
                print(f"skip    {name}: no sentences")
                outcomes["empty"] += 1
            elif over:
                print(f"skip    {name}: {detail} ({', '.join(over)})")
                outcomes["filtered"] += 1
            else:
                print(f"copy    {name}: {detail}")
                outcomes["copy"] += 1

                if args.write:
                    target = PROPOSALS_PATH / year / path.name
                    target.parent.mkdir(exist_ok=True)

                    # "x" fails if the file exists, so nothing can be overwritten
                    with open(target, "xb") as file:
                        file.write(raw)

    in_force = ", ".join(f"max {limit} {cert}" for cert, limit in limits.items() if limit is not None) or "no limits"

    print(
        f"\n{sum(outcomes.values())} bills checked: {outcomes['copy']} {'copied' if args.write else 'to copy'}, "
        f"{outcomes['exists']} already in proposals/, {outcomes['filtered']} over the limits ({in_force}), "
        f"{outcomes['empty']} without sentences, {outcomes['unreadable']} unreadable"
    )

    if outcomes["copy"] and not args.write:
        print("Nothing was written, run again with --write to copy the files.")


if __name__ == "__main__":
    main()
