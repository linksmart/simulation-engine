import logging
import json
import os
import sys

from simulator.openDSS import OpenDSS
#from simulation_management import simulation_management as SM

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class gridController:

    def __init__(self, id):
        super(gridController, self).__init__()
        logger.info("Initializing simulation controller")
        self.sim = OpenDSS("S4G Simulation")
        self.id = id
        self.nodeNames =[]
        self.allBusMagPu=[]
        self.yCurrent = []
        self.losses = []
        self.voltage_bases = []
        self.city = None
        self.country = None
        self.profess_url = "http://localhost:8080"
        self.sim_days = 0

    def get_profess_url(self):
        return self.profess_url

    def get_city(self):
        return self.city

    def get_country(self):
        return self.country

    def get_sim_days(self):
        return self.sim_days

    def setNewCircuit(self, name, object):
        logger.debug("Creating a new circuit with the name: "+str(name))
        self.sim.setNewCircuit(name, object)
        if object["voltage_bases"]:
            self.voltage_bases = object["voltage_bases"]
            logger.debug(" voltage bases " + str(self.voltage_bases))
        if object["url_storage_controller"]:
            self.profess_url = object["url_storage_controller"]
            logger.debug("profess url: "+str(self.profess_url))
        if object["city"]:
            self.city = object["city"]
            logger.debug("city: "+str(self.city))
        if object["country"]:
            self.country = object["country"]
            logger.debug("country: "+str(self.country))
        if object["simulation_days"]:
            self.sim_days = object["simulation_days"]
            logger.debug("sim_days: "+str(self.sim_days))
        logger.debug("New circuit created")

    def enableCircuit(self, name):
        logger.debug("Enabling the circuit with the name: "+str(name))
        self.sim.enableCircuit(name)
        logger.debug("Circuit "+str(name)+" enabled")

    def setParameters(self, id, duration):
        self.id = id
        self.duration = duration

    def getId(self):
        return self.id

    def getDuration(self):
        return self.duration

    def disableCircuit(self, name):
        logger.debug("Disabling the circuit with the name: "+str(name))
        self.sim.disableCircuit(name)
        logger.debug("Circuit "+str(name)+" disabled")

    def setLoads(self, id, object):
        self.object=object
        logger.debug("Charging loads into the simulator")
        self.sim.setLoads(self.object)
        logger.debug("Loads charged")

    def setTransformers(self, id, object):
        logger.debug("Charging transformers into the simulator")
        self.object = object
        self.sim.setTransformers(self.object)
        logger.debug("Transformers charged")

    def setRegControls(self, id, object):
        logger.debug("Charging RegControls into the simulator")
        self.object = object
        self.sim.setRegControls(self.object)
        logger.debug("RegControls charged")

    def setPowerLines(self, id, powerlines): #(self, id, powerlines, linecodes):
        logger.debug("Charging power lines into the simulator")
        #self.sim.setLineCodes(linecodes)
        try:
            self.sim.setPowerLines(powerlines)
            logger.debug("Power lines charged")
        except ValueError as e:
            logger.error(e)
        
    def setCapacitors(self, id, capacitors):
        logger.debug("Charging capacitors into the simulator")
        #self.object = object
        #self.sim.setCapacitors(self.object)
        self.sim.setCapacitors(capacitors)
        logger.debug("Capacitor charged")

    def setLineCodes(self, id, linecode):
        logger.debug("Charging LineCode into the simulator")
        #self.object = object
        #self.sim.setLineCodes(self.object)
        self.sim.setLineCodes(linecode)
        logger.debug("LineCode charged")

    def setXYCurve(self, id, npts, xarray, yarray):
        logger.debug("Setting the XYCurve into the simulator")
        self.object = object
        self.sim.setXYCurve(self.object)
        logger.debug("XYCurve set")

    def setPhotovoltaic(self, id, photovoltaics):
        logger.debug("Charging the photovoltaics into the simulator")

        self.sim.setPhotovoltaics(photovoltaics)
        logger.debug("Photovoltaics charged")

    def setPVshapes(self, id, pvs, city, country, sim_days, profiles, profess):
        if not city == None and not country == None:
            logger.debug("Charging the pvshapes into the simulator from profiles")
            self.sim.setPVshapes(pvs, city, country, sim_days, profiles, profess)
            logger.debug("loadshapes from profiles charged")
        else:
            logger.error("City and country are not present")

    def setLoadshapes_Off(self, id, loadshapes):
        logger.debug("Charging the loadshapes into the simulator")
        self.sim.setLoadshapes(loadshapes)
        logger.debug("loadshapes charged")

    def setLoadshapes(self, id, loads, sim_days, profiles, profess):
        logger.debug("Charging the loadshapes into the simulator from profiles")
        self.sim.setLoadshapes(loads, sim_days, profiles, profess)
        logger.debug("loadshapes from profiles charged")

    def setLoadshape(self, id, npts, interval, mult):
        logger.debug("Charging a loadshape into the simulator")
        self.sim.setLoadshape(id, npts, interval, mult)
        logger.debug("a loadshape charged")

    def setStorage(self, id, storage):
        logger.debug("Charging the ESS into the simulator")
        self.sim.setStorages(storage)
        logger.debug("ESS charged")

    def setChargingPoints(self, id, object):
        logger.debug("Charging the charging points into the simulator")
        self.object = object
        self.sim.setChargingPoints(self.object)
        logger.debug("Charging points charged")

    def run(self, profess):#self, id, duration):
        #self.id = id
        #self.duration = duration

        logger.debug("Simulation of grid " + self.id + " started")
        logger.debug("These are the parameters")
        logger.debug("GridID: "+str(self.id))
        """logger.debug("Duration: "+str(self.duration))

        day = self.duration.to_dict()["day"]
        logger.debug("Days: "+str(day))
        month= self.duration.to_dict()["month"]
        logger.debug("Months: " + str(month))
        year = self.duration.to_dict()["year"]
        logger.debug("year: " + str(year))
        if day is 0 and month is 0 and year is 0:
            return "Duration is no present"
        if day > 0:
            numSteps=1440*day
        elif month > 0:
            numSteps=1440*30*month
        elif year > 0:
            numSteps = 365

        #self.sim.runNode13()"""
        self.sim.enableCircuit(self.id)

        logger.debug("Active circuit: "+str(self.sim.getActiveCircuit()))
        #return "ok"
        ##################################################################################PROBLEM################################
      
        #self.sim.setVoltageBases(115, 4.16, 0.48)
        self.sim.setVoltageBases(self.voltage_bases)
        #self.sim.setMode("snap")
        self.sim.setMode("daily")
        self.sim.setStepSize("hours")
        self.sim.setNumberSimulations(1)
        logger.info("Solution mode 2: " + str(self.sim.getMode()))
        logger.info("Number simulations 2: " + str(self.sim.getNumberSimulations()))
        logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
        logger.info("Voltage bases: " + str(self.sim.getVoltageBases()))
        logger.info("Starting Hour : " + str(self.sim.getStartingHour()))
        numSteps=self.get_sim_days()
        #numSteps=3
        logger.debug("Number of steps: "+str(numSteps))
        result=[]

        nodeNames = self.sim.get_node_list()

        logger.debug("node_ names "+str(nodeNames))
        voltages = [[] for i in range(len(nodeNames))]
        currents = [[] for i in range(len(nodeNames))]
        losses = [[] for i in range(len(nodeNames))]

        charging = True

        for i in range(numSteps):
            logger.info("#####################################################################")
            logger.info("loop  numSteps, i= " + str(i) )
            logger.info("Starting Hour : " + str(self.sim.getStartingHour()))
            logger.info("#####################################################################")

            topology = profess.json_parser.get_topology()

            if "storageUnits" in topology["radials"][0].keys():
                logger.debug("---------storage control in the loop--------------------------------")
                hours = self.sim.getStartingHour()
                logger.debug("timestep " + str(hours))
                professLoads = self.sim.getProfessLoadschapes(hours, 24)
                #logger.debug("professLoads: " + str(professLoads))
                professPVs = self.sim.getProfessLoadschapesPV(hours, 24)
                #logger.debug("professPVs: " + str(professPVs))
                dummyPrice = [3] * 24
                dummyGESSCON = [3] * 24


                SoC = float(self.sim.getSoCfromBattery("Akku1"))
                logger.debug("SoC_value: " + str(SoC))
                logger.debug("charging " + str(charging))
                if charging is True:
                    logger.debug("Entered to charging")
                    if SoC >= 100:
                        logger.debug("Setting charging to false")
                        charging = False
                    self.sim.setActivePowertoBatery("Akku1", -0.5)
                else:
                    logger.debug("Entered to discharging")
                    if SoC <= 0:
                        charging = True
                    self.sim.setActivePowertoBatery("Akku1",0.5)



                #profess.set_up_profess_for_existing_topology(professLoads, professPVs, dummyPrice, dummyGESSCON)
                """self.profess.set_up_profess_for_existing_topology( professLoads, self.dummyPV, self.dummyPrice, self.dummyGESSCON)
                self.profess.start_all()
                print("--------------------start profess results----------------------------")
                print(self.profess.dataList)
                print(self.profess.wait_and_get_output())
                soc_list = [{"633": {"SoC": 5}}, {"671": {"SoC": 4}}, {"634": {"SoC": 20}}]
                self.profess.update(professLoads, self.dummyPV, self.dummyPrice, soc_list, self.dummyGESSCON)
                print(self.profess.dataList)
                print("--------------------end profess results----------------------------")"""
            else:
                logger.debug("No Storage Units present")


            puVoltages, Currents, Losses = self.sim.solveCircuitSolution()
            logger.debug("Voltage "+str(puVoltages[0]))
            for i in range(len(nodeNames)):
                voltages[i].append(puVoltages[i])
                currents[i].append(Currents[i])
                losses[i].append(Losses[i])



        #logger.debug("volt finish "+str(voltages))

        data ={}
        raw_data={}

        for i in range(len(nodeNames)):
            raw_data[nodeNames[i]] = {"Voltage": voltages[i], "Current": currents[i], "Loss": losses[i]}
            data[nodeNames[i]]={"Voltage": {"max":max(voltages[i]), "min":min(voltages[i])}, "Current":max(currents[i]), "Loss":max(losses[i])}

        data2={}
        for key, value in data.items():
            node, phase = key.split(".", 1)
            if node not in data2.keys():
                data2[node] = {}

            data2[node]["Phase_" + phase] = value


        result=data2
        #logger.debug("result: "+str(result))

        """df = self.sim.utils.lines_to_dataframe()
        data = df[['Bus1', 'Bus2']].to_dict(orient="index")
        for name in data:
            self.sim.Circuit.SetActiveBus(f"{name}")
            if phase in self.sim.Bus.Nodes():
                index = self.sim.Bus.Nodes().index(phase)
                re, im = self.sim.Bus.PuVoltage()[index:index+2]
                V = abs(complex(re,im))
        logger.info("Voltage: " + str(V))"""
        logger.info("Solution step size 2: " + str(self.sim.getStepSize()))
        """logger.info("Node Names: "+ str(nodeNames))
        logger.info("All Bus MagPus: " + str(allBusMagPu))"""
        #!TODO: return node names, voltage and current in json
        #data = {"NodeNames": nodeNames, "Voltage": allBusMagPu}
        #return json.dumps(data)
        """logger.info("YCurrent: " + str(yCurrent))
        logger.info("losses: " + str(losses))"""
        #return ("Nodes: " + str(nodeNames), "\nVoltages " + str(allBusMagPu))
        #return (nodeNames, allBusMagPu)
        #filename = str(id)+"_results.txt"
        #!TODO: Create filename with id so serve multiple simultaneous simulations#DONE
        #json_data = json.dumps(allBusMagPu)
        fname = (str(self.id))+"_result"
        fname_row = (str(self.id)) + "_result_row.json"
        logger.debug("Storing results in data folder")
        os.chdir(r"./data")
        with open(fname, 'w', encoding='utf-8') as outfile: 
            #/usr/src/app/tests/results/
            #outfile.write(json_data) # working
            #logger.debug("data "+str(allBusMagPu))
            json.dump(result, outfile, ensure_ascii=False, indent=2) # working
            #json.dump(json_data, outfile, ensure_ascii=False, indent=2)  # not working !!!
        logger.debug("Results succesfully stored")
        logger.debug("Stroring raw data in data folder")
        with open(fname_row, 'w', encoding='utf-8') as outfile:
            json.dump(raw_data, outfile, ensure_ascii=False, indent=2) # working
        logger.debug("Raw data successfully stored")

        os.chdir(r"../")

        return id
    
    #def results(self):   
        #return (self.nodeNames, self.allBusMagPu)
        #self.finish_status = True
        #return "OK"
        """#ToDo test with snap and daily
        self.sim.setMode("daily")
        self.sim.setStepSize("minutes")
        self.sim.setNumberSimulations(1)
        self.sim.setStartingHour(0)
        self.sim.setVoltageBases(0.4,16)

        #for i in range(numSteps):
            #self.sim.solveCircuitSolution()
            #setStorageControl()
            #If
            #DSSSolution.Converged
            #Then
            #V = DSSCircuit.AllBusVmagPu"""
