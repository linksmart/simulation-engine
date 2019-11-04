import datetime
import logging
import json
import numpy as np
import time

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
from gesscon.MQTTClient import MQTTClient

class GESSCon():
        def __init__(self):
                self.payload  = {}
                self.payload_set = False

        def get_ESS_data_format(self, storage):
                """
                returns ESS data in the following format:
                {'633': {'id':"name", 'SoC': 0.4, 'Battery_Capacity':70, 'max_charging_power':33, 'max_discharging_power':33}},
                {'671': {'id':"name", 'SoC': 0.4, 'Battery_Capacity':70, 'max_charging_power':33, 'max_discharging_power':33}}]
                """
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
                logger.debug("ESS Data= %s", ess_data_list)
                return ess_data_list

        def aggregate(self, data_list):
                """
                Calculates the aggregate values of load and pv.
                Args:
                        load/pv(list): load/pv profile per node
                Returns:
                        list: aggregated profile(list of 24 values)
                """
                aggregate_list = []
                for data in data_list:
                        data_id = list(data.keys())
                        data_values = data[data_id[0]]
                        if (isinstance(data_values, dict)):
                                agg_list = []
                                for val in data_values:
                                        agg_list.append(np.square(data_values[val]))
                                aggregate = [sum(x) for x in zip(*agg_list)]
                                aggregate_list.append(list(np.sqrt(aggregate)))
                aggregate_list = [sum(x) for x in zip(*aggregate_list)]
                #logger.debug("Aggregated data = %s ", aggregate_list)
                return aggregate_list

        def create_tele_config(self, Soc):
                soc_values = []
                len_soc = len(Soc)
                b_max = []
                pc_max = []
                pd_max = []
                soc_nodes = []
                soc_ids = []
                for s in (Soc):
                        soc_node = list(s.keys())[0]
                        soc_nodes.append(soc_node)
                        soc_ids.append(s[soc_node]['ESS']['id'])
                        soc_values.append(s[soc_node]['ESS']['SoC']/100)
                        b_max.append(s[soc_node]['ESS']['Battery_Capacity'])
                        pc_max.append(s[soc_node]['ESS']['max_charging_power'])
                        pd_max.append(s[soc_node]['ESS']['max_discharging_power'])

                tele = {"SOC": soc_values}
                config = {
                        "ESS_number": len_soc,
                        "tariff": 0,
                        "grid_i": 1000,
                        "grid_o": 1000,
                        "ess_eff": [0.96] * len_soc,
                        "bmax": b_max,
                        "bmin": [0] * len_soc,
                        "pcmax": pc_max,
                        "pdmax": pd_max,
                        "cycle": [0] * len_soc,
                        "loss": 0
                }
                logger.debug("Soc = %s", soc_values)
                return tele, config, soc_nodes, soc_ids

        def gesscon(self, load, pv, price, Soc, timestamp = None):
                """
        Calculates the aggregate values of load and pv, publishes the payload JSON to GessconSimulationInput as per the given date, subscribes to GessconSimulationOutput and
        returns the result as per the format.
        [{ node: { id: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}},
                        { node: { id: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}] .
        Args:
            load(list): load profile per node
            pv(list): pv profile per node
            price(list): price profile
            Soc: Batteries data
            timestamp: input date with timestamp. Takes current date by default.for e.g:
                        timestamp = datetime.datetime.strptime("2018.10.04 00:00:00", '%Y.%m.%d %H:%M:%S').timestamp()
        Returns:
            list: as described above
        """
                try:
                        logger.debug("GESSCon connector started ")
                        aggregated_pv = self.aggregate(pv)
                        aggregated_load = self.aggregate(load)
                        tele, config, soc_nodes, soc_ids = self.create_tele_config(Soc)

                        #Creating JSON payload to be sent to GESSCon service
                        elprices = []
                        demand = []
                        pv_list = []
                        ev_list  =[]
                        #string to date
                        #start_date = datetime.datetime.strptime(date, '%Y.%m.%d %H:%M:%S')
                        if not timestamp:
                                start_date = datetime.datetime.now().strftime("%Y.%m.%d 00:00:00")
                        else:
                                start_date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y.%m.%d 00:00:00")
                        # timestamp from date to date format
                        start_date = datetime.datetime.strptime(start_date, '%Y.%m.%d %H:%M:%S')
                        #timestamp from date to date format
                        start_date_format = datetime.datetime.fromtimestamp(start_date.timestamp()).strftime("%Y.%m.%d %H:%M:%S")
                        for val in range(24):
                                date = datetime.datetime.fromtimestamp(start_date.timestamp()).strftime("%Y.%m.%d %H:%M:%S")
                                elprices.append({"DateTime": date, "elprice": price[val]})
                                demand.append({"DateTime": date, "Loads": aggregated_load[val]})
                                pv_list.append({"DateTime": date, "pv": aggregated_pv[val]})
                                ev_list.append({"DateTime": date, "ev": 0.0})
                                if(val == 23):
                                        continue
                                start_date = start_date + datetime.timedelta(hours = 1)
                        end_date_format = datetime.datetime.fromtimestamp(start_date.timestamp()).strftime("%Y.%m.%d %H:%M:%S")
                        raw = {"elprices":elprices, "demand": demand, "pv": pv_list, "ev": ev_list}

                        payload_var = {"site": "EDYNA-0018",
                        "time_start": start_date_format,
                        "time_stop": end_date_format,
                        "raw": raw,
                        "tele": tele,
                        "config": config }
                        payload = json.dumps(payload_var)
                        #logger.info("Payload: %s", payload)

                        # MQTT
                        #ca_cert_path_input = "/etc/openvpn/s4g-ca.crt"
                        ca_cert_path_input = "/usr/src/app/openvpn/s4g-ca.crt"
                        logger.debug("Publishing values in MQTT")
                        mqtt_send = MQTTClient("10.8.0.50", 8883, "gesscon_send", keepalive=60, username="fronius-fur", password="r>U@U7J8xZ+fu_vq", ca_cert_path=ca_cert_path_input, set_insecure=True, id=None)
                        logger.debug("mqtt send: "+str(mqtt_send))
                        mqtt_receive = MQTTClient("10.8.0.50", 8883, "gesscon_receive", keepalive=60, username="fronius-fur",
                                                password="r>U@U7J8xZ+fu_vq", ca_cert_path=ca_cert_path_input,
                                                set_insecure=True, id=None)
                        mqtt_receive.subscribe_to_topics([("GessconSimulationOutput",2)], self.on_msg_received)
                        logger.debug("successfully subscribed")
                        mqtt_send.publish("GessconSimulationInput", payload, False)
                        # Checks for output from GESSCon for atmost 15 seconds
                        t = 0
                        while t<= 60:
                                logger.debug("Waiting for GESSCon response")

                                if not self.payload_set:
                                        t = t + 1
                                        time.sleep(1)
                                else:
                                        break
                        output_list = []
                        if "data" in self.payload.keys() and self.payload["data"] is not None:
                                dict_data = self.payload['data']
                                for node_data, node, id in zip(dict_data, soc_nodes, soc_ids):
                                        node_data_double = node_data.copy()
                                        node_data_double.extend(node_data)
                                        id_output = {id: node_data_double}
                                        output_node = {node: id_output}
                                        output_list.append(output_node)
                        else:
                                logger.error(str(self.payload))
                        mqtt_send.MQTTExit()
                        mqtt_receive.MQTTExit()
                        #logger.debug("GESSCon Connector Output: %s", output_list)
                        return output_list
                except Exception as e:
                        logger.error(e)

        def on_msg_received(self, payload):
                payload = json.loads(payload)
                if "data" in payload.keys():
                        self.payload_set = True
                        self.payload = payload
