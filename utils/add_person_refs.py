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

"""Add tingdata.fo person references to <persName> elements.

Looks every name up in utils/person_refs.json (see export_person_refs.py) and

  - fills <persName ref=""> where the reference is empty;
  - with --signatures, also adds a reference to a <persName> without a ref
    attribute directly inside <signed>.

A reference that is already filled in is never changed, and a name that is not
in the mapping is left as it is and listed. Only the <persName> start tags are
rewritten, the rest of the file stays byte for byte the same.

Nothing is written unless --write is given.

usage: python3 utils/add_person_refs.py [--signatures] [--write] [-m MAPPING] PATH [PATH ...]
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

from export_person_refs import PERS_NAME, REF_PATTERN, REPO_ROOT, clean_name

SCRIPT_DIR = Path(__file__).resolve().parent

MAPPING_PATH = SCRIPT_DIR / "person_refs.json"

SIGNED = "{http://www.tei-c.org/ns/1.0}signed"

# <persName ...> start tags; comments, CDATA sections and processing instructions
# are matched first so that a tag inside one of them is not counted
START_TAG = re.compile(r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<\?.*?\?>|(<persName(?=[\s/>])[^<>]*>)", re.DOTALL)
EMPTY_REF = re.compile(r"""(?<![\w:.-])ref\s*=\s*(?:"\s*"|'\s*')""")

EMPTY = "empty ref"
SIGNATURE = "signature"


class SkipFile(Exception):
    pass


def xml_files(paths):
    files = []

    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.xml")))
        elif path.is_file():
            files.append(path)
        else:
            sys.exit(f"error: {path} is not a file or a folder")

    return files


def load_mapping(path: Path) -> dict:
    mapping = json.loads(path.read_text(encoding="utf-8"))

    for name, ref in mapping.items():
        if not isinstance(ref, str) or not REF_PATTERN.fullmatch(ref):
            sys.exit(f"error: {path}: unexpected reference for \"{name}\": {ref!r}")

    return mapping


def shown(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def canonical(tree) -> bytes:
    return etree.tostring(tree, method="c14n")


def add_refs(raw: bytes, mapping: dict, signatures: bool):
    """Return (new content, changes, unmatched) for the content of one XML file.

    changes is a list of (line, kind, name, ref) and unmatched a Counter of (kind, name).
    """
    try:
        text = raw.decode("utf-8")
        root = etree.fromstring(raw)
    except (UnicodeDecodeError, etree.XMLSyntaxError) as exc:
        raise SkipFile(str(exc))

    elements = list(root.iter(PERS_NAME))
    tags = [match for match in START_TAG.finditer(text) if match.group(1)]

    if len(tags) != len(elements):
        raise SkipFile(f"found {len(tags)} <persName> start tags in the text but {len(elements)} elements")

    changes = []
    unmatched = Counter()
    pieces = []
    position = 0

    for element, tag in zip(elements, tags):
        ref = element.get("ref")
        parent = element.getparent()

        if ref is not None and not ref.strip():
            kind = EMPTY
        elif ref is None and signatures and parent is not None and parent.tag == SIGNED:
            kind = SIGNATURE
        else:
            continue

        name = clean_name(element)
        new_ref = mapping.get(name)

        if new_ref is None:
            # a signature without a name is not worth listing, an empty ref always is
            if name or kind == EMPTY:
                unmatched[(kind, name or "(no name)")] += 1

            continue

        old_tag = tag.group(1)

        if kind == EMPTY:
            new_tag, count = EMPTY_REF.subn(f'ref="{new_ref}"', old_tag, count=1)

            if count != 1:
                raise SkipFile(f"line {element.sourceline}: could not find the empty ref in {old_tag}")
        else:
            new_tag = f'<persName ref="{new_ref}"' + old_tag[len("<persName"):]

        pieces.append(text[position:tag.start(1)])
        pieces.append(new_tag)
        position = tag.end(1)

        element.set("ref", new_ref)
        changes.append((element.sourceline, kind, name, new_ref))

    pieces.append(text[position:])
    new_raw = "".join(pieces).encode("utf-8")

    # the rewritten text must be the same document as the tree with the references set
    if canonical(etree.fromstring(new_raw).getroottree()) != canonical(root.getroottree()):
        raise SkipFile("the rewritten file would differ in more than the references")

    return new_raw, changes, unmatched


def main() -> None:
    parser = argparse.ArgumentParser(description="Add tingdata.fo person references to <persName> elements.")
    parser.add_argument('-s', '--signatures', action='store_true', help='Also add a reference to <persName> without ref inside <signed>')
    parser.add_argument('-w', '--write', action='store_true', help='Write the changes (default: only show them)')
    parser.add_argument('-m', '--mapping', type=Path, default=MAPPING_PATH, help='Mapping file (default: utils/person_refs.json)')
    parser.add_argument("paths", type=Path, nargs='+', metavar='PATH', help='XML file or folder')
    args = parser.parse_args()

    mapping = load_mapping(args.mapping)
    files = xml_files(args.paths)

    kind_counts = Counter()
    unmatched = Counter()
    changed_files = 0
    skipped_files = 0

    for path in files:
        try:
            raw = path.read_bytes()
            new_raw, changes, file_unmatched = add_refs(raw, mapping, args.signatures)
        except (OSError, SkipFile) as exc:
            print(f"skipped {shown(path)}: {exc}", file=sys.stderr)
            skipped_files += 1
            continue

        unmatched.update(file_unmatched)

        if not changes:
            continue

        for line, kind, name, ref in changes:
            print(f"{shown(path)}:{line}: {name} -> {ref} ({kind})")
            kind_counts[kind] += 1

        changed_files += 1

        if args.write:
            path.write_bytes(new_raw)

    for kind, title in ((EMPTY, "Empty refs left empty, the name is not in the mapping:"),
                        (SIGNATURE, "Signatures without a reference, the name is not in the mapping:")):
        names = sorted((name, count) for (k, name), count in unmatched.items() if k == kind)

        if names:
            print(f"\n{title}")

            for name, count in names:
                print(f"  {name} ({count})")

    total = sum(kind_counts.values())

    print(
        f"\n{len(files)} files checked: {total} references {'added' if args.write else 'to add'} in {changed_files} files "
        f"({kind_counts[EMPTY]} empty refs, {kind_counts[SIGNATURE]} signatures), {skipped_files} files skipped"
    )

    if total and not args.write:
        print("Nothing was written, run again with --write to change the files.")


if __name__ == "__main__":
    main()
