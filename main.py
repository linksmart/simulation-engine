"""
 Created by Gustavo Aragón on 14.03.2018

"""

import logging, time
import swagger_server.wsgi as webserver
#import swagger_server.__main__ as webserver

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

"""
Get the address of the data.dat
"""

def main():

    logger.info("Simulation Engine started")

    logger.info("Starting the webserver")
    webserver.main()
    #webserver.main()




if __name__ == "__main__":
        # execute only if run as a script
        main()