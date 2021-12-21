import requests
import time
import base64
import json

import xbmc


class HRTiAPI:
    user_agent = "kodi plugin for hrti.hrt.hr (python)"

    def __init__(self, username, password, plugin):
        self.plugin = plugin
        self._auth = None
        self.logged_in = False
        self.__username = username
        self.__password = password
        self.__ip = self.get_ip()
        self.device_id = plugin.uniq_id()
        xbmc.log("hrti init with IP: " + str(self.__ip), level=xbmc.LOGDEBUG)

    @staticmethod
    def get_ip():
        url = "https://hrti.hrt.hr/api/api/ott/getIPAddress"
        r = requests.get(url)
        return r.json()

    def grant_access(self):
        url = "https://hrti.hrt.hr/api/api/ott/GrantAccess"
        payload = {'username': self.__username, 'password': self.__password, 'OperatorReferenceId': 'hrt'}
        headers = {'Content-Type': 'application/json',
                   'DeviceId': '',
                   'DeviceTypeId': 6,
                   'Host': 'hrti.hrt.hr',
                   'IPAddress': self.__ip,
                   'OperatorReferenceId': 'hrt',
                   'Origin': 'https://hrti.hrt.hr',
                   'Referer': 'https://hrti.hrt.hr/signin'}
        self._auth = None
        r = requests.post(url, data=payload, headers=headers)
        if r.status_code == 200:
            self._auth = r.json()
            self.logged_in = True
            xbmc.log("hrti grant access: " + str(self._auth), level=xbmc.LOGDEBUG)
            self._auth["expires"] = time.time() + self._auth["expires_in"]
        return r.status_code