#Dummy Data
"""price = [1.909825, 1.83985, 1.8422625, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.019425]
storage = {"storageUnits": [
        {
                "id": "Akku1",
                "bus1": "633",
                "phases": 3,
                "connection": "wye",
                "soc": 40,
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
                "soc": 20,
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
pv = [{'633':
               {'633.1.2': [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0,
                            0, 0, 0, 0]}},
      {'671': {'671.1.2.3': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 4]}}]
load = [{'633':
{'633.1': [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0],
'633.2': [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0],
'633.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 9]}},
{'671': {'671.1.2.3': [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0]}}]
Soc = [{'node_a6': {'ESS': {'SoC': 50.0, 'T_SoC': 25, 'id': 'Akku2', 'Battery_Capacity': 3, 'max_charging_power': 1.5, 'max_discharging_power': 1.5, 'charge_efficiency': 90, 'discharge_efficiency': 90}, 'Grid': {'Q_Grid_Max_Export_Power': 6, 'P_Grid_Max_Export_Power': 6}, 'PV': {'pv_name': 'PV_2'}}}]
g = GESSCon()
#Soc = g.get_ESS_data_format(storage)
start_date = datetime.datetime.strptime("2018.10.04 10:12:03", '%Y.%m.%d %H:%M:%S')
output = g.gesscon(load, pv, price, Soc)"""