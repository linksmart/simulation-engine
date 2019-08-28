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
    def __init__(self,parameter_topology):
        self.topology = parameter_topology

    def search(self, search_in, search_for, search_id, returns_all):
        """

        :param search_in: in which list, dict is searched in
        :param search_for: for which string are searching for for example "bus"
        :param search_id: value searchFor should have
        :param returns_all: boolean if all should be returned, example: search(topology, "StorageUnits","",True) returns
        all storage units
        :return: returns the result of the search
        """
        search_result = []
        dummy_list = search_in
        #in case we search in a list we have to create a list of indices, to have a consistent iteration
        if type(search_in) == list:
            dummy_list = []
            for element in range(len(search_in)):
                dummy_list.append(element)
        for iteration_value in dummy_list:
            if type(iteration_value) == dict or type(iteration_value) == list:
                for element in iteration_value:
                    if isinstance(iteration_value[element], Iterable) and type(iteration_value[element]) != str:
                        search_result = search_result + self.search(iteration_value[element], search_for, search_id, returns_all)
            else:
                if str(iteration_value).startswith(search_for):
                    if str(search_in[iteration_value]).startswith(search_id) or returns_all:
                        if returns_all:
                            if type(search_in[iteration_value]) == list:
                                helpList = {}
                                for element in search_in[iteration_value]:
                                    search_result.append(element)
                            else:
                                search_result.append(search_in[iteration_value])
                        else:

                            search_result.append(search_in)
                if isinstance(search_in[iteration_value], Iterable) and type(search_in[iteration_value]) != str:
                    search_result = search_result + self.search(search_in[iteration_value], search_for, search_id, returns_all)

        return search_result



    def set_topology(self, json_topology):
        """
        changes the topology
        :param json_topology: new topology
        :return:
        """
        self.topology = json_topology
        logger.debug(self.topology)
        logger.debug("-------------------------------------------------------------------------------------------------")
        logger.debug("topology was changed")
        logger.debug("-------------------------------------------------------------------------------------------------")

    def get_node_element_list(self):
        """
        :return: a list with all nodes that have a ess and all connected devices(loads, pvs)
        """
        ##logger.debug("get_node_element_list started")
        node_element_list = []

        #logger.debug("topology "+str(self.topology))
        if "radials" in self.topology.keys():
            for radial_number in range(len(self.topology["radials"])):
                node_list = self.get_node_name_list()
                index = 0
                for node_name in node_list:
                    #adds ess to the output list
                    if "storageUnits" in self.topology["radials"][radial_number]:
                        for essunits in self.topology["radials"][radial_number]["storageUnits"]:
                            pattern = re.compile("[^.]*")
                            m = pattern.findall(essunits["bus1"])
                            essunitsBus= m[0]
                            if essunitsBus == node_name:
                                ess_index = self.topology["radials"][radial_number]["storageUnits"].index(essunits)
                                node_element_list.append(
                                    {node_name: [
                                        {"storageUnits": self.topology["radials"][radial_number]["storageUnits"][
                                            ess_index]}]})
                    #adds pv to ouput list
                    if "photovoltaics" in self.topology["radials"][radial_number]:
                        for pvunits in self.topology["radials"][radial_number]["photovoltaics"]:
                            pattern = re.compile("[^.]*")
                            m = pattern.findall(pvunits["bus1"])
                            pvunitsBus= m[0]
                            if pvunitsBus == node_name:
                                alreadyInList=False
                                for item in node_element_list:
                                    if node_name in item.keys():
                                        alreadyInList = True
                                        listIndex= node_element_list.index(item)
                                pv_index = self.topology["radials"][radial_number]["photovoltaics"].index(pvunits)
                                if alreadyInList:
                                    node_element_list[listIndex][node_name].append({"photovoltaics": self.topology["radials"][radial_number]["photovoltaics"][
                                                pv_index]})
                                else:
                                    node_element_list.append(
                                        {node_name: [
                                            {"photovoltaics": self.topology["radials"][radial_number]["photovoltaics"][
                                                pv_index]}]})
                    # adds loads to output list
                    if node_element_list[index][node_name] is not None:
                        #it depends on the topology
                        node_element_list[index][node_name].append(
                            {"loads": (
                                self.search(self.topology["radials"][radial_number]["loads"], "bus", node_name, False)+
                                self.search(self.topology["radials"][radial_number]["loads"], "id", node_name, False))})
                    else:
                        logger.debug("no load was added")
                    index = index + 1
        else: logger.debug("no radials where found")

        ##logger.debug(node_element_list)
        return node_element_list

    def get_node_name_list(self):
        """

        :return: a list of node_names where an ess is connected, otherwise 0 is returned
        """
        storage_node_list = []
        pv_node_list = []
        node_list = []
        if "radials" in self.topology.keys():
            for radial_number in range(len(self.topology["radials"])):
                # search for nodes with ESS
                if "storageUnits" in self.topology["radials"][radial_number].keys():
                    for storage_node in self.search(self.topology["radials"][radial_number]["storageUnits"], "bus1", "", True):
                        pattern = re.compile("[^.]*")  # regex to shorten nodde_name.1.2.3 or node_name.1 etc to node_name
                        storage_regex = pattern.findall(storage_node)
                        node_name = storage_regex[0]
                        storage_node_list.append(node_name)
                    node_list = storage_node_list
                    ##logger.debug("storages found")

                # if "photovoltaics" in self.topology["radials"][radial_number].keys():
                #     for element in self.search(self.topology["radials"][radial_number]["photovoltaics"], "bus1", "", True):
                #         pattern = re.compile("[^.]*")  # regex to find professID
                #         m = pattern.findall(element)
                #         element = m[0]
                #         pv_node_list.append(element)
                #     node_list=pv_node_list
                #     ##logger.debug("pvs found")
                # if storage_node_list is not None and pv_node_list is not None:
                #     node_list= storage_node_list + list(set(pv_node_list) - set(storage_node_list))

        if node_list != []:
            return node_list
        else: return 0
