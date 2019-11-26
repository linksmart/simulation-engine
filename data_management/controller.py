import logging
import json
import os
import time
import sys

from profess.JSONparser import *
from profess.Profess import *
from profess.Profev import *

from simulator.openDSS import OpenDSS
from data_management.redisDB import RedisDB
from profiles.profiles import *
from gesscon.gessconConnnector import GESSCon
# from simulation_management import simulation_management as SM
from data_management.inputController import InputController
from data_management.utils import Utils
import threading
import random

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class gridController(threading.Thread):
	
	def __init__(self, id, duration):
		super(gridController, self).__init__()
		logger.info("Initializing simulation controller")
		self.sim = OpenDSS(id)
		self.id = id
		logger.debug("id " + str(id))
		self.nodeNames = []
		self.allBusMagPu = []
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
		
		self.stopRequest = None#threading.Event()
		logger.debug("Simulation controller initiated")
	
	def get_profess_url(self):
		return self.profess_url
	
	def getId(self):
		return self.id
	
	def join(self, timeout=None):
		#self.stopRequest.set()
		super(gridController, self).join(timeout)
	
	def Stop(self):
		try:
			logger.debug("Stop signal received. Stopping the simulation")
			self.sim.Stop()
			self.redisDB.set(self.finish_status_key, "True")
		except Exception as e:
			self.logger.error("error stopping simulator " + str(e))
		
		self.redisDB.set(self.stop_signal_key, "True")
		if self.isAlive():
			try:
				self.join(1)
			except Exception as e:
				logger.error(e)
		sys.exit(0)
	
	def get_finish_status(self):
		return self.redisDB.get(self.finish_status_key)
	
	def run(self):  # self, id, duration):

		self.redisDB.set("status_"+ str(self.id), "OK")
		start_time = time.time()
		common = self.topology["common"]
		radial = self.topology["radials"]
		
		self.input.setParameters(self.id, common)
		self.sim.set_base_frequency(self.input.get_base_frequency())
		self.sim.setNewCircuit(self.id, common)
		
		# ----------PROFESS----------------#
		if common["url_storage_controller"]:
			self.profess_url = common["url_storage_controller"]
			logger.debug("profess url " + str(self.profess_url))
		else:
			self.profess_url = "http://localhost:8080"
		self.domain = self.get_profess_url() + "/v1/"
		logger.debug("profess url: " + str(self.domain))
		self.profess = Profess(self.id, self.domain, self.topology)
		self.profev = Profev(self.id, self.domain, self.topology)
		
		# ----------PROFILES----------------#
		self.profiles = Profiles()
		self.global_control = GESSCon()
		# profess.json_parser.set_topology(data)
		price_profile = None
		answer_setup = self.input.setup_elements_in_simulator(self.topology, self.profiles, self.profess)
		logger.debug("answer "+ str(answer_setup))
		if not answer_setup == 0:
			logger.error(answer_setup)
			self.redisDB.set("status_"+ str(self.id), answer_setup)
			self.Stop()
		logger.debug("!---------------Elements added to simulator------------------------ \n")
		
		transformer_names = self.sim.get_transformer_names()
		logger.debug("Transformer names: " + str(transformer_names))
		logger.debug("Transformers in the circuit")
		for i in range(len(transformer_names)):
			self.sim.create_monitor("monitor_transformer_" + str(i), "Transformer." + str(transformer_names[i]), 1, 1)
		
		logger.debug("#####################################################################")
		logger.debug("Simulation of grid " + self.id + " started")
		logger.debug("GridID: " + str(self.id))
		logger.debug("#####################################################################")
		
		# self.sim.runNode13()
		self.sim.enableCircuit(self.id)
		
		logger.debug("Active circuit: " + str(self.sim.getActiveCircuit()))
		
		##################################################################################PROBLEM################################
		numSteps = self.sim_hours
		logger.debug("Number of steps: " + str(numSteps))

		self.sim.setVoltageBases(self.input.get_voltage_bases())
		self.sim.setMode("yearly")
		self.sim.setStepSize("hours")
		self.sim.setNumberSimulations(1)#(numSteps)
		logger.info("Solution mode: " + str(self.sim.getMode()))
		logger.info("Number simulations: " + str(self.sim.getNumberSimulations()))
		logger.info("Solution stepsize: " + str(self.sim.getStepSize()))
		logger.info("Voltage bases: " + str(self.sim.getVoltageBases()))

		PV_objects_dict = self.sim.get_photovoltaics_objects()
		PV_names = self.input.get_PV_names(self.topology)
		logger.debug("PV_names " + str(PV_names))
		if not PV_names == []:
			flag_is_PV = True
		else:
			flag_is_PV = False

		pvNames = list(PV_objects_dict.keys())
		len_pvNames = len(pvNames)
		loadNames = self.sim.get_all_load_names()
		len_loadNames = len(loadNames)
		#pvNames = self.sim.get_all_pv_names()
		#len_pvNames = len(pvNames)
		essNames = self.input.get_Storage_names(self.topology)
		len_essNames = len(essNames)
		nodeNames = self.sim.get_node_list()
		len_nodeNames = len(nodeNames)
		elementNames = self.sim.get_element_names()
		len_elementNames = len(elementNames)
		#nodeNamesCurrents = self.sim.get_YNodeOrder()
		#len_nodeNamesCurrents = len(nodeNamesCurrents)
		lineNames = self.sim.get_all_lines_names()
		len_lineNames = len(lineNames)
		len_transformerNames = len(transformer_names)

		
		# logger.debug("node_ names "+str(nodeNames))
		load_powers_phase_1 = [[] for i in range(len_loadNames)]
		load_powers_phase_2 = [[] for i in range(len_loadNames)]
		load_powers_phase_3 = [[] for i in range(len_loadNames)]
		pv_powers_phase_1 = [[] for i in range(len_pvNames)]
		pv_powers_phase_2 = [[] for i in range(len_pvNames)]
		pv_powers_phase_3 = [[] for i in range(len_pvNames)]
		ess_powers_phase_1 = [[] for i in range(len_essNames)]
		ess_powers_phase_2 = [[] for i in range(len_essNames)]
		ess_powers_phase_3 = [[] for i in range(len_essNames)]
		trafo_powers_phase_1 = [[] for i in range(len_transformerNames)]
		trafo_powers_phase_2 = [[] for i in range(len_transformerNames)]
		trafo_powers_phase_3 = [[] for i in range(len_transformerNames)]
		ess_soc = [[] for i in range(len_essNames)]
		voltages = [[] for i in range(len(nodeNames))]
		currents = [[] for i in range(len_lineNames)]
		losses = [[] for i in range(len_elementNames)]
		total_losses = []


		ESS_names = self.input.get_Storage_names(self.topology)
		logger.debug("ESS_names " + str(ESS_names))
		soc_from_profess = [[] for i in range(len(ESS_names))]
		ess_powers_from_profess = [[] for i in range(len(ESS_names))]
		
		logger.debug("+++++++++++++++++++++++++++++++++++++++++++")
		flag_is_charging_station = self.input.is_Charging_Station_in_Topology(self.topology)
		logger.debug("Charging station flag " + str(flag_is_charging_station))
		charger_residential_list = []
		charger_commercial_list = []
		charger_list_without_control = []
		soc_list_evs_residential = None
		soc_list_evs_commercial = None
		soc_list_new_evs = []
		soc_list_new_storages = []
		EV_names = []
		EV_position = []

		chargers= None
		if flag_is_charging_station:
			chargers = self.sim.get_chargers()
			
			list_node_charging_station_without_storage = self.input.get_list_nodes_charging_station_without_storage(
				self.topology, chargers)
			logger.debug(
				"list_node_charging_station_without_storage " + str(list_node_charging_station_without_storage))
			

			for key, charger_element in chargers.items():
				logger.debug("charger_element.get_bus_name() " + str(charger_element.get_bus_name()))
				
				if charger_element.get_type_application() == "residential" and not charger_element.get_bus_name() in list_node_charging_station_without_storage:
					charger_residential_list.append(charger_element)
				elif charger_element.get_type_application() == "commercial" and not charger_element.get_bus_name() in list_node_charging_station_without_storage:
					charger_commercial_list.append(charger_element)
				else:
					charger_list_without_control.append(charger_element)
				
				evs_connected = charger_element.get_EV_connected()
				
				for ev_unit in evs_connected:
					ev_unit.calculate_position(self.sim_hours, 1)
					EV_names.append("ESS_" + ev_unit.get_id())
					EV_position.append({ev_unit.get_id(): ev_unit.get_position_profile()})
					logger.debug(
						"position profile for " + str(ev_unit.get_id()) + ": " + str(ev_unit.get_position_profile()))
			
			logger.debug("EV_names " + str(EV_names))
			soc_from_EV = [[] for i in range(len(EV_names))]
			ev_powers = [[] for i in range(len(EV_names))]
			
			logger.debug("residential list " + str(charger_residential_list))
			logger.debug("commercial list " + str(charger_commercial_list))
			logger.debug("charger without control list " + str(charger_list_without_control))
			
			if not charger_residential_list == []:
				soc_list_evs_residential = self.input.get_soc_list_evs(self.topology, charger_residential_list)
				logger.debug("soc_list_evs residential" + str(soc_list_evs_residential))
			
			if not charger_commercial_list == []:
				soc_list_evs_commercial = self.input.get_soc_list_evs(self.topology, charger_commercial_list)
				logger.debug("soc_list_evs commercial" + str(soc_list_evs_commercial))

		pv_objects_alone = []
		if not chargers == None:
			pv_objects_alone = self.input.get_list_pvs_alone(self.topology, PV_objects_dict, chargers)
		else:
			pv_objects_alone = self.input.get_list_pvs_alone(self.topology, PV_objects_dict)


		logger.debug("+++++++++++++++++++++++++++++++++++++++++++")
		if flag_is_charging_station:
			flag_is_storage = self.input.is_Storage_in_Topology_without_charging_station(self.topology, chargers)
		else:
			flag_is_storage = self.input.is_Storage_in_Topology_without_charging_station(self.topology)
		logger.debug("Storage flag: " + str(flag_is_storage))
		
		if flag_is_storage:
			soc_list = self.input.get_soc_list(self.topology)
			if isinstance(soc_list, str):
				logger.error(soc_list)
				self.Stop()

		flag_is_price_profile_needed = self.input.is_price_profile_needed(self.topology)

		flag_global_control = self.input.is_global_control_in_Storage(self.topology)
		global_profile_total = []
		logger.debug("Global control flag: " + str(flag_global_control))
		if flag_global_control:
			flag_is_price_profile_needed = True
		logger.debug("Flag price profile needed: " + str(flag_is_price_profile_needed))
		
		logger.debug("+++++++++++++++++++++++++++++++++++++++++++")


		if flag_is_price_profile_needed or flag_global_control:
			price_profile_data = self.input.get_price_profile()
			logger.debug("length price profile " + str(len(price_profile_data)))

		for i in range(numSteps):
			# time.sleep(0.1)
			logger.info("#####################################################################")
			logger.info("loop  numSteps, i= " + str(i))
			hours = self.sim.getStartingHour()
			logger.info("Starting Hour : " + str(hours))
			logger.info("#####################################################################")
			
			self.redisDB.set("timestep_" + str(self.id), i)
			logger.debug("status key "+str(self.redisDB.get(self.finish_status_key)))
			if self.redisDB.get(self.finish_status_key) == "True":
				logger.debug("Setting finish_status_key as True")
				self.Stop()

			# terminal=self.sim.get_monitor_terminals("mon_transformer")
			# logger.debug("Number of terminals in monitor "+str(terminal))
			
			######################################################################################
			################  Flag control  ###################################################
			######################################################################################
			try:
				logger.debug("flag_is_storage "+str(flag_is_storage))
				logger.debug("flag_is_charging_station "+str(flag_is_charging_station))
				if flag_is_PV:
					pv_profiles = self.sim.getProfessLoadschapesPV(hours, 24)

				if flag_is_storage or flag_is_charging_station:
					load_profiles = self.sim.getProfessLoadschapes(hours, 24)


					if flag_is_price_profile_needed or flag_global_control:
						if self.input.is_price_profile():
							price_profile = price_profile_data[int(hours):int(hours + 24)]
							logger.debug("price profile present")

					if flag_is_charging_station:
						soc_list_new_evs = self.input.set_new_soc_evs(soc_list_evs_commercial, soc_list_evs_residential,
																	  chargers)
					if flag_is_storage:
						logger.debug("Entered to soc_new_list_storages")
						soc_list_new_storages = self.input.set_new_soc(soc_list)

					if flag_global_control:
						logger.debug("Global control present")
						soc_list_new_total = soc_list_new_evs + soc_list_new_storages

						if hours == 0 or not ((hours + 1) % 24):
							logger.debug("Getting global profile")
							global_profile_total = self.global_control.gesscon(load_profiles, pv_profiles, price_profile,
																			   soc_list_new_total)

						if not global_profile_total == [] and not global_profile_total == None:
							logger.debug("Global profile received")
							global_profile = self.input.get_profile(global_profile_total, hours, 24)
						# logger.debug("profess_global_profile "+str(profess_global_profile))

						else:
							logger.error("GESSCon didn't answer to the request")
							self.redisDB.set("status_"+ str(self.id),"Global control service missing")
							logger.error("Global control service missing")
							self.Stop()
			except Exception as e:
				logger.error(e)

			######################################################################################
			################  PV control  ###################################################
			######################################################################################
			if not pv_objects_alone == []:
				logger.debug("-------------------------------------------")
				logger.debug("Single PVs present in the simulation")
				logger.debug("-------------------------------------------")
				for pv_object in pv_objects_alone:
					if not int(hours) == 0:
						node = pv_object.get_node_base()
						voltage_R_pu = puVoltages[nodeNames.index(str(node) + ".1")]
						voltage_S_pu = puVoltages[nodeNames.index(str(node) + ".2")]
						voltage_T_pu = puVoltages[nodeNames.index(str(node) + ".3")]
						list_voltage_at_node = [voltage_R_pu, voltage_S_pu, voltage_T_pu]
						self.sim.setActivePowertoPV(pv_object, list_voltage_at_node)
					else:
						self.sim.setActivePowertoPV(pv_object)


			######################################################################################
			################  Storage control  ###################################################
			######################################################################################
			if flag_is_storage:
				logger.debug("-------------------------------------------")
				logger.debug("storages present in the simulation")
				logger.debug("-------------------------------------------")
				
				if flag_global_control:
					# logger.debug("price profile " + str(price_profile))
					logger.debug("global profile "+str(global_profile))
					self.profess.set_up_profess(soc_list_new_storages, load_profiles, pv_profiles, price_profile,
					                            global_profile)
				elif not flag_global_control and flag_is_price_profile_needed:
					self.profess.set_up_profess(soc_list_new_storages, load_profiles, pv_profiles, price_profile)
				else:
					self.profess.set_up_profess(soc_list_new_storages, load_profiles, pv_profiles)
				
				status_profess = self.profess.start_all(soc_list_new_storages)
				
				if not status_profess:
					profess_output = self.profess.wait_and_get_output(soc_list_new_storages)
					logger.debug("output profess " + str(profess_output))
					if not profess_output == []:
						logger.debug("Optimization succeded")

						profess_result = self.input.get_powers_from_profess_output(profess_output,
						                                                           soc_list_new_storages)
						
						for element in profess_result:
							ess_name = None
							pv_name = None
							p_ess_output = None
							p_pv_output = None
							max_charging_power = None


							pv_object = None
							for key, value in element.items():
								ess_name = value["ess_name"]
								p_ess_output = value["P_ESS_Output"]
								pv_name = value["pv_name"]
								p_pv_output = value["P_PV_Output"]
								pv_object = PV_objects_dict[pv_name]
								control_strategy_object = pv_object.get_control_strategy().get_strategy()
								control_strategy_object.set_control_power(p_pv_output)
								max_charging_power = value["max_charging_power"]
								max_discharging_power = value["max_discharging_power"]
							
							logger.debug("p_ess: " + str(p_ess_output) + " p_pv: " + str(p_pv_output))
							self.sim.setActivePowertoBatery(ess_name, p_ess_output, max_charging_power)

							if not int(hours) == 0:
								node = pv_object.get_node_base()
								voltage_R_pu = puVoltages[nodeNames.index(str(node) + ".1")]
								voltage_S_pu = puVoltages[nodeNames.index(str(node) + ".2")]
								voltage_T_pu = puVoltages[nodeNames.index(str(node) + ".3")]
								list_voltage_at_node = [voltage_R_pu, voltage_S_pu, voltage_T_pu]
								self.sim.setActivePowertoPV(pv_object, list_voltage_at_node)
							else:
								self.sim.setActivePowertoPV(pv_object)


							soc_from_profess[ESS_names.index(ess_name)].append(self.sim.getSoCfromBattery(ess_name))
							ess_powers_from_profess[ESS_names.index(ess_name)].append(p_ess_output)
					else:
						logger.error("OFW returned empty values")
						self.Stop()
				else:
					logger.error("OFW instances could not be started")
					self.Stop()
				
				if hours == (self.sim_hours - 1):
					self.profess.erase_all_ofw_instances(soc_list_new_storages)

			else:
				logger.debug("-------------------------------------------")
				logger.debug("No storages present in the simulation")
				logger.debug("-------------------------------------------")
			
			######################################################################################
			################  Charging station control  ###################################################
			######################################################################################

			if flag_is_charging_station:
				logger.debug("-------------------------------------------")
				logger.debug("charging stations present in the simulation")
				logger.debug("-------------------------------------------")
				
				for key, charger_element in chargers.items():
					evs_connected = charger_element.get_EV_connected()
					
					for ev_unit in evs_connected:
						position_profile = ev_unit.get_position_profile(hours, 1)
						logger.debug("-------------------------------------------")
						logger.debug("position profile: " + str(position_profile))
						# logger.debug("position profile for " + str(ev_unit.get_id()) + ": " + str(
						# ev_unit.get_position_profile()))
						logger.debug("-------------------------------------------")
						if position_profile[0] == 1:
							# EV connected to the grid
							charger_element.set_ev_plugged(ev_unit)
							
							name = "Line_" + ev_unit.get_id()
							self.sim.set_switch(name, False)
							
							element_id = "ESS_" + ev_unit.get_id()
							SoC = float(self.sim.getSoCfromBattery(element_id))
							ev_unit.set_SoC(SoC)
							logger.debug(str(ev_unit.get_id()) + " SoC: " + str(ev_unit.get_SoC()))
						
						else:
							charger_element.set_ev_plugged(None)
							
							name = "Line_" + ev_unit.get_id()
							self.sim.set_switch(name, True)
							
							logger.debug(str(ev_unit.get_id()) + " SoC: " + str(ev_unit.get_SoC()))
							number_km_driven = int(random.uniform(0, 6))
							logger.debug("km driven " + str(number_km_driven))
							SoC = ev_unit.calculate_S0C_next_timestep(-1, number_km_driven)
							ev_unit.set_SoC(SoC)
							logger.debug(str(ev_unit.get_id()) + " SoC: " + str(ev_unit.get_SoC()))
							element_id = "ESS_" + ev_unit.get_id()
							self.sim.setSoCBattery(element_id, SoC)
				
				if not soc_list_new_evs == []:
					
					if flag_global_control:
						self.profev.set_up_profev(soc_list_new_evs, load_profiles, pv_profiles, price_profile,
						                          global_profile, chargers=chargers)
					elif not flag_global_control and flag_is_price_profile_needed:
						self.profev.set_up_profev(soc_list_new_evs, load_profiles, pv_profiles, price_profile, None,
						                          chargers=chargers)
					else:
						self.profev.set_up_profev(soc_list_new_evs, load_profiles, pv_profiles, None, None,
						                          chargers=chargers)
					parallel = True
					if parallel:
						logger.debug("Starting parallel")

						status_profev = self.profev.start_all(soc_list_new_evs, chargers)
						
						if not status_profev:
							logger.debug("Optimization succeded")
							profev_output = self.profev.wait_and_get_output(soc_list_new_evs)
							logger.debug("profev output " + str(profev_output))
							if profev_output == []:
								logger.error("OFW instances sent and empty response")
								self.Stop()

							chargers = self.sim.get_chargers()
							for key, charger_element in chargers.items():
								evs_connected = charger_element.get_EV_connected()
								
								for ev_unit in evs_connected:
									
									p_ev, p_ess, p_pv = self.input.get_powers_from_profev_output(profev_output,
									                                                             charger_element,
									                                                             ev_unit)
									
									logger.debug("p_ev " + str(p_ev) + " p_ess: " + str(p_ess) + " p_pv: " + str(p_pv))
									if not p_ev == None:
										element_id = "ESS_" + ev_unit.get_id()
										self.sim.setActivePowertoBatery(element_id,
										                                -1 * p_ev,
										                                charger_element.get_max_charging_power())
										soc_from_EV[EV_names.index(element_id)].append(
											self.sim.getSoCfromBattery(element_id))
										ev_powers[EV_names.index(element_id)].append(p_ev)
									else:
										logger.error("Problems for finding EV name of node " + str(
											charger_element.get_bus_name()))
									
									ess_name, max_charging_power = self.input.get_ESS_name_for_node(soc_list_new_evs,
									                                                                charger_element.get_bus_name())
									if not ess_name == None and not max_charging_power == None:
										self.sim.setActivePowertoBatery(ess_name, p_ess, max_charging_power)
										soc_from_profess[ESS_names.index(ess_name)].append(
											self.sim.getSoCfromBattery(ess_name))
										ess_powers_from_profess[ESS_names.index(ess_name)].append(p_ess)
									else:
										logger.error("Problems for finding storage name of node " + str(
											charger_element.get_bus_name()))
									
									pv_name = self.input.get_PV_name_for_node(soc_list_new_evs,
									                                          charger_element.get_bus_name())
									if not pv_name == None:
										pv_object = PV_objects_dict[pv_name]
										control_strategy_object = pv_object.get_control_strategy().get_strategy()
										control_strategy_object.set_control_power(p_pv)
										if not int(hours) == 0:
											node = pv_object.get_node_base()
											voltage_R_pu = puVoltages[nodeNames.index(str(node) + ".1")]
											voltage_S_pu = puVoltages[nodeNames.index(str(node) + ".2")]
											voltage_T_pu = puVoltages[nodeNames.index(str(node) + ".3")]
											list_voltage_at_node = [voltage_R_pu, voltage_S_pu, voltage_T_pu]
											self.sim.setActivePowertoPV(pv_object, list_voltage_at_node)
										else:
											self.sim.setActivePowertoPV(pv_object)

									else:
										logger.error("Problems for finding PV name of node " + str(
											charger_element.get_bus_name()))


						else:
							logger.error("OFW instances could not be started")
							self.Stop()
					
					else:
						logger.debug("Starting serial")
						profev_output = []
						node_name_list = self.profev.json_parser.get_node_name_list(soc_list_new_evs)
						
						for node_name in node_name_list:
							instance = []
							for element in soc_list_new_evs:
								for node, data in element.items():
									if node == node_name:
										instance.append(element)
							# logger.debug("instance "+str(instance))
							
							status_profev = self.profev.start_all(instance, chargers)
							
							if not status_profev:
								logger.debug("Optimization succeded")
								profev_output_partial = self.profev.wait_and_get_output(instance)
								# logger.debug("profev output partial " + str(profev_output_partial))
								if len(profev_output_partial) > 0:
									profev_output.append(profev_output_partial[0])
						# logger.debug("profev output " + str(profev_output))
						
						if not profev_output == []:
							chargers = self.sim.get_chargers()
							for key, charger_element in chargers.items():
								evs_connected = charger_element.get_EV_connected()
								
								for ev_unit in evs_connected:
									
									p_ev, p_ess, p_pv = self.input.get_powers_from_profev_output(profev_output,
									                                                             charger_element,
									                                                             ev_unit)
									
									logger.debug("p_ev " + str(p_ev) + " p_ess: " + str(p_ess) + " p_pv: " + str(p_pv))
									if not p_ev == None:
										element_id = "ESS_" + ev_unit.get_id()
										self.sim.setActivePowertoBatery(element_id,
										                                -1 * p_ev,
										                                charger_element.get_max_charging_power())
										soc_from_EV[EV_names.index(element_id)].append(
											self.sim.getSoCfromBattery(element_id))
										ev_powers[EV_names.index(element_id)].append(p_ev)
									else:
										logger.error("Problems for finding EV name of node " + str(
											charger_element.get_bus_name()))
									
									ess_name, max_charging_power = self.input.get_ESS_name_for_node(soc_list_new_evs,
									                                                                charger_element.get_bus_name())
									if not ess_name == None and not max_charging_power == None:
										self.sim.setActivePowertoBatery(ess_name, p_ess, max_charging_power)
										soc_from_profess[ESS_names.index(ess_name)].append(
											self.sim.getSoCfromBattery(ess_name))
										ess_powers_from_profess[ESS_names.index(ess_name)].append(p_ess)
									else:
										logger.error("Problems for finding storage name of node " + str(
											charger_element.get_bus_name()))
									
									pv_name = self.input.get_PV_name_for_node(soc_list_new_evs,
									                                          charger_element.get_bus_name())
									if not pv_name == None:
										pv_object = PV_objects_dict[pv_name]
										control_strategy_object = pv_object.get_control_strategy().get_strategy()
										control_strategy_object.set_control_power(p_pv)
										if not int(hours) == 0:
											node = pv_object.get_node_base()
											voltage_R_pu = puVoltages[nodeNames.index(str(node) + ".1")]
											voltage_S_pu = puVoltages[nodeNames.index(str(node) + ".2")]
											voltage_T_pu = puVoltages[nodeNames.index(str(node) + ".3")]
											list_voltage_at_node = [voltage_R_pu, voltage_S_pu, voltage_T_pu]
											self.sim.setActivePowertoPV(pv_object, list_voltage_at_node)
										else:
											self.sim.setActivePowertoPV(pv_object)

									else:
										logger.error("Problems for finding PV name of node " + str(
											charger_element.get_bus_name()))
						
						else:
							logger.error("OFW instances sent and empty response")
							self.Stop()
				
				if not charger_list_without_control == []:
					
					chargers = self.sim.get_chargers()
					for key, charger_element in chargers.items():
						evs_connected = charger_element.get_EV_connected()
						
						for ev_unit in evs_connected:
							position_profile = ev_unit.get_position_profile(hours, 1)
							logger.debug("position profile: " + str(position_profile))
							if position_profile[0] == 1:
								# EV connected to the grid
								charger_element.set_ev_plugged(ev_unit)
								name = "Line_" + ev_unit.get_id()
								self.sim.set_switch(name, False)
								element_id = "ESS_" + ev_unit.get_id()
								SoC = float(self.sim.getSoCfromBattery(element_id))
								ev_unit.set_SoC(SoC)
								logger.debug(str(ev_unit.get_id()) + " SoC: " + str(ev_unit.get_SoC()))
								
								self.sim.setActivePowertoBatery(element_id,
								                                -1 * charger_element.get_max_charging_power(),
								                                charger_element.get_max_charging_power())
							
							else:
								# EV not connected. Calculate EV SoC
								name = "Line_" + ev_unit.get_id()
								self.sim.set_switch(name, True)
								logger.debug(str(ev_unit.get_id()) + " SoC: " + str(ev_unit.get_SoC()))
								number_km_driven = int(random.uniform(0, 6))
								logger.debug("km driven " + str(number_km_driven))
								SoC = ev_unit.calculate_S0C_next_timestep(-1, number_km_driven)
								ev_unit.set_SoC(SoC)
								element_id = "ESS_" + ev_unit.get_id()
								self.sim.setSoCBattery(element_id, SoC)
							# logger.debug(str(ev_unit.get_id()) + " SoC: " + str(ev_unit.get_SoC()))


				if hours == (self.sim_hours - 1):
					if not soc_list_evs_commercial == None:
						self.profev.erase_all_ofw_instances(soc_list_evs_commercial)
					if not soc_list_evs_residential == None:
						self.profev.erase_all_ofw_instances(soc_list_evs_residential)
			else:
				logger.debug("-------------------------------------------")
				logger.debug("No charging stations present in the simulation")
				logger.debug("-------------------------------------------")



			puVoltages, Currents, Losses = self.sim.solveCircuitSolution()


			Currents = self.sim.get_line_magnitude_currents()


			tot_losses = self.sim.get_total_losses()
			total_losses.append(str(complex(tot_losses[0], tot_losses[1])))

			for i in range(len_nodeNames):
				voltages[i].append(puVoltages[i])
			
			for i in range(len_elementNames):
				number = int(i + (len_elementNames))
				losses[i].append(str(complex(Losses[i], Losses[number])))
			
			for i in range(len_lineNames):
				currents[i].append(Currents[i])


			if not len_loadNames == 0:
				Trafo_powers = self.sim.get_trafo_powers()
				for i in range(len_transformerNames):
					trafo_powers_phase_1[i].append(Trafo_powers[i][0])
					trafo_powers_phase_2[i].append(Trafo_powers[i][1])
					trafo_powers_phase_3[i].append(Trafo_powers[i][2])

			if not len_loadNames == 0:
				Load_powers = self.sim.get_load_powers()
				for i in range(len_loadNames):
					load_powers_phase_1[i].append(Load_powers[i][0])
					load_powers_phase_2[i].append(Load_powers[i][1])
					load_powers_phase_3[i].append(Load_powers[i][2])

			if not len_pvNames == 0:
				PV_powers = self.sim.get_pv_powers()
				for i in range(len_pvNames):
					pv_powers_phase_1[i].append(PV_powers[i][0])
					pv_powers_phase_2[i].append(PV_powers[i][1])
					pv_powers_phase_3[i].append(PV_powers[i][2])

			if not len_essNames == 0:
				ESS_powers = self.input.get_storage_powers(essNames)
				for i in range(len_essNames):
					ess_powers_phase_1[i].append(ESS_powers[i][0])
					ess_powers_phase_2[i].append(ESS_powers[i][1])
					ess_powers_phase_3[i].append(ESS_powers[i][2])

				ESS_soc = self.input.get_storage_socs(self.topology)
				for i in range(len_essNames):
					ess_soc[i].append(ESS_soc[i])

			logger.debug("Finish timestep "+str(hours))


		logger.debug("#####################################################################################")
		
		data = {}
		data_voltages = {}
		data_currents = {}
		data_losses = {}
		raw_data = {}
		raw_data_voltages = {}
		raw_data_currents = {}
		raw_data_losses = {}
		raw_data_power = {}
		raw_data_load = {}
		
		############################### Losses ###################################
		
		for i in range(len_elementNames):
			element_group, element_name = elementNames[i].split(".", 1)
			if element_group not in raw_data_losses.keys():
				raw_data_losses[element_group] = {}
			raw_data_losses[element_group][element_name] = losses[i]
		
		for i in range(len_elementNames):
			element = [abs(complex(x)) for x in (losses[i])]
			element_group, element_name  = elementNames[i].split(".", 1)
			if element_group not in data_losses.keys():
				data_losses[element_group] = {}
			data_losses[element_group][element_name] = max(element)
		
		abs_total_losses = []
		raw_data_losses["circuit_total_losses"] = total_losses
		for element in total_losses:
			abs_total_losses.append(abs(complex(element)))
		data_losses["circuit_total_losses"] = max(abs_total_losses)

		############################### Currents ###################################
		#for i in range(len_lineNames):
			#raw_data_currents[str(lineNames[i]).lower()] = currents[i]

		data3 = {}

		for name_number in range(len_lineNames):
			element = currents[name_number]#[abs(complex(x)) for x in (currents[i])]
			len_element = len(element)
			number_phases = len(element[0])
			phase1=[]
			phase2=[]
			phase3=[]
			for i in range(len_element):
				for j in range(number_phases):
					if j == 0:
						phase1.append(element[i][j])
					elif j==1:
						phase2.append(element[i][j])
					elif j==2:
						phase3.append(element[i][j])

			key= str(lineNames[name_number]).lower()

			data3[key] = {}
			raw_data_currents[key] = {}

			if not phase1==[]:
				data3[key]["Phase 1"] = {"max": max(phase1),"min": min(phase1)}
				raw_data_currents[key]["Phase 1"]=phase1
			if not phase2 == []:
				data3[key]["Phase 2"] = {"max": max(phase2), "min": min(phase2)}
				raw_data_currents[key]["Phase 2"] = phase2
			if not phase3 == []:
				data3[key]["Phase 3"] = {"max": max(phase3), "min": min(phase3)}
				raw_data_currents[key]["Phase 3"] = phase3



		############################### Voltages ###################################
		for i in range(len(nodeNames)):
			raw_data_voltages[nodeNames[i]] = {"Voltage": voltages[i]}
			data_voltages[nodeNames[i]] = {"max": max(voltages[i]), "min": min(voltages[i])}
		
		data2 = {}
		for key, value in data_voltages.items():
			node, phase = key.split(".", 1)
			if node not in data2.keys():
				data2[node] = {}
			data2[node]["Phase " + phase] = value
			
		raw_data_voltages2 = {}
		for key, value in raw_data_voltages.items():
			value = value['Voltage']
			node, phase = key.split(".", 1)
			if node not in raw_data_voltages2.keys():
				raw_data_voltages2[node] = {}
			raw_data_voltages2[node]["Phase " + phase] = value
		###############################Max power in transformers###################################
		S_total = []
		mon_sample = []
		for i in range(len(transformer_names)):
			name_monitor = "monitor_transformer_" + str(i)
			S_total.append(self.sim.get_monitor_sample(name_monitor))

		power={}
		power["Transformer"] = {}
		raw_data_power["Transformer"] = {}
		for i in range(len(transformer_names)):
			if transformer_names[i] not in raw_data_power["Transformer"].keys():
				raw_data_power["Transformer"][transformer_names[i]]={}
			raw_data_power["Transformer"][transformer_names[i]] = {"Phase 1":[str(i) for i in trafo_powers_phase_1[i]],
			                                        "Phase 2":[str(i) for i in trafo_powers_phase_2[i]], "Phase 3":[str(i) for i in trafo_powers_phase_3[i]]}
			#raw_data_power["Transformer"][str(transformer_names[i])] = S_total[i]
			power["Transformer"][str(transformer_names[i])] = max(S_total[i])

		raw_data_power["Load"] = {}
		for i in range(len_loadNames):
			if loadNames[i] not in raw_data_power["Load"].keys():
				raw_data_power["Load"][loadNames[i]]={}
			raw_data_power["Load"][loadNames[i]] = {"Phase 1":[str(i) for i in load_powers_phase_1[i]],
			                                        "Phase 2":[str(i) for i in load_powers_phase_2[i]], "Phase 3":[str(i) for i in load_powers_phase_3[i]]}

		raw_data_power["Photovoltaic"] = {}
		for i in range(len_pvNames):
			if pvNames[i] not in raw_data_power["Photovoltaic"].keys():
				raw_data_power["Photovoltaic"][pvNames[i]] = {}
			raw_data_power["Photovoltaic"][pvNames[i]] = {"Phase 1": [str(i) for i in pv_powers_phase_1[i]],
													"Phase 2": [str(i) for i in pv_powers_phase_2[i]],
													"Phase 3": [str(i) for i in pv_powers_phase_3[i]]}

		raw_data_power["Storages"] = {}
		for i in range(len_essNames):
			if essNames[i] not in raw_data_power["Storages"].keys():
				raw_data_power["Storages"][essNames[i]] = {}
			raw_data_power["Storages"][essNames[i]] = {"Phase 1": [str(i) for i in ess_powers_phase_1[i]],
														  "Phase 2": [str(i) for i in ess_powers_phase_2[i]],
														  "Phase 3": [str(i) for i in ess_powers_phase_3[i]]}

		raw_soc = {}
		raw_soc["EVs"] = {}
		raw_data_power["EVs"] = {}
		for i in range(len(EV_names)):
			if EV_names[i] not in raw_data_power["EVs"].keys():
				raw_data_power["EVs"][EV_names[i]] = {}
			if EV_names[i] not in raw_soc["EVs"].keys():
				raw_soc["EVs"][EV_names[i]] = {}
			raw_data_power["EVs"][EV_names[i]] = ev_powers[i]
			raw_soc["EVs"][EV_names[i]] = soc_from_EV[i]

		raw_soc["Storages"] = {}
		for i in range(len_essNames):
			if essNames[i] not in raw_soc["Storages"].keys():
				raw_soc["Storages"][essNames[i]] = {}
			raw_soc["Storages"][essNames[i]] = ess_soc[i]

		raw_soc["Storages"] = {}
		for i in range(len_essNames):
			if essNames[i] not in raw_soc["Storages"].keys():
				raw_soc["Storages"][essNames[i]] = {}
			raw_soc["Storages"][essNames[i]] = ess_soc[i]

		raw_usage = {}
		raw_usage["Photovoltaic"] = {}

		for i in range(len_pvNames):
			if pvNames[i] not in raw_usage["Photovoltaic"].keys():
				raw_usage["Photovoltaic"][pvNames[i]] = {}
			for name, pv_object in PV_objects_dict.items():
				if name == pvNames[i]:
					raw_usage["Photovoltaic"][pvNames[i]] = pv_object.get_use_percent()

		data = {"voltages": data2, "currents": data3, "losses": data_losses, "powers": power}
		
		raw_data = {"voltages": raw_data_voltages2, "currents": raw_data_currents, "losses": raw_data_losses,
		            "powers": raw_data_power, "soc": raw_soc, "usage":raw_usage}


		###############################PV and ESS###################################

		raw_ess_power_profess = {}
		raw_ess_soc_profess = {}
		for i in range(len(ESS_names)):
			raw_ess_soc_profess[ESS_names[i]] = soc_from_profess[i]
			raw_ess_power_profess[ESS_names[i]] = ess_powers_from_profess[i]

		raw_ev_power_profess = {}
		raw_ev_soc_profess = {}
		for i in range(len(EV_names)):
			raw_ev_soc_profess[EV_names[i]] = soc_from_EV[i]
			raw_ev_power_profess[EV_names[i]] = ev_powers[i]


		raw_data_control = {  "ESS_SoC_profess": raw_ess_soc_profess,
		                    "ESS_power_profess": raw_ess_power_profess, "EV_SoC": raw_ev_soc_profess, "EV_power": raw_ev_power_profess, "EV_position": EV_position}
		
		result = data
		
		fname = (str(self.id)) + "_result"
		path = os.path.join("data", str(self.id), fname)
		logger.debug("Storing results in data folder")
		self.utils.store_data(path, result)
		logger.debug("Results succesfully stored")
		logger.debug("Storing raw data in data folder")
		fname_row = (str(self.id)) + "_result_raw.json"
		path = os.path.join("data", str(self.id), fname_row)
		self.utils.store_data_raw(path, raw_data)
		fname_row = (str(self.id)) + "_pv_curtailed_raw.json"
		path = os.path.join("data", str(self.id), fname_row)
		self.utils.store_data_raw(path, raw_data_control)
		logger.debug("Raw data successfully stored")
		
		end_time = time.time()
		total_time = end_time - start_time
		total_time_min = total_time / 60
		logger.debug("-------------------------------------------------------------------------------------")
		logger.info("Total simulation time: " + str(int(total_time)) + " s or " + str(
			"{0:.2f}".format(total_time_min)) + " min")
		logger.debug("-------------------------------------------------------------------------------------")
		self.Stop()
		
		logger.debug("#####################################################################################")
		logger.debug("##########################   Simulation End   #######################################")
		logger.debug("#####################################################################################")

