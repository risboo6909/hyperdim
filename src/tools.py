# 2010 Boris Tatarintsev
# mailto: ttyv00@gmail.com

import re
import string
import copy

from geometry import *
from utils3d import *

def flat(xss):
   if not isinstance(xss, list): return [xss]
   elif len(xss) == 1: return(flat(xss[0]))   
   return reduce( lambda x, y: flat(x) + flat(y), xss ) 

def flatToStr(xss):
   return reduce( lambda x, y: str(x) + str(y), flat(xss) )

def findDataBlocks(filename):
    verticesData, edgesData = [], []
    properties = {}
    
    flag1, flag2 = False, False
    f = open(filename, "rt")
    data = f.readlines()
    for line in data:
        # data blocks
        if string.strip(line) == "Vertices:":
            # read vertices data
            flag1, flag2 = True, False
            continue
        elif string.strip(line) == "Edges:":
            # read edges data
            flag1, flag2 = False, True
            continue
        # properties [property_name:value]
        else:
            tmp = re.split('#', filter(lambda x: x != '\n' and x != '\t' and x != ' ', line))[0]
            if tmp != "":                
                result = re.search("([a-z]+).*:.*(\d+)", tmp, flags = re.IGNORECASE)
                if result:
                    key, value = getPropertyValue(result)
                    properties[key] = value
                    continue
        if flag1:
            verticesData.append(line[:])
        elif flag2:
            edgesData.append(line[:])
    f.close()
    return verticesData, edgesData, properties

def getPropertyValue(match):    
    return match.group(1), match.group(2)

def parseData(data):
    parsedData = {}
    # parse data
    for item in data:
        # split each string into two parts: before # and after #
        tmp = re.split('#', filter(lambda x: x != '\n' and x != '\t' and x != ' ', item))[0]
        # yeahh, functional programming is cool )))
        # extract prefix and suffix (they are separated by ':')
        if len(tmp.split(':')) == 2:
            # split into tokens
            (pref, post) = re.split(':', tmp.strip())
            # filter, re and map :)
            tmp = filter(lambda x: len(x) > 0, re.split(',', string.strip(post,'{}')))
            parsedData[int(pref)] =  map(lambda x: float(x.strip()), tmp)
    return parsedData

def readDataFromFile(filename):
    # read data from a file
    verticesData, edgesData, properties = findDataBlocks(filename)
    return parseData(verticesData), parseData(edgesData), properties

def loadModelFromFile(name, filename, sceneObjects):
    # reads geometry data of ND model from a file
    verticesData, edgesData, properties = readDataFromFile(filename)
    sceneObjects[name] = Geometry(verticesData, edgesData, properties)
