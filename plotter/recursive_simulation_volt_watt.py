import logging
import os
import sys
import time
import pandas as pd

from profess.Http_commands import Http_commands
from plotter.plot import Plotter
from data_management.utils import Utils

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)



def read_file_csv():
    import csv
    data_file = "./id_info_volt_var.csv"
    data_list=[]
    logger.debug("data_file "+str(data_file))
    with open(data_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                #logger.debug(f'Column names are {"; ".join(row)}')
                line_count += 1
            data_list.append({"id":row["ID"], "name":row["File_name"]})
            #print(
                #f'\t{row["Id_number"]} works in the {row["ID"]} department, and was born in {row["File_name"]}.')
            line_count += 1
        logger.debug(f'Processed {line_count} lines.')
        logger.debug(str(data_list))
        return data_list


def main():
    url = "http://simplon.fit.fraunhofer.de:9090"
    plotter = Plotter(url)
    data_list = read_file_csv()
    logger.debug("data_list "+str(data_list))
    
    for element in data_list:
        logger.debug("#################################################################################")
        logger.debug("#################################################################################")
        id = element["id"]
        complex_name = element["name"]
        folder_name = os.path.join(os.getcwd(), "results", "pv_penetration_volt_var", complex_name)
        logger.debug("id " + str(id))
        logger.debug("Folder name "+str(folder_name))
        logger.debug("########################## Voltages ##########################################")
        plotter.create_plots_for_voltages(id, folder_name)
        logger.debug("########################## Powers ##########################################")
        plotter.create_plots_for_powers(id, folder_name)
        logger.debug("########################## SoCs ##########################################")
        plotter.create_plots_for_socs(id, folder_name)
        logger.debug("########################## PV Usage ##########################################")
        plotter.create_plots_for_pv_usage(id, folder_name)
        
        
        


    
    

if __name__ == '__main__':
    main()