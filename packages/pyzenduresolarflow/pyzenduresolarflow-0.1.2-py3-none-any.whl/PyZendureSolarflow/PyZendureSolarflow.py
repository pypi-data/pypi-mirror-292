import logging
import sys
import json
import base64
from typing import Dict
from paho.mqtt import client as mqtt_client

from PyZendureSolarflow.ZendureHttpApi import ZendureHttpAPI
from PyZendureSolarflow.devicetypes import (
    ZendureAce,
    ZendureAio,
    ZendureHyper,
    ZendureSolarflowHub,
)

FORMAT = "%(asctime)s:%(levelname)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level="INFO", format=FORMAT)
log = logging.getLogger("")

"""Connection Parameter"""

hostname = "app.zendure.tech"
versionGlobal = "v2"
versionEu = "eu"
solarFlowDevRegisterPath = "developer/api/apply"
solarFlowTokenPath = "auth/app/token"
solarFlowDeviceListPath = "productModule/device/queryDeviceListByConsumerId"

parameterEu = {
    "solarFlowDevRegisterUrl": f"https://{hostname}/{versionEu}/{solarFlowDevRegisterPath}",
    "solarFlowTokenUrl": f"https://{hostname}/{versionEu}/{solarFlowTokenPath}",
    "solarFlowQueryDeviceListUrl": f"https://{hostname}/{versionEu}/{solarFlowDeviceListPath}",
    "mqttUrl": "mqtteu.zen-iot.com",
    "mqttPort": 1883,
    "mqttUser": "zenApp",
    "mqttPassword": "SDZzJGo5Q3ROYTBO",
}

parameterGlobal = {
    "solarFlowDevRegisterUrl": f"https://{hostname}/{versionGlobal}/{solarFlowDevRegisterPath}",
    "solarFlowTokenUrl": f"https://{hostname}/{versionGlobal}/{solarFlowTokenPath}",
    "solarFlowQueryDeviceListUrl": f"https://{hostname}/{versionGlobal}/{solarFlowDeviceListPath}",
    "mqttUrl": "mq.zen-iot.com",
    "mqttPort": 1883,
    "mqttUser": "zenApp",
    "mqttPassword": "b0sjUENneTZPWnhk",
}


class PyZendureSolarflow:
    _token = None
    _location_: str = None
    _username: str = None
    _password: str = None
    _client: mqtt_client.Client = None
    _devices: Dict[str, any] = None
    _templates: Dict[str, any] = None

    def __init__(self, username, password, location="global", debug=False):
        """Create a PyZendureSolarflow object."""
        self._location = location
        self._username = username
        self._password = password

        if debug == True:
            log.setLevel(level="DEBUG")

    def login(self):
        if not self._location or not self._username or not self._password:
            log.error("Missing parameters!")
            return

        if self._location == "eu":
            self._parameter = parameterEu
        else:
            self._parameter = parameterGlobal

        with ZendureHttpAPI(parameter=self._parameter) as zendureHttpApi:
            self._token = zendureHttpApi.authenticate(self._username, self._password)

            if self._devices is None:
                self._devices = {}

            if self._token:
                self._client = self.connect_zendure_mqtt(
                    token=self._token,
                    mqttUrl=self._parameter["mqttUrl"],
                    mqttPort=self._parameter["mqttPort"],
                    mqttUser=self._parameter["mqttUser"],
                    mqttPassword=base64.b64decode(
                        self._parameter["mqttPassword"]
                    ).decode("utf-8"),
                )

                devicelist = zendureHttpApi.get_device_list()
                for _device in devicelist:
                    device = None
                    if _device["productKey"] == "8bM93H":
                        # ACE 1500
                        device = ZendureAce(_device, self._client)
                        self._devices[device.deviceKey] = device
                    elif _device["productKey"] == "73bkTV":
                        # HUB 1200
                        device = ZendureSolarflowHub(_device, self._client)
                        self._devices[device.deviceKey] = device
                    elif _device["productKey"] == "A8yh63":
                        # HUB 2000
                        device = ZendureSolarflowHub(_device, self._client)
                        self._devices[device.deviceKey] = device
                    elif _device["productKey"] == "yWF7hV":
                        # AIO
                        device = ZendureAio(_device, self._client)
                        self._devices[device.deviceKey] = device
                    elif _device["productKey"] == "s3Xk4x":
                        # Smart Plug EU
                        device = None
                    elif _device["productKey"] == "gDa3tb":
                        # Hyper
                        device = ZendureHyper(_device, self._client)
                        self._devices[device.deviceKey] = device

                    if self._client and device:
                        self.subscribe(device.productKey, device.deviceKey)

                self._client.loop_start()
            else:
                log.error("Missing token!")

    def connect_zendure_mqtt(
        self, token, mqttUrl, mqttPort, mqttUser, mqttPassword
    ) -> mqtt_client:
        _mqtt_client = mqtt_client.Client(
            client_id=token, userdata="Zendure Production MQTT"
        )
        _mqtt_client.username_pw_set(username=mqttUser, password=mqttPassword)
        _mqtt_client.reconnect_delay_set(min_delay=1, max_delay=120)
        _mqtt_client.on_connect = self.on_connect
        _mqtt_client.on_disconnect = self.on_disconnect
        _mqtt_client.connect(mqttUrl, mqttPort)
        return _mqtt_client

    def subscribe(self, productKey: str, deviceKey: str):
        report_topic = f"/{productKey}/{deviceKey}/#"
        iot_topic = f"iot/{productKey}/{deviceKey}/#"
        self._client.subscribe(report_topic)
        self._client.subscribe(iot_topic)
        self._client.on_message = self.on_message

    def on_connect(self, client: mqtt_client.Client, userdata, flags, rc):
        if rc == 0:
            log.info(f"Connected to MQTT Broker: {userdata}")
        else:
            log.error("Failed to connect, return code %d\n", rc)

    def on_disconnect(self, client: mqtt_client.Client, userdata, rc):
        if rc != 0:
            log.warning("Disconnected from Zendure MQTT: " + str(rc))
            client.loop_stop()
            client.disconnect()

    def on_message(self, client: mqtt_client.Client, userdata, msg):
        payload = json.loads(msg.payload.decode())

        topicSplitted = msg.topic.split("/")
        deviceKey = topicSplitted[2]

        device = self._devices[deviceKey]

        if device:
            if "properties/report" in msg.topic and "properties" in payload:
                device._update(payload["properties"])

            if "packData" in payload:
                packdata = payload["packData"]
                if len(packdata) > 0:
                    device._updatePackData(packdata)
