#!/usr/bin/env python3
""" Export data to sqlite """
import datetime
import argparse
import logging.config

import nafstat.update
import nafstat.to_db

logging.config.fileConfig('pylogging.conf', disable_existing_loggers=True)
LOG = logging.getLogger("nafstat.to_db")
logging.getLogger("nafstat.file_loader").setLevel(logging.INFO)


def add_arguments(argument_parser, default_source):
    argument_parser.add_argument("--debug", help="Log level debug", action="store_true")
    subparsers = argument_parser.add_subparsers(dest="command")

    exporter = subparsers.add_parser("export", help="nafstat export TYPE [SOURCE] DEST") 
    nafstat.to_db.add_arguments(exporter, default_source)

    updater = subparsers.add_parser("update", help="nafstat update TYPE [SOURCE] DEST")
    nafstat.update.add_arguments(updater, default_source)
    return argument_parser

def run_with_arguments(arguments):
    if arguments.command == "update":
        nafstat.update.run_with_arguments(arguments)
    elif arguments.command == "export" and arguments.type == "sqlite":
        nafstat.to_db.run_with_arguments(arguments)
    else:
        print(arguments)
        print("Not implemented")


def main():
    import sys
    print(__name__)
    #log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    #logging.basicConfig(level=logging.INFO if "--debug" is sys.argv else logging.INFO, format=log_format)

    argument_parser = argparse.ArgumentParser()
    default_source="data/"

    argument_parser = add_arguments(argument_parser, default_source)

    arguments = argument_parser.parse_args()
    LOG.debug("debugged")
    run_with_arguments(arguments)


if __name__ == "__main__":
    main()
