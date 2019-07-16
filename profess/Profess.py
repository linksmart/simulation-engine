from Http_commands import Http_commands
import re
import copy
from JSONparser import *
import win32com.client
from win32com.client import makepy
import sys
import numpy as np
import simplejson as json
import time

#global variables

domain = "http://localhost:8080/v1/"
dummyInputData = open('inputData.json').read()
jsonInputDataFile=json.loads(dummyInputData)
IEEE13=open("IEEE13_changed.json").read()
jsonIEEE=json.loads(IEEE13)

dataList=[]


modelDataFile = open('model.json').read()
httpClass = Http_commands()


######################


class Profess:
    def __init__(self):
        print("profess class created")


    def post_model(self, modelName, modelData):
        response=httpClass.put(domain+"models/"+modelName, modelData)
        json_response = response.json()
        #print(json_response)

    def post_data(self, inputData, nodeName):

        response = httpClass.post(domain+"inputs/dataset", inputData, "json")
        json_response = response.json()
        print("answer: "+json_response)
        pattern = re.compile("/inputs*[/]([^']*)")  #regex to find professID
        m= pattern.findall(str(response.headers))

        #print(response.status_code)
        if m!="":
            professID = m[0]
        else:
            print("an error happend with regex")

        self.setProfessIDForNode(nodeName,professID)
        self.setConfigJSON(nodeName, professID, inputData)
        #print(dataList)
    def postAllDummyData(self):
        elements=getNodeElementList()
        for nodeKey in elements:
            for value in nodeKey:
                self.post_data(json.loads(dummyInputData), value)
                self.setStorage(value)
        #TODO
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
    def startAll(self,modelName):
        for element in getNodeNameList():

            self.start(10, 24, 3600, modelName, 1, "ipopt", "discrete",self.getProfessID(element))
    def stop(self,professID):
        if professID!="":
            response = httpClass.put(domain + "optimization/stop/" + professID)
            json_response = response.json()
            print(json_response)
        else:
            print("No Input to stop declared")
    def updateConfigJson(self,professID,configJSON):
        httpClass.put(domain+"inputs/dataset/"+professID, configJSON)

    def setStorage(self, nodeName):
        #print(getNodeElementList()[nodeNumber])
        nodeNumber=getNodeNameList().index(nodeName)
        for element in dataList[nodeNumber]:
            nodeName =element
        for element in dataList[nodeNumber][nodeName]:
            professID=element
        jsonDataOfNode= dataList[nodeNumber][nodeName][professID]
        jsonDataOfNode["ESS"]["SoC_Value"] = getNodeElementList()[nodeNumber][nodeName][0]["storageUnits"]["soc"]/100
        jsonDataOfNode["ESS"]["meta"]["ESS_Charging_Eff"] = getNodeElementList()[nodeNumber][nodeName][0]["storageUnits"][
            "charge_efficiency"]/100
        jsonDataOfNode["ESS"]["meta"]["ESS_Discharging_Eff"] = getNodeElementList()[nodeNumber][nodeName][0]["storageUnits"][
            "discharge_efficiency"]/100
        jsonDataOfNode["ESS"]["meta"]["ESS_Max_Charge_Power"] = getNodeElementList()[nodeNumber][nodeName][0]["storageUnits"][
            "kw_rated"]
        jsonDataOfNode["ESS"]["meta"]["ESS_Max_Discharge_Power"] = getNodeElementList()[nodeNumber][nodeName][0]["storageUnits"][
            "kw_rated"]
        jsonDataOfNode["ESS"]["meta"]["ESS_Capacity"] = getNodeElementList()[nodeNumber][nodeName][0]["storageUnits"]["kwh_rated"]

    def setConfigJSON(self,nodeName,professID,jsonConfig):
        nodeNumber=getNodeNameList().index(nodeName)

        dataList[nodeNumber][nodeName][professID] = copy.deepcopy(jsonConfig)
    def setProfessIDForNode(self,nodeName,professID):
        nodeNumber=getNodeNameList().index(nodeName)

        dataList[nodeNumber][nodeName][professID]= {}
    def setProfils(self,profilesList):
        for nodeName in getNodeNameList():
            nodeNumber = getNodeNameList().index(nodeName)
            for element in profilesList:
                if nodeName in element:
                    professID=self.getProfessID(nodeName)
                    jsonDataOfNode = dataList[nodeNumber][nodeName][professID]
                    jsonDataOfNode["photovoltaic"]["P_PV"] =element[nodeName][0]["PV"]
                    jsonDataOfNode["generic"]["Price_Forecast"] =element[nodeName][2]["price"] #No reserved words for price
                    for phase in element[nodeName][1]["load"]:

                        if nodeName+".1" in phase:
                            jsonDataOfNode["load"]["P_Load_R"] = phase[nodeName+".1"]
                        if nodeName+".2" in phase:
                            jsonDataOfNode["load"]["P_Load_S"] = phase[nodeName+".2"]
                        if nodeName+".3" in phase:
                            jsonDataOfNode["load"]["P_Load_T"] = phase[nodeName+".3"]
        #TODO
    def setLoad(self,nodeName):
        print("TODO")
    def getProfessID(self,nodeName):
        nodeNumber = getNodeNameList().index(nodeName)

        for element in dataList[nodeNumber][nodeName]:
            professID =element
        return professID

    def setDataList(self):
        nodeList = getNodeElementList()
        for element in range(len(nodeList)):
            for nodeKey in (nodeList[element]):
                nodeList[element] = {nodeKey: {}}

        # print(jsonInputDataFile)
        global dataList
        dataList = nodeList
    def setUpProfess(self,profilesList):
        p1.setDataList()
        self.postAllDummyData()
        self.setProfils(profilesList)
        for nodeName in getNodeNameList():
            self.setStorage(nodeName)
            professID=self.getProfessID(nodeName)
            nodeNumber = getNodeNameList().index(nodeName)
            self.updateConfigJson(professID,dataList[nodeNumber][nodeName][professID])

        print(dataList)

    def setDummyJSON(self,dummy):
        global dummyInputData
        dummyInputData=dummy

p1 = Profess()
dummyLoad=[0]*24
dummyList=[]
for element in getNodeNameList():
    dummyDict={element:[{"PV": copy.deepcopy(dummyLoad)},{"load":[{element+".1":copy.deepcopy(dummyLoad)},
                                                                   {str(element)+".2":copy.deepcopy(dummyLoad)},
                                                                   {str(element)+".3":copy.deepcopy(dummyLoad)}]},
                        {"price":copy.deepcopy(dummyLoad)}]}
    dummyList.append(dummyDict)
print(dummyList)




p1.setUpProfess(dummyList)
p1.startAll("testmodel")
#p1.post_model("testmodel", modelDataFile)
for element in dataList[0]["633"]:
    #print(element)
    print(httpClass.get(domain+"inputs/dataset/"+element).json())
