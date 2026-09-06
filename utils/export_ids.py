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
from pathlib import Path
from typing import Iterator
from lxml import etree
from id_utils import generate_b32_id
import json

def xml_files(root: str | Path) -> Iterator[Path]:
    root = Path(root)
    for p in root.rglob("*"):
        # robust across case-sensitive (Linux) and case-insensitive (macOS) filesystems
        if p.is_file() and p.suffix.lower() == ".xml":
            yield p


def parse_sentences_for_extraction(filepath) -> list[tuple[str, str, int | None]]:
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
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'tei': 'http://www.tei-c.org/ns/1.0'
    }

    # Extract year from publication date in sourceDesc (optional)
    # Get first date without type attribute from sourceDesc
    year = None
    try:
        date_elements = tree.xpath('//tei:sourceDesc//tei:date[@when and not(@type)]', namespaces=namespaces)
        if date_elements:
            date_when = date_elements[0].get('when')
            if date_when and len(date_when) >= 4:
                # Extract year from date (e.g., "2025-09-03" -> 2025)
                year = int(date_when[:4])
    except (ValueError, IndexError, AttributeError):
        # If date parsing fails, year remains None
        pass

    # Find elements and add xml:id
    ## for element in tree.findall('.//{http://www.tei-c.org/ns/1.0}s'):
    for element in tree.xpath('//tei:s[@xml:id] | //tei:seg[@type="sentence"][@xml:id]', namespaces=namespaces):

        found_id = element.get('{http://www.w3.org/XML/1998/namespace}id')

        cert = element.get('cert')

        xml_lang = element.get('{http://www.w3.org/XML/1998/namespace}lang')

        if cert is not None:
            cert_lower = cert.lower()
            
            if 'low' == cert_lower:
                continue 

        if found_id is not None and len(found_id) == 10:

            if xml_lang == 'da':
                continue

            element_text_content = element.xpath('string()')

            if element_text_content is not None:

                results.append((found_id, " ".join(element_text_content.strip().split()), year))

    # # Write back with minimal changes
    # result = etree.tostring(tree,
    #                        encoding='unicode',
    #                        pretty_print=False,
    #                        method='xml')
    #
    # with open(filepath, 'w', encoding='utf-8') as f:
    #     f.write(result)

    return results


def parse_sentences(filepath) -> list[str]:
    # Parse with a parser that preserves whitespace
    parser = etree.XMLParser(remove_blank_text=False, 
                             remove_comments=False,
                             strip_cdata=False)
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ## print("Processing file: " + str(filepath))

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
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'tei': 'http://www.tei-c.org/ns/1.0'
    }

    # Find elements and add xml:id
    for element in tree.xpath('//tei:s | //tei:seg[@type="sentence"]', namespaces=namespaces):

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

def parse_standoff_sentences(filepath) -> list[tuple[str, str, int | None]]:
    """Extracts only the sentences defined in the <standOff> <join> elements."""
    parser = etree.XMLParser(remove_blank_text=False, remove_comments=False, strip_cdata=False)
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = etree.fromstring(f.read().encode('utf-8'), parser)

    namespaces = {
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'tei': 'http://www.tei-c.org/ns/1.0'
    }
    results = []

    # Get year (to match your existing tuple format)
    year = None
    try:
        date_elements = tree.xpath('//tei:sourceDesc//tei:date[@when and not(@type)]', namespaces=namespaces)
        if date_elements:
            date_when = date_elements[0].get('when')
            if date_when and len(date_when) >= 4:
                year = int(date_when[:4])
    except (ValueError, IndexError, AttributeError):
        pass

    # Map IDs to text for fast lookup
    id_map = {el.get('{http://www.w3.org/XML/1998/namespace}id'): el for el in tree.xpath('//*[@xml:id]', namespaces=namespaces)}

    # Process only the joins
    for join in tree.xpath('//tei:standOff/tei:join[@target]', namespaces=namespaces):
        targets = join.get('target').replace('#', '').split()
        joined_parts = []
        skip = False

        for t_id in targets:

            print(t_id)

            target_element = id_map.get(t_id)
            if target_element is not None:

                print("found target element")

                # Apply your exact same exclusion rules
                cert = target_element.get('cert')
                xml_lang = target_element.get('{http://www.w3.org/XML/1998/namespace}lang')
                if (cert and cert.lower() == 'low') or xml_lang == 'da':
                    skip = True

                    print("skipping!")

                    break
                
                text_content = target_element.xpath('string()')

                print("text_content: " + text_content)

                if text_content is not None:
                    joined_parts.append(" ".join(text_content.strip().split()))

        # Add to results if valid
        if not skip and joined_parts:
            primary_id = join.get('{http://www.w3.org/XML/1998/namespace}id')

            print("primary_id: " + primary_id)

            cert = target_element.get('cert')
            if cert != "low":

                if len(primary_id) == 10:
                    results.append((primary_id, " ".join(joined_parts), year))

    return results

