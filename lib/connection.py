import requests
import json
import grequests


class BackendConnection:

    def __init__(self):
        self.MAIN_URL = "http://176.107.133.21:8090/api/v1/users"
        self.uid = "5cd5f75a50805d51d06b25bb"
        (self.usr, self.pwd) = ("", "")
        self.logged = False

    def save_pulse(self, pulse, callback):
        userid = self.uid
        username, password = self.usr, self.pwd
        url = self.MAIN_URL + "/" + userid + "/pulses"
        data = {"pulse": pulse}
        headers = {"Content-Type": "application/json"}
        req = [grequests.post(url, data=json.dumps(data), headers=headers, auth=(username, password),
                              hooks={'response': callback})]
        grequests.map(req)

    def save_emotions(self, emotions, callback):
        userid = self.uid
        username, password = self.usr, self.pwd
        url = self.MAIN_URL + "/" + userid + "/emotions"
        print(emotions)
        data = {"anger": float(emotions[0]), "disgust": float(emotions[1]), "fear": float(emotions[2]),
                "happiness": float(emotions[3]), "sadness": float(emotions[4]), "surprise": float(emotions[5])}
        headers = {"Content-Type": "application/json"}
        req = [grequests.post(url, data=json.dumps(data), headers=headers, auth=(username, password),
                              hooks={'response': callback})]
        grequests.map(req)

    def get_pulse(self):
        userid = self.uid
        username = self.usr
        password = self.pwd
        url = self.MAIN_URL + "/" + userid + "/pulses"
        req = requests.get(url, auth=(username, password))
        return req

    def register_user(self, username, password):
        url = self.MAIN_URL
        data = {"name": username, "password": password}
        headers = {"Content-Type": "application/json"}
        req = requests.post(url, data=json.dumps(data), headers=headers)
        return req

    def get_user_id(self, callback1):
        username, password = self.usr, self.pwd
        url = self.MAIN_URL + "/" + username + "/byName"
        req = [grequests.get(url, auth=(username, password), hooks={'response': callback1})]
        grequests.map(req)

    def get_status(self):
        return self.logged

    def login(self, username, password, call):
        self.usr = username
        self.pwd = password

        self.get_user_id(call)

    def set_user_id(self, uid):
        self.uid = uid
