from profess.Http_commands import Http_commands
import json
import copy
import os
import yaml
import matplotlib.pyplot as plt
import datetime
import time
domain = "http://localhost:9090/se/"
#dummyInputData = open('topologies\PVgridTest.json').read()
dummyInputData = open('topologies\StorageGridBiggerESS.json').read()
ref_topology=json.loads(dummyInputData)
array_of_ids=[0]*11

array_of_ids = [0]

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
    start_time=time.time()
    print(str(start_time))
    define_all_topologies()
    time.sleep(10)
    for id in array_of_ids:
        run_simulation(id,hours)
        response = http.get(domain + "commands/status/" + str(id))
        print(response)
        if id !=0:
            while str(response.json()) != str(100):
                print("still running")
                time.sleep(1)
                response = http.get(domain + "commands/status/" + str(id))

        print("next started")

    output_file = open("mapping.txt", "w+")
    output_file.write(str(array_of_ids))
    print("finished in "+(str(time.time()-start_time))+" seconds")
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
    phase_count=[0]*len(node_list)
    for element in new_topology["radials"][0]["loads"]:
        bus = element["bus"]
        #print(bus)
        bus_name = bus.split(".", 1)[0]
        if bus_name in node_list:
            #print(bus_name)
            index=node_list.index(bus_name)
            phase_count[index]=phase_count[index]+1
    #print(str(phase_count))
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
        file_without_txt=filename.split(".txt")[0]
        file_label=file_without_txt+" load "
        plot_node(output_profile, file_label)
        return output_profile

def plot_node_in_every_test(path,node_name,mapping_name):
    plt.figure(figsize=(10,10))
    #mapping_file = open(path + 'mappingSelfConsumption.txt').read()

    average=calculate_voltage(path,node_name,mapping_name)
    for percentage in average:
        linecount=len(average[percentage])
        #plot_node(average[percentage],percentage)
    node_number=node_name.split("_a")[1]

    profile_path="C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential/"
    profile_name=str("profile_"+str(node_number)+".txt")
    load=plot_profile(profile_path,profile_name ,linecount)
    pv=plot_pv_profile(path,linecount,mapping_name)
    pess=plot_pess(path,linecount, "Akku"+str(node_number),mapping_name)
    #TODO for multiple plotted shapes
    p_pv_curt=plot_P_PV_curt(path,linecount,"Akku"+str(node_number),mapping_name)
    plot_P_Grid(path,linecount,pv,load,pess,p_pv_curt)
    #plot_soc(path,linecount,"Akku"+str(node_number),mapping_name)
    #################################
    pv_difference=[]
    for element in range(linecount):

        #pv_difference.append(pv[element] - p_pv_curt[element])
        pass
    print("difference between pv and curt "+str(pv_difference))

    ######################

    #plt.ylabel('Power [kW]')
    plt.ylabel('Power [kW]')
    plt.xlabel("Time [hours]")
    plt.title(str(node_name))
    plt.legend()
    plt.savefig(node_name + ".png")
    plt.show()
def plot_soc(path,linecount,target,mapping_name):
    mapping_file = open(path+mapping_name+'.txt').read()
    mapping=parse_mapping(mapping_file)
    ##########
    for result_id in mapping:
        pess_file = open(path + result_id + "/" + result_id + "_soc_result").read()
        pess_loadshapes = json.loads(pess_file)
        print(pess_loadshapes)
        flag_plotted=False
        for batteryName in pess_loadshapes:
            print("fitting batteryname " + str(batteryName))
            loadshape = pess_loadshapes[batteryName]["SoC"]
            print(loadshape)
            if time != -1:
                shape_to_plot = loadshape[:linecount]
            else:
                shape_to_plot = loadshape
            plot_node(shape_to_plot, " SoC :" + str(batteryName))
            if batteryName==target:
                pass


def calculate_voltage(path,node_name,mapping_name):
    mapping_file = open(path+mapping_name+'.txt').read()
    mapping=parse_mapping(mapping_file)
    print(mapping)
    percentage=0
    returned_averages={}
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
                print("length of voltage list "+str(time))
                returned_averages[str(percentage)+"%"]=average_over_phases
                #plot_node(average_over_phases,str(percentage)+"%")
        percentage=percentage+10
    return returned_averages

def calculate_average_of_phase(phase1,phase2,phase3):
    output_list= []
    for index in range(len(phase1)):
        added=phase1[index]+phase2[index]+phase3[index]
        added=added/3
        output_list.append(added)
    return output_list
def help_function_for_timestamps(date):
    now = datetime.datetime.strptime(date, '%Y.%m.%d %H:%M:%S')
    timestamp = now.timestamp()
    return timestamp

def plot_pv_profile(path,time,mapping_name):
    mapping_file = open(path+mapping_name+'.txt').read()
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
    return shape_to_plot
    ##############
