# 2010 Boris Tatarintsev
# mailto: ttyv00@gmail.com

import random

from matrix import *
from vector import *

# simple unit tests class
class UnitTests:
    
    def __init__(self):
        pass
    
    def generateRandomVectors(self, dimension):
        # generates N random N-vectors, where N is equal dimension
        v_list = [ ([0] * dimension) for j in xrange(0, dimension) ]        
        for vector in v_list:
            for idx in xrange(0, len(vector)):
                vector[idx] = int(random.random() * 10)
        return v_list

    def crossProductsCheck3D(self, vectors):
        # check cross-product correctness using simple
        # formula for 3D and using common algorithm
        r1 = Matrix.crossProduct3D(Vector(vectors[0]), Vector(vectors[1]))
        r2 = Matrix.crossProduct(Matrix([Vector(vectors[0]), Vector(vectors[1])]))
        if r1 != r2:
            print "Incorrect!"
            print "r1 (simple cross3D):", r1.toString()
            print "r2 (common algorithm):", r2.toString()
        else:
            print "Correct!"
            print "r1 (simple cross3D):", r1.toString()
            print "r2 (common algorithm):", r2.toString()
            
        