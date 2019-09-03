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
        """

        :param domain: domain where the ofw is reached
        :param topology: grid topology which is used for the optimization
        """
        self.domain = domain #domainName is different on operating systems
        self.dataList=[]    #list where all config data of nodes are saved
        self.httpClass = Http_commands()
        self.json_parser=JsonParser(topology)
        # mapping from topology to ofw input
        # syntax: topology_value : ofw_value for direct mapping
        # syntax: topology_value : [ofw_value1, ofw_value2] for mapping of one topology value to multiple ofw values
        # syntax: topology_value : {"meta": ofwvalue} for mapping of meta parameters
        self.storage_mapping={"soc": "SoC_Value", "charge_efficiency":{"meta":"ESS_Charging_Eff"},"discharge_efficiency"
        :{"meta":"ESS_Discharging_Eff"},"kw_rated":[{"meta":"ESS_Max_Charge_Power"},{"meta":"ESS_Max_Discharge_Power"}],
                              "kwh_rated":{"meta":"ESS_Capacity"},"max_charging_power":{"meta":"ESS_Max_Charge_Power"},
                              "max_discharging_power":{"meta":"ESS_Max_Discharge_Power"},
                              "storage_capacity":{"meta":"ESS_Capacity"},"min_soc":{"meta":"ESS_Min_SoC"},"max_soc":
                                  {"meta":"ESS_Max_SoC"}}
        # list of all topology values which are in percent, but need to be mapped to a value between 1.0 and 0.0
        self.percentage_mapping=["charge_efficiency","soc","discharge_efficiency","min_soc","max_soc"]
        #pv mapping has the same syntax as storage_mapping
        self.pv_mapping={"max_power_kW":{"meta":"PV_Inv_Max_Power"}}
        #a dict with standard values for the ofw
        self.standard_data = {"load": {
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
        self.list_with_desired_output_parameters=["P_ESS_Output", "P_PV_Output", "P_PV_R_Output", "P_PV_S_Output"
            , "P_PV_T_Output", "Q_PV_Output", "Q_PV_R_Output", "Q_PV_S_Output", "Q_PV_T_Output"]

        logger.debug("Profess instance created")

    def post_model(self, model_name, model_data):
        """
        post the model to the ofw
        :param model_name: name of posted model
        :param model_data:  optimization model see @linksmartOptimizationFramework for definition
        :return: returns 0 when successful, 1 when not successful
        """
        response=""
        try:
            response=self.httpClass.put(self.domain + "models/" + model_name, model_data)
            json_response = response.json()
            logger.debug("postmodel started " + str(model_name) + " ,response of ofw: " + str(json_response))
            if response.status_code == 200:
                logger.debug("model post completed: " + str(model_name))
                return 0
            else:
                logger.error("failed to post model: " + str(model_name))
                return 1
        except:
            logger.error("Failed to post model, No connection to the OFW could be established at :"+str(self.domain)+"models/")
            return 1
    def post_data(self, input_data, node_name):
        """
        posts the ofw input data on bus: node_name, and saves the profess_id of the submitted data together with the
        submitted data
        :param input_data: input for ofw: {"load":{"meta":{...},...},{"ESS":{"meta:{...}, ...}, {"grid":{"meta":{...}},
        {"photovoltaic":{ "meta":{...}, ...}, "generic":{..}}
        which information is needed depends on the used optimization_model for the optimization
        :param node_name: name of bus
        :return: returns 0 when successful, 1 when not successful
        """
        logger.debug("Profess: post data started " + str(node_name))
        response=""
        try:
            response = self.httpClass.post(self.domain + "inputs/dataset", input_data, "json")
            json_response = response.json()
            # regex to get profess_id
            pattern = re.compile("/inputs*[/]([^']*)")
            m = pattern.findall(str(response.headers))
            if m != "":
                profess_id = m[0]
            else:
                logger.error("failed to post data to the ofw, no professID was returned " + str(node_name))
            logger.debug("Response of OFW after post data: " + str(json_response) + ": " + str(profess_id)+ " , statusCode: "+str(response.json()))
            # the professId is saved for futher referencing
            self.set_profess_id_for_node(node_name, profess_id)
            # the posted data is also saved internaly for other optimizations
            self.set_config_json(node_name, profess_id, input_data)
            if response.status_code == 200:
                return 0
            else:
                logger.error("failed to post_data node: " + str(node_name) + " and input data: " + str(
                    input_data) + "Response Code: "+str(response.status_code)+",  Response from the OFW: " + str(response.json()))
                return 1
        except:
            logger.error("Failed to post data, No connection to the OFW could be established at :"+str(self.domain)+"/inputs/dataset")
            return 1


    def post_all_standard_data(self):
        """
        posts standard_data to the ofw for every relevant bus (nodes with ESS)
        :return: returns 0 when successful, 1 when not successful
        """
        node_element_list = self.json_parser.get_node_element_list()
        all_successful=True
        for node_element in node_element_list:
            for node_name in node_element:
                if self.post_data((self.standard_data), node_name):

                    all_successful=False
        if all_successful:
            return 0
        else:
            logger.error("failed to post_all_standard_data ")
            return 1


    def set_standard_data(self, standard_data):
        """
        function to change standard values
        :param standard_data: dict with new standard values, syntax:
        {"load":{"meta":{...},...},{"ESS":{"meta:{...}, ...}, {"grid":{"meta":{...}},
        {"photovoltaic":{ "meta":{...}, ...}, "generic":{..}}
        :return:
        """
        self.standard_data=standard_data
    def get_optimization_status(self):
        """
        :return: dict with the optimization_status of all optimizations
        syntax of returned dict: {"status":{profess_id1:{"config":{'control_frequency': int, 'dT_in_seconds':int,
         'horizon_in_steps':int,
         'model_name':model_name,
         'optimization_type':opt_type,
         'repetition':int,
         'single_ev':boolean,
         'solver':solver_name},
         "start_time:time_value,
         "status":status_type},{profess_id2:...}}
        """
        try:
            response = self.httpClass.get(self.domain + "optimization/status")
            json_response = response.json()
            if response.status_code == 200:


                return json_response
            else:
                logger.error("Failed to get_optimization_status, response from ofw:" + str(json_response))
                return 1
        except:
            logger.error("Failed to get optimization status, No connection to the OFW could be established at :"+str(self.domain)+"optimization/status")

    def get_output(self, profess_id):
        """
        :param profess_id: id which optimization should return the output
        :return: returns the optimization output:
        {
        ofw_variable: {time_value1:variable_value1, ...},{ofw_variable2 : {time_value1:variable_value, ...}
        }
        if it failed, 1 is returned
        """
        try:
            response = self.httpClass.get(self.domain + "outputs/" + profess_id)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("failed to get output from professID: " + str(profess_id) + " response from ofw: " + str(
                    response.json()))
                return 1
        except:
            logger.error("Failed to get optimization output, No connection to the OFW could be established at :"+str(self.domain)+"outputs/")
            return 1

    def is_running(self):
        """
        :return: Returns if a optimization on a node is still running, true if on a node runs an optimization,
        otherwise false
        """
        #busy waiting
        time.sleep(5)
        opt_status = self.get_optimization_status()
        #logger.debug("optimization status: " + str(opt_status))
        running_flag=False
        node_name_list=self.json_parser.get_node_name_list()
        for node_name in node_name_list:
            profess_id=self.get_profess_id(node_name)
            if profess_id !=0:
                if profess_id in opt_status["status"]:
                    if opt_status["status"][profess_id]["status"] == "running":
                        logger.debug("An optimization is still running: " + str(profess_id))
                        running_flag=True
                else:
                    logger.error("Failed to check if "+str(profess_id)+ " is still running, not found in optimization status")
            else:
                logger.error("Check connection to the OFW, we try to check a non existing profess_id: "+str(profess_id))
        if running_flag: return True
        else: return False

    def wait_and_get_output(self):
        """
        :return: returns a list with the translated ouputs of all nodes see (@translate_output)
        """
        logger.debug("wait for OFW output")
        node_name_list = self.json_parser.get_node_name_list()
        if node_name_list!=0:
            while self.is_running():
                pass
            output_list=[]

            for node_name in node_name_list:
                profess_id=self.get_profess_id(node_name)
                if profess_id != 0:
                    output_list.append({profess_id: self.get_output(profess_id)})
            logger.debug("OFW finished, all optimizations stopped")
            translated_output = self.translate_output(output_list)
            return translated_output
        else:return []
    def start(self, freq, horizon, dt, model, repition, solver, optType, profess_id):
        """
        starts an optimization of profess_id on the ofw
        for first 6 params see Linksmart OFW API Doc
        :param freq: Frequency for ofw, for example: 1
        :param horizon: time horizon, for example 24
        :param dt: seconds in a horizon step: for example 3600 are an hour
        :param model: used model, string of a model in the ofw, for example "MaximizePVNoLoad"
        :param repition: times ofw does repition, -1 is infinite
        :param solver: which solver is used, name of the solver, for example: "ipopt" , "glpk" or "bonmin"
        :param optType: optimization type, for example : "discrete", "stochastic", "MPC"
        :param profess_id: profess_id which optimization should be started
        :return: 0 when successfull, response why it failed when not successfull
        """
        logger.debug("start "+str(profess_id))
        try:
            response = self.httpClass.put(self.domain + "optimization/start/" + profess_id, {"control_frequency": freq,
                                                                                             "horizon_in_steps": horizon,
                                                                                             "dT_in_seconds": dt,
                                                                                             "model_name": model,
                                                                                             "repetition": repition,
                                                                                             "solver": solver,
                                                                                             "optimization_type": optType})
            json_response = response.json()
            logger.debug(str(json_response) + ": " + str(profess_id)+" , Status code of start: "+str(response.status_code))
            if response.status_code == 200 and json_response == "System started succesfully":
                # code 200 is returned even when the optimization couldn't start because of missing data for the optimization
                return 0
            else:

                return response
        except:
            logger.error("Failed to start optimization, No connection to the OFW could be established at :"+str(self.domain)+"optimization/start/")




    def start_all(self, optimization_model=None):
        """
        starts all optimizations on the relevant nodes (nodes with ESS)
        :param optimization_model: optional optimization_model, when no model is given the models in the ESS definition
        are used, see topology
        :return: returns 0 when successful, else 1
        """
        logger.debug("All optimizations are being started.")
        node_name_list =self.json_parser.get_node_name_list()
        if node_name_list !=0:

            for node_name in node_name_list:
                #search for list with all elemens that are connected to bus: node_name
                element_node=(next(item for item in self.json_parser.get_node_element_list() if node_name in item))
                for node_element in element_node[node_name]:
                    if "storageUnits" in node_element:
                        storage = node_element
                        storage_opt_model = storage["storageUnits"]["optimization_model"]
                if optimization_model is None:
                    optimization_model = storage_opt_model
                start_response=self.start(1, 24, 3600, optimization_model, 1, "ipopt", "discrete", self.get_profess_id(node_name))
                if start_response:
                    self.check_start_issue(start_response,node_name)
                    return 1
            return 0
        else:return 0
    def check_start_issue(self,response,node_name):
        """
        parses the response a failed optimization start returns, and  logs why it might have failed
        :param response: ofw response of failed start
        :param node_name: node name where start failed
        :return:
        """
        json_response=response.json()
        if "Data source for following keys not declared:" in json_response:
            logger.error("Missing data for optimization model, couldn't start")
            pattern = re.compile("'(.*?)'")  # regex to find which parameters where missing
            missing_parameters = pattern.findall(str(json_response))
            for parameter in missing_parameters:
                if "PV" in parameter:
                    node_element_list=self.json_parser.get_node_element_list()
                    for bus_element in node_element_list:
                        if node_name in bus_element:
                            pv_flag=False
                            storage_info=""
                            pv_info=""
                            for node_element in bus_element[node_name]:
                                if "photovoltaic" in node_element:
                                    pv_flag = True
                                    pv_info=node_element
                                if "storageUnits" in node_element:
                                    storage_info=node_element
                            if pv_flag:
                                logger.error("PV Information is missing but PV is connected at :"+str(node_name)+ " , connected storage: "+ str(storage_info)+ " , connected pv: "+ str(pv_info))
                            else:
                                logger.error(str(parameter)+" is needed for the optimization, but no pv was connected to :" + str(node_name)+ " , connected storage: "+ str(storage_info))
        else:

            logger.error("start failed, but no data keys where missing, reason it failed: "+str(json_response)+" response status code: "+str(response.status_code))
    def stop(self, profess_id):
        """
        stops the optimization with id: profess_id in the ofw
        :param profess_id: which optimization should be stopped
        :return: 0 when successful, else 1
        """
        logger.debug("Stop optimization: "+str(profess_id))
        if profess_id != 0:
            response = self.httpClass.put(self.domain + "optimization/stop/" + profess_id)
            json_response = response.json()
            logger.debug(json_response+" :"+str(profess_id))
            if response.status_code==200: return 0
            else: return 1
        else:
            logger.error("No Input to stop declared")
            return 1
    def update_config_json(self, profess_id, config_json):
        """
        updates the input data for the optimization in the ofw
        :param profess_id: id which optimization is changed
        :param config_json: new input data for ofw, syntax: {"load":{"meta":{...},...},{"ESS":{"meta:{...}, ...}, {"grid":{"meta":{...}},
        {"photovoltaic":{ "meta":{...}, ...}, "generic":{..}}
        :return: 0 when successful, else 1
        """
        logger.debug("update_config_json has started at "+ str(profess_id))
        if profess_id != 0:
            response = self.httpClass.put(self.domain + "inputs/dataset/" + profess_id, config_json)
            json_response = response.json()
            logger.debug("Response from OFW to update_config :"+str(json_response)+ ": "+str(profess_id))
            if response.status_code==200: return 0
            else: return 1
        else: return 1
    def set_storage(self, node_name):
        """
        sets all storage related values of the local config of node_name
        :param node_name: name of the bus
        :return:
        """
        logger.debug("set_storage config data of "+ str(node_name))
        node_number = self.json_parser.get_node_name_list().index(node_name)
        profess_id=self.get_profess_id(node_name)
        if profess_id != 0:
            config_data_of_node = self.dataList[node_number][node_name][profess_id]
            for radial_number in range(len(self.json_parser.topology["radials"])):
                node_element_list = self.json_parser.get_node_element_list()[node_number][node_name]
                storage_index = 0
                for node_element in node_element_list:
                    if "storageUnits" in node_element:
                        #searche for the index where the storage is
                        storage_index = node_element_list.index(node_element)
                if "storageUnits" in node_element_list[storage_index].keys():
                    for storage_key in self.storage_mapping:
                        if storage_key in node_element_list[storage_index]["storageUnits"]:
                            if storage_key in self.percentage_mapping:
                                percentage = 100
                            else: percentage = 1
                            if type(self.storage_mapping[storage_key]) == dict:
                                #this means the key is mapped to meta data
                                config_data_of_node["ESS"]["meta"][self.storage_mapping[storage_key]["meta"]] = \
                                    node_element_list[storage_index]["storageUnits"][storage_key] / percentage
                            if type(self.storage_mapping[storage_key]) == list:
                                #this means a value in the storageunit is mapped to multiple values in the ofw
                                for part in self.storage_mapping[storage_key]:
                                    if "meta" in part:
                                        config_data_of_node["ESS"]["meta"][part["meta"]] = node_element_list[storage_index]
                                        ["storageUnits"][storage_key] / percentage
                                    else:
                                        config_data_of_node["ESS"][part] = node_element_list[storage_index]["storageUnits"][
                                                                             storage_key] / percentage
                            if type(self.storage_mapping[storage_key]) == str:
                                #the key can be directly mapped
                                config_data_of_node["ESS"][self.storage_mapping[storage_key]] = \
                                    node_element_list[storage_index]["storageUnits"][storage_key] / percentage


    def set_photovoltaics(self,node_name):
        """
        set all the photovoltaics related values of the local config of node_name
        :param node_name: the name of the bus
        :return:
        """
        logger.debug("set photovoltaics config data of "+ str(node_name))
        node_number = self.json_parser.get_node_name_list().index(node_name)
        for profess_id in self.dataList[node_number][node_name]:
            config_data_of_node= self.dataList[node_number][node_name][profess_id]
            for radial_number in range(len(self.json_parser.topology["radials"])):
                node_element_list=self.json_parser.get_node_element_list()[node_number][node_name]
                pv_index=0
                for node_element in node_element_list:
                    if "photovoltaics" in node_element:
                        #searches for the index where the pv is
                        pv_index=node_element_list.index(node_element)
                if "photovoltaics" in node_element_list[pv_index]:

                    for pv_key in self.pv_mapping:
                        if pv_key in node_element_list[pv_index]["photovoltaics"]:
                            if pv_key in self.percentage_mapping:
                                percentage=100
                            else: percentage = 1
                            if type(self.pv_mapping[pv_key]) == str:
                                #can be directly mapped
                                config_data_of_node["photovoltaic"][self.pv_mapping[pv_key]] = node_element_list[pv_index]["photovoltaics"][pv_key]/percentage
                            if type(self.pv_mapping[pv_key]) == dict:
                                #this means the key is mapped to meta data
                                config_data_of_node["photovoltaic"]["meta"][self.pv_mapping[pv_key]["meta"]] = node_element_list[pv_index]["photovoltaics"][pv_key]/percentage

    def set_config_json(self, node_name, profess_id, config_json):
        """
        sets the config data in profess of the node node_name
        :param node_name: name of the bus
        :param profess_id: id of the optimization
        :param config_json: new config data, syntac:
        {"load":{"meta":{...},...},{"ESS":{"meta:{...}, ...}, {"grid":{"meta":{...}},
        {"photovoltaic":{ "meta":{...}, ...}, "generic":{..}}
        :return:
        """
        logger.debug("set_config_json at "+str(node_name)+" ,"+str(profess_id)+"  with config: "+str(config_json))
        if profess_id!=0:
            node_number = self.json_parser.get_node_name_list().index(node_name)
            self.dataList[node_number][node_name][profess_id] = copy.deepcopy(config_json)

    def set_profess_id_for_node(self, node_name, new_profess_id):
        """
        saves the profess_id of an optimization in the config of node_name
        :param node_name: name of the bus
        :param new_profess_id: which profess_id should be set
        :return:
        """
        logger.debug("set_profess_id_for_node " + str(node_name) +" ," + str(new_profess_id))
        if new_profess_id!=0:
            node_number = self.json_parser.get_node_name_list().index(node_name)
            self.dataList[node_number][node_name][new_profess_id]= {}
        else: logger.error("a wrong profess_id was set for node: "+str(node_name)+ " , profess_id: " +str(new_profess_id))
    def set_profiles(self, load_profiles=None, pv_profiles=None, price_profiles=None, ess_con=None):
        """
        sets the profiles for all configs of all relevant nodes(nodes with ESS)

        :param load_profiles: [{node_name1:{node_name1.1[value1, value2,...],node_name1.2[value1, value2,...]}
        {node_name2:{node_name2.1.2.3[value1, value2,...]}, {node_name3:{node_name3[value1, value2,...]}, ...]
        the load profile can be given for each phase individually they have to be named: node_name.phase,
        or one profile for all three phases can be given by naming it: node_name.1.2.3 or just node_name

        :param pv_profiles: [{node_name:{node_name:[value1,value2,...]}}, ...]
        :param price_profiles: [value1, value2, value3, ....] is the price profile for the whole grid
        :param ess_con: [{node_name:{node_name.1.2.3:[value1,value2, ...]}, ...}
        """
        logger.debug("Setting_profiles ")
        #logger.debug("load profile: "+str(load_profiles)+" ,pv_profiles: "+str(pv_profiles)+" ,price_profile: "+str(price_profiles)+" ,ess_con "+str(ess_con))
        node_name_list =self.json_parser.get_node_name_list()
        if node_name_list !=0:
            for node_name in node_name_list:
                node_number = node_name_list.index(node_name)
                if load_profiles is not None:
                    #logger.debug("load profile set")
                    for load_profile_for_node in load_profiles:
                        if node_name in load_profile_for_node:
                            profess_id = self.get_profess_id(node_name)
                            if profess_id!= 0:
                                config_data_of_node = self.dataList[node_number][node_name][profess_id]
                                phase = load_profile_for_node[node_name]
                                r_flag=False
                                s_flag=False
                                t_flag=False
                                #checks which phases are used
                                if node_name + ".1" in phase:
                                    config_data_of_node["load"]["P_Load_R"] = phase[node_name + ".1"]
                                    r_flag=True
                                if node_name + ".2" in phase:
                                    config_data_of_node["load"]["P_Load_S"] = phase[node_name + ".2"]
                                    s_flag=True
                                if node_name + ".3" in phase:
                                    config_data_of_node["load"]["P_Load_T"] = phase[node_name + ".3"]
                                    t_flag=True
                                length = 0
                                if r_flag:
                                    length = len(config_data_of_node["load"]["P_Load_R"])
                                if s_flag:
                                    length = len(config_data_of_node["load"]["P_Load_S"])
                                if t_flag:
                                    length = len(config_data_of_node["load"]["P_Load_T"])
                                if not r_flag:
                                    config_data_of_node["load"]["P_Load_R"] = [0] * length
                                if not s_flag:
                                    config_data_of_node["load"]["P_Load_S"] = [0] * length
                                if not t_flag:
                                    config_data_of_node["load"]["P_Load_T"] = [0] * length

                                if ("P_Load_R" in config_data_of_node["load"]) and ("P_Load_S" in config_data_of_node["load"]) and \
                                        ("P_Load_T" in config_data_of_node["load"]):
                                    logger.debug("p_load_r :" + str(
                                        config_data_of_node["load"]["P_Load_R"]) + " ,p_load_s :" + str(
                                        config_data_of_node["load"]["P_Load_S"]) + " ,p_load_t :" + str(
                                        config_data_of_node["load"]["P_Load_T"]))

                                    three_phase = []
                                    for value in range(len(config_data_of_node["load"]["P_Load_T"])):
                                        three_phase_value = config_data_of_node["load"]["P_Load_R"][value] + \
                                                            config_data_of_node["load"]["P_Load_S"][value] + \
                                                            config_data_of_node["load"]["P_Load_T"][value]
                                        three_phase.append(three_phase_value)
                                    config_data_of_node["load"]["P_Load"] = three_phase
                                else:
                                    three_phase = [0] * length
                                    for value in range(length):

                                        three_phase_value = config_data_of_node["load"]["P_Load_R"][value] + \
                                                            config_data_of_node["load"]["P_Load_S"][value] + \
                                                            config_data_of_node["load"]["P_Load_T"][value]

                                        three_phase.append(three_phase_value)
                                    config_data_of_node["load"]["P_Load"] = three_phase

                                if node_name + ".1.2.3" in phase or node_name == phase:
                                    three_phase=[]
                                    if node_name in phase:
                                        config_data_of_node["load"]["P_Load"] = phase[node_name]
                                        three_phase = phase[node_name]
                                    if node_name + ".1.2.3" in phase:
                                        config_data_of_node["load"]["P_Load"] = phase[node_name + ".1.2.3"]
                                        three_phase = phase[node_name + ".1.2.3"]
                                    single_phase = []
                                    for value in three_phase:
                                        value = value / 3
                                        single_phase.append(value)
                                    config_data_of_node["load"]["P_Load_R"] = copy.deepcopy(single_phase)
                                    config_data_of_node["load"]["P_Load_S"] = copy.deepcopy(single_phase)
                                    config_data_of_node["load"]["P_Load_T"] = copy.deepcopy(single_phase)
                                logger.debug("load profile set for "+str(node_name))
                else: logger.debug("no load profile was given")
                if pv_profiles is not None:
                    for pv_profiles_for_node in pv_profiles:
                        profess_id = self.get_profess_id(node_name)
                        if profess_id != 0:
                            config_data_of_node = self.dataList[node_number][node_name][profess_id]
                            if node_name in pv_profiles_for_node:
                                phase = pv_profiles_for_node[node_name]
                                if node_name + ".1.2.3" or node_name in phase:
                                    if node_name in phase:
                                        config_data_of_node["photovoltaic"]["P_PV"]= phase[node_name]
                                        three_phase=phase[node_name]
                                    if node_name + ".1.2.3" in phase:
                                        config_data_of_node["photovoltaic"]["P_PV"] = phase[node_name + ".1.2.3"]
                                        three_phase=phase[node_name + ".1.2.3"]
                                    single_phase = []
                                    for value in three_phase:
                                        value = value / 3
                                        single_phase.append(value)
                                    config_data_of_node["photovoltaic"]["P_PV_R"] = copy.deepcopy(single_phase)
                                    config_data_of_node["photovoltaic"]["P_PV_S"] = copy.deepcopy(single_phase)
                                    config_data_of_node["photovoltaic"]["P_PV_T"] = copy.deepcopy(single_phase)
                                    logger.debug("pv profile set for "+ str(node_name))
                else: logger.debug("no pv_profile was given")
                if ess_con is not None:
                    for ess_con_global in ess_con:
                        profess_id = self.get_profess_id(node_name)
                        if profess_id != 0:
                            config_data_of_node = self.dataList[node_number][node_name][profess_id]
                            if node_name in ess_con_global:
                                phase = pv_profiles_for_node[node_name]
                                if node_name + ".1.2.3" in phase:
                                    config_data_of_node["generic"]["ESS_Control"] = phase[node_name + ".1.2.3"]
                                    #logger.debug("ess_con profile set")
                                if node_name in phase:
                                    config_data_of_node["generic"]["ESS_Control"] = phase[node_name]
                                logger.debug("ess_con profile set")
                profess_id = self.get_profess_id(node_name)
                if profess_id != 0:
                    config_data_of_node = self.dataList[node_number][node_name][profess_id]
                    if price_profiles is not None:
                        config_data_of_node["generic"]["Price_Forecast"] = price_profiles #No reserved words for price
                        #logger.debug("price profile set")

    def get_profess_id(self, node_name):
        """
        :param node_name: bus name
        :return: profess_id which is the optimization id of the optimization on node_name
        """
        node_number = self.json_parser.get_node_name_list().index(node_name)
        profess_id =0
        for element in self.dataList[node_number][node_name]:
            profess_id = element
        return profess_id
    def get_node_name(self, profess_id):
        """
        :param profess_id:
        :return: bus name for profess_id
        """
        node_name=""
        name_list = self.json_parser.get_node_name_list()
        for name in name_list:
            node_number = name_list.index(name)
            for element in self.dataList[node_number][name]:
                if element==profess_id:
                    node_name= name
        if node_name=="":
            logger.error("there is no node which has the profess_id: "+profess_id)
        return node_name
    def set_data_list(self):
        """
        sets up data_list with a list of dictonaries to, with the relevant nodes(nodes with ESS):
        [{node_name1:{},{node_name2:{},...]

        :return:
        """
        #logger.debug("data for nodes is set")
        node_element_list = self.json_parser.get_node_element_list()
        logger.debug("node element list "+str(node_element_list))
        for index in range(len(node_element_list)):
            for node_name in (node_element_list[index]):
                node_element_list[index] = {node_name: {}}
        self.dataList = node_element_list


    def set_up_profess(self,soc_list=None, load_profiles=None, pv_profiles=None, price_profiles=None, ess_con=None):
        """
        sets all important information retrieved from the parameters and topology
        :param soc_list: syntax when a list: [{node_name1:{"SoC":value, "id": id_name},{node_name2:{...},...] value is
        between 0 and 100  syntax when a dict: it is the new topology for the grid, see definition of topology

        :param load_profiles: [{node_name1:{node_name1.1[value1, value2,...],node_name1.2[value1, value2,...]}
        {node_name2:{node_name2.1.2.3[value1, value2,...]}, {node_name3:{node_name3[value1, value2,...]}, ...]
        the load profile can be given for each phase individually they have to be named: node_name.phase,
        or one profile for all three phases can be given by naming it: node_name.1.2.3 or just node_name

        :param pv_profiles: [{node_name:{node_name:[value1,value2,...]}}, ...]
        :param price_profiles: [value1, value2, value3, ....] is the price profile for the whole grid
        :param ess_con: [{node_name:{node_name.1.2.3:[value1,value2, ...]}, ...}
        :return:
        """
        logger.debug("set_up_profess started")
        #logger.debug("soc_list "+ str(soc_list))
        #logger.debug("load_profiles "+ str(load_profiles))
        #logger.debug("pv_profiles "+ str(pv_profiles))
        #logger.debug("price_profiles "+ str(price_profiles))
        #logger.debug("ess_con " + str(ess_con))
        if self.dataList == []:
            #this happends just for the first set_up
            self.set_data_list()
            self.post_all_standard_data()
        if soc_list is not None:
            if type(soc_list) is dict:
                self.json_parser.set_topology(soc_list)
        self.set_profiles(load_profiles=load_profiles, pv_profiles=pv_profiles, price_profiles=price_profiles
                          ,ess_con=ess_con)
        node_name_list = self.json_parser.get_node_name_list()
        if node_name_list!=0:
            for nodeName in node_name_list:
                self.set_storage(nodeName)
                self.set_photovoltaics(nodeName)
                profess_id=self.get_profess_id(nodeName)
                if profess_id !=0:
                    node_index = node_name_list.index(nodeName)
                    self.update_config_json(profess_id, self.dataList[node_index][nodeName][profess_id])
            node_element_list = self.json_parser.get_node_element_list()
            if soc_list is not None:
                if type(soc_list) is list:
                    for node_element in node_element_list:
                        for node_name in node_element:
                            index = node_element_list.index(node_element)
                            profess_id = self.get_profess_id(node_name)
                            if profess_id != 0:
                                for node_soc in soc_list:
                                    if node_name in node_soc:
                                        soc_index = soc_list.index(node_soc)
                                        self.dataList[index][node_name][profess_id]["ESS"]["SoC_Value"] = (
                                                soc_list[soc_index][node_name]["SoC"] / 100)
                                self.update_config_json(profess_id, self.dataList[index][node_name][profess_id])

    def translate_output(self, output_data):
        """
        translates the ouptut data from whole time horizon to next hour, and also just returns wanted values
        :param output_data: data which has to be translated
        :return: translated output, syntax: [{node_name:{ profess_id:{ variable1: value1, variable2:value2, ...]}, ...]
        """
        logger.debug("output of ofw is being translated to se ")
        output_list=copy.deepcopy(output_data)
        #finding the lowest value of each variable and delete all not needed timesteps
        for parameter_output_list in output_data:
            for node_name in parameter_output_list:
                for profess_id in parameter_output_list[node_name]:
                    sorted_output = dict(sorted(parameter_output_list[node_name][profess_id].items()))
                    index=output_data.index(parameter_output_list)
                    output_list[index][node_name][profess_id] = parameter_output_list[node_name][profess_id][min(sorted_output)]

        #sets the right format node_name:{profess_id:{data}}
        for config in self.dataList:
            for node_name in config:
                for output_for_node in output_list:
                    for profess_id in output_for_node:
                        if profess_id in config[node_name]:
                            index=output_list.index(output_for_node)
                            output_list[index]={node_name:output_list[index]}
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
        sorted_output=copy.deepcopy(output_list)

        for output_for_node in sorted_output:
            for node_name in output_for_node:
                for profess_id in output_for_node[node_name]:
                    for values_output_for_node in output_for_node[node_name][profess_id]:
                        #delete undisired parameters
                        if not values_output_for_node in self.list_with_desired_output_parameters:
                            index=sorted_output.index(output_for_node)
                            output_list[index][node_name][profess_id].pop(values_output_for_node, None)
        return output_list



