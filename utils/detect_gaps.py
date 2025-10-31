import re

from export_ids import xml_files

NUMBER_PATTERN = re.compile("52-(\\d+)-\\d+\\.xml")

def match_number_part(string) -> int|None:
    found_matches = NUMBER_PATTERN.split(str(string))

    if found_matches is not None and len(found_matches) > 1:
        return int(found_matches[1])

    return None

SECTION_52A_QUESTION_STATS = {
    2008: 39,
    2009: 115,
    2010: 85,
    2011: 46,
    2012: 60,
    2013: 66,
    2014: 108,
    2015: 71,
    2016: 100,
    2017: 86,
    2018: 88,
    2019: 120,
    2020: 169,
    2021: 222,
    2022: 135,
    2023: 141,
    2024: 119
}

def count_stats():

    results = dict()

    for x in range(2008, 2025):
        results[x] = 0

    for x in range(2008, 2025):
        files = xml_files("../parliamentary-questions/" + str(x))
        results[x] = len(list(files))

    for x in range(2008, 2025):

        number_of_records = str(results[x]).rjust(3, ' ')
        total_records = str(SECTION_52A_QUESTION_STATS[x]).rjust(3, ' ')

        percentage_records = "{:.1f}".format((results[x]/SECTION_52A_QUESTION_STATS[x]) * 100)

        diff = SECTION_52A_QUESTION_STATS[x] - results[x]

        print(str(x) + ": " + number_of_records + " / " + str(total_records) + " " + (percentage_records + "%").rjust(6, ' ') + "    " + str(diff).rjust(3, ' '))

    totals = 0
    records = 0

    for x in range(2008, 2025):
        totals += SECTION_52A_QUESTION_STATS[x]
        records += results[x]

    print(str(records) + " of " + str(totals))
    print("{:.1f}".format((records/totals) * 100))

def main():
    files = xml_files("../parliamentary-questions/2012")

    found_numbers = set()

    for f in files:
        found_numbers.add(match_number_part(f))

    found_number_list = list(found_numbers)

    found_number_list.sort()

    last_number = 0

    for number in found_number_list:

        if number - last_number > 1:
            print("Found a gap!")

        last_number = number

        print(number)

    count_stats()

if __name__ == "__main__":
    main()