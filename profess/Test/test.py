from Profess import *
from JSONparser import *

domain = "http://localhost:8080/v1/"
dummyInputData = open('inputData.json').read()
jsonInputDataFile=json.loads(dummyInputData)
IEEE13=open("IEEE13_changed.json").read()
jsonIEEE = json.loads(IEEE13)

modelDataFile = open('model.json').read()


p1 = Profess(dummyInputData)
dummyLoad=[0]*24
dummyList=[]
p1.json_parser.set_topology(jsonIEEE)
for element in p1.json_parser.get_node_name_list():
    dummyDict={element:[{"PV": copy.deepcopy(dummyLoad)},{"load":[{element+".1":copy.deepcopy(dummyLoad)},
                                                                   {str(element)+".2":copy.deepcopy(dummyLoad)},
                                                                   {str(element)+".3":copy.deepcopy(dummyLoad)}]},
                        {"price":copy.deepcopy(dummyLoad)}]}
    dummyList.append(dummyDict)
print(dummyList)


print(p1.json_parser.get_node_element_list())

p1.set_up_profess(jsonIEEE, dummyLoad, dummyLoad, dummyLoad)
p1.start_all("MaximizePVNoLoad")
print(p1.json_parser.get_node_element_list())
#p1.post_model("testmodel", modelDataFile)



#for element in p1.dataList[0]["633"]:
    #print(element)
    #print(p1.httpClass.get(domain+"inputs/dataset/"+element).json())
