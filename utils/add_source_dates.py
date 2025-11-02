#!/usr/bin/env python3
"""
Add source document dates to parliamentary question metadata.

This script copies the date from div[@type="signature"]/closer/dateline/date
into the teiHeader/fileDesc/sourceDesc/bibl element if no date element
(without a type attribute) already exists there.
"""

import os
import sys
from pathlib import Path
from lxml import etree

# TEI namespace
TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NAMESPACES = {
    'tei': TEI_NS,
    'xml': XML_NS
}


def process_file(filepath):
    """
    Process a single XML file to add missing source date.

    Returns True if file was modified, False otherwise.
    """
    # Parse the XML file with settings that preserve formatting
    parser = etree.XMLParser(
        remove_blank_text=False,
        remove_comments=False,
        strip_cdata=False
    )

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the XML
    root = etree.fromstring(content.encode('utf-8'), parser)

    # Find the bibl element
    bibl_elements = root.xpath(
        '//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:bibl',
        namespaces=NAMESPACES
    )

    if not bibl_elements:
        print(f"  Warning: No <bibl> element found in {filepath.name}")
        return False

    bibl = bibl_elements[0]

    # Check if there's already a date element without a type attribute
    existing_dates = bibl.xpath('tei:date[not(@type)]', namespaces=NAMESPACES)

    if existing_dates:
        # Date without type attribute already exists, skip
        return False

    # Find the date in the signature section (may be nested in other elements)
    signature_dates = root.xpath(
        '//tei:div[@type="signature"]//tei:date',
        namespaces=NAMESPACES
    )

    if not signature_dates:
        print(f"  Warning: No signature date found in {filepath.name}")
        return False

    signature_date = signature_dates[0]
    when_attr = signature_date.get('when')

    if not when_attr:
        print(f"  Warning: Signature date has no 'when' attribute in {filepath.name}")
        return False

    # Create a new date element to add to bibl
    # We need to create it with the TEI namespace
    new_date = etree.Element(f"{{{TEI_NS}}}date", attrib={'when': when_attr})

    # Set the tail for the new date element (newline + 8 spaces for closing </bibl>)
    new_date.tail = '\n        '

    # Find the right position to insert the date (after <note> if it exists, otherwise at the end)
    note_elements = bibl.xpath('tei:note', namespaces=NAMESPACES)
    if note_elements:
        # Insert after the last note element
        last_note = note_elements[-1]
        # Update the tail of the last note to add proper indentation
        last_note.tail = '\n          '
        note_index = list(bibl).index(last_note)
        bibl.insert(note_index + 1, new_date)
    else:
        # Just append to the end
        # Find the last child element and update its tail
        if len(bibl) > 0:
            last_child = bibl[-1]
            last_child.tail = '\n          '
        bibl.append(new_date)

    # Write back with minimal changes
    result = etree.tostring(root,
                           encoding='unicode',
                           pretty_print=False,
                           method='xml')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)

    return True


def main():
    """Process all parliamentary question XML files."""
    # Get the repository root (parent of utils directory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    pq_dir = repo_root / 'parliamentary-questions'

    if not pq_dir.exists():
        print(f"Error: Parliamentary questions directory not found: {pq_dir}")
        sys.exit(1)

    # Find all XML files matching the pattern 52-*-*.xml
    xml_files = sorted(pq_dir.glob('*/52-*-*.xml'))

    if not xml_files:
        print(f"No parliamentary question files found in {pq_dir}")
        sys.exit(0)

    print(f"Found {len(xml_files)} parliamentary question files")
    print()

    modified_count = 0

    for filepath in xml_files:
        print(f"Processing {filepath.parent.name}/{filepath.name}...", end=' ')

        try:
            was_modified = process_file(filepath)
            if was_modified:
                print("✓ Added source date")
                modified_count += 1
            else:
                print("- Skipped (date already exists or not found)")
        except Exception as e:
            print(f"✗ Error: {e}")

    print()
    print(f"Modified {modified_count} file(s)")


if __name__ == '__main__':
    main()
