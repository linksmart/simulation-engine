from profess.Http_commands import Http_commands
import re
import copy
from profess.JSONparser import *
import simplejson as json
import time

class Profess:
    def __init__(self, domain):
        self.domain = domain #domainName is different on operating systems
        self.dataList=[]
        self.httpClass = Http_commands()
        self.json_parser=JsonParser()
        self.dummy_data = {"load": {
         "meta": {
             "pf_Load": 1
         }
     },
     "photovoltaic": {
         "meta": {
             "PV_Inv_Max_Power": 15.00
         }

},
"grid":{
"meta":{
"Q_Grid_Max_Export_Power":15,
"P_Grid_Max_Export_Power":15
}
},
"generic":{
	"T_SoC":25,
    "mu_P": 1.2,
    "mu_Q": -1.5
},
"ESS":{
"meta":{
"ESS_Max_SoC":1,
"ESS_Min_SoC":0.2
}
}
}
        self.list_with_desired_output_words=["P_ESS_Output", "P_PV_Output", "P_PV_R_Output", "P_PV_S_Output"
            , "P_PV_T_Output", "Q_PV_Output", "Q_PV_R_Output", "Q_PV_S_Output", "Q_PV_T_Output"]
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
                self.post_data((self.dummy_data), value)

    def set_dummy_data(self,dummy_data):
        self.dummy_data=dummy_data
    def get_optimization_status(self):
        response = self.httpClass.get(self.domain + "optimization/status")
        json_response = response.json()
        return json_response
    def get_output(self, profess_id):
        if profess_id != "":
            response = self.httpClass.get(self.domain + "outputs/" + profess_id)
        else:
            print("No Input get output declared")
        return response.json()

    def wait_and_get_output(self):
        data=self.dataList
        something_running = True
        while something_running:
            time.sleep(.3)
            opt_status = self.get_optimization_status()
            something_running = False
            for element in data:
                for value in element:
                    for key in element[value]:
                        if opt_status["status"][key]["status"] == "running":
                            something_running = True
        output_list=[]
        for element in data:
            for value in element:
                for key in element[value]:
                    output_list.append({key:self.get_output(key)})


        return self.translate_output(output_list)



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

    def start_all(self):
        for node_name in self.json_parser.get_node_name_list():
            element_node=(next(item for item in self.json_parser.get_node_element_list() if node_name in item))
            storage=(next(item for item in element_node[node_name] if item["storageUnits"]))
            self.start(1, 24, 3600, storage["storageUnits"]["optimization_model"], 1, "ipopt", "discrete", self.get_profess_id(node_name))

    def stop(self, profess_id):
        if profess_id != "":
            response = self.httpClass.put(self.domain + "optimization/stop/" + profess_id)
            json_response = response.json()
            print(json_response)
        else:
            print("No Input to stop declared")
    def update(self, load_profiles, pv_profiles, price_profiles, soc_list, ess_con):
        self.set_profiles(load_profiles,pv_profiles,price_profiles,ess_con)
        elements = self.json_parser.get_node_element_list()
        for nodeKey in elements:
            for node_name in nodeKey:
                index=elements.index(nodeKey)
                profess_id=self.get_profess_id(node_name)
                for value in soc_list:
                    if node_name in value:
                        soc_index=soc_list.index(value)

                        self.dataList[index][node_name][profess_id]["ESS"]["SoC_Value"]=(soc_list[soc_index][node_name]/100)
                self.update_config_json(profess_id, self.dataList[index][node_name][profess_id])
    def update_config_json(self, profess_id, config_json):
        response = self.httpClass.put(self.domain + "inputs/dataset/" + profess_id, config_json)
        json_response = response.json()
        print(json_response+ ": "+profess_id)
    def set_storage(self, node_name):
        node_number = self.json_parser.get_node_name_list().index(node_name)
        for element in self.dataList[node_number]:
            node_name = element
        for element in self.dataList[node_number][node_name]:
            profess_id= element
        json_data_of_node= self.dataList[node_number][node_name][profess_id]
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
        self.dataList[node_number][node_name][profess_id] = copy.deepcopy(config_json)

    def set_profess_id_for_node(self, node_name, profess_id):
        node_number = self.json_parser.get_node_name_list().index(node_name)
        self.dataList[node_number][node_name][profess_id]= {}

    def set_profiles(self, load_profiles, pv_profiles, price_profiles, ess_con):
        for nodeName in self.json_parser.get_node_name_list():
            node_number = self.json_parser.get_node_name_list().index(nodeName)
            for element in load_profiles:
                if nodeName in element:
                    profess_id=self.get_profess_id(nodeName)
                    json_data_of_node = self.dataList[node_number][nodeName][profess_id]
                    phase=element[nodeName]
                    if nodeName + ".1" in phase:
                        json_data_of_node["load"]["P_Load_R"] = phase[nodeName + ".1"]
                    if nodeName + ".2" in phase:
                        json_data_of_node["load"]["P_Load_S"] = phase[nodeName + ".2"]
                    if nodeName + ".3" in phase:
                        json_data_of_node["load"]["P_Load_T"] = phase[nodeName + ".3"]

                    if "P_Load_R" in json_data_of_node["load"] and "P_Load_S" in json_data_of_node["load"] and \
                            "P_Load_T" in json_data_of_node["load"]:
                        three_phase = []
                        for value in range(len(json_data_of_node["load"]["P_Load_T"])):
                            three_phase_value = json_data_of_node["load"]["P_Load_R"][value] + \
                                                json_data_of_node["load"]["P_Load_S"][value] + \
                                                json_data_of_node["load"]["P_Load_T"][value]
                            three_phase.append(three_phase_value)
                        json_data_of_node["load"]["P_Load"] = three_phase
                    if nodeName + ".1.2.3" in phase:
                        json_data_of_node["load"]["P_Load"] = phase[nodeName + ".1.2.3"]
                        single_phase = []
                        for value in phase[nodeName + ".1.2.3"]:
                            value = value / 3
                            single_phase.append(value)
                        json_data_of_node["load"]["P_Load_R"] = copy.deepcopy(single_phase)
                        json_data_of_node["load"]["P_Load_S"] = copy.deepcopy(single_phase)
                        json_data_of_node["load"]["P_Load_T"] = copy.deepcopy(single_phase)
            for element in pv_profiles:
                profess_id = self.get_profess_id(nodeName)
                json_data_of_node = self.dataList[node_number][nodeName][profess_id]
                if nodeName in element:
                    phase = element[nodeName]
                    if nodeName + ".1.2.3" in phase:
                        json_data_of_node["photovoltaic"]["P_PV"] = phase[nodeName + ".1.2.3"]
                        single_phase = []
                        for value in phase[nodeName + ".1.2.3"]:
                            value = value / 3
                            single_phase.append(value)
                        json_data_of_node["photovoltaic"]["P_PV_R"] = copy.deepcopy(single_phase)
                        json_data_of_node["photovoltaic"]["P_PV_S"] = copy.deepcopy(single_phase)
                        json_data_of_node["photovoltaic"]["P_PV_T"] = copy.deepcopy(single_phase)
            for element in ess_con:
                profess_id = self.get_profess_id(nodeName)
                json_data_of_node = self.dataList[node_number][nodeName][profess_id]
                if nodeName in element:
                    phase = element[nodeName]
                    if nodeName + ".1.2.3" in phase:
                        json_data_of_node["generic"]["ESS_Control"]=phase[nodeName + ".1.2.3"]
            profess_id = self.get_profess_id(nodeName)
            json_data_of_node = self.dataList[node_number][nodeName][profess_id]
            json_data_of_node["generic"]["Price_Forecast"] = price_profiles #No reserved words for price

    def get_profess_id(self, nodeName):
        node_number = self.json_parser.get_node_name_list().index(nodeName)

        for element in self.dataList[node_number][nodeName]:
            profess_id = element
        return profess_id
    def get_node_name(self, profess_id):
        nodeName=""
        name_list = self.json_parser.get_node_name_list()
        for name in name_list:
            node_number = self.json_parser.get_node_name_list().index(name)
            for element in self.dataList[node_number][name]:
                if element==profess_id:
                    nodeName= name

        return nodeName
    def set_data_list(self):
        node_list = self.json_parser.get_node_element_list()
        for element in range(len(node_list)):
            for nodeKey in (node_list[element]):
                node_list[element] = {nodeKey: {}}

        self.dataList = node_list

    def set_up_profess(self, topology, load_profiles, pv_profiles, price_profiles, ess_con):
        self.json_parser.set_topology(topology)
        self.set_data_list()
        self.post_all_dummy_data()
        #TODO
        self.set_profiles(load_profiles, pv_profiles, price_profiles,ess_con)
        for nodeName in self.json_parser.get_node_name_list():
            self.set_storage(nodeName)
            professID=self.get_profess_id(nodeName)
            nodeNumber = self.json_parser.get_node_name_list().index(nodeName)
            self.update_config_json(professID, self.dataList[nodeNumber][nodeName][professID])


    def translate_output(self, output_data):
        #print(self.get)
        output_list=copy.deepcopy(output_data)
        #finding the lowest value of each variable
        for element in output_data:
            for node_name in element:
                for profess_id in element[node_name]:
                    helper = dict(sorted(element[node_name][profess_id].items()))
                    index=output_data.index(element)
                    output_list[index][node_name][profess_id] = element[node_name][profess_id][min(helper)]
        #matching the right professid with nodename
        for element in self.dataList:
            for value in element:
                for key in output_list:
                    for profess_id in key:
                        if profess_id in element[value]:
                            index=output_list.index(key)
                            output_list[index]={value:output_list[index]}
        #TODO group phases together, i.e. translate phases into number
        # for node in output_list:
        #     for node_name in node:
        #         print(node[node_name])
        #         for profess_id in node[node_name]:
        #             node[node_name][profess_id]["Grid"]=[]
        #             for element in node[node_name][profess_id]:
        #                 if str(element).startswith("P_Grid"):
        #                     power_name="P"
        #                 if str(element).startswith("Q_Grid"):
        #                     power_name="Q"
        #                 if str(element).endswith("Grid_R_Output"):
        #                     print(node[node_name][profess_id]["Grid"])
        #                     print((any(helper_dict["P"]) for helper_dict in node[node_name][profess_id]["Grid"]))
        #                     if any(node[node_name][profess_id]["Grid"])==power_name:
        #
        #                         node[node_name][profess_id]["Grid"][power_name][node_name + ".1"]={node[node_name][profess_id][element]}
        #                     else:
        #                         node[node_name][profess_id]["Grid"].append({power_name:{node_name+".1":node[node_name][profess_id][element]}})
        #                 if str(element).endswith("Grid_S_Output"):
        #                     if any(node[node_name][profess_id]["Grid"])==power_name:
        #                         node[node_name][profess_id]["Grid"][power_name][node_name + ".2"]={node[node_name][profess_id][element]}
        #                     else:
        #                         node[node_name][profess_id]["Grid"].append({power_name:{node_name+".2":node[node_name][profess_id][element]}})
        #                 if str(element).endswith("Grid_T_Output"):
        #                     if any(node[node_name][profess_id]["Grid"])==power_name:
        #                         node[node_name][profess_id]["Grid"][power_name][node_name + ".3"]={node[node_name][profess_id][element]}
        #                     else:
        #                         node[node_name][profess_id]["Grid"].append({power_name:{node_name+".3":node[node_name][profess_id][element]}})
        helper=copy.deepcopy(output_list)

        for element in helper:
            for node_name in element:
                for profess_id in element[node_name]:
                    for key in element[node_name][profess_id]:
                        if not key in self.list_with_desired_output_words:
                            index=helper.index(element)
                            output_list[index][node_name][profess_id].pop(key, None)
        return output_list



