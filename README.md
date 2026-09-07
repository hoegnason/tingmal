# Tingmál

**A curated Faroese parliamentary, legal and administrative text corpus.**

Tingmál combines manually corrected text and native-speaker-reviewed sentence segmentation with document-level source metadata. It provides **TEI/XML documents for context and provenance** and a **deduplicated JSONL export for sentence-level research and NLP**.

The collection covers parliamentary questions, legislative proposals, legislation, reports, administrative decisions, coalition agreements and debate transcripts, with supplementary historical and literary texts. It supports corpus research, terminology, parliamentary analysis, retrieval and Faroese language-model adaptation. It is a domain corpus, not a balanced sample of general Faroese.

> Tingmál is an independent, unofficial publication. It is not affiliated with or endorsed by Løgtingið.

## Statistics

Statistics snapshot: **7 September 2026**, commit [`9747212`](https://github.com/hoegnason/tingmal/tree/974721277c23978209c69017cda234484584ea6f).

The figures below describe [`sentences.jsonl`](sentences.jsonl), the **deduplicated sentence export**, not document counts or all text occurrences in the TEI collection.

| Metric | Value |
|---|---:|
| Sentences | **146,154** |
| Tokens, whitespace-separated | **3,125,792** |
| Types, unique lowercased token strings | 157,333 |
| Mean sentence length, tokens | 21.39 |
| Median sentence length, tokens | 19 |
| Sentence length, 5th–95th percentile, tokens | 7–43 |
| Mean sentence length, characters | 139.3 |

**Comparing corpus sizes:** [`utils/compute_stats.py`](utils/compute_stats.py) counts runs of non-whitespace characters (`\S+`); punctuation remains attached. These counts are not model-specific subword tokens, lemmas or dictionary entries. Compare using the same tokenization and deduplication conventions.

### Coverage

**74.23%** of exported sentences are assigned to the 2010s and 2020s; **6,828 sentences (4.67%)** have no extracted year. Coverage is uneven across periods and document categories. Dates refer to the export's `year` field, with the limitations described below.

<details>
<summary>Sentence and token distribution by decade</summary>

| Decade | Sentences | Share | Tokens |
|---|---:|---:|---:|
| 1900s | 8 | 0.01% | 137 |
| 1930s | 617 | 0.42% | 14,060 |
| 1940s | 175 | 0.12% | 3,119 |
| 1950s | 377 | 0.26% | 9,693 |
| 1970s | 106 | 0.07% | 1,650 |
| 1980s | 204 | 0.14% | 4,439 |
| 1990s | 13,090 | 8.96% | 320,261 |
| 2000s | 16,257 | 11.12% | 319,975 |
| 2010s | 39,379 | 26.94% | 812,475 |
| 2020s | 69,113 | 47.29% | 1,486,891 |
| Unknown | 6,828 | 4.67% | 153,092 |

</details>

**Reported §52a parliamentary-question coverage, 2008–2024:** **1,380 of 1,770 records (approximately 78%)**. This is a category-specific coverage measure, not completeness of the whole corpus or all parliamentary questions.

<details>
<summary>§52a coverage by year and counting notes</summary>

| Year | Collected | Official total | Coverage |
|---|---:|---:|---:|
| 2008 | 24 | 39 | 61.5% |
| 2009 | 50 | 115 | 43.5% |
| 2010 | 85 | 85 | 100.0% |
| 2011 | 46 | 46 | 100.0% |
| 2012 | 60 | 60 | 100.0% |
| 2013 | 66 | 66 | 100.0% |
| 2014 | 108 | 108 | 100.0% |
| 2015 | 71 | 71 | 100.0% |
| 2016 | 76 | 100 | 76.0% |
| 2017 | 24 | 86 | 27.9% |
| 2018 | 31 | 88 | 35.2% |
| 2019 | 43 | 120 | 35.8% |
| 2020 | 79 | 169 | 46.7% |
| 2021 | 222 | 222 | 100.0% |
| 2022 | 135 | 135 | 100.0% |
| 2023 | 141 | 141 | 100.0% |
| 2024 | 119 | 119 | 100.0% |

These are the project's reported coverage figures. Reference totals are recorded in [`utils/section52a_coverage.py`](utils/section52a_coverage.py). Its current counter includes every XML file in each year directory; restrict counting to §52a records before updating this table where other question types are present. File counts do not establish completeness of each document's contents.

</details>

## Provenance and data formats

### TEI/XML: documents and source metadata

The XML files retain document structure and separate the original source from the Tingmál publication. Depending on the document, headers record title, author or speaker, publisher, original URL, source date, source format, access date and editorial notes.

For example, [`52-001-2024.xml`](parliamentary-questions/2024/52-001-2024.xml) identifies the original Løgting document, its author, date and PDF source, and describes correction and segmentation. Metadata completeness varies, particularly for supplementary historical and literary texts; consult individual headers.

**Use TEI for** source attribution, document context, contextual retrieval and occurrence-based analysis. It is the richer representation; JSONL is a derived view.

### JSONL: deduplicated sentence text

[`sentences.jsonl`](sentences.jsonl) is UTF-8, with one JSON object per line. The exporter writes:

| Field | Meaning |
|---|---|
| `id` | 10-character identifier of the retained TEI segment or stand-off join. |
| `text` | Sentence text with normalized whitespace. |
| `year` | Integer extracted from source metadata, or `null`. |

Match `id` to `xml:id` in the **same repository snapshot** to recover source context. JSONL does not include source URLs, authors, document boundaries or all duplicate occurrences.

**Date limitation:** the exporter takes the first eligible date in `sourceDesc` across each XML file. For files containing multiple documents, this may not be the date of every sentence. Check document-level dates for temporal research.

**Use JSONL for** deduplicated sentence-level experiments. Alphabetical order and deduplicated counts do not preserve original document order or occurrence frequencies. For model evaluation, use document- or document-family-based splits rather than randomly distributing related sentences across training and test sets.

## Curation and pipeline

Curation includes manual correction of OCR/extraction errors, structural encoding and sentence segmentation reviewed by a native Faroese speaker. Editorial notes are recorded in TEI where available. The corpus is curated text with structural markup, not a gold-standard POS-tagged or dependency-parsed dataset.

```text
Source documents, including PDF and HTML
    → text extraction and manual correction
    → TEI/XML structure, source metadata and sentence segmentation
    → sentence IDs, filtering and whitespace normalization
    → exact-text deduplication and sorting
    → sentences.jsonl
```

[`utils/export_ids.py`](utils/export_ids.py) implements the export:

- **Selection and filtering:** extracts `<s>` and `<seg type="sentence">` elements with 10-character IDs, plus stand-off joins from selected supplementary texts. Excludes selected elements explicitly marked `xml:lang="da"` or `cert="low"`. Untagged elements remain eligible; the exporter does not perform automatic language identification.
- **Normalization:** collapses whitespace and exports plain text without XML markup.
- **Deduplication:** removes exact, case-sensitive duplicate texts after normalization, retaining one occurrence's ID and year. Sorts by lowercased text. Near-duplicates are not removed by this step.

Human review does not guarantee error-free transcription or segmentation. Consult the original source when an individual reading matters.

## Copyright and reuse

**Dataset license:** Tingmál is distributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) ([LICENSE](LICENSE)). This covers rights held by the project's contributors, not additional rights in third-party works or public-domain text. When relying on this license, provide attribution, link to the license and indicate changes. Utility files with separate license notices retain those terms.

