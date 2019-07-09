import json
from collections.abc import Iterable

IEEE13=open("IEEE13_changed.json").read()

jsonIEEE=json.loads(IEEE13)

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
                            for element in searchIn[value]:
                                searchResult.append(element)
                        else:
                            searchResult.append(searchIn[value])
                    else:
                        searchResult.append(searchIn)
            if isinstance(searchIn[value], Iterable) and type(searchIn[value]) != str:
                searchResult = searchResult + search(searchIn[value], searchFor, searchID, returnsAll)

    return searchResult
#print(search(jsonIEEE,"bus1",nodeID,False))
helps=[]
helps=search(jsonIEEE,"storageUnits","storageUnits",True)
#print(helps)
helper=search(helps,"bus1","bus1",True)
#print(helper)
#print(int(helper[0]))
for element in range(len(helper)):

    print(search(jsonIEEE,"bus1",helper[element],False)+search(jsonIEEE,"bus",helper[element],False))