def plot_pess(path,linecount,target,mapping_name):
    mapping_file = open(path+mapping_name+'.txt').read()
    mapping=parse_mapping(mapping_file)
    ##########
    for result_id in mapping:
        pess_file = open(path + result_id + "/" + result_id + "_soc_result").read()
        pess_loadshapes = json.loads(pess_file)
        print(pess_loadshapes)
        flag_plotted=False
        for batteryName in pess_loadshapes:
            if batteryName==target:
                print("fitting batteryname " + str(batteryName))
                loadshape = pess_loadshapes[batteryName]["P_ESS"]
                if time != -1:
                    shape_to_plot=loadshape[:linecount]
                else:
                    shape_to_plot = loadshape
                plot_node(shape_to_plot," P_ESS")
    return shape_to_plot
    #TODO for multiple
            # plt.plot(loadshape[15])
    ##############
def plot_P_PV_curt(path,time,target,mapping_name):
    mapping_file = open(path+mapping_name+'.txt').read()
    mapping=parse_mapping(mapping_file)
    ##########
    for result_id in mapping:
        pess_file = open(path + result_id + "/" + result_id + "_soc_result").read()
        p_pv_curt_loadshapes = json.loads(pess_file)
        flag_plotted=False
        for batteryName in p_pv_curt_loadshapes:
            if batteryName==target:
                print("fitting batteryname " + str(batteryName))
                loadshape = p_pv_curt_loadshapes[batteryName]["P_PV"]
                if time != -1:
                    shape_to_plot=loadshape[:time]
                else:
                    shape_to_plot = loadshape
                print("the load shape of p_pv_curtailed :" +str(shape_to_plot))
                plot_node(shape_to_plot," P_PV curtailed")
    return shape_to_plot
def plot_P_Grid(path,time,pv,load,pess=None, p_pv_curt=None):
    if pess == None:
        pess=[0]*time
    if p_pv_curt == None:
        p_pv_curt=pv
        print("p_pv_curtailed not given")
    result=[]
    for index in range(time):
        p_grid=-p_pv_curt[index]-pess[index]+load[index]
        result.append(p_grid)

    print(result)
    plot_node(result,"P Grid")
def calculate_pv_size(pathPv,pathProfile):
    output_file = open("proposed_PV_ESS.txt", "w+")
    pv_raw=open(pathPv).read()
    pv=yaml.load(pv_raw)
    pv_kw=0
    peak_pv=0
    for element in pv["PV_1"]["loadshape"]:
        if float(element)>float(peak_pv):
            peak_pv=element
        pv_kw=float(pv_kw)+float(element)
    daily_average_pv=pv_kw/len(pv["PV_1"]["loadshape"])*24
    output_file.write("timehorizon kw for pv "+str(pv_kw)+" average over day "+str(daily_average_pv)+" and peak pv "+str(peak_pv))
    output_file.write(("\n"))
    directory = os.fsencode(pathProfile)
    number_of_files=20
    linecount=48
    wanted_profiles=[1,2,3,4,5,6,8,9,10,11,12,14,15,17,18,29,20]
    kw=3
    peak_load_list = {}
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        number_and_txt=filename.split("_")[1]
        number=number_and_txt.split(".")[0]
        if int(number) in wanted_profiles:
            peak=0
            count=0
            kw_for_timehorizon=0
            for line in open(pathProfile + "/" + filename):
                if count<linecount:
                    if float(line.rstrip()) > peak:
                        peak=float(line.rstrip())
                    count=count+1
                    kw_for_timehorizon=kw_for_timehorizon+float(line.rstrip())*kw
            peak_load_list[number]=peak
            daily_average_load=kw_for_timehorizon/count*24
            final_result=(daily_average_load*peak_pv)/(daily_average_pv)

            final_result_ESS=daily_average_load/1
            # output_file.write("timesteps in load_profile "+str(count)+" , kw in timehorizon "+str(kw_for_timehorizon)+" ,average over day "+ str(daily_average_load))
            # output_file.write(("\n"))
            # output_file.write("final result of pv size for "+str(number)+" is "+str(final_result))
            # output_file.write(("\n"))
            # output_file.write("proposed ess_size in kw "+str(final_result_ESS))
            # output_file.write(("\n"))
    print(str(peak_load_list)+" and "+str(peak_pv))

def calculate_difference_between_profiles(path_to_profileA,path_to_profileB,node):
    result_fileA = open(path_to_profileA).read()
    file_nameA = yaml.load(result_fileA)
    result_fileB = open(path_to_profileB).read()
    file_nameB= yaml.load(result_fileB)
    difference={}
    for elementA in file_nameA['voltages']:
        splittedA = elementA.split(".", 1)[0]
        if splittedA in get_relevant_nodes():
            for elementB in file_nameB['voltages']:
                splittedB = elementB.split(".", 1)[0]
                if splittedB == splittedA:
                    difference[splittedB]=[]
                    min_len=min(len(file_nameA['voltages'][elementA]["Voltage"]),len(file_nameB['voltages'][elementB]["Voltage"]))
                    #print(min_len)
                    #print(file_nameA['voltages'][elementA]["Voltage"])
                    #print(file_nameB['voltages'][elementB]["Voltage"])
                    for i in range(min_len):
                        valueA=file_nameA['voltages'][elementA]["Voltage"][i]
                        valueB=file_nameB['voltages'][elementB]["Voltage"][i]
                        difference_i= float(valueA-valueB)
                        #print("valueA "+str(valueA)+" valueB "+str(valueB)+" and difference "+str(difference_i))
                        difference[splittedB].append(difference_i)
    difference_result=open("difference_profiles.txt","w+")
    difference_result.write(str(difference))
    return difference

