[![CC BY 4.0][cc-by-shield]][cc-by]

#  Tingmál
Tingmál is an **unofficial** structured dataset of documents, acts, and proceedings from the Parliament of the Faroe Islands (Løgtingið).

> **Note:** This is not an official publication of Løgtingið.

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Data Formats](#data-formats)
  - [TEI/XML Format](#teixml-format)
  - [JSONL Format](#jsonl-format)
- [Processing Pipeline](#processing-pipeline)
- [Utility Scripts](#utility-scripts)
- [Provenance & Legal Notes](#provenance--legal-notes)
- [License](#license)
- [Stats](#stats)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)

## Overview
- **What it is:** A cleaned, structured compilation intended for research, analysis, and tooling.
- **What it isn't:** An official publication of Løgtingið.
- **Typical uses:** text mining, parliamentary analytics, search/indexing experiments, Faroese language data, dataset tooling.

## Project Structure

The repository is organized into the following directories:

```
tingmal/
├── parliamentary-questions/   # Parliamentary questions organized by year (2008-2025)
│   └── YYYY/                 # Each year contains XML files named: 52-NNN-YYYY.xml
├── legislation/              # Laws, guidelines, and procedural rules
│   └── loegtingid/          # Parliament-specific regulations and procedures
├── proposals/               # Legislative proposals organized by year
├── reports/                 # Committee reports organized by year
├── decisions/               # Administrative decisions from various bodies
├── coalition-agreements/    # Government coalition agreements
├── misc/                    # Miscellaneous documents
├── utils/                   # Python utilities for data processing
│   ├── compute_stats.py          # Generate statistics from sentences.jsonl
│   ├── section52a_coverage.py   # Compute parliamentary question coverage
│   ├── detect_gaps.py            # Detect gaps in question numbering
│   ├── export_ids.py             # Export and manage sentence IDs
│   └── id_utils.py               # Generate unique base32 IDs
└── sentences.jsonl          # Deduplicated sentence-level dataset (23,664+ sentences)
```

**Key files:**
- All documents are encoded in **TEI/XML** format (Text Encoding Initiative)
- Parliamentary questions follow naming convention: `52-NNN-YYYY.xml` where NNN is the question number
- `sentences.jsonl` contains all extracted Faroese sentences with unique identifiers

## Data Formats

### TEI/XML Format

All documents in this repository use the **TEI (Text Encoding Initiative) P5** XML standard, a widely-used format for encoding structured texts in the humanities and social sciences.

#### Document Structure

Each TEI/XML document consists of two main parts:

**1. TEI Header (`<teiHeader>`)** - Contains metadata:
```xml
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>52-1/2024: Miðfyrisitingin</title>
      </titleStmt>
      <publicationStmt>
        <publisher>Rani Høgnason Hansen</publisher>
        <idno type="url">https://github.com/hoegnason/tingmal</idno>
        <availability status="free">
          <licence target="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</licence>
        </availability>
      </publicationStmt>
      <sourceDesc>
        <bibl type="parliamentary_document">
          <publisher>Føroya Løgting</publisher>
          <author>
            <persName ref="https://tingdata.fo/person/...">Name</persName>
          </author>
          <ref target="https://www.logting.fo/documents/..."/>
        </bibl>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
```

The header includes:
- Document title and identification
- License information (CC BY 4.0)
- Original source references with URLs to official Løgtingið documents
- Author information with persistent identifiers
- Editorial notes about text correction and segmentation

**2. Text Body (`<text>`)** - Contains the actual content:
```xml
  <text>
    <body>
      <div type="question">
        <div type="questioner">
          <head>Spyrjari: </head>
          <persName>Name, <roleName>løgtingsmaður</roleName></persName>
        </div>
        <div type="question-list">
          <s xml:id="woyjvu7qcg" xml:lang="fo">
            Hvør er árligi kostnaðurin av aðalráðunum árini 2019 – 2023?
          </s>
        </div>
        <div type="background">
          <s xml:id="uf6ofajlqn" xml:lang="fo">
            Hetta er ein uppfylging uppá spurning 52-133/2023...
          </s>
        </div>
      </div>
    </body>
  </text>
</TEI>
```

**Structural elements:**
- `<div type="question">` - Parliamentary question container
- `<div type="questioner">` - Person asking the question
- `<div type="respondent">` - Person who must respond (usually a minister)
- `<div type="subject">` - Subject/topic of the question
- `<div type="question-list">` - The actual questions
- `<div type="background">` - Background context and justification

**Sentence-level markup:**
- Every sentence is wrapped in `<s>` element
- `xml:id` attribute: 10-character base32 identifier (globally unique)
- `xml:lang` attribute: Language code (`fo` = Faroese, `da` = Danish)
- IDs are cryptographically generated and serve as stable identifiers for citation

**Example sentence:**
```xml
<s xml:id="woyjvu7qcg" xml:lang="fo">Hvør er árligi kostnaðurin?</s>
```

### JSONL Format

The `sentences.jsonl` file uses **JSONL (JSON Lines)** format - a newline-delimited JSON format where each line is a complete, valid JSON object. This format is ideal for streaming large datasets and line-by-line processing.

#### Structure

Each line contains a single sentence object:
```json
{"id": "clbkpo3l72", "text": "\"Teppið skrikt undan teimum\" við hesi skerjing, sum fór fram, og eftirfylgjandi hevur tað havt negativa ávirkan á teirra dagliga og lívsgóðsku og teirra sosialu møguleikar verða skerdir og sjálvbjargni minkar."}
{"id": "n42wesqrbx", "text": "\"Vit skulu ikki gloyma, at umhvørvisfelagsskapir eru líka ágangandi móti veiðu á djúphavinum, sum móti grindadrápi\"."}
```

#### Fields

- **`id`** (string): The 10-character base32 identifier from `xml:id` in the TEI/XML source
  - Format: lowercase letters and digits from base32 alphabet (`a-z`, `2-7`)
  - Always starts with a letter (XML requirement)
  - Globally unique across all documents in the repository

- **`text`** (string): The sentence text with normalized whitespace
  - Multiple spaces/tabs collapsed to single space
  - Leading and trailing whitespace removed
  - Original Faroese orthography preserved (including diacritics: áíóúýæøð)

#### Properties

- **Format**: One JSON object per line (no comma between objects)
- **Encoding**: UTF-8
- **Language**: Only Faroese sentences (`xml:lang="fo"`); Danish excluded
- **Deduplication**: Duplicate sentences removed (only first occurrence retained)
- **Sorting**: Alphabetically sorted by text (case-insensitive)
- **Size**: 23,664+ unique sentences

#### Reading JSONL in Python

```python
import json

# Read line by line (memory efficient)
with open('sentences.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        print(f"ID: {obj['id']}, Text: {obj['text'][:50]}...")
```

#### Reading JSONL in Other Languages

```bash
# Command line tools
jq '.text' sentences.jsonl              # Extract all text fields
grep '"id": "woyjvu7qcg"' sentences.jsonl  # Find specific sentence
wc -l sentences.jsonl                   # Count sentences
```

## Processing Pipeline

The following diagram shows how data flows from source documents to the final datasets:

```
PDF Documents (løgting.fo)
         ↓
   Manual extraction & OCR correction
         ↓
   TEI/XML Documents (.xml files)
         ↓
   ID Assignment (export_ids.py)
   • Scans all XML files
   • Generates unique 10-char IDs
   • Adds xml:id to <s> elements
         ↓
   Sentence Extraction (export_ids.py)
   • Extracts text from <s> elements
   • Filters by language (fo only)
   • Normalizes whitespace
         ↓
   Deduplication & Sorting
   • Removes duplicate sentences
   • Sorts alphabetically
         ↓
   sentences.jsonl (Final dataset)
```

### Detailed Processing Steps

**1. ID Generation (`id_utils.py`)**
- Generates cryptographically secure random IDs using Python's `secrets` module
- Uses base32 alphabet: `abcdefghijklmnopqrstuvwxyz234567`
- Ensures IDs start with letter (XML compliance)
- Tracks used IDs in `utils/used_ids.txt` to prevent collisions

**2. XML Processing (`export_ids.py`)**
- Parses XML with `lxml` while preserving whitespace
- Namespace handling:
  - TEI namespace: `http://www.tei-c.org/ns/1.0`
  - XML namespace: `http://www.w3.org/XML/1998/namespace`
- XPath queries: `tree.xpath('//tei:s[@xml:id]', namespaces=namespaces)`
- Adds missing IDs to sentences without `xml:id` attribute

**3. Sentence Extraction**
```python
# Pseudocode showing extraction logic
for xml_file in all_xml_files:
    for sentence_element in xml_file.find_all('<s>'):
        if sentence_element.xml_lang == 'da':
            continue  # Skip Danish sentences

        text = sentence_element.text_content()
        text = ' '.join(text.strip().split())  # Normalize whitespace

        sentences.append({
            'id': sentence_element.xml_id,
            'text': text
        })
```

**4. Deduplication & Output**
- Sentences sorted alphabetically (case-insensitive)
- Duplicates removed based on text content
- First occurrence of each sentence retained
- Written as JSONL (one JSON object per line)

### Regenerating the Dataset

To regenerate `sentences.jsonl` after modifying XML files:

```bash
cd utils
python3 export_ids.py
```

This will:
1. Scan all XML files in the repository
2. Assign IDs to any new sentences
3. Extract all Faroese sentences
4. Generate fresh `sentences.jsonl` in parent directory

## Utility Scripts

The `utils/` directory contains Python scripts for data processing and quality assurance:

### `compute_stats.py`
Generates statistics from `sentences.jsonl`:

```bash
python3 utils/compute_stats.py [path/to/sentences.jsonl]
```

**Output:** Markdown table with metrics:
- Total sentence count
- Token count (space-split)
- Vocabulary size (unique tokens, case-folded)
- Average/median sentence length
- Percentile ranges

### `section52a_coverage.py`
Computes parliamentary question coverage by year:

```bash
python3 utils/section52a_coverage.py
```

**Output:**
- `PQ_STATS.json` - Machine-readable coverage data
- `PQ_STATS.md` - Markdown table for README
- Console output showing gaps in question numbering

### `detect_gaps.py`
Detects missing parliamentary questions by analyzing filename sequences:

```bash
python3 utils/detect_gaps.py
```

Identifies missing question numbers (e.g., 52-015-2020 through 52-019-2020).

### `export_ids.py`
Core processing script - assigns IDs and generates `sentences.jsonl`:

```bash
cd utils
python3 export_ids.py
```

**Functions:**
- `xml_files(path)` - Recursively finds all .xml files
- `parse_sentences(filepath)` - Extracts existing IDs
- `add_ids_to_file(filepath, used_ids)` - Adds missing IDs
- `parse_sentences_for_extraction(filepath)` - Extracts sentence text
- `process_files(path)` - Main processing loop

### `id_utils.py`
ID generation utility (imported by other scripts):

```python
from id_utils import generate_b32_id

# Generate a new 10-character ID
new_id = generate_b32_id(length=10)  # e.g., 'woyjvu7qcg'
```

### Dependencies

The utility scripts require:
- **Python 3.10+**
- **lxml** - XML processing library
  ```bash
  pip install lxml
  ```

## Provenance & Legal Notes
- See the headers of **individual** documents for the original source of data.
- Content includes material exempt under **§9 (public documents)** and **§27 (public debate)** of the Faroese Copyright Act.

## License 

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg


You are free to:

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.

## Stats
The summary below was **computed from `sentences.jsonl`**, a sentence-level JSONL file with fields `id` and `text`. It contains only **full, deduplicated sentences** where formatting such as bullet points, ordinal list numbers, and legal section symbols (§) has been removed. Sentence segmentation has been reviewed by a Faroese native speaaker.


| Metric | Value |
|:---|---:|
| Sentences | 23,664 |
| Tokens (space-split) | 463,313 |
| Types (unique tokens, case-folded) | 49,998 |
| Avg. sentence length (tokens) | 19.58 |
| Median sentence length (tokens) | 18 |
| 5-95% sentence length (tokens) | 7-39 |
| Avg. sentence length (characters) | 127.4 |


### Coverage of Parliamentary Questions

The table below reports yearly coverage of parliamentary questions - currently limited to §52a - by comparing the number of TEI/XML records present in this repository with the official yearly totals.
These figures are computed from the files under **`parliamentary-questions/<YEAR>/`** using the script in `utils/section52a_coverage.py`. 


| Year | Collected | Official total | Coverage | Missing |
|:----:|----------:|---------------:|---------:|--------:|
| 2008 |         0 |             39 |     0.0% |      39 |
| 2009 |        50 |            115 |    43.5% |      65 |
| 2010 |        85 |             85 |   100.0% |       0 |
| 2011 |        46 |             46 |   100.0% |       0 |
| 2012 |        60 |             60 |   100.0% |       0 |
| 2013 |        66 |             66 |   100.0% |       0 |
| 2014 |       108 |            108 |   100.0% |       0 |
| 2015 |        71 |             71 |   100.0% |       0 |
| 2016 |        76 |            100 |    76.0% |      24 |
| 2017 |        24 |             86 |    27.9% |      62 |
| 2018 |        31 |             88 |    35.2% |      57 |
| 2019 |        43 |            120 |    35.8% |      77 |
| 2020 |        79 |            169 |    46.7% |      90 |
| 2021 |       222 |            222 |   100.0% |       0 |
| 2022 |       135 |            135 |   100.0% |       0 |
| 2023 |       141 |            141 |   100.0% |       0 |
| 2024 |       119 |            119 |   100.0% |       0 |

**Totals:** Collected **1,356** of **1,770** (overall coverage **76.6%**). *Note:* these figures currently exclude regular written and oral parliamentary questions; those will be added in a later release.

## Contributing
Issues and pull requests are welcome. Please open an issue to discuss substantial changes.

## Disclaimer
- Tingmál is provided “as is,” without warranties of any kind.
- The author(s)/maintainer(s) are **not** affiliated with Løgtingið.
- You are responsible for compliance with applicable laws when redistributing or adapting the data (e.g., §27(2) - the limitation to the "public debate" exemption i.e. original contributor's exclusive right to *collections consisting of only their own contributions*).