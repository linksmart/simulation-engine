# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 15:05:36 2018

@author: garagon
"""


import logging
import opendssdirect as dss


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class OpenDSS:
    def __init__(self, grid_name):
        logger.info("Starting OpenDSS")
        logger.info("OpenDSS version: " + dss.__version__)
        self.grid_name=grid_name
        dss.run_command("Clear")
        #dss.Basic.NewCircuit("Test 1")
        #dss.run_command("New circuit.{circuit_name}".format(circuit_name="Test 1"))

    def setNewCircuit(self, name):
        #dss.run_command("New circuit.{circuit_name}".format(circuit_name= name))
        dss.Basic.NewCircuit(name)
        logger.debug("Name of the active circuit: "+str(self.getActiveCircuit()))

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
        dss.Solution.Solve()
        #logger.info("Loads names: "+str(dss.Loads.AllNames()))
        #logger.info("Bus names: " + str(dss.Circuit.AllBusNames()))
        #logger.info("All Node names: " + str(dss.Circuit.AllNodeNames()))
        #logger.info("Length of Node Names: " + str(len(dss.Circuit.AllNodeNames())))
        #logger.info("Voltages: "+str(dss.Circuit.AllBusVolts()))
        #logger.info("Length of Bus Voltages: "+str(len(dss.Circuit.AllBusVolts())))
        #logger.info("Bus Voltages: "+ str(dss.Bus.Voltages()))
        #logger.info("Just magnitude of Voltages: "+str(dss.Circuit.AllBusVMag()))
        #logger.info("Length of Bus Voltages: " + str(len(dss.Circuit.AllBusVMag())))
        #logger.info("Just pu of Voltages: " + str(dss.Circuit.AllBusMagPu()))
        #logger.info("Length of Bus Voltages: " + str(len(dss.Circuit.AllBusMagPu())))
        return (dss.Circuit.AllNodeNames(),dss.Circuit.AllBusMagPu())
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

    def setVoltageBases(self,V1=None,V2=None,V3=None,V4=None,V5=None):
        self.V1=V1
        self.V2=V2
        self.V3=V3
        self.V4=V4
        self.V5=V5
        #dss.Settings.VoltageBases(0.4,16)
        dss.run_command("Set voltagebases = [{value1},{value2},{value3},{value4},{value5}]".format(value1=self.V1,value2=self.V2,value3=self.V3,value4=self.V4,value5=self.V5))
        dss.run_command("calcv")
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
        logger.debug("Simulation number " + str(dss.Solution.Number()))
        #dss.run_command("Set number =" + self.number)

    def setLoads(self, loads):
        logger.debug("Setting up the loads")
        self.loads=loads
        try:
            for element in self.loads:
                for key, value in element.items():
                    #logger.debug("Key: "+str(key)+" Value: "+str(value))
                    if key=="id":
                        load_name=value
                    elif key=="node":
                        bus_name=value
                    elif key=="phases":
                        num_phases=value
                    elif key == "voltage":
                        voltage_kV = value
                    elif key == "powerfactor":
                        power_factor = value
                    elif key == "power_profile":
                        power_profile = value
                    else:
                        break
                self.setLoad(load_name, bus_name, num_phases, voltage_kV, power_factor, power_profile)

            dss.run_command('Solve')

            logger.info("Load names: " + str(dss.Loads.AllNames()))
        except Exception as e:
            logger.error(e)

    def setLoad(self, load_name, bus_name, num_phases=3, voltage_kV=0.4, power_factor=1, power_profile=None):
        self.load_name=load_name
        self.bus_name=bus_name
        self.num_phases=num_phases
        self.voltage_kV=voltage_kV
        self.power_factor=power_factor
        self.power_profile=power_profile

        dss.run_command(
            "New Load.{load_name} Bus1={bus_name}  Phases={num_phases} Conn=Delta Model=1 kV={voltage_kV}   pf={power_factor} Daily={shape}".format(
                load_name=self.load_name,
                bus_name=self.bus_name,
                num_phases=self.num_phases,
                voltage_kV=self.voltage_kV,
                power_factor=self.power_factor,
                shape=self.power_profile
            ))

    def setTransformers(self, transformers):
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
        dss.run_command(dss_string)

    def setLineCodes(self, lines):
        logger.info("Setting up the linecodes: "+str(lines))
        logger.debug("Type of lines: "+str(type(lines)))
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
                dss.run_command("Solve")
                logger.debug("Finished adding linecodes")
        except Exception as e:
            logger.error(e)

    def setLineCode(self, id, r1, x1, c0, units):
        # new Linecode.underground_95mm R1=0.193 X1=0.08 C0=0 Units=km
        dss_string = "new Linecode.{id} R1={r1} X1={x1} C0={c0} Units={units}".format(
            id = id,
            r1 = r1,
            x1 = x1,
            c0 = c0,
            units = units
        )
        logger.info(dss_string)
        dss.run_command(dss_string)

    def setPowerLines(self, lines):
        logger.info("Setting up the powerlines")
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
                    if key == "node1":
                        node1 = value
                    if key == "node2":
                        node2 = value
                    if key == "phases":
                        phases = value
                    if key == "length":
                        length = value
                    if key == "unitlength":
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
        dss.run_command(dss_string)

    def setXYCurves(self, xycurves):
        logger.info("Setting up the XYCurves")
        logger.debug("XY Curve in OpenDSS: " + str(xycurves))
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
                dss.run_command('Solve')

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
        logger.info(dss_string)
        dss.run_command(dss_string)

    def setLoadshapes(self, loadshapes):
        logger.debug("Setting up the Loadshapes")
        logger.debug("Loadshape in OpenDSS: " + str(loadshapes))
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
                dss.run_command('Solve')
                logger.debug("Loadshape names: " + str(dss.LoadShape.AllNames()))
        except Exception as e:
            logger.error(e)

    def setLoadshape(self, id, npts, interval, mult):
        # New Loadshape.assumed_irrad npts=24 interval=1 mult=[0 0 0 0 0 0 .1 .2 .3  .5  .8  .9  1.0  1.0  .99  .9  .7  .4  .1 0  0  0  0  0]
        dss_string = "New Loadshape.{id} npts={npts} interval={interval} mult=[{mult}]".format(
            id=id,
            npts=npts,
            interval=interval,
            mult=','.join(['{:f}'.format(x) for x in mult])
        )
        logger.info(dss_string)
        dss.run_command(dss_string)

    def setTshapes(self, tshapes):
        logger.info("Setting up the TShapes")
        logger.debug("Tshape in OpenDSS: "+str(tshapes))
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
                dss.run_command('Solve')
                logger.info("TShape names: " + str(dss.LoadShape.AllNames()))
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
        logger.info(dss_string)
        dss.run_command(dss_string)

    def setPhotovoltaics(self, photovoltaics):
        logger.debug("Setting up the Photovoltaics")
        try:
            for element in photovoltaics:
                id = None
                phases = None
                bus1 = None
                voltage = None
                power = None
                effcurve = None
                ptcurve = None
                daily = None
                tdaily = None
                pf = None
                temperature = None
                irrad = None
                pmpp = None
                for key, value in element.items():
                    #logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key == "id":
                        id = value
                    if key == "phases":
                        phases = value
                    if key == "bus1":
                        bus1 = value
                    if key == "voltage":
                        voltage = value
                    if key == "power":
                        power = value
                    if key == "effcurve":
                        effcurve = value
                    if key == "ptcurve":
                        ptcurve = value
                    if key == "daily":
                        daily = value
                    if key == "tdaily":
                        tdaily = value
                    if key == "pf":
                        pf = value
                    if key == "temperature":
                        temperature = value
                    if key == "irrad":
                        irrad = value
                    if key == "pmpp":
                            pmpp = value
                self.setPhotovoltaic(id, phases, bus1, voltage, power, effcurve, ptcurve, daily, tdaily, pf, temperature, irrad, pmpp)
                dss.run_command('Solve')
                logger.debug("Photovoltaics: " + str(dss.PVsystems.AllNames()))
        except Exception as e:
            logger.error(e)

    def setPhotovoltaic(self, id, phases, bus1, voltage, power, effcurve, ptcurve, daily, tdaily, pf, temperature, irrad, pmpp):
        # New PVSystem.PV_Menapace phases=3 bus1=121117 kV=0.4  kVA=10  effcurve=panel_absorb_eff  P-TCurve=panel_temp_eff Daily=assumed_irrad TDaily=assumed_Temp PF=0.96 temperature=25 irrad=0.8  Pmpp=10
        dss_string = "New PVSystem.{id} phases={phases} bus1={bus1} kV={voltage} kVA={power} effcurve={effcurve} P-TCurve={ptcurve} Daily={daily} TDaily={tdaily} PF={pf} temperature={temperature} irrad={irrad} Pmpp={pmpp}".format(
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
        logger.info(dss_string)
        dss.run_command(dss_string)

    def setStorages(self, storage):
        logger.info("Setting up the Storages")
        try:
            for element in storage:
                id = None
                phases = None
                node = None
                voltage = None
                power = None
                kwhrated = None
                kwrated = None
                for key, value in element.items():
                    logger.debug("Key: " + str(key) + " Value: " + str(value))
                    if key == "id":
                        id = value
                    if key == "phases":
                        phases = value
                    if key == "node":
                        node = value
                    if key == "voltage":
                        voltage = value
                    if key == "power":
                        power = value
                    if key == "kwhrated":
                        kwhrated = value
                    if key == "kwrated":
                        kwrated = value
                self.setStorage(id, phases, node, voltage, power, kwhrated, kwrated)
                dss.run_command('Solve')
                logger.info("Storage names: " + str(dss.Circuit.AllNodeNames()))
        except Exception as e:
            logger.error(e)

    def setStorage(self, id, phases, node, voltage, power, kwhrated, kwrated):
        # New Storage.AtPVNode phases=3 bus1=121117 kV=0.4  kva=5 kWhrated=9.6 kwrated=6.4
        dss_string = "New Storage.{id} phases={phases} bus1={node} kV={voltage} kVA={power} kWhrated={kwhrated} kwrated={kwrated}".format(
            id=id,
            phases=phases,
            node=node,
            voltage=voltage,
            power=power,
            kwhrated=kwhrated,
            kwrated=kwrated
        )
        logger.info(dss_string)
        dss.run_command(dss_string)