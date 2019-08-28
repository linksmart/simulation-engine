from profess.Http_commands import Http_commands
import re
import copy
from profess.JSONparser import *
import simplejson as json
import time
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
class Profess:
    def __init__(self, domain,topology):
        self.domain = domain #domainName is different on operating systems
        self.dataList=[]
        self.httpClass = Http_commands()
        self.json_parser=JsonParser()
        self.json_parser.set_topology(topology)
        self.storage_mapping={"soc": "SoC_Value", "charge_efficiency":{"meta":"ESS_Charging_Eff"},"discharge_efficiency"
        :{"meta":"ESS_Discharging_Eff"},"kw_rated":[{"meta":"ESS_Max_Charge_Power"},{"meta":"ESS_Max_Discharge_Power"}],
                              "kwh_rated":{"meta":"ESS_Capacity"},"max_charging_power":{"meta":"ESS_Max_Charge_Power"},
                              "max_discharging_power":{"meta":"ESS_Max_Discharge_Power"},
                              "storage_capacity":{"meta":"ESS_Capacity"},"min_soc":{"meta":"ESS_Min_SoC"},"max_soc":
                                  {"meta":"ESS_Max_SoC"}}
        self.percentage_mapping=["charge_efficiency","soc","discharge_efficiency","min_soc","max_soc"]
        self.pv_mapping={"max_power_kW":"PV_Inv_Max_Power"}
        self.dummy_data = {"load": {
         "meta": {
         }
     },
     "photovoltaic": {
         "meta": {
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
},
"ESS":{
"meta":{
"ESS_Max_SoC":1,
"ESS_Min_SoC":0.2,
"ESS_Discharging_Eff":0.95,
"ESS_Charging_Eff":0.95
}
}
}
        self.list_with_desired_output_words=["P_ESS_Output", "P_PV_Output", "P_PV_R_Output", "P_PV_S_Output"
            , "P_PV_T_Output", "Q_PV_Output", "Q_PV_R_Output", "Q_PV_S_Output", "Q_PV_T_Output"]

        logger.debug("Profess instance created")

    def post_model(self, model_name, model_data):
        logger.debug("postmodel started "+ model_name)
        response=self.httpClass.put(self.domain + "models/" + model_name, model_data)
        json_response = response.json()
        logger.debug(json_response)

    def post_data(self, input_data, node_name):
        logger.debug("post data started "+ node_name)
        response = self.httpClass.post(self.domain + "inputs/dataset", input_data, "json")
        json_response = response.json()
        pattern = re.compile("/inputs*[/]([^']*)")  #regex to find profess_id
        m= pattern.findall(str(response.headers))
        if m != "":
            profess_id = m[0]
        else:
            logger.error("post_data failed at "+node_name)
        logger.debug(json_response + ": " + profess_id)
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
            logger.debug("No Input get output declared")
        return response.json()
    def is_running(self):
        data=self.dataList
        time.sleep(5)
        opt_status = self.get_optimization_status()
        logger.debug("optimization status: ")
        logger.debug(opt_status)
        for element in data:
            for value in element:
                for key in element[value]:
                    if opt_status["status"][key]["status"] == "running":
                        logger.debug("An optimization is still running " + key)
                        return True

        return False

    def wait_and_get_output(self):
        logger.debug("wait for ofw output")
        data=self.dataList
        while self.is_running():
            time.sleep(0.1)
        output_list=[]
        for element in data:
            for value in element:
                for key in element[value]:
                    output_list.append({key:self.get_output(key)})

        logger.debug("OFW finished, all optimizations stopped")
        return self.translate_output(output_list)



    def start(self, freq, horizon, dt, model, repition, solver, optType, profess_id):
        logger.debug("start "+profess_id)
        if profess_id != "":
            response = self.httpClass.put(self.domain + "optimization/start/" + profess_id, {"control_frequency": freq,
                                                                                    "horizon_in_steps": horizon,
                                                                                    "dT_in_seconds": dt,
                                                                                    "model_name": model,
                                                                                    "repetition": repition,
                                                                                             "solver": solver,
                                                                                             "optimization_type": optType})
            json_response = response.json()
            logger.debug(json_response +  ": " +profess_id)
            logger.debug("status code " +str(response.status_code))
            if response.status_code == 200 and json_response=="System started succesfully":
                return 0
            else:

                return response
        else:
            logger.debug("No Input to start declared")
            return 1

    def start_all(self, optimization_model=None):
        logger.debug("All optimizations are being started.")
        for node_name in self.json_parser.get_node_name_list():
            element_node=(next(item for item in self.json_parser.get_node_element_list() if node_name in item))
            for item in element_node[node_name]:
                if "storageUnits" in item:
                    storage = next(item for item in element_node[node_name] if item["storageUnits"])
                    model = storage["storageUnits"]["optimization_model"]
            if optimization_model is None:
                optimization_model=model
            start_response=self.start(1, 24, 3600, optimization_model, 1, "ipopt", "discrete", self.get_profess_id(node_name))
            if start_response:
                self.check_start_issue(start_response,node_name)
                return 1
        return 0
    def check_start_issue(self,response,node_name):
        json_response=response.json()
        if "Data source for following keys not declared:" in json_response:
            logger.error("Missing data for optimization model, couldn't start")
            pattern = re.compile("'(.*?)'")  # regex to find profess_id
            m = pattern.findall(str(json_response))
            for element in m:
                if "PV" in element:
                    node_element_list=self.json_parser.get_node_element_list()
                    for bus_element in node_element_list:
                        if node_name in bus_element:
                            pv_flag=False
                            storage_info=""
                            for node_element in bus_element[node_name]:
                                if "photovoltaic" in node_element:
                                    pv_flag = True
                                if "storageUnits" in node_element:
                                    storage_info=node_element
                            if pv_flag:
                                logger.error("PV Information is missing but PV is connected at :"+node_name)
                            else:
                                logger.error(element+" is needed for the optimization, but no pv was connected to :" + node_name)
                                logger.error(storage_info)
        else:
            logger.error("Failed to start because of other reasons")
        logger.debug("--------------------------------------------------------------------------------------------------------")
    def stop(self, profess_id):
        logger.debug("stop "+profess_id)
        if profess_id != "":
            response = self.httpClass.put(self.domain + "optimization/stop/" + profess_id)
            json_response = response.json()
            logger.debug(json_response+" :"+str(profess_id))
        else:
            logger.debug("No Input to stop declared")
    def update_config_json(self, profess_id, config_json):
        logger.debug("update_config_json has started")
        response = self.httpClass.put(self.domain + "inputs/dataset/" + profess_id, config_json)
        json_response = response.json()
        logger.debug(json_response+ ": "+profess_id)
    def set_storage(self, node_name):
        logger.debug("set_storage of "+ node_name)
        node_number = self.json_parser.get_node_name_list().index(node_name)
        for element in self.dataList[node_number]:
            node_name = element
        for profess_id in self.dataList[node_number][node_name]:
            json_data_of_node= self.dataList[node_number][node_name][profess_id]
            for radial_number in range(len(self.json_parser.topology["radials"])):
                node_element_list=self.json_parser.get_node_element_list()[node_number][node_name]
                storage_index=0
                for element in node_element_list:
                    if "storageUnits" in element:
                        storage_index=node_element_list.index(element)
                if "storageUnits" in node_element_list[storage_index].keys():
                    for element in self.storage_mapping:
                        if element in node_element_list[storage_index]["storageUnits"]:
                            percentage = 1
                            if element in self.percentage_mapping:
                                percentage=100
                            if type(self.storage_mapping[element]) == dict:
                                json_data_of_node["ESS"]["meta"][self.storage_mapping[element]["meta"]]=\
                                    node_element_list[storage_index]["storageUnits"][element]/percentage
                            if type(self.storage_mapping[element]) == list:
                                for part in self.storage_mapping[element]:
                                    if "meta" in part:
                                        json_data_of_node["ESS"]["meta"][part["meta"]] = node_element_list[storage_index]
                                        ["storageUnits"][element]/percentage
                                    else:
                                        json_data_of_node["ESS"][part] = node_element_list[storage_index]["storageUnits"][element]/percentage
                            if type(self.storage_mapping[element]) == str:
                                json_data_of_node["ESS"][self.storage_mapping[element]] = node_element_list[storage_index]["storageUnits"][element]/percentage

    def set_photovoltaics(self,node_name):
        logger.debug("set photovoltaics "+ node_name)
        node_number = self.json_parser.get_node_name_list().index(node_name)
        for profess_id in self.dataList[node_number][node_name]:
            json_data_of_node= self.dataList[node_number][node_name][profess_id]
            for radial_number in range(len(self.json_parser.topology["radials"])):
                node_element_list=self.json_parser.get_node_element_list()[node_number][node_name]
                pv_index=0
                for element in node_element_list:
                    if "photovoltaics" in element:
                        pv_index=node_element_list.index(element)
                if "photovoltaics" in node_element_list[pv_index]:

                    for element in self.pv_mapping:
                        if element in node_element_list[pv_index]["photovoltaics"]:
                            percentage = 1
                            if element in self.percentage_mapping:
                                percentage=100
                            if type(self.pv_mapping[element]) == str:
                                json_data_of_node["photovoltaic"][self.pv_mapping[element]] = node_element_list[pv_index]["photovoltaics"][element]/percentage

    def set_config_json(self, node_name, profess_id, config_json):
        logger.debug("set_config_json "+node_name+" ,"+profess_id)
        logger.debug(config_json)
        node_number = self.json_parser.get_node_name_list().index(node_name)
        self.dataList[node_number][node_name][profess_id] = copy.deepcopy(config_json)

    def set_profess_id_for_node(self, node_name, profess_id):
        logger.debug("set_profess_id_for_node "+node_name+" ,"+profess_id)
        node_number = self.json_parser.get_node_name_list().index(node_name)
        self.dataList[node_number][node_name][profess_id]= {}

    def set_profiles(self, load_profiles=None, pv_profiles=None, price_profiles=None, ess_con=None):
        logger.debug("setting_profiles ")
        """logger.debug(load_profiles)
        logger.debug(pv_profiles)
        logger.debug(price_profiles)
        logger.debug(ess_con)"""
        node_name_list =self.json_parser.get_node_name_list()
        for nodeName in node_name_list:

            node_number = node_name_list.index(nodeName)
            if load_profiles is not None:
                #logger.debug("load profile set")
                for element in load_profiles:
                    if nodeName in element:
                        profess_id = self.get_profess_id(nodeName)
                        json_data_of_node = self.dataList[node_number][nodeName][profess_id]
                        phase = element[nodeName]
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
                        if nodeName + ".1.2.3" or nodeName in phase:
                            if nodeName in phase:
                                json_data_of_node["load"]["P_Load"] = phase[nodeName]
                                for_list = phase[nodeName]
                            if nodeName + ".1.2.3" in phase:
                                json_data_of_node["load"]["P_Load"] = phase[nodeName + ".1.2.3"]
                                for_list = phase[nodeName + ".1.2.3"]
                            single_phase = []
                            for value in for_list:
                                value = value / 3
                                single_phase.append(value)
                            json_data_of_node["load"]["P_Load_R"] = copy.deepcopy(single_phase)
                            json_data_of_node["load"]["P_Load_S"] = copy.deepcopy(single_phase)
                            json_data_of_node["load"]["P_Load_T"] = copy.deepcopy(single_phase)
            else: logger.debug("no load profile was given")
            if pv_profiles is not None:
                for element in pv_profiles:
                    profess_id = self.get_profess_id(nodeName)
                    json_data_of_node = self.dataList[node_number][nodeName][profess_id]
                    if nodeName in element:
                        phase = element[nodeName]
                        #logger.debug("pv_profile match found")
                        if nodeName + ".1.2.3" or nodeName in phase:
                            if nodeName in phase:
                                json_data_of_node["photovoltaic"]["P_PV"]= phase[nodeName]
                                for_list=phase[nodeName]
                            if nodeName + ".1.2.3" in phase:
                                json_data_of_node["photovoltaic"]["P_PV"] = phase[nodeName + ".1.2.3"]
                                for_list=phase[nodeName + ".1.2.3"]
                            single_phase = []
                            for value in for_list:
                                value = value / 3
                                single_phase.append(value)
                            json_data_of_node["photovoltaic"]["P_PV_R"] = copy.deepcopy(single_phase)
                            json_data_of_node["photovoltaic"]["P_PV_S"] = copy.deepcopy(single_phase)
                            json_data_of_node["photovoltaic"]["P_PV_T"] = copy.deepcopy(single_phase)
                            #logger.debug("pv profile set")
            else: logger.debug("no pv_profile was given")
            if ess_con is not None:
                for element in ess_con:
                    profess_id = self.get_profess_id(nodeName)
                    json_data_of_node = self.dataList[node_number][nodeName][profess_id]
                    if nodeName in element:
                        phase = element[nodeName]
                        if nodeName + ".1.2.3" in phase:
                            json_data_of_node["generic"]["ESS_Control"] = phase[nodeName + ".1.2.3"]
                            #logger.debug("ess_con profile set")
                        if nodeName in phase:
                            json_data_of_node["generic"]["ESS_Control"] = phase[nodeName]
                            #logger.debug("ess_con profile set")
            profess_id = self.get_profess_id(nodeName)
            json_data_of_node = self.dataList[node_number][nodeName][profess_id]
            if price_profiles is not None:
                json_data_of_node["generic"]["Price_Forecast"] = price_profiles #No reserved words for price
                #logger.debug("price profile set")

    def get_profess_id(self, nodeName):
        node_number = self.json_parser.get_node_name_list().index(nodeName)

        for element in self.dataList[node_number][nodeName]:
            profess_id = element
        return profess_id
    def get_node_name(self, profess_id):
        nodeName=""
        name_list = self.json_parser.get_node_name_list()
        for name in name_list:
            node_number = name_list.index(name)
            for element in self.dataList[node_number][name]:
                if element==profess_id:
                    nodeName= name

        return nodeName
    def set_data_list(self):
        #logger.debug("data for nodes is set")
        node_list = self.json_parser.get_node_element_list()
        logger.debug("node element list "+str(node_list))
        for element in range(len(node_list)):
            for nodeKey in (node_list[element]):
                node_list[element] = {nodeKey: {}}
        self.dataList = node_list


    def set_up_profess(self,soc_list=None, load_profiles=None, pv_profiles=None, price_profiles=None, ess_con=None):
        logger.debug("set_up_profess started")
        if self.dataList == []:
            self.set_data_list()
            self.post_all_dummy_data()
        #TODO
        if soc_list is not None:
            if type(soc_list) is dict:
                self.json_parser.set_topology(soc_list)
        self.set_profiles(load_profiles=load_profiles, pv_profiles=pv_profiles, price_profiles=price_profiles
                          ,ess_con=ess_con)
        node_name_list = self.json_parser.get_node_name_list()
        for nodeName in node_name_list:
            self.set_storage(nodeName)
            self.set_photovoltaics(nodeName)
            professID=self.get_profess_id(nodeName)
            nodeNumber = node_name_list.index(nodeName)
            self.update_config_json(professID, self.dataList[nodeNumber][nodeName][professID])
        elements = self.json_parser.get_node_element_list()
        if soc_list is not None:
            if type(soc_list) is list:
                for nodeKey in elements:
                    for node_name in nodeKey:
                        index = elements.index(nodeKey)
                        profess_id = self.get_profess_id(node_name)
                        if soc_list is not None:
                            for value in soc_list:
                                if node_name in value:
                                    soc_index = soc_list.index(value)
                                    self.dataList[index][node_name][profess_id]["ESS"]["SoC_Value"] = (
                                            soc_list[soc_index][node_name]["SoC"] / 100)
                        self.update_config_json(profess_id, self.dataList[index][node_name][profess_id])

    def translate_output(self, output_data):
        logger.debug("output of ofw is being translated to se ")
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



