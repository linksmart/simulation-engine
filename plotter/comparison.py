import logging
import os
from data_management.utils import Utils

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Comparison:

    def __init__(self):
        logger.debug("Comparison class started")
        self.utils = Utils()

    def get_grid_data_from_node(self, base_file_list, node_name, data_file_name="powers_P.json", data_type="grid", list_plot_names=None):

        if not isinstance(base_file_list, list):
            logger.error("Base file is not a list")
            return 1

        data_to_send = []
        result_to_send = {}
        count = 1
        for base_path in base_file_list:
            path = os.path.join(base_path, node_name, data_file_name)
            complete_path = self.utils.get_path(path)
            logger.debug("complete_path to read data: " +str(complete_path))
            result = self.utils.read_data_from_file(complete_path)


            if not result == None:

                if not data_file_name.find("voltage") == -1:
                    logger.debug("result "+str(result))
                    if count == 1:
                        result_to_send["higher limit"] = result["higher limit"]
                        result_to_send["lower limit"] = result["lower limit"]

                    result_to_send[list_plot_names[count-1]] = result[node_name]
                else:
                    for element_type, data in result.items():
                        if not element_type.find(data_type) == -1:
                            result_to_send[list_plot_names[count-1]] = result[element_type]
                        else:
                            logger.error("No information about " + str(data_type) + " in " + str(complete_path))
                data_to_send.append(result_to_send)
                count= count + 1
            else:
                logger.error("Result is none while reading the files")
        logger.debug("result to send "+str(result_to_send))
        return result_to_send

