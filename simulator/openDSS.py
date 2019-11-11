# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:05:36 2018

@author: Gustavo Aragon & Sisay Chala
"""


import logging
import math
import random
import re
import opendssdirect as dss
from data_management.redisDB import RedisDB

from profess.EV import EV
from profess.EV import Charger

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class OpenDSS:
    def __init__(self, grid_name):
        logger.info("Starting OpenDSS")
        logger.info("OpenDSS version: " + dss.__version__)
        logger.debug("grid_name in opendss "+str(grid_name))
        self.grid_name= str(grid_name)
        dss.run_command("Clear")
        self.redisDB = RedisDB()

        #dss.Basic.NewCircuit("Test 1")
        #dss.run_command("New circuit.{circuit_name}".format(circuit_name="Test 1"))
        #dat to erase 
        self.loadshapes_for_loads={} #empty Dictionary for laod_id:load_profile pairs
        self.EVs = {}
        self.Chargers = {}
        self.loadshapes_for_pv = {}
        self.dummyGESSCON=[{'633': {'633.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'671': {'671.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}]
        self.dummyPrice=[3] * 24
        logger.debug("Initialization of Opendss finished")

    def set_base_frequency(self, frequency):
        dss_string="Set DefaultBaseFrequency="+str(frequency)
        logger.debug(dss_string)
        dss.run_command(dss_string)

    def setNewCircuit(self, name, common):
        self.common = common
        try:
            for key, value in self.common.items():
                if key == "id":
                    common_id = value
                elif key == "base_kV":
                    common_base_kV = value
                elif key == "per_unit":
                    common_per_unit = value
                elif key == "phases":
                    common_phases_input = value
                elif key == "bus1":
                    common_bus1 = value
                elif key == "angle":
                    common_angle = value
                elif key == "MVAsc3":
                    common_MVAsc3 = value
                elif key == "MVAsc1":
                    common_MVAsc1 = value
                else:
                    logger.debug("key not processed "+str(key))
                    pass
            dss_string = "New circuit.{circuit_name} basekv={base_k_v} pu={per_unit} phases={phases} bus1={bus1}  Angle={angle} MVAsc3={mv_asc3} MVASC1={mv_asc1}".format(
                circuit_name=name,
                phases=common_phases_input,
                per_unit=common_per_unit,
                base_k_v= common_base_kV,
                mv_asc1= common_MVAsc1,
                mv_asc3= common_MVAsc3,
                bus1=common_bus1,
                angle=common_angle,
            )
            print(dss_string + "\n")
            dss.run_command(dss_string)
        except Exception as e:
            logger.error(e)

    def getActiveCircuit(self):
        return dss.Circuit.Name()

    def enableCircuit(self, name):
        logger.debug("Circuits available: " + str(dss.Basic.NumCircuits()))
        #dss.Circuit.Enable(str(name))
        dss.run_command(
            "Set Circuit = Circuit.{name}".format(name=name))
        logger.debug("Circuit "+str(name)+" activated")
        logger.debug("Name of the active circuit: " + str(self.getActiveCircuit()))

    def disableCircuit(self, name):
        dss.Circuit.Disable(name)
        logger.debug("Circuit "+str(name)+" disabled")
        logger.debug("Name of the active circuit: " + str(self.getActiveCircuit()))
        #dss.Circuit.Enable(name)
        #logger.debug("Name of the active circuit: " + str(self.getActiveCircuit()))

    def runNode13(self):
        dss.run_command('Redirect /usr/src/app/tests/data/13Bus/IEEE13Nodeckt.dss')

    def get_node_list(self):
        return dss.Circuit.AllNodeNames()

    def set_active_element(self, element_name):
        dss.Circuit.SetActiveElement(element_name)

    def get_transformer_names(self):
        return dss.Transformers.AllNames()

    def create_monitor(self, name, element_name, mode=1, terminal=None):
        dss_string="New Monitor."+str(name)+" element="+str(element_name)+" mode="+str(mode)#+" ppolar=no"
        if not terminal==None:
            dss_string=dss_string+" terminal="+str(terminal)
        logger.debug(dss_string)
        dss.run_command(dss_string)
        #dss.Monitors.Name(name)
        #logger.debug("Name " + str(dss.Monitors.Name()))
        #dss.Monitors.Element(element_name)
        #logger.debug("Element " + str(dss.Monitors.Element()))
        #dss.Monitors.Mode(mode)
        #logger.debug("Mode " + str(dss.Monitors.Mode()))
        logger.debug("Monitor "+str(name)+" for element "+str(element_name)+" in terminals "+str(terminal)+ " created")

    def get_monitor_terminals(self, name):
        #self.set_active_element(name)
        dss.Monitors.First()
        terminal=dss.Monitors.Terminal()
        logger.debug("Terminals "+str(terminal)+" for monitor "+str(dss.Monitors.Name()))
        return terminal

    def get_monitor_sample(self, name):
        dss.Monitors.Name(name)
        logger.debug("Name "+str(dss.Monitors.Name()))

        number_samples=dss.Monitors.SampleCount()
        #logger.debug("Number samples "+str(number_samples))
        dss.Monitors.Save()

        numChannels = 6#dss.Monitors.NumChannels()
        #logger.debug("Number channels " + str(numChannels))
        channel=[]
        for i in range(numChannels):
            #logger.debug("i "+str(i))
            channel.append(dss.Monitors.Channel(i+1))
            #logger.debug("Channel "+str(i) +str(channel[i]))

        S_total=[]
        for i in range(len(channel[0])):
            S_total.append(math.sqrt(math.pow(channel[0][i],2)+math.pow(channel[2][i],2)+math.pow(channel[4][i],2)))
        #logger.debug("S total "+str(S_total))
        #logger.debug("Number samples " + str(dss.Monitors.SampleCount()))

        return S_total


    def get_total_losses(self):
        return dss.Circuit.Losses()

    def get_total_power(self):
        return dss.Circuit.TotalPower()

    def setActivePowertoPV(self, pv_name, power):
        self.set_active_element(pv_name)
        #logger.debug("pv power " + str(power))
        if power >= 0:
            dss_string = "Generator." + str(pv_name) + ".kw=" + str(power)
            logger.debug("dss_string " + str(dss_string))
            dss.run_command(dss_string)
            return 0
        else:
            return 1

    def set_switch(self, line_name, opened):
        self.set_active_element(line_name)
        if opened:
            dss_string = "Line." + str(line_name) + ".Switch=y"
        else:
            dss_string = "Line." + str(line_name) + ".Switch=n"

        logger.debug("dss_string " + str(dss_string))
        dss.run_command(dss_string)

    def setSoCtoBatery(self, battery_name, soc_value):
        self.set_active_element(battery_name)
        dss_string = "Storage." + str(battery_name) + ".%stored=" + str(int(soc_value))
        logger.debug("dss_string " + str(dss_string))
        dss.run_command(dss_string)

    def setActivePowertoBatery(self,battery_name, power, max_power):
        self.set_active_element(battery_name)
        """storageName = "Storage.Akku1"
                dss.Circuit.SetActiveElement(storageName)

                print("kWhstored vor Solution.Solve: " + str(dss.Properties.Value("kWhstored")))
                print("kW vor Solution.Solve: " + str(dss.Properties.Value("kW")))
                print("Storage.Akku1.State: " + str(dss.Properties.Value("State")))
                print("Storage.Akku1.DispMode: " + str(dss.Properties.Value("DispMode")))
                
        if hours < 5:
                       dss.run_command('Storage.Akku1.kWrated = 15')  #power in kw to or from the battery (kWrated should be replaced with the value from PROFESS )
                       #dss.run_command('Storage.Akku1.kW = 15')  #power in kw to or from the battery
                       dss.run_command('Storage.Akku1.State = Discharging')
                   else:
                       dss.run_command('Storage.Akku1.kWrated = 30') # kWrated should be replaced with the value from PROFESS )
                       #dss.run_command('Storage.Akku1.kW = -5')
                       dss.run_command('Storage.Akku1.State = charging')"""
        #logger.debug("power " + str(power))
        if power < 0:
            percentage_charge=(abs(power)/max_power)*100
            dss_string = "Storage."+str(battery_name)+".%Charge="+str(int(percentage_charge))
            #dss_string = "Storage." + str(battery_name) + ".kW=" + str(power)
            logger.debug("dss_string " + str(dss_string))
            dss.run_command(dss_string)
            dss_string="Storage."+str(battery_name)+".State = Charging"
            logger.debug("dss_string " + str(dss_string))
            dss.run_command(dss_string)
        elif power == 0:
            dss_string = "Storage." + str(battery_name) + ".State = Idling"
            logger.debug("dss_string " + str(dss_string))
            dss.run_command(dss_string)
        else:

            percentage_charge = (power / max_power) * 100
            #dss_string = "Storage." + str(battery_name) + ".kW=" + str(power)
            dss_string = "Storage." + str(battery_name) + ".%Discharge=" + str(int(percentage_charge))
            logger.debug("dss_string " + str(dss_string))
            dss.run_command(dss_string)
            dss_string = "Storage." + str(battery_name) + ".State = Discharging"
            logger.debug("dss_string " + str(dss_string))
            dss.run_command(dss_string)

    def update_storage(self):
        dss.Circuit.UpdateStorage()

    def get_power_Transformer(self, name):
        self.set_active_element(name)
        logger.debug("Transformer name "+str(dss.Transformers.Name()))
        dss.Transformers.Wdg(1)
        logger.debug("Tranformer KVA "+str(dss.Transformers.kVA()))

        #dss_string = "? Transformer." + str(battery_name) + ".%stored"

    def setSoCBattery(self, battery_name, value):
        self.set_active_element(battery_name)
        dss_string="Storage."+str(battery_name)+".%stored="+str(value)
        logger.debug("dss_string "+str(dss_string))
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def getSoCfromBattery(self, battery_name):
        #logger.debug("Battery name "+str(battery_name))
        self.set_active_element(battery_name)
        dss_string="? Storage."+str(battery_name)+".%stored"
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def getCapacityfromBattery(self, battery_name):
        self.set_active_element(battery_name)
        dss_string="? Storage."+str(battery_name)+".kWhrated"
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def getMinSoCfromBattery(self, battery_name):
        self.set_active_element(battery_name)
        dss_string="? Storage."+str(battery_name)+".%reserve"
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def getkWfromBattery(self, battery_name):
        self.set_active_element(battery_name)
        logger.debug("name powers ESS " + str(dss.CktElement.Name()))
        logger.debug("powers ESS "+str(dss.CktElement.Powers()))
        dss_string="? Storage."+str(battery_name)+".kW"
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def getkWhStoredfromBattery(self, battery_name):
        self.set_active_element(battery_name)
        dss_string="? Storage."+str(battery_name)+".kWhstored"
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def getkWratedfromBattery(self, battery_name):
        self.set_active_element(battery_name)
        dss_string="? Storage."+str(battery_name)+".kWRated"
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def getStatefromBattery(self, battery_name):
        self.set_active_element(battery_name)
        dss_string="? Storage."+str(battery_name)+".State"
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def getBusfromBattery(self, battery_name):
        self.set_active_element(battery_name)
        dss_string="? Storage."+str(battery_name)+".bus1"
        #dss.run_command('? Storage.Akku1.%stored')
        return dss.run_command(dss_string)

    def get_YCurrents(self):
        return dss.Circuit.YCurrents()

    def get_all_element_losses(self):
        return dss.Circuit.AllElementLosses()

    def get_all_ckt_element_names(self):
        return dss.CktElement.AllPropertyNames()

    def get_all_ckt_powers(self):
        return dss.CktElement.Powers()

    def Stop(self):
        logger.debug("Stopping the simulator")


    def solveCircuitSolution(self):
        logger.info("Start solveCircuitSolution")

        try:
            dss.Solution.Solve()

        except Exception as e:
            logger.error("ERROR Running Solve!")
            logger.error(e)

        voltageList = dss.Circuit.AllBusMagPu()
        ycurrents = dss.Circuit.YCurrents()
        elementLosses = dss.Circuit.AllElementLosses()

        return (voltageList, ycurrents, elementLosses)

    def get_all_storage_names(self):
        return dss.Storages.AllNames()

    def get_all_load_names(self):
        return dss.Loads.AllNames()

    def get_all_pv_names(self):
        return dss.Generators.AllNames()

    def get_node_order(self):
        return dss.CktElement.NodeOrder()

    def get_load_powers(self):

        i_Power = dss.Loads.First()

        powers_from_loads = []
        while i_Power > 0:
            powers = dss.CktElement.Powers()
            node_order = self.get_node_order()
            list=[]
            count = 0

            if 1 in node_order:
                list.append(complex(powers[count], powers[count + 1]))
                count = count + 2
            else:
                list.append(0)
            if 2 in node_order:
                list.append(complex(powers[count], powers[count + 1]))
                count = count + 2
            else:
                list.append(0)
            if 3 in node_order:
                list.append(complex(powers[count], powers[count + 1]))
                count = count + 2
            else:
                list.append(0)


            if not list == []:
                powers_from_loads.append(list)

            #logger.debug("powers_from_loads "+str(list))
            i_Power = dss.Loads.Next()
        return powers_from_loads

    def get_pv_powers(self):

        i_Power = dss.Generators.First()
        powers_from_generators = []
        while i_Power > 0:
            powers = dss.CktElement.Powers()
            node_order = self.get_node_order()
            list = []
            count = 0

            if 1 in node_order:
                list.append(complex(powers[count], powers[count + 1]))
                count = count + 2
            else:
                list.append(0)
            if 2 in node_order:
                list.append(complex(powers[count], powers[count + 1]))
                count = count + 2
            else:
                list.append(0)
            if 3 in node_order:
                list.append(complex(powers[count], powers[count + 1]))
                count = count + 2
            else:
                list.append(0)

            if not list == []:
                powers_from_generators.append(list)

            #logger.debug("Currents from lines " + str(currents_from_lines))
            i_Power = dss.Generators.Next()
        return powers_from_generators

    def get_line_magnitude_currents(self):

        i_Line = dss.Lines.First()
        currents_from_lines = []
        while i_Line > 0:
            currents = dss.CktElement.CurrentsMagAng()
            len_currents = len(currents)
            #logger.debug("currents "+str(currents))
            if len_currents == 12:
                list=[currents[0], currents[2], currents[4]]
            elif len_currents == 8:
                list = [currents[0], currents[2]]
            elif len_currents == 4:
                list = [currents[0]]
            else:
                logger.error("Length of currents not supported")

            currents_from_lines.append(list)

            #logger.debug("Currents from lines " + str(currents_from_lines))
            i_Line = dss.Lines.Next()
        return currents_from_lines

    def get_line_currents(self):

        i_Line = dss.Lines.First()
        currents_from_lines = []
        while i_Line > 0:
            logger.debug("Currents "+str(dss.CktElement.Currents()))
            currents_from_lines.append(dss.CktElement.Currents())
            i_Line = dss.Lines.Next()
        return currents_from_lines


    def get_all_lines_names(self):
        return dss.Lines.AllNames()

    def get_YNodeOrder(self):
        return dss.Circuit.YNodeOrder()

    def get_line_losses(self):
        return dss.Circuit.LineLosses()

    def get_element_names(self):
        return dss.Circuit.AllElementNames()

    def get_node_names(self):
        return dss.Circuit.AllNodeNames()

    def get_number_of_elements(self):
        dss.Circuit.NumCktElements()
    #def setSolveMode(self, mode):
     #   self.mode=mode
      #  dss.run_command("Solve mode=" + self.mode)


    def getStartingHour(self):
        return dss.Solution.DblHour()

    def setStartingHour(self, hour):
        self.hour=hour
        dss.Solution.DblHour(self.hour)
        logger.debug("Starting hour "+str(dss.Solution.DblHour()))

    def getVoltageBases(self):
        return dss.Settings.VoltageBases()

    def setVoltageBases(self, bases_list):
        dss_string = "Set voltagebases = "+str(bases_list)
        logger.debug(dss_string + "\n")

        dss.run_command(dss_string)
        dss.run_command("CalcVoltageBases");


    def solutionConverged(self):
        return dss.Solution.Coverged()

    def getMode(self):
        return dss.Solution.ModeID()

    def setMode(self, mode):
        self.mode = mode
        dss.run_command("Set mode="+self.mode)
        #logger.debug("Solution mode "+str(dss.Solution.ModeID()))

    def getStepSize(self):
        return dss.Solution.StepSize()
    #Options: minutes or hours
    def setStepSize(self, time_step):
        self.time_step=time_step
        if "minutes" in self.time_step:
            dss.Solution.StepSizeMin(1)
        if "hours" in self.time_step:
            dss.Solution.StepSizeHr(1)
        #logger.debug("Simulation step_size " + str(dss.Solution.StepSize()))

    def getNumberSimulations(self):
        return dss.Solution.Number()

    def setNumberSimulations(self, number):
        self.number=number
        dss.Solution.Number(self.number)


    def setRegControls(self, regcontrols):

        self.regcontrols = regcontrols
        try:
            for element in self.regcontrols:
                #logger.info("RegControl:" + str(element))
                for k, v in element.items():
                    #logger.info("key:" + str(k) + ", value: "+ str(v))
                    #logger.info("value:" + str(v))
                    if k == "id":
                        Id = v
                    elif k == "transformer":
                        transformer_id = v
                    elif k == "winding":
                        winding_id = v
                    elif k == "vreg":
                        voltage_setting = v
                    elif k == "band":
                        bandwidth_volt = v
                    elif k == "ptration":
                        PT_Ratio = v
                    elif k == "ctprim":
                        CT_primary_rating_Amp = v
                    elif k == "r":
                        line_drop_compensator_R_Volt = v
                    elif k == "x":
                        line_drop_compensator_X_Volt = v
                    else:
                        break

                cmd = "New regcontrol.{rc_id} transformer={tra} winding={winding} vreg={vreg} band={band}  ptratio={ptratio} ctprim={ctprim} R={R} X={X}".format(
                rc_id=Id,
                tra=transformer_id,
                winding=winding_id,
                vreg=voltage_setting,
                band=bandwidth_volt,
                ptratio=PT_Ratio,
                ctprim=CT_primary_rating_Amp,
                R=line_drop_compensator_R_Volt,
                X=line_drop_compensator_X_Volt)

                #logger.info("run_command: " + cmd)
                logger.debug(cmd + "\n")
                dss.run_command(cmd)
            return 0
        except Exception as e:
            logger.error(e)
            return e

    def setTransformers(self, transformers):
        #logger.debug("Setting up the transformers")
        #logger.debug("transformers: " + str(transformers))
        self.transformers = transformers
        try:
            for element in self.transformers:
                #logger.info("element:" + str(element))
                bank=None
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    #logger.info("key:" + str(key))
                    #logger.info("value:" + str(value))
                    if key == "id":
                        transformer_id = value
                    elif key == "phases":
                        phases = value
                    elif key == "windings":
                        windings = value
                    elif key == "buses":  ###TODO in command
                        buses = value
                    elif key == "kvas":  ###TODO in command
                        kvas = value
                    elif key == "kvs":
                        kvs = value
                    elif key == "conns":
                        conns = value
                    elif key == "xsc_array":
                        xsc_array = value
                    elif key == "percent_rs":
                        percent_rs = value
                    elif key == "percent_load_loss":
                        percent_load_loss = value
                    elif key == "bank":
                        bank = value
                    elif key == "taps":
                        taps = value
                    else:
                        break

                self._id = transformer_id
                self._phases = phases
                self._windings = windings
                self._buses = buses
                self._kvas = kvas
                self._kvs = kvs
                self._conns = conns
                self._xsc_array = xsc_array
                self._percent_rs = percent_rs
                self._percent_load_loss = percent_load_loss
                self._bank = bank
                self._taps = taps


                portion_str = " bank={bank} " if bank != None else " "
                #portion_str = portion_str + " Basefreq={base_frequency} " if base_frequency != None else " "
                portion_str = portion_str + " Taps={taps} " if taps != None else " "
                portion_str = portion_str + " %LoadLoss={percent_load_loss} " if percent_load_loss != None else " "
                portion_str = portion_str + " %Rs={percent_rs} " if percent_rs != None else " "
                portion_str = portion_str + " Conns={conns} " if conns != None else " "

                dss_string = "New Transformer.{transformer_name} Phases={phases} Windings={winding} Buses={buses} kVAs={kvas} kVs={kvs} XscArray={xsc_array}" + portion_str + " "

                #logger.info("portion_str: " + portion_str)
                #logger.info("dss_string: " + dss_string)

                dss_string = dss_string.format(
                        transformer_name=self._id,
                        phases=self._phases,
                        winding=self._windings,
                        buses=self._buses,
                        kvas=self._kvas,
                        kvs=self._kvs,
                        conns=self._conns,
                        xsc_array=self._xsc_array,
                        percent_rs=self._percent_rs,
                        percent_load_loss=self._percent_load_loss,
                        bank=self._bank,
                        taps=self._taps)

                #logger.info("dss_string: " + dss_string)
                logger.debug(dss_string + "\n")
                dss.run_command(dss_string)
            return 0


            # !logger.debug("Transformer_names: " + str(dss.Transformers.AllNames()))
            # dss.run_command('Solve')
            # !logger.debug("Load SOLVED") #It does not get here. This is now good
            # logger.info("Load names: " + str(dss.Loads.AllNames())) #listed load names
        except Exception as e:
            logger.error(e)
            return e




    def getProfessLoadschapes(self,  start: int, size=24):
        # Preparing loadshape values in a format required by PROFESS
        # All loads are includet, not only the one having storage attached
        result = {}
        #logger.debug( "getProfessLoadschapes")
        try:
            for key, value in self.loadshapes_for_loads.items():
                load_id = key
                bus_name = value["bus"]
                #logger.debug("bus name " + str(bus_name))
                main_bus_name = bus_name.split('.', 1)[0]

                loadshape = value["loadshape"]
                #logger.debug("load_id: " + str(load_id) + " bus_name: " + str(bus_name)+ " main_bus_name: " + str(main_bus_name)+ "size"+ str(size)+" start "+str(start)+" loadshape_size: " + str(len(loadshape)))
                loadshape_portion=loadshape[int(start):int(start+size)]
                #print("loadshape_portion: " + str(loadshape_portion))
                bus_loadshape={bus_name:loadshape_portion}
                #print("bus_loadshape: " + str(bus_loadshape))

                if main_bus_name in result:
                    # extend existing  element
                    result[main_bus_name].update(bus_loadshape)
                else:
                    # add new element
                    result[main_bus_name] = bus_loadshape
        except Exception as e:
            logger.error(e)
        #print("resulting_loadshape_profess: " + str(result))
        return [result]


    def getProfessLoadschapesPV(self, start: int, size=24):
        # Preparing loadshape values in a format required by PROFESS
        # All loads are includet, not only the one having storage attached
        result = {}
        #logger.debug( "getPVLoadschapes")
        #logger.debug("node_name_list " + str(node_name_list))
        try:
            for key, value in self.loadshapes_for_pv.items():
                pv_id = key
                #logger.debug("key " + str(key))
                bus_name = value["bus"]
                main_bus_name = bus_name.split('.', 1)[0]
                #logger.debug("main bus name " + str(main_bus_name))
                #if main_bus_name in node_name_list:
                #print("bus_name: " + str(bus_name) + ", main_bus_name: " + str(main_bus_name))
                loadshape = value["loadshape"]
                #logger.debug("load_id: " + str(load_id) + " bus_name: " + str(bus_name)+ " main_bus_name: " + str(main_bus_name)+ " loadshape_size: " + str(len(loadshape)))
                loadshape_portion=loadshape[int(start):int(start+size)]
                #print("loadshape_portion: " + str(loadshape_portion))
                bus_loadshape={bus_name:loadshape_portion}
                #print("bus_loadshape: " + str(bus_loadshape))

                if main_bus_name in result:
                    # extend existing  element
                    result[main_bus_name].update(bus_loadshape)
                else:
                    # add new element
                    result[main_bus_name] = bus_loadshape

        except Exception as e:
            logger.error(e)
        #print("resulting_loadshape_profess: " + str(result))
        return [result]

    def setLoads(self, loads):
        #!logger.debug("Setting up the loads")
        self.loads=loads
        try:
            for element in self.loads:
                #logger.debug("element "+str(element))
                model = 1
                load_name = None
                bus_name = None
                num_phases = 3
                connection_type =  None
                voltage_kV = None
                power_kVar = None
                power_kW = None
                connection_type = None
                powerfactor = None
                for key, value in element.items():

                    #logger.debug("Key: "+str(key)+" Value: "+str(value))
                    if key=="id":
                        load_name=value
                    elif key=="bus":
                        bus_name=value
                    elif key=="phases":
                        num_phases=value
                    elif key == "connection_type":
                        connection_type = value
                    elif key == "model":
                        model = value
                    elif key == "kV":
                        voltage_kV = value
                    elif key == "kW":
                        power_kW = value
                    elif key == "kVar":
                        power_kVar = value
                    elif key == "powerfactor":
                        powerfactor = value
                    else:
                        logger.debug("key not processed "+str(key))


                #dss_string = "New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn={conn} Model={model} kV={voltage_kV} kW={voltage_kW} kVar={voltage_kVar} pf={power_factor} power_profile_id={shape}".format(
                dss_string="New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn={conn} Model={model} kV={voltage_kV} kW={voltage_kW}".format(
                load_name=load_name,
                bus_name=bus_name,
                num_phases=num_phases,
                conn=connection_type,
                model=model,
                voltage_kV=voltage_kV,
                voltage_kW=power_kW,
                )

                if not power_kVar == None:
                    dss_string = dss_string + " kVar=" + str(power_kVar)

                if not powerfactor == None:
                    dss_string = dss_string + " pf=" + str(powerfactor)
                #---------- chek for available loadschape and attach it to the load
                if load_name in self.loadshapes_for_loads:
                    dss_string = dss_string + " Yearly=" + self.loadshapes_for_loads[load_name]["name"]

                #logger.info("dss_string: " + dss_string)
                logger.debug(dss_string + "\n")
                dss.run_command(dss_string)
            return 0
        except Exception as e:
            logger.error(e)
            return e


    def setLineCodes(self, lines):
        #logger.debug("Setting up linecodes")
        #logger.debug("lines "+str(lines))
        self.linecodes=lines

        try:
            for element in self.linecodes:
                #logger.debug(str(element))
                cmatrix_str = " "
                linecode_name = None
                num_phases = None
                rmatrix = None
                xmatrix = None
                cmatrix = None
                units = None
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key=="id":
                        linecode_name=value
                    elif key=="nphases":
                        #logger.debug(str(key))
                        num_phases=value
                    elif key == "rmatrix":
                        rmatrix = value
                    elif key == "xmatrix":
                        xmatrix = value
                    elif key == "cmatrix":
                        cmatrix = value
                    elif key == "units":
                        units = value
                    else:
                        logger.debug("key not registered "+str(key))



                rmatrix_str = "{rmatrix[0][0]}" if num_phases == 1 \
                            else "{rmatrix[0][0]} | {rmatrix[1][0]}  {rmatrix[1][1]}" if num_phases == 2 \
                            else "{rmatrix[0][0]} | {rmatrix[1][0]}  {rmatrix[1][1]} | {rmatrix[2][0]} {rmatrix[2][1]} {rmatrix[2][2]}"
                xmatrix_str = "{xmatrix[0][0]}" if num_phases == 1 \
                            else "{xmatrix[0][0]} | {xmatrix[1][0]}  {xmatrix[1][1]}" if num_phases == 2 \
                            else "{xmatrix[0][0]} | {xmatrix[1][0]}  {xmatrix[1][1]} | {xmatrix[2][0]} {xmatrix[2][1]} {xmatrix[2][2]}"
                cmatrix_str = " " if cmatrix is None \
                                    else "cmatrix=(" + ( "{cmatrix[0][0]}" if num_phases == 1 \
                                    else "{cmatrix[0][0]} | {cmatrix[1][0]}  {cmatrix[1][1]}" if num_phases == 2 \
                                    else "{cmatrix[0][0]} | {cmatrix[1][0]}  {cmatrix[1][1]} | {cmatrix[2][0]} {cmatrix[2][1]} {cmatrix[2][2]}" ) \
                                    + ") "


                dss_string = "New linecode.{linecode_name} nphases={num_phases} rmatrix=(" + rmatrix_str + " ) xmatrix=(" + xmatrix_str + " ) " + cmatrix_str +  " units={units}"
                dss_string = dss_string.format(
                linecode_name = linecode_name,
                num_phases = num_phases,
                rmatrix = rmatrix,
                xmatrix = xmatrix,
                cmatrix = cmatrix,
                units = units
                )

                logger.debug(dss_string + "\n")
                dss.run_command( dss_string)
            return 0

        except Exception as e:
            logger.error(e)
            return e

    def setPowerLines(self, lines):
        #logger.debug("Setting up the powerlines")
        self.lines=lines
        try:
            for element in self.lines:
                linecode = None
                line_id = None
                bus1 = None
                bus2 = None
                length = None
                unitlength = None
                phases = 3  # default
                r1 = None
                r0 = None
                x1 = None
                x0 = None
                c1 = None
                c0 = None
                switch = None
                for key, value in element.items():
                    if key=="id":
                        line_id=value
                    elif key=="bus1":
                        bus1=value
                    elif key=="bus2":
                        bus2=value
                    elif key=="phases":
                        phases=value
                    elif key == "linecode":
                        linecode = value
                    elif key == "length":
                        length = value
                    elif key == "unitlength":
                        unitlength = value
                    elif key == "r1":
                        r1 = value
                    elif key == "r0":
                        r0 = value
                    elif key == "x1":
                        x1 = value
                    elif key == "x0":
                        x0 = value
                    elif key == "c1":
                        c1 = value
                    elif key == "c0":
                        c0 = value
                    elif key == "switch":
                        switch = value
                    else:
                        logger.debug("key not registered "+str(key))


                self.setPowerLine(line_id, phases, bus1, bus2, length, unitlength, linecode, r1, r0, x1, x0, c1, c0, switch)

            return 0

        except Exception as e:
            logger.error(e)
            return e
        

    def setPowerLine(self, id, phases, bus1, bus2, length=None, unitlength=None, linecode=None, r1=None, r0=None, x1=None, x0=None, c1=None, c0=None, switch=None):
        my_str = []
        if not r1 == None and linecode == None:
            # portion_str = "r1={r1} r0={r0} x1={x1} x0={x0} c1={c1}  c0={c0} " if switch == True else " length={length} units={unitlength} linecode={linecode} "
            my_str.append("r1={r1} ")

            if not r0 == None:
                my_str.append("r0={r0} ")
            if not x1 == None:
                my_str.append("x1={x1} ")
            if not x0 == None:
                my_str.append("x0={x0} ")
            if not c1 == None:
                my_str.append("c1={c1} ")
            if not c0 == None:
                my_str.append("c0={c0} ")
        else:
            if not linecode == None and r1 == None:
                my_str.append("linecode={linecode} ")
            else:
                # raise Exception("r1 and linecode cannot be entered at the same time")
                logger.error("r1 and linecode cannot be entered at the same time")
                return "r1 and linecode cannot be entered at the same time"
                # sys.exit(0)
                # raise ValueError('r1 and linecode cannot be entered at the same time')

        if not length == None:
            my_str.append("length={length} ")
        if not unitlength == None:
            my_str.append("units={unitlength} ")

        portion_str = ''.join(my_str)

        dss_string = "New Line.{line_id} bus1={bus1} bus2={bus2} phases={phases} " + portion_str + " "

        dss_string = dss_string.format(
            line_id=id,
            phases=phases,
            bus1=bus1,
            bus2=bus2,
            linecode=linecode,
            length=length,
            unitlength=unitlength,
            r1=r1,
            r0=r0,
            x1=x1,
            x0=x0,
            c1=c1,
            c0=c0,
        )
        if not switch == None:
            dss_string = dss_string + "switch=" + str(switch)
        logger.debug(dss_string + "\n")
        dss.run_command(dss_string)

        return 0

    def setXYCurves(self, xycurves):
        #!logger.info("Setting up the XYCurves")
        #!logger.debug("XY Curve in OpenDSS: " + str(xycurves))
        try:
            for element in xycurves:
                id = None
                npts = None
                xarray = None
                yarray = None
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key == "id":
                        id = value
                    if key == "npts":
                        npts = value
                    if key == "xarray":
                        xarray = value
                    if key == "yarray":
                        yarray = value
                self.setXYCurve(id, npts, xarray, yarray)
                #dss.run_command('Solve')
            return 0
        except Exception as e:
            logger.error(e)
            return e

    def setXYCurve(self, id, npts, xarray, yarray):
        # New XYCurve.panel_temp_eff npts=4  xarray=[0  25  75  100]  yarray=[1.2 1.0 0.8  0.6]
        # New XYCurve.panel_absorb_eff npts=4  xarray=[.1  .2  .4  1.0]  yarray=[.86  .9  .93  .97]
        dss_string = "New XYCurve.{id} npts={npts} xarray=[{xarray}] yarray=[{yarray}]".format(
            id = id,
            npts = npts,
            xarray = ','.join(['{:f}'.format(x) for x in xarray]),
            yarray = ','.join(['{:f}'.format(x) for x in yarray])
        )
        #!logger.info(dss_string)
        logger.debug(dss_string + "\n")
        dss.run_command(dss_string)



    def setPVshapes(self, pvs, powerprofiles, city, country, sim_days, profiles, profess):

        #!logger.debug("Setting up the loads")

        try:
            # ----------get_a_profile---------------#
            pv_profile_data = profiles.pv_profile(city, country, sim_days)
            for element in pvs:
                pv_name = element["id"]
                bus_name = element["bus1"]
                max_power= element["max_power_kW"]
                logger.debug("max power "+str(max_power))


                if 'power_profile_id' in element.keys() and element["power_profile_id"] is not None:

                    powerprofile_id = element['power_profile_id']
                    logger.debug("Power profile id found: " + str(powerprofile_id))
                    pv_profile = []
                    for powerprofile in powerprofiles:
                        if (powerprofile_id == powerprofile['id']):
                            loadshape_id = powerprofile_id
                            items = powerprofile['items']
                            normalize = powerprofile['normalized']
                            useactual = powerprofile['use_actual_values']
                            interval = powerprofile['interval']
                            multiplier = 1
                            if 'multiplier' in powerprofile.keys() and powerprofile['multiplier'] is not None:
                                multiplier = powerprofile['multiplier']
                            if powerprofile['interval']:
                                items = [item * multiplier for item in items]
                            elif powerprofile['m_interval']:
                                items = [item * multiplier for item in items[::60]]
                            elif powerprofile['s_interval']:
                                items = [item * multiplier for item in items[::3600]]
                            pv_profile.extend(items)
                    # --------store_profile_for_line----------#
                    self.loadshapes_for_pv[pv_name] = {"name": loadshape_id, "bus": bus_name,"loadshape": pv_profile}
                else:
                    loadshape_id = "Shape_"+pv_name
                    pv_profile = [i for i in pv_profile_data]
                    normalize = True
                    useactual = False
                    # --------store_profile_for_line----------#
                    self.loadshapes_for_pv[pv_name] = {"name": loadshape_id, "bus": bus_name, "loadshape": pv_profile}

                    self.setLoadshape(loadshape_id, sim_days * 24, 1, pv_profile, normalize, useactual)

            return 0

        except Exception as e:
            logger.error(e)
            return e

    def setLoadshapes(self, loads, powerprofiles, sim_days, profiles, profess):

        try:
            for element in loads:
                interval = 1
                npts = 0
                mult = []
                load_name = element["id"]
                bus_name = element["bus"]
                #max_power = element["kW"]
                set_load_shape_flag = False

                if 'power_profile_id' in element.keys() and element["power_profile_id"] is not None:
                    powerprofile_id = element['power_profile_id']
                    if not powerprofile_id:
                        logger.debug("power profile = False")
                        continue
                    elif bool(re.search("profile_\d", powerprofile_id)):
                        logger.debug("2 ")
                        int_value = int(powerprofile_id[8:])
                        load_profile_data = profiles.load_profile(type="residential", randint=int_value, days=sim_days)
                        if not load_profile_data:
                            logger.error("No load profile data found for %s", (load_name))
                            continue
                        load_profile_data = [i for i in load_profile_data]

                        npts = len(load_profile_data)
                        mult = load_profile_data
                        normalize = True
                        useactual= False
                        loadshape_id = "Lsp_" + str(int_value)
                        set_load_shape_flag = True
                    else:
                        logger.debug("4 ")
                        load_profile_data = []
                        for powerprofile in powerprofiles:
                            if (powerprofile_id == powerprofile['id']):
                                loadshape_id = powerprofile_id
                                items = powerprofile['items']
                                interval = powerprofile['interval']
                                multiplier = 1
                                if 'multiplier' in powerprofile.keys() and powerprofile['multiplier'] is not None:
                                    multiplier = powerprofile['multiplier']
                                if powerprofile['interval']:
                                    items = [item * multiplier  for item in items]
                                elif powerprofile['m_interval']:
                                    items = [item * multiplier  for item in items[::60]]
                                elif powerprofile['s_interval']:
                                    items = [item * multiplier  for item in items[::3600]]
                                load_profile_data.extend(items)
                                set_load_shape_flag = False


                else:
                    logger.debug("5 ")
                    # ----------get_a_profile---------------#
                    randint_value = random.randrange(0, 475)

                    load_profile_data = profiles.load_profile(type="residential", randint=randint_value, days=sim_days)

                    load_profile_data = [i for i in load_profile_data]
                    npts = len(load_profile_data)
                    mult = load_profile_data
                    normalize = True
                    useactual = False
                # --------store_profile_for_line----------#
                    loadshape_id = "Lsp_" + str(randint_value)
                    set_load_shape_flag = True

                self.loadshapes_for_loads[load_name] = {"name": loadshape_id, "bus": bus_name,
                                                        "loadshape": load_profile_data}

                if set_load_shape_flag:
                    self.setLoadshape(loadshape_id, npts, interval, mult, normalize, useactual)
            return 0
        except Exception as e:
            logger.error(e)
            return e


    def setLoadshape(self, id, npts, interval, mult, normalize=True, useactual=False):
        try:
            logger.debug("New Loadshape." + id)
            my_str=[]
            if normalize:
                my_str.append("Action=Normalize ")
            if useactual:
                my_str.append("useactual = true ")
            else:
                my_str.append("useactual = false ")

            portion_str = ''.join(my_str)

            dss_string = "New Loadshape.{id} npts={npts} interval={interval} mult=({mult}) "+ portion_str + " "
            dss_string = dss_string.format(
                id=id,
                npts=npts,
                interval=interval,
                mult=' '.join(['{:f}'.format(x) for x in mult])
            )


            dss.run_command(dss_string)
            logger.debug(dss_string)
            dss_string = "? Loadshape." + str(id) + ".mult"

            result = dss.run_command(dss_string)
            logger.debug("Loadshape." + str(id) + ".mult count:" +  str(len((str(result)).split(" "))) + "\n")
            return 0
        except Exception as e:
            logger.error(e)



    def setTshapes(self, tshapes):

        try:
            for element in tshapes:
                id = None
                npts = None
                interval = None
                temp = None
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key == "id":
                        id = value
                    if key == "npts":
                        npts = value
                    if key == "interval":
                        interval = value
                    if key == "temp":
                        temp = value
                self.setTshape(id, npts, interval, temp)

            #dss.run_command('Solve')
                #!logger.info("TShape names: " + str(dss.LoadShape.AllNames()))
        except Exception as e:
            logger.error(e)

    def setTshape(self, id, npts, interval, temp):
        # New Tshape.assumed_Temp npts=24 interval=1 temp=[10, 10, 10, 10, 10, 10, 12, 15, 20, 25, 30, 30  32 32  30 28  27  26  25 20 18 15 13 12]
        dss_string = "New Loadshape.{id} npts={npts} interval={interval} temp=[{temp}]".format(
            id=id,
            npts=npts,
            interval=interval,
            temp=','.join(['{:f}'.format(x) for x in temp])
        )
        #!logger.info(dss_string)
        logger.debug(dss_string + "\n")
        dss.run_command(dss_string)

    def setPhotovoltaics(self, photovoltaics):
        #!logger.debug("Setting up the Photovoltaics")
        try:
            for element in photovoltaics:
                id = None
                phases = None
                bus1 = None
                voltage = None
                power = None
                powerunit= None
                effcurve = None
                ptcurve = None
                daily = None
                tdaily = None
                pf = 1 #default value
                temperature = None
                irrad = None
                pmpp = None
                for key, value in element.items():
                    if key == "id":
                        id = value
                    elif key == "phases":
                        phases = value
                    elif key == "bus1":
                        bus1 = value
                    elif key == "kV":
                        voltage = value
                    elif key == "power":
                        power = value
                    elif key == "max_power_kW":
                        pmpp = value
                    elif key == "effcurve":
                        effcurve = value
                    elif key == "ptcurve":
                        ptcurve = value
                    elif key == "daily":
                        daily = value
                    elif key == "tdaily":
                        tdaily = value
                    elif key == "powerfactor":
                        pf = value
                    elif key == "temperature":
                        temperature = value
                    elif key == "irrad":
                        irrad = value
                    else:
                        logger.debug("keys not registered "+str(key))

                self.setPhotovoltaic(id, phases, bus1, voltage, power, effcurve, ptcurve, daily, tdaily, pf, temperature, irrad, pmpp)
                #!dss.run_command('Solve')
                #!logger.debug("Photovoltaics: " + str(dss.PVsystems.AllNames()))
            return 0
        except Exception as e:
            logger.error(e)
            return e

    def setPhotovoltaic(self, id, phases, bus1, voltage, power, effcurve, ptcurve, daily, tdaily, pf, temperature, irrad, pmpp):
        dss_string = "New Generator.{id} phases={phases} bus1={bus1} kV={voltage} kW={pmpp} PF={pf} model=1".format(
            id=id,
            phases=phases,
            bus1=bus1,
            voltage=voltage,
            pmpp=pmpp,
            pf=pf,
            ptcurve=ptcurve,
        )

        # ---------- chek for available loadschape and attach it to the load
        if id in self.loadshapes_for_pv:
            dss_string = dss_string + " Yearly=" + str(self.loadshapes_for_pv[id]["name"])

        logger.debug(dss_string + "\n")
        dss.run_command(dss_string)

    def setChargingStations(self, charging_stations):
        import sys
        #logger.debug("charging stations "+str(charging_stations))

        try:
            for element in charging_stations:
                id = None
                bus1 = None
                phases = None
                connection = "wye"
                soc = 40 #! defalt value
                dod = 20 #! defalt value
                kv = None
                kw_rated = 0
                kwh_rated = 50 #! defalt value
                kwh_stored = 50 #! defalt value
                charge_efficiency = 90 #! defalt value
                discharge_efficiency = 90 #! defalt value
                powerfactor = 1 #! defalt value
                type_application = "residential"


                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key == "id":
                        id = value
                    elif key == "bus":
                        bus1 = value
                    elif key == "phases":
                        phases = value
                    elif key == "connection":
                        connection = value
                    #elif key == "soc":
                        #soc = value
                    elif key == "min_soc":
                        dod = value
                    elif key == "max_charging_power_kW":
                        kw_rated = value
                    elif key == "kV":
                        kv = value

                    #elif key == "storage_capacity":
                        #kwh_rated = value
                    #elif key == "kwh_stored":
                        #kwh_stored = value
                    elif key == "charging_efficiency":
                        charge_efficiency = value
                    elif key == "type_application":
                        type_application = value
                    #elif key == "discharge_efficiency":
                        #discharge_efficiency = value
                    elif key == "powerfactor":
                        powerfactor = value
                    elif key == "hosted_ev":
                        ev_object = []
                        for evs in value:
                            self.EVs[evs["id"]] = EV(evs["id"], evs["battery_capacity_kWh"], evs["SoC"], evs["consumption_in_kW_pro_100_km"])
                            if "unplugged_mean" in evs.keys() and "unplugged_mean_std" in evs.keys():
                                self.EVs[evs["id"]].set_unplugged_values(evs["unplugged_mean"], evs["unplugged_mean_std"])
                            if "plugged_mean" in evs.keys() and "plugged_mean_std" in evs.keys():
                                self.EVs[evs["id"]].set_plugged_values(evs["plugged_mean"], evs["plugged_mean_std"])
                            ev_object.append(self.EVs[evs["id"]])
                    else:
                        logger.debug("key not registered: "+str(key))

                logger.debug("type_application "+str(type_application))
                self.Chargers[id] = Charger(id, kw_rated, ev_object, kw_rated, type_application, bus1, charge_efficiency)
                ev_unit = self.Chargers[id].get_EV_connected()[0]
                self.Chargers[id].set_ev_plugged(ev_unit)



                #logger.debug("bus 2 "+str(bus2))

                list_ev = self.Chargers[id].get_EV_connected()
                logger.debug("list ev "+str(list_ev))
                counter = 1
                for ev in list_ev:
                    bus2 = bus1 + "_"+str(counter)
                    self.setPowerLine("Line_"+ev.get_id(), phases, bus1, bus2, r1=0.0001, r0=0.0001, x1=0, x0=0, c1=0, c0=0, switch="y")
                    self.setStorage("ESS_"+ev.get_id(),bus2, phases, connection, ev.get_SoC(),min_soc=0, kv=kv, kw_rated=kw_rated, kwh_rated=ev.get_Battery_Capacity(), kwh_stored=ev.get_Battery_Capacity(), charge_efficiency=charge_efficiency, discharge_efficiency=1, powerfactor=powerfactor)
                    counter = counter + 1

            return 0
        except Exception as e:
            logger.error(e)
            return e

    def get_chargers(self):
        return self.Chargers

    def setStorages(self, storage):
        #logger.info("Setting up the Storages")
        try:
            for element in storage:
                id = None
                bus1 = None
                phases = None
                connection = "wye"
                soc = 100 #! defalt value
                min_soc = 20 #! defalt value
                kv = None
                kw_rated = 0
                kwh_rated = 50 #! defalt value
                kwh_stored = 50 #! defalt value
                charge_efficiency = 90 #! defalt value
                discharge_efficiency = 90 #! defalt value
                powerfactor = 1 #! defalt value

                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key == "id":
                        id = value
                    elif key == "bus1":
                        bus1 = value
                    elif key == "phases":
                        phases = value
                    elif key == "connection":
                        connection = value
                    elif key == "soc":
                        soc = value
                    elif key == "min_soc":
                        min_soc = value
                    elif key == "max_charging_power":
                        kw_rated = value
                    elif key == "kv":
                        kv = value
                    elif key == "kw_rated":
                        kw_rated = value
                    elif key == "storage_capacity":
                        kwh_rated = value
                    elif key == "kwh_stored":
                        kwh_stored = value
                    elif key == "charge_efficiency":
                        charge_efficiency = value
                    elif key == "discharge_efficiency":
                        discharge_efficiency = value
                    elif key == "powerfactor":
                        powerfactor = value
                    else:
                        logger.debug("key not registered: "+str(key))
                self.setStorage(id, bus1, phases, connection, soc, min_soc, kv, kw_rated, kwh_rated, kwh_stored, charge_efficiency, discharge_efficiency, powerfactor)
                #!dss.run_command('Solve')
                #!logger.info("Storage names: " + str(dss.Circuit.AllNodeNames()))
            return 0
        except Exception as e:
            logger.error(e)
            return e


    def setStorage(self, id, bus1, phases, connection, soc, min_soc, kv, kw_rated, kwh_rated, kwh_stored, charge_efficiency, discharge_efficiency, powerfactor):

        dss_string="New Storage.{id} bus1={bus1}  phases={phases} conn={connection} %stored={soc} %reserve={min_soc} kV={kv}  kWhrated={kwh_rated} %EffCharge={charge_efficiency} %EffDischarge={discharge_efficiency} pf={powerfactor}".format(
                id=id,
            bus1=bus1,
            phases=phases,
            connection=connection,
            soc=soc,
            min_soc=min_soc,
            kv=kv,
            kwh_rated=kwh_rated,
            kwh_stored=kwh_stored,
            charge_efficiency=charge_efficiency,
            discharge_efficiency=discharge_efficiency,
            powerfactor=powerfactor
        )


        dss_string = dss_string + " TimeChargeTrigger=-1 "
        if not kw_rated == None:
            dss_string = dss_string + " kWrated="+str(kw_rated)

        logger.debug(dss_string)
        dss.run_command(dss_string)
        self.setSoCBattery(id, soc)

    def setCapacitors(self, capacitors):

        self.capacitors=capacitors
        try:
            for element in self.capacitors:
                #logger.debug("Element: "+str(element))
                id = None
                bus = None
                phases= 3
                voltage_kV = None
                power_kVar = None

                for key, value in element.items():
                    #logger.debug("Key: "+str(key)+" Value: "+str(value))
                    if key=="id":
                        id=value
                    elif key=="bus":
                        bus=value
                    elif key=="phases":
                        phases=value 
                    elif key == "kVAR":
                        power_kVar = value
                    elif key == "kV":
                        voltage_kV = value
                    else:
                        logger.debug("key nor registered "+str(key))

                dss_string = "New Capacitor.{capacitor_name} Bus1={bus_name}  Phases={num_phases} kV={voltage_kV} kVar={voltage_kVar}".format(
                capacitor_name=id,
                bus_name=bus,
                num_phases=phases,
                voltage_kV=voltage_kV,
                voltage_kVar=power_kVar
                )

                logger.debug(dss_string + "\n")
                dss.run_command(dss_string)

            return 0
        except Exception as e:
            logger.error(e)
            return e
