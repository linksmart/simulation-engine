from profess.Http_commands import Http_commands
import re
import copy
from profess.JSONparser import *
import simplejson as json
import time
import logging
from data_management.redisDB import RedisDB

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class Profess:
    def __init__(self,id, domain, topology):
        """

        :param domain: domain where the ofw is reached
        :param topology: grid topology which is used for the optimization
        """
        self.domain = domain  # domainName is different on operating systems
        self.dataList = []  # list where all config data of nodes are saved
        self.httpClass = Http_commands()
        self.json_parser = JsonParser(topology)
        self.redisDB = RedisDB()
        self.finish_status_key = "finish_status_" + id
        # mapping from topology to ofw input
        # syntax: topology_value : ofw_value for direct mapping
        # syntax: topology_value : [ofw_value1, ofw_value2] for mapping of one topology value to multiple ofw values
        # syntax: topology_value : {"meta": ofwvalue} for mapping of meta parameters
        self.storage_mapping = {"soc": "SoC_Value", "charge_efficiency": {"meta": "ESS_Charging_Eff"},
                                "discharge_efficiency"
                                : {"meta": "ESS_Discharging_Eff"},
                                "kw_rated": [{"meta": "ESS_Max_Charge_Power"}, {"meta": "ESS_Max_Discharge_Power"}],
                                "kwh_rated": {"meta": "ESS_Capacity"},
                                "max_charging_power": {"meta": "ESS_Max_Charge_Power"},
                                "max_discharging_power": {"meta": "ESS_Max_Discharge_Power"},
                                "storage_capacity": {"meta": "ESS_Capacity"}, "min_soc": {"meta": "ESS_Min_SoC"},
                                "max_soc":
                                    {"meta": "ESS_Max_SoC"}, "SoC": "SoC_Value",
                                "Battery_Capacitiy": {"meta": "ESS_Capacity"}}
        # list of all topology values which are in percent, but need to be mapped to a value between 1.0 and 0.0
        self.percentage_mapping = ["charge_efficiency", "discharge_efficiency", "min_soc", "max_soc"]
        # pv mapping has the same syntax as storage_mapping
        self.pv_mapping = {"max_power_kW": {"meta": "PV_Inv_Max_Power"}}
        # informations about the grid have to be at the pv
        self.grid_mapping = {"Q_Grid_Max_Export_Power": {"meta": "Q_Grid_Max_Export_Power"},
                             "P_Grid_Max_Export_Power": {"meta": "P_Grid_Max_Export_Power"}}
        # at the moment all generic informations are at the storage
        self.generic_mapping = {"T_SoC": "T_SoC"}
        # a dict with standard values for the ofw
        self.standard_data = {"load": {
            "meta": {
            }
        },
            "photovoltaic": {
                "meta": {
                }

            },
            "grid": {
                "meta": {

                }
            },
            "generic": {
            },
            "ESS": {
                "meta": {
                }
            },
            "global_control": {}
        }
        self.list_with_desired_output_parameters = ["P_ESS_Output", "P_PV_Output", "P_PV_R_Output", "P_PV_S_Output"
            , "P_PV_T_Output", "Q_PV_Output", "Q_PV_R_Output", "Q_PV_S_Output", "Q_PV_T_Output"]

        logger.debug("Profess instance created")

    def post_model(self, model_name, model_data):
        """
        post the model to the ofw
        :param model_name: name of posted model
        :param model_data:  optimization model see @linksmartOptimizationFramework for definition
        :return: returns 0 when successful, 1 when not successful
        """
        response = ""
        try:
            response = self.httpClass.put(self.domain + "models/" + model_name, model_data)
            #json_response = response.json()
            #logger.debug("postmodel started " + str(model_name) + " ,response of ofw: " + str(json_response))
            if response.status_code == 200:
                logger.debug("model post completed: " + str(model_name))
                return 0
            else:
                logger.error("failed to post model: " + str(model_name))
                return 1
        except:
            logger.error("Failed to post model, No connection to the OFW could be established at :" + str(
                self.domain) + "models/")

            return 1

    def post_data(self, input_data, node_name, soc_list):
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
        response = ""
        try:
            response = self.httpClass.post(self.domain + "inputs/dataset", input_data, "json")
            #json_response = response.json()
            # regex to get profess_id
            pattern = re.compile("/inputs*[/]([^']*)")
            m = pattern.findall(str(response.headers))
            if m != "":
                profess_id = m[0]
            else:
                logger.error("failed to post data to the ofw, no professID was returned " + str(node_name))
            #logger.debug("Response of OFW after post data: " + str(json_response) + ": " + str(
                #profess_id) + " , statusCode: " + str(response.json()))
            # the professId is saved for futher referencing
            self.set_profess_id_for_node(node_name, profess_id, soc_list)
            # the posted data is also saved internaly for other optimizations
            self.set_config_json(node_name, profess_id, input_data, soc_list)
            if response.status_code == "Instance created" or response.status_code == 201:
                return 0
            else:
                logger.error("failed to post_data node: " + str(node_name) + " and input data: " + str(
                    input_data) + "Response Code: " + str(response.status_code) + ",  Response from the OFW: " + str(
                    response.json()))
                return 1
        except:
            logger.error("Failed to post data, No connection to the OFW could be established at :" + str(
                self.domain) + "inputs/dataset")
            return 1

    def post_all_standard_data(self, soc_list):
        """
        posts standard_data to the ofw for every relevant bus (nodes with ESS)
        :return: returns 0 when successful, 1 when not successful
        """
        node_element_list = self.json_parser.get_node_element_list(soc_list)
        all_successful = True
        for node_element in node_element_list:
            for node_name in node_element:
                if self.post_data((self.standard_data), node_name, soc_list):
                    all_successful = False
        if all_successful:
            return 0
        else:
            logger.error("failed to post_all_standard_data ")
            return 1

    def get_ofw_ids(self, soc_list):
        id_list=[]
        node_name_list = self.json_parser.get_node_name_list(soc_list)
        for node_name in node_name_list:
            profess_id = self.get_profess_id(node_name, soc_list)
            id_list.append(profess_id)
        return id_list

    def get_ofw_ids_and_node_name(self, soc_list):
        id_list=[]
        node_name_list = self.json_parser.get_node_name_list(soc_list)
        for node_name in node_name_list:
            profess_id = self.get_profess_id(node_name, soc_list)
            id_list.append({profess_id: node_name})
        return id_list

    def erase_all_ofw_instances(self, soc_list):
        id_list = self.get_ofw_ids(soc_list)
        for id in id_list:
            response = self.httpClass.delete(self.domain + "inputs/dataset/"+str(id))
            #logger.debug("response "+str(response))

    def set_standard_data(self, standard_data):
        """
        function to change standard values
        :param standard_data: dict with new standard values, syntax:
        {"load":{"meta":{...},...},{"ESS":{"meta:{...}, ...}, {"grid":{"meta":{...}},
        {"photovoltaic":{ "meta":{...}, ...}, "generic":{..}}
        :return:
        """
        self.standard_data = standard_data

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
            logger.error("Failed to get optimization status, No connection to the OFW could be established at :" + str(
                self.domain) + "optimization/status")

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
            #logger.debug("response start "+str(response.json()))
            if response.status_code == 200:
                if not response.json() == {}:
                    return response.json()
                else:
                    logger.error("OFW returned an empty response")
                    return 1
            else:
                logger.error("failed to get output from professID: " + str(profess_id) + " response from ofw: " + str(
                    response.json()))
                return 1
        except:
            logger.error("Failed to get optimization output, No connection to the OFW could be established at :" + str(
                self.domain) + "outputs/")
            return 1

    def is_running(self, soc_list):
        """
        :return: Returns if a optimization on a node is still running, true if on a node runs an optimization,
        otherwise false
        """
        # busy waiting
        time.sleep(0.5)
        opt_status = self.get_optimization_status()
        # logger.debug("optimization status: " + str(opt_status))
        running_flag = False
        node_name_list = self.json_parser.get_node_name_list(soc_list)
        for node_name in node_name_list:
            profess_id = self.get_profess_id(node_name, soc_list)
            if profess_id != 0:
                if profess_id in opt_status["status"]:
                    if opt_status["status"][profess_id]["status"] == "running":
                        #logger.debug("An optimization is still running: " + str(profess_id))
                        running_flag = True
                else:
                    logger.error(
                        "Failed to check if " + str(profess_id) + " is still running, not found in optimization status")
            else:
                logger.error(
                    "Check connection to the OFW, we try to check a non existing profess_id: " + str(profess_id))
        if running_flag:
            return True
        else:
            return False

    def wait_and_get_output(self, soc_list):
        """
        :return: returns a list with the translated ouputs of all nodes see (@translate_output)
        """
        logger.debug("wait for OFW output")
        node_name_list = self.json_parser.get_node_name_list(soc_list)
        if node_name_list != 0:
            while self.is_running(soc_list):
                logger.debug("finish status key"+str(self.redisDB.get(self.finish_status_key)))
                if self.redisDB.get(self.finish_status_key) == "True":
                    break
                else:
                    pass
            output_list = []

            for node_name in node_name_list:
                profess_id = self.get_profess_id(node_name, soc_list)
                if profess_id != 0:
                    output = self.get_output(profess_id)
                    if not output == 1:
                        output_list.append({profess_id: output})
            logger.debug("OFW finished, all optimizations stopped")
            translated_output = self.translate_output(output_list, soc_list)
            return translated_output
        else:
            return []

    def start(self, freq, horizon, dt, model, repition, solver, optType, profess_id, single_ev = False):
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
        logger.debug("start " + str(profess_id))
        try:
            response = self.httpClass.put(self.domain + "optimization/start/" + profess_id, {"control_frequency": freq,
                                                                                             "horizon_in_steps": horizon,
                                                                                             "dT_in_seconds": dt,
                                                                                             "model_name": model,
                                                                                             "repetition": repition,
                                                                                             "solver": solver,
                                                                                             "optimization_type": optType,
                                                                                             "single_ev":single_ev})
            #json_response = response.json()
            #logger.debug(
                #str(json_response) + ": " + str(profess_id) + " , Status code of start: " + str(response.status_code))
            if (str(response.status_code) == 200):
                # code 200 is returned even when the optimization couldn't start because of missing data for the optimization
                return 0
            else:
                return response
        except:
            logger.error("Failed to start optimization, No connection to the OFW could be established at :" + str(
                self.domain) + "optimization/start/")

    def start_all(self, soc_list=None, chargers=None):
        """
        starts all optimizations on the relevant nodes (nodes with ESS)
        :param optimization_model: optional optimization_model, when no model is given the models in the ESS definition
        are used, see topology
        :return: returns 0 when successful, else 1
        """

        logger.debug("All optimizations are being started.")

        if not soc_list == None:
            node_name_list = self.json_parser.get_node_name_list(soc_list)

        if not node_name_list == None:
            storage_opt_model = None
            for node_name in node_name_list:
                # search for list with all elemens that are connected to bus: node_name
                element_node = (
                    next(item for item in self.json_parser.get_node_element_list(soc_list) if node_name in item))
                solver = "cbc"
                for node_element in element_node[node_name]:
                    if "storageUnits" in node_element:
                        storage = node_element
                        storage_opt_model = storage["storageUnits"]["optimization_model"]
                        #logger.debug("storage element "+str(storage["storageUnits"]))
                        global_control = storage["storageUnits"]["global_control"]

                        type = None
                        if not chargers == None:
                            for charger_name, charger_element in chargers.items():
                                node = charger_element.get_bus_name()
                                # logger.debug("node name "+str(node_name)+" node "+str(node))
                                if node == node_name:
                                    type = charger_element.get_type_application()

                        if not type == None:
                            type_optimization = "stochastic"
                            if type == "residential" and storage_opt_model == "Maximize Self-Consumption":
                                storage_opt_model = "StochasticResidentialMaxPV"
                                solver = "cbc"
                                single_ev = True
                            if type == "residential" and storage_opt_model == "Maximize Self-Production":
                                storage_opt_model = "StochasticResidentialMinGrid"
                                solver = "ipopt"
                                single_ev = True
                            if type == "residential" and storage_opt_model == "MinimizeCosts":
                                storage_opt_model = "StochasticResidentialMinPBill"
                                solver = "cbc"
                                single_ev = True
                            if type == "commercial" and storage_opt_model == "Maximize Self-Consumption":
                                storage_opt_model = "CarParkModel"
                                solver = "cbc"
                                single_ev = False
                            if type == "commercial" and storage_opt_model == "Maximize Self-Production":
                                storage_opt_model = "CarParkModelMinGrid"
                                solver = "ipopt"
                                single_ev = False
                        else:
                            type_optimization = "discrete"
                            if storage_opt_model == "Maximize Self-Consumption" and not global_control:
                                solver = "cbc"
                                single_ev = False
                            if storage_opt_model == "Maximize Self-Production" and not global_control:
                                solver = "gurobi"
                                single_ev = False
                            if storage_opt_model == "MinimizeCosts" and not global_control:
                                solver = "cbc"
                                single_ev = False
                            if storage_opt_model == "Maximize Self-Consumption" and global_control:
                                storage_opt_model = "Maximize Self-Consumption with global control"
                                solver = "cbc"
                                single_ev = False
                            if storage_opt_model == "Maximize Self-Production" and global_control:
                                storage_opt_model = "Maximize Self-Production with global control"
                                solver = "ipopt"
                                single_ev = False
                            if storage_opt_model == "MinimizeCosts" and global_control:
                                storage_opt_model = "MinimizeCosts with global control"
                                solver = "cbc"
                                single_ev = False


                logger.debug("optimization model: " + str(storage_opt_model) + " single_ev " + str(single_ev))
                if storage_opt_model == None:
                    logger.error(
                        "No optimization model given for storage element " + str(node_element["storageUnits"]["id"]))
                    break

                start_response = self.start(1, 24, 3600, storage_opt_model, 1, solver, type_optimization,
                                            self.get_profess_id(node_name, soc_list), single_ev)

                if start_response is None:
                    break
                    return 1
                if start_response.status_code is not 200 and start_response is not None:
                    self.check_start_issue(start_response, node_name, soc_list)
                    break
                    return 1
            return 0
        else:
            return 0



    def check_start_issue(self, response, node_name, soc_list):
        """
        parses the response a failed optimization start returns, and  logs why it might have failed
        :param response: ofw response of failed start
        :param node_name: node name where start failed
        :return:
        """
        json_response = response.json()
        if "Data source for following keys not declared:" in json_response:
            logger.error("Missing data for optimization model, couldn't start")
            pattern = re.compile("'(.*?)'")  # regex to find which parameters where missing
            missing_parameters = pattern.findall(str(json_response))
            for parameter in missing_parameters:
                if "PV" in parameter:
                    node_element_list = self.json_parser.get_node_element_list(soc_list)
                    for bus_element in node_element_list:
                        if node_name in bus_element:
                            pv_flag = False
                            storage_info = ""
                            pv_info = ""
                            for node_element in bus_element[node_name]:
                                if "photovoltaic" in node_element:
                                    pv_flag = True
                                    pv_info = node_element
                                if "storageUnits" in node_element:
                                    storage_info = node_element
                            if pv_flag:
                                logger.error("PV Information is missing but PV is connected at :" + str(
                                    node_name) + " , connected storage: " + str(
                                    storage_info) + " , connected pv: " + str(pv_info))
                            else:
                                logger.error(str(
                                    parameter) + " is needed for the optimization, but no pv was connected to :" + str(
                                    node_name) + " , connected storage: " + str(storage_info))
        else:

            logger.error("start failed, but no data keys where missing, reason it failed: " + str(
                json_response) + " response status code: " + str(response.status_code))

    def stop(self, profess_id):
        """
        stops the optimization with id: profess_id in the ofw
        :param profess_id: which optimization should be stopped
        :return: 0 when successful, else 1
        """
        logger.debug("Stop optimization: " + str(profess_id))
        if profess_id != 0:
            response = self.httpClass.put(self.domain + "optimization/stop/" + profess_id)
            #json_response = response.json()
            #logger.debug(json_response + " :" + str(profess_id))
            if response.status_code == 200:
                return 0
            else:
                return 1
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
        logger.debug("update_config_json has started at " + str(profess_id))
        if profess_id != 0:
            response = self.httpClass.put(self.domain + "inputs/dataset/" + profess_id, config_json)
            #json_response = response.json()
            #logger.debug("Response from OFW to update_config :" + str(json_response) + ": " + str(profess_id))
            if response.status_code == 200:
                return 0
            else:
                return 1
        else:
            return 1

    def set_storage(self, node_name, soc_list):
        """
        sets all storage related values of the local config of node_name
        :param node_name: name of the bus
        :return:
        """
        logger.debug("set_storage config data of " + str(node_name))
        self.set_soc_ess(soc_list)
        node_number = self.json_parser.get_node_name_list(soc_list).index(node_name)
        profess_id = self.get_profess_id(node_name, soc_list)
        if profess_id != 0:
            config_data_of_node = self.dataList[node_number][node_name][profess_id]

            # for radial_number in range(len(self.json_parser.topology["radials"])):
            node_element_list = self.json_parser.get_node_element_list(soc_list)[node_number][node_name]

            config_data_of_node = self.iterate_mapping(self.storage_mapping, "ESS", "storageUnits", node_element_list,
                                                       config_data_of_node)
            config_data_of_node = self.iterate_mapping(self.generic_mapping, "generic", "storageUnits",
                                                       node_element_list,
                                                       config_data_of_node)
            config_data_of_node = self.iterate_mapping(self.grid_mapping, "grid", "storageUnits", node_element_list,
                                                       config_data_of_node)
            self.dataList[node_number][node_name][profess_id] = config_data_of_node
            #logger.debug("dataList " + str(self.dataList[node_number][node_name][profess_id]))

    def iterate_mapping(self, mapping, name_in_ofw, name_in_topology, node_element_list, config_data_of_node):
        """
        helper function to iterate trough a mapping and set the values in the config_data
        :param mapping: which mapping is used, see mappings of profess for further information
        :param name_in_ofw: to which category the values will be mapped, usual values: load, photovoltaic, grid, ESS, generic
        :param name_in_topology: name of the element where values should, be retrieved, usualy photovoltaics and StorageUnits
        :param node_element_list: all connected elements at a specific node
        :param config_data_of_node: data for the ofw
        :return:
        """

        #logger.debug("we use mapping: "+str(mapping)+" iterate mapping: name in ofw: " + str(name_in_ofw) + ", name in topology: " + str(name_in_topology))

        element_index = 0
        for node_element in node_element_list:
            if name_in_topology in node_element:
                # searche for the index where the storage is
                element_index = node_element_list.index(node_element)
        if name_in_topology in node_element_list[element_index].keys():
            for mapping_key in mapping:
                if mapping_key in node_element_list[element_index][name_in_topology]:
                    if mapping_key in self.percentage_mapping:
                        percentage = 100
                    else:
                        percentage = 1

                    #logger.debug("mappingkey " + str(mapping_key) + " and is mapped to " + str(mapping[mapping_key]))

                    if type(mapping[mapping_key]) == dict:
                        # this means the key is mapped to meta data
                        config_data_of_node[name_in_ofw]["meta"][mapping[mapping_key]["meta"]] = \
                            node_element_list[element_index][name_in_topology][mapping_key] / percentage
                    if type(mapping[mapping_key]) == list:
                        # this means a value in the storageunit is mapped to multiple values in the ofw
                        for part in mapping[mapping_key]:
                            if "meta" in part:
                                config_data_of_node[name_in_ofw]["meta"][part["meta"]] = \
                                    node_element_list[element_index][name_in_topology][mapping_key] / percentage
                            else:
                                config_data_of_node[name_in_ofw][part] = \
                                node_element_list[element_index][name_in_topology][
                                    mapping_key] / percentage
                    if type(mapping[mapping_key]) == str:
                        # the key can be directly mapped
                        config_data_of_node[name_in_ofw][mapping[mapping_key]] = \
                            node_element_list[element_index][name_in_topology][mapping_key] / percentage
        return config_data_of_node

    def set_photovoltaics(self, node_name, soc_list):
        """
        set all the photovoltaics related values of the local config of node_name
        :param node_name: the name of the bus
        :return:
        """
        logger.debug("set photovoltaics config data of " + str(node_name))
        node_number = self.json_parser.get_node_name_list(soc_list).index(node_name)
        profess_id = self.get_profess_id(node_name, soc_list)
        if profess_id != 0:
            config_data_of_node = self.dataList[node_number][node_name][profess_id]
            #for radial_number in range(len(self.json_parser.topology["radials"])):
            node_element_list = self.json_parser.get_node_element_list(soc_list)[node_number][node_name]
            config_data_of_node = self.iterate_mapping(self.pv_mapping, "photovoltaic", "photovoltaics",
                                                       node_element_list, config_data_of_node)
            config_data_of_node = self.iterate_mapping(self.grid_mapping, "grid", "photovoltaics", node_element_list,
                                                       config_data_of_node)
            config_data_of_node = self.iterate_mapping(self.generic_mapping, "generic", "photovoltaics",
                                                       node_element_list, config_data_of_node)
            self.dataList[node_number][node_name][profess_id] = config_data_of_node


    def set_config_json(self, node_name, profess_id, config_json, soc_list):
        """
        sets the config data in profess of the node node_name
        :param node_name: name of the bus
        :param profess_id: id of the optimization
        :param config_json: new config data, syntac:
        {"load":{"meta":{...},...},{"ESS":{"meta:{...}, ...}, {"grid":{"meta":{...}},
        {"photovoltaic":{ "meta":{...}, ...}, "generic":{..}}
        :return:
        """
        logger.debug(
            "set_config_json at " + str(node_name) + " ," + str(profess_id) + "  with config: " + str(config_json))
        if profess_id != 0:
            node_number = self.json_parser.get_node_name_list(soc_list).index(node_name)
            self.dataList[node_number][node_name][profess_id] = copy.deepcopy(config_json)

    def set_profess_id_for_node(self, node_name, new_profess_id, soc_list):
        """
        saves the profess_id of an optimization in the config of node_name
        :param node_name: name of the bus
        :param new_profess_id: which profess_id should be set
        :return:
        """
        logger.debug("set_profess_id_for_node " + str(node_name) + " ," + str(new_profess_id))
        if new_profess_id != 0:
            node_number = self.json_parser.get_node_name_list(soc_list).index(node_name)
            self.dataList[node_number][node_name][new_profess_id] = {}
        else:
            logger.error(
                "a wrong profess_id was set for node: " + str(node_name) + " , profess_id: " + str(new_profess_id))

    def set_profiles(self, load_profiles=None, pv_profiles=None, price_profiles=None, ess_con=None, soc_list=None, voltage_prediction=None):
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
        #logger.debug(str(pv_profiles))
        # logger.debug("load profile: "+str(load_profiles)+" ,pv_profiles: "+str(pv_profiles)+" ,price_profile: "+str(price_profiles)+" ,ess_con "+str(ess_con))
        node_name_list = self.json_parser.get_node_name_list(soc_list)
        if node_name_list != 0:
            for node_name in node_name_list:
                node_number = node_name_list.index(node_name)
                if load_profiles is not None:
                    # setting load profiles
                    for load_profile_for_node in load_profiles:
                    #ToDo copy PV in load
                        node_name_base = node_name
                        if "." in node_name_base:
                            node_name_base = node_name.split(".")[0]
                        if node_name_base in load_profile_for_node:
                            profess_id = self.get_profess_id(node_name, soc_list)
                            if profess_id != 0:
                                config_data_of_node = self.dataList[node_number][node_name][profess_id]
                                #logger.debug("config data "+str(config_data_of_node))
                                phase = load_profile_for_node[node_name_base]
                                #logger.debug("phase "+str(phase))
                                #flag for every phase, R=1, S=2, T=3
                                r_flag = False
                                s_flag = False
                                t_flag = False
                                # checks which phases are used
                                if node_name_base + ".1" in phase:
                                    config_data_of_node["load"]["P_Load_R"] = phase[node_name_base + ".1"]
                                    r_flag = True
                                if node_name_base + ".2" in phase:
                                    config_data_of_node["load"]["P_Load_S"] = phase[node_name_base + ".2"]
                                    s_flag = True
                                if node_name_base + ".3" in phase:
                                    config_data_of_node["load"]["P_Load_T"] = phase[node_name_base + ".3"]
                                    t_flag = True
                                #check if there is a profile for all three phases, if not add all phases to get P_load
                                if node_name_base + ".1.2.3" in phase or node_name_base == phase: #a load profile for all phases can be given as node_name.1.2.3 or as node_name
                                    three_phase = []
                                    #logger.debug("I entered here")
                                    if node_name_base in phase:
                                        config_data_of_node["load"]["P_Load"] = phase[node_name_base]
                                        three_phase = phase[node_name_base]
                                    if node_name + ".1.2.3" in phase:
                                        config_data_of_node["load"]["P_Load"] = phase[node_name_base + ".1.2.3"]
                                        three_phase = phase[node_name_base + ".1.2.3"]
                                    single_phase = []
                                    for value in three_phase:
                                        #when one profile is given, a symetrical load is assumed
                                        value = value / 3
                                        single_phase.append(value)
                                    config_data_of_node["load"]["P_Load_R"] = copy.deepcopy(single_phase)
                                    config_data_of_node["load"]["P_Load_S"] = copy.deepcopy(single_phase)
                                    config_data_of_node["load"]["P_Load_T"] = copy.deepcopy(single_phase)
                                else:
                                    # create loads for phases, with no profile
                                    if not r_flag:
                                        config_data_of_node["load"]["P_Load_R"] = [0] * 24
                                    if not s_flag:
                                        config_data_of_node["load"]["P_Load_S"] = [0] * 24
                                    if not t_flag:
                                        config_data_of_node["load"]["P_Load_T"] = [0] * 24
                                    three_phase = []
                                    for value in range(24):
                                        three_phase_value = config_data_of_node["load"]["P_Load_R"][value] + \
                                                            config_data_of_node["load"]["P_Load_S"][value] + \
                                                            config_data_of_node["load"]["P_Load_T"][value]
                                        three_phase.append(three_phase_value)
                                    config_data_of_node["load"]["P_Load"] = three_phase

                                #logger.debug("load profile set for " + str(node_name))
                else:
                    logger.debug("no load profile was given")
                #logger.debug("pv profiles "+str(pv_profiles))
                if pv_profiles is not None:
                    # setting pv_profiles
                    for pv_profiles_for_node in pv_profiles:
                        profess_id = self.get_profess_id(node_name, soc_list)
                        if profess_id != 0:
                            config_data_of_node = self.dataList[node_number][node_name][profess_id]
                            node_name_base = node_name
                            if "." in node_name_base:
                                node_name_base = node_name.split(".")[0]

                            if node_name_base in pv_profiles_for_node:
                                phase = pv_profiles_for_node[node_name_base]
                                #logger.debug("phase pv "+str(phase))

                                #if node_name_base + ".1.2.3" or node_name_base in phase:
                                    #logger.debug("node_name_base or 123 in phase")
                                for node_name_complete in phase.keys():

                                    len_node_name_complete = 1
                                    if "." in node_name_complete:
                                        len_node_name_complete = len(node_name_complete.split("."))

                                    if (node_name_base == node_name_complete) or len_node_name_complete > 2:
                                        config_data_of_node["photovoltaic"]["P_PV"] = phase[node_name_complete]
                                        three_phase = phase[node_name_complete]
                                        single_phase = []

                                        if len_node_name_complete != 3:
                                            for value in three_phase:
                                                # when one profile is given, a symetrical load is assumed
                                                value = value / 3
                                                single_phase.append(value)
                                            config_data_of_node["photovoltaic"][
                                                "P_PV_R"] = single_phase
                                            config_data_of_node["photovoltaic"][
                                                "P_PV_S"] = single_phase
                                            config_data_of_node["photovoltaic"][
                                                "P_PV_T"] = single_phase
                                        elif len_node_name_complete == 3:
                                            logger.debug("three phase "+str(three_phase))

                                            for value in three_phase:
                                                # when one profile is given, a symetrical load is assumed
                                                value = value / 2
                                                single_phase.append(value)
                                            if ".1" in node_name_complete:
                                                config_data_of_node["photovoltaic"][
                                                    "P_PV_R"] = single_phase
                                            else:
                                                config_data_of_node["photovoltaic"]["P_PV_R"] = [0] * 24
                                            if ".2" in node_name_complete:
                                                config_data_of_node["photovoltaic"][
                                                    "P_PV_S"] = single_phase
                                            else:
                                                config_data_of_node["photovoltaic"]["P_PV_S"] = [0] * 24
                                            if ".3" in node_name_complete:
                                                config_data_of_node["photovoltaic"][
                                                    "P_PV_T"] = single_phase
                                            else:
                                                config_data_of_node["photovoltaic"]["P_PV_T"] = [0] * 24

                                    elif node_name_base in node_name_complete:

                                        r_flag = False
                                        s_flag = False
                                        t_flag = False
                                        # checks which phases are used
                                        if node_name_base + ".1" == node_name_complete:
                                            config_data_of_node["photovoltaic"]["P_PV_R"] = phase[node_name_complete]
                                            r_flag = True
                                        if node_name_base + ".2" == node_name_complete:
                                            config_data_of_node["photovoltaic"]["P_PV_S"] = phase[node_name_complete]
                                            s_flag = True
                                        if node_name_base + ".3" == node_name_complete:
                                            config_data_of_node["photovoltaic"]["P_PV_T"] = phase[node_name_complete]
                                            t_flag = True

                                        if not r_flag:
                                            config_data_of_node["photovoltaic"]["P_PV_R"] = [0] * 24
                                        if not s_flag:
                                            config_data_of_node["photovoltaic"]["P_PV_S"] = [0] * 24
                                        if not t_flag:
                                            config_data_of_node["photovoltaic"]["P_PV_T"] = [0] * 24
                                        three_phase = []
                                        for value in range(24):
                                            three_phase_value = config_data_of_node["photovoltaic"]["P_PV_R"][value] + \
                                                                config_data_of_node["photovoltaic"]["P_PV_S"][value] + \
                                                                config_data_of_node["photovoltaic"]["P_PV_T"][value]
                                            three_phase.append(three_phase_value)
                                        config_data_of_node["photovoltaic"]["P_PV"] = three_phase
                                    else:
                                        logger.debug("No node_name in phase")


                else:
                    logger.debug("no pv_profile was given")
                if ess_con is not None:
                    # setting gesscon profile
                    for ess_con_global in ess_con:
                        profess_id = self.get_profess_id(node_name, soc_list)
                        if profess_id != 0:
                            config_data_of_node = self.dataList[node_number][node_name][profess_id]
                            if node_name in ess_con_global:
                                phase = ess_con_global[node_name]
                                for battery_name in phase:
                                    #At the moment only one ess is connected
                                    config_data_of_node["global_control"]["ESS_Control"] = phase[battery_name]
                else:
                    logger.debug("no ess_con profile was given")
                if voltage_prediction is not None:
                    for voltage_profile in voltage_prediction:
                        profess_id = self.get_profess_id(node_name,soc_list)
                        if profess_id != 0:
                            config_data_of_node = self.dataList[node_number][node_name][profess_id]
                            if node_name == voltage_profile:
                                phase = voltage_prediction[node_name]
                                config_data_of_node["generic"]["voltage_prediction"] = phase
                                logger.debug("voltage profile set")


                profess_id = self.get_profess_id(node_name, soc_list)
                if profess_id != 0:
                    config_data_of_node = self.dataList[node_number][node_name][profess_id]
                    #logger.debug("price prifile profess " + str(price_profiles))
                    if price_profiles is not None:
                        config_data_of_node["generic"]["Price_Forecast"] = price_profiles
                        # logger.debug("price profile set")
                    # updates the profiles in the ofw
                    node_index = node_name_list.index(node_name)
                    self.update_config_json(profess_id, self.dataList[node_index][node_name][profess_id])

    def get_profess_id(self, node_name_input, soc_list):
        """
        :param node_name: bus name
        :return: profess_id which is the optimization id of the optimization on node_name
        """
        profess_id = 0
        for element in self.dataList:
            for node_name, value in element.items():
                for id, rest in value.items():
                    if node_name_input == node_name:
                        profess_id = id
        return profess_id

    def get_node_name(self, profess_id, soc_list):
        """
        :param profess_id:
        :return: bus name for profess_id
        """
        node_name = ""
        name_list = self.json_parser.get_node_name_list(soc_list)
        for name in name_list:
            node_number = name_list.index(name)
            for element in self.dataList[node_number][name]:
                if element == profess_id:
                    node_name = name
        if node_name == "":
            logger.error("there is no node which has the profess_id: " + profess_id)
        return node_name

    def set_data_list(self, soc_list):
        """
        sets up data_list with a list of dictonaries to, with the relevant nodes(nodes with ESS):
        [{node_name1:{},{node_name2:{},...]

        :return:
        """
        # logger.debug("data for nodes is set")
        node_element_list = self.json_parser.get_node_element_list(soc_list)
        #logger.debug("node element list " + str(node_element_list))
        for index in range(len(node_element_list)):
            for node_name in (node_element_list[index]):
                node_element_list[index] = {node_name: {}}
        self.dataList = node_element_list


    def set_up_profess(self, soc_list=None, load_profiles=None, pv_profiles=None, price_profiles=None, ess_con=None,voltage_prediction=None):
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
        logger.debug("setup profess started")
        #logger.debug("price prifile profess " + str(price_profiles))
        #logger.debug("soc_list " + str(soc_list))
        #logger.debug("load_profiles "+ str(load_profiles))
        # logger.debug("pv_profiles "+ str(pv_profiles))
        # logger.debug("price_profiles "+ str(price_profiles))
        # logger.debug("ess_con " + str(ess_con))
        if self.dataList == []:
            # this happends just for the first set_up
            self.set_data_list(soc_list)
            self.post_all_standard_data(soc_list)
            node_name_list = self.json_parser.get_node_name_list(soc_list)
            if node_name_list != 0:
                for nodeName in node_name_list:
                    self.set_storage(nodeName, soc_list)
                    self.set_photovoltaics(nodeName, soc_list)
                    self.set_generic(nodeName,soc_list)
                    self.set_grid(nodeName,soc_list)

                #node_element_list = self.json_parser.get_node_element_list(soc_list)
                #logger.debug("node_ element list "+str(node_element_list))
        #logger.debug("price prifile profess "+str(price_profiles))
        if soc_list is not None:
            self.set_soc_ess(soc_list)

            self.set_profiles(load_profiles=load_profiles, pv_profiles=pv_profiles, price_profiles=price_profiles
                              , ess_con=ess_con, soc_list=soc_list, voltage_prediction=voltage_prediction)
            #logger.debug("data list "+str(self.dataList))



    def set_grid(self, node_name, soc_list):
        """
        sets all grid related data
        :param node_name: node name where the data is set
        :param soc_list: soc_list where the grid data is
        :return:
        """
        logger.debug("Setting grid ")
        node_name_list = self.json_parser.get_node_name_list(soc_list)
        node_number = node_name_list.index(node_name)
        if soc_list is not None:
            # sets new values for storage: soc, charging ,...
            if type(soc_list) is list:
                for soc_list_for_node in soc_list:
                    profess_id = self.get_profess_id(node_name, soc_list)
                    if profess_id != 0:
                        config_data_of_node = self.dataList[node_number][node_name][profess_id]
                        if node_name in soc_list_for_node:
                            storage_information = soc_list_for_node[node_name]
                            for grid_key in self.grid_mapping:
                                if grid_key in storage_information["Grid"]:
                                    if grid_key in self.percentage_mapping:
                                        percentage = 100
                                    else:
                                        percentage = 1
                                    if type(self.grid_mapping[grid_key]) == dict:
                                        # this means the key is mapped to meta data
                                        config_data_of_node["grid"]["meta"][self.grid_mapping[grid_key]["meta"]] = \
                                            storage_information["Grid"][grid_key] / percentage


                                    if type(self.grid_mapping[grid_key]) == list:
                                        # this means a value in the storageunit is mapped to multiple values in the ofw
                                        for part in self.grid_mapping[grid_key]:
                                            if "meta" in part:
                                                config_data_of_node["grid"]["meta"][part["meta"]] = \
                                                    storage_information["Grid"][grid_key] / percentage
                                            else:
                                                config_data_of_node["grid"][part] = \
                                                    storage_information["Grid"][grid_key] / percentage
                                    if type(self.grid_mapping[grid_key]) == str:
                                        # the key can be directly mapped
                                        config_data_of_node["grid"][self.grid_mapping[grid_key]] = \
                                            storage_information["Grid"][grid_key] / percentage

    def set_generic(self, node_name, soc_list):
        """
        sets all generic related data
        :param node_name: node name where the data is set
        :param soc_list: soc_list where the generic data is
        :return:
        """
        logger.debug("Setting generic ")
        node_name_list = self.json_parser.get_node_name_list(soc_list)
        node_number = node_name_list.index(node_name)
        if soc_list is not None:
            # sets new values for storage: soc, charging ,...
            if type(soc_list) is list:
                for soc_list_for_node in soc_list:
                    profess_id = self.get_profess_id(node_name, soc_list)
                    if profess_id != 0:
                        config_data_of_node = self.dataList[node_number][node_name][profess_id]
                        if node_name in soc_list_for_node:
                            storage_information = soc_list_for_node[node_name]
                            for generic_key in self.generic_mapping:
                                if generic_key in storage_information["ESS"]:
                                    if generic_key in self.percentage_mapping:
                                        percentage = 100
                                    else:
                                        percentage = 1
                                    if type(self.generic_mapping[generic_key]) == dict:
                                        # this means the key is mapped to meta data
                                        config_data_of_node["generic"][
                                            self.generic_mapping[generic_key]["meta"]] = \
                                            storage_information["ESS"][generic_key] / percentage
                                    if type(self.generic_mapping[generic_key]) == list:
                                        # this means a value in the storageunit is mapped to multiple values in the ofw
                                        for part in self.generic_mapping[generic_key]:
                                            if "meta" in part:
                                                config_data_of_node["generic"]["meta"][part["meta"]] = \
                                                    storage_information["ESS"][generic_key] / percentage
                                            else:
                                                config_data_of_node["generic"][part] = \
                                                    storage_information["ESS"][generic_key] / percentage
                                    if type(self.generic_mapping[generic_key]) == str:
                                        # the key can be directly mapped
                                        config_data_of_node["generic"][self.generic_mapping[generic_key]] = \
                                            storage_information["ESS"][generic_key] / percentage

    def set_soc_ess(self, soc_list):
        """
        updates soc related values
        :param soc_list: soc_list with all updates values
        :return:
        """
        logger.debug("Setting updated ess soc_list values ")
        # logger.debug("load profile: "+str(load_profiles)+" ,pv_profiles: "+str(pv_profiles)+" ,price_profile: "+str(price_profiles)+" ,ess_con "+str(ess_con))
        node_name_list = self.json_parser.get_node_name_list(soc_list)
        if node_name_list != 0:
            for node_name in node_name_list:
                node_number = node_name_list.index(node_name)
                if soc_list is not None:
                    # sets new values for storage: soc, charging ,...
                    if type(soc_list) is list:
                        for soc_list_for_node in soc_list:
                            profess_id = self.get_profess_id(node_name, soc_list)
                            if profess_id != 0:
                                config_data_of_node = self.dataList[node_number][node_name][profess_id]
                                if node_name in soc_list_for_node:
                                    storage_information = soc_list_for_node[node_name]

                                    for storage_key in self.storage_mapping:
                                        if storage_key in storage_information["ESS"]:
                                            if storage_key in self.percentage_mapping:
                                                percentage = 100
                                            else:
                                                percentage = 1
                                            if type(self.storage_mapping[storage_key]) == dict:
                                                # this means the key is mapped to meta data
                                                config_data_of_node["ESS"]["meta"][
                                                    self.storage_mapping[storage_key]["meta"]] = \
                                                    storage_information["ESS"][storage_key] / percentage
                                            if type(self.storage_mapping[storage_key]) == list:
                                                # this means a value in the storageunit is mapped to multiple values in the ofw
                                                for part in self.storage_mapping[storage_key]:
                                                    if "meta" in part:
                                                        config_data_of_node["ESS"]["meta"][part["meta"]] = \
                                                            storage_information["ESS"][storage_key] / percentage
                                                    else:
                                                        config_data_of_node["ESS"][part] = \
                                                            storage_information["ESS"][storage_key] / percentage
                                            if type(self.storage_mapping[storage_key]) == str:
                                                # the key can be directly mapped
                                                config_data_of_node["ESS"][self.storage_mapping[storage_key]] = \
                                                    storage_information["ESS"][storage_key] / percentage
    def translate_output(self, output_data, soc_list):
        """
        translates the ouptut data from whole time horizon to next hour, and also just returns wanted values
        :param output_data: data which has to be translated
        :return: translated output, syntax: [{node_name:{ profess_id:{ variable1: value1, variable2:value2, ...]}, ...]
        """
        if output_data == {}:
            logger.error("No results were returned by the OFW")

        list_profess_id_and_node_name = self.get_ofw_ids_and_node_name(soc_list)
        output_list = []
        #logger.debug("output data " + str(output_data))
        for parameter_output_list in output_data:
            output_dictionary={}
            #logger.debug("parameter list "+str(parameter_output_list))
            for profess_id, ofw_outputs in parameter_output_list.items():
                #logger.debug("profess id "+str(profess_id)+" ofw outputs "+str(ofw_outputs))
                for element in list_profess_id_and_node_name:
                    for id, node_name in element.items():
                        if profess_id == id:
                            output_dictionary[node_name]={}
                            node_name_intern=node_name
                output_dictionary[node_name_intern][profess_id] = {}
                for key, results in ofw_outputs.items():
                    list_timestep=[]
                    for timestep in results.keys():
                        list_timestep.append(float(timestep))
                    min_timestep=min(list_timestep)
                    #logger.debug("list timestep "+str(list_timestep))
                    #logger.debug("min "+str(min_timestep))
                    output_dictionary[node_name_intern][profess_id][key]=results[str(min_timestep)]
                    #logger.debug("output_dictionary " + str(output_dictionary))
                output_list.append(output_dictionary)

        #logger.debug("output list "+str(output_list))


        return output_list
