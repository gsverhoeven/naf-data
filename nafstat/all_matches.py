#!/usr/bin/env python
"""  Parse match from HTML """
import copy
import logging
import argparse

import csv

import nafstat.collate
LOG = logging.getLogger(__package__)


def switch_home_away(m):
    row = {}
    for key, value in m.items():
        if key.startswith("home_"):
            row[key.replace("home_", "away_")] = value
        elif key.startswith("away_"):
            row[key.replace("away_", "home_")] = value
        else:
            row[key] = value
    row["repeated_match"] = 1
    return row


def write_match(csv_writer, m):
    LOG.debug(f"Write match {m['tournament_name']} {m['home_coach']} {m['home_race']} {m['home_score']}-{m['away_score']} {m['away_race']} {m['away_coach']}")
    csv_writer.writerow(m)

def to_csv(matches, output_file = "all_matches.csv", repeat_matches = False):
    LOG.debug("Opening %s", output_file)
    with open(output_file, 'w') as csvfile:
        columns = ["date",
                   "tournament_id",
                   "match_id",
                   "tournament_name",
                   "home_coach",
                   "home_race",
                   "home_result",
                   "home_score",
                   "away_score",
                   "away_result",
                   "away_race",
                   "away_coach",
                   "casualties?",
                   "home_cas",
                   "away_cas",
                   "mirror",
                   "home_tr",
                   "away_tr",
                   "variant",
                   "swiss",
                   "ruleset",
                   "style",
                   "location",
                   "home_nationality",
                   "away_nationality"]
        if repeat_matches:
            columns.append("repeated_match")

        csv_writer = csv.DictWriter(csvfile, fieldnames=columns, extrasaction='ignore', quotechar='"')
        LOG.debug("Write header")
        csv_writer.writeheader()
        tournament_name = ""
        for m in matches:
            write_match(csv_writer, m)
            if repeat_matches:
                write_match(csv_writer, switch_home_away(m))

            if m["tournament_name"] != tournament_name:
                LOG.info("Writing tournament %s", m["tournament_name"])
                tournament_name = m["tournament_name"]

    LOG.debug(f"Finished writing all_matches.csv")
    LOG.info("Copy file to target")


def all_matches():
    for t in nafstat.collate.load_all():
        for m in t["matches"]:
            match = copy.copy(m)
            match["tournament_id"] = t["tournament_id"]
            match["tournament_name"] = t["name"]
            match["tmid"] = f"{t['tournament_id']}#{m['match_id'].zfill(3)}"
            match["variant"] = t["variant"]
            match["swiss"] = t["swiss"]
            match["datetime"] = f'{m["date"]} {m["time"]}'
            match["tournament_date"] = t["start_date"]
            match["location"] = t["location"]
            match["style"] = t["style"].strip().replace("\n", '').replace("  ", " ")
            match["casualties?"] = t["casualties"]
            match["order"] = f"{t['start_date']} {t['name']} {m['match_id'].zfill(4)}"
            match["mirror"] = m["home_race"].lower() == m["away_race"].lower()
            match["ruleset"] = t["ruleset"] if "unknown" not in t["ruleset"] else ""
            match["repeated_match"] = 0
            yield match


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    LOG.info("All matches")
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("output_file")
    argument_parser.add_argument("--repeat-matches", action="store_true", default=False)

    arguments = argument_parser.parse_args()

    if not arguments.output_file.endswith(".csv"):
        sys.exit("Sure? '{}' does not end with .csv".format(arguments.output_file))

    to_csv(sorted(all_matches(), key=lambda m: m["order"], reverse=True),
           arguments.output_file,
           repeat_matches=arguments.repeat_matches)


if __name__ == "__main__":
    main()