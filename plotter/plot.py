
import logging

import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import seaborn as sns

from profess.Http_commands import Http_commands
import os

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Plotter:

    def __init__(self, url):
        self.url_dsf_se = url
        self.httpClass = Http_commands()
        logger.debug("Plotter created")

    def get_connection_topology(self, id):
        query = self.url_dsf_se + "/se/simulation/" + id + "/connections"
        response = self.httpClass.get(query)
        json_response = response.json()
        # logger.debug("type json_response "+str(type(json_response)))
        if response.status_code == 200:
            return json_response

        else:
            logger.error("Failed to get voltages, response from dsf-se:" + str(json_response))
            return 1

    def get_data_voltages(self, id, name=None, phase_number = 1):
        query = self.url_dsf_se+"/se/simulation/"+ id +"/voltages"
        response = self.httpClass.get(query)
        json_response = response.json()
        #logger.debug("type json_response "+str(type(json_response)))
        if response.status_code == 200:
            if name == None:
                data = json_response["voltages"]
                data_to_return = {}
                for node_name, value in data.items():
                    if not node_name in data_to_return.keys():
                        data_to_return[node_name] = {}
                    for phase_name, value_phase in value.items():
                        if phase_name == "Phase "+str(phase_number):
                            data_to_return[node_name] = value_phase
                            len_data = len(value_phase)

                limit_list_high = [1.1 for i in range(len_data)]
                limit_list_low = [0.9 for i in range(len_data)]
                data_to_return["higher limit"] = limit_list_high
                data_to_return["lower limit"] = limit_list_low
                return data_to_return
            else:
                data = json_response["voltages"][name]
                data_to_return = {}

                data_to_return[name] = {}
                for phase_name, value_phase in data.items():
                    if phase_name == "Phase " + str(phase_number):
                        data_to_return[name] = value_phase
                        len_data = len(value_phase)

                limit_list_high = [1.1 for i in range(len_data)]
                limit_list_low = [0.9 for i in range(len_data)]
                data_to_return["higher limit"] = limit_list_high
                data_to_return["lower limit"] = limit_list_low
                return data_to_return
        else:
            logger.error("Failed to get voltages, response from dsf-se:" + str(json_response))
            return 1

    def get_data_soc(self, id, element="Storages", name=None):
        possible_elements = ["EVs", "Storages"]
        if not element in possible_elements:
            logger.error("Wrong element. Possible elements " + str(possible_elements))
        query = self.url_dsf_se + "/se/simulation/" + id + "/soc/"+element
        response = self.httpClass.get(query)
        json_response = response.json()
        # logger.debug("type json_response "+str(type(json_response)))
        if response.status_code == 200:
            if name == None:
                return json_response["soc"][element]
            else:
                data_to_return = {}
                data = json_response["soc"][element][name]
                data_to_return[name] = [float(i) for i in data]
                len_data= len(json_response["soc"][element][name])
                limit_list_high = [1.1 for i in range(len_data)]
                data_to_return["high"]=limit_list_high
                return data_to_return
        else:
            logger.error("Failed to get voltages, response from dsf-se:" + str(json_response))
            return 1

    def get_data_powers(self, id, element="Load", name=None):
        possible_elements = ["Load", "Photovoltaic", "EVs", "Storages"]
        if not element in possible_elements:
            logger.error("Wrong element. Possible elements "+str(possible_elements))
        query = self.url_dsf_se+"/se/simulation/"+ str(id) +"/powers/" + str(element)
        #logger.debug("query "+str(query))
        response = self.httpClass.get(query)
        json_response = response.json()
        #logger.debug("type json_response "+str(type(json_response)))
        if response.status_code == 200:
            if name == None:
                return json_response["powers"][element]
            else:
                data_to_return = {}
                data_to_return[name]=json_response["powers"][element][name.lower()]
                return data_to_return
        else:
            logger.error("Failed to get voltages, response from dsf-se:" + str(json_response))
            return 1

    def get_data_voltages_at_node(self, id, node):
        query = self.url_dsf_se+"/se/simulation/"+ id +"/voltages/"+node
        response = self.httpClass.get(query)
        json_response = response.json()

        json_response=json_response["voltages"]

        if response.status_code == 200:
            return json_response
        else:
            logger.error("Failed to get voltages, response from dsf-se:" + str(json_response))
            return 1

    def get_active_powers(self, data_dict, phase_number=1):
        new_data = {}
        #logger.debug("data_dict "+str(data_dict))
        if phase_number <= 3:
            for name, values in data_dict.items():
                if name not in new_data.keys():
                    new_data[name]={}
                for phase, list_values in values.items():
                    if phase == "Phase "+str(phase_number):
                        power_per_phase=[complex(i).real for i in list_values]
                        new_data[name] = power_per_phase
        else:
            for name, values in data_dict.items():
                if name not in new_data.keys():
                    new_data[name]={}
                power_per_phase_1 =[]
                power_per_phase_2 = []
                power_per_phase_3 = []
                for phase, list_values in values.items():
                    if phase == "Phase 1":
                        power_per_phase_1=[complex(i).real for i in list_values]
                    if phase == "Phase 2":
                        power_per_phase_2=[complex(i).real for i in list_values]
                    if phase == "Phase 3":
                        power_per_phase_3=[complex(i).real for i in list_values]

                    new_data[name] =[sum(x) for x in zip(power_per_phase_1, power_per_phase_2, power_per_phase_3)]

        return new_data

    def get_reactive_powers(self, data_dict, phase_number=1):
        new_data = {}
        if phase_number <= 3:
            for name, values in data_dict.items():
                if name not in new_data.keys():
                    new_data[name]={}
                for phase, list_values in values.items():
                    if phase == "Phase "+str(phase_number):
                        power_per_phase=[complex(i).imag for i in list_values]
                        new_data[name] = power_per_phase
        else:
            for name, values in data_dict.items():
                if name not in new_data.keys():
                    new_data[name]={}
                power_per_phase_1 =[]
                power_per_phase_2 = []
                power_per_phase_3 = []
                for phase, list_values in values.items():
                    if phase == "Phase 1":
                        power_per_phase_1=[complex(i).imag for i in list_values]
                    if phase == "Phase 2":
                        power_per_phase_2=[complex(i).imag for i in list_values]
                    if phase == "Phase 3":
                        power_per_phase_3=[complex(i).imag for i in list_values]

                    new_data[name] =[sum(x) for x in zip(power_per_phase_1, power_per_phase_2, power_per_phase_3)]
        return new_data

    def add_grid_values(self, data_dict_PV=None, data_dict_Load=None, data_dict_ESS=None, data_dict_EV=None):

        data_list_PV = None
        data_list_ESS = None
        data_list_Load = None
        data_list_EV = None

        if not data_dict_PV == None and not data_dict_PV == {}:
            for element, values in data_dict_PV.items():
                data_list_PV = values

        if not data_dict_Load == None and not data_dict_Load == {}:
            for element, values in data_dict_Load.items():
                data_list_Load = values

        if not data_dict_ESS == None and not data_dict_ESS == {}:
            for element, values in data_dict_ESS.items():
                data_list_ESS = values

        if not data_dict_EV == None and not data_dict_EV == {}:
            for element, values in data_dict_EV.items():
                data_list_EV = values

        power_consumption =[]
        power_generation = []

        if not data_list_Load == None and not data_dict_Load == {} and not data_list_EV == None and not data_dict_EV == {}:
            power_consumption = [sum(x) for x in zip(data_list_Load, data_list_EV)]
        elif not data_list_Load == None:
            power_consumption = data_list_Load
        else:
            logger.error("No data for power consumption")
            return None

        if not data_list_PV == None and not data_dict_PV == {} and not data_list_ESS == None and not data_dict_ESS == {}:
            power_generation = [sum(x) for x in zip(data_list_PV, data_list_ESS)]

        elif not data_list_PV == None:
            power_generation = [x for x in data_list_PV]
        else:
            logger.error("No data for power generation")



        if not power_consumption == [] and not power_generation==[]:
            #logger.debug("power consumption "+str(power_consumption))

            power_generation = [-x for x in power_generation]
            #logger.debug("power generation " + str(power_generation))
            power_grid =  [sum(x) for x in zip(power_consumption, power_generation)]
        elif not power_consumption == []:
            power_grid = power_consumption

        #logger.debug("power grid "+str(power_grid))
            #power_consumption = [0]*n


        #power_load + power_EV = power_PV + power_ess + p_grid
        return {"grid_power":power_grid}

    def plot(self, dict_voltages, file_name = None, xlabel= None, ylabel=None):
        data = dict_voltages
        #logger.debug("data "+str(data))
        for key, value in data.items():
            len_data = len(value)

        obj= pd.DataFrame.from_dict(data)
        #logger.debug("obj "+str(obj))

        sns.set(context="paper")
        sns.set(context="paper", rc={'figure.figsize': (14, 8), "lines.linewidth": 1.5}, font_scale=1.5)
        sns.set_style("ticks", {'grid.color': '.8'})

        fig, ax1 = plt.subplots(1,1)
        #continent_colors = ["#009432", "#0652DD", "#EE5A24", "#9980FA", "#B53471" ]
        sns.set_palette(sns.hls_palette(8, l=.4, s=.8))

        g = sns.lineplot(data=obj, sort=False, ax=ax1, dashes=False)

        #leg = g._legend.texts
        #logger.debug("legend "+str(leg))

        #g.set_xlim(0, 48)
        # g.set_xticks(np.arange(24))
        plt.xticks(rotation=0)
        if not xlabel == None:
            g.set_xlabel(xlabel)
        if not ylabel == None:
            g.set_ylabel(ylabel)
        g.yaxis.grid(True)
        # g.xaxis.set_label_coords(0.5, -0.15)
        # Put a legend to the right side
        # Removed 'ax' from T.W.'s answer here aswell:
        box = g.get_position()

        g.set_position([box.x0, box.y0, box.width * 0.85, box.height])  # resize position
        g.legend(loc='center right', bbox_to_anchor=(1.25, 0.5), ncol=1)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

        if not file_name == None:
            file_name = "./" + file_name + ".jpg"
            folder_name = os.path.dirname(file_name)
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            plt.savefig(file_name, dpi=600, format="jpg", bbox_inches="tight")
            import sys
            sys.exit(0)
        else:
            plt.show()


    def get_power(self, id, folder_name, connections):
        ######################################################################
        #################### powers ##########################################
        ######################################################################
        xlabel = "Timestamp [h]"
        ylabel = "Power [kW]"
        phase_number = 4


        for bus_name, element_object in connections.items():
            base = "results/" + folder_name + "/" + bus_name + "/"
            file_name_P = base + "powers_P"
            file_name_Q = base + "powers_Q"
            logger.debug("file name P: " + str(file_name_P))
            logger.debug("file name Q: " + str(file_name_Q))

            element_type_to_get = None
            real_powers = {"photovoltaics" :None, "loads":None, "storageUnits":None, "chargingStations":None}
            reactive_powers = {"photovoltaics" :None, "loads":None, "storageUnits":None, "chargingStations":None}
            for element_type, element_names in element_object.items():
                #if element_type == "transformers":
                    ##element_type_to_get = "transformers"
                if element_type == "loads":
                    element_type_to_get = "Load"
                elif element_type == "photovoltaics":
                    element_type_to_get = "Photovoltaic"
                elif element_type == "storageUnits":
                    element_type_to_get = "Storages"
                elif element_type == "chargingStations":
                    element_type_to_get = "EVs"

                for name in element_names:
                    if not element_type_to_get == None:
                        #logger.debug("element_type_to_get "+str(element_type_to_get)+ " with name "+str(name))
                        powers = self.get_data_powers(id, str(element_type_to_get), str(name))

                        if not element_type in real_powers.keys():
                            real_powers[element_type]={}
                        real_powers[element_type] = self.get_active_powers(powers, phase_number)

                        if not element_type in reactive_powers.keys():
                            reactive_powers[element_type]={}

                        reactive_powers[element_type] = self.get_reactive_powers(powers, phase_number)
            logger.debug("real powers " +str(real_powers))
            logger.debug("reactive powers "+ str(reactive_powers))

            real_power_grid = self.add_grid_values(real_powers["photovoltaics"], real_powers["loads"], real_powers["storageUnits"],
                                                   real_powers["chargingStations"])
            reactive_power_grid = self.add_grid_values(reactive_powers["photovoltaics"], reactive_powers["loads"], reactive_powers["storageUnits"],
                                                   reactive_powers["chargingStations"])

            if not real_power_grid == None:
                PVs = real_powers["photovoltaics"] or {}
                loads = real_powers["loads"] or {}
                ESS = real_powers["storageUnits"] or {}
                EVs = real_powers["chargingStations"] or {}

                total_real_powers = {**real_power_grid, **loads, **PVs, **ESS, **EVs, }


                #logger.debug("total_real_powers " + str(total_real_powers))
                self.plot(total_real_powers, file_name=file_name_P, xlabel=xlabel, ylabel=ylabel)

            if not reactive_power_grid == None:
                PVs = reactive_powers["photovoltaics"] or {}
                loads = reactive_powers["loads"] or {}
                ESS = reactive_powers["storageUnits"] or {}
                EVs = reactive_powers["chargingStations"] or {}

                total_reactive_powers = {**real_power_grid, **loads, **PVs, **ESS, **EVs}
                #logger.debug("total_reactive_powers " + str(total_reactive_powers))
                self.plot(total_reactive_powers, file_name=file_name_Q, xlabel=xlabel, ylabel=ylabel)



    def create_plots_for_grid(self, id, folder_name):
        connections = self.get_connection_topology(id)
        logger.debug("connections " + str(connections))

        base_all_voltages = "results/" + folder_name + "/"
        file_name_voltages = base_all_voltages + "all_voltages"
        logger.debug("file_name_voltages " + str(file_name_voltages))

        xlabel = "Timestamp [h]"
        ylabel = "Voltage [pu]"
        for i in range(3):
            voltages = self.get_data_voltages(id, phase_number=(i + 1))
            #logger.debug("data voltages " + str(voltages))
            #self.plot(voltages, file_name=file_name_voltages + "_phase_" + str(i + 1), xlabel=xlabel, ylabel=ylabel)



        for bus_name, connected_elements in connections.items():
            xlabel = "Timestamp [h]"
            ylabel = "Voltage [pu]"
            base = "results/"+ folder_name + "/" + bus_name + "/"
            file_name_voltage_node = base + "voltage_" + bus_name
            logger.debug("file_name_voltage_node "+str(file_name_voltage_node))

            for i in range(3):
                voltages_node = self.get_data_voltages(id, bus_name, phase_number=(i + 1))
                #self.plot(voltages_node, file_name=file_name_voltage_node + "_phase_" + str(i + 1), xlabel=xlabel,
                           #ylabel=ylabel)


        self.get_power(id,folder_name, connections)

        """file_name_soc = base + "soc"
        xlabel = "Timestamp [h]"
        ylabel = "SoC [%]"
        soc_ESS = self.get_data_soc(id, element_type_ess, element_name_ess)
        logger.debug("soc " + str(soc_ESS))
        self.plot(soc_ESS, file_name=file_name_soc, xlabel=xlabel, ylabel=ylabel)"""





