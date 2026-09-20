#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2025 Rani Høgnason Hansen
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

import argparse
import json
from pathlib import Path
from collections import defaultdict

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent

SCHEMA_PATH = SCRIPT_DIR / ".." / "schemas" / "tei_all.rng"

def clean_up_error_type(input: str) -> str:
    return input.replace("RELAXNG_ERR_", "")

def validate_file(schema: etree.RelaxNG, path: Path) -> dict:
    try:
        document = etree.parse(path)
    except etree.XMLSyntaxError as exc:
        return {
            "path": str(path),
            "valid": False,
            "issues": [
                {
                    # "source": "xml",
                    "type": "XML",
                    "line": error.line,
                    # "column": error.column, TODO: only show column if not equal to zero
                    "msg": error.message,
                }
                for error in exc.error_log
            ],
        }

    valid = schema.validate(document)

    return {
        "path": str(path),
        "valid": valid,
        "issues": [
            {
                # "source": "relaxng",
                "line": error.line,
                # "column": error.column, TODO: only show column if not equal to zero
                "type": clean_up_error_type(error.type_name),
                "msg": error.message,
            }
            for error in schema.error_log
        ],
    }


def number_of_issue_types(item) -> int:
    error_type_counts = defaultdict(int)

    for issue in item["issues"]:
        type_name = issue["type"]
        error_type_counts[type_name] += 1

    return len(error_type_counts)


def number_of_line_issues(item) -> int:
    line_number_set = set()

    for issue in item["issues"]:
        line_number_set.add(issue["line"])

    return len(line_number_set)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--minimal', action='store_true', help='Minimal output (show only failing files)')
    parser.add_argument('-s', '--sorted', action='store_true', help='Sort output by number of different issues and problematic lines')
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    minimal = args.minimal
    sort_by_issues_then_problematic_lines = args.sorted

    schema = etree.RelaxNG(file=str(SCHEMA_PATH))

    valid_count = 0
    invalid_count = 0

    results = []

    files = []

    if args.root.is_file():
        files.append(args.root)
    else:
        files = sorted(args.root.rglob("*.xml"))

    for path in files:
        result = validate_file(schema, path)

        if (minimal and not result["valid"]) or not minimal:
            results.append(result)

        # print(json.dumps(result, ensure_ascii=False))

        if result["valid"]:
            valid_count += 1
        else:
            invalid_count += 1

        if minimal:
            del result["valid"]

    error_type_counts = defaultdict(int)

    for item in results:
        for issue in item["issues"]:
            type_name = issue["type"]
            error_type_counts[type_name] += 1

    if sort_by_issues_then_problematic_lines:
        results.sort(key=lambda x: (-number_of_issue_types(x), -number_of_line_issues(x), x["path"]))

    print(
        json.dumps(
            {
                "type": "summary",
                "stats": {
                    "valid_files": valid_count,
                    "invalid_files": invalid_count,
                    "total_files": valid_count + invalid_count,
                    "error_types": error_type_counts,
                },
                "results": results
            }
        )
    )


if __name__ == "__main__":
    main()