import requests
import json

class Http_commands:
    def __init__(self):
        print("Http_commands created.")

    def post(self,target, payLoad, type):
        request = requests.post(target, json=payLoad, headers={"Content-Type": "application/"+type})

        return request

    def put(self,target,jsonLoad):
        return requests.put(target, json=jsonLoad)
    def get(self,target):
        return requests.get(target)

