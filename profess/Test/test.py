from Profess import *
from JSONparser import *
import json

#domain = "http://localhost:8080/v1/"
domain = "http://192.168.99.100:8080/v1/"
dummyInputData = open('inputData.json').read()
jsonInputDataFile=json.loads(dummyInputData)
IEEE13=open("IEEE13_changed.json").read()
jsonIEEE = json.loads(IEEE13)

modelDataFile = open('model.json').read()


p1 = Profess("http://localhost:8080/v1/")
dummyprofile= [3] * 24
dummyLoads=[]
dummyPrice=[]
dummyPV=[]
p1.json_parser.set_topology(jsonIEEE)
dummyPVdict=[]
for element in p1.json_parser.get_node_name_list():
    dummyDict={element:{element+".1": copy.deepcopy(dummyprofile),element+".2": copy.deepcopy(dummyprofile),element+".3": copy.deepcopy(dummyprofile)}}
    dummyLoads.append(dummyDict)
    dummyPVdict={element:{element+".1.2.3": copy.deepcopy(dummyprofile)}}
    dummyPV.append(dummyPVdict)


dummyPrice = copy.deepcopy(dummyprofile)
element="671"
dummyDict = {element: [{element + ".1.2.3": copy.deepcopy(dummyprofile)}]}
dummyLoads[1]= dummyDict
dummyGESSCON=[{'633':
{'633.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0]}},
{'671': {'671.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0]}}]

#print(dummyLoads)
#print(dummyPV)
#print(dummyPrice)

#print(p1.json_parser.get_node_element_list())

p1.set_up_profess(jsonIEEE, dummyLoads, dummyPV, dummyPrice, dummyGESSCON)
#print(p1.json_parser.get_node_element_list())

p1.start_all()
#print(p1.dataList)
print(p1.wait_and_get_output())


soc_list=[{"633":{"SoC":5}},{"671":{"SoC":4}},{"634":{"SoC":20}}]
p1.update(dummyLoads, dummyPV, dummyPrice,soc_list,dummyGESSCON)
#print(p1.dataList)

#print(sorted(test))
#p1.translate_output(test)