# 2010 Boris Tatarintsev
# mailto: ttyv00@gmail.com

from vector     import *
from matrix     import *
from utils3d    import *

class Camera3D:
    
    def __init__(self, position, up, direction):
        # position    - location vector of a camera
        # up          - up vector of a camera
        # direction   - direction vector of a camera        
        self.v = Matrix.crossProduct3D(up, direction)        
        self.up = up
        self.direction = direction
        self.position = position
        # homogenous coords
        self.v.appendComponent(0)
        self.up.appendComponent(0)
        self.direction.appendComponent(0)
        self.position.appendComponent(1)
        # create camera matrix
        self.camMat = Matrix()
        self.camMat.appendRow(self.v)
        self.camMat.appendRow(self.up)
        self.camMat.appendRow(self.direction)
        self.camMat.appendRow(self.position)
        # transpose matrix (for OpenGL)
        self.camMat.transposeSelf()
        # compute transform matrix
        (self.plain, self.ogl) = self.compute()
        # this is a 3D camera
        self.cameraDim = 3
    
    def getCameraDim(self):
        return self.cameraDim
    
    def setupProjectionMatrix(self, projMat):
        self.projMat = projMat        

    def getCameraBasis(self):
        e1  = self.camMat.getCol(0).getComponents()
        e2  = self.camMat.getCol(1).getComponents()
        e3  = self.camMat.getCol(2).getComponents()
        pos = self.camMat.getCol(3).getComponents()
        return([e1, e2, e3, pos])

    def getCameraTransformation(self):
        # returns transformation matrix for the current camera
        return self.plain
    
    def getOGLCameraTransformation(self):
        # returns transformation matrix for the camera in OpenGL form        
        return self.ogl
        
    def compute(self):
        # compute camera transformation
        basis = self.getCameraBasis()        
        return (Matrix([basis[0], basis[1], basis[2], basis[3]]).invertSelf(), Matrix([basis[0], basis[1], basis[2], basis[3]]).invertSelf().toOGLform())

    def applyProjectionMatrix(self, vertices):
        if self.projMat == None:
            return vertices
        
