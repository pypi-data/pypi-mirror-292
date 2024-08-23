import json
import logging
import sys
import requests
from requests.adapters import HTTPAdapter

FORMAT = "%(asctime)s:%(levelname)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level="INFO", format=FORMAT)
log = logging.getLogger("")


class ZendureHttpAPI:
    """An API class to handle communication with the Zendure API"""

    def __init__(self, parameter=None):
        self.parameter = parameter
        self.session = None

    def __enter__(self):
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=3)
        self.session.verify = True
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers = {
            "Content-Type": "application/json",
            "Accept-Language": "de-DE",
            "appVersion": "4.3.1",
            "User-Agent": "Zendure/4.3.1 (iPhone; iOS 14.4.2; Scale/3.00)",
            "Accept": "*/*",
            "Authorization": "Basic Q29uc3VtZXJBcHA6NX4qUmRuTnJATWg0WjEyMw==",
            "Blade-Auth": "bearer (null)",
        }
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()
        self.session = None

    def authenticate(self, username, password):
        authBody = {
            "password": password,
            "account": username,
            "appId": "121c83f761305d6cf7e",
            "appType": "iOS",
            "grantType": "password",
            "tenantId": "",
        }

        try:
            url = f'{self.parameter["solarFlowTokenUrl"]}'
            log.info("Authenticating with Zendure ...")
            response = self.session.post(url=url, json=authBody)
            if response.ok:
                respJson = response.json()
                token = respJson["data"]["accessToken"]
                self.session.headers["Blade-Auth"] = f"bearer {token}"
                return token
            else:
                log.error("Authentication failed!")
                log.error(response.text)
        except Exception as e:
            log.error(e)

    def get_device_list(self):
        try:
            url = f'{self.parameter["solarFlowQueryDeviceListUrl"]}'
            log.info("Getting device list ...")
            response = self.session.post(url=url)
            if response.ok:
                respJson = response.json()
                return respJson["data"]
            else:
                log.error("Fetching device list failed!")
                log.error(response.text)
        except Exception as e:
            log.error(e)
