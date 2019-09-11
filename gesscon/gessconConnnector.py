import datetime
import logging
import json
import numpy as np
from data_management.utils import Utils

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
from gesscon.MQTTClient import MQTTClient

class GESSCon():
	def __init__(self):
		self.soc_nodes = ""
		self.soc_ids = ""
		self.utils = Utils()
		
	def get_ESS_data_format(self, storage):
		"""
		returns ESS data in the following format:
		{'633': {'id':"name", 'SoC': 0.4, 'Battery_Capacity':70, 'max_charging_power':33, 'max_discharging_power':33}},
		{'671': {'id':"name", 'SoC': 0.4, 'Battery_Capacity':70, 'max_charging_power':33, 'max_discharging_power':33}}]
		"""
		ess_data_list = []
		storage = storage["storageUnits"]
		for ess in storage:
			ess_data = {}
			data = {}
			data['id'] = ess['id']
			data['SoC'] = ess['soc']
			data['Battery_Capacity'] = ess['kwh_rated']
			data['max_charging_power'] = ess['pcmax']
			data['max_discharging_power'] = ess['pdmax']
			ess_data[ess['bus1']] = data
			ess_data_list.append(ess_data)
		logger.debug("ESS Data= %s", ess_data_list)
		return ess_data_list
		
	def aggregate(self, data_list):
		"""
			Calculates the aggregate values of load and pv.
			Args:
				load/pv(list): load/pv profile per node
			Returns:
				list: aggregated profile(list of 24 values)
			"""
		aggregate_list = []
		for data in data_list:
			data_id = list(data.keys())
			data_values = data[data_id[0]]
			if (isinstance(data_values, dict)):
				agg_list = []
				for val in data_values:
					agg_list.append(np.square(data_values[val]))
				aggregate = [sum(x) for x in zip(*agg_list)]
				aggregate_list.append(list(np.sqrt(aggregate)))
		aggregate_list = [sum(x) for x in zip(*aggregate_list)]
		logger.debug("Aggregated data = %s ", aggregate_list)
		return aggregate_list
	
	# def aggregated_load(self, load_list):
	# 	aggregate_list = []
	# 	for load in load_list:
	# 		load_ids = list(load.keys())
	# 		load_values = load[load_ids[0]]
	# 		if (isinstance(load_values, list)):
	# 			agg_list = []
	# 			aggregate = [0]*24
	# 			for val in load_values:
	# 				agg_list = (list(val.values())[0])
	# 				aggregate = [x + y**2 for x, y in zip(aggregate, agg_list)]
	# 			aggregate_list.append(list(np.sqrt(aggregate)))
	# 	aggregate_list = [sum(x) for x in zip(*aggregate_list)]
	# 	logger.info("Load data = %s ", aggregate_list)
	# 	return aggregate_list
	
	def create_tele_config(self, Soc):
		soc_values = {}
		len_soc = len(Soc)
		b_max = []
		pc_max = []
		pd_max = []
		soc_nodes = []
		soc_ids = []
		for s in (Soc):
			soc_value = {}
			soc_node = list(s.keys())[0]
			soc_nodes.append(soc_node)
			soc_ids.append(s[soc_node]['id'])
			soc_value["SoC"] = s[soc_node]['SoC']
			soc_values[soc_node] = soc_value
			b_max.append(s[soc_node]['Battery_Capacity'])
			pc_max.append(s[soc_node]['max_charging_power'])
			pd_max.append(s[soc_node]['max_discharging_power'])
		self.soc_nodes = soc_nodes
		self.soc_ids = soc_ids
		tele = {"SOC": soc_values}
		config = {
			"ESS_number": len_soc,
			"tariff": 0,
			"grid_i": 1000,
			"grid_o": 1000,
			"ess_eff": [0.96] * len_soc,
			"bmax": b_max,
			"bmin": [0] * len_soc,
			"pcmax": pc_max,
			"pdmax": pd_max,
			"cycle": [0] * len_soc,
			"loss": 0
		}
		logger.debug("Soc = %s", soc_values)
		return tele, config
		
	def gesscon(self, load, pv, price, Soc, date = "2018.10.01 00:00:00"):
		"""
        Calculates the aggregate values of load and pv, publishes the payload JSON as per the given date, subscribes to another topic and
        returns the result as per the format.
        [{'633': {'id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}},
			{'671': {'id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}] .
        Args:
            load(list): load profile per node
            pv(list): pv profile per node
            price(list): price profile
            Soc: Batteries data
            date: input date with the format %Y.%m.%d %H:%M:%S. 01/10/2018 by default.

        Returns:
            list: as described above
        """
		aggregated_pv = self.aggregate(pv)
		aggregated_load = self.aggregate(load)
		tele, config = self.create_tele_config(Soc)
		
		#Creating JSON payload to be sent to GESSCon service
		elprices = []
		demand = []
		pv_list = []
		ev_list  =[]
		start_date = datetime.datetime.strptime(date, '%Y.%m.%d %H:%M:%S')
		start_date_format = datetime.datetime.fromtimestamp(start_date.timestamp()).strftime("%Y.%m.%d %H:%M:%S")
		for val in range(24):
			date = datetime.datetime.fromtimestamp(start_date.timestamp()).strftime("%Y.%m.%d %H:%M:%S")
			elprices.append({"DateTime": date, "elprice": price[val]})
			demand.append({"DateTime": date, "Loads": aggregated_load[val]})
			pv_list.append({"DateTime": date, "pv": aggregated_pv[val]})
			ev_list.append({"DateTime": date, "ev": 0.0})
			if(val == 23):
				continue
			start_date = start_date + datetime.timedelta(hours = 1)
		end_date_format = datetime.datetime.fromtimestamp(start_date.timestamp()).strftime("%Y.%m.%d %H:%M:%S")
		raw = {"elprices":elprices, "demand": demand, "pv": pv_list, "ev": ev_list}
		
		payload_var = {"site": "EDYNA-0018",
		"time_start": start_date_format,
		"time_stop": end_date_format,
		"raw": raw,
	    "tele": tele,
	    "config": config }
		payload = json.dumps(payload_var)

		logger.info("Payload: %s", payload_var)
		result= self.on_msg_received(payload)
		return result
		# MQTT
		# mqtt_send = MQTTClient("mosquito_S4G1", 1883, "gesscon_send")
		# mqtt_receive = MQTTClient("mosquito_S4G1", 1883, "gesscon_receive")
		# mqtt_receive.subscribe_to_topics([("gesscon/data",2)], self.on_msg_received)
		# logger.debug("successfully subscribed")
		#
		# mqtt_send.publish("gesscon/data", payload, True)
		# mqtt_send.MQTTExit()
		# mqtt_receive.MQTTExit()
		

	def on_msg_received(self, payload):
		# Mock Output from GESSCon
		output_list = []

		path = self.utils.get_path("gesscon/gesscon_output.json")
		with open(path, "r") as file:
			dict_data = json.load(file)
		logger.debug(dict_data)
		dict_data = dict_data['data']
		for node_data, node, id in zip(dict_data, self.soc_nodes, self.soc_ids):
			id_output = {id: node_data}
			output_node = {node: id_output}
			output_list.append(output_node)
		logger.debug(output_list)
		return output_list

