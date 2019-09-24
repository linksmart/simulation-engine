"""
Created on Jul 16 14:13 2018

@author: nishit
"""
import json

import os
import math

import datetime
import logging
from data_management.utils import Utils

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class InputController:

    def __init__(self, id, sim_instance, sim_hours):
        self.stop_request = False
        self.id = id
        self.sim= sim_instance
        self.city = None
        self.country = None
        self.profiles = None
        self.profess = None
        self.sim_hours = sim_hours
        self.voltage_bases = None
        self.base_frequency = 60
        self.price_profile = None
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

    def get_price_profile(self):
        return self.price_profile

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

    def get_price_profile_from_server(self, city, country, sim_hours):
        price_profile_data= self.profiles.price_profile(city, country, sim_hours)
        return price_profile_data

    def is_price_profile_needed(self,topology):
        radial = topology["radials"]
        flag_to_return = False
        for values in radial:
            if "storageUnits" in values.keys():
                for ess_element in values["storageUnits"]:
                    if ess_element["optimization_model"] == "MinimizeCosts":
                        return True
        return flag_to_return

    def is_price_profile(self):
        self.price_profile
        if isinstance(self.price_profile, list):
            if len(self.price_profile) > 0:
                return True
            else:
                return False
        else:
            return False

    def setLoadshapes_Off(self, id, loadshapes):
        logger.debug("Charging the loadshapes into the simulator")
        message = self.sim.setLoadshapes(loadshapes)
        logger.debug("loadshapes charged")
        return message

    def setLoadshapes(self, id, loads, sim_hours):
        logger.debug("Charging the loadshapes into the simulator from profiles")
        message = self.sim.setLoadshapes(loads, sim_hours, self.profiles, self.profess)
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

    def setChargingStations(self, id, object):
        logger.debug("Charging the charging stations into the simulator")
        message = self.sim.setChargingStations(object)
        logger.debug("Charging stations charged")
        return message

    def get_PV_names(self, topology):
        PV_names = []
        radial = topology["radials"]  # ["storageUnits"]
        photovoltaics = []
        for element in radial:
            for key, value in element.items():
                if key == "photovoltaics":
                    photovoltaics = value

        for pv_element in photovoltaics:
            PV_names.append(pv_element["id"])
        return PV_names

    def get_Storage_names(self, topology):
        Storage_names = []
        radial = topology["radials"]  # ["storageUnits"]
        storages = []

        for element in radial:
            for key, value in element.items():
                if key == "storageUnits":
                    storages = value

        for ess_element in storages:
            Storage_names.append(ess_element["id"])
        return Storage_names

    def get_soc_list(self,topology):
        radial=topology["radials"]#["storageUnits"]
        common=topology["common"]
        list_storages=[]
        soc_list = []
        soc_dict_intern = {"SoC":None}
        charging_station = []
        photovoltaics = []
        storages = []
        for element in radial:
            for key, value in element.items():
                if key == "chargingStations":
                    charging_station = value
                if key == "storageUnits":
                    storages = value
                if key == "photovoltaics":
                    photovoltaics = value

        charging_station_buses =[]
        for cs in charging_station:
            charging_station_buses.append(cs["bus"])

        for ess_element in storages:
            if not ess_element["bus1"] in charging_station_buses:
                soc_dict = {}
                #logger.debug("element intern "+str(ess_element))
                soc_dict[ess_element["bus1"]]={"ESS":{"SoC":ess_element["soc"],
                                                        "T_SoC":25,
                                                        "id":ess_element["id"],
                                                        "Battery_Capacity":ess_element["storage_capacity"],
                                                        "max_charging_power":ess_element["max_charging_power"],
                                                        "max_discharging_power":ess_element["max_discharging_power"],
                                                        "charge_efficiency":ess_element["charge_efficiency"],
                                                        "discharge_efficiency":ess_element["discharge_efficiency"]},
                                                "Grid":{
                                                        "Q_Grid_Max_Export_Power": common["max_reactive_power_in_kVar_to_grid"],
                                                        "P_Grid_Max_Export_Power": common["max_real_power_in_kW_to_grid"]}}
                for pv_element in photovoltaics:
                    if pv_element["bus1"] == ess_element["bus1"]:
                        soc_dict[ess_element["bus1"]]["PV"]={"pv_name": pv_element["id"]}
                soc_list.append(soc_dict)
                #list_storages.append(ess_element)
        #logger.debug("list_storages "+str(list_storages))
        logger.debug("soc_list " + str(soc_list))
        return soc_list

    def get_soc_list_evs(self,topology, chargers):
        radial=topology["radials"]#["storageUnits"]
        common=topology["common"]
        list_storages=[]
        soc_list = []
        soc_dict_intern = {"SoC":None}
        charging_station=[]
        photovoltaics=[]
        storages = []
        for element in radial:
            for key, value in element.items():
                if key == "chargingStations":
                    charging_station=value
                if key == "storageUnits":
                    storages=value
                if key == "photovoltaics":
                    photovoltaics=value

        for key, charger_element in chargers.items():
            soc_dict = {}
            evs_connected = charger_element.get_EV_connected()
            for ev_unit in evs_connected:
                ev_unit.calculate_position(self.sim_hours + 24, 1)
                soc_dict[charger_element.get_bus_name()] = {"EV":{"SoC": ev_unit.get_SoC(),
                                                                    "T_SoC": 25,
                                                                    "id": ev_unit.get_id(),
                                                                    "Battery_Capacity": ev_unit.get_Battery_Capacity(),
                                                                    "max_charging_power": charger_element.get_max_charging_power(),
                                                                    "charge_efficiency": charger_element.get_charging_efficiency()},
                                                            "Grid":{
                                                                    "Q_Grid_Max_Export_Power": common["max_reactive_power_in_kVar_to_grid"],
                                                                    "P_Grid_Max_Export_Power": common["max_real_power_in_kW_to_grid"]}
                                                            }

                for pv_element in photovoltaics:
                    if pv_element["bus1"] == charger_element.get_bus_name():
                        soc_dict[charger_element.get_bus_name()]["PV"]={"pv_name": pv_element["id"]}
                for ess_element in storages:
                    if ess_element["bus1"] == charger_element.get_bus_name():
                        soc_dict[charger_element.get_bus_name()]["ESS"] = {"ess_name": ess_element["id"]}
            soc_list.append(soc_dict)
            #list_storages.append(ess_element)
        #logger.debug("list_storages "+str(list_storages))
        #logger.debug("soc_list_evs " + str(soc_list))
        return soc_list

    def set_new_soc(self, soc_list):
        #self.sim.getSoCfromBattery("Akku1")

        new_soc_list=[]
        for element in soc_list:
            for key, value in element.items():
                element_id=value["id"]
                #logger.debug("ESS_id "+str(element_id))
                #logger.debug("SoC 1 " + str(self.sim.getSoCfromBattery(element_id)))
                SoC = float(self.sim.getSoCfromBattery(element_id))
                value["SoC"]=SoC
                new_soc_list.append(element)
        logger.debug("new soc list: " + str(new_soc_list))
        return new_soc_list

    def set_new_soc_evs(self, soc_list):
        #self.sim.getSoCfromBattery("Akku1")

        new_soc_list=[]
        for element in soc_list:
            for key, value in element.items():
                element_id=value["id"]
                #logger.debug("ESS_id "+str(element_id))
                #logger.debug("SoC 1 " + str(self.sim.getSoCfromBattery(element_id)))
                SoC = float(self.sim.getSoCfromBattery(element_id))
                value["SoC"]=SoC
                new_soc_list.append(element)
        logger.debug("new soc list: " + str(new_soc_list))
        return new_soc_list


    def is_Charging_Station_in_Topology(self, topology):
        # topology = profess.json_parser.get_topology()
        # logger.debug("type topology " + str(type(self.topology)))
        radial = topology["radials"]
        flag_to_return = False
        for values in radial:
            if "chargingStations" in values.keys():
                flag_to_return = True
        return flag_to_return

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

    def is_global_control_in_Storage(self, topology):
        radial = topology["radials"]
        for element in radial:
            storages_elements = element["storageUnits"]
        flag_to_return = False
        for values in storages_elements:
            if "global_control" in values.keys():
                if values["global_control"]:
                    flag_to_return = True
        return flag_to_return

    def is_city(self, common):
        if "city" in common.keys():
            return True
        else:
            return False

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
        return self.sim_hours


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
        time_in_days = math.ceil(self.sim_hours / 24) + 1
        if self.is_city(common):
            city = self.get_city(common)
            logger.debug("city " + str(city))
            country = self.get_country(common)
            logger.debug("country " + str(country))
            flag_is_price_profile_needed = self.is_price_profile_needed(topology)
            logger.debug("Flag price profile needed: " + str(flag_is_price_profile_needed))
            if flag_is_price_profile_needed:
                self.price_profile = self.get_price_profile_from_server(city, country, time_in_days)
                #logger.debug("length price profile "+str(len(self.price_profile)))

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
                #logger.debug("LineCode: " + str(linecode))
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
                message = self.setLoadshapes(id, load, time_in_days)
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


            if "chargingStations" in values.keys() and values["chargingStations"] is not None:
                logger.debug("---------------Setting charging stations-------------------------")
                chargingStations = values["chargingStations"]
                message = self.setChargingStations(id, chargingStations)
                if not message == 0:
                    return message

            """if "voltage_regulator" in values.keys() and values["voltage_regulator"] is not None:
                logger.debug("---------------Setting Voltage regulator-------------------------")
                voltage_regulator = values["voltage_regulator"]
                logger.debug("Voltage Regulator: " + str(voltage_regulator))
                factory.gridController.setVoltageRegulator(id, voltage_regulator)
            """

            if "loadshapes" in values.keys() and values["loadshapes"] is not None:
                logger.debug("! ---------------Setting loadshapes------------------------- \n")
                loadshapes = values["loadshapes"]

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

                if not city == None and not country == None:
                    logger.debug("! >>>  ---------------Loading PV Profiles beforehand ------------------------- \n")
                    message = self.setPVshapes(id, photovoltaics, city, country, time_in_days)
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


        return id








