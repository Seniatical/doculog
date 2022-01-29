"""
CLI entrypoints to the code.
"""
from asyncio.log import logger
from pathlib import Path
from argparse import ArgumentParser
import os
import logging
import sys

from doculog.config import configure
from doculog import ChangelogDoc, __version__


def generate_changelog(overwrite: bool = False):
    root = Path.cwd()

    config = configure(root)
    log_path = root / config["changelog_name"]

    if overwrite:
        if log_path.exists():
            os.remove(log_path.absolute())
            logger.info("Overwriting current changelog")
        else:
            logger.warning("Skipping overwrite, existing changelog file not found", exc_info=1)

    doc = ChangelogDoc(log_path, config["categories"], config["category_options"])
    doc.generate()
    doc.save()

    if log_path.exists():
        logger.info(f"Saved changelog to: {log_path}")
    else:
        logger.error(f"Generating changelog failed, path provided: {log_path}", exc_info=1)

parser = ArgumentParser(
    prog="doculog",
    description=f"Doculog v{__version__}",
)

parser.add_argument("-cl", "--change-log", 
    action="store_true",
    dest="cl",
    help="generates changelog for project"
)

parser.add_argument("-v", "--version",
    action="store_true",
    dest="v",
    help="returns current doculog version"
)

parser.add_argument("-ow", "--overwrite",
    action="store_true",
    dest="ow",
    help="Overwrites existing changelog"
)

def update_logger():
    # We want all messages to be displayed
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(handler)

def parse():
    args = vars(parser.parse_args())

    # When working with CLI we want logs to be in a place a user can see
    # To file: doculog > output.log
    # else just displays to sys.sdout
    update_logger()

    # if args["cl"]:
    #    # Called when --cl or -change-log flag is used
    #    generate_changelog()

    if args["v"]:
        print(f"v{__version__}")

    logger.debug("Generating changelog")
    generate_changelog(args["ow"])

    exit(0)