#### Dummy data ####
# price = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
#
# storage = {"storageUnits": [
# 	{
# 		"id": "Akku1",
# 		"bus1": "633",
# 		"phases": 3,
# 		"connection": "wye",
# 		"soc": 0,
# 		"dod": 0,
# 		"kv": 0,
# 		"kw_rated": 0,
#
# 		"pcmax": 1,
# 		"pdmax": 2,
# 		"kwh_rated": 1,
# 		"kwh_stored": 0,
# 		"charge_efficiency": 0,
# 		"discharge_efficiency": 0,
# 		"powerfactor": 0
# 	},
# 	{
# 		"id": "Akku2",
# 		"bus1": "671",
# 		"phases": 3,
# 		"connection": "wye",
# 		"soc": 0,
# 		"dod": 0,
# 		"kv": 0,
# 		"kw_rated": 0,
#
# 		"pcmax": 3,
# 		"pdmax": 4,
# 		"kwh_rated": 10,
# 		"kwh_stored": 0,
# 		"charge_efficiency": 0,
# 		"discharge_efficiency": 0,
# 		"powerfactor": 0
# 	}
# ]}
#
# pv = [{'633':
# 	       {'633.1.2': [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0,
# 	                    0, 0, 0, 0]}},
#       {'671': {'671.1.2.3': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                              0, 0, 0, 0, 0, 0, 0, 4]}}]
#
# load = [{'633':
# {'633.1': [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 0, 0, 0, 0],
# '633.2': [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 0, 0, 0],
# '633.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 0, 0, 9]}},
# {'671': {'671.1.2.3': [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 0, 0, 0, 0, 0, 0, 0, 0]}}]



#### Dummy data ####
"""
price = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

storage = {"storageUnits": [
	{
		"id": "Akku1",
		"bus1": "633",
		"phases": 3,
		"connection": "wye",
		"soc": 0,
		"dod": 0,
		"kv": 0,
		"kw_rated": 0,
		
		"pcmax": 1,
		"pdmax": 2,
		"kwh_rated": 1,
		"kwh_stored": 0,
		"charge_efficiency": 0,
		"discharge_efficiency": 0,
		"powerfactor": 0
	},
	{
		"id": "Akku2",
		"bus1": "671",
		"phases": 3,
		"connection": "wye",
		"soc": 0,
		"dod": 0,
		"kv": 0,
		"kw_rated": 0,
		
		"pcmax": 3,
		"pdmax": 4,
		"kwh_rated": 10,
		"kwh_stored": 0,
		"charge_efficiency": 0,
		"discharge_efficiency": 0,
		"powerfactor": 0
	}
]}

pv = [{'633':
	       {'633.1.2': [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0,
	                    0, 0, 0, 0]}},
      {'671': {'671.1.2.3': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 4]}}]

load = [{'633':
{'633.1': [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0],
'633.2': [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0],
'633.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 9]}},
{'671': {'671.1.2.3': [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0]}}]
>>>>>>> origin/gustavo

# g = GESSCon()
# Soc = g.get_ESS_data_format(storage)
# g.gesscon(load, pv, price, Soc)
"""