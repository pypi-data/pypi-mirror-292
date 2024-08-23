#!/usr/bin/env python
"""A simple CLI tool."""
# -*- coding: utf-8 -*-

from __future__ import print_function
import configparser
import logging
import argparse
import sys

from PyZendureSolarflow.PyZendureSolarflow import PyZendureSolarflow

FORMAT = "%(asctime)s:%(levelname)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level="INFO", format=FORMAT)
log = logging.getLogger("")
config: configparser.ConfigParser


def main(args=None):
    """Enter the main function of the CLI tool."""
    parser = argparse.ArgumentParser(description="Zendure Solarflow CLI tool.")
    parser.add_argument(
        "-v", action="store_true", dest="verbose", help="be more verbose"
    )
    parser.add_argument(
        "-l",
        "--location",
        type=str,
        dest="location",
        help="Zendure Account Location",
        default="global",
    )
    parser.add_argument(
        "-u", "--username", type=str, dest="username", help="Zendure Account Username"
    )
    parser.add_argument(
        "-p", "--password", type=str, dest="password", help="Zendure Account Password"
    )

    args = parser.parse_args(args)
    config = load_config()

    username = config.get("global", "username", fallback=None) or args.username

    password = config.get("global", "password", fallback=None) or args.password

    location = config.get("global", "location", fallback=None) or args.location

    logging.basicConfig()
    if args.verbose:
        logging.getLogger("PyZendureSolarflow").setLevel(logging.DEBUG)

    zendureapi = None
    try:
        zendureapi = PyZendureSolarflow(
            username=username, password=password, location=location
        )
        zendureapi.login()
    finally:
        log.error("PyZendureSolarflow stopped!")


def load_config():
    config = configparser.ConfigParser()
    try:
        with open("config.ini", "r") as cf:
            config.read_file(cf)
    except:
        log.info("No configuration file (config.ini) found! Using input args")
    return config


if __name__ == "__main__":
    main()
