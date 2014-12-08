# 2010 Boris Tatarintsev
# mailto: ttyv00@gmail.com

from matrix import Matrix
from vector import Vector
from utils3d import *

import copy
import tools

# Contains geometry data

epsilon = 1.0 / (10 ** 10)

class Geometry:
    
    def __init__(self, vertexData, edgesData, properties):
        self.properties = properties
        # contains data which describes faces triangles
        self.facesData = []
        # as we may have higher dimensions data, we need to save
        # projected into 3D volume vertices data in dedicated lists
        self.vertexData3D = None
        # temporary vertex data
        self.vertexTempData = None
        # dim of geometry data
        self.dim = 3
        # setup data
        self.setVertexData(vertexData)
        self.setEdgesData(edgesData)
        # compute center of mass
        self.setCenterOfMass(computeCenterOfMass(self.getVertexData().values()))
        
    def setCenterOfMass(self, centerOfMass):
        self.centerOfMassVec = centerOfMass.clone()
    
    def getCenterOfMass(self):
        return self.centerOfMassVec
    
    def testInclusion(self, v, vertices):
        for v_prime in vertices:
            if v == v_prime: return False
        return True
         
    def generateFacesData(self, vertices = [], inclusionTest = [], cur = 0, N = None):        
        # calculate points which lie in the same plane
        # If we have M > 3 points for a face we have to determine 
        # each M points which lie in the same plane
        # The algorithm is as follows:
        # 1. take any 3 points, they are always produce a triangle
        # 2. assume that this triangle is a plane we are trying to find
        # 3. compute normal vector to the plane (N), it will be a cross product of two vectors of a triangle
        # 4. check each of the points left, if radius-vector of our point (R) lies in the same plane as three
        # points of a triangle, we assume that these M + 1 points produce a plane in space
        # The formal definition will be:
        # 1. take three points: a, b, c
        # 2. calculate radius vectors: ab, ac
        # 3. compute their cross product: N = cross(ab, ac)
        # 4. check whether fourth point p, produces vector ap which has a zero dot product with N: dot(N, ap) == 0
        # 5. if true then we have a quad plane, if false go to the next point        
        
        if not self.properties.has_key('VertPerFace'):
            print "Unable to generate faces data, VertPerFace property missing!"
            return
        
        if cur == 3:
            # we have a triangle, compute a normal vector to it
            vec1, vec2, vec3 = Vector(vertices[0]), Vector(vertices[1]), Vector(vertices[2])
            N = Matrix.crossProduct3D(vec2 - vec1, vec3 - vec1)            
            
        if int(self.properties['VertPerFace']) == cur:
            # check if we have a 'good' plane
            isPlane = True            
            for j in xrange(3, len(vertices)):                
                if abs((Vector(vertices[j]) - Vector(vertices[0])).dotProduct(N)) > epsilon:
                    isPlane = False
                    break
            if isPlane:     
                s = set(tools.flat(vertices))
                try:
                    # check if we have this item in our list already
                    inclusionTest.index(s)
                except:                    
                    # add if not
                    self.facesData.append(vertices[:])
                    inclusionTest.append(s)
            return
        
        for v in filter(lambda x: self.testInclusion(x, vertices), self.getVertexData().values()):            
            vertices.append(v)
            #print "+", vertices
            self.generateFacesData(vertices, inclusionTest, cur + 1, N)
            vertices.pop()
            #print "-", vertices
                                      
    def setVertexData(self, vertexData):
        if vertexData != None:
            self.vertexData = copy.copy(vertexData)
            self.dim = len(vertexData.values()[0])
            # if dimension of data is 3D then it does not need to be projected into 3D
            if self.dim == 3:
                self.vertexData3D = self.vertexData
        else:
            self.vertexData = None
        
    def setEdgesData(self, edgesData):
        if edgesData != None:
            self.edgesData = copy.copy(edgesData)
            if self.dim == 3:
                self.edgesData3D = self.edgesData
        else:
            self.edgesData = None
            
    def setVertexData3D(self, vertexData):
        if vertexData != None:
            self.vertexData3D = copy.copy(vertexData)
        else:
            self.vertexData3D = None
    
    def setVertexTempData(self, vertexData):
        self.vertexTempData = vertexData
        
    def getVertexData(self):
        return self.vertexData
    
    def getEdgesData(self):        
        return self.edgesData

    def getVertexTempData(self):
        return self.vertexTempData

    def getVertexData3D(self):
        return self.vertexData3D

    def getDim(self):
        return self.dim
