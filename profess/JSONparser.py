import json
from collections.abc import Iterable
import re
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class JsonParser:
    # @search returns a list with results
    # @searchIn is the dict/list we search in
    # @searchFor is the String we search for
    # @returnsAll if true, returns all where searchFor fits, even if searchID doesn't fit
    def __init__(self):
        self.topology = ""

    def search(self, search_in, search_for, search_id, returns_all):
        #logger.debug("search ")
        #logger.debug(search_in)
        #logger.debug(search_for)
        #logger.debug(search_id)
        search_result = []
        dummy_list = search_in
        if type(search_in) == list:
            dummy_list = []
            for element in range(len(search_in)):
                dummy_list.append(element)
        for value in dummy_list:
            if type(value) == dict or type(value) == list:
                for element in value:
                    if isinstance(value[element], Iterable) and type(value[element]) != str:
                        search_result = search_result + self.search(value[element], search_for, search_id, returns_all)
            else:
                if str(value).startswith(search_for):
                    if str(search_in[value]).startswith(search_id) or returns_all:
                        if returns_all:
                            if type(search_in[value]) == list:
                                helpList = {}
                                for element in search_in[value]:
                                    search_result.append(element)
                            else:
                                search_result.append(search_in[value])
                        else:

                            search_result.append(search_in)
                if isinstance(search_in[value], Iterable) and type(search_in[value]) != str:
                    search_result = search_result + self.search(search_in[value], search_for, search_id, returns_all)

        return search_result

    def set_topology(self, json_topology):
        logger.debug("topology was changed --------------------------------------------------------------------------")

        logger.debug(self.topology)
        global topology

        self.topology = json_topology
        logger.debug("to: ")
        logger.debug(self.topology)

    def get_topology(self):
        return self.topology

    def get_node_element_list(self):
        ##logger.debug("get_node_element_list started")

        node_element_list = []
        storage_node_list = []
        pv_node_list = []
        if "radials" in self.topology:
            for radial_number in range(len(self.topology["radials"])):
                if "storageUnits" in self.topology["radials"][radial_number].keys():
                    for element in self.search(self.topology["radials"][radial_number]["storageUnits"], "bus1", "", True):
                        pattern = re.compile("[^.]*")  # regex to find professID
                        m = pattern.findall(element)
                        element = m[0]
                        storage_node_list.append(element)
                    node_list=storage_node_list
                    ##logger.debug("storages found")


                if "photovoltaics" in self.topology["radials"][radial_number].keys():
                    for element in self.search(self.topology["radials"][radial_number]["photovoltaics"], "bus1", "", True):
                        pattern = re.compile("[^.]*")  # regex to find professID
                        m = pattern.findall(element)
                        element = m[0]
                        pv_node_list.append(element)
                    node_list=pv_node_list
                    ##logger.debug("pvs found")
                if storage_node_list is not None and pv_node_list is not None:
                    node_list= storage_node_list + list(set(pv_node_list) - set(storage_node_list))
                ##logger.debug("list of nodes with pv or ess :")
                ##logger.debug(node_list)
                count = 0
                for element in node_list:
                    if "storageUnits" in self.topology["radials"][radial_number]:
                        for essunits in self.topology["radials"][radial_number]["storageUnits"]:
                            m = pattern.findall(essunits["bus1"])
                            essunitsBus= m[0]
                            if essunitsBus == element:
                                ess_index = self.topology["radials"][radial_number]["storageUnits"].index(essunits)
                                node_element_list.append(
                                    {element: [
                                        {"storageUnits": self.topology["radials"][radial_number]["storageUnits"][
                                            ess_index]}]})
                    if "photovoltaics" in self.topology["radials"][radial_number]:
                        for pvunits in self.topology["radials"][radial_number]["photovoltaics"]:
                            #print(pvunits)
                            #print(element)
                            m = pattern.findall(pvunits["bus1"])
                            pvunitsBus= m[0]
                            if pvunitsBus == element:
                                alreadyInList=False
                                for item in node_element_list:
                                    if element in item.keys():
                                        alreadyInList = True
                                        listIndex= node_element_list.index(item)
                                pv_index = self.topology["radials"][radial_number]["photovoltaics"].index(pvunits)
                                if alreadyInList:
                                    node_element_list[listIndex][element].append({"photovoltaics": self.topology["radials"][radial_number]["photovoltaics"][
                                                pv_index]})
                                else:
                                    node_element_list.append(
                                        {element: [
                                            {"photovoltaics": self.topology["radials"][radial_number]["photovoltaics"][
                                                pv_index]}]})

                    #print(element)
                    #print(count)
                    #print(node_element_list)

                    if node_element_list[count][element] is not None:
                        ##logger.debug("load was added to "+str(element))
                        ##logger.debug(self.search(self.topology["radials"][radial_number]["loads"], "bus", element, False)+self.search(self.topology["radials"][radial_number]["loads"], "id", element, False))
                        node_element_list[count][element].append(
                            {"loads": (
                                self.search(self.topology["radials"][radial_number]["loads"], "bus", element, False)+self.search(self.topology["radials"][radial_number]["loads"], "id", element, False))})
                    else:
                        logger.debug("no load was added")
                        # TODO PV etc
                    count = count + 1
        else: logger.debug("no radials where found")

        ##logger.debug(node_element_list)
        return node_element_list

    def get_node_name_list(self):
        name_list = []
        if not self.get_node_element_list() == -1:
            for element in self.get_node_element_list():
                for value in element:
                    name_list.append(value)
            return name_list
        else:
            return -1