def main():
    import sys
    url = "http://192.168.99.100:9090"
    plotter = Plotter(url)
    #id = "80dcb13d0478"  #with ESS
    id = "24fafe423bcc"   #with PV



    plotter.create_plots_for_grid(id, "grid_with_PV")
    sys.exit(0)
    node = "node_a12"
    xlabel = "Timestamp [h]"
    ylabel = "Voltage [pu]"
    base = "results/grid_with_PV/"+node+"/"


    file_name_voltages = base+"all_voltages"
    file_name_voltage_node = base + "voltage_"+node

    for i in range(3):
        voltages = plotter.get_data_voltages(id, phase_number=(i+1))
        logger.debug("data voltages "+str(voltages))
        plotter.plot(voltages, file_name=file_name_voltages+"_phase_"+str(i+1), xlabel=xlabel, ylabel=ylabel)

        voltages_node=plotter.get_data_voltages(id , node, phase_number=(i+1))
        plotter.plot(voltages_node, file_name=file_name_voltage_node+"_phase_"+str(i+1), xlabel=xlabel, ylabel=ylabel)



    #"Voltage [pu]"
    ######################################################################
    #################### powers ##########################################
    ######################################################################
    xlabel = "Timestamp [h]"
    ylabel = "Power [kW]"
    phase_number = 4
    file_name_P = base+"powers_P"
    file_name_Q = base+"powers_Q"

    element_type = "Photovoltaic"
    #element_name = "pv_VEAB3cqi-"
    element_name = "pv_veab3cqi-"
    powers_PV= plotter.get_data_powers(id, element_type, element_name)
    real_powers_PV = plotter.get_active_powers(powers_PV, phase_number)
    reactive_powers_PV = plotter.get_reactive_powers(powers_PV, phase_number)
    logger.debug("real powers PV " + str(real_powers_PV))
    logger.debug("reactive powers PV " + str(reactive_powers_PV))

    element_type_ess = "Storages"
    element_name_ess = None#"storage_MI93AZgxP"
    powers_ESS = plotter.get_data_powers(id, element_type_ess, element_name_ess)
    real_powers_ESS = plotter.get_active_powers(powers_ESS, phase_number)
    reactive_powers_ESS = plotter.get_reactive_powers(powers_ESS, phase_number)
    logger.debug("real powers ESS " + str(real_powers_ESS))
    logger.debug("reactive powers ESS " + str(reactive_powers_ESS))

    element_type = "Load"
    element_name = "load_4006422"
    powers_Load = plotter.get_data_powers(id, element_type, element_name)
    real_powers_Load = plotter.get_active_powers(powers_Load, phase_number)
    reactive_powers_Load = plotter.get_reactive_powers(powers_Load, phase_number)
    logger.debug("real powers Load " + str(real_powers_Load))
    logger.debug("reactive powers Load " + str(reactive_powers_Load))

    element_type = "EVs"
    element_name = None
    powers_EV = plotter.get_data_powers(id, element_type, element_name)
    real_powers_EV = plotter.get_active_powers(powers_EV, phase_number)
    reactive_powers_EV = plotter.get_reactive_powers(powers_EV, phase_number)


    real_power_grid = plotter.add_grid_values(real_powers_PV, real_powers_Load, real_powers_ESS, real_powers_EV)
    reactive_power_grid = plotter.add_grid_values(reactive_powers_PV, reactive_powers_Load, reactive_powers_ESS, reactive_powers_EV)

    total_real_powers = {**real_powers_PV, **real_powers_Load, **real_powers_ESS, **real_powers_EV, **real_power_grid}
    total_reactive_powers = {**reactive_powers_PV, **reactive_powers_Load, **reactive_powers_ESS, **reactive_powers_EV, **reactive_power_grid}



    plotter.plot(total_real_powers,  file_name= file_name_P,xlabel=xlabel, ylabel=ylabel)

    plotter.plot(total_reactive_powers,  file_name=file_name_Q, xlabel=xlabel, ylabel=ylabel)

    file_name_soc = base + "soc"
    xlabel = "Timestamp [h]"
    ylabel = "SoC [%]"
    soc_ESS = plotter.get_data_soc(id, element_type_ess, element_name_ess)
    logger.debug("soc "+str(soc_ESS))
    plotter.plot(soc_ESS,  file_name=file_name_soc, xlabel=xlabel, ylabel=ylabel)





if __name__ == '__main__':
    main()
