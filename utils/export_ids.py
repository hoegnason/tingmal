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

from pathlib import Path
from typing import Iterator
from lxml import etree
from id_utils import generate_b32_id

def xml_files(root: str | Path) -> Iterator[Path]:
    root = Path(root)
    for p in root.rglob("*"):
        # robust across case-sensitive (Linux) and case-insensitive (macOS) filesystems
        if p.is_file() and p.suffix.lower() == ".xml":
            yield p


def parse_sentences(filepath) -> list[str]:
    # Parse with a parser that preserves whitespace
    parser = etree.XMLParser(remove_blank_text=False, 
                             remove_comments=False,
                             strip_cdata=False)
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the XML
    tree = etree.fromstring(content.encode('utf-8'), parser)

    results = []

    # Define namespace map
    namespaces = {
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }

    # Find elements and add xml:id
    ## for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}s'):
    for element in tree.xpath('//*[@xml:id]', namespaces=namespaces):

        found_id = element.get('{http://www.w3.org/XML/1998/namespace}id')

        if found_id is not None and len(found_id) == 10:

            # element.set('{http://www.w3.org/XML/1998/namespace}id', id_value)

            results.append(found_id)

    
    # # Write back with minimal changes
    # result = etree.tostring(tree,
    #                        encoding='unicode',
    #                        pretty_print=False,
    #                        method='xml')
    #
    # with open(filepath, 'w', encoding='utf-8') as f:
    #     f.write(result)

    return results


def add_ids_to_file(filepath: str, used_ids: set) -> list[str]:
    # Parse with a parser that preserves whitespace
    parser = etree.XMLParser(remove_blank_text=False,
                             remove_comments=False,
                             strip_cdata=False)

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the XML
    tree = etree.fromstring(content.encode('utf-8'), parser)

    results = []

    # Define namespace map
    namespaces = {
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }

    # Find elements and add xml:id
    for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}s'):

        found_id = element.get('{http://www.w3.org/XML/1998/namespace}id')

        if found_id is None or len(found_id) <= 0:

            generated_id = generate_b32_id()

            if generated_id in used_ids:
                raise RuntimeError(f"Generated ID '{generated_id}' is already in use.")

            element.set('{http://www.w3.org/XML/1998/namespace}id', generated_id)

            results.append(found_id)

    # Write back with minimal changes
    result = etree.tostring(tree,
                           encoding='unicode',
                           pretty_print=False,
                           method='xml')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)

    return results

# Example usage

def do_work(target_file: str):

    print("target file: " + target_file)

    used_ids = set()

    for file in xml_files("../"):
        output = parse_sentences(file)

        for found_id in output:
            used_ids.add(found_id)

    print(len(used_ids))

    with open("used_ids.txt", "w") as file:
        for line in used_ids:
            file.write(line + "\n")

    add_ids_to_file(target_file, used_ids)

def main():

    relevant_files = xml_files("/home/rani/Repositories/tingmal/parliamentary-questions/2024")

    for relevant_file in relevant_files:
        do_work(str(relevant_file))

if __name__ == "__main__":
    main()