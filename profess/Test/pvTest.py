from profess.Http_commands import Http_commands
import json
import copy
import time
import os
import yaml
import matplotlib.pyplot as plt
domain = "http://localhost:9090/se/"
dummyInputData = open('PVgrid.json').read()
ref_topology=json.loads(dummyInputData)
array_of_ids=[0]*11

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
        #print(element["max_power_kW"])
    return new_topology
def define_all_topologies():
    percentage_list=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    for percentage in percentage_list:
        new_topology=change_kw_value(percentage)
        index=percentage_list.index(percentage)
        simulation_id=post_topology(new_topology)
        array_of_ids[index]=simulation_id
def get_relevant_nodes():
    new_topology=copy.deepcopy(ref_topology)
    node_list=[]
    for element in new_topology["radials"][0]["photovoltaics"]:
        bus=element["bus1"]
        bus_name=bus.split(".",1)[0]
        node_list.append(bus_name)
    return node_list
def get_result_information(result):
    relevant_results={}
    for element in result["voltages"]:
        if element in get_relevant_nodes():
            payload=get_min_max_for_node(result["voltages"][element])
            relevant_results[element]=payload
    return relevant_results
def get_min_max_for_node(node_result):
    minimum=100
    maximum=-1
    for phase in node_result:
        if node_result[phase]["max"]>maximum:
            maximum=node_result[phase]["max"]
        if node_result[phase]["min"]<minimum:
            minimum=node_result[phase]["min"]
    return {"max":maximum,"min":minimum}
def get_overall_min_max(result):
    minimum=100
    nodeMax=""
    maximum=-1
    nodeMin=""
    for phase in result:
        if result[phase]["max"]>maximum:
            maximum=result[phase]["max"]
            nodeMax=phase
        if result[phase]["min"]<minimum:
            minimum=result[phase]["min"]
            nodeMin=phase
    return {"max":{nodeMax:maximum},"min":{nodeMin:minimum}}
def iterate_result(path):
    mapping_file = open(path+'mapping.txt').read()
    mapping=parse_mapping(mapping_file)
    print(mapping)
    percentage=0
    output_file=open("results.txt","w+")
    for result_id in mapping:

        path_of_results=path+result_id+"/"+result_id+"_result"
        result_file=open(path_of_results).read()
        resultJson=json.loads(result_file)

        print(str(percentage)+"% penetration: "+str(get_overall_min_max(get_result_information(resultJson))))
        output_file.write(str(percentage)+"% penetration: "+str(get_overall_min_max(get_result_information(resultJson)))+"\n")
        percentage = percentage + 10
    output_file.close()
def parse_mapping(mapping):
    output=[]
    splitted_map=mapping.split(",")
    for element in splitted_map:
        splitted=element.split("'",1)
        #print(element)
        test=splitted[1].strip("'")
        #print(test)
        test2=test.strip("[")
        test2 = test2.strip("]")
        #print(test2)
        test3=test2.strip("'")
        output.append(test3)

    return output

def parse_relevant_results_to_latex():
    header=""

def plot_node(node_infos,phase):
    plt.plot(node_infos,label=phase)
    print("plotted")


def parse_raw_data(file_name):
    for element in file_name['voltages']:
        splitted = element.split(".", 1)[0]
        if splitted in get_relevant_nodes():
            print(file_name["voltages"][element])
            plot_node(file_name["voltages"][element]["Voltages"],element)

    plt.ylabel('Voltage in pu')
    plt.xlabel("hours")
    plt.show()

def iterate_through_profiles(directory_in_str,linecount):
    directory = os.fsencode(directory_in_str)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".txt") or filename.endswith(".py"):
            print("we got here with "+filename)
            count=0
            output_profile=[]
            for line in open(directory_in_str+"/"+filename):
                if count<linecount:

                    output_profile.append(float(line.rstrip()))
                    count=count+1
            print(output_profile)
            plot_node(output_profile,filename)
        else:
            continue
#define_all_topologies()
#output_file=open("mapping.txt").write()
#print(array_of_ids)
#print(get_relevant_nodes())
#print(get_overall_min_max(get_result_information(resultJson)))
#run_all(48)

#iterate_result("PVTest/")
#file=open("4a88bbde8854_result_raw.json").read()
file=open("1295459c89e1_result_raw.json").read()

file_json=yaml.load(file)

iterate_through_profiles("C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential",48)
plt.ylabel('power in percentage of maximum')
plt.xlabel("hours")
plt.legend()
plt.show()
#file_json2=json.loads(file_json)
#file_json3=json.loads(file_json2)
#print(type(file_json3))
#parse_raw_data(file_json)