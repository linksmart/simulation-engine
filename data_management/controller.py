import logging
import json
import os
import time
import sys

from profess.JSONparser import *
from profess.Profess import *
from simulator.openDSS import OpenDSS
from data_management.redisDB import RedisDB
from profiles.profiles import *
from gesscon.gessconConnnector import GESSCon
#from simulation_management import simulation_management as SM
from data_management.inputController import InputController
from data_management.utils import Utils
import threading

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class gridController(threading.Thread):

    def __init__(self, id, duration):
        super(gridController, self).__init__()
        logger.info("Initializing simulation controller")
        self.sim = OpenDSS(id)
        self.id = id
        logger.debug("id "+str(id))
        self.nodeNames =[]
        self.allBusMagPu=[]
        self.yCurrent = []
        self.losses = []
        self.voltage_bases = []
        self.city = None
        self.country = None
        self.redisDB = RedisDB()
        self.lock_key = "id_lock"
        self.stop_signal_key = "opt_stop_" + self.id
        self.finish_status_key = "finish_status_" + self.id
        self.redisDB.set(self.stop_signal_key, "False")
        self.redisDB.set(self.finish_status_key, "False")
        self.sim_hours = duration
        logger.debug("Starting input controller")
        self.input = InputController(id, self.sim, self.sim_hours)
        self.topology = self.input.get_topology()
        self.utils = Utils()

        self.stopRequest = threading.Event()
        logger.debug("Simulation controller initiated")


    def get_profess_url(self):
        return self.profess_url

    def get_soc_list(self,topology, sim_hours):
        radial=topology["radials"]#["storageUnits"]
        common=topology["common"]
        list_storages=[]
        soc_list = []
        soc_dict_intern = {"SoC":None}
        storages=[]
        photovoltaics=[]
        for element in radial:
            for key, value in element.items():
                if key == "storageUnits":
                    storages=value
                if key == "photovoltaics":
                    photovoltaics=value

        for ess_element in storages:
            soc_dict = {}
            logger.debug("element intern "+str(ess_element))
            soc_dict[ess_element["bus1"]]={"SoC":ess_element["soc"],
                                              "T_SoC":25,
                                              "id":ess_element["id"],
                                              "Battery_Capacity":ess_element["storage_capacity"],
                                              "max_charging_power":ess_element["max_charging_power"],
                                              "max_discharging_power":ess_element["max_discharging_power"],
                                                "charge_efficiency":ess_element["charge_efficiency"],
                                           "discharge_efficiency":ess_element["discharge_efficiency"],
                                              "Q_Grid_Max_Export_Power": common["max_reactive_power_in_kVar_to_grid"],
                                              "P_Grid_Max_Export_Power": common["max_real_power_in_kW_to_grid"]}
            for pv_element in photovoltaics:
                if pv_element["bus1"] == ess_element["bus1"]:
                    soc_dict[ess_element["bus1"]]["pv_name"]=pv_element["id"]
            soc_list.append(soc_dict)
            #list_storages.append(ess_element)
        #logger.debug("list_storages "+str(list_storages))
        logger.debug("soc_list " + str(soc_list))
        return soc_list

    def set_new_soc(self, soc_list):
        #self.sim.getSoCfromBattery("Akku1")

        new_soc_list=[]
        for element in soc_list:
            for key, value in element.items():
                element_id=value["id"]
                logger.debug("ESS_id "+str(element_id))
                logger.debug("SoC 1 " + str(self.sim.getSoCfromBattery(element_id)))
                SoC = float(self.sim.getSoCfromBattery(element_id))
                value["SoC"]=SoC
                new_soc_list.append(element)
        logger.debug("new soc list: " + str(new_soc_list))
        return new_soc_list


    def getId(self):
        return self.id



    def join(self, timeout=None):
        self.stopRequest.set()
        super(gridController, self).join(timeout)

    def Stop(self):
        try:
            self.sim.Stop()
        except Exception as e:
            self.logger.error("error stopping simulator " + str(e))

        self.redisDB.set(self.stop_signal_key, "True")
        if self.isAlive():
            self.join(1)


    def get_finish_status(self):
        return self.redisDB.get(self.finish_status_key)


    def run(self):#self, id, duration):
        #self.id = id
        #self.duration = duration

        common = self.topology["common"]
        radial = self.topology["radials"]

        self.input.setParameters(self.id, common)
        self.sim.set_base_frequency(self.input.get_base_frequency())
        self.sim.setNewCircuit(self.id, common)





        # ----------PROFESS----------------#
        if common["url_storage_controller"]:
            self.profess_url = common["url_storage_controller"]
            logger.debug("profess url "+str(self.profess_url))
        else:
            self.profess_url = "http://localhost:8080"
        self.domain = self.get_profess_url() + "/v1/"
        logger.debug("profess url: " + str(self.domain))
        self.profess = Profess(self.domain, self.topology)

        # ----------PROFILES----------------#
        self.profiles = Profiles()
        self.global_control = GESSCon()
        # profess.json_parser.set_topology(data)

        self.input.setup_elements_in_simulator(self.topology, self.profiles, self.profess)
        logger.debug("!---------------Elements added to simulator------------------------ \n")


        transformer_names=self.sim.get_transformer_names()
        logger.debug("Transformer names: "+str(transformer_names))
        logger.debug("Transformers in the circuit")
        for i in range(len(transformer_names)):
            self.sim.create_monitor("monitor_transformer_"+str(i), "Transformer."+str(transformer_names[i]),1,1)

        logger.debug("#####################################################################")
        logger.debug("Simulation of grid " + self.id + " started")
        logger.debug("GridID: "+str(self.id))
        logger.debug("#####################################################################")

        #self.sim.runNode13()
        self.sim.enableCircuit(self.id)

        logger.debug("Active circuit: "+str(self.sim.getActiveCircuit()))

        ##################################################################################PROBLEM################################
      
        #self.sim.setVoltageBases(115, 4.16, 0.48)
        self.sim.setVoltageBases(self.input.get_voltage_bases())
        #self.sim.setMode("snap")
        #self.sim.setMode("daily")
        self.sim.setMode("yearly")
        self.sim.setStepSize("hours")
        self.sim.setNumberSimulations(1)
        logger.info("Solution mode 2: " + str(self.sim.getMode()))
        logger.info("Number simulations 2: " + str(self.sim.getNumberSimulations()))
        logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
        logger.info("Voltage bases: " + str(self.sim.getVoltageBases()))
        logger.info("Starting Hour : " + str(self.sim.getStartingHour()))
        numSteps=self.sim_hours
        #self.redisDB.set("sim_days_"+str(self.id),numSteps)
        #numSteps=3
        logger.debug("Number of steps: "+str(numSteps))
        result=[]

        nodeNames = self.sim.get_node_list()
        len_nodeNames = len(nodeNames)
        elementNames = self.sim.get_element_names()
        len_elementNames= len(elementNames)
        nodeNamesCurrents = self.sim.get_YNodeOrder()
        len_nodeNamesCurrents = len(nodeNamesCurrents)

        #logger.debug("node_ names "+str(nodeNames))
        voltages = [[] for i in range(len(nodeNames))]
        currents = [[] for i in range(len_nodeNamesCurrents)]
        losses = [[] for i in range(len_elementNames)]
        total_losses = []
        powers = [[] for i in range(len(nodeNames))]

        soc_list = self.get_soc_list(self.topology, self.sim_hours)
        charging = True
        logger.debug("+++++++++++++++++++++++++++++++++++++++++++")
        flag_is_storage = self.input.is_Storage_in_Topology(self.topology)
        logger.debug("Storage flag: "+str(flag_is_storage))
        if flag_is_storage:
            flag_global_control = self.input.is_global_control_in_Storage(self.topology)
            logger.debug("Global control flag: "+str(flag_global_control))
        flag_is_charging_station = self.input.is_Charging_Station_in_Topology(self.topology)
        logger.debug("Charging station flag "+str(flag_is_charging_station))
        flag_is_price_profile_needed = self.input.is_price_profile_needed(self.topology)
        logger.debug("Flag price profile needed: "+str(flag_is_price_profile_needed))
        if flag_is_price_profile_needed:
            price_profile_data=self.input.get_price_profile()



        for i in range(numSteps):
            #time.sleep(0.1)
            logger.info("#####################################################################")
            logger.info("loop  numSteps, i= " + str(i) )
            hours = self.sim.getStartingHour()
            logger.info("Starting Hour : " + str(hours))
            logger.info("#####################################################################")

            self.redisDB.set("timestep_"+str(self.id), i)


            #terminal=self.sim.get_monitor_terminals("mon_transformer")
            #logger.debug("Number of terminals in monitor "+str(terminal))


            if flag_is_storage:

                professLoads = self.sim.getProfessLoadschapes(hours, 24)
                #logger.debug("loads "+str(professLoads))
                professPVs = self.sim.getProfessLoadschapesPV(hours, 24)
                #logger.debug("PVs "+str(professPVs))

                if flag_is_price_profile_needed and self.input.is_price_profile():
                    logger.debug("price profile present")
                    price_profile = price_profile_data[int(hours):int(hours+24)]

                soc_list_new = self.set_new_soc(soc_list)

                if flag_global_control:
                    logger.debug("global control present")
                    profess_global_profile = self.global_control.gesscon(professLoads, professPVs, price_profile, soc_list_new)
                    logger.debug("GESSCon result "+str(profess_global_profile))

                if flag_global_control and flag_is_price_profile_needed:
                    self.profess.set_up_profess(soc_list_new, professLoads, professPVs, price_profile, profess_global_profile)
                elif not flag_global_control and flag_is_price_profile_needed:
                    self.profess.set_up_profess(soc_list_new, professLoads, professPVs, price_profile)
                else:
                    self.profess.set_up_profess(soc_list_new, professLoads, professPVs)

                status_profess=self.profess.start_all()

                if not status_profess:
                    profess_output=self.profess.wait_and_get_output()
                    logger.debug("output profess " + str(profess_output))

                    # output syntax from profess[{node_name: {profess_id: {'P_ESS_Output': value, ...}}, {node_name2: {...}]
                    # soc list: [{'node_a15': {'SoC': 60.0, 'id': 'Akku1', 'Battery_Capacity': 3, 'max_charging_power': 1.5, 'max_discharging_power': 1.5}}, {'node_a6': {'SoC': 40.0, 'id': 'Akku2', 'Battery_Capacity': 3, 'max_charging_power': 1.5, 'max_discharging_power': 1.5}}]

                    profess_result=[]
                    for element in profess_output:
                        profess_result_intern = {}
                        for key, value in element.items():
                            node_name = key
                            profess_result_intern[node_name]={}
                            for element_soc in soc_list:
                                for key_node in element_soc.keys():
                                    if key_node == node_name:
                                        profess_result_intern[node_name]["ess_name"] = element_soc[key_node]["id"]
                                        profess_result_intern[node_name]["pv_name"] = element_soc[key_node]["pv_name"]
                                        profess_result_intern[node_name]["max_charging_power"] = element_soc[key_node]["max_charging_power"]
                                        profess_result_intern[node_name]["max_discharging_power"] = element_soc[key_node]["max_discharging_power"]
                            for profess_id, results in value.items():
                                for key_results, powers in results.items():
                                    profess_result_intern[node_name][key_results] = powers

                        profess_result.append(profess_result_intern)
                    logger.debug("profess result: "+str(profess_result))

                    for element in profess_result:
                        ess_name = None
                        pv_name = None
                        p_ess_output = None
                        p_pv_output = None
                        for key, value in element.items():
                            ess_name = value["ess_name"]
                            p_ess_output = value["P_ESS_Output"]
                            pv_name = value["pv_name"]
                            p_pv_output = value["P_PV_Output"]
                            max_charging_power = value["max_charging_power"]
                            max_discharging_power = value["max_discharging_power"]
                        self.sim.setActivePowertoBatery(ess_name, p_ess_output, max_charging_power)
                        self.sim.setActivePowertoPV(pv_name, p_pv_output)
                else:
                    logger.error("OFW instances could not be started")

                # output syntax from profess[{node_name: {profess_id: {'P_ESS_Output': value, ...}}, {node_name2: {...}]

                #soc list: [{'node_a15': {'SoC': 60.0, 'id': 'Akku1', 'Battery_Capacity': 3, 'max_charging_power': 1.5, 'max_discharging_power': 1.5}}, {'node_a6': {'SoC': 40.0, 'id': 'Akku2', 'Battery_Capacity': 3, 'max_charging_power': 1.5, 'max_discharging_power': 1.5}}]

                #self.redisDB.set(self.finish_status_key, "True")

                """logger.debug("kWhRated " + str(self.sim.getCapacityfromBattery("Akku1")))
                logger.debug("kWRated " + str(self.sim.getkWratedfromBattery("Akku1")))
                logger.debug("kWStored " + str(self.sim.getkWhStoredfromBattery("Akku1")))
                logger.debug("kW " + str(self.sim.getkWfromBattery("Akku1")))
                logger.debug("Min_SoC " + str(self.sim.getMinSoCfromBattery("Akku1")))
                logger.debug("bus " + str(self.sim.getBusfromBattery("Akku1")))
                logger.debug("ESS state "+str(self.sim.getStatefromBattery("Akku1")))
                max_charging_power_value=float(self.sim.getkWratedfromBattery("Akku1"))

                SoC = float(self.sim.getSoCfromBattery("Akku1"))
                logger.debug("SoC_value Akku1: " + str(SoC))
                if i>0:

                    if charging is True:

                        if SoC >= 100:
                            charging = False
                            logger.debug("Entered to discharging")
                            self.sim.setActivePowertoBatery("Akku1",0.5,max_charging_power_value)
                        else:
                            logger.debug("Entered to charging")
                            self.sim.setActivePowertoBatery("Akku1", -0.5, max_charging_power_value)
                    else:

                        if SoC <= 20:
                            charging = True
                            logger.debug("Entered to charging")
                            self.sim.setActivePowertoBatery("Akku1", -0.5, max_charging_power_value)
                        else:
                            logger.debug("Entered to discharging")
                            self.sim.setActivePowertoBatery("Akku1",0.5, max_charging_power_value)
                logger.debug("ESS state " + str(self.sim.getStatefromBattery("Akku1")))"""

                #logger.debug("######################Ending profess##################################")


                #profess.set_up_profess_for_existing_topology(professLoads, professPVs, dummyPrice, dummyGESSCON)
                """self.profess.set_up_profess_for_existing_topology( professLoads, self.dummyPV, self.dummyPrice, self.dummyGESSCON)
                self.profess.start_all()
                print("--------------------start profess results----------------------------")
                print(self.profess.dataList)
                print(self.profess.wait_and_get_output())
                soc_list = [{"633": {"SoC": 5}}, {"671": {"SoC": 4}}, {"634": {"SoC": 20}}]
                self.profess.update(professLoads, self.dummyPV, self.dummyPrice, soc_list, self.dummyGESSCON)
                print(self.profess.dataList)
                print("--------------------end profess results----------------------------")"""
            else:
                logger.debug("No Storage Units present")

            if flag_is_charging_station:
                logger.debug("charging stations present in the simulation")
                #check if is residential or commercial

                #check if ev is present per charging station and receive a mapping list
                #flag_is_EV = self.input.is_EV(charging_station)

                #send it to profev

            else:
                logger.debug("No charging stations present in the simulation")


            puVoltages, Currents, Losses = self.sim.solveCircuitSolution()
            tot_losses = self.sim.get_total_losses()

            for i in range(len_nodeNames):
                voltages[i].append(puVoltages[i])

            for i in range(len_elementNames):
                number = int(i+(len_elementNames))
                losses[i].append(complex(Losses[i], Losses[number]))

            for i in range(len_nodeNamesCurrents):
                currents[i].append(complex(Currents[i], Currents[int(i+(len_nodeNamesCurrents))]))

            total_losses.append(complex(tot_losses[0],tot_losses[1]))


        #logger.debug("volt finish "+str(voltages))
        logger.debug("#####################################################################################")

        data ={}
        data_voltages={}
        data_currents={}
        data_losses={}
        raw_data={}
        raw_data_voltages={}
        raw_data_currents={}
        raw_data_losses={}
        raw_data_power={}

        ############################### Losses ###################################

        for i in range(len_elementNames):
            raw_data_losses[elementNames[i]]=losses[i]

        for i in range(len_elementNames):
            element= [abs(x) for x in losses[i]]
            data_losses[elementNames[i]]= max(element)

        abs_total_losses=[]
        raw_data_losses["circuit_total_losses"]=total_losses
        for element in total_losses:
            abs_total_losses.append(abs(element))
        data_losses["circuit_total_losses"]=max(abs_total_losses)

        #logger.debug("total_losses " + str(total_losses))
        #data_losses
        ############################### Currents ###################################
        for i in range(len_nodeNamesCurrents):
            raw_data_currents[str(nodeNamesCurrents[i]).lower()]=currents[i]

        for i in range(len_nodeNamesCurrents):
            element= [abs(x) for x in currents[i]]
            key=nodeNamesCurrents[i]
            data_currents[key]=max(element)

        data3 = {}
        for key, value in data_currents.items():
            node, phase = key.split(".", 1)
            key_to_give = str(node).lower()
            if key_to_give not in data3.keys():
                data3[key_to_give] = {}
            data3[key_to_give]["Phase " + phase] = value


        ############################### Voltages ###################################
        for i in range(len(nodeNames)):
            raw_data_voltages[nodeNames[i]] = {"Voltage": voltages[i]}
            data_voltages[nodeNames[i]]={"max":max(voltages[i]), "min":min(voltages[i])}

        data2 = {}
        for key, value in data_voltages.items():
            node, phase = key.split(".", 1)
            if node not in data2.keys():
                data2[node] = {}
            data2[node]["Phase " + phase] = value

        ###############################Max power in transformers###################################
        S_total = []
        mon_sample = []
        for i in range(len(transformer_names)):
            name_monitor="monitor_transformer_" + str(i)
            #logger.debug("i in sample monitor "+str(i)+" "+str(name_monitor))
            S_total.append(self.sim.get_monitor_sample(name_monitor))

        power={}
        for i in range(len(transformer_names)):
            raw_data_power[transformer_names[i]]=S_total[i]
            power["Transformer."+str(transformer_names[i])]=max(S_total[i])
        #logger.debug("power "+str(power))
        data={"voltages":data2, "currents":data3,"losses":data_losses, "powers":power}


        raw_data = {"voltages": raw_data_voltages, "currents": raw_data_currents, "losses": raw_data_losses, "powers": raw_data_power}



        result=data



        fname = (str(self.id))+"_result"
        path = os.path.join("data", str(self.id), fname)
        logger.debug("Storing results in data folder")
        self.utils.store_data(path, result)
        logger.debug("Results succesfully stored")
        logger.debug("Stroring raw data in data folder")
        fname_row = (str(self.id)) + "_result_raw.json"
        path = os.path.join("data", str(self.id), fname_row)
        self.utils.store_data_raw(path, raw_data)
        logger.debug("Raw data successfully stored")
        self.redisDB.set(self.finish_status_key, "True")

        logger.debug("#####################################################################################")
        logger.debug("##########################   Simulation End   #######################################")
        logger.debug("#####################################################################################")




        #return id
    
    #def results(self):   
        #return (self.nodeNames, self.allBusMagPu)
        #self.finish_status = True
        #return "OK"
        """#ToDo test with snap and daily
        self.sim.setMode("daily")
        self.sim.setStepSize("minutes")
        self.sim.setNumberSimulations(1)
        self.sim.setStartingHour(0)
        self.sim.setVoltageBases(0.4,16)

        #for i in range(numSteps):
            #self.sim.solveCircuitSolution()
            #setStorageControl()
            #If
            #DSSSolution.Converged
            #Then
            #V = DSSCircuit.AllBusVmagPu

        df = self.sim.utils.lines_to_dataframe()
               data = df[['Bus1', 'Bus2']].to_dict(orient="index")
               for name in data:
                   self.sim.Circuit.SetActiveBus(f"{name}")
                   if phase in self.sim.Bus.Nodes():
                       index = self.sim.Bus.Nodes().index(phase)
                       re, im = self.sim.Bus.PuVoltage()[index:index+2]
                       V = abs(complex(re,im))
               logger.info("Voltage: " + str(V))"""
        # logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
        """logger.info("Node Names: "+ str(nodeNames))
        logger.info("All Bus MagPus: " + str(allBusMagPu))
        # !TODO: return node names, voltage and current in json
        # data = {"NodeNames": nodeNames, "Voltage": allBusMagPu}
        # return json.dumps(data)
        logger.info("YCurrent: " + str(yCurrent))
        logger.info("losses: " + str(losses))
        # return ("Nodes: " + str(nodeNames), "\nVoltages " + str(allBusMagPu))
        # return (nodeNames, allBusMagPu)
        # filename = str(id)+"_results.txt"
        # !TODO: Create filename with id so serve multiple simultaneous simulations#DONE
        # json_data = json.dumps(allBusMagPu)"""
