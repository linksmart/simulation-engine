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


    def solveCircuitSolution(self):
        #dss.Solution.Solve()
        dss.run_command('Redirect /usr/src/app/tests/data/13Bus/IEEE13Nodeckt.dss')
        logger.info("Loads names: "+str(dss.Loads.AllNames()))
        logger.info("Bus names: " + str(dss.Circuit.AllBusNames()))
        logger.info("All Node names: " + str(dss.Circuit.AllNodeNames()))
        logger.info("Length of Node Names: " + str(len(dss.Circuit.AllNodeNames())))
        logger.info("Voltages: "+str(dss.Circuit.AllBusVolts()))
        logger.info("Length of Bus Voltages: "+str(len(dss.Circuit.AllBusVolts())))
        logger.info("Bus Voltages: "+ str(dss.Bus.Voltages()))
        logger.info("Just magnitude of Voltages: "+str(dss.Circuit.AllBusVMag()))
        logger.info("Length of Bus Voltages: " + str(len(dss.Circuit.AllBusVMag())))
        logger.info("Just pu of Voltages: " + str(dss.Circuit.AllBusMagPu()))
        logger.info("Length of Bus Voltages: " + str(len(dss.Circuit.AllBusMagPu())))
        return (dss.Circuit.AllNodeNames(),dss.Circuit.AllBusMagPu())
    #def getVoltages(self):


    #def setSolveMode(self, mode):
     #   self.mode=mode
      #  dss.run_command("Solve mode=" + self.mode)
    def setStartingHour(self, hour):
        self.hour=hour
        dss.Solution.DblHour(self.hour)
        logger.debug("Starting hour "+str(dss.Solution.DblHour()))

    def setVoltageBases(self,V1,V2):
        self.V1=V1
        self.V2=V2
        #dss.Settings.VoltageBases(0.4,16)
        dss.run_command("Set voltagebases = [{value1},{value2}]".format(value1=self.V1,value2=self.V2))
        dss.run_command("calcv")
        logger.debug("Voltage bases: "+str(dss.Settings.VoltageBases()))

    def solutionConverged(self):
        return dss.Solution.Coverged()

    def setMode(self, mode):
        self.mode = mode
        dss.run_command("Set mode="+self.mode)
        logger.debug("Solution mode "+str(dss.Solution.ModeID()))

    #Options: minutes or hours
    def setStepSize(self, time_step):
        self.time_step=time_step
        if "minutes" in self.time_step:
            dss.Solution.StepSizeMin(1)
        if "hours" in self.time_step:
            dss.Solution.StepSizeHr(1)
        logger.debug("Simulation step_size " + str(dss.Solution.StepSize()))


    def numberSimulations(self, number):
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

""""
    def example(self):

        dss.run_command('Redirect ./tests/data/13Bus/IEEE13Nodeckt.dss')
        for i in dss.Circuit.AllBusNames():
            logger.info(i)

        logger.info("Inspecting submodules")
        import types

        import inspect

        logger.info("2")
        for name, module in inspect.getmembers(dss):
            if isinstance(module, types.ModuleType) and not name.startswith('_'):
                logger.info(f'dss.{name}')

        logger.info("3")
        for name, function in inspect.getmembers(dss.Loads):
            if callable(function) and not name.startswith('_'):
                logger.info(f'dss.Loads.{name}')

        logger.info("4")

        logger.info("Load names: " + str(dss.Loads.AllNames()))
        logger.info("5")
        dss.Loads.First()
        logger.info("6")
        while True:

            logger.info(
                'Name={name} \t kW={kW}'.format(
                    name=str(dss.Loads.Name()),
                    kW=str(dss.Loads.kW())
                )
            )

            if not dss.Loads.Next() > 0:
                break
        logger.info("7")
        dss.run_command(
            "New Load.{load_name} Bus1={bus_name}  Phases=3 Conn=Delta Model=1 kV=4.16   kW=1155 kvar=660".format(
                load_name='Aragon',
                bus_name='671.1.2.3'
            ))
        dss.run_command('Solve')

        logger.info("Load names 2: " + str(dss.Loads.AllNames()))

        logger.info("8")
        from opendssdirect.utils import Iterator
        for i in Iterator(dss.Loads, 'Name'):
            logger.info(
                'Name={name} \t kW={kW}'.format(
                    name=str(i()),
                    kW=str(dss.Loads.kW())
                )
            )
        logger.info("9")
        dss.run_command(
            "New Storage.{bus_name} Bus1={bus_name} phases=1 kV=2.2 kWRated={rating} kWhRated={kwh_rating} kWhStored={initial_state} %IdlingkW=0 %reserve=0 %EffCharge=100 %EffDischarge=100 State=CHARGING".format(
                bus_name='675',
                rating=20,
                kwh_rating=20,
                initial_state=20
            ))
"""