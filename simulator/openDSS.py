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
        try:
            id = None
            phases = None
            winding = None
            xhl = None
            kvs = None
            kvas = None
            wdg = None
            bus = None
            connection = None
            kv = None
            for key, value in transformers.items():
                # logger.debug("Key: "+str(key)+" Value: "+str(value))
                if key == "id":
                    id = value
                if key == "phases":
                    phases = value
                if key == "winding":
                    winding = value
                if key == "xhl":
                    xhl = value
                if key == "kvs":
                    kvs = value
                if key == "kvas":
                    kvas = value
                if key == "wdg":
                    wdg = value
                if key == "bus":
                    bus = value
                if key == "connection":
                    connection = value
                if key == "kv":
                    kv = value

            #    if key == "voltagePrimary":
            #        voltagePrimary = value
            #    if key == "voltageSecondary":
            #        voltageSecondary = value
            #    if key == "voltageBasePrimary":
            #        voltageBasePrimary = value
            #    if key == "voltageBaseSecondary":
            #        voltageBaseSecondary = value
            #    if key == "powerPrimary":
            #        powerPrimary = value
            #    if key == "powerSecondary":
            #        powerSecondary = value
            #    if key == "nodeHV":
            #        nodeHV = value
            #    if key == "nodeLV":
            #        nodeLV = value
            #    if key == "noLoadLoss":
            #        noLoadLoss = value
            #    if key == "Req":
            #        Req = value
            #    if key == "Xeq":
            #        Xeq = value
            #    if key == "CeqTotal":
            #        CeqTotal = value
            #    if key == "monitor":
            #        monitor = value
            #    if key == "control":
            #        control = value
            #    if key == "tapLevel":
            #        tapLevel = value
            #    if key == "voltageunit":
            #        voltageunit = value
            #    if key == "frequency":
            #        frequency = value
            #    if key == "unitpower":
            #        unitpower = value

            self.setTransformer(id, phases, winding, xhl, kvs, kvas, wdg, bus, connection, kv)
            dss.run_command('Solve')

            logger.info("Transformer names: " + str(dss.Transformers.AllNames()))
        except Exception as e:
            logger.error(e)


    def setTransformer(self, transformer_name, phases, winding, xhl, kvs, kvas, wdg, bus, conn, kv):
        # New Transformer.TR1 phases=3 winding=2 xhl=0.014 kVs=(16, 0.4) kVAs=[400 400] wdg=1 bus=SourceBus conn=delta kv=16  !%r=.5 XHT=1 wdg=2 bus=225875 conn=wye kv=0.4        !%r=.5 XLT=1
        dss_string = "New Transformer.{transformer_name} Phases={phases} Windings={winding} XHL={xhl} KVs=[{kvs}] KVAs=[{kvas}] Wdg={wdg} Bus={bus} Conn={conn} Kv={kv}".format(
                transformer_name = transformer_name,
                phases = phases,
                winding = winding,
                xhl = xhl,
                kvs = ','.join(kvs),
                kvas = ','.join(kvas),
                wdg = wdg,
                bus = bus,
                conn = conn,
                kv = kv
            )
        logger.debug(dss_string)
        dss.run_command(dss_string)