import json
import numpy as np
import random
def pv_generation(result, percent = 0.10, control = "no_control"):
	for radials in result['radials']:
		radials['photovoltaic'] = []
		total_power = 0
		no_of_nodes = len(radials['loads'])
		for load in radials['loads']:
			total_power += load['kW']
		# no_of_nodes += 1
		
		total_power = percent * total_power
		random_list = random.sample(range(int(total_power)), k=no_of_nodes)
		random_sum = np.sum(random_list)
		random_list = [round(i * (total_power / random_sum)) for i in random_list]
		count = 0
		for load in radials['loads']:
			pv = {}
			pv['id'] = "PV_" + load['id']
			pv['kV'] = load['kV']
			pv['phases'] = load['phases']
			bus = load['bus'].split('.')[0]
			pv['bus1'] = bus
			pv['power_profile_id'] = "pv_profile"
			pv['control'] = control
			pv['max_power_kW'] = random_list[count]
			count += 1
			radials['photovoltaic'].append(pv)
	# result['radials'].append(radials)
	with open("Result_pv.json", 'w') as file:
		json.dump(result, file, ensure_ascii=False, indent=4)

with open('Result.json') as f:
	result = json.load(f)
	print(result)

pv_generation(result, 0.1)