from Profess import *
from JSONparser import *

domain = "http://localhost:8080/v1/"
dummyInputData = open('inputData.json').read()
jsonInputDataFile=json.loads(dummyInputData)
IEEE13=open("IEEE13_changed.json").read()
jsonIEEE = json.loads(IEEE13)

modelDataFile = open('model.json').read()


p1 = Profess("http://localhost:8080/v1/", dummyInputData)
dummyprofile= [3] * 24
dummyLoads=[]
dummyPrice=[]
dummyPV=[]
p1.json_parser.set_topology(jsonIEEE)
for element in p1.json_parser.get_node_name_list():
    dummyDict={element:[{element+".1": copy.deepcopy(dummyprofile)},
                        {element+".2": copy.deepcopy(dummyprofile)},
                        {element+".3": copy.deepcopy(dummyprofile)}]}
    dummyLoads.append(dummyDict)
dummyPV = copy.deepcopy(dummyprofile)
dummyPrice = copy.deepcopy(dummyprofile)
element="671"
dummyDict = {element: [{element + ".1.2.3": copy.deepcopy(dummyprofile)}]}
dummyLoads[1]= dummyDict
#print(dummyLoads)
#print(dummyPV)
#print(dummyPrice)

#print(p1.json_parser.get_node_element_list())

p1.set_up_profess(jsonIEEE, dummyLoads, dummyPV, dummyPrice)
p1.start_all("MaximizePVNoLoad")
#print(p1.dataList)
print(p1.wait_and_get_output(p1.dataList))



