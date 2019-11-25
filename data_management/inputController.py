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
        self.sim_hours = sim_hours
        self.voltage_bases = None
        self.base_frequency = 60
        self.price_profile = None
        logger.debug("Grid id " + str(id))
        self.utils = Utils()

    def get_topology(self):
        logger.debug("getting topology of grid id "+str(self.id))
        fname = str(self.id) + "_input_grid"
        path = os.path.join("data", str(self.id), fname)
        data = self.utils.get_stored_data(path)
        if data == 1:
            logger.error("Error while opening the input file ")
            return 1
        else:
            return data

    def get_topology_per_node(self, id):
        topology = self.get_topology()
        radial = topology["radials"]

        data_to_return = {}
        for radial_element in radial:

            for grid_element_type, values_element in radial_element.items():
                logger.debug("grid_element "+str(grid_element_type))
                for elements in values_element:
                    if not elements == [] and not elements == None:
                        if grid_element_type == "transformer":
                            id = elements["id"]
                            bus1 = elements["buses"][0]
                            bus2 = elements["buses"][1]
                            if not bus1 in data_to_return.keys():
                                data_to_return[bus1]={"transformers":[]}
                            if not bus2 in data_to_return.keys():
                                data_to_return[bus2]={"transformers":[]}

                            data_to_return[bus1]["transformers"].append(id)
                            data_to_return[bus2]["transformers"].append(id)

                        if grid_element_type == "loads" or grid_element_type == "chargingStations":
                            id = elements["id"]
                            bus = elements["bus"]
                            if not bus in data_to_return.keys():
                                data_to_return[bus]={}
                            if not grid_element_type in data_to_return[bus].keys():
                                data_to_return[bus][grid_element_type]=[]

                            data_to_return[bus][grid_element_type].append(id)
                        if grid_element_type == "photovoltaics" or grid_element_type == "storageUnits":
                            id = elements["id"]
                            bus = elements["bus1"]
                            if not bus in data_to_return.keys():
                                data_to_return[bus] = {}
                            if not grid_element_type in data_to_return[bus].keys():
                                data_to_return[bus][grid_element_type] = []

                            data_to_return[bus][grid_element_type].append(id)

        logger.debug("data_to_return "+str(data_to_return))
        return data_to_return


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

    def setLoads(self, object):
        self.object = object
        logger.debug("Charging loads into the simulator")
        message = self.sim.setLoads(self.object)
        logger.debug("Loads charged")
        return message

    def setTransformers(self, object):
        logger.debug("Charging transformers into the simulator")
        self.object = object
        message = self.sim.setTransformers(self.object)
        logger.debug("Transformers charged")
        return message

    def setRegControls(self, object):
        logger.debug("Charging RegControls into the simulator")
        self.object = object
        message = self.sim.setRegControls(self.object)
        logger.debug("RegControls charged")
        return message

    def setPowerLines(self, powerlines):  # (self, id, powerlines, linecodes):
        logger.debug("Charging power lines into the simulator")
        # self.sim.setLineCodes(linecodes)
        message = self.sim.setPowerLines(powerlines)
        logger.debug("Power lines charged")
        return message

    def setCapacitors(self, capacitors):
        logger.debug("Charging capacitors into the simulator")
        # self.object = object
        # self.sim.setCapacitors(self.object)
        message = self.sim.setCapacitors(capacitors)
        logger.debug("Capacitor charged")
        return message

    def setLineCodes(self, linecode):
        logger.debug("Charging LineCode into the simulator")
        # self.object = object
        # self.sim.setLineCodes(self.object)
        message = self.sim.setLineCodes(linecode)
        logger.debug("LineCode charged")
        return message

    def setXYCurve(self, npts, xarray, yarray):
        logger.debug("Setting the XYCurve into the simulator")
        self.object = object
        message = self.sim.setXYCurve(self.object)
        logger.debug("XYCurve set")
        return message
    
    def setPowerProfile(self, powerprofile):
        logger.debug("Setting the Powerprofile into the simulator")
        self.object = object
        for element in powerprofile:
            items = element['items']
            normalize = element['normalized']
            useactual = element['use_actual_values']
            if 'multiplier' in element.keys() and element['multiplier'] is not None:
                items = [item * element['multiplier'] for item in items]
            npts = len(items)
            interval = 1
            if "interval" in element.keys() and element['interval'] is not None:
                interval = element['interval']
            elif "m_interval" in element.keys() and element['m_interval'] is not None:
                interval = element['m_interval']
            elif "s_interval" in element.keys() and element['s_interval'] is not None:
                interval = element['s_interval']
            message = self.sim.setLoadshape(element['id'], npts, interval, items, normalize, useactual)
        logger.debug("Powerprofile set")
        return message

    def setPhotovoltaic(self, photovoltaics):
        logger.debug("Charging the photovoltaics into the simulator")

        message = self.sim.setPhotovoltaics(photovoltaics)
        logger.debug("message "+str(message))
        logger.debug("Photovoltaics charged")
        return message

    def setPVshapes(self, profiles_object, profess_object, pvs, city, country, sim_days, powerprofile):
        if not city == None and not country == None:
            logger.debug("Charging the pvshapes into the simulator from profiles")
            message = self.sim.setPVshapes(pvs, powerprofile, city, country, sim_days, profiles_object, profess_object)
            if message == 0:
                logger.debug("Loadshapes for PVs charged")
            return message
        else:
            error = "City and country are not present"
            logger.error(error)
            return error

    # profess_global_profile =[{'node_a6': {
    # 'Akku2': [0.03, 0.03, -0.03, 0.0024003110592032, 0.03, 0.0, 0.0, -0.028741258741258702, 0.0,
    # 0.0, 0.0, -0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}}]
    def get_profile(self, data, start, number_of_points):
        data_list=[]

        for element in data:
            data_dict = {}
            for node_name, value in element.items():
                data_dict[node_name]={}
                for battery_name, profile in value.items():
                    data_dict[node_name][battery_name] = profile[int(start):int(start+number_of_points)]
            data_list.append(data_dict)
        return data_list

    def get_price_profile_from_server(self, profiles_object, city, country, sim_days):
        price_profile_data= profiles_object.price_profile(city, country, sim_days)
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

    def setLoadshapes(self, profiles_object, profess_object, loads, powerprofile, sim_days):
        logger.debug("Charging the loadshapes into the simulator from profiles")
        message = self.sim.setLoadshapes(loads, powerprofile, sim_days, profiles_object, profess_object)
        logger.debug("loadshapes from profiles charged")
        return message


    def setStorage(self, storage):
        logger.debug("Charging the ESS into the simulator")
        message = self.sim.setStorages(storage)
        logger.debug("ESS charged")
        return message

    def setChargingStations(self, object):
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
        if not photovoltaics == None:
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

        if not storages == []:
            for ess_element in storages:
                Storage_names.append(ess_element["id"])
            return Storage_names
        else:
            return []


    def get_Storage_nodes(self, topology):
        Storage_nodes = []
        radial = topology["radials"]  # ["storageUnits"]
        storages = []

        for element in radial:
            for key, value in element.items():
                if key == "storageUnits":
                    storages = value

        for ess_element in storages:
            Storage_nodes.append(ess_element["bus1"])
        return Storage_nodes

    def get_storage_powers(self, list_storage_names):
        list_power = []
        for ess_name in list_storage_names:
            value = self.sim.getkWfromBattery(ess_name)
            list_power.append(value)
        return list_power

    def get_storage_socs(self, topology):
        list_storage_names = self.get_Storage_names(topology)
        list_soc = []
        for ess_name in list_storage_names:
            list_soc.append(self.sim.getSoCfromBattery(ess_name))
        return list_soc

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
                if "max_reactive_power_in_kVar_to_grid" and "max_real_power_in_kW_to_grid" in common.keys():
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
                else:
                    return "Missing \"max_reactive_power_in_kVar_to_grid\" or \"max_real_power_in_kW_to_grid\" in common"
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

        ess_buses = []
        for storage_element in storages:
            ess_buses.append(storage_element["bus1"])

        for charger_element in chargers:
            if charger_element.get_bus_name() in ess_buses:
                soc_dict = {}
                evs_connected = charger_element.get_EV_connected()
                for ev_unit in evs_connected:
                    #ev_unit.calculate_position(self.sim_hours + 24, 1)
                    soc_dict[charger_element.get_bus_name()] = {"EV":{"SoC": ev_unit.get_SoC(),
                                                                        "id": ev_unit.get_id(),
                                                                        "Battery_Capacity": ev_unit.get_Battery_Capacity(),
                                                                        "max_charging_power": charger_element.get_max_charging_power(),
                                                                        "charge_efficiency": charger_element.get_charging_efficiency()},
                                                                "Grid":{
                                                                        "Q_Grid_Max_Export_Power": common["max_reactive_power_in_kVar_to_grid"],
                                                                        "P_Grid_Max_Export_Power": common["max_real_power_in_kW_to_grid"]}
                                                                }

                    for pv_element in photovoltaics:
                        bus_pv = pv_element["bus1"]
                        if "." in bus_pv:
                            if len(bus_pv.split(".")) == 4:
                                bus_pv = bus_pv.split(".")[0]
                        if bus_pv == charger_element.get_bus_name():
                            soc_dict[charger_element.get_bus_name()]["PV"]={"pv_name": pv_element["id"]}
                    for ess_element in storages:
                        bus_ess = ess_element["bus1"]
                        if "." in bus_ess:
                            if len(bus_ess.split(".")) == 4:
                                bus_ess = bus_ess.split(".")[0]
                        if bus_ess == charger_element.get_bus_name():
                            soc_dict[charger_element.get_bus_name()]["ESS"] = {"SoC":ess_element["soc"],
                                                            "T_SoC":25,
                                                            "id":ess_element["id"],
                                                            "Battery_Capacity":ess_element["storage_capacity"],
                                                            "max_charging_power":ess_element["max_charging_power"],
                                                            "max_discharging_power":ess_element["max_discharging_power"],
                                                            "charge_efficiency":ess_element["charge_efficiency"],
                                                            "discharge_efficiency":ess_element["discharge_efficiency"]}
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
                element_id=value["ESS"]["id"]
                SoC = float(self.sim.getSoCfromBattery(element_id))
                value["ESS"]["SoC"]=SoC
                new_soc_list.append(element)
        #logger.debug("new soc list: " + str(new_soc_list))
        return new_soc_list

    def get_powers_from_profess_output(self, profess_output, soc_list):
        profess_result = []
        for element in profess_output:
            profess_result_intern = {}
            for key, value in element.items():
                node_name = key
                profess_result_intern[node_name] = {}
                for element_soc in soc_list:
                    for key_node in element_soc.keys():
                        if key_node == node_name:
                            profess_result_intern[node_name]["ess_name"] = element_soc[key_node]["ESS"]["id"]
                            profess_result_intern[node_name]["pv_name"] = element_soc[key_node]["PV"]["pv_name"]
                            profess_result_intern[node_name]["max_charging_power"] = element_soc[key_node]["ESS"][
                                "max_charging_power"]
                            profess_result_intern[node_name]["max_discharging_power"] = element_soc[key_node]["ESS"][
                                "max_discharging_power"]
                for profess_id, results in value.items():
                    for key_results, powers in results.items():
                        profess_result_intern[node_name][key_results] = powers

            profess_result.append(profess_result_intern)
        return profess_result

    def get_powers_from_profev_output(self, profev_output, charger_element, ev_unit):

        p_ev = None
        p_ess =  None
        p_pv = None
        for element in profev_output:
            for node_name, rest in element.items():
                if charger_element.get_bus_name() == node_name:
                    for profess_id, results in rest.items():
                        for value_key, value in results.items():
                            if ev_unit.get_id() in value_key:
                                p_ev = value
                            if "p_ess" == value_key:
                                p_ess = value
                            if "p_pv" == value_key:
                                p_pv = value
        if p_ev == None:
            p_ev = 0
        return (p_ev, p_ess, p_pv)

    def set_new_soc_evs(self, soc_list_commercial=None, soc_list_residential=None, chargers = None):
        #self.sim.getSoCfromBattery("Akku1")

        new_soc_list = []
        if not soc_list_commercial == None:

            for element in soc_list_commercial:
                for node_name, value in element.items():
                    element_id = value["ESS"]["id"]
                    SoC = float(self.sim.getSoCfromBattery(element_id))
                    value["ESS"]["SoC"] = SoC

                    if not chargers == None:
                        element_id = value["EV"]["id"]
                        SoC = None
                        for cs_id, charger in chargers.items():
                            ev_connected = charger.get_EV_connected()
                            for ev in ev_connected:
                                #if charger.get_ev_plugged() == ev:
                                if ev.get_id() == element_id:
                                    SoC = ev.get_SoC()
                        value["EV"]["SoC"] = SoC
                    else:
                        element_id = "ESS_" + value["EV"]["id"]
                        SoC = float(self.sim.getSoCfromBattery(element_id))
                        value["EV"]["SoC"] = SoC
                    value["EV"]["commercial"] = True
                    new_soc_list.append(element)

        if not soc_list_residential == None:

            for element in soc_list_residential:
                for node_name, value in element.items():
                    element_id = value["ESS"]["id"]
                    SoC = float(self.sim.getSoCfromBattery(element_id))
                    value["ESS"]["SoC"] = SoC

                    if not chargers == None:
                        element_id = value["EV"]["id"]
                        SoC = None
                        for cs_id, charger in chargers.items():
                            ev_connected = charger.get_EV_connected()
                            for ev in ev_connected:
                                # if charger.get_ev_plugged() == ev:
                                if ev.get_id() == element_id:
                                    SoC = ev.get_SoC()
                        value["EV"]["SoC"] = SoC
                    else:
                        element_id = "ESS_" + value["EV"]["id"]
                        SoC = float(self.sim.getSoCfromBattery(element_id))
                        value["EV"]["SoC"] = SoC
                    value["EV"]["commercial"] = False
                    new_soc_list.append(element)

        if soc_list_commercial == None and soc_list_residential == None:
            new_soc_list = []
        #logger.debug("new soc list: " + str(new_soc_list))
        return new_soc_list

    def get_ESS_name_for_node(self, soc_list, node_name_input):

        ess_name = None
        max_charging_power = None
        for element in soc_list:
            for node_name, rest in element.items():
                if node_name == node_name_input:
                    ess_name = rest["ESS"]["id"]
                    max_charging_power =rest["ESS"]["max_charging_power"]

        return (ess_name, max_charging_power)

    def get_PV_name_for_node(self, soc_list, node_name_input):
        pv_name = None
        for element in soc_list:
            for node_name, rest in element.items():
                if node_name == node_name_input:
                    pv_name = rest["PV"]["pv_name"]

        return pv_name

    def is_Charging_Station_in_Topology(self, topology):
        # topology = profess.json_parser.get_topology()
        # logger.debug("type topology " + str(type(self.topology)))
        radial = topology["radials"]

        flag_to_return = False
        for values in radial:
            for key, data in values.items():
                if key == "chargingStations" and len(data) >0:
                    flag_to_return = True
        return flag_to_return

    def get_nodes_Charging_Station_in_Topology(self, chargers):
        # topology = profess.json_parser.get_topology()
        # logger.debug("type topology " + str(type(self.topology)))

        list_nodes_cs = []
        for key, charger_element in chargers.items():
            list_nodes_cs.append(charger_element.get_bus_name())
        return list_nodes_cs


    def get_list_nodes_storages(self, radial):
        for element in radial:
            for key, value in element.items():
                if key == "storageUnits":
                    storages = value

        list_nodes_storages=[]

        for ess_element in storages:
            list_nodes_storages.append(ess_element["bus1"])
        return list_nodes_storages

    def get_list_pvs_alone(self, topology, pv_object_dict,chargers=None):
        radial = topology["radials"]

        list_nodes_cs = []
        if not chargers == None:
            list_nodes_cs = self.get_nodes_Charging_Station_in_Topology(chargers)
        logger.debug("list_nodes_cs "+str(list_nodes_cs))


        list_nodes_storage = self.get_list_nodes_storages(radial)
        logger.debug("list_nodes_storage "+ str(list_nodes_storage))

        list_nodes_pvs = []
        for id, pv_object in pv_object_dict.items():
            list_nodes_pvs.append(pv_object.get_node())

        logger.debug("list_nodes_pvs "+str(list_nodes_pvs))

        list_nodes_pvs_single = []

        for node_pv in list_nodes_pvs:
            if node_pv not in list_nodes_storage and node_pv not in list_nodes_cs:
                list_nodes_pvs_single.append(node_pv)

        logger.debug("list_nodes_pvs_single "+str(list_nodes_pvs_single))
        list_pv_single=[]

        for id, pv_object in pv_object_dict.items():
            for node_pv in list_nodes_pvs_single:
                if pv_object.get_node() == node_pv:
                    list_pv_single.append(pv_object)
                    control = pv_object.get_control_strategy().get_name()
                    if control == "ofw":
                        pv_object.set_control_strategy("no_control")
        return list_pv_single

    def get_list_nodes_charging_station_without_storage(self, topology, chargers):
        radial = topology["radials"]

        list_nodes_cs = self.get_nodes_Charging_Station_in_Topology(chargers)
        #logger.debug("list_nodes_cs "+str(list_nodes_cs))
        list_nodes_cs_with_storage = self.get_list_nodes_storages_with_charging_station(radial, chargers)
        #logger.debug("list_nodes_cs_with_storage "+ str(list_nodes_cs_with_storage))

        list_cs=[]
        for cs_node in list_nodes_cs:
            flag = False
            #logger.debug("cs_node "+str(cs_node))
            for node_without_storage in list_nodes_cs_with_storage:
                #logger.debug("node_without_storage "+str(node_without_storage))
                if cs_node == node_without_storage:
                    #logger.debug("flag")
                    flag = True
            #logger.debug("flag "+str(flag))
            if not flag:
                list_cs.append(cs_node)
        return list_cs

    def get_list_nodes_storages_with_charging_station(self, radial, chargers):
        for element in radial:
            for key, value in element.items():
                if key == "storageUnits":
                    storages = value

        list_nodes_storages_with_cs=[]
        for key, charger_element in chargers.items():
            for ess_element in storages:
                if ess_element["bus1"] == charger_element.get_bus_name():
                    list_nodes_storages_with_cs.append(ess_element["bus1"])
        return list_nodes_storages_with_cs

    def is_Storage_in_Topology_without_charging_station(self, topology, chargers=None):
        # topology = profess.json_parser.get_topology()
        # logger.debug("type topology " + str(type(self.topology)))
        radial = topology["radials"]
        for values in radial:
            if not "storageUnits" in values.keys():
                return False
            for key, data in values.items():
                if key == "storageUnits" and len(data) == 0:
                    return False

        if not chargers == None:
            list_nodes_storages_with_cs=self.get_list_nodes_storages_with_charging_station(radial, chargers)
            list_nodes_storages_with_cs = list(dict.fromkeys(list_nodes_storages_with_cs))
            logger.debug("list_nodes_storages_with_cs "+str(list_nodes_storages_with_cs))
            list_all_storage_nodes = self.get_Storage_nodes(topology)
            list_all_storage_nodes = list(dict.fromkeys(list_all_storage_nodes))
            logger.debug("list_all_storage_nodes "+str(list_all_storage_nodes))

            if not len(list_nodes_storages_with_cs) == 0:
                if list_nodes_storages_with_cs == list_all_storage_nodes:
                    return False
                else:
                    return True
            else:
                return True
        else:
            return True



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
        common = topology["common"]
        radial = topology["radials"]
        time_in_days = math.ceil(self.sim_hours / 24) + 1
        if self.is_city(common):
            city = self.get_city(common)
            logger.debug("city " + str(city))
            country = self.get_country(common)
            logger.debug("country " + str(country))
            #self.price_profile = self.get_price_profile_from_server(city,country,self.sim_days)
            flag_is_price_profile_needed = self.is_price_profile_needed(topology)
            flag_global_control = self.is_global_control_in_Storage(topology)
            logger.debug("Flag price profile needed: " + str(flag_is_price_profile_needed))
            if flag_is_price_profile_needed or flag_global_control:
                self.price_profile = self.get_price_profile_from_server(profiles, city, country, time_in_days)
                if not isinstance(self.price_profile, list):
                    return "Price prediction service missing"
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
                message = self.setTransformers(transformer)
                if not message == 0:
                    return message

            if "regcontrol" in values.keys() and values["regcontrol"] is not None:
                logger.debug("!---------------Setting RegControl------------------------ \n")
                regcontrol = values["regcontrol"]
                #                logger.debug("RegControl" + str(regcontrol))
                message = self.setRegControls(regcontrol)
                if not message == 0:
                    return message

            if "linecode" in values.keys() and values["linecode"] is not None:
                logger.debug("! ---------------Setting LineCode------------------------- \n")
                linecode = values["linecode"]
                #logger.debug("LineCode: " + str(linecode))
                message = self.setLineCodes(linecode)
                if not message == 0:
                    return message
                
                
            if "powerProfiles" in values.keys() and values["powerProfiles"] is not None:
                logger.debug("!---------------Setting powerProfile------------------------- \n")
                powerProfile = values["powerProfiles"]
                message = self.setPowerProfile(powerProfile)
                logger.debug(str(message))
                if not message == 0:
                    return message
                
                
            if "loads" in values.keys() and values["loads"] is not None:
                logger.debug("! ---------------Setting Loads------------------------- \n")
                load = values["loads"]
                powerprofile = []
                if "powerProfiles" in values.keys() and values["powerProfiles"] is not None:
                    powerprofile = values["powerProfiles"]

                logger.debug("! >>>  ---------------Loading Load Profiles beforehand ------------------------- \n")
                message = self.setLoadshapes(profiles, profess, load, powerprofile, time_in_days)

                if not message == 0:
                    return message
                logger.debug("! >>>  ---------------and the Loads afterwards ------------------------- \n")
                message = self.setLoads(load)
                if not message == 0:
                    return message

            if "capacitor" in values.keys() and values["capacitor"] is not None:
                # logger.debug("---------------Setting Capacitors-------------------------")
                logger.debug("! ---------------Setting Capacitors------------------------- \p")
                capacitor = values["capacitor"]
                # logger.debug("Capacitors: " + str(capacitor))
                message = self.setCapacitors(capacitor)
                if not message == 0:
                    return message

            if "powerLines" in values.keys() and values["powerLines"] is not None:
                # logger.debug("---------------Setting Powerlines-------------------------")
                logger.debug("!---------------Setting Powerlines------------------------- \n")

                powerLines = values["powerLines"]
                message = self.setPowerLines(powerLines)
                logger.debug(str(message))
                if not message == 0:
                    return message
                

            if "xycurves" in values.keys() and values["xycurves"] is not None:
                xycurves = values["xycurves"]  # TORemove
                message = self.setXYCurves(xycurves)
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
                message = self.setStorage(storage)  # TODO: fix and remove comment
                if not message == 0:
                    return message


            if "chargingStations" in values.keys() and values["chargingStations"] is not None:
                logger.debug("---------------Setting charging stations-------------------------")
                chargingStations = values["chargingStations"]
                message = self.setChargingStations(chargingStations)
                if not message == 0:
                    return message

            """if "voltage_regulator" in values.keys() and values["voltage_regulator"] is not None:
                logger.debug("---------------Setting Voltage regulator-------------------------")
                voltage_regulator = values["voltage_regulator"]
                logger.debug("Voltage Regulator: " + str(voltage_regulator))
                factory.gridController.setVoltageRegulator(id, voltage_regulator)
            """

            if "tshapes" in values.keys() and values["tshapes"] is not None:
                logger.debug("---------------Setting tshapes-------------------------")
                tshapes = values["tshapes"]
                logger.debug("Tshapes: " + str(tshapes))
                message = self.setTShape(tshapes)
                if not message == 0:
                    return message
            if "photovoltaics" in values.keys() and values["photovoltaics"] is not None:
                logger.debug("! ---------------Setting Photovoltaic------------------------- \n")
                photovoltaics = values["photovoltaics"]

                powerprofile = []
                if "powerProfiles" in values.keys() and values["powerProfiles"] is not None:
                    powerprofile = values["powerProfiles"]

                if not city == None and not country == None:
                    logger.debug("! >>>  ---------------Loading PV Profiles beforehand ------------------------- \n")
                    message = self.setPVshapes(profiles, profess, photovoltaics, city, country, time_in_days, powerprofile)
                    logger.debug("message "+str(message))
                    if not message == 0:
                        return message
                    logger.debug("! >>>  ---------------and the PVs afterwards ------------------------- \n")
                    message = self.setPhotovoltaic(photovoltaics)
                    logger.debug("message "+str(message))
                    if not message == 0:
                        return message
                else:
                    error = "Fatal error: city and country are missing"

                    logger.error(error)
                    return error
                logger.debug("! >>>  ---------------PVs finished ------------------------- \n")


        return 0