**Source-text rights:** the project cites the following provisions of the [Faroese Copyright Act, Act No. 30 of 30 April 2015](https://www.logir.fo/Logtingslog/30-fra-30-04-2015-um-upphavsraett), where applicable:

- **§9 — public documents:** laws, regulations, judgments and similar public-authority documents are not protected by copyright. Independently contributed works within them are treated separately under §9(2).
- **§27 — public debate:** permits reproduction of specified public proceedings, including parliamentary proceedings. Contributors retain the exclusive right to publish collections of their own contributions under §27(2).

These are not blanket permissions for every text in the repository. Check individual sources, particularly independent contributions and supplementary literary material, and retain source attribution. The dataset license does not resolve every source-rights or privacy question. This is a documentation summary, not legal advice; the corpus is provided without warranties.

## Reproducibility and citation

To recompute export statistics, run from the repository root:

```bash
python3 utils/compute_stats.py sentences.jsonl
```

The statistics script uses the Python standard library. The TEI exporter requires Python 3.10+ and `lxml`, and currently has machine-specific paths that need adapting. ID assignment can rewrite XML files; rebuild in a working copy. The statistics command does not reproduce source extraction or human review.

For research, cite **Rani Høgnason Hansen, Tingmál [dataset]**, the [repository](https://github.com/hoegnason/tingmal), the exact commit used and your access date. State whether you used TEI or JSONL and report additional filtering or tokenization. Retain document references and sentence IDs where relevant.

Corrections and contributions are welcome through [issues](https://github.com/hoegnason/tingmal/issues) and pull requests. For text corrections, include the document path, sentence ID and original-source reference when available.
