import logging, os, json
from profess.MonteCarloSimulator import Uncertainty

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class EV:

    def __init__(self,id, Battery_Capacity, SoC, consumption_pro_100_km):
        self.Battery_Capacity = Battery_Capacity
        self.consumption = consumption_pro_100_km
        self.Soc = SoC
        self.id = id
        self.uncertainty = Uncertainty()
        self.position_profile = None
        self.unplugged_mean = 7.32
        self.unplugged_mean_std = 0.78
        self.plugged_mean = 18.76
        self.plugged_mean_std = 1.3
        logger.debug("EV "+str(self.id)+" created")

    def get_plugged_values(self):
        return (self.plugged_mean, self.plugged_mean_std)

    def get_unplugged_values(self):
        return (self.unplugged_mean, self.unplugged_mean_std)

    def set_plugged_values(self, plugged_mean, plugged_mean_std):
        self.plugged_mean = plugged_mean
        self.plugged_mean_std = plugged_mean_std

    def set_unplugged_values(self, unplugged_mean, unplugged_mean_std):
        self.unplugged_mean = unplugged_mean
        self.unplugged_mean_std = unplugged_mean_std

    def get_id(self):
        return self.id

    def get_SoC(self):
        return self.Soc

    def set_SoC(self, value):
        if value < 0 or value >1:
            return 0
        else:
            self.Soc = value
            return 1

    def get_Battery_Capacity(self):
        return self.Battery_Capacity

    def calculate_S0C_next_timestep(self, P_ev, number_km_driven):
        #number_km = 5
        number_km = number_km_driven
        #consumption_for_x_km = (11.7 * number_km) / 100  # 11.7 kwh/100km consumption for VW Eup
        consumption_for_x_km = self.consumption * number_km
        # logger.debug("consumption for " +str(number_km)+" is "+str(consumption_for_x_km))
        #Capacity = 18.700  # kWh
        if P_ev == -1:
            # logger.debug("car " + str(car) + " power " + str(power))
            value = (self.Soc - (consumption_for_x_km / self.Battery_Capacity))
            logger.debug("value "+str(value))
            if value < 0:
                return 0
            else:
                return value
        else:
            value = (self.Soc + (P_ev / self.Battery_Capacity))
            logger.debug("value " + str(value))
            if value > 1:
                return 1
            else:
                return value

    def get_position_profile(self):
        return self.position_profile

    def calculate_position(self, horizon, repetition):
        self.position_profile = self.uncertainty.monte_carlo_simulation(3600, horizon, repetition, self.unplugged_mean, self.unplugged_mean_std,
                                                               self.plugged_mean, self.plugged_mean_std, 1)
        #logger.debug("position profile "+str(self.position_profile))



class Charger:
    def __init__(self, Max_Capacity, list_EV_connected, type_application):
        self.Max_Capacity = Max_Capacity
        self.EV_connected = list_EV_connected
        self.type_application = type_application

    def get_type_application(self):
        return self.type_application

    def set_EV_connected(self, EV_connected):
        self.EV_connected.append(EV_connected)

    def get_EV_connected(self):
        return  self.EV_connected

    def get_Max_Capacity(self):
        return self.Max_Capacity