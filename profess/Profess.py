from Http_commands import Http_commands
import re
import copy
from JSONparser import *
import simplejson as json


class Profess:
    def __init__(self, domain, dummy_data):
        self.domain = domain #domainName is different on operating systems
        self.dataList=[]
        self.httpClass = Http_commands()
        self.json_parser=JsonParser()
        self.dummy_data = dummy_data
        print("profess class created")

    def post_model(self, model_name, model_data):
        response=self.httpClass.put(self.domain + "models/" + model_name, model_data)
        json_response = response.json()
        print(json_response)

    def post_data(self, input_data, node_name):

        response = self.httpClass.post(self.domain + "inputs/dataset", input_data, "json")
        json_response = response.json()
        pattern = re.compile("/inputs*[/]([^']*)")  #regex to find profess_id
        m= pattern.findall(str(response.headers))
        if m != "":
            profess_id = m[0]
        else:
            print("an error happened with regex")
        print(json_response + ": " + profess_id)
        self.set_profess_id_for_node(node_name, profess_id)
        self.set_config_json(node_name, profess_id, input_data)

    def post_all_dummy_data(self):
        elements = self.json_parser.get_node_element_list()
        for nodeKey in elements:
            for value in nodeKey:
                self.post_data(json.loads(self.dummy_data), value)

    def set_dummy_data(self,dummy_data):
        self.dummy_data=dummy_data

    def get_output(self, profess_id):
        if profess_id != "":
            response = self.httpClass.get(self.domain + "outputs/" + profess_id)
        else:
            print("No Input get output declared")
        return response.json()

    def start(self, freq, horizon, dt, model, repition, solver, optType, profess_id):
        if profess_id != "":
            response = self.httpClass.put(self.domain + "optimization/start/" + profess_id, {"control_frequency": freq,
                                                                                    "horizon_in_steps": horizon,
                                                                                    "dT_in_seconds": dt,
                                                                                    "model_name": model,
                                                                                    "repetition": repition,
                                                                                             "solver": solver,
                                                                                             "optimization_type": optType})
            json_response = response.json()
            print(json_response +  ": " +profess_id)
        else:
            print("No Input to start declared")

    def start_all(self, model_name):
        for element in self.json_parser.get_node_name_list():

            self.start(10, 24, 3600, model_name, 1, "ipopt", "discrete", self.get_profess_id(element))

    def stop(self, profess_id):
        if profess_id != "":
            response = self.httpClass.put(self.domain + "optimization/stop/" + profess_id)
            json_response = response.json()
            print(json_response)
        else:
            print("No Input to stop declared")

    def update_config_json(self, profess_id, config_json):
        self.httpClass.put(self.domain + "inputs/dataset/" + profess_id, config_json)

    def set_storage(self, node_name):
        node_number = self.json_parser.get_node_name_list().index(node_name)
        for element in dataList[node_number]:
            node_name = element
        for element in dataList[node_number][node_name]:
            profess_id= element
        json_data_of_node= dataList[node_number][node_name][profess_id]
        json_data_of_node["ESS"]["SoC_Value"] = self.json_parser.get_node_element_list()[node_number][node_name][0]["storageUnits"]["soc"] / 100
        json_data_of_node["ESS"]["meta"]["ESS_Charging_Eff"] = self.json_parser.get_node_element_list()[node_number][node_name][0]["storageUnits"][
            "charge_efficiency"] / 100
        json_data_of_node["ESS"]["meta"]["ESS_Discharging_Eff"] = self.json_parser.get_node_element_list()[node_number][node_name][0]["storageUnits"][
            "discharge_efficiency"] / 100
        json_data_of_node["ESS"]["meta"]["ESS_Max_Charge_Power"] = self.json_parser.get_node_element_list()[node_number][node_name][0]["storageUnits"][
            "kw_rated"]
        json_data_of_node["ESS"]["meta"]["ESS_Max_Discharge_Power"] = self.json_parser.get_node_element_list()[node_number][node_name][0]["storageUnits"][
            "kw_rated"]
        json_data_of_node["ESS"]["meta"]["ESS_Capacity"] = self.json_parser.get_node_element_list()[node_number][node_name][0]["storageUnits"]["kwh_rated"]

    def set_config_json(self, node_name, profess_id, config_json):
        node_number = self.json_parser.get_node_name_list().index(node_name)
        dataList[node_number][node_name][profess_id] = copy.deepcopy(config_json)

    def set_profess_id_for_node(self, node_name, profess_id):
        node_number = self.json_parser.get_node_name_list().index(node_name)
        dataList[node_number][node_name][profess_id]= {}

    def set_profiles(self, load_profiles, pv_profiles, price_profiles):
        for nodeName in self.json_parser.get_node_name_list():
            node_number = self.json_parser.get_node_name_list().index(nodeName)
            for element in load_profiles:
                if nodeName in element:
                    profess_id=self.get_profess_id(nodeName)
                    json_data_of_node = dataList[node_number][nodeName][profess_id]
                    for phase in element[nodeName]:

                        if nodeName+".1" in phase:
                            json_data_of_node["load"]["P_Load_R"] = phase[nodeName+".1"]
                        if nodeName+".2" in phase:
                            json_data_of_node["load"]["P_Load_S"] = phase[nodeName+".2"]
                        if nodeName+".3" in phase:
                            json_data_of_node["load"]["P_Load_T"] = phase[nodeName+".3"]
            for element in pv_profiles:
                if nodeName in element:
                    profess_id = self.get_profess_id(nodeName)
                    json_data_of_node = dataList[node_number][nodeName][profess_id]
                    json_data_of_node["photovoltaic"]["P_PV"] = element[nodeName]

            profess_id = self.get_profess_id(nodeName)
            json_data_of_node = dataList[node_number][nodeName][profess_id]
            json_data_of_node["generic"]["Price_Forecast"] = price_profiles #No reserved words for price

    def get_profess_id(self, nodeName):
        node_number = self.json_parser.get_node_name_list().index(nodeName)

        for element in dataList[node_number][nodeName]:
            profess_id = element
        return profess_id

    def set_data_list(self):
        node_list = self.json_parser.get_node_element_list()
        for element in range(len(node_list)):
            for nodeKey in (node_list[element]):
                node_list[element] = {nodeKey: {}}

        global dataList
        dataList = node_list

    def set_up_profess(self, topology, load_profiles, pv_profiles, price_profiles):
        self.json_parser.set_topology(topology)
        self.set_data_list()
        self.post_all_dummy_data()
        #TODO
        self.set_profiles(load_profiles, pv_profiles, price_profiles)
        for nodeName in self.json_parser.get_node_name_list():
            self.set_storage(nodeName)
            professID=self.get_profess_id(nodeName)
            nodeNumber = self.json_parser.get_node_name_list().index(nodeName)
            self.update_config_json(professID, dataList[nodeNumber][nodeName][professID])

    def set_dummy_json(self, dummy):
        global dummyInputData
        dummyInputData=dummy
