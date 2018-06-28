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
        dss.run_command("New circuit.{circuit_name}".format(circuit_name="Test 1"))



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