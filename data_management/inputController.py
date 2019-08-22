"""
Created on Jul 16 14:13 2018

@author: nishit
"""
import json

import os

import datetime
import logging
from data_management.utils import Utils

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class InputController:

    def __init__(self, id, sim_instance, sim_days):
        self.stop_request = False
        self.id = id
        self.sim= sim_instance
        self.city = None
        self.country = None
        self.profiles = None
        self.profess = None
        self.sim_days = sim_days
        self.voltage_bases = None
        self.base_frequency = 60
        logger.debug("id " + str(id))
        self.utils = Utils()

    def get_topology(self):
        logger.debug("id "+str(self.id))
        fname = str(self.id) + "_input_grid"
        path = os.path.join("data", str(self.id), fname)
        data = self.utils.get_stored_data(path)
        if data == 1:
            logger.error("Error while opening the input file ")
            return 1
        else:
            return data

    def setParameters(self, name, object):
        logger.debug("Creating a new circuit with the name: "+str(name))
        if object["VoltageBases"]:
            self.voltage_bases = object["VoltageBases"]
            logger.debug(" voltage bases " + str(self.voltage_bases))
        if object["base_frequency"]:
            self.base_frequency = object["base_frequency"]
            logger.debug("base_frequency " + str(self.base_frequency))
        if object["url_storage_controller"]:
            self.profess_url = object["url_storage_controller"]
            logger.debug("profess url: "+str(self.profess_url))
        if object["city"]:
            self.city = object["city"]
            logger.debug("city: "+str(self.city))
        if object["country"]:
            self.country = object["country"]
            logger.debug("country: "+str(self.country))
        logger.debug("New circuit created")

    def get_voltage_bases(self):
        return self.voltage_bases

    def get_base_frequency(self):
        return self.base_frequency

    def enableCircuit(self, name):
        logger.debug("Enabling the circuit with the name: "+str(name))
        self.sim.enableCircuit(name)
        logger.debug("Circuit "+str(name)+" enabled")

    def disableCircuit(self, name):
        logger.debug("Disabling the circuit with the name: " + str(name))
        self.sim.disableCircuit(name)
        logger.debug("Circuit " + str(name) + " disabled")

    def setLoads(self, id, object):
        self.object = object
        logger.debug("Charging loads into the simulator")
        message = self.sim.setLoads(self.object)
        logger.debug("Loads charged")
        return message

    def setTransformers(self, id, object):
        logger.debug("Charging transformers into the simulator")
        self.object = object
        message = self.sim.setTransformers(self.object)
        logger.debug("Transformers charged")
        return message

    def setRegControls(self, id, object):
        logger.debug("Charging RegControls into the simulator")
        self.object = object
        message = self.sim.setRegControls(self.object)
        logger.debug("RegControls charged")
        return message

    def setPowerLines(self, id, powerlines):  # (self, id, powerlines, linecodes):
        logger.debug("Charging power lines into the simulator")
        # self.sim.setLineCodes(linecodes)
        message = self.sim.setPowerLines(powerlines)
        logger.debug("Power lines charged")
        return message

    def setCapacitors(self, id, capacitors):
        logger.debug("Charging capacitors into the simulator")
        # self.object = object
        # self.sim.setCapacitors(self.object)
        message = self.sim.setCapacitors(capacitors)
        logger.debug("Capacitor charged")
        return message

    def setLineCodes(self, id, linecode):
        logger.debug("Charging LineCode into the simulator")
        # self.object = object
        # self.sim.setLineCodes(self.object)
        message = self.sim.setLineCodes(linecode)
        logger.debug("LineCode charged")
        return message

    def setXYCurve(self, id, npts, xarray, yarray):
        logger.debug("Setting the XYCurve into the simulator")
        self.object = object
        message = self.sim.setXYCurve(self.object)
        logger.debug("XYCurve set")
        return message

    def setPhotovoltaic(self, id, photovoltaics):
        logger.debug("Charging the photovoltaics into the simulator")

        message = self.sim.setPhotovoltaics(photovoltaics)
        logger.debug("Photovoltaics charged")
        return message

    def setPVshapes(self, id, pvs, city, country, sim_days):
        if not city == None and not country == None:
            logger.debug("Charging the pvshapes into the simulator from profiles")
            message = self.sim.setPVshapes(pvs, city, country, sim_days, self.profiles, self.profess)
            logger.debug("loadshapes from profiles charged")
            return message
        else:
            error = "City and country are not present"
            logger.error(error)
            return error

    def setLoadshapes_Off(self, id, loadshapes):
        logger.debug("Charging the loadshapes into the simulator")
        message = self.sim.setLoadshapes(loadshapes)
        logger.debug("loadshapes charged")
        return message

    def setLoadshapes(self, id, loads, sim_days):
        logger.debug("Charging the loadshapes into the simulator from profiles")
        message = self.sim.setLoadshapes(loads, sim_days, self.profiles, self.profess)
        logger.debug("loadshapes from profiles charged")
        return message

    def setLoadshape(self, list_loadshapes):
        logger.debug("Charging a loadshape into the simulator")
        message = self.sim.setLoadshapes_off(id, list_loadshapes)
        logger.debug("a loadshape charged")
        return message

    def setStorage(self, id, storage):
        logger.debug("Charging the ESS into the simulator")
        message = self.sim.setStorages(storage)
        logger.debug("ESS charged")
        return message

    def setChargingPoints(self, id, object):
        logger.debug("Charging the charging points into the simulator")
        self.object = object
        message = self.sim.setChargingPoints(self.object)
        logger.debug("Charging points charged")
        return message

    def is_Storage_in_Topology(self, topology):
        # topology = profess.json_parser.get_topology()
        # logger.debug("type topology " + str(type(self.topology)))
        radial = topology["radials"]
        flag_to_return = False
        for values in radial:
            #values = values.to_dict()
            # logger.debug("values "+str(values))
            # for key in values.keys():
            # logger.debug("key "+str(key))
            if "storageUnits" in values.keys():
                flag_to_return = True
        return flag_to_return

    def get_city(self, common):
        if common["city"]:
            self.city = common["city"]
            return self.city
        else:
            return 1

    def get_country(self, common):
        if common["country"]:
            self.country = common["country"]
            return self.country
        else:
            return 1

    def get_sim_days(self):
        return self.sim_days


    def setup_elements_in_simulator(self, topology, profiles, profess):

        """
        dummyprofile = [3] * 24
        dummyLoads = []
        dummyPrice = []
        dummyPV = []


        dummyPVdict = []
        print("profess.json_parser.get_node_name_list(): " + str(profess.json_parser.get_node_name_list()))

        for element in profess.json_parser.get_node_name_list():
            print("element: " + str(element))
            dummyDict = { element: {element + ".1": copy.deepcopy(dummyprofile), element + ".2": copy.deepcopy(dummyprofile), element + ".3": copy.deepcopy(dummyprofile)}}
            print("dummyDict: " + str(dummyDict))
            dummyLoads.append(dummyDict)
            dummyPVdict = {element: {element + ".1.2.3": copy.deepcopy(dummyprofile)}}
            dummyPV.append(dummyPVdict)


        dummyPrice = copy.deepcopy(dummyprofile)

        element = "671"
        dummyDict = {element: [{element + ".1.2.3": copy.deepcopy(dummyprofile)}]}

        print("dummyDict: " + str(dummyDict))
        print("dummyLoads: " + str(dummyLoads))
        print("dummyPV: " +  str(dummyPV))
        print("dummyPrice: " + str(dummyPrice))

        print("dummyLoads len: " + str(len(dummyLoads)))

        dummyLoads[0] = dummyDict
        dummyGESSCON = [{'633': {'633.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}},
                        {'671': {'671.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}]

        #profess.set_up_profess( dummyLoads, dummyPV, dummyPrice, dummyGESSCON)
        #profess.start_all()
        print(profess.dataList)
        print(profess.wait_and_get_output())

        soc_list = [{"633": {"SoC": 0.5}}, {"671": {"SoC": 0.4}}, {"634": {"SoC": 0.2}}]
        #profess.update(dummyLoads, dummyPV, dummyPrice, soc_list, dummyGESSCON)
        #print(profess.dataList)
        #---------------PROFESS_END--------------------#

        """
        self.profiles = profiles
        self.profess = profess
        common = topology["common"]
        radial = topology["radials"]

        for values in radial:
            #logger.debug("values of the radial: "+str(values))
            #values = values.to_dict()
            # logger.debug("Values: "+str(values))

            if "transformer" in values.keys() and values["transformer"] is not None:
                # logger.debug("!---------------Setting Transformers------------------------")
                logger.debug("!---------------Setting Transformers------------------------ \n")
                transformer = values["transformer"]
                #                logger.debug("Transformers" + str(transformer))
                message = self.setTransformers(id, transformer)
                if not message == 0:
                    return message

            if "regcontrol" in values.keys() and values["regcontrol"] is not None:
                logger.debug("!---------------Setting RegControl------------------------ \n")
                regcontrol = values["regcontrol"]
                #                logger.debug("RegControl" + str(regcontrol))
                message = self.setRegControls(id, regcontrol)
                if not message == 0:
                    return message

            if "linecode" in values.keys() and values["linecode"] is not None:
                logger.debug("! ---------------Setting LineCode------------------------- \n")
                linecode = values["linecode"]
                logger.debug("LineCode: " + str(linecode))
                message = self.setLineCodes(id, linecode)
                if not message == 0:
                    return message

            if "loads" in values.keys() and values["loads"] is not None:
                # logger.debug("---------------Setting Loads-------------------------")
                logger.debug("! ---------------Setting Loads------------------------- \n")
                # radial=radial.to_dict()
                load = values["loads"]
                # logger.debug("Loads" + str(load))
                logger.debug("! >>>  ---------------Loading Load Profiles beforehand ------------------------- \n")
                message = self.setLoadshapes(id, load, self.sim_days)
                if not message == 0:
                    return message
                logger.debug("! >>>  ---------------and the Loads afterwards ------------------------- \n")
                message = self.setLoads(id, load)
                if not message == 0:
                    return message

            if "capacitor" in values.keys() and values["capacitor"] is not None:
                # logger.debug("---------------Setting Capacitors-------------------------")
                logger.debug("! ---------------Setting Capacitors------------------------- \p")
                capacitor = values["capacitor"]
                # logger.debug("Capacitors: " + str(capacitor))
                message = self.setCapacitors(id, capacitor)
                if not message == 0:
                    return message

            if "powerLines" in values.keys() and values["powerLines"] is not None:
                # logger.debug("---------------Setting Powerlines-------------------------")
                logger.debug("!---------------Setting Powerlines------------------------- \n")

                powerLines = values["powerLines"]
                # linecodes = values["linecode"]
                # factory.gridController.setPowerLines(id, powerLines, linecodes) #TODO: Where does linecodes come from?
                # logger.debug("Powerlines" + str(powerLines))
                message = self.setPowerLines(id, powerLines)
                logger.debug(str(message))
                if not message == 0:
                    return message

            if "powerProfile" in values.keys() and values["powerProfile"] is not None:
                logger.debug("!---------------Setting powerProfile------------------------- \n")
                powerProfile = values["powerProfile"]
                # logger.debug("Powerprofile" + str(powerProfile))
                message = self.setPowerProfile(id, powerProfile)
                if not message == 0:
                    return message

            if "xycurves" in values.keys() and values["xycurves"] is not None:
                xycurves = values["xycurves"]  # TORemove
                message = self.setXYCurves(id, xycurves)
                if not message == 0:
                    return message

            """if "photovoltaics" in values.keys() and values["photovoltaics"] is not None:
                photovoltaics = values["photovoltaics"]
                #xycurves = radial["xycurves"]
                #loadshapes = radial["loadshapes"]
                #tshapes = radial["tshapes"]
                factory.gridController.setPhotovoltaic(id, photovoltaics)"""  # TODO: fix and remove comment

            """
            and "xycurves" in radial.values.keys()s() and radial["xycurves"] is not None 
                            and "loadshapes" in radial.values.keys()s() and radial["loadshapes"] is not None 
                            and "tshapes" in radial.values.keys()s() and radial["tshapes"] is not None: 
            """
            if "storageUnits" in values.keys() and values["storageUnits"] is not None:
                # logger.debug("---------------Setting Storage-------------------------")
                logger.debug("! ---------------Setting Storage------------------------- \n")
                # radial=radial.to_dict()
                storage = values["storageUnits"]
                #for storage_elements in storage:
                    #if not storage_elements["optimization_model"] in models_list:
                        #message = "Following optimization models are possible: " + str(models_list)
                        #return message
                message = self.setStorage(id, storage)  # TODO: fix and remove comment
                if not message == 0:
                    return message

            """if "chargingPoints" in values.keys() and values["chargingPoints"] is not None:
                # radial=radial.to_dict()
                chargingPoints = values["chargingPoints"]
                gridController.setChargingPoints(id, chargingPoints)
            """
            if "chargingPoints" in values.keys() and values["chargingPoints"] is not None:
                # logger.debug("---------------Setting chargingPoints-------------------------")
                chargingPoints = values["chargingPoints"]
                message = self.setChargingPoints(id, chargingPoints)
                if not message == 0:
                    return message

            """if "voltage_regulator" in values.keys() and values["voltage_regulator"] is not None:
                logger.debug("---------------Setting Voltage regulator-------------------------")
                voltage_regulator = values["voltage_regulator"]
                logger.debug("Voltage Regulator: " + str(voltage_regulator))
                factory.gridController.setVoltageRegulator(id, voltage_regulator)
            """

            if "loadshapes" in values.keys() and values["loadshapes"] is not None:
                #                logger.debug("---------------Setting loadshapes-------------------------")
                logger.debug("! ---------------Setting loadshapes------------------------- \n")
                loadshapes = values["loadshapes"]
                #                logger.debug("Load Shapes: " + str(loadshapes))

                message = self.setLoadShape(id, loadshapes)
                if not message == 0:
                    return message
            if "tshapes" in values.keys() and values["tshapes"] is not None:
                logger.debug("---------------Setting tshapes-------------------------")
                tshapes = values["tshapes"]
                logger.debug("Tshapes: " + str(tshapes))
                message = self.setTShape(id, tshapes)
                if not message == 0:
                    return message
            if "photovoltaics" in values.keys() and values["photovoltaics"] is not None:
                logger.debug("! ---------------Setting Photovoltaic------------------------- \n")
                photovoltaics = values["photovoltaics"]
                # xycurves = radial["xycurves"]
                # loadshapes = radial["loadshapes"]
                # tshapes = radial["tshapes"]

                city = self.get_city(common)
                logger.debug("city " + str(city))
                country = self.get_country(common)
                logger.debug("country " + str(country))
                if not city == None and not country == None:
                    logger.debug("! >>>  ---------------Loading PV Profiles beforehand ------------------------- \n")
                    message = self.setPVshapes(id, photovoltaics, city, country, self.sim_days)
                    if not message == 0:
                        return message
                    logger.debug("! >>>  ---------------and the PVs afterwards ------------------------- \n")
                    message = self.setPhotovoltaic(id, photovoltaics)
                    if not message == 0:
                        return message
                else:
                    error = "Fatal error: city and country are missing"

                    logger.error(error)
                    return error
                logger.debug("! >>>  ---------------PVs finished ------------------------- \n")

        ######Disables circuits untilo the run simulation is started
        # factory.gridController.disableCircuit(id)

        # result = factory.gridController.run(profess)

        return id
        # return " Result: " + str(result)







