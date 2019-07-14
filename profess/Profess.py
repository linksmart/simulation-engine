from Http_commands import Http_commands
import re
import copy
from JSONparser import search
import win32com.client
from win32com.client import makepy
import sys
import numpy as np
import simplejson as json
import time

#global variables

domain = "http://localhost:8080/v1/"
inputDataFile = open('inputData.json').read()
jsonInputDataFile=json.loads(inputDataFile)
IEEE13=open("IEEE13_changed.json").read()
jsonIEEE=json.loads(IEEE13)

dataList=[]


modelDataFile = open('model.json').read()
pathLoad=""
pathModel=""
pathLinesCode =""
pathLines =""
pathTransformator=""
pathNodes=""
ofwOutput =""
httpClass = Http_commands()



# Power Flow with NO generation
    #DSSText.Command='clear'
    #DSSText.Command='Redirect (' + path_complete + ')'
    #DSSText.Command='New Energymeter.m1 element=Line.ln5815900-1 terminal=1'
    #DSSText.Command='set Maxiterations=20'     # Sometimes the solution takes more than the default 15 iterations
    #DSSSolution.Solve()
# Show some results
    #DSSText.Command='Plot Profile Phases=All'
    #DSSText.Command='Show EventLog'
    #Show_Summary_BaseCase()


######################


class Profess:
    def __init__(self):
        print("profess class created")


    def post_model(self, modelName, modelData):
        response=httpClass.put(domain+"models/"+modelName, modelData)
        json_response = response.json()
        print(json_response)

    def post_data(self, inputData, nodeNumber):

        response = httpClass.post(domain+"inputs/dataset", inputData, "json")
        json_response = response.json()
        print("answer: "+json_response)
        pattern = re.compile("/inputs*[/]([^']*)")  #regex to find professID
        m= pattern.findall(str(response.headers))

        print(response.status_code)
        if m!="":
            professID = m[0]
            print(professID)
        else:
            print("an error happend with regex")
        self.setProfessIDForNode(nodeNumber,professID)
        self.setConfigJSON(nodeNumber, professID, inputData)
        print(dataList)
    def get_output(self,professID):
        if(professID!=""):
            response = httpClass.get(domain+"outputs/"+professID)

        else:
            print("No Input get output declared")
        return response.json()
    def start(self,freq,horizon,dt,model,repition,solver,optType,professID):
        if professID!="":
            response = httpClass.put(domain + "optimization/start/" + professID, {"control_frequency": freq,
                                                                                    "horizon_in_steps": horizon,
                                                                                    "dT_in_seconds": dt,
                                                                                    "model_name": model,
                                                                                    "repetition": repition,
                                                                                    "solver": solver,
                                                                                    "optimization_type": optType})
            json_response = response.json()
            print(json_response)
        else:
            print("No Input to start declared")

    def stop(self,professID):
        if professID!="":
            response = httpClass.put(domain + "optimization/stop/" + professID)
            json_response = response.json()
            print(json_response)
        else:
            print("No Input to stop declared")
    def updateConfigJson(self,professID,configJSON):
        httpClass.put(domain+"inputs/dataset/"+professID, configJSON, "json")
    def setDataValue(self,valueName1,valueName2,dataKey,targetDict):
        targetDict[valueName1]=search(jsonIEEE, "storageUnits", "storageUnits", True)[dataKey][valueName2]
        #TODO
    def setStorage(self,dataKey):
        for element in dataList[dataKey]:
            nodeName =element
        for element in dataList[dataKey][nodeName]:
            professID=element
        jsonDataOfNode= dataList[dataKey][nodeName][professID]
        self.setDataValue("SoC_Value","soc",dataKey,jsonDataOfNode["ESS"])
        self.setDataValue("ESS_Charging_Eff","charge_efficiency",dataKey,jsonDataOfNode["ESS"]["meta"])
        self.setDataValue("ESS_Discharging_Eff", "discharge_efficiency", dataKey, jsonDataOfNode["ESS"]["meta"])

        self.setDataValue("ESS_Max_Charge_Power", "kw_rated", dataKey, jsonDataOfNode["ESS"]["meta"])
        self.setDataValue("ESS_Max_Discharge_Power", "kw_rated", dataKey, jsonDataOfNode["ESS"]["meta"])
        self.setDataValue("ESS_Capacity", "kwh_rated", dataKey, jsonDataOfNode["ESS"]["meta"])
        #TODO changes have to be made
    def setConfigJSON(self,nodeNumber,professID,jsonConfig):
        for element in dataList[nodeNumber]:
            nodeName=element
        dataList[nodeNumber][nodeName][professID] = copy.deepcopy(jsonConfig)
    def setProfessIDForNode(self,nodeNumber,professID):
        for element in dataList[nodeNumber]:
            nodeName=element
        dataList[nodeNumber][nodeName][professID]= {}
    def setPV(self,nodeNumber):
        print("TODO")
        #TODO
    def setLoad(self,nodeNumber):
        print("TODO")

p1 = Profess()

nodeList=search(jsonIEEE["radials"][0]["storageUnits"], "bus1", "", True)
print(nodeList)
print()
for element in range(len(nodeList)):
    nodeList[element] = {nodeList[element]: {}}
#print(jsonInputDataFile)
dataList=nodeList


#print(jsonInputDataFile)
#print(search(jsonIEEE, "storageUnits", "storageUnits", True))
#print(dataList)

#helper=json.loads(inputDataFile)
#helper["ESS"]["SoC_Value"]=1
#print((type(helper["ESS"]["SoC_Value"])))
p1.post_data(json.loads(inputDataFile),0)
p1.setStorage(0)
for element in dataList[0]["633"]:
    print(element)
    print(httpClass.get(domain+"inputs/dataset/"+element).json())
    p1.start(10, 24, 3600, "testmodel", 1, "ipopt", "discrete",element)
p1.post_model("testmodel", modelDataFile)


#while str(p1.get_output())=="{}": #busy Waiting
    #time.sleep(5)
    #print("waiting for output")



#print(p1.get_output())
#ofwOutput=p1.get_output()
#print(ofwOutput['P_ESS_Output'])
#print(type(search(jsonIEEE,"storageUnits","storageUnits",True)[2]))

