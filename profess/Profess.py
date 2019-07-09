from Http_commands import Http_commands
import re
import win32com.client
from win32com.client import makepy
import sys


import numpy as np
import simplejson as json
import time

#global variables

domain = "http://localhost:8080/v1/"
inputDataFile = open('inputData.json').read()
location = ""
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

    def post_data(self, inputData):

        response = httpClass.post(domain+"inputs/dataset", inputData, "json")
        json_response = response.json()
        print("answer: "+json_response)
        pattern = re.compile("/inputs*[/]([^']*)")
        m= pattern.findall(str(response.headers))
        global location
        print(response.status_code)
        if m!="":
            location = m[0]
            print(location)
        else:
            print("an error happend with regex")
    def get_output(self):
        if(location!=""):
            response = httpClass.get(domain+"outputs/"+location)

        else:
            print("No Input get output declared")
        return response.json()
    def start(self,freq,horizon,dt,model,repition,solver,optType):
        if location!="":
            response = httpClass.put(domain + "optimization/start/" + location, {"control_frequency": freq,
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

    def stop(self):
        if location!="":
            response = httpClass.put(domain + "optimization/stop/" + location)
            json_response = response.json()
            print(json_response)
        else:
            print("No Input to stop declared")



p1 = Profess()

p1.post_data(json.loads(inputDataFile))
p1.post_model("testmodel", modelDataFile)
p1.start(10, 24, 3600, "testmodel", 1, "ipopt", "discrete")


while str(p1.get_output())=="{}": #busy Waiting
    time.sleep(5)
    print("waiting for output")



print(p1.get_output())
ofwOutput=p1.get_output()
print(ofwOutput['P_ESS_Output'])

#TODO es gibt fehler im konvertieren der files zu json, die zu errorn führen