def plot_differences(pathA,pathB,node,nameA,nameB,mappingA,mappingB):
    plt.figure(figsize=(10,10))
    voltageA=calculate_voltage(pathA,node,mappingA)
    voltageB=calculate_voltage(pathB,node,mappingB)
    difference={}
    for percentageA in voltageA:
        profileA=voltageA[percentageA]
        for percentageB in voltageB:
            profileB=voltageB[percentageB]
            if percentageA==percentageB:
                difference_for_percentage_value=[]
                min_length=min(len(profileA),len(profileB))
                for index in range(min_length):
                    difference_for_percentage_value.append(profileA[index]-profileB[index])
                #label=percentageA
                label="100% pv penetration"
                difference[percentageA]=difference_for_percentage_value
                plot_node(profileA[:min_length],nameA+" "+str(label))
                plot_node(profileB[:min_length],nameB+" "+str(label))
                plot_node(difference[percentageA],"difference, penetration "+str(label))
    print(str(difference))
    plt.ylabel('Voltage [pu]')
    plt.xlabel("Time [hours]")
    plt.title("Voltage deviations")
    plt.legend()
    plt.savefig(node + "_deviations.png")
    plt.show()
def voltage_prediction(path,mapping_name):
    output_file = open("voltage_prediction.txt", "w+")
    output_json={}
    for node_name in get_relevant_nodes():

        voltage_profile=calculate_voltage(path,node_name,mapping_name)
        output_json[node_name]=voltage_profile["0%"]
    output_file.write(str(output_json))
def calculate_sensitivity(path,mapping_nameA,mapping_nameB):
    result_fileSingle = open(path+mapping_nameA+".txt").read()
    single_json = yaml.load(result_fileSingle)
    result_fileMultiple = open(path+mapping_nameB+".txt").read()
    multiple_json = yaml.load(result_fileMultiple)
    count=0
    node_list= [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 14, 15, 17, 18, 19, 20]
    voltage_list_curtailed={}
    for node in node_list:
        node_name="node_a"+str(node)
        voltage_result=calculate_voltage(path,node_name,mapping_nameB)
        index_node=node_list.index(node)
        voltage_list_curtailed[node_name]=voltage_result[str(index_node*10)+"%"]

def calculate_surplus(path,mapping):
    pass

#print(get_relevant_nodes())
#print(get_overall_min_max(get_result_information(resultJson)))

#define_all_topologies()
#print(array_of_ids)
#run_simulation(array_of_ids[0],10)
#response = http.get(domain + "commands/status/" + str(array_of_ids[0]))
#print(response)
#voltage_prediction("PVTest/","mapping")

run_all(48)
#calculate_pv_size("PVTest/cc589737d784/cc589737d784_pv_result","C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential")
#print(array_of_ids)
#helper()
#iterate_result("PVTest/")
#file=open("4a88bbde8854_result_raw.json").read()

#plt.plot(file_json[:48])
#iterate_through_profiles("C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential",48)

#iterate_through_profiles("C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential",96,20)
path="C:/Users/klingenb/Documents/BAThesis/Results/TestStorages/self-consumption/"
#plot_node_in_every_test(path,"node_a12","mapping_SC_1kw_P_Bigger_ESS")
#plot_node_in_every_test("StorageTest/","node_a12","SP_big_ESS_Curt_cbc_changed_SOC")
#plot_node_in_every_test("PVTest/","node_a12","mapping")
#plot_differences("PVTest/","StorageTest/","node_a12","Only PV","Minimize costs 1kw max export","mapping","mappingBigESS1kwMC")

#plot_differences(path,"StorageTest/","node_a12","Self Consumption,1kw max export and bigger ess","Self Consumption,1kw max export and P_pv curtailment","mapping_SC_1kw_P_Bigger_ESS","mappingSC_big_ESS_Curt")


#print(help_function_for_timestamps("2018.07.03 00:00:00"))
#print(calculate_difference_between_profiles("PVTest/312a9208e97b/312a9208e97b_result_raw.json","StorageTest/ce08e0f4d52a/ce08e0f4d52a_result_raw.json","node_a12"))
excluded=[0,7,12,13,19]
# for i in range(25):
#     if i not in excluded:
#         plot_profile("C:/Users/klingenb/PycharmProjects/simulation-engine/profiles/load_profiles/residential","profile_"+str(i)+".txt",48)



#file_json2=json.loads(file_json)
#file_json3=json.loads(file_json2)
#print(type(file_json3))
#parse_raw_data(file_json)