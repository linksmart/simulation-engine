import json
from collections.abc import Iterable
import re

IEEE13=open("IEEE13_changed.json").read()
topology =json.loads(IEEE13)

# @search returns a list with results
    # @searchIn is the dict/list we search in
    # @searchFor is the String we search for
    # @returnsAll if true, returns all where searchFor fits, even if searchID doesn't fit
def search(searchIn, searchFor, searchID, returnsAll):

    searchResult = []
    dummyList = searchIn
    if type(searchIn) == list:
        dummyList = []
        for element in range(len(searchIn)):
            dummyList.append(element)
    for value in dummyList:
        if type(value) == dict or type(value) == list:
            for element in value:
               if isinstance(value[element], Iterable) and type(value[element]) != str:
                   searchResult = searchResult + search(value[element], searchFor, searchID, returnsAll)
        else:
            if value == searchFor:
               if searchIn[value] == searchID or returnsAll:
                    # print("matching id")
                    if returnsAll:
                        if type(searchIn[value]) == list:
                            helpList={}
                            for element in searchIn[value]:
                                searchResult.append(element)
                        else:
                            searchResult.append(searchIn[value])
                    else:
                        #print(searchIn)
                        #print(value)
                        searchResult.append(searchIn)
            if isinstance(searchIn[value], Iterable) and type(searchIn[value]) != str:
                searchResult = searchResult + search(searchIn[value], searchFor, searchID, returnsAll)

    return searchResult
def setTopology(jsonTopology):
    global topology
    topology=jsonTopology
def getNodeElementList():
    nodeElementList=[]
    nodeList=search(topology["radials"][0]["storageUnits"], "bus1", "", True)



    count=0
    for element in nodeList:
        pattern = re.compile("[^.]*")  #regex to find professID
        m= pattern.findall(element)
        element=m[0]
        nodeElementList.append({element:[{"storageUnits":topology["radials"][0]["storageUnits"][count]}]})
        nodeElementList[count][element].append({"loads":(search(topology["radials"][0]["loads"], "bus", element, False))})
        #TODO PV etc
        count=count+1
    return nodeElementList
def getNodeNameList():
    nameList=[]
    for element in getNodeElementList():
        for value in element:

            nameList.append(value)
    return nameList
setTopology(json.loads(IEEE13))

#print(search(jsonIEEE,"bus1",nodeID,False))
helps=[]
helps=search(topology, "storageUnits", "storageUnits", True)
#print(helps)
helper=search(helps, "bus1", "bus1", True)
#print(helper)
#for element in helper:
    #print(search(topology, "bus1", element, False)+search(topology, "bus", element, False))

getNodeElementList()
#print(int(helper[0]))
