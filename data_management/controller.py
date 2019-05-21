import logging
import json

from simulator.openDSS import OpenDSS
#from simulation_management import simulation_management as SM

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class gridController:

    def __init__(self, id):
        super(gridController, self).__init__()
        logger.info("Initializing simulation controller")
        self.sim = OpenDSS("S4G Simulation")
        self.id = id
        self.nodeNames =[]
        self.allBusMagPu=[]
        self.yCurrent = []
        self.losses = []

    def setNewCircuit(self, name):
        logger.debug("Creating a new circuit with the name: "+str(name))
        self.sim.setNewCircuit(name)
        logger.debug("New circuit created")

    def enableCircuit(self, name):
        logger.debug("Enabling the circuit with the name: "+str(name))
        self.sim.enableCircuit(name)
        logger.debug("Circuit "+str(name)+" enabled")

    def setParameters(self, id, duration):
        self.id = id
        self.duration = duration

    def getId(self):
        return self.id

    def getDuration(self):
        return self.duration

    def disableCircuit(self, name):
        logger.debug("Disabling the circuit with the name: "+str(name))
        self.sim.disableCircuit(name)
        logger.debug("Circuit "+str(name)+" disabled")

    def setLoads(self, id, object):
        self.object=object
        logger.debug("Charging loads into the simulator")
        self.sim.setLoads(self.object)
        logger.debug("Loads charged")

    def setTransformers(self, id, object):
        logger.debug("Charging transformers into the simulator")
        self.object = object
        self.sim.setTransformers(self.object)
        logger.debug("Transformers charged")

    def setPowerLines(self, id, powerlines): #(self, id, powerlines, linecodes):
        logger.debug("Charging power lines into the simulator")
        #self.sim.setLineCodes(linecodes)
        self.sim.setPowerLines(powerlines)
        logger.debug("Power lines charged")
        
    def setCapacitors(self, id, capacitors):
        logger.debug("Charging capacitors into the simulator")
        #self.object = object
        #self.sim.setCapacitors(self.object)
        self.sim.setCapacitors(capacitors)
        logger.debug("Capacitor charged")
    def setLineCodes(self, id, linecode):
        logger.debug("Charging LineCode into the simulator")
        #self.object = object
        #self.sim.setLineCodes(self.object)
        self.sim.setLineCodes(linecode)
        logger.debug("LineCode charged")

    def setXYCurve(self, id, npts, xarray, yarray):
        logger.debug("Setting the XYCurve into the simulator")
        self.object = object
        self.sim.setXYCurve(self.object)
        logger.debug("XYCurve set")

    def setPhotovoltaic(self, id, photovoltaics, xycurves, loadshapes, tshapes):
        logger.debug("Charging the photovoltaics into the simulator")
        self.sim.setXYCurves(xycurves)
        self.sim.setLoadshapes(loadshapes)
        logger.debug("Tshape: "+str(tshapes))
        self.sim.setTshapes(tshapes)
        self.sim.setPhotovoltaics(photovoltaics)
        logger.debug("Photovoltaics charged")

    def setStorage(self, id, storage):
        logger.debug("Charging the ESS into the simulator")
        self.sim.setStorages(storage)
        logger.debug("ESS charged")

    def setChargingPoints(self, id, object):
        logger.debug("Charging the charging points into the simulator")
        self.object = object
        self.sim.setChargingPoints(self.object)
        logger.debug("Charging points charged")

    def run(self):#self, id, duration):
        #self.id = id
        #self.duration = duration

        logger.debug("Simulation of grid " + self.id + " started")
        logger.debug("These are the parameters")
        logger.debug("GridID: "+str(self.id))
        """logger.debug("Duration: "+str(self.duration))

        day = self.duration.to_dict()["day"]
        logger.debug("Days: "+str(day))
        month= self.duration.to_dict()["month"]
        logger.debug("Months: " + str(month))
        year = self.duration.to_dict()["year"]
        logger.debug("year: " + str(year))
        if day is 0 and month is 0 and year is 0:
            return "Duration is no present"
        if day > 0:
            numSteps=1440*day
        elif month > 0:
            numSteps=1440*30*month
        elif year > 0:
            numSteps = 365

        #self.sim.runNode13()"""
        self.sim.enableCircuit(self.id)

        logger.debug("Active circuit: "+str(self.sim.getActiveCircuit()))
        #return "ok"
        ##################################################################################PROBLEM################################
        logger.info("Solution mode: "+str(self.sim.getMode()))
        logger.info("Solution step size: " + str(self.sim.getStepSize()))
        logger.info("Number simulations: " + str(self.sim.getNumberSimulations()))
        logger.info("Voltage bases: " + str(self.sim.getVoltageBases()))
        self.sim.setMode("snap")
        logger.info("Solution mode 2: " + str(self.sim.getMode()))
        self.sim.setStepSize("minutes")
        #logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
        self.sim.setNumberSimulations(1)
        logger.info("Number simulations 2: " + str(self.sim.getNumberSimulations()))
        self.sim.setVoltageBases(115,4.16,0.48)
        logger.info("Voltage bases: " + str(self.sim.getVoltageBases()))
        logger.info("Starting Hour : " + str(self.sim.getStartingHour()))
        self.sim.setVoltageBases()
        numSteps= 100
        logger.info("Number of steps: "+str(numSteps))
        for i in range(numSteps):
            nodeNames, allBusMagPu, yCurrent, losses = self.sim.solveCircuitSolution()
        logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
        logger.info("Node Names: "+ str(nodeNames))
        logger.info("All Bus MagPus: " + str(allBusMagPu))
        #!TODO: return node names, voltage and current in json
        #data = {"NodeNames": nodeNames, "Voltage": allBusMagPu}
        #return json.dumps(data)
        logger.info("YCurrent: " + str(yCurrent))
        logger.info("losses: " + str(losses))
        #return ("Nodes: " + str(nodeNames), "\nVoltages " + str(allBusMagPu))
        #return (nodeNames, allBusMagPu)
        #filename = str(id)+"_results.txt"
        filename = '/usr/src/app/tests/results/results.txt'
        f = open(filename, 'w')
        f.writelines("Nodes: " + str(nodeNames)+"\n")
        f.writelines("Voltages: " + str(allBusMagPu))
        
        logger.info("File "+filename+" written")
        f.close()
        return id
    
    #def results(self):   
        #return (self.nodeNames, self.allBusMagPu)
        #self.finish_status = True
        #return "OK"
        """#ToDo test with snap and daily
        self.sim.setMode("daily")
        self.sim.setStepSize("minutes")
        self.sim.setNumberSimulations(1)
        self.sim.setStartingHour(0)
        self.sim.setVoltageBases(0.4,16)

        #for i in range(numSteps):
            #self.sim.solveCircuitSolution()
            #setStorageControl()
            #If
            #DSSSolution.Converged
            #Then
            #V = DSSCircuit.AllBusVmagPu"""
