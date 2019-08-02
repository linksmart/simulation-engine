import datetime
import logging
import requests
import json
from senml import senml
import time
import numpy as np
logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
from gesscon.MQTTClient import MQTTClient


def get_ESS_data_format(storage):
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
	logging.info("ESS Data= %s", ess_data_list)
	return ess_data_list
		

def aggregate(data_list):
	aggregate_list = []
	for data in data_list:
		data_id = list(data.keys())
		data_values = data[data_id[0]]
		if (isinstance(data_values, dict)):
			agg_list = []
			# aggregate = [0]*24
			for val in data_values:
				agg_list.append(np.square(data_values[val]))
				# aggregate = [x + y**2 for x, y in zip(aggregate, agg_list)]
			aggregate = [sum(x) for x in zip(*agg_list)]
			aggregate_list.append(list(np.sqrt(aggregate)))
	aggregate_list = [sum(x) for x in zip(*aggregate_list)]
	logger.info("PV data = %s ", aggregate_list)
	return aggregate_list

def aggregated_load(load_list):
	aggregate_list = []
	for load in load_list:
		load_ids = list(load.keys())
		load_values = load[load_ids[0]]
		if (isinstance(load_values, list)):
			agg_list = []
			aggregate = [0]*24
			for val in load_values:
				agg_list = (list(val.values())[0])
				aggregate = [x + y**2 for x, y in zip(aggregate, agg_list)]
			aggregate_list.append(list(np.sqrt(aggregate)))
	aggregate_list = [sum(x) for x in zip(*aggregate_list)]
	logger.info("Load data = %s ", aggregate_list)
	return aggregate_list

