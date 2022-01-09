import json
import requests


class APIVRM:
    def __init__(self):
        self.urlbase = 'https://vrmapi.victronenergy.com/v2/'
        self.urllogin = f'{self.urlbase}auth/login'

        self.loginfo = {
            "username": "luis.gonzalezvilas@artov.ismar.cnr.it",
            "password": "Garda_21"
        }
        self.token = None
        self.idUser = None
        self.auth_header = None

        self.login()

        self.auth_header = {
            "X-Authorization": f"Bearer {self.token}"
        }

    def login(self):
        response = requests.post(self.urllogin, json=self.loginfo)
        if response.ok:
            jresponse = response.json()
            self.token = jresponse['token']
            self.idUser = jresponse['idUser']

    def get_info_installation(self, name):
        url = f'{self.urlbase}users/{self.idUser}/installations?extended=1'
        response = requests.get(url, headers=self.auth_header)
        if response.json()['success']:
            for r in response.json()['records']:
                if r['name'] == name:
                    return r
        return None

    def get_idsite(self,name):
        idSite = -1
        info = self.get_info_installation(name)
        if not info is None:
            idSite = info['idSite']
        return idSite

    def get_devices_installation(self, name, idSite):
        if idSite == -1 and not name is None:
            idSite = self.get_idsite(name)
        if idSite == -1:
            return None
        url = f'{self.urlbase}installations/{idSite}/system-overview'
        response = requests.get(url, headers=self.auth_header)
        print(response.json())
        if response.json()['success']:
            return response.json()['records']['devices']
        return None

    def get_diagnose_installation(self,name,idSite):
        if idSite == -1 and not name is None:
            idSite = self.get_idsite(name)
        if idSite == -1:
            return None
        url = f'{self.urlbase}installations/{idSite}/diagnostics?count=1000'
        response = requests.get(url, headers=self.auth_header)
        if response.json()['success']:
            return response.json()['records']
        return None