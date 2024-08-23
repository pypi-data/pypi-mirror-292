"""The Solarflow Hub Device class."""

# -*- coding: utf-8 -*-

import json
import logging
import sys
from typing import Dict

from .ZendureABPack import ZendureABPack
from .ZendureDeviceBase import SolarflowDeviceBase

FORMAT = "%(asctime)s:%(levelname)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level="INFO", format=FORMAT)
log = logging.getLogger("")


class ZendureSolarflowHub(SolarflowDeviceBase):
    """The Solarflow Hub Device class."""

    outputPackPower: int = 0
    outputHomePower: int = 0
    packInputPower: int = 0
    solarPower1: int = 0
    solarPower2: int = 0
    solarInputPower: int = 0
    packNum: int = 0
    outputLimit: int = 0
    inputLimit: int = 0
    inverseMaxPower: int = 0
    buzzerSwitch: int = 0
    minSoc: int = 0
    socSet: int = 0
    remainOutTime: int = 59940
    remainInputTime: int = 59940
    inputMode: int = 0
    passMode: int = 1
    autoRecover: int = 0
    gridPower: int = 0

    """ masterSwitch = 0
    wifiState = 0
    socSet = 0
    solarInputPower = 0
    packInputPower = 0
    outputPackPower = 74
    outputHomePower = 46
    outputLimit = 800    
    packState = 1
    hubState = 1
    masterSoftVersion = 8232
    masterhaerVersion = 0
    inputMode = 0
    blueOta = 1
    pvBrand = 1
    minSoc = 50    
    autoModel = 0
    gridPower = 0
    smartMode = 0
    smartPower = 0
    passMode = 1
    autoRecover = 0
    masterSwitch = 1
    buzzerSwitch = 0
    socSet = 1000
    solarInputPower = 115
    packInputPower = 0
    outputPackPower = 67
    outputHomePower = 44
    outputLimit = 800
    inputLimit = 0
    remainOutTime = 604
    remainInputTime = 59940
    packState = 1
    hubState = 1
    masterSoftVersion = 8232
    masterhaerVersion = 0
    inputMode = 0
    blueOta = 1
    pvBrand = 1
    autoModel = 0
    gridPower = 0
    smartMode = 0
    smartPower = 0 """

    packData: Dict[str, ZendureABPack] = {}

    def _update(self, data):
        super()._update(data)
        log.debug("Update Zendure Solarflow Hub " + self.__repr__())

        if "outputPackPower" in data:
            self.outputPackPower = data["outputPackPower"]

            if self.outputPackPower > 0:
                self.packInputPower = 0

        if "outputHomePower" in data:
            self.outputHomePower = data["outputHomePower"]

        if "solarPower1" in data:
            self.solarPower1 = data["solarPower1"]

        if "solarPower2" in data:
            self.solarPower2 = data["solarPower2"]

        if "solarInputPower" in data:
            self.solarInputPower = data["solarInputPower"]

        if "packInputPower" in data:
            self.packInputPower = data["packInputPower"]

            if self.packInputPower > 0:
                self.outputPackPower = 0

        if "packNum" in data:
            self.packNum = data["packNum"]

        if "outputLimit" in data:
            self.outputLimit = data["outputLimit"]

        if "inputLimit" in data:
            self.inputLimit = data["inputLimit"]

        if "inverseMaxPower" in data:
            self.inverseMaxPower = data["inverseMaxPower"]

        if "buzzerSwitch" in data:
            self.buzzerSwitch = data["buzzerSwitch"]

        if "minSoc" in data:
            self.minSoc = data["minSoc"] / 10

        if "socSet" in data:
            self.socSet = data["socSet"] / 10

        if "remainOutTime" in data:
            self.remainOutTime = data["remainOutTime"]

        if "remainInputTime" in data:
            self.remainInputTime = data["remainInputTime"]

        if "inputMode" in data:
            self.inputMode = data["inputMode"]

        if "passMode" in data:
            self.passMode = data["passMode"]

        if "autoRecover" in data:
            self.autoRecover = data["autoRecover"]

        if "gridPower" in data:
            self.gridPower = data["gridPower"]

    def _updatePackData(self, packdata):
        if packdata is None:
            return

        log.debug("Update Pack for Zendure Solarflow Hub " + self.__repr__())

        for _pack in packdata:
            if _pack["sn"] in self.packData.keys():
                # Pack is already in list
                pack = self.packData[_pack["sn"]]
                pack._update(pack)
            else:
                # Pack is not in list
                pack = ZendureABPack(_pack)
                self.packData[_pack["sn"]] = pack

    def setOutputlimit(self, outputlimit: int):
        if self.productKey and self.deviceKey and outputlimit:
            outputlimitdata = {"properties": {"outputLimit": outputlimit}}
            self._mqttClient.publish(
                f"iot/{self.productKey}/{self.deviceKey}/properties/write",
                json.dumps(outputlimitdata),
            )

    def setBuzzerSwitch(self, value: bool):
        buzzerSwitch = {"properties": {"buzzerSwitch": 0 if not value else 1}}
        self._mqttClient.publish(
            f"iot/{self.productKey}/{self.deviceKey}/properties/write",
            json.dumps(buzzerSwitch),
        )

    def setAutorecoverSwitch(self, value: bool):
        autorecoverSwitch = {"properties": {"autoRecover": 0 if not value else 1}}
        self._mqttClient.publish(
            f"iot/{self.productKey}/{self.deviceKey}/properties/write",
            json.dumps(autorecoverSwitch),
        )

    def setBypassSwitch(self, value: bool):
        passmodeSwitch = {"properties": {"passMode": 2 if value else 1}}
        self._mqttClient.publish(
            f"iot/{self.productKey}/{self.deviceKey}/properties/write",
            json.dumps(passmodeSwitch),
        )

    def setDischargeLimit(self, dischargelimit: int):
        dischargelimitdata = {"properties": {"minSoc": dischargelimit * 10}}
        self._mqttClient.publish(
            f"iot/{self.productKey}/{self.deviceKey}/properties/write",
            json.dumps(dischargelimitdata),
        )

    def setChargeLimit(self, chargelimit: int):
        chargelimitdata = {"properties": {"socSet": chargelimit * 10}}
        self._mqttClient.publish(
            f"iot/{self.productKey}/{self.deviceKey}/properties/write",
            json.dumps(chargelimitdata),
        )
