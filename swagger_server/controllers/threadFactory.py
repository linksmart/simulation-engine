
import os
import logging
import configparser
import json

from data_management.controller import gridController

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class ThreadFactory:

    def __init__(self, id, duration):
        self.id = id
        self.duration = duration

        #self.initializeGridController()



    def setParameters(self, id, duration):
        self.id = id


    def getId(self):
        return self.id



    def startController(self):

        logger.info("Creating se controller thread")

        self.gridController = gridController(self.id, self.duration)
        # Initializing constructor of the optimization controller thread
        #self.gridController=self.redisDB.get("controller: " + id)
        #logger.debug("This is the gridController in Threadfactory: "+str(self.gridController))
        try:

            logger.debug("Starting thread")
            self.gridController.start()

            return 0

        except Exception as e:
            logger.error(e)
            return 1
        #logger.debug("Simulation Engine object started")

    def stopControllerThread(self):
        try:
            # stop as per ID
            logger.info("Stopping controller thread")
            self.gridController.Stop()

            #self.gridController.Stop(self.id)
            logger.info("controller thread stopped")
            return " controller thread stopped"
        except Exception as e:
            logger.error(e)
            return e

    def is_running(self):
        return self.gridController.get_finish_status()