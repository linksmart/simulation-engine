import logging
import os
import sys
import time

from profess.Http_commands import Http_commands
from plotter.plot import Plotter
from data_management.utils import Utils

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


files_names = ["ev_one_charging_station_5_15.json", "ev_one_charging_station_5_16.json","ev_one_charging_station_5_17.json",
             "ev_one_charging_station_5_18.json", "ev_one_charging_station_5_19.json", "ev_one_charging_station_5_20.json",
               "ev_one_charging_station_9_15.json",  "ev_one_charging_station_9_16.json",  "ev_one_charging_station_9_17.json",
               "ev_one_charging_station_9_18.json",  "ev_one_charging_station_9_19.json",  "ev_one_charging_station_9_20.json"]

id_list_self_production = ["59eb8f6c48dd", "18827ad0c85c", "02f39cbac932", "5e9a3d50e492", "6be2e518a03a", "201ea86f704b", "ad8a1c5f5604", "4822e068a297", "7b626a3fa5a3", "0ea261251d9d","0168a1f32bdf", "a228c91cd7f6"]
id_list_self_consumption=["1a29ad53ceed", "7cf10d4d5877","e2b79a45789f", "e71c5e3061ed", "f66385a57e6f", "758833fa1413", "c0d26dbdeaa7", "9754aad5efd4", "a1c73affc4f4", "abbf63bacde0", "7fdf34c264b2", "aea5b6f447e3"]
id_list_min_costs=["2ca1815a8cda","9d612eaabad8", "8da1400e71ca", "8e145e3ab8b1", "5593efdc099b", "4944f550bdcd", "f2a5585386dd", "2abcc1d857e4", "1ecbb227e0b8", "21344a82b952", "16a59b6990df", "a45f93772256"]
id_list_self_production_vc = ["b21aa10dbff7", "b69c1d0f9c29", "1502ed1b2702", "7280deee7951", "326de0037ba0", "3c5e31f53728", "bb30fe8a6b53", "22a72855384d", "9497039e9385", "0db32893e846", "17b51efdd476", "161f73f8db05"]
id_list_self_consumption_vc = ["8d242b6af1b4", "ce0db4538207", "96b4851b2160", "f7e2c355c3fa", "ec9911d961d5", "863e1f13fa67", "10b8d2f72b9c", "8e497740ba88", "53c29f7530c7", "8db0dc21b6c5", "8f43fbacdc0e", "86e73e67a0f8"]
id_list_min_costs_vc=["3e4a8be63038", "c7bafe8de5f2", "ba2c7a3a69ad", "e77cfeb64a66", "367c7e8ce5e3", "461f447a99bc", "5a89e1dadd03", "9c18ddcff1c5", "d7bb136983ab", "564b84f98df9", "7122ec92a7a6", "5ab2eb14f720"]
id_list = ["10b8d2f72b9c", "8e497740ba88", "53c29f7530c7", "8db0dc21b6c5", "8f43fbacdc0e", "86e73e67a0f8",
           "3e4a8be63038", "c7bafe8de5f2", "ba2c7a3a69ad", "e77cfeb64a66", "367c7e8ce5e3", "461f447a99bc", "5a89e1dadd03", "9c18ddcff1c5", "d7bb136983ab", "564b84f98df9", "7122ec92a7a6", "5ab2eb14f720"]



def main_plot():
    url = "http://localhost:9091"
    plotter = Plotter(url)
    
    
    for i in range(12):
    
    logger.debug("dict_with_id_single_ev "+str(dict_with_id_single_ev))
    
    logger.debug("Reading information from dsf-se")
    folder_basis = os.path.join(os.getcwd(),"inputs", "Bolzano")
    logger.debug("folder_basis "+str(folder_basis))
    for name1 in os.listdir(folder_basis):
        logger.debug("name 1 "+str(name1))
        if name1 == "virtual_capacity":
            folder_basis_2 = os.path.join(folder_basis, name1)
            if os.path.isdir(folder_basis_2):
                for name2 in os.listdir(folder_basis_2):
                    logger.debug("name 2 " + str(name2))
                    folder_basis_3 = os.path.join(folder_basis_2, name2)
                    if os.path.isdir(folder_basis_3):
                        for file_name in os.listdir(folder_basis_3):
                            folder_name = name1+"_"+name2+"_"+file_name.split(".")[0]+"_Steps_10_5"
                            logger.debug(folder_name)
                            if "Self-Consumption" in name2:
                                logger.debug("Self-Consumption")
                                id = dict_with_id_single_ev["self-consumption"][file_name]
                            elif "Self-Production" in name2:
                                logger.debug("Self-Production")
                                id = dict_with_id_single_ev["self-production"][file_name]
                            elif "MinimizeCosts" in name2:
                                logger.debug("MinimizeCosts")
                                id = dict_with_id_single_ev["min-costs"][file_name]
                                
                            logger.debug("id "+str(id))
                            logger.debug("########################## Voltages ##########################################")
                            plotter.create_plots_for_voltages(id, folder_name)
                            logger.debug("########################## Powers ##########################################")
                            plotter.create_plots_for_powers(id, folder_name)
                            logger.debug("########################## SoCs ##########################################")
                            plotter.create_plots_for_socs(id, folder_name)
                            logger.debug("########################## PV Usage ##########################################")
                            plotter.create_plots_for_pv_usage(id, folder_name)


    
    

if __name__ == '__main__':
    main_plot()