import logging, os, json

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Photovoltaic:

    def __init__(self,id, phases, voltage, max_power, powerfactor, control_strategy="profess"):
        self.id =id
        self.voltage = voltage
        self.max_power = max_power
        self.pf = powerfactor
        self.control = control_strategy
        self.momentary_power = 0
        logger.debug("PV "+str(self.id)+" created")

    def get_name(self):
        return self.id

    def get_control_strategy(self):
        return self.control

    def set_control_strategy(self, control_strategy):
        self.control = control_strategy

    def get_max_power(self):
        return self.max_power

    def set_max_power(self, max_power):
        self.max_power = max_power

    def get_momentary_power(self):
        return self.momentary_power

    def set_momentary_power(self, power):
        self.momentary_power = power

