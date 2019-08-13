# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:05:36 2018

@author: Gustavo Aragon & Sisay Chala
"""


import logging
import random
import opendssdirect as dss
#from profess.Profess import *

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class OpenDSS:
    def __init__(self, grid_name):
        logger.info("Starting OpenDSS")
        logger.info("OpenDSS version: " + dss.__version__)
        self.grid_name=grid_name
        dss.run_command("Clear")
        dss.run_command("Set DefaultBaseFrequency=60")
        #dss.Basic.NewCircuit("Test 1")
        #dss.run_command("New circuit.{circuit_name}".format(circuit_name="Test 1"))
        #dat to erase 
        self.loadshapes_for_loads={} #empty Dictionary for laod_id:load_profile pairs
        self.loadshapes_for_pv = {}
        self.profess=None
        self.dummyGESSCON=[{'633': {'633.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}, {'671': {'671.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}]
        self.dummyPrice=[3] * 24
        self.dummyPV = [{'633': {'633.1.2.3': [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]}}, {
            '671': {'671.1.2.3': [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]}}, {
                    '634': {'634.1.2.3': [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]}}]

    def setNewCircuit(self, name, common):
        self.common = common
        try:
            for key, value in self.common.items():
                if key == "id":
                    common_id = value
                elif key == "base_k_v":
                    common_base_kV = value
                elif key == "per_unit":
                    common_per_unit = value
                elif key == "phases":
                    common_phases_input = value
                elif key == "bus1":
                    common_bus1 = value
                elif key == "angle":
                    common_angle = value
                elif key == "mv_asc3":
                    common_MVAsc3 = value
                elif key == "mv_asc1":
                    common_MVAsc1 = value
                else:
                    logger.debug("key not processed "+str(key))
                    pass
            dss_string = "New circuit.{circuit_name} basekv={base_k_v} pu={per_unit} phases={phases} bus1={bus1}  Angle={angle} MVAsc3={mv_asc3} MVASC1={mv_asc1}".format(
                circuit_name=common_id,
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

    def solveCircuitSolution(self):
        logger.info("Start solveCircuitSolution")
        #logger.info("Start solveCircuitSolution " + str(dss.Loads.AllNames()))

        """storageName = "Storage.Akku1"
        dss.Circuit.SetActiveElement(storageName)

        print("kWhstored vor Solution.Solve: " + str(dss.Properties.Value("kWhstored")))
        print("kW vor Solution.Solve: " + str(dss.Properties.Value("kW")))
        print("Storage.Akku1.State: " + str(dss.Properties.Value("State")))
        print("Storage.Akku1.DispMode: " + str(dss.Properties.Value("DispMode")))
        """


        try:
            #dss. dss.run_command("calcv ")
            #dss.Circuit.SetActiveElement(storageName)
            #dss.Properties.Name("kW")
            #dss.Properties.Value(15)




            """if hours < 5:
                dss.run_command('Storage.Akku1.kWrated = 15')  #power in kw to or from the battery (kWrated should be replaced with the value from PROFESS )
                #dss.run_command('Storage.Akku1.kW = 15')  #power in kw to or from the battery
                dss.run_command('Storage.Akku1.State = Discharging')
            else:
                dss.run_command('Storage.Akku1.kWrated = 30') # kWrated should be replaced with the value from PROFESS )
                #dss.run_command('Storage.Akku1.kW = -5')
                dss.run_command('Storage.Akku1.State = charging')"""


            dss.Solution.Solve()

        except:
            logger.info("ERROR Running Solve!")



        """print("Result2 %stored: " + str(dss.Properties.Value("%stored")))
        print("Result1 %stored: " + str(dss.run_command('? Storage.Akku1.%stored')))
        """
        #print("Result1 kWhstored: " + str(dss.run_command('? Storage.Akku1.kWhstored')))
        #print("Result2 kWhstored: " + str(dss.Properties.Value("kWhstored")))

        #dss.Circuit.s setActiveElement(storageName)
        # dss.ActiveCircuit.setActiveElement(storageName)
        #print(dss.CktElement.AllPropertyNames())
        #energy_ESS=[]
        #energyStored = dss.CktElement.Variable("%stored",energy_ESS)
        #print("The result of ESS energy",str(energy_ESS))
        #energyStored = dssElem.Properties(" % stored").Val
        #print("==> energyStored: " + str(energyStored))

        #logger.info("Loads names: "+str(dss.Loads.AllNames()))
        #logger.info("Bus names: " + str(dss.Circuit.AllBusNames()))
        #logger.info("All Node names: " + str(dss.Circuit.AllNodeNames()))
        #logger.info("Length of Node Names: " + str(len(dss.Circuit.AllNodeNames())))
        #logger.info("Voltages: "+str(dss.Circuit.AllBusVolts()))
        #logger.info("Length of Bus Voltages: "+str(len(dss.Circuit.AllBusVolts())))
        """print("Bus PuVoltages: "+ str(dss.Bus.PuVoltage()))
        print("Bus Voltages: " + str(dss.Circuit.AllBusVolts()))
        print("AllBusVMag: "+str(dss.Circuit.AllBusVMag()))
        print("AllBusMagPu: "+str(dss.Circuit.AllBusMagPu()))"""
        #logger.info("Length of Bus Voltages: " + str(len(dss.Circuit.AllBusVMag())))
        #logger.info("Just pu of Voltages: " + str(dss.Circuit.AllBusMagPu()))
        #logger.info("Length of Bus Voltages: " + str(len(dss.Circuit.AllBusMagPu())))
        #dss.Circuit.AllNodeVmagPUByPhase(1),
        #dss.run_command('Redirect /usr/src/app/tests/data/13Bus/IEEE13Nodeckt.dss')
        #dss.run_command('Redirect /usr/src/app/tests/data/13Bus/IEEELineCodes.dss')
        #logger.info(dss.utils.class_to_dataframe('Load'))
        result = []
        nodeList = dss.Circuit.AllNodeNames()
        puList = dss.Circuit.AllBusMagPu()
        ycurrents = dss.Circuit.YCurrents()
        elementLosses = dss.Circuit.AllElementLosses()
        for i in range(len(nodeList)):
            #result[nodeList[i]] = puList[i]
            result.append({"Node": nodeList[i], "Pu": puList[i], "YCurrent": ycurrents[i], "Loss": elementLosses[i]})
            #print(str(nodeList[i]) + ", " + str(puList[i])+ ", "+str(ycurrents[i])+", "+str(elementLosses[i]))
        return (dss.Circuit.AllNodeNames(), result, dss.Circuit.YCurrents(), dss.Circuit.AllElementLosses())
        #return (dss.Circuit.AllNodeNames(), dss.Circuit.AllNodeVmagPUByPhase(1), dss.Circuit.YCurrents(), dss.Circuit.AllElementLosses()) 
        #def getVoltages(self):


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
        #values=[]


        #for i in range(len(bases_list)):
            #values.append(bases_list[i])

        #dss_string = "Set voltagebases = [{value1},{value2},{value3},{value4},{value5}]".format(value1=self.V1,value2=self.V2,value3=self.V3,value4=self.V4,value5=self.V5)
        #dss_string = "Set voltagebases = [{value1},{value2},{value3},{value4},{value5}]".format(value1=values[0],value2=values[1],value3=values[2],value4=values[3],value5=values[4])
        dss_string = "Set voltagebases = "+str(bases_list)
        print(dss_string + "\n")

        dss.run_command(dss_string)
        dss.run_command(" CalcVoltageBases");

        #logger.debug("Voltage bases: "+str(dss.Settings.VoltageBases()))

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
        #!logger.debug("Simulation number " + str(dss.Solution.Number()))
        #dss.run_command("Set number =" + self.number)

    def setRegControls(self, regcontrols):
        #logger.debug("Setting up the regcontrols")
        #logger.debug("regcontrols: " + str(regcontrols))
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
                print(cmd + "\n")
                dss.run_command(cmd)
        except Exception as e:
            logger.error(e)

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
                    elif key == "base_frequency":
                        base_frequency = value
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
                self._base_frequency = base_frequency

                portion_str = " bank={bank} " if bank != None else " "
                portion_str = portion_str + " Basefreq={base_frequency} " if base_frequency != None else " "
                portion_str = portion_str + " Taps={taps} " if taps != None else " "
                portion_str = portion_str + " %LoadLoss={percent_load_loss} " if percent_load_loss != None else " "
                portion_str = portion_str + " %Rs={percent_rs} " if percent_rs != None else " "
                portion_str = portion_str + " Conns={conns} " if conns != None else " "

                dss_string = "New Transformer.{transformer_name} Phases={phases} Windings={winding} Buses={buses} kVAs={kvas} kVs={kvs} XscArray={xsc_array} " + portion_str + " "

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
                        taps=self._taps,
                        base_frequency=self._base_frequency )

                #logger.info("dss_string: " + dss_string)
                print(dss_string + "\n")
                dss.run_command(dss_string)

                """dss.run_command(
                    "New Transformer.{transformer_name} Phases={phases} Windings={winding} Buses=[{buses}] kVAs=[{kvas}] kVs= [{kvs}] Conns={conns} XscArray=[{xsc_array}] %Rs=[{percent_rs}] %LoadLoss=[{percent_load_loss}] bank=[{bank}] Taps=[{taps}] base_frequency=[{base_frequency}]".format(
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
                        taps=self._taps,
                        base_frequency=self._base_frequency

                    ))
                """
            # !logger.debug("Transformer_names: " + str(dss.Transformers.AllNames()))
            # dss.run_command('Solve')
            # !logger.debug("Load SOLVED") #It does not get here. This is now good
            # logger.info("Load names: " + str(dss.Loads.AllNames())) #listed load names
        except Exception as e:
            logger.error(e)

    """def setTransformers(self, transformers):
        logger.debug("Setting up the transformers")
        try:
            id = None
            phases = None
            winding = None
            xhl = None
            kvs = None
            kvas = None
            wdg = None
            bus = None
            connection = None
            kv = None
            for key, value in transformers.items():
                #logger.debug("Key: "+str(key)+" Value: "+str(value))
                if key == "id":
                    id = value
                if key == "phases":
                    phases = value
                if key == "winding":
                    winding = value
                if key == "xhl":
                    xhl = value
                if key == "kvs":
                    kvs = value
                if key == "kvas":
                    kvas = value
                if key == "wdg":
                    wdg = value
                if key == "bus":
                    bus = value
                if key == "connection":
                    connection = value
                if key == "kv":
                    kv = value

            #    if key == "voltagePrimary":
            #        voltagePrimary = value
            #    if key == "voltageSecondary":
            #        voltageSecondary = value
            #    if key == "voltageBasePrimary":
            #        voltageBasePrimary = value
            #    if key == "voltageBaseSecondary":
            #        voltageBaseSecondary = value
            #    if key == "powerPrimary":
            #        powerPrimary = value
            #    if key == "powerSecondary":
            #        powerSecondary = value
            #    if key == "nodeHV":
            #        nodeHV = value
            #    if key == "nodeLV":
            #        nodeLV = value
            #    if key == "noLoadLoss":
            #        noLoadLoss = value
            #    if key == "Req":
            #        Req = value
            #    if key == "Xeq":
            #        Xeq = value
            #    if key == "CeqTotal":
            #        CeqTotal = value
            #    if key == "monitor":
            #        monitor = value
            #    if key == "control":
            #        control = value
            #    if key == "tapLevel":
            #        tapLevel = value
            #    if key == "voltageunit":
            #        voltageunit = value
            #    if key == "frequency":
            #        frequency = value
            #    if key == "unitpower":
            #        unitpower = value

            self.setTransformer(id, phases, winding, xhl, kvs, kvas, wdg, bus, connection, kv)
            dss.run_command('Solve')

            logger.info("Transformer names: " + str(dss.Transformers.AllNames()))
        except Exception as e:
            logger.error(e)

    def setTransformer(self, transformer_name, phases, winding, xhl, kvs, kvas, wdg, bus, conn, kv):
        # New Transformer.TR1 phases=3 winding=2 xhl=0.014 kVs=(16, 0.4) kVAs=[400 400] wdg=1 bus=SourceBus conn=delta kv=16  !%r=.5 XHT=1 wdg=2 bus=225875 conn=wye kv=0.4        !%r=.5 XLT=1
        dss_string = "New Transformer.{transformer_name} Phases={phases} Windings={winding} XHL={xhl} KVs=[{kvs}] KVAs=[{kvas}] Wdg={wdg} Bus={bus} Conn={conn} Kv={kv}".format(
                transformer_name = transformer_name,
                phases = phases,
                winding = winding,
                xhl = str(xhl),
                kvs = ','.join(['{:f}'.format(x) for x in kvs]),
                kvas = ','.join(['{:f}'.format(x) for x in kvas]),
                wdg = wdg,
                bus = bus,
                conn = conn,
                kv = kv
            )
        logger.debug(dss_string)
        dss.run_command(dss_string)"""

    def getProfessLoadschapes(self, start: int, size=24):
        # Preparing loadshape values in a format required by PROFESS
        # All loads are includet, not only the one having storage attached
        result = {}
        print( "----------------- getProfessLoadschapes ----------------------")
        try:
            for key, value in self.loadshapes_for_loads.items():
                load_id = key
                bus_name = value["bus"]
                main_bus_name = bus_name.split('.', 1)[0]
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


    def getProfessLoadschapesPV(self, start: int, size=24):
        # Preparing loadshape values in a format required by PROFESS
        # All loads are includet, not only the one having storage attached
        result = {}
        print( "----------------- getProfessLoadschapes ----------------------")
        try:
            for key, value in self.loadshapes_for_pv.items():
                pv_id = key
                bus_name = value["bus"]
                main_bus_name = bus_name.split('.', 1)[0]
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
                for key, value in element.items():
                    #logger.debug("Key: "+str(key)+" Value: "+str(value))
                    if key=="id":
                        load_name=value
                    elif key=="bus":
                        bus_name=value
                    elif key=="phases":
                        #!TODO: counting phases when the phases are given as boolean values
                        #temp = value #json.loads("\""+str(value)+"\"")
                        #i = 0
                        #for k, v in temp.items():
                            #if k == "phase_R": #if k=="phase_R" and v==True, then i=i+1
                                #val = 1
                            #elif k == "phase_S":
                                #val = 2
                            #elif k == "phase_T":
                                #val = 3
                        num_phases=value #This is an alternative of the above TODO
                    elif key == "connection_type":
                        connection_type = value
                    elif key == "model":
                        model = value
                    elif key == "k_v": #elif key == "voltage": 
                        voltage_kV = value
                    elif key == "k_w":
                        voltage_kW = value
                    elif key == "k_var":
                        voltage_kVar = value
                    #elif key == "powerfactor":
                    #    power_factor = value
                    #elif key == "power_profile_id":
                    #    power_profile_id = value
                    else:
                        break
                self.load_name=load_name
                self.bus_name=bus_name
                self.num_phases=num_phases
                self.connection_type = connection_type
                self.model = model
                self.k_v=voltage_kV
                self.k_w=voltage_kW
                self.k_var=voltage_kVar
                #self.power_factor=power_factor
                #self.power_profile_id=power_profile_id

                #dss_string = "New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn={conn} Model={model} kV={voltage_kV} kW={voltage_kW} kVar={voltage_kVar} pf={power_factor} power_profile_id={shape}".format(
                dss_string="New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn={conn} Model={model} kV={voltage_kV} kW={voltage_kW} kVar={voltage_kVar} ".format(
                load_name=self.load_name,
                bus_name=self.bus_name,
                num_phases=self.num_phases,
                conn=self.connection_type,
                model=self.model,
                voltage_kV=self.k_v,
                voltage_kW=self.k_w,
                voltage_kVar=self.k_var,
                #power_factor=self.power_factor
                #shape=self.power_profile_id
                )

                #---------- chek for available loadschape and attach it to the load
                if self.load_name in self.loadshapes_for_loads:
                    dss_string = dss_string + " Yearly=" + load_name

                #logger.info("dss_string: " + dss_string)
                print(dss_string + "\n")
                dss.run_command(dss_string)

                """dss.run_command("New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn={conn} Model={model} kV={voltage_kV} kW={voltage_kW} kVar={voltage_kVar} pf={power_factor} power_profile_id={shape}".format(
                load_name=self.load_name,
                bus_name=self.bus_name,
                num_phases=self.num_phases,
                conn=self.connection_type,
                model=self.model,
                voltage_kV=self.k_v,
                voltage_kW=self.k_w,
                voltage_kVar=self.k_var,
                power_factor=self.power_factor,
                shape=self.power_profile_id
                ))"""

                """logger.debug(#See if the values are loaded to the command. This is good :)
                " load_name 1: "+str(load_name) + 
                " bus_name = "+str(bus_name)+
                " num_phases = " +str(num_phases)+
                " conn = " +connection_type+
                " model = " +str(model)+
                " k_v = " +str(voltage_kV)+
                " k_w = " + str(voltage_kW)+
                " k_var = " + str(voltage_kVar)+
                " power_factor = "+str(power_factor)+
                " shape = " + power_profile_id
                )""" 
                #dss.run_command('Solve') #How do we get the result?
                #logger.debug("Load SOLVED") #It does not get here. This is now good
                #!logger.info("Load names: " + str(dss.Loads.AllNames())) #listed load names
                #dss.run_command('Solve');
        except Exception as e:
            logger.error(e)
    """def setLoads(self, loads):
        logger.debug("Setting up the loads")
        self.loads=loads
        try:
            for element in self.loads:
                for key, value in element.items():
                    #logger.debug("Key: "+str(key)+" Value: "+str(value))
                    if key=="id":
                        load_name=value
                    elif key=="bus":
                        bus_name=value
                    elif key=="phases":
                        #temp = value #json.loads("\""+str(value)+"\"")
                        i = 0
                        #for k, v in temp.items():
                            #if k == "phase_R": #if k=="phase_R" and v==True, then i=i+1
                                #val = 1
                            #elif k == "phase_S":
                                #val = 2
                            #elif k == "phase_T":
                                #val = 3
                        num_phases="3" #num_phases=i
                    elif key == "connection_type":
                        connection_type = value
                    elif key == "model":
                        model = value
                    elif key == "k_v": #elif key == "voltage": 
                        voltage_kV = value
                    elif key == "k_w":
                        voltage_kW = value
                    elif key == "k_var":
                        voltage_kVar = value
                    elif key == "powerfactor":
                        power_factor = value
                    elif key == "power_profile_id":
                        power_profile_id = value
                    else:
                        break
                logger.debug(#See if the values are loaded to the command. This is good :)
                " load_name 1: "+str(load_name) + 
                " bus_name = "+str(bus_name)+
                " num_phases = " +str(num_phases)+
                " conn = " +connection_type+
                " model = " +str(model)+
                " k_v = " +str(voltage_kV)+
                " k_w = " + str(voltage_kW)+
                " k_var = " + str(voltage_kVar)+
                " power_factor = "+str(power_factor)+
                " shape = " + power_profile_id
                ) 
                self.setLoad(load_name, bus_name, num_phases, connection_type, model, voltage_kV, voltage_kW, voltage_kVar, power_factor, power_profile_id)
            dss.run_command('Solve') #How do we get the result?
            #logger.debug("Load SOLVED") #It does not get here. This is now good
            #logger.info("Load names: " + str(dss.Loads.AllNames())) #listed load names
        except Exception as e:
            logger.error(e)

    def setLoad(self, load_name, bus_name, num_phases, connection_type, model, voltage_kV, voltage_kW, voltage_kVar, power_factor, power_profile_id): #(self, load_name, bus_name, connection_type, model, voltage_kW, voltage_kVar, num_phases=3, voltage_kV=0.4, power_factor=1, power_profile_id=None)
        self.load_name=load_name
        self.bus_name=bus_name
        self.num_phases=num_phases
        self.connection_type = connection_type
        self.model = model
        self.k_v=voltage_kV
        self.k_w=voltage_kW
        self.k_var=voltage_kVar
        self.power_factor=power_factor
        self.power_profile_id=power_profile_id
        dss.run_command(
            #"New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn=Delta Model=1 kV={voltage_kV}   pf={power_factor} Daily={shape}".format(
            "New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn={conn} Model={model} kV={voltage_kV} kW={voltage_kW} kVar={voltage_kVar} pf={power_factor} power_profile_id={shape}".format(
                load_name=self.load_name,
                bus_name=self.bus_name,
                num_phases=self.num_phases,
                conn=self.connection_type,
                model=self.model,
                voltage_kV=self.k_v,
                voltage_kW=self.k_w,
                voltage_kVar=self.k_var,
                power_factor=self.power_factor,
                shape=self.power_profile_id
                ))
        logger.debug(#See if the values are loaded to the command. This is good now
                " load_name: "+str(self.load_name) + 
                " bus_name = "+str(self.bus_name)+
                " num_phases = " +str(self.num_phases)+
                " conn = " +self.connection_type+
                " model = " +str(self.model)+
                " k_v = " +str(self.k_v)+
                " k_w = " + str(self.k_w)+
                " k_var = " + str(self.k_var)+
                " power_factor = "+str(self.power_factor)+
                " shape = " + self.power_profile_id
                ) 
        #logger.debug("Load SOLVED 2") # It works up to here. Where will the output be sent?"""

    """def setLineCodes(self, lines):
        #!logger.info("Setting up the linecodes: "+str(lines))
        #!logger.debug("Type of lines: "+str(type(lines)))
        try:
            for element in lines:
                id = None
                r1 = None
                x1 = None
                c0 = None
                units = None
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str (value))
                    if key == "id":
                        id = value
                    if key == "r1":
                        r1 = value
                    if key == "x1":
                        x1 = value
                    if key == "c0":
                        c0 = value
                    if key == "units":
                        units = value
                self.setLineCode(id, r1, x1, c0, units)
                #!dss.run_command("Solve")
                #!logger.debug("Finished adding linecodes")
        except Exception as e:
            logger.error(e)

    def setLineCode(self, id, r1, x1, c0, units):
        # example: new Linecode.underground_95mm R1=0.193 X1=0.08 C0=0 Units=km
        dss_string = "new Linecode.{id} R1={r1} X1={x1} C0={c0} Units={units}".format(
            id = id,
            r1 = r1,
            x1 = x1,
            c0 = c0,
            units = units
        )
        logger.info(dss_string)
        dss.run_command(dss_string)"""

    def setLineCodes(self, lines):
        #logger.debug("Setting up linecodes")
        self.linecodes=lines

        try:
            for element in self.linecodes:
                #logger.debug(str(element))
                cmatrix_str = " "
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key=="id":
                        linecode_name=value
                    elif key=="nphases":
                        #logger.debug(str(key))
                        num_phases=value 
                    elif key == "base_frequency":
                        BaseFreq = value
                    elif key == "rmatrix":
                        rmatrix = value
                    elif key == "xmatrix":
                        xmatrix = value
                    elif key == "cmatrix":
                        cmatrix = value
                    elif key == "units":
                        units = value
                    else:
                        break
                self.id=linecode_name
                self.nphases=num_phases
                self.base_frequency = BaseFreq
                self.rmatrix = rmatrix
                self.xmatrix = xmatrix 
                self.cmatrix = cmatrix
                self.units = units


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

                #logger.info("rmatrix_str: " + rmatrix_str)
                #logger.info("xmatrix_str: " + xmatrix_str)
                #logger.info("cmatrix_str: " + cmatrix_str)

                dss_string = "New linecode.{linecode_name} nphases={num_phases} BaseFreq={BaseFreq} rmatrix=(" + rmatrix_str + " ) xmatrix=(" + xmatrix_str + " ) " + cmatrix_str +  " units = {units}"
                dss_string = dss_string.format(
                #dss_string = "New linecode.{linecode_name} nphases={num_phases} BaseFreq={BaseFreq} rmatrix={rmatrix[0][0]} | {rmatrix[1][0]} | {rmatrix[1][1]} | {rmatrix[1][2]} | {rmatrix[2][0]} | {rmatrix[2][1]} | {rmatrix[2][2]} xmatrix={xmatrix[0][0]} | {xmatrix[1][0]} | {xmatrix[1][1]} | {xmatrix[1][2]} | {xmatrix[2][0]} | {xmatrix[2][1]} | {xmatrix[2][2]} units = {units}".format(
                linecode_name = self.id,
                num_phases = self.nphases,
                BaseFreq = self.base_frequency,
                rmatrix = self.rmatrix,
                xmatrix = self.xmatrix,
                cmatrix = self.cmatrix,
                units = self.units
                )

                #logger.info("dss_string: " + dss_string)
                print(dss_string + "\n")
                dss.run_command( dss_string)

                """dss.run_command("New linecode.{linecode_name} nphases={num_phases} BaseFreq={BaseFreq} rmatrix={(rmatrix1 + '|' rmatrix2 + '|' rmatrix3)} xmatrix={(xmatrix1 + '|' xmatrix2 + '|' xmatrix3)} units = {units}".format(
                linecode_name = self.id,
                num_phases = self.nphases,
                BaseFreq = self.BaseFreq,
                rmatrix1 = self.rmatrix1,
                rmatrix2 = self.rmatrix2,
                rmatrix3 = self.rmatrix3,
                xmatrix1 = self.xmatrix1,
                xmatrix2 = self.xmatrix2,
                xmatrix3 = self.xmatrix3,
                units = self.units
            ))"""
                """ logger.debug(#See if the values are loaded to the command. This is good :)
                " load_name 1: "+str(load_name) + 
                " bus_name = "+str(bus_name)+
                " num_phases = " +str(num_phases)+
                " conn = " +connection_type+
                " model = " +str(model)+
                " k_v = " +str(voltage_kV)+
                " k_w = " + str(voltage_kW)+
                " k_var = " + str(voltage_kVar)+
                " power_factor = "+str(power_factor)+
                " shape = " + power_profile_id
                ) """
            #dss.run_command('Solve')
            #logger.debug("Load SOLVED") #It does not get here. This is now good
            #logger.info("Load names: " + str(dss.Loads.AllNames())) #listed load names
        except Exception as e:
            logger.error(e)

    def setPowerLines(self, lines):
        #logger.debug("Setting up the powerlines")
        self.lines=lines
        try:
            for element in self.lines:
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
                        break
                self._id = line_id
                self._phases = phases
                self._bus1 = bus1
                self._bus2 = bus2
                self._linecode = linecode
                #logger.debug("linecode :"+str(self._linecode))

                self._length = length
                #logger.debug("length :" + str(self._length))
                self._unitlength = unitlength
                #logger.debug("unit :" + str(self._unitlength))
                self._r1 = r1
                #logger.debug("r1 :" + str(self._r1))
                self._r0 = r0
                #logger.debug("r0 :" + str(self._r0))
                self._x1 = x1
                #logger.debug("x1 :" + str(self._x1))
                self._x0 = x0
                #logger.debug("x0 :" + str(self._x0))
                self._c1 = c1
                #logger.debug("c1 :" + str(self._c1))
                self._c0 = c0
                #logger.debug("c0 :" + str(self._c0))
                self._switch = switch
                #logger.debug("switch :" + str(self._switch))


                my_str=[]
                if not self._r1 == None and self._linecode == None:
                    #portion_str = "r1={r1} r0={r0} x1={x1} x0={x0} c1={c1}  c0={c0} " if switch == True else " length={length} units={unitlength} linecode={linecode} "
                    my_str.append("r1={r1} ")

                    if not self._r0 == None:
                        my_str.append("r0={r0} ")
                    if not self._x1 == None:
                        my_str.append("x1={x1} ")
                    if not self._x0 == None:
                        my_str.append("x0={x0} ")
                    if not self._c1 == None:
                        my_str.append("c1={c1} ")
                    if not self._c0 == None:
                        my_str.append("c0={c0} ")
                else:
                    if not self._linecode == None and self._r1 == None:
                        my_str.append("linecode={linecode} ")
                    else:
                        logger.error("r1 and linecode cannot be entered at the same time")
                        sys.exit(0)
                        raise ValueError('r1 and linecode cannot be entered at the same time')


                if not self._length == None:
                    my_str.append("length={length} ")
                if not self._unitlength == None:
                    my_str.append("units={unitlength} ")

                portion_str = ''.join(my_str)

                dss_string = "New Line.{line_id} bus1={bus1} bus2={bus2} phases={phases} switch={switch} " + portion_str + " "

                dss_string = dss_string.format(
                line_id = self._id,
                phases=self._phases,
                bus1=self._bus1,
                bus2=self._bus2,
                linecode=self._linecode,
                length=self._length,
                unitlength=self._unitlength,
                r1=self._r1,
                r0=self._r0,
                x1=self._x1,
                x0=self._x0,
                c1=self._c1,
                c0=self._c0,
                switch=self._switch
                )

                print(dss_string + "\n")
                dss.run_command(dss_string)



                """logger.debug(#See if the values are loaded to the command. This is good :)
                "line_id = "+str(self._id)+
                "phases="+str(self._phases)+ 
                "bus1="+str(self._bus1)+
                "bus2="+str(self._bus2)+
                "linecode="+str(self._linecode)+
                "length="+str(self._length)+
                "unitlength="+str(self._unitlength)+
                "r1="+str(self._r1)+
                "r0="+str(self._r0)+
                "x1="+str(self._x1)+
                "x0="+str(self._x0)+
                "c1="+str(self._c1)+
                "c0="+str(self._c0)+
                "switch="+str(self._switch)
                )""" 
            #dss.run_command('Solve') #How do we get the result?
            #!logger.debug("Load SOLVED") #It does not get here. This is now good
            #!logger.info("Power lines: " + str(dss.Lines.AllNames())) #listed load names
        except Exception as e:
            logger.error(e)
        
    """def setPowerLines(self, lines):
        logger.info("Setting up the powerlines")
        self.lines=lines
        try:
            for element in lines:
                id = None
                node1 = None
                node2 = None
                phases = None
                length = None
                unit = None
                linecode = None
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key == "id":
                        id = value
                    if key == "bus1":
                        node1 = value
                    if key == "bus2":
                        node2 = value
                    if key == "phases":
                        phases = value
                    if key == "length":
                        length = value
                    if key == "unit":
                        unit = value
                    if key == "linecode":
                        linecode = value
                self.setPowerLine(id, node1, node2, phases, length, unit, linecode)
                dss.run_command('Solve')
                logger.debug("Power lines: " + str(dss.Lines.AllNames()))
        except Exception as e:
            logger.error(e)

    def setPowerLine(self, id, node1, node2, phases, length, unit, linecode):
        # New line.82876 bus1=225875 bus2=107558 phases=3  length=0.007 units=km linecode=underground_95mm
        dss_string = "New Line.{id} bus1={bus1} bus2={bus2} phases={phases} length={length} units={units} linecode={linecode}".format(
            id = id,
            bus1 = node1,
            bus2 = node2,
            phases = phases,
            length = length,
            units = unit,
            linecode = linecode
        )
        logger.info(dss_string)
        dss.run_command(dss_string)"""

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

        except Exception as e:
            logger.error(e)

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
        print(dss_string + "\n")
        dss.run_command(dss_string)



    def setPVshapes(self, pvs, city, country, sim_days, profiles, profess):
        self.profess=profess
        #!logger.debug("Setting up the loads")
        self.pvs=pvs
        try:
            for element in self.pvs:
                #for kskd in element.keys():
                    #logger.debug("key "+str(kskd))
                pv_name = element["id"]
                bus_name = element["bus1"]
                max_power= element["max_power_k_w"]
                logger.debug("max power "+str(max_power))
                #self.pv_name=pv_name
                #self.bus_name=bus_name

                # ----------get_a_profile---------------#
                pv_profile_data = profiles.pv_profile(city, country, sim_days, max_power)
                #logger.debug("pv profile: "+str(pv_profile_data))
                #print("load_profile_data: randint=" + str(randint_value))

                #--------store_profile_for_line----------#
                self.loadshapes_for_pv[pv_name] = {"bus":bus_name, "loadshape":pv_profile_data}
                #loadshape_id=load_name + bus_name
                loadshape_id=pv_name

                self.setLoadshapePV(loadshape_id, sim_days * 24, 1, pv_profile_data)

        except Exception as e:
            logger.error(e)

    def setLoadshapes(self, loads, sim_days, profiles, profess):
        self.profess=profess
        #!logger.debug("Setting up the loads")
        self.loads=loads
        try:
            for element in self.loads:
                load_name = element["id"]
                bus_name = element["bus"]

                self.load_name=load_name
                self.bus_name=bus_name

                # ----------get_a_profile---------------#
                randint_value=random.randrange(0, 50)
                load_profile_data = profiles.load_profile(type="residential", randint=randint_value, days=sim_days)
                #print("load_profile_data: randint=" + str(randint_value))

                #--------store_profile_for_line----------#
                self.loadshapes_for_loads[load_name] = {"bus":bus_name, "loadshape":load_profile_data}
                #loadshape_id=load_name + bus_name
                loadshape_id=load_name

                self.setLoadshape(loadshape_id, sim_days*24, 1, load_profile_data)

        except Exception as e:
            logger.error(e)


    def setLoadshapes_off(self, loadshapes):
        #!logger.debug("Setting up the Loadshapes")
        #!logger.debug("Loadshape in OpenDSS: " + str(loadshapes))
        try:
            for element in loadshapes:
                id = None
                npts = None
                interval = None
                mult = None
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key == "id":
                        id = value
                    if key == "npts":
                        npts = value
                    if key == "interval":
                        interval = value
                    if key == "mult":
                        mult = value
                self.setLoadshape(id, npts, interval, mult)
                #!dss.run_command('Solve')
                #!logger.debug("Loadshape names: " + str(dss.LoadShape.AllNames()))
        except Exception as e:
            logger.error(e)

    def setLoadshape(self, id, npts, interval, mult):
        try:
            print("New Loadshape." + id)
            # New Loadshape.assumed_irrad npts=24 interval=1 mult=[0 0 0 0 0 0 .1 .2 .3  .5  .8  .9  1.0  1.0  .99  .9  .7  .4  .1 0  0  0  0  0]
            dss_string = "New Loadshape.{id} npts={npts} interval={interval} mult=({mult})".format(
                id=id,
                npts=npts,
                interval=interval,
                mult=' '.join(['{:f}'.format(x) for x in mult])
                #mult = ','.join(['{:f}'.format(x) for x in mult])
            )
            #!logger.info(dss_string)
            #print(dss_string + "\n")
            #dss_string="New Loadshape1 npts=24 interval=1 mult=(0 0 0 0 0 0 .1 .2 .3 .5 .8 .9 1.0 1.0 .99 .9 .7 .4 .1 0 0 0 0 0)"
            #print(dss_string + "\n")
            dss.run_command(dss_string)

            dss_string = "? Loadshape." + str(id) + ".mult"
            #dss_string = "? Loadshape1.mult"
            #print(dss_string + "\n")
            result = dss.run_command(dss_string)
            print("Loadshape." + str(id) + ".mult count:" +  str(len((str(result)).split(" "))) + "\n")
            #print("Loadshape." + str(id) + ".mmult:" +  str(result) + "\n")
        except Exception as e:
            logger.error(e)

    def setLoadshapePV(self, id, npts, interval, mult):
        try:
            print("New Loadshape.Shape_" + id)
            # New Loadshape.assumed_irrad npts=24 interval=1 mult=[0 0 0 0 0 0 .1 .2 .3  .5  .8  .9  1.0  1.0  .99  .9  .7  .4  .1 0  0  0  0  0]
            dss_string = "New Loadshape.Shape_{id} npts={npts} interval={interval} mult=({mult})".format(
                id=id,
                npts=npts,
                interval=interval,
                mult=' '.join(['{:f}'.format(x) for x in mult])
                #mult = ','.join(['{:f}'.format(x) for x in mult])
            )
            #!logger.info(dss_string)
            #print(dss_string + "\n")
            #dss_string="New Loadshape1 npts=24 interval=1 mult=(0 0 0 0 0 0 .1 .2 .3 .5 .8 .9 1.0 1.0 .99 .9 .7 .4 .1 0 0 0 0 0)"
            #print(dss_string + "\n")
            dss.run_command(dss_string)

            dss_string = "? Loadshape.Shape_" + str(id) + ".mult"
            #dss_string = "? Loadshape1.mult"
            #print(dss_string + "\n")
            result = dss.run_command(dss_string)
            print("Loadshape.Shape_" + str(id) + ".mult count:" +  str(len((str(result)).split(" "))) + "\n")
            #print("Loadshape." + str(id) + ".mmult:" +  str(result) + "\n")
        except Exception as e:
            logger.error(e)

    def setTshapes(self, tshapes):
        #!logger.info("Setting up the TShapes")
        #!logger.debug("Tshape in OpenDSS: "+str(tshapes))
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
        print(dss_string + "\n")
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
                pf = None
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
                    elif key == "max_power_kw":
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
                        pass

                self.setPhotovoltaic(id, phases, bus1, voltage, power, effcurve, ptcurve, daily, tdaily, pf, temperature, irrad, pmpp)
                #!dss.run_command('Solve')
                #!logger.debug("Photovoltaics: " + str(dss.PVsystems.AllNames()))
        except Exception as e:
            logger.error(e)

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
        # !logger.info(dss_string)
        # ---------- chek for available loadschape and attach it to the load
        if id in self.loadshapes_for_pv:
            dss_string = dss_string + " Yearly=Shape_" + id

        print(dss_string + "\n")
        dss.run_command(dss_string)
        """dss_string = "New PVSystem.{id} phases={phases} bus1={bus1} kV={voltage} kVA={power} effcurve={effcurve} P-TCurve={ptcurve} Daily={daily} TDaily={tdaily} PF={pf} temperature={temperature} irrad={irrad} Pmpp={pmpp}".format(
            id=id,
            phases=phases,
            bus1=bus1,
            voltage=voltage,
            power=power,
            effcurve=effcurve,
            ptcurve=ptcurve,
            daily=daily,
            tdaily=tdaily,
            pf=pf,
            temperature=temperature,
            irrad=irrad,
            pmpp=pmpp
        )
        #!logger.info(dss_string)
        print(dss_string + "\n")
        dss.run_command(dss_string)"""

    def setStorages(self, storage):
        #logger.info("Setting up the Storages")
        try:
            for element in storage:
                id = None
                bus1 = None
                phases = None
                connection = "wye"
                soc = 100 #! defalt value
                dod = 20 #! defalt value
                kv = None
                kw_rated = None
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
                    elif key == "dod":
                        dod = value
                    elif key == "kv":
                        kv = value
                    elif key == "kw_rated":
                        kw_rated = value
                    elif key == "kwh_rated":
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
                        pass
                self.setStorage(id, bus1, phases, connection, soc, dod, kv, kw_rated, kwh_rated, kwh_stored, charge_efficiency, discharge_efficiency, powerfactor)
                #!dss.run_command('Solve')
                #!logger.info("Storage names: " + str(dss.Circuit.AllNodeNames()))
        except Exception as e:
            logger.error(e)


    def setStorage(self, id, bus1, phases, connection, soc, dod, kv, kw_rated, kwh_rated, kwh_stored, charge_efficiency, discharge_efficiency, powerfactor):
        #logger.info("starting setStorage for ID: " + str(id))
        # New Storage.AtPVNode phases=3 bus1=121117 kV=0.4  kva=5 kWhrated=9.6 kwrated=6.4


        #dss_string = "New Storage.{id} bus1={bus1}  phases={phases} conn={connection} %stored={soc} %reserve={dod} kV={kv} kWrated={kw_rated} kWhrated={kwh_rated} kWhstored={kwh_stored} %EffCharge={charge_efficiency} %EffDischarge={discharge_efficiency} pf={powerfactor}".format(
        dss_string="New Storage.{id} bus1={bus1}  phases={phases} conn={connection} %stored={soc} %reserve={dod} kV={kv} kWrated={kw_rated} kWhrated={kwh_rated} %EffCharge={charge_efficiency} %EffDischarge={discharge_efficiency} pf={powerfactor}".format(
                id=id,
            bus1=bus1,
            phases=phases,
            connection=connection,
            soc=soc,
            dod=dod,
            kv=kv,
            kw_rated=kw_rated,
            kwh_rated=kwh_rated,
            kwh_stored=kwh_stored,
            charge_efficiency=charge_efficiency,
            discharge_efficiency=discharge_efficiency,
            powerfactor=powerfactor
        )

        #testing storage charge/discharge
        #addition = " kW=15 state=discharging DischargeTrigger=0.8 ChargeTrigger=0.3 "
        #addition = " kW=10 state=IDLING DischargeTrigger=0.8 ChargeTrigger=0.3 "
        addition = " DispMode=FOLLOW "
        dss_string = dss_string + addition

        #logger.info(dss_string)
        print(dss_string + "\n")
        dss.run_command(dss_string)

    def setCapacitors(self, capacitors):
        #!logger.info("Setting up the capacitors")
        self.capacitors=capacitors
        try:
            for element in self.capacitors:
                #logger.debug("Element: "+str(element))
                for key, value in element.items():
                    #logger.debug("Key: "+str(key)+" Value: "+str(value))
                    if key=="id":
                        id=value
                    elif key=="bus":
                        bus=value
                    elif key=="phases":
                        phases=value 
                    elif key == "k_var":
                        voltage_kVar = value
                    elif key == "k_v":  
                        voltage_kV = value
                    else:
                        break
                self.capacitor_name=id
                self.bus_name=bus
                self.num_phases=phases
                self.k_v=voltage_kV
                self.k_var=voltage_kVar

                dss_string = "New Capacitor.{capacitor_name} Bus1={bus_name}  Phases={num_phases} kV={voltage_kV} kVar={voltage_kVar}".format(
                capacitor_name=self.capacitor_name,
                bus_name=self.bus_name,
                num_phases=self.num_phases,
                voltage_kV=self.k_v,
                voltage_kVar=self.k_var
                )
                #logger.info("dss_string: " + dss_string)
                print(dss_string + "\n")
                dss.run_command(dss_string)
                """logger.info(#See if the values are loaded to the command. This is good :)
                " capacitor_name 1: "+str(self.capacitor_name) + 
                " bus_name = "+str(self.bus_name)+
                " num_phases = " +str(self.num_phases)+
                " k_v = " +str(self.voltage_kV)+
                " k_var = " + str(self.voltage_kVar)
                )"""
            #dss.run_command('Solve')
        except Exception as e:
            logger.error(e)
