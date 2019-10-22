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

    def get_all_elements(self, element_name):
        """
        :param element_name: type of element, for example "storageUnits"
        :return: all elements in the topology with the type element_name
        """
        search_result=[]
        if "radials" in self.topology:
            for radial in self.topology["radials"]:
                for element in radial:
                    if element_name in element:
                        search_result=search_result+radial[element]
        return search_result

    def filter_search(self,search_key, search_value, element_list):
        """
        filters the element_list and returns only the elements where search_key and search_value fit
        :param search_key: name of key we want to match
        :param search_value: value searchkey needs to be
        :param element_list: List where we search in
        :return: list where search_key and search_value fit
        """
        filter_result=[]
        for element in element_list:
            for element_key in element:
                if element_key == search_key and element[element_key] == search_value:
                    #print(element)
                    filter_result.append(element)

        return filter_result


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

    def get_node_element_list(self, soc_list):
        """
        :return: a list with all nodes that have a ess and all connected devices(loads, pvs)
        syntax: [{node_name1:["storageUnits":{...}, "photovoltaics" :{ ....}, "loads":{ ...}]},{node_name2:[ ....]}]
        """
        ##logger.debug("get_node_element_list started")
        node_element_list = []

        #logger.debug("topology "+str(self.topology))
        if "radials" in self.topology.keys():
            for radial_number in range(len(self.topology["radials"])):
                node_list = self.get_node_name_list(soc_list)
                #logger.debug("node list "+str(node_list))
                index = 0
                if node_list!=0:
                    for node_name in node_list:
                        #logger.debug("node name "+str(node_name))
                        #adds ess to the output list
                        if "storageUnits" in self.topology["radials"][radial_number]:
                            for essunits in self.topology["radials"][radial_number]["storageUnits"]:
                                #logger.debug("ess units"+str(essunits))
                                pattern = re.compile("[^.]*")
                                m = pattern.findall(essunits["bus1"])
                                essunitsBus= m[0]
                                #logger.debug("essunitsbus "+str(essunitsBus))
                                node_name_original = node_name
                                if "." in node_name:
                                    node_name = node_name.split(".")[0]
                                #logger.debug("node name " + str(node_name))
                                if essunitsBus == node_name:
                                    ess_index = self.topology["radials"][radial_number]["storageUnits"].index(essunits)
                                    node_element_list.append(
                                        {node_name_original: [
                                            {"storageUnits": self.topology["radials"][radial_number]["storageUnits"][
                                                ess_index]}]})
                        #adds pv to ouput list
                        if "photovoltaics" in self.topology["radials"][radial_number]:
                            for pvunits in self.topology["radials"][radial_number]["photovoltaics"]:
                                pattern = re.compile("[^.]*")
                                m = pattern.findall(pvunits["bus1"])
                                pvunitsBus= m[0]
                                #logger.debug("pvunitsBus "+str(pvunitsBus))
                                #logger.debug("node name " + str(node_name))
                                if pvunitsBus == node_name:
                                    alreadyInList=False
                                    for item in node_element_list:
                                        #logger.debug("item "+str(item))
                                        if node_name_original in item.keys():
                                            alreadyInList = True
                                            listIndex= node_element_list.index(item)
                                    pv_index = self.topology["radials"][radial_number]["photovoltaics"].index(pvunits)
                                    #logger.debug("alreadyInList "+str(alreadyInList))
                                    if alreadyInList:
                                        node_element_list[listIndex][node_name_original].append({"photovoltaics": self.topology["radials"][radial_number]["photovoltaics"][
                                                    pv_index]})
                                    else:
                                        node_element_list.append(
                                            {node_name_original: [
                                                {"photovoltaics": self.topology["radials"][radial_number]["photovoltaics"][
                                                    pv_index]}]})


                        # adds loads to output list
                        if node_element_list[index][node_name_original] is not None:
                            #it depends on the topology
                            load_elements_list=self.get_all_elements("loads")
                            node_element_list[index][node_name_original].append(
                                {"loads": (
                                    self.filter_search("bus",node_name_original,load_elements_list)+
                                    self.filter_search("id",node_name_original,load_elements_list))})
                        else:
                            logger.debug("no load was added for "+ str(node_name_original)+ " in get_node_elements")
                        index = index + 1
                        #logger.debug("node element list " + str(node_element_list))
        else: logger.debug("no radials where found")

        ##logger.debug(node_element_list)
        return node_element_list

    def get_node_name_list(self, soc_list):
        """

        :return: a list of node_names where an ess is connected, otherwise 0 is returned
        [node_name1, node_name2, ...]
        """
        storage_node_list = []
        node_list = []
        for element in soc_list:
            #logger.debug("element "+str(element))
            for node_name in element.keys():
                node_list.append(node_name)
        if not node_list == []:
            node_list = list(dict.fromkeys(node_list))

        #logger.debug("node list "+str(node_list))
        """pv_node_list = []
        
        if "radials" in self.topology.keys():
            for radial_number in range(len(self.topology["radials"])):
                # search for nodes with ESS
                if "storageUnits" in self.topology["radials"][radial_number].keys():

                    for storage_node in self.get_all_elements("storageUnits"):
                        storage_node_name=storage_node["bus1"]
                        pattern = re.compile("[^.]*")  # regex to shorten nodde_name.1.2.3 or node_name.1 etc to node_name
                        storage_regex = pattern.findall(storage_node_name)
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
                #     node_list= storage_node_list + list(set(pv_node_list) - set(storage_node_list))"""

        if node_list != []:
            return node_list
        else: return None

