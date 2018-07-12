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

    def runSimulation(self, gridId, duration):
        self.gridID = gridId
        self.duration = duration

        logger.debug("Simulation of grid " + self.gridID + " started")
        logger.debug("These are the parameters")
        logger.debug("GridID: "+str(self.gridID))
        logger.debug("Duration: "+str(self.duration))

        day = self.duration.to_dict()["day"]
        month= self.duration.to_dict()["month"]
        year = self.duration.to_dict()["year"]
        if day > 0:
            numSteps=1440*day
        elif month > 0:
            numSteps=1440*30*month
        elif year > 0:
            numSteps = 365

        self.sim.runNode13()
        logger.info("Solution mode: "+str(self.sim.getMode()))
        logger.info("Solution step size: " + str(self.sim.getStepSize()))
        logger.info("Number simulations: " + str(self.sim.getNumberSimulations()))
        logger.info("Voltage bases: " + str(self.sim.getVoltageBases()))
        self.sim.setMode("daily")
        logger.info("Solution mode 2: " + str(self.sim.getMode()))
        #self.sim.setStepSize("minutes")
        #logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
        self.sim.setNumberSimulations(1)
        logger.info("Number simulations 2: " + str(self.sim.getNumberSimulations()))
        self.sim.setVoltageBases(115,4.16,0.48)
        logger.info("Voltage bases: " + str(self.sim.getVoltageBases()))
        logger.info("Starting Hour : " + str(self.sim.getStartingHour()))
        #self.sim.setVoltageBases()
        numSteps=100
        logger.info("Number of steps: "+str(numSteps))
        for i in range(numSteps):
            listNames, listValues = self.sim.solveCircuitSolution()
        logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
        return (listNames, listValues)
        #return "OK"
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
