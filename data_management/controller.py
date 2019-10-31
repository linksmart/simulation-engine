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
		# self.id = id
		# self.duration = duration
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
		if answer_setup == 1:
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
		
		# self.sim.setVoltageBases(115, 4.16, 0.48)
		self.sim.setVoltageBases(self.input.get_voltage_bases())
		# self.sim.setMode("snap")
		# self.sim.setMode("daily")
		self.sim.setMode("yearly")
		self.sim.setStepSize("hours")
		self.sim.setNumberSimulations(1)
		logger.info("Solution mode 2: " + str(self.sim.getMode()))
		logger.info("Number simulations 2: " + str(self.sim.getNumberSimulations()))
		logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
		logger.info("Voltage bases: " + str(self.sim.getVoltageBases()))
		logger.info("Starting Hour : " + str(self.sim.getStartingHour()))
		numSteps = self.sim_hours
		# self.redisDB.set("sim_days_"+str(self.id),numSteps)
		# numSteps=3
		logger.debug("Number of steps: " + str(numSteps))
		result = []
		
		nodeNames = self.sim.get_node_list()
		len_nodeNames = len(nodeNames)
		elementNames = self.sim.get_element_names()
		len_elementNames = len(elementNames)
		nodeNamesCurrents = self.sim.get_YNodeOrder()
		len_nodeNamesCurrents = len(nodeNamesCurrents)
		
		# logger.debug("node_ names "+str(nodeNames))
		voltages = [[] for i in range(len(nodeNames))]
		currents = [[] for i in range(len_nodeNamesCurrents)]
		losses = [[] for i in range(len_elementNames)]
		total_losses = []
		
		PV_names = self.input.get_PV_names(self.topology)
		logger.debug("PV_names " + str(PV_names))
		powers_pv_curtailed = [[] for i in range(len(PV_names))]
		
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
		if flag_is_charging_station:
			chargers = self.sim.get_chargers()
			
			list_node_charging_station_without_storage = self.input.get_list_nodes_charging_station_without_storage(
				self.topology, chargers)
			logger.debug(
				"list_node_charging_station_without_storage " + str(list_node_charging_station_without_storage))
			
			# logger.debug("type chargers " + str(type(chargers)))
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
		
		logger.debug("+++++++++++++++++++++++++++++++++++++++++++")
		if flag_is_charging_station:
			flag_is_storage = self.input.is_Storage_in_Topology_without_charging_station(self.topology, chargers)
		else:
			flag_is_storage = self.input.is_Storage_in_Topology_without_charging_station(self.topology)
		logger.debug("Storage flag: " + str(flag_is_storage))
		
		if flag_is_storage:
			soc_list = self.input.get_soc_list(self.topology)

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
			################  Storage control  ###################################################
			######################################################################################
			try:
				if flag_is_storage or flag_is_charging_station:
					load_profiles = self.sim.getProfessLoadschapes(hours, 24)
					#logger.debug("loads "+str(load_profiles))
					pv_profiles = self.sim.getProfessLoadschapesPV(hours, 24)
					# logger.debug("PVs "+str(professPVs))
					if flag_is_price_profile_needed or flag_global_control:
						if self.input.is_price_profile():
							# logger.debug("price profile present")
							price_profile = price_profile_data[int(hours):int(hours + 24)]
							logger.debug("price profile present")

					if flag_is_charging_station:
						soc_list_new_evs = self.input.set_new_soc_evs(soc_list_evs_commercial, soc_list_evs_residential,
																	  chargers)
					# logger.debug("soc_list_new_evs " + str(soc_list_new_evs))

					if flag_is_storage:
						soc_list_new_storages = self.input.set_new_soc(soc_list)
					# logger.debug("soc_list_new_storages " + str(soc_list_new_storages))

					# soc_list_new_total = soc_list_new_evs + soc_list_new_storages
					# logger.debug("soc_list_new_total: " + str(soc_list_new_total))

					if flag_global_control:
						logger.debug("Trying to get global profile")
						soc_list_new_total = soc_list_new_evs + soc_list_new_storages
						#logger.debug("soc_list_new_total: "+str(soc_list_new_total))

						if not ((hours + 1) % 24):
							global_profile_total = self.global_control.gesscon(load_profiles, pv_profiles, price_profile,
																			   soc_list_new_total)


						if not global_profile_total == []:
							logger.debug("Global profile received")
							global_profile = self.input.get_profile(global_profile_total, hours, 24)
						# logger.debug("profess_global_profile "+str(profess_global_profile))

						else:
							logger.error("GESSCon didn't answer to the request")
			except Exception as e:
				logger.error(e)

			logger.debug("status key " + str(self.redisDB.get(self.finish_status_key)))
			if flag_is_storage:
				logger.debug("-------------------------------------------")
				logger.debug("storages present in the simulation")
				logger.debug("-------------------------------------------")
				
				if flag_global_control:
					# logger.debug("price profile " + str(price_profile))
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
						# output syntax from profess[{node_name: {profess_id: {'P_ESS_Output': value, ...}}, {node_name2: {...}]
						# soc list: [{'node_a15': {'SoC': 60.0, 'id': 'Akku1', 'Battery_Capacity': 3, 'max_charging_power': 1.5, 'max_discharging_power': 1.5}}, {'node_a6': {'SoC': 40.0, 'id': 'Akku2', 'Battery_Capacity': 3, 'max_charging_power': 1.5, 'max_discharging_power': 1.5}}]
						
						profess_result = self.input.get_powers_from_profess_output(profess_output,
						                                                           soc_list_new_storages)
						#logger.debug("profess result: "+str(profess_result))
						
						for element in profess_result:
							ess_name = None
							pv_name = None
							p_ess_output = None
							p_pv_output = None
							max_charging_power = None
							for key, value in element.items():
								ess_name = value["ess_name"]
								p_ess_output = value["P_ESS_Output"]
								pv_name = value["pv_name"]
								p_pv_output = value["P_PV_Output"]
								max_charging_power = value["max_charging_power"]
								max_discharging_power = value["max_discharging_power"]
							
							logger.debug("p_ess: " + str(p_ess_output) + " p_pv: " + str(p_pv_output))
							self.sim.setActivePowertoBatery(ess_name, p_ess_output, max_charging_power)
							self.sim.setActivePowertoPV(pv_name, p_pv_output)
							#### Creating lists for storing values
							powers_pv_curtailed[PV_names.index(pv_name)].append(p_pv_output)
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
				logger.debug("No Storage Units present")
			
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
										self.sim.setActivePowertoPV(pv_name, p_pv)
										powers_pv_curtailed[PV_names.index(pv_name)].append(p_pv)
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
										self.sim.setActivePowertoPV(pv_name, p_pv)
										powers_pv_curtailed[PV_names.index(pv_name)].append(p_pv)
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
				logger.debug("No charging stations present in the simulation")


			puVoltages, Currents, Losses = self.sim.solveCircuitSolution()
			tot_losses = self.sim.get_total_losses()
			
			for i in range(len_nodeNames):
				voltages[i].append(puVoltages[i])
			
			for i in range(len_elementNames):
				number = int(i + (len_elementNames))
				losses[i].append(str(complex(Losses[i], Losses[number])))
			
			for i in range(len_nodeNamesCurrents):
				currents[i].append(str(complex(Currents[i], Currents[int(i + (len_nodeNamesCurrents))])))
			
			total_losses.append(str(complex(tot_losses[0], tot_losses[1])))
			logger.debug("Finish timestep "+str(hours))
		
		# logger.debug("volt finish "+str(voltages))
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
		
		############################### Losses ###################################
		
		for i in range(len_elementNames):
			raw_data_losses[elementNames[i]] = losses[i]
		
		for i in range(len_elementNames):
			element = [abs(complex(x)) for x in (losses[i])]
			data_losses[elementNames[i]] = max(element)
		
		abs_total_losses = []
		raw_data_losses["circuit_total_losses"] = total_losses
		for element in total_losses:
			abs_total_losses.append(abs(complex(element)))
		data_losses["circuit_total_losses"] = max(abs_total_losses)
		
		# logger.debug("total_losses " + str(total_losses))
		# data_losses
		############################### Currents ###################################
		for i in range(len_nodeNamesCurrents):
			raw_data_currents[str(nodeNamesCurrents[i]).lower()] = currents[i]
		
		for i in range(len_nodeNamesCurrents):
			element = [abs(complex(x)) for x in (currents[i])]
			key = nodeNamesCurrents[i]
			data_currents[key] = max(element)
		
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
			data_voltages[nodeNames[i]] = {"max": max(voltages[i]), "min": min(voltages[i])}
		
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
			name_monitor = "monitor_transformer_" + str(i)
			# logger.debug("i in sample monitor "+str(i)+" "+str(name_monitor))
			S_total.append(self.sim.get_monitor_sample(name_monitor))
		
		power = {}
		for i in range(len(transformer_names)):
			raw_data_power[transformer_names[i]] = S_total[i]
			power["Transformer." + str(transformer_names[i])] = max(S_total[i])
		# logger.debug("power "+str(power))
		data = {"voltages": data2, "currents": data3, "losses": data_losses, "powers": power}
		
		raw_data = {"voltages": raw_data_voltages, "currents": raw_data_currents, "losses": raw_data_losses,
		            "powers": raw_data_power}
		
		raw_data_pv_curtailment = {}
		for i in range(len(PV_names)):
			raw_data_pv_curtailment[PV_names[i]] = powers_pv_curtailed[i]
		
		raw_ess_power = {}
		raw_ess_soc = {}
		for i in range(len(ESS_names)):
			raw_ess_soc[ESS_names[i]] = soc_from_profess[i]
			raw_ess_power[ESS_names[i]] = ess_powers_from_profess[i]
		
		raw_ev_power = {}
		raw_ev_soc = {}
		for i in range(len(EV_names)):
			raw_ev_soc[EV_names[i]] = soc_from_EV[i]
			raw_ev_power[EV_names[i]] = ev_powers[i]
		
		raw_data_control = {"pv_curtailment": raw_data_pv_curtailment, "ESS_SoC": raw_ess_soc,
		                    "ESS_power": raw_ess_power,
		                    "EV_SoC": raw_ev_soc, "EV_power": raw_ev_power, "EV_position": EV_position}
		
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

