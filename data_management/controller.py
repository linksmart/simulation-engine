import logging

from simulator.openDSS import OpenDSS
#from simulation_management import simulation_management as SM

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class gridController:

    def __init__(self):
        logger.debug("Grid Controller created")
        self.sim = OpenDSS("Test 1")

    def setLoads(self, object):
        self.object=object
        logger.debug("Creating an instance of the simulator")
        logger.debug("Charging the loads into the simulator")
        self.sim.setLoads(self.object)
        logger.debug("Loads charged")

    def runSimulation(self, gridId, duration, thres_High, thres_Medium, thres_Low):
        self.gridID = gridId
        self.duration = duration
        self.thres_High = thres_High
        self.thres_Medium = thres_Medium
        self.thres_Low = thres_Low
        logger.debug("Simulation of grid " + self.gridID + " started")
        logger.debug("These are the parameters")
        logger.debug("GridID: "+str(self.gridID))
        logger.debug("Duration: "+str(self.duration))
        logger.debug("Thresholds: "+str(self.thres_High)+str(self.thres_Medium)+str(self.thres_Low))
        day = self.duration.to_dict()["day"]
        month= self.duration.to_dict()["month"]
        year = self.duration.to_dict()["year"]
        if day > 0:
            numSteps=1440*day
        elif month > 0:
            numSteps=1440*30*month
        elif year > 0:
            numSteps = 365

        #self.sim.setSolveMode("snap")
        listNames, listValues = self.sim.solveCircuitSolution()
        return (listNames, listValues)
        """#ToDo test with snap and daily
        self.sim.setMode("daily")
        self.sim.setStepSize("minutes")
        self.sim.numberSimulations(1)
        self.sim.setStartingHour(0)
        self.sim.setVoltageBases(0.4,16)
"""
        #for i in range(numSteps):
            #self.sim.solveCircuitSolution()
            #setStorageControl()
            #If
            #DSSSolution.Converged
            #Then
            #V = DSSCircuit.AllBusVmagPu
