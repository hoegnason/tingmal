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

"""Map person names to tingdata.fo person references.

Scans every <persName ref="https://tingdata.fo/person/..."> in proposals/ and
parliamentary-questions/ and writes a JSON object {name: reference}, sorted by
name, to utils/person_refs.json. Every spelling that occurs with a reference
becomes a key.

A name that occurs with more than one reference is reported on stderr; the most
frequent reference is used. Such a conflict is an error in the XML and should be
corrected there.

usage: python3 utils/export_person_refs.py [-o OUTPUT]
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FOLDERS = ("proposals", "parliamentary-questions")
OUTPUT_PATH = SCRIPT_DIR / "person_refs.json"

PERS_NAME = "{http://www.tei-c.org/ns/1.0}persName"
REF_PATTERN = re.compile(r"https://tingdata\.fo/person/[a-z2-7]{8}")


def _name_parts(element):
    """Yield the text inside element, leaving out <roleName> and comments."""
    yield element.text or ""

    for child in element:
        # comments and processing instructions have a non-string tag
        if isinstance(child.tag, str) and etree.QName(child).localname.lower() != "rolename":
            yield from _name_parts(child)

        yield child.tail or ""


def clean_name(pers_name) -> str:
    """Return the name in a <persName> element as it is used as a key in the mapping.

    The role is left out, whitespace is collapsed and punctuation at either end is
    removed, so 'Jenis av Rana, <roleName>løgtingsmaður</roleName>' gives 'Jenis av Rana'.
    """
    text = " ".join("".join(_name_parts(pers_name)).split())

    return text.strip(" ,.;:")


def warn(message: str) -> None:
    print(message, file=sys.stderr)


def collect(folders):
    """Return ({name: Counter of refs}, {(name, ref): [locations]}, number of files)."""
    refs_by_name = defaultdict(Counter)
    locations = defaultdict(list)
    file_count = 0

    for folder in folders:
        for path in sorted(folder.rglob("*.xml")):
            file_count += 1

            try:
                root = etree.parse(str(path)).getroot()
            except (etree.XMLSyntaxError, OSError) as exc:
                warn(f"warning: skipped {path}: {exc}")
                continue

            for pers_name in root.iter(PERS_NAME):
                ref = (pers_name.get("ref") or "").strip()

                if not ref:
                    continue

                try:
                    shown_path = path.relative_to(REPO_ROOT)
                except ValueError:
                    shown_path = path

                location = f"{shown_path}:{pers_name.sourceline}"

                if not REF_PATTERN.fullmatch(ref):
                    warn(f"warning: {location}: unexpected ref \"{ref}\", skipped")
                    continue

                name = clean_name(pers_name)

                if not name:
                    warn(f"warning: {location}: persName has a ref but no name, skipped")
                    continue

                refs_by_name[name][ref] += 1
                locations[(name, ref)].append(location)

    return refs_by_name, locations, file_count


def build_mapping(refs_by_name, locations):
    """Return ({name: ref}, number of conflicts); conflicts are reported on stderr."""
    mapping = {}
    conflict_count = 0

    for name in sorted(refs_by_name):
        ranked = refs_by_name[name].most_common()
        best_ref, best_count = ranked[0]

        if len(ranked) == 1:
            mapping[name] = best_ref
            continue

        conflict_count += 1
        tied = ranked[1][1] == best_count

        if tied:
            warn(f"conflict: \"{name}\" is left out, no reference is more frequent than the others:")
        else:
            mapping[name] = best_ref
            warn(f"conflict: \"{name}\" has more than one reference, using {best_ref}:")

        for ref, count in ranked:
            warn(f"  {ref} ({count})")

            if tied or ref != best_ref:
                for location in locations[(name, ref)]:
                    warn(f"    {location}")

    return mapping, conflict_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Map person names to tingdata.fo person references found in proposals/ and parliamentary-questions/."
    )
    parser.add_argument('-o', '--output', type=Path, default=OUTPUT_PATH, help='Output file (default: utils/person_refs.json)')
    args = parser.parse_args()

    refs_by_name, locations, file_count = collect([REPO_ROOT / folder for folder in FOLDERS])
    mapping, conflict_count = build_mapping(refs_by_name, locations)

    args.output.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"{file_count} files scanned: {len(mapping)} names for {len(set(mapping.values()))} persons, "
        f"{conflict_count} conflicts, written to {args.output}"
    )


if __name__ == "__main__":
    main()