def process_stand_off_file(stand_off_file):
    sentences = []

    for file in xml_files("../"):
        output = parse_sentences_for_extraction(file)

        for item in output:
            sentences.append(item)

    standoff_sentences = parse_standoff_sentences("/home/rani/Repositories/tingmal-public/misc/effersoe.xml")
    for item in standoff_sentences:
        sentences.append(item)

    standoff_sentences = parse_standoff_sentences("/home/rani/Repositories/tingmal-public/misc/patursson.xml")
    for item in standoff_sentences:
        sentences.append(item)

    standoff_sentences = parse_standoff_sentences("/home/rani/Repositories/tingmal-public/misc/petersen.xml")
    for item in standoff_sentences:
        sentences.append(item)

    standoff_sentences = parse_standoff_sentences("/home/rani/Repositories/tingmal-public/misc/av_skardi.xml")
    for item in standoff_sentences:
        sentences.append(item)

    results: list[dict[str, str | int | None]] = []

    for item in sentences:

        formatted = {
            'id': item[0],
            'text': item[1],
            'year': item[2],
        }

        results.append(formatted)

    seen_sentences = set()
    deduplicated_sentences: list[dict[str, str | int | None]] = []

    # Or if you want case-insensitive sorting:
    results = sorted(results, key=lambda x: x['text'].lower())

    for sentence in results:
        if sentence['text'] not in seen_sentences:
            deduplicated_sentences.append(sentence)
            seen_sentences.add(sentence['text'])

    with open('../sentences.jsonl', 'w', encoding='utf-8') as f:

        for result in deduplicated_sentences:

            f.write(json.dumps(result, ensure_ascii=False) + '\n')

def process_files(relevant_files_path):
    # relevant_files = xml_files("/home/rani/Repositories/tingmal/parliamentary-questions")
    # relevant_files = xml_files("/home/rani/Repositories/tingmal/decisions")
    relevant_files = xml_files(relevant_files_path)

    for relevant_file in relevant_files:
        do_work(str(relevant_file))

    # do_work("/home/rani/Repositories/tingmal/legislation/vegleiding_til_standard_leigusattmalan.xml")
    # do_work("/home/rani/Repositories/tingmal/decisions/datueftirlitid.xml")

    # return

    # relevant_files = xml_files("/home/rani/Repositories/tingmal/proposals/2006")
    #
    #### for relevant_file in relevant_files:
        #### do_work(str(relevant_file))

    sentences = []

    for file in xml_files("../"):
        output = parse_sentences_for_extraction(file)

        for item in output:
            sentences.append(item)

    results: list[dict[str, str | int | None]] = []

    for item in sentences:

        formatted = {
            'id': item[0],
            'text': item[1],
            'year': item[2],
        }

        results.append(formatted)

    seen_sentences = set()
    deduplicated_sentences: list[dict[str, str | int | None]] = []

    # Or if you want case-insensitive sorting:
    results = sorted(results, key=lambda x: x['text'].lower())

    for sentence in results:
        if sentence['text'] not in seen_sentences:
            deduplicated_sentences.append(sentence)
            seen_sentences.add(sentence['text'])

    with open('../sentences.jsonl', 'w', encoding='utf-8') as f:

        for result in deduplicated_sentences:

            f.write(json.dumps(result, ensure_ascii=False) + '\n')



if __name__ == "__main__":
    #process_files("/home/rani/Repositories/tingmal-public/coalition-agreements")
    #process_files("/home/rani/Repositories/tingmal-public/debates")
    ######### process_files("/home/rani/Repositories/tingmal-public/decisions")
    #process_files("/home/rani/Repositories/tingmal-public/legislation/2016")
    #process_files("/home/rani/Repositories/tingmal-public/misc")
    ## process_files("/home/rani/Repositories/tingmal-public/parliamentary-questions/1998")
    ##### process_files("/home/rani/Repositories/tingmal-public/misc/local")
    process_files("/home/rani/Repositories/tingmal-public/proposals/2024")
    process_stand_off_file("/home/rani/Repositories/tingmal-public/misc/joannes-patursson.xml")
