# 2010 Boris Tatarintsev
# mailto: ttyv00@gmail.com

import copy

from vector     import *
from matrix     import *

epsilon = 1.0 / (10 ** 10)

class Camera4D:

    def __init__(self, position, up, direction, w):
        # we need three vectors to be defined to set up a camera
        # position in 4D space instead of two vectors (up and direction) in 3D
        # since I don't know how to name the third vector I will simply call
        # it w further in code
        self.v = Matrix.crossProduct(Matrix([up, direction, w]))
        self.up = up
        self.direction = direction
        self.position = position
        self.w = w
        # homogenous coords
        self.v.appendComponent(0)
        self.up.appendComponent(0)
        self.direction.appendComponent(0)
        self.position.appendComponent(0)
        self.w.appendComponent(0)
        # create camera matrix
        #print "\n*", self.v.toString()
        #print "*", self.up.toString()
        #print "*", self.direction.toString()
        #print "*", self.w.toString()
        #print "*", self.position.toString()
        self.camMat = Matrix()
        self.camMat.appendRow(self.v)
        self.camMat.appendRow(self.up)
        self.camMat.appendRow(self.direction)
        self.camMat.appendRow(self.w)
        self.camMat.appendRow(self.position)
        # we don't need to transpose camMat here because we don't use
        # openGL to calculate it
        
        # this is a 4D camera
        self.cameraDim = 4

    def getCameraDim(self):
        return self.cameraDim

    def buildProjectionMatrix4D(self, left, right, bottom, top, near, far):
        """                
        construct the 4D->3D projection matrix
        We need to define projecting volume (as analogue to NEAR projecting
        plane in 3D->2D perspective projection).            
        We define this volume by its constraints:
            left, right, bottom, top, near, far - these three parameters
            define cube in 3D space which our 4D models will project in
       
        @param params: left, right, bottom, top, near, far
        @type params: float, float, float, float, float, float
        @return: projection matrix
        @rtype: Matrix
        """
        row1 = Vector([2.0 / (right - left), 0, 0, 0, -1.0 * (right + left) / (right - left)])
        row2 = Vector([0, 2.0 / (top - bottom), 0, 0, -1.0 * (top + bottom) / (top - bottom)])
        row3 = Vector([0, 0, 2.0 / (far - near), 0, -1.0 * (far + near) / (far - near)])
        row4 = Vector([0, 0, 0, 0, 0])
        row5 = Vector([0, 0, 0, 0, 1.0])
        return Matrix([row1, row2, row3, row4, row5])

    def setupProjectionMatrix(self, projMat):
        self.projMat = projMat       

    def getCameraTransformation(self):
        # returns transformation matrix for the current camera
        return self.plain

    def getOGLCameraTransformation(self):
        # returns transformation matrix for the camera in OpenGL form        
        return self.ogl

    def getCameraBasis(self):
        e1  = self.camMat.getCol(0).getComponents()
        e2  = self.camMat.getCol(1).getComponents()
        e3  = self.camMat.getCol(2).getComponents()
        e4  = self.camMat.getCol(3).getComponents()
        pos = self.camMat.getCol(4).getComponents()
        return([e1, e2, e3, e4, pos])

    def compute(self, object):
        # compute camera transformation      
        #print self.camMat.transposeSelf().toString()  
        buf = {}
        for vKey in object.getVertexData().keys():
            # TODO: optimize!            
            v = object.getVertexData()[vKey][:]
            v.append(1.0)
            tmp = Matrix.mul(Matrix([v]), self.camMat)            
            buf[vKey] = (tmp.getRow(0).getComponents()[:-1])
        object.setVertexTempData(buf)
        #object.setVertexTempData(object.getVertexData())
    
    def applyProjectionMatrix(self, vertices):
        if self.projMat == None:
            return vertices
        vcopy = copy.deepcopy(vertices)
        M = Matrix.transpose(self.projMat)
        # TODO: optimize!        
        for vidx in vcopy.keys():
            vertex = vcopy[vidx]
            vertex.append(1.0)
            for idx in xrange(0, len(vertex) - 1):
                if abs(vertex[3]) > epsilon:
                    vertex[idx] /= vertex[3]
                result_vec = Matrix.mul(Vector(vertex), M)
            # result_vec is a Matrix type, so we need to convert it back to list of vertices            
            vcopy[vidx] = result_vec.getRow(0).getComponents()[:len(vertex) - 2]
        return vcopy
