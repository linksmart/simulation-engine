#!/usr/bin/env python3

import connexion
import logging

from connexion.resolver import RestyResolver
from flask_cors import CORS

from swagger_server import encoder


def create_app():
    logging.getLogger('connexion.operation').setLevel('ERROR')
    app = connexion.App(__name__, specification_dir='./swagger/')
    CORS(app.app) #TODO: Test if it resolves CORS issue
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'DSF-SE API'})
    return app

def main():
    #application=create_app()
    create_app().run(port=9090)


if __name__ == '__main__':
    create_app()
    #main()

