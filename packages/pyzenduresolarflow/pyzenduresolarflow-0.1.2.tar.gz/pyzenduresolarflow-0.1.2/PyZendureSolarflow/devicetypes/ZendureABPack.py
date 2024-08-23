"""The Solarflow Battery class."""

# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import sys

FORMAT = "%(asctime)s:%(levelname)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level="INFO", format=FORMAT)
log = logging.getLogger("")


class ZendureABPack:
    """The Solarflow Battery class."""

    sn: str = None
    type: str = None
    socLevel: int = 0
    power: int = 0
    maxTemp: int = 0
    minVol: float = 0.0
    maxVol: float = 0.0
    totalVol: float = 0.0

    def __init__(self, data):
        """Create an entity base object."""
        if data is None:
            return

        self._update(data)

    def __repr__(self):
        """Return a string."""
        return "{type}: {sn}".format(
            type=self.type,
            sn=self.sn,
        )

    def _update(self, data):
        if "sn" in data.keys():
            self.sn = data["sn"]
            if self.sn[0] == "C":
                # It's a AB2000
                self.type = "AB2000"

            elif self.sn[0] == "A":
                # It's a AB1000
                self.type = "AB1000"

        if "socLevel" in data:
            self.socLevel = data["socLevel"]

        if "power" in data:
            self.power = data["power"]

        if "maxTemp" in data:
            self.maxTemp = data["maxTemp"]

        if "minVol" in data:
            self.minVol = data["minVol"]

        if "maxVol" in data:
            self.maxVol = data["maxVol"]

        if "totalVol" in data:
            self.totalVol = data["totalVol"]

        log.debug("Updated battery " + self.__repr__())
