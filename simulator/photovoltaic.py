import logging, os, json

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Photovoltaic:

    def __init__(self,id, node, phases, voltage, max_power, max_q_power, powerfactor, control_strategy="ofw"):
        self.id =id
        self.voltage = voltage
        self.node =  node
        self.max_power = max_power
        self.max_q_power = max_q_power
        self.pf = powerfactor
        self.control = Control_strategy(control_strategy)
        self.momentary_power = 0
        self.output_power = 0
        self.output_q_power = 0
        logger.debug("PV "+str(self.id)+" created")

    def get_name(self):
        return self.id

    def get_node_base(self):
        node=self.node
        if "." in node:
            node.split(".")[0]
        return node

    def get_node(self):
        return self.node

    def get_control_strategy(self):
        return self.control

    def set_control_strategy(self, control_strategy):
        self.control = Control_strategy(control_strategy)

    def get_max_q_power(self):
        return self.max_q_power

    def set_max_q_power(self, max_power):
        self.max_q_power = max_power

    def get_max_power(self):
        return self.max_power

    def set_max_power(self, max_power):
        self.max_power = max_power

    def get_momentary_power(self):
        return self.momentary_power

    def set_momentary_power(self, power):
        self.momentary_power = power

    def set_output_power(self, output_power):
        self.output_power = output_power

    def get_output_power(self):
        return self.output_power

    def set_output_q_power(self, output_power):
        self.output_q_power = output_power

    def get_output_q_power(self):
        return self.output_q_power


class Control_strategy:

    def __init__(self, name):
        self.name = name
        if name == "limit_power":
            self.strategy = Limit_power()
        elif name == "volt-watt":
            self.strategy = Volt_Watt()
        elif name == "volt-var":
            self.strategy = Volt_Var()
        elif name == "ofw":
            self.strategy = Ofw()
        else:
            return "Control strategy not implemented"

    def get_strategy(self):
        return self.strategy

    def get_name(self):
        return self.name


class Ofw:
    def __init__(self):
        self.power =  0
        self.name = "ofw"

    def get_name(self):
        return self.name

    def set_control_power(self, power):
        self.power = power

    def get_control_power(self):
        return self.power

class Limit_power:
    def __init__(self):
        self.percentage  = 50
        self.name = "limit_power"

    def get_name(self):
        return self.name

    def get_percentage(self):
        return self.percentage

    def set_percentage(self, percentage_max_power):
        self.percentage = percentage_max_power


class Volt_Watt:
    def __init__(self):
        self.percentage = 50

        self.name = "volt_watt"

    def get_name(self):
        return self.name

    def get_percentage(self):
        return self.percentage

    def set_percentage(self, percentage_max_power):
        self.percentage = percentage_max_power

class Volt_Var:
    def __init__(self):
        self.percentage = 50

        self.name = "volt_var"

    def get_name(self):
        return self.name

    def get_percentage(self):
        return self.percentage

    def set_percentage(self, percentage_max_power):
        self.percentage = percentage_max_power