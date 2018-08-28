
import os
import logging
import configparser
import json

from data_management.controller import gridController

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class ThreadFactory:

    def __init__(self, id):
        self.gridController=gridController(id)

    def setParameters(self, id, duration):
        self.id = id
        self.duration = duration

    def getId(self):
        return self.id

    def getDuration(self):
        return self.duration

    def startController(self, duration):
        self.duration=duration
        logger.info("Creating se controller thread")
        logger.info("Duration: " + str(self.duration))


        # Initializing constructor of the optimization controller thread
        #self.gridController=self.redisDB.get("controller: " + id)
        logger.debug("This is the gridController in Threadfactory: "+str(self.gridController))
        try:
            self.gridController.duration=self.duration
            listNames, listValues = self.gridController.run()
            return (listNames,listValues)

        except Exception as e:
            logger.error(e)
            return e
        #logger.debug("Simulation Engine object started")

    def stopController(self):
        try:
            # stop as per ID
            for name, obj in self.prediction_threads.items():
                obj.Stop()
            for name, obj in self.non_prediction_threads.items():
                obj.Stop()
            logger.info("Stopping controller thread")
            self.gridController.Stop(self.id)
            logger.info("controller thread stopped")
            return " controller thread stopped"
        except Exception as e:
            logger.error(e)
            return e

    def is_running(self):
        return not self.gridController.finish_status