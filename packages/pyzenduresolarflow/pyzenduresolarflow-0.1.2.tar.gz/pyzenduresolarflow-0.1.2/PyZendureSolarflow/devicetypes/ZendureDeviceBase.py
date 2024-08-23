"""The base device class."""

# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import sys
from paho.mqtt import client as mqtt_client

FORMAT = "%(asctime)s:%(levelname)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level="INFO", format=FORMAT)
log = logging.getLogger("")


class SolarflowDeviceBase:
    """The Solarflow Device class."""

    _mqttClient: mqtt_client.Client = None

    id = None
    deviceKey: str = None
    snNumber: str = None
    namev = None
    productId = None
    productKey: str = None
    onlineFlag = None
    productName: str = None
    wifiStatus = None
    blueState = None
    fourGStatus = None
    isShareFlag = None
    input = None
    output = None
    soc = None  # electricity / electricLevel
    restState = None
    upsMode = None
    upgradeStatusDes = None
    productType = None
    upgradeStatus = None
    bindId = None
    bindStatus = None
    batteryCode = None
    packList = None
    inputPower = None
    outputPower = None
    slowChargePower = None
    temperature = None
    temperatureUnit = None
    remainOutTime = None
    bindType = None
    seriesMode = None
    parallelMode = None
    networkType = None
    standard = None
    isSwitch = None
    url = None
    remainOil = None
    genMode = None
    shortCode = None
    phaseCheck = None
    passMode = None  # pass
    clusterList = None
    clusterNotice = None
    nodeStatus = None
    clusterId = None
    phase = None
    reverseState = None

    def __init__(self, data, mqttclient):
        """Create an entity base object."""
        if data is not None:
            self.name = data["name"]
            self.productName = data["productName"]
            self.productKey = data["productKey"]
            self.deviceKey = data["deviceKey"]
            self.soc = data["electricity"]
            self.id = data["id"]
            self.snNumber = data["snNumber"]
            self.productId = data["productId"]
            self.onlineFlag = data["onlineFlag"]
            self.wifiStatus = data["wifiStatus"]
            self.blueState = data["blueState"]
            self.fourGStatus = data["fourGStatus"]
            self.isShareFlag = data["isShareFlag"]
            self.input = data["input"]
            self.output = data["output"]
            self.electricity = data["electricity"]
            self.restState = data["restState"]
            self.upsMode = data["upsMode"]
            self.upgradeStatusDes = data["upgradeStatusDes"]
            self.productType = data["productType"]
            self.upgradeStatus = data["upgradeStatus"]
            self.bindId = data["bindId"]
            self.bindStatus = data["bindStatus"]
            self.batteryCode = data["batteryCode"]
            self.packList = data["packList"]
            self.inputPower = data["inputPower"]
            self.outputPower = data["outputPower"]
            self.slowChargePower = data["slowChargePower"]
            self.temperature = data["temperature"]
            self.temperatureUnit = data["temperatureUnit"]
            self.remainOutTime = data["remainOutTime"]
            self.bindType = data["bindType"]
            self.seriesMode = data["seriesMode"]
            self.parallelMode = data["parallelMode"]
            self.networkType = data["networkType"]
            self.standard = data["standard"]
            self.isSwitch = data["isSwitch"]
            self.url = data["url"]
            self.remainOil = data["remainOil"]
            self.genMode = data["genMode"]
            self.shortCode = data["shortCode"]
            self.phaseCheck = data["phaseCheck"]
            self.clusterList = data["clusterList"]
            self.clusterNotice = data["clusterNotice"]
            self.nodeStatus = data["nodeStatus"]
            self.clusterId = data["clusterId"]
            self.phase = data["phase"]
            self.reverseState = data["reverseState"]
            self.passMode = data["pass"]
        else:
            log.error("Error creating device, data is empty!")

    def __repr__(self):
        """Return a string."""
        return "{productName}: {name}".format(
            productName=self.productName,
            name=self.name,
        )

    def _update(self, data):
        log.debug("Update base device" + self.__repr__())
        if "name" in data:
            self.name = data["name"]

        if "electricLevel" in data:
            self.soc = data["electricLevel"]

        if "wifiState" in data:
            self.wifiStatus = data["wifiState"]

    def _requestUpdate(self):
        if self.productKey and self.deviceKey:
            self._mqttClient.publish(
                f"iot/{self.productKey}/{self.deviceKey}/properties/read",
                '{"properties": ["getAll"]}',
            )
