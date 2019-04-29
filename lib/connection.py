import requests
import json
import grequests

class BackendConnection:

    def __init__(self):
        self.MAIN_URL = "http://192.168.1.162:8090/api/v1/users"
        self.uid = "5cc4dfe523d29335f6f733da"
        (self.usr, self.pwd) = ("adam2", "adam")
        self.logged = True

    def save_pulse(self, pulse):
        userid = self.uid
        username, password = self.usr, self.pwd
        url = self.MAIN_URL + "/" + userid + "/pulses"
        data = {"pulse": pulse}
        headers = {"Content-Type": "application/json"}
        #req = requests.post(url, data=json.dumps(data), headers=headers, auth=(username, password))
        req = grequests.post(url, data=json.dumps(data), headers=headers, auth=(username, password), callback=callback)
        res = grequests.send(req, grequests.Pool(1))
        return res

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

    def get_user_id(self):
        #self.uid = "5cc4a94abf41a2029907f8e1"
        username, password = self.usr, self.pwd
        url = self.MAIN_URL + "/" + username + "/byName"
        print(url)
        req = requests.get(url, auth=(username, password))
        return req

    def get_status(self):
        return self.logged

    def login(self, username, password):
        if username == self.usr and password == self.pwd:
            return True
        else:
            return False

def callback(response, **kwargs):
    print("UDALO SIE!", response.content)