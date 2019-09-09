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
    response= http.put(domain+"commands/run/"+str(id),payload)
    return response.json()
def run_all(hours):
    for id in array_of_ids:
        run_simulation(id,hours)
        response = http.get(domain + "commands/status/" + str(id))
        if id !=0:
            while str(response.json()) != str(100):
                print("still running")
                time.sleep(1)
                response = http.get(domain + "commands/status/" + str(id))

        print("next started")

    output_file = open("mapping.txt", "w+")
    output_file.write(str(array_of_ids))
def change_kw_value(percentage):
    new_topology=copy.deepcopy(ref_topology)
    for element in new_topology["radials"][0]["photovoltaics"]:
        element["max_power_kW"]=element["max_power_kW"]*percentage
        #print(element["max_power_kW"])
    return new_topology
def define_all_topologies():
    percentage_list=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    percentage_list=[1]
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
    print("we plot "+str(node_infos))
    print("plotted "+str(phase))


def parse_and_plot_raw_data(file_name):
    for element in file_name['voltages']:
        splitted = element.split(".", 1)[0]
        if splitted in get_relevant_nodes():
            print(file_name["voltages"][element])
            plot_node(file_name["voltages"][element]["Voltages"],element)

    plt.ylabel('Voltage [pu]')
    plt.xlabel("Time [hours]")
    plt.show()

def iterate_through_profiles(directory_in_str,linecount,number_of_files):
    directory = os.fsencode(directory_in_str)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        number_and_txt=filename.split("_")[1]
        number=number_and_txt.split(".")[0]
        print(number)
        if int(number)<number_of_files:
            plot_profile(directory_in_str,filename,linecount)
    plt.ylabel('Load power [Percentage of Max Power]')
    plt.xlabel("Time [hours]")
    plt.legend()
    plt.show()
    plt.savefig("load_profiles.png")
def plot_profile(directory_in_str,filename,linecount):
    if filename.endswith(".txt") or filename.endswith(".py"):
        print("we got here with " + filename)
        count = 0
        output_profile = []
        for line in open(directory_in_str + "/" + filename):
            if count < linecount or linecount==-1:
                output_profile.append(float(line.rstrip()))
                count = count + 1
        print(output_profile)
        plot_node(output_profile, filename)

def plot_node_in_every_test(path,node_name):
    plt.figure(figsize=(10,10))
    
    mapping_file = open(path+'mapping.txt').read()
    mapping=parse_mapping(mapping_file)
    print(mapping)
    percentage=0
    for result_id in mapping:
        path_of_results=path+result_id+"/"+result_id+"_result_raw.json"
        flag_list=[False]*len(get_relevant_nodes())
        result_file=open(path_of_results).read()
        file_name=yaml.load(result_file)
        for element in file_name['voltages']:
            splitted = element.split(".", 1)[0]
            if splitted ==node_name and not flag_list[get_relevant_nodes().index(splitted)]:
                flag_list[get_relevant_nodes().index(splitted)]=True
                average_over_phases=(calculate_average_of_phase(file_name["voltages"][splitted+".1"]["Voltage"],
                                                 file_name["voltages"][splitted+".2"]["Voltage"],
                                                 file_name["voltages"][splitted+".3"]["Voltage"]))
                time=len(average_over_phases)
                print(average_over_phases)
                plot_node(average_over_phases,str(percentage)+"%")
        percentage=percentage+10

    node_number=node_name.split("_a")[1]

    profile_path="C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential/"
    plot_profile(profile_path,"profile_"+str(node_number)+".txt",time)
    plot_pv_profile(path,time)
    plt.ylabel('Voltage [pu]')
    plt.xlabel("Time [hours]")
    plt.title(str(node_name))

    plt.legend()
    plt.savefig(node_name+".png")
    plt.show()
def calculate_average_of_phase(phase1,phase2,phase3):
    output_list= []
    for index in range(len(phase1)):
        added=phase1[index]+phase2[index]+phase3[index]
        added=added/3
        output_list.append(added)
    return output_list
def plot_pv_profile(path,time):
    mapping_file = open(path+'mapping.txt').read()
    mapping=parse_mapping(mapping_file)
    ##########
    for result_id in mapping:
        pv_file = open(path + result_id + "/" + result_id + "_pv_result").read()
        PV_loadshapes = json.loads(pv_file)
        flag_plotted=False
        for PV in PV_loadshapes:
            if not flag_plotted:
                print("fitting pv " + PV)
                loadshape = PV_loadshapes[PV]["loadshape"]
                if time != -1:
                    shape_to_plot=loadshape[:time]
                else:
                    shape_to_plot = loadshape
                plot_node(shape_to_plot," PV_profile")
                flag_plotted=True
            # plt.plot(loadshape[15])
    ##############
#define_all_topologies()

#print(array_of_ids)
#print(get_relevant_nodes())
#print(get_overall_min_max(get_result_information(resultJson)))
#run_all(96)
#print(array_of_ids)

#iterate_result("PVTest/")
#file=open("4a88bbde8854_result_raw.json").read()
file=open("PvProfile/result_pv.txt").read()

file_json=yaml.load(file)
#plt.plot(file_json[:48])
#iterate_through_profiles("C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential",48)

#iterate_through_profiles("C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential",96,20)

plot_node_in_every_test("PVTest/","node_a12")
excluded=[0,7,12,13,19]
# for i in range(25):
#     if i not in excluded:
#         plot_profile("C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential","profile_"+str(i)+".txt",48)



#file_json2=json.loads(file_json)
#file_json3=json.loads(file_json2)
#print(type(file_json3))
#parse_raw_data(file_json)