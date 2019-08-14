import json
from collections.abc import Iterable
import re

class JsonParser:
    # @search returns a list with results
    # @searchIn is the dict/list we search in
    # @searchFor is the String we search for
    # @returnsAll if true, returns all where searchFor fits, even if searchID doesn't fit
    def __init__(self):
        self.topology = ""

    def search(self, search_in, search_for, search_id, returns_all):

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
        global topology
        self.topology = json_topology

    def get_node_element_list(self):
        node_element_list = []
        storage_node_list = []
        pv_node_list = []
        for radial_number in range(len(self.topology["radials"])):
            if "storageUnits" in self.topology["radials"][radial_number].keys():
                storage_node_list = self.search(self.topology["radials"][radial_number]["storageUnits"], "bus1", "", True)
                node_list=storage_node_list
            if "photovoltaics" in self.topology["radials"][radial_number].keys():
                pv_node_list = self.search(self.topology["radials"][radial_number]["photovoltaics"], "bus1", "", True)
                node_list=pv_node_list
            if storage_node_list is not None and pv_node_list is not None:
                node_list= storage_node_list + list(set(pv_node_list) - set(storage_node_list))
                #print(storage_node_list)
            count = 0
            for element in node_list:

                pattern = re.compile("[^.]*")  # regex to find professID
                m = pattern.findall(element)
                element = m[0]
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
                #print("here is for")
                #print(node_element_list)
                if "photovoltaics" in self.topology["radials"][radial_number]:
                    for pvunits in self.topology["radials"][radial_number]["photovoltaics"]:
                        m = pattern.findall(pvunits["bus1"])
                        pvunitsBus= m[0]
                        if pvunitsBus is element:
                            pv_index = self.topology["radials"][radial_number]["photovoltaics"].index(pvunits)
                            node_element_list.append(
                                {element: [
                                    {"photovoltaics": self.topology["radials"][radial_number]["photovoltaics"][
                                        pv_index]}]})

                #print(element)
                #print(count)
                #print(node_element_list)
                if node_element_list[count][element] is not None:
                    node_element_list[count][element].append(
                        {"loads": (
                            self.search(self.topology["radials"][radial_number]["loads"], "bus", element, False))})

                    # TODO PV etc
                count = count + 1

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