def gesscon(load, pv, price, Soc):
	pv = aggregate(pv)
	load = aggregate(load)
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
	logging.info("Soc = %s", soc_values)
	
	# elprices = []
	# demands = []
	# pv = []
	# start_date = "2018.10.01 00:00:00"
	# start_date_timestamp = datetime.datetime.strftime(start_date, "%Y.%m.%d %H:%M:%S").timestamp()
	# for val in range(24):
	# 	date = start_date_timestamp.strftime("%Y.%m.%d %H:%M:%S")
	# 	elprice = {"DateTime": date, "elprice": price[val]}
	# 	elprices.append(elprice)
	#
	payload_var = {
	"site": "EDYNA-0018",
	"time_start": "2018.10.01 00:00:00",
	"time_stop": "2018.10.01 23:00:00",
	"raw": {
				"elprices": [{
					"DateTime": "2018.10.01 00:00:00",
					"elprice": price[0]
				},
				{
					"DateTime": "2018.10.01 01:00:00",
					"elprice": price[1]
				},
				{
					"DateTime": "2018.10.01 02:00:00",
					"elprice": price[2]
				},
				{
					"DateTime": "2018.10.01 03:00:00",
					"elprice": price[3]
				},
				{
					"DateTime": "2018.10.01 04:00:00",
					"elprice": price[4]
				},
				{
					"DateTime": "2018.10.01 05:00:00",
					"elprice": price[5]
				},
				{
					"DateTime": "2018.10.01 06:00:00",
					"elprice": price[6]
				},
				{
					"DateTime": "2018.10.01 07:00:00",
					"elprice": price[7]
				},
				{
					"DateTime": "2018.10.01 08:00:00",
					"elprice": price[8]
				},
				{
					"DateTime": "2018.10.01 09:00:00",
					"elprice": price[9]
				},
				{
					"DateTime": "2018.10.01 10:00:00",
					"elprice": price[10]
				},
				{
					"DateTime": "2018.10.01 11:00:00",
					"elprice": price[11]
				},
				{
					"DateTime": "2018.10.01 12:00:00",
					"elprice": price[12]
				},
				{
					"DateTime": "2018.10.01 13:00:00",
					"elprice": price[13]
				},
				{
					"DateTime": "2018.10.01 14:00:00",
					"elprice": price[14]
				},
				{
					"DateTime": "2018.10.01 15:00:00",
					"elprice": price[15]
				},
				{
					"DateTime": "2018.10.01 16:00:00",
					"elprice": price[16]
				},
				{
					"DateTime": "2018.10.01 17:00:00",
					"elprice": price[17]
				},
				{
					"DateTime": "2018.10.01 18:00:00",
					"elprice": price[18]
				},
				{
					"DateTime": "2018.10.01 19:00:00",
					"elprice": price[19]
				},
				{
					"DateTime": "2018.10.01 20:00:00",
					"elprice": price[20]
				},
				{
					"DateTime": "2018.10.01 21:00:00",
					"elprice": price[21]
				},
				{
					"DateTime": "2018.10.01 22:00:00",
					"elprice": price[22]
				},
				{
					"DateTime": "2018.10.01 23:00:00",
					"elprice": price[23]
				}],
				"demand": [{
					"DateTime": "2018.10.01 00:00:00",
					"Loads": load[0]
				},
				{
					"DateTime": "2018.10.01 01:00:00",
					"Loads": load[1]
				},
				{
					"DateTime": "2018.10.01 02:00:00",
					"Loads": load[2]
				},
				{
					"DateTime": "2018.10.01 03:00:00",
					"Loads": load[3]
				},
				{
					"DateTime": "2018.10.01 04:00:00",
					"Loads": load[4]
				},
				{
					"DateTime": "2018.10.01 05:00:00",
					"Loads": load[5]
				},
				{
					"DateTime": "2018.10.01 06:00:00",
					"Loads": load[6]
				},
				{
					"DateTime": "2018.10.01 07:00:00",
					"Loads": load[7]
				},
				{
					"DateTime": "2018.10.01 08:00:00",
					"Loads": load[8]
				},
				{
					"DateTime": "2018.10.01 09:00:00",
					"Loads": load[9]
				},
				{
					"DateTime": "2018.10.01 10:00:00",
					"Loads": load[10]
				},
				{
					"DateTime": "2018.10.01 11:00:00",
					"Loads": load[11]
				},
				{
					"DateTime": "2018.10.01 12:00:00",
					"Loads": load[12]
				},
				{
					"DateTime": "2018.10.01 13:00:00",
					"Loads": load[13]
				},
				{
					"DateTime": "2018.10.01 14:00:00",
					"Loads": load[14]
				},
				{
					"DateTime": "2018.10.01 15:00:00",
					"Loads": load[15]
				},
				{
					"DateTime": "2018.10.01 16:00:00",
					"Loads": load[16]
				},
				{
					"DateTime": "2018.10.01 17:00:00",
					"Loads": load[17]
				},
				{
					"DateTime": "2018.10.01 18:00:00",
					"Loads": load[18]
				},
				{
					"DateTime": "2018.10.01 19:00:00",
					"Loads": load[19]
				},
				{
					"DateTime": "2018.10.01 20:00:00",
					"Loads": load[20]
				},
				{
					"DateTime": "2018.10.01 21:00:00",
					"Loads": load[21]
				},
				{
					"DateTime": "2018.10.01 22:00:00",
					"Loads": load[22]
				},
				{
					"DateTime": "2018.10.01 23:00:00",
					"Loads": load[23]
				}],
				"pv": [{
					"DateTime": "2018.10.01 00:00:00",
					"pv": pv[0]
				},
				{
					"DateTime": "2018.10.01 01:00:00",
					"pv": pv[1]
				},
				{
					"DateTime": "2018.10.01 02:00:00",
					"pv": pv[2]
				},
				{
					"DateTime": "2018.10.01 03:00:00",
					"pv": pv[3]
				},
				{
					"DateTime": "2018.10.01 04:00:00",
					"pv": pv[4]
				},
				{
					"DateTime": "2018.10.01 05:00:00",
					"pv": pv[5]
				},
				{
					"DateTime": "2018.10.01 06:00:00",
					"pv": pv[6]
				},
				{
					"DateTime": "2018.10.01 07:00:00",
					"pv": pv[7]
				},
				{
					"DateTime": "2018.10.01 08:00:00",
					"pv": pv[8]
				},
				{
					"DateTime": "2018.10.01 09:00:00",
					"pv": pv[9]
				},
				{
					"DateTime": "2018.10.01 10:00:00",
					"pv": pv[10]
				},
				{
					"DateTime": "2018.10.01 11:00:00",
					"pv": pv[11]
				},
				{
					"DateTime": "2018.10.01 12:00:00",
					"pv": pv[12]
				},
				{
					"DateTime": "2018.10.01 13:00:00",
					"pv": pv[13]
				},
				{
					"DateTime": "2018.10.01 14:00:00",
					"pv": pv[14]
				},
				{
					"DateTime": "2018.10.01 15:00:00",
					"pv": pv[15]
				},
				{
					"DateTime": "2018.10.01 16:00:00",
					"pv": pv[16]
				},
				{
					"DateTime": "2018.10.01 17:00:00",
					"pv": pv[17]
				},
				{
					"DateTime": "2018.10.01 18:00:00",
					"pv": pv[18]
				},
				{
					"DateTime": "2018.10.01 19:00:00",
					"pv": pv[19]
				},
				{
					"DateTime": "2018.10.01 20:00:00",
					"pv": pv[20]
				},
				{
					"DateTime": "2018.10.01 21:00:00",
					"pv": pv[21]
				},
				{
					"DateTime": "2018.10.01 22:00:00",
					"pv": pv[22]
				},
				{
					"DateTime": "2018.10.01 23:00:00",
					"pv": pv[23]
				}],
				"ev": [{
					"DateTime": "2018.10.01 00:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 01:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 02:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 03:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 04:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 05:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 06:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 07:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 08:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 09:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 10:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 11:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 12:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 13:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 14:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 15:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 16:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 17:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 18:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 19:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 20:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 21:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 22:00:00",
					"ev": 0.0
				},
				{
					"DateTime": "2018.10.01 23:00:00",
					"ev": 0.0
				}]
			},
	"tele": {
			"SOC" : soc_values
			},
	"config": {
			"ESS_number": len_soc,
			"tariff" : 0,
			"grid_i" : 1000,
																																																																																																																							"grid_o" : 1000,
			"ess_eff" : [0.96]*len_soc,
			"bmax" : b_max,
			"bmin" : [0]*len_soc,
			"pcmax" : pc_max,
			"pdmax" : pd_max,
			"cycle" : [0]*len_soc,
			"loss" : 0
				}}
	payload = json.dumps(payload_var)
	logging.info(payload)
	m = MQTTClient("mosquito_S4G", 1883, "gesscon_send")
	m.publish("gesscon/data", payload, True)
	
	mqtt = MQTTClient("mosquito_S4G", 1883, "gesscon_receive")
	mqtt.subscribe_to_topics([("gesscon/data",2)], on_msg_received)
	logging.info("successfully subscribed")
	m.MQTTExit()
	
	output_list = []
	with open("gesscon_output.json","r") as file:
		dict_data = json.load(file)
	for node_data, node, id in zip(dict_data, soc_nodes, soc_ids):
		doc = senml.SenMLDocument.from_json(node_data)
		meas_list = []
		for meas in doc.measurements:
			meas_list.append(meas.value)
		id_output = {id : meas_list}
		output_node= {node : id_output}
		output_list.append(output_node)
	return output_list


def on_msg_received(self, payload=""):
	pass

#### Dummy data ####
price = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

pv = [{'633':
	       {'633.1.2': [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0,
	                    0, 0, 0, 0]}},
      {'671': {'671.1.2.3': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 4]}}]

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
load = [{'633':
{'633.1': [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0],
'633.2': [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0],
'633.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 9]}},
{'671': {'671.1.2.3': [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0]}}]

Soc = get_ESS_data_format(storage)
gesscon(load, pv, price, Soc)