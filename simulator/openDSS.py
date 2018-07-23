# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:05:36 2018

@author: garagon
"""


import logging
import opendssdirect as dss


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class OpenDSS:
    def __init__(self, grid_name):
        logger.info("Starting OpenDSS")
        logger.info("OpenDSS version: " + dss.__version__)
        self.grid_name=grid_name
        dss.run_command("Clear")
        dss.Basic.NewCircuit("Test 1")
        #dss.run_command("New circuit.{circuit_name}".format(circuit_name="Test 1"))

    def runNode13(self):
        dss.run_command('Redirect /usr/src/app/tests/data/13Bus/IEEE13Nodeckt.dss')

    def solveCircuitSolution(self):
        dss.Solution.Solve()
        #logger.info("Loads names: "+str(dss.Loads.AllNames()))
        #logger.info("Bus names: " + str(dss.Circuit.AllBusNames()))
        #logger.info("All Node names: " + str(dss.Circuit.AllNodeNames()))
        #logger.info("Length of Node Names: " + str(len(dss.Circuit.AllNodeNames())))
        #logger.info("Voltages: "+str(dss.Circuit.AllBusVolts()))
        #logger.info("Length of Bus Voltages: "+str(len(dss.Circuit.AllBusVolts())))
        #logger.info("Bus Voltages: "+ str(dss.Bus.Voltages()))
        #logger.info("Just magnitude of Voltages: "+str(dss.Circuit.AllBusVMag()))
        #logger.info("Length of Bus Voltages: " + str(len(dss.Circuit.AllBusVMag())))
        #logger.info("Just pu of Voltages: " + str(dss.Circuit.AllBusMagPu()))
        #logger.info("Length of Bus Voltages: " + str(len(dss.Circuit.AllBusMagPu())))
        return (dss.Circuit.AllNodeNames(),dss.Circuit.AllBusMagPu())
    #def getVoltages(self):


    #def setSolveMode(self, mode):
     #   self.mode=mode
      #  dss.run_command("Solve mode=" + self.mode)
    def getStartingHour(self):
        return dss.Solution.DblHour()

    def setStartingHour(self, hour):
        self.hour=hour
        dss.Solution.DblHour(self.hour)
        logger.debug("Starting hour "+str(dss.Solution.DblHour()))

    def getVoltageBases(self):
        return dss.Settings.VoltageBases()

    def setVoltageBases(self,V1=None,V2=None,V3=None,V4=None,V5=None):
        self.V1=V1
        self.V2=V2
        self.V3=V3
        self.V4=V4
        self.V5=V5
        #dss.Settings.VoltageBases(0.4,16)
        dss.run_command("Set voltagebases = [{value1},{value2},{value3},{value4},{value5}]".format(value1=self.V1,value2=self.V2,value3=self.V3,value4=self.V4,value5=self.V5))
        dss.run_command("calcv")
        #logger.debug("Voltage bases: "+str(dss.Settings.VoltageBases()))

    def solutionConverged(self):
        return dss.Solution.Coverged()

    def getMode(self):
        return dss.Solution.ModeID()

    def setMode(self, mode):
        self.mode = mode
        dss.run_command("Set mode="+self.mode)
        #logger.debug("Solution mode "+str(dss.Solution.ModeID()))

    def getStepSize(self):
        return dss.Solution.StepSize()
    #Options: minutes or hours
    def setStepSize(self, time_step):
        self.time_step=time_step
        if "minutes" in self.time_step:
            dss.Solution.StepSizeMin(1)
        if "hours" in self.time_step:
            dss.Solution.StepSizeHr(1)
        #logger.debug("Simulation step_size " + str(dss.Solution.StepSize()))

    def getNumberSimulations(self):
        return dss.Solution.Number()

    def setNumberSimulations(self, number):
        self.number=number
        dss.Solution.Number(self.number)
        logger.debug("Simulation number " + str(dss.Solution.Number()))
        #dss.run_command("Set number =" + self.number)

    def setLoads(self, loads):
        logger.debug("Setting up the loads")
        self.loads=loads
        try:
            for element in self.loads:
                for key, value in element.items():
                    logger.debug("Key: "+str(key)+" Value: "+str(value))
                    if key=="id":
                        load_name=value
                    elif key=="node1":
                        bus_name=value
                    elif key=="phases":
                        num_phases=value
                    elif key == "voltage":
                        voltage_kV = value
                    elif key == "powerfactor":
                        power_factor = value
                    elif key == "power_profile":
                        power_profile = value
                    else:
                        break
                self.setLoad(load_name, bus_name, num_phases, voltage_kV, power_factor, power_profile)

            dss.run_command('Solve')

            logger.info("Load names: " + str(dss.Loads.AllNames()))
        except Exception as e:
            logger.error(e)


    def setLoad(self, load_name, bus_name, num_phases=3, voltage_kV=0.4, power_factor=1, power_profile=None):
        self.load_name=load_name
        self.bus_name=bus_name
        self.num_phases=num_phases
        self.voltage_kV=voltage_kV
        self.power_factor=power_factor
        self.power_profile=power_profile

        dss.run_command(
            "New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn=Delta Model=1 kV={voltage_kV}   pf={power_factor} Daily={shape}".format(
                load_name=self.load_name,
                bus_name=self.bus_name,
                num_phases=self.num_phases,
                voltage_kV=self.voltage_kV,
                power_factor=self.power_factor,
                shape=self.power_profile
            ))


    def setTransformers(self, transformers):
        logger.debug("Setting up the transformers")
        self.transformers=transformers
        try:
            for element in self.transformers:
                for key, value in element.items():
                    logger.debug("Key: "+str(key)+" Value: "+str(value))
                    if key=="id":
                        transformer_name=value
                    elif key=="voltagePrimary":
                        voltage_primary=value
                    elif key=="voltageSecondary":
                        voltage_secondary=value
                    elif key == "voltageBasePrimary":
                        voltage_Base_Primary = value
                    elif key == "voltageBaseSecondary":
                        voltage_Base_Secondary = value
                    elif key == "powerPrimary":
                        power_Primary = value
                    elif key=="powerSecondary":
                        power_Secondary=value
                    elif key=="connection":
                        connection=value
                    elif key == "nodeHV":
                        node_HV = value
                    elif key == "nodeLV":
                        power_factor = value
                    elif key == "noLoadLoss":
                        power_profile = value
                    elif key == "Req":
                        power_profile = value
                    elif key=="Xeq":
                        voltage_primary=value
                    elif key=="CeqTotal":
                        voltage_secondary=value
                    elif key == "monitor":
                        voltage_kV = value
                    elif key == "control":
                        power_factor = value
                    elif key == "tapLevel":
                        power_profile = value
                    elif key == "voltageunit":
                        voltage_kV = value
                    elif key == "frequency":
                        power_factor = value
                    elif key == "unitpower":
                        power_profile = value
                    else:
                        break
                self.setTransformer(load_name, bus_name, num_phases, voltage_kV, power_factor, power_profile)

            dss.run_command('Solve')

            logger.info("Transformer names: " + str(dss.Transformers.AllNames()))
        except Exception as e:
            logger.error(e)


    def setTransformer(self, load_name, bus_name, num_phases=3, voltage_kV=0.4, power_factor=1, power_profile=None):
        self.load_name=load_name
        self.bus_name=bus_name
        self.num_phases=num_phases
        self.voltage_kV=voltage_kV
        self.power_factor=power_factor
        self.power_profile=power_profile

        dss.run_command(
            "New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn=Delta Model=1 kV={voltage_kV}   pf={power_factor} Daily={shape}".format(
                load_name=self.load_name,
                bus_name=self.bus_name,
                num_phases=self.num_phases,
                voltage_kV=self.voltage_kV,
                power_factor=self.power_factor,
                shape=self.power_profile
            ))