[![CC BY 4.0][cc-by-shield]][cc-by]

#  Tingmál
Tingmál is an **unofficial** structured dataset of documents, acts, and proceedings from the Parliament of the Faroe Islands (Løgtingið).

> **Note:** This is not an official publication of Løgtingið.

## Table of Contents
- [Overview](#overview)
- [Provenance & Legal Notes](#provenance--legal-notes)
- [License](#license)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)

## Overview
- **What it is:** A cleaned, structured compilation intended for research, analysis, and tooling.
- **What it isn’t:** An official publication of Løgtingið.
- **Typical uses:** text mining, parliamentary analytics, search/indexing experiments, Faroese language data, dataset tooling.

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