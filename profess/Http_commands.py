import requests
import json
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Http_commands:
    def __init__(self):
        print("Http_commands created.")
        logging.debug("Http_commands created.")


    def post(self,target, payLoad, type):
        request = requests.post(target, json=payLoad, headers={"Content-Type": "application/"+type})

        return request

    def put(self,target,jsonLoad):
        return requests.put(target, json=jsonLoad)
    def get(self,target):
        logging.debug("get "+target)
        return requests.get(target)

