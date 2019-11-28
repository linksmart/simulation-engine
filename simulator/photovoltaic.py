import logging, os, json

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Photovoltaic:

    def __init__(self,id, node, phases, voltage, max_power, max_q_power, powerfactor, control_strategy="ofw", meta=None):
        self.id =id
        self.voltage = voltage
        self.node =  node
        self.max_power = max_power
        self.max_q_power = max_q_power
        self.pf = powerfactor
        self.control = Control_strategy(control_strategy)
        if not meta== None:
            for control_setting, value_control in meta.items():
                if control_strategy == "limit_power":
                    if control_setting == "percentage_max_power":
                        self.control.get_strategy().set_percentage(value_control)
                    if control_setting == "sensitivity_factor":
                        self.control.get_strategy().set_sensitivity_factor(value_control)
                if control_strategy == "volt-watt" or control_strategy == "volt-var":
                    if control_setting == "min_vpu_high":
                        self.control.get_strategy().set_min_vpu_high(value_control)
                    if control_setting == "max_vpu_high":
                        self.control.get_strategy().set_max_vpu_high(value_control)
                if control_strategy == "volt-var":
                    if control_setting == "min_vpu_low":
                        self.control.get_strategy().set_min_vpu_low(value_control)
                    if control_setting == "max_vpu_low":
                        self.control.get_strategy().set_max_vpu_low(value_control)


        self.momentary_power = 0
        self.output_power = 0
        self.output_q_power = 0
        self.use_in_percent = []
        self.meta = meta
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

    def get_use_percent(self):
        return self.use_in_percent

    def set_use_percent(self, percentage_value):
        if percentage_value > 100:
            percentage_value = 100
        if percentage_value < 0:
            percentage_value = 0
        self.use_in_percent.append(percentage_value)


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
        elif name == "no_control":
            self.strategy = No_control()
        else:
            return "Control strategy not implemented"

    def get_strategy(self):
        return self.strategy

    def get_name(self):
        return self.name


class No_control:
    def __init__(self):
        self.power =  0
        self.name = "no_control"

    def get_name(self):
        return self.name

    def set_control_power(self, power):
        self.power = power

    def get_control_power(self):
        return self.power

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
        self.sensitivity_factor = 1
        self.name = "limit_power"

    def get_name(self):
        return self.name

    def get_percentage(self):
        return self.percentage

    def set_percentage(self, percentage_max_power):
        self.percentage = percentage_max_power

    def get_sensitivity_factor(self):
        return self.sensitivity_factor

    def set_sensitivity_factor(self, sensitivity_factor):
        self.sensitivity_factor = sensitivity_factor

    def set_control_power(self, power):
        self.power = power

    def get_control_power(self):
        return self.power


class Volt_Watt:
    def __init__(self):
        self.min_vpu_low = 1.06
        self.max_vpu_low = 1.1
        self.name = "volt-watt"

    def get_name(self):
        return self.name

    def get_min_vpu_high(self):
        return self.min_vpu_high

    def set_min_vpu_high(self, min_vpu_high):
        self.min_vpu_high = min_vpu_high

    def get_max_vpu_high(self):
        return self.max_vpu_high

    def set_max_vpu_high(self, max_vpu_high):
        self.max_vpu_high = max_vpu_high

    def set_control_power(self, power):
        self.power = power

    def get_control_power(self):
        return self.power

class Volt_Var:
    def __init__(self):
        self.min_vpu_low = 0.92
        self.max_vpu_low = 0.98
        self.min_vpu_high = 1.02
        self.max_vpu_high = 1.08
        self.name = "volt-var"

    def get_name(self):
        return self.name

    def get_min_vpu_low(self):
        return self.min_vpu_low

    def set_min_vpu_low(self, min_vpu_low):
        self.min_vpu_low = min_vpu_low

    def get_max_vpu_low(self):
        return self.max_vpu_low

    def set_max_vpu_low(self, max_vpu_low):
        self.max_vpu_low = max_vpu_low

    def get_min_vpu_high(self):
        return self.min_vpu_high

    def set_min_vpu_high(self, min_vpu_high):
        self.min_vpu_high = min_vpu_high

    def get_max_vpu_high(self):
        return self.max_vpu_high

    def set_max_vpu_high(self, max_vpu_high):
        self.max_vpu_high = max_vpu_high

    def set_control_power(self, power):
        self.power = power

    def get_control_power(self):
        return self.power