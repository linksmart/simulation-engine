from profess.Http_commands import Http_commands
import json
import copy
import time
domain = "http://localhost:9090/se/"
dummyInputData = open('PVgrid.json').read()
ref_topology=json.loads(dummyInputData)
array_of_ids=[0]*10

http = Http_commands()


def post_topology(topology):
    response = http.post(domain + "simulation", topology, "json")
    return response.json()
def run_simulation(id,hours):
    payload={"sim_duration_in_hours":hours
}
    response= http.put(domain+"commands/run/"+id,payload)
    return response.json()
def run_all(hours):
    for id in array_of_ids:
        run_simulation(id,hours)
        time.sleep(10)
def change_kw_value(percentage):
    new_topology=copy.deepcopy(ref_topology)
    for element in new_topology["radials"][0]["photovoltaics"]:
        element["max_power_kW"]=element["max_power_kW"]*percentage
        print(element["max_power_kW"])
    return new_topology
def define_all_topologies():
    percentage_list=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    for percentage in percentage_list:
        new_topology=change_kw_value(percentage)
        index=percentage_list.index(percentage)
        print(index)
        array_of_ids[index-1]=post_topology(new_topology)


define_all_topologies()
print(array_of_ids)
run_all(48)