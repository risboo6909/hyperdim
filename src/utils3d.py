# 2010 Boris Tatarintsev
# mailto: ttyv00@gmail.com+

from matrix import Matrix
from vector import Vector

def getTransformToStandart(transform):
    # returns transformation from the given basis to the standart [1,0,0],[0,1,0],[0,0,1]
    e1, e2, e3 = Vector([1.0, 0.0, 0.0, 0.0]), Vector([0.0, 1.0, 0.0, 0.0]), Vector([0.0, 0.0, 1.0, 0.0])
    #print transform.toString()
    ne1, ne2, ne3 = transform.mul(e1, transform), transform.mul(e2, transform), transform.mul(e3, transform)
    return (Matrix([ne1, ne2, ne3, Vector(0.0, 0.0, 0.0, 0.1)])).transposeSelf()

def computeCenterOfMass(vertices):
    # calculates center of mass of geometry
    # we assume that the mass of each vertex is equals to 1
    # therefore the resulting formula will be:
    # sum(Ri/Mi) where i is in range of [0..number of vertices - 1] and it works
    # along all the axes
    centerVec = []
    for component in xrange(0, len(vertices[0])):
        tmp = 0.0
        for vector in vertices:
            tmp += vector[component]
        tmp /= 1.0 * len(vertices)
        centerVec.append(tmp)    
    return(Vector(centerVec))

def gramm(X):
    # Returns the Gramm-Schmidt orthogonalization of matrix X
    # taken from http://adorio-research.org

    # X must be a vector-column matrix

    k = X.colsNum()         # number of columns. 
    n = X.rowsNum()         # number of rows.
 
    for j in range(k):
       for i in range(j):
          D = sum([X.getElement(p, i) * X.getElement(p, j) for p in range(n)])
 
          for p in range(n):             
            X.setElement(p, j, X.getElement(p, j) - (D * X.getElement(p, i)))
 
       # Normalize column V[j]
       invnorm = 1.0 / X.getCol(j).length()
       for p in range(n):
           X.setElement(p, j, X.getElement(p, j) * invnorm)
        
    return X

def translate(vector, translation, invert):
    for component in xrange(0, len(vector)):
        if invert:
            vector[component] -= translation[component]
        else:
            vector[component] += translation[component]

def OGLRotationMatrix(basis):
    # returns OpenGL form of transformation matrix from one basis to another one
    tmp = basis.toOGLform()
    tmp.insert(3, 0.0)
    tmp.insert(6, 0.0)
    tmp.insert(9, 0.0)
    tmp.extend([0.0, 0.0, 0.0, 1.0])
    return tmp

def createOGLMatrixFromLists(*args):
    # flattern lists into one big list for OpenGL
    result = []
    for vector in args:
        result.extend(vector)
    return result

def dumpOGLMatrix(matrix):
    # converts OpenGL matrix into human-readable form
    for row in xrange(0, 4):
        for col in xrange(0, 4):
            print matrix[col][row],
        print "\n"
