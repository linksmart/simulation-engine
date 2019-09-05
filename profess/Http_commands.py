import requests
import json
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Http_commands:
    def __init__(self):
        logging.debug("Http_commands created.")


    def post(self,target, payLoad, type):
        """
        :param target: target domain
        :param payLoad: payload
        :param type: which type the payload has, for example: json
        :return:
        """
        request = requests.post(target, json=payLoad, headers={"Content-Type": "application/"+type})

        return request

    def put(self, target, payLoad):
        """
        :param target: target domain
        :param payLoad:
        :return:
        """
        return requests.put(target, json=payLoad)
    def get(self,target):
        """

        :param target: target domain
        :return:
        """
        logging.debug("get "+target)
        return requests.get(target)

