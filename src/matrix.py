# 2009 - 2010 Boris Tatarintsev
# mailto: ttyv00@gmail.com

"""
Matrices module.
All the matrixes are represented as a list of lists, this way is
intuitively easy and also makes an implementation simple.

Contains methods for close integration with OpenGL.
"""

from vector     import *
from myexcept   import *

homogenousVec = [0.0, 0.0, 0.0, 1.0]

e1 = [1.0, 0.0, 0.0, 0.0]
e2 = [0.0, 1.0, 0.0, 0.0]
e3 = [0.0, 0.0, 1.0, 0.0]

epsilon = 1.0 / (10 ** 10)

INV_MINORS = 0
INV_GAUSS_JORDAN = 1

class Matrix:
    
    def __init__(self, inputArg = None):
        
        # construct matrix from input vectors
        # each vector represents a row of a matrix
        #
        #  scheme:
        #  [ vector1, vector2, vector3 ]
        #
        # rowVectors is a list of vectors
        
        self.__initMatrix(inputArg)

    def __initMatrix(self, inputArg):
        
        self.__matrix = []
        
        if(inputArg == None):
            # just create an empty matrix
            return(self)
                
        # looks ugly but this price we pay for types absence
        if(not isinstance(inputArg, Matrix)):
            if(isinstance(inputArg, Vector)):
                self.__matrix.append(inputArg.clone())
            elif(isinstance(inputArg, list)):
                for item in inputArg:
                    if(isinstance(item, Vector)):
                        # create from vectors
                        self.__matrix.append(item.clone())
                    elif(isinstance(item, list)):
                        # or from lists
                        self.__matrix.append(Vector(item))
        else:
            for vectorIdx in xrange(0, inputArg.rowsNum()):
                self.__matrix.append(inputArg.getRow(vectorIdx))
                
        return(self)
    
    def __getRawRepresentation(self):
        # this should be deprecated, but it's not for this moment )
        return(self.__matrix)
    
    def __getRow(self, rowIdx):
        # returns reference to matrix row, it's dangerous procedure
        # use it only to improve performace in some operations
        if(rowIdx < 0 or rowIdx >= self.rowsNum()):
            raise WrongIndexException()
        return self.__getRawRepresentation()[rowIdx]
    
    def __setRow(self, vectorRow, rowIdx):
        # updates the specified matrix row with the new one
        if(rowIdx < 0 or rowIdx >= self.rowsNum()):
            raise WrongIndexException()
        if(not isinstance(vectorRow, Vector)):
            raise WrongTypeException()
        self.__matrix[rowIdx] = vectorRow.clone()

    def __elementRelativeWeight(self, element, rowIdx):
        # calculates weight of an element relative to the row
        # with the index = rowIdx
        self.__getRow(rowIdx).getComponents()
        m = max(self.__getRow(rowIdx).getComponents())
        return 1.0 * element / m
                
    def getIdentityMatrix(self, size):
        # returns identity matrix of the given size
        tmp = Matrix()
        for j in xrange(0, size):
            row = [0.0] * size
            row[j] = 1.0
            tmp.appendRow(Vector(row))
        return(tmp)
    # make it static
    getIdentityMatrix = classmethod(getIdentityMatrix)       

    def buildFromOGL(self, oglform):
        # constructs matrix from OpenGL array        
        return Matrix([ oglform[:4], oglform[4:8], oglform[8:12], oglform[12:16] ]).transposeSelf()
    # make it static
    buildFromOGL = classmethod(buildFromOGL)    

    def clone(self):
        # makes a deep copy of matrix
        return(Matrix(self))
   
    def toString(self):
        # returns a string representation of the current matrix
        outStr = ""
        for row in self.__matrix:
            outStr += str(row.toString() + "\n")
        return(outStr)
    
    def rowsNum(self):
        return(len(self.__matrix))
    
    def colsNum(self):
        return(self.getRow(0).numComponents())
        
    def isQuadratic(self, M):
        # determines wether the current matrix is quadratic or not
        if(M.rowsNum() == M.colsNum()):
            return(True)
        return(False)
    # make it static
    isQuadratic = classmethod(isQuadratic) 
    
    def appendCol(self, vectorCol):
        # appends a col to a matrix
        if(not isinstance(vectorCol, Vector)):
            raise WrongTypeException()
        if(vectorCol.numComponents() != self.rowsNum()):
           raise SizeMismatchException()
        for idx in xrange(0, self.rowsNum()):
            # get reference to improve speed (dangerous though!)
            self.__getRow(idx).appendComponent(vectorCol.getComponent(idx))
    
    def appendRow(self, vectorRow):
        # appends a new row to a matrix
        if(not isinstance(vectorRow, Vector)):
            raise WrongTypeException()
        self.__matrix.append(vectorRow)
    
    def getRow(self, rowIdx):
        # returns vector-row
        if(rowIdx < 0 or rowIdx >= self.rowsNum()):
            raise WrongIndexException()
        # return cloned version of matrix's row to avoid implicit modification
        # straight modification of matrix rows should be avoided if possible
        return(self.__matrix[rowIdx].clone())
    
    def getCol(self, colIdx):
        # returns vector-col
        if(colIdx < 0 or colIdx >= self.colsNum()):
            raise WrongIndexException()
        vectorCol = []
        for vectorRow in self.__matrix:
            vectorCol.append(vectorRow.getComponent(colIdx))
        # return cloned version of matrix's column to avoid implicit modification
        # straight modification of matrix columns should be avoided if possible
        return(Vector(vectorCol))
    
    def appendElement(self, rowIdx, element):
        # appends new element to the selected row
        try:
            tmpRow = self.getRow(rowIdx)
            tmpRow.appendComponent(element)
            self.__setRow(tmpRow, rowIdx)
        except:
            raise
    
    def getElement(self, rowIdx, colIdx):
        # returns element located at rowIdx x colIdx
        try:
            return(self.getRow(rowIdx).getComponent(colIdx))
        except WrongIndexException:
            raise WrongIndexException()
        
    def setElement(self, rowIdx, colIdx, value):
        # sets the element at index rowIdx x colIdx
        try:
            self.__setRow(self.getRow(rowIdx).setComponent(colIdx, value), rowIdx)
        except:
            raise
        return(self)
        
    def insertRowBefore(self, rowIdx, rowVector):
        # inserts additional row into the matrix before the row denoted by rowIdx
        
        # check all the conditions )
        if(not isinstance(rowVector, Vector)):
            raise WrongTypeException()
        if(rowIdx < 0 or rowIdx >= self.rowsNum()):
            raise WrongIndexException()
        if(rowVector.numComponents() != self.colsNum()):
            raise SizeMismatchException()
        
        tmpArr = []
        for idx in xrange(0, self.rowsNum()):
            if(idx == rowIdx):
                tmpArr.append(rowVector)
            tmpArr.append(self.getRow(idx))
        self.__initMatrix(tmpArr)
        return(self)
    
    def insertColBefore(self, colIdx, colVector):
        # inserts an additional column into the matrix before the column denoted by rowIdx

        # check all the conditions )
        if(not isinstance(colVector, Vector)):
            raise WrongTypeException()
        if(colIdx < 0 or colIdx >= self.colsNum()):
            raise WrongIndexException()
        if(colVector.numComponents() != self.rowsNum()):
            raise SizeMismatchException()
        for curRow in xrange(0, self.rowsNum()):
            tmp = self.__getRow(curRow).getComponents()
            newRow = tmp[:colIdx] + [colVector.getComponent(curRow)] + tmp[colIdx:]
            self.__setRow(Vector(newRow), curRow)
        
    def getSubMatrix(self, rowIdx, colIdx):
        # returns submatrix for given rowIdx and colIdx
        tmpMatrix = []
        for curRow in xrange(0, self.rowsNum()):
            if(curRow == rowIdx):
                continue
            tmpRow = []
            for curCol in xrange(0, self.colsNum()):
                if(curCol == colIdx):
                    continue
                tmpRow.append(self.getElement(curRow, curCol))
            tmpMatrix.append(Vector(tmpRow))
        return(Matrix(tmpMatrix))
    
    def isCorrect(self):
        # verify consistency of the current matrix
        rowLen = -1
        for vectorRow in self.__matrix:
            if(rowLen == -1):
                rowLen = vectorRow.numComponents()
            else:
                if (rowLen != vectorRow.numComponents()):
                    return(False)
        return(True)
    
    def getSkewMatrix(self):
        # calculates the skew-martix from the given matrix
        tmpTransposed = self.transpose()
        # TODO: skew-matrix if needed
        pass
    
    def mulNum(self, inMatrix, number):
        # multiplies matrix by a number
        for rowVector in inMatrix.__getRawRepresentation():
            rowVector.mulNumSelf(number)
        # return the result
        return(inMatrix)
    # make it static
    mulNum = classmethod(mulNum)
    
    def mul(self, firstMatrix, secondMatrix):
        # matrixes multiplication
        
        # the quantity of cols in the first matrix must
        # be equal to the number of rows in the second one
        
        # it's also possible to multiply matrix by vector and vice versa
        # we done this by temporary converting vector to matrix
        if(isinstance(firstMatrix, Vector)):
            # convert vector into matrix
            firstMatrix = Matrix( [firstMatrix] )
        if(isinstance(secondMatrix, Vector)):
            # convert vector into matrix
            secondMatrix = Matrix ( [secondMatrix] )       
        tmpMatrix = []
        for rowIdx in xrange(0, firstMatrix.rowsNum()):
            vec1 = firstMatrix.getRow(rowIdx)
            
            tmpRow = [0] * secondMatrix.colsNum()
            for colIdx in xrange(0, secondMatrix.colsNum()):
                vec2 = secondMatrix.getCol(colIdx)
                result = vec1.dotProduct(vec2)
                tmpRow[colIdx] = result
            tmpMatrix.append(Vector(tmpRow))
        return(Matrix(tmpMatrix))
    # make it static
    mul = classmethod(mul)
    
    def add(self, firstMatrix, secondMatrix):
        # adds one matrix to another
        tmpMatrix = []
        for rowIdx in xrange(0, firstMatrix.rowsNum()):
            tmpRow = []
            for colIdx in xrange(0, firstMatrix.getRow(rowIdx).numComponents()):
                tmpRow.append(firstMatrix.getElement(rowIdx, colIdx) + secondMatrix.getElement(rowIdx, colIdx))
            tmpMatrix.append(Vector(tmpRow))     
        return(Matrix(tmpMatrix))
    # make it static
    add = classmethod(add)
    
    def substract(self, firstMatrix, secondMatrix):
        # substracts one matrix from another      
        # the trick is to multiply the secondMatrix by (-1) and add it to the first matrix
        negativeMatrix = Matrix.mulNum(secondMatrix, (-1))
        return(firstMatrix.addSelf(negativeMatrix))
    # make it static
    substract = classmethod(substract)   
    
    def substractSelf(self, secondMatrix):
        self.__initMatrix(Matrix.substract(firstMatrix, secondMatrix))
        return(self)
    
    def addSelf(self, secondMatrix):
        self.__initMatrix(Matrix.add(firstMatrix, secondMatrix))
        return(self)

    def toOGLform(self):
        # openGL treats matrices as arrays of length 16, where
        # each four numbers represent one column starting from the leftmost one.
        #tmp = Matrix.transpose(self)
        tmp = []
        for j in xrange(0, self.rowsNum()):
            tmp.extend((self.__getRow(j).getComponents()))
        return tmp
    
    def getUnionMatrix(self):
        # returns union matrix calculated from the given matrix
        if(not self.isQuadratic()):
            # we can get det for quadratic matrix only
            raise SizeMismatchException()
        tmpMatrix = [0] * self.rowsNum()
        for rowIdx in xrange(0, self.rowsNum()):
            tmpRow = [0] * self.colsNum()
            for colIdx in xrange(0, self.colsNum()):
                subMatrix = self.getSubMatrix(rowIdx, colIdx)
                algAdjunct = ((-1)**(rowIdx + colIdx + 2)) * self.det(subMatrix)
                tmpRow[colIdx] = algAdjunct
            tmpMatrix[rowIdx] = Vector(tmpRow)
        return(Matrix(tmpMatrix))
    
    def crossProduct3D(self, vector1, vector2):
        # optimized cross-product for 3d vectors
        x1, y1, z1 = vector1.getComponent(0), vector1.getComponent(1), vector1.getComponent(2)
        x2, y2, z2 = vector2.getComponent(0), vector2.getComponent(1), vector2.getComponent(2)
        return Vector([y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2])
    # make it static
    crossProduct3D = classmethod(crossProduct3D)
    
    def crossProduct(self, inputMatrix):
        # calculates the n-cross product
        # Input matrix must not be quadratic, for instance consider the following
        # set of orthogonal vectors:
        #
        #  v1 = ( a1, b1, c1, d1 )
        #  v2 = ( a2, b2, c2, d2 )
        #  v3 = ( a3, b3, c3, d3 )
        #
        # If one needs to find the vector (v4) perpendicular to all these 3 vectors
        # he has to create the matrix from these three vectors
        # it will be automatically extended to quadratic matrix to perform
        # the appropriate calculations.
        # In case of using quadratic matrix one must care to set the first row-vector
        # to (1, 1, 1 ,1, ..., 1) manually.

        # check the type
        if(not isinstance(inputMatrix, Matrix)):
            raise WrongTypeException()
        
        # check whether the input matrix is a quadratic matrix or not
        if(not Matrix.isQuadratic(inputMatrix)):
            # extend the input matrix to meet the requirement mentioned above
            vectorRow = Vector([1] * inputMatrix.colsNum())
            inputMatrix.insertRowBefore(0, vectorRow)
        
        # calculation process itself
        components = []
        for colIdx in xrange(0, inputMatrix.colsNum()):
            components.append((-1)**(colIdx + 2) * inputMatrix.det(inputMatrix.getSubMatrix(0, colIdx)))
        return(Vector(components))
    # make it static
    crossProduct = classmethod(crossProduct)
    
    def invert(self):
        # constructs invert matrix for the current matrix
        # algorithm description:
        #
        # 1. find the union matrix for the given matrix
        # 2. transpose union matrix
        # 3. get the invert matrix by using next formula:
        #   A^(-1) = 1/det(A) * (transpose(C))
        #   where A^(-1)        - inverse matrix
        #         det(A)        - determinant of the given matrix
        #         transpose(C)  - transposed union matrix
        
        # check if it's possible to compute the invert matrix
        det = self.det()
        if(abs(det) <= abs(epsilon)):
            raise InvertedUndetermined()
        return(Matrix.mulNum((self.getUnionMatrix()).transposeSelf(), (1.0 / det)))
    
    def invertGaussJordan(self):
        # compute inverse matrix by using Gauss-Jordan elimination
        # this should be faster than the previous one.
        # we have few steps to do:
        # 1. extend matrix to the form of A = [M:E]
        # 2. perform Gauss-Jordan on A
        # 3. fetch inverted matrix from A
        
        # step 1
        self.augmentSelf()
        
        # step 2
        for pivotIdx in xrange(0, self.rowsNum()):
            max = self.__elementRelativeWeight(self.getElement(pivotIdx, pivotIdx), pivotIdx)
            row = pivotIdx; newrow = row
            for j in xrange(pivotIdx, self.rowsNum()):
                # look if we can find any row below with bigger pivot element
                tmp = self.__elementRelativeWeight(self.getElement(j, pivotIdx), j)
                if tmp > max:
                    max, newrow = tmp, j
            # swap rows if needed
            if newrow != row:                
                tmp = self.getRow(row)
                self.__setRow(self.getRow(newrow), row)
                self.__setRow(tmp, newrow)
            # check singularity
            if self.getElement(pivotIdx, pivotIdx) <= epsilon:
                raise InvertedUndetermined()
            # now the most interesting part of the algorithm
            tmpRow = self.getRow(pivotIdx)
            tmpRow.mulNumSelf(1.0 / tmpRow.getComponent(pivotIdx))
            self.__setRow(tmpRow, pivotIdx)
            # eliminate current column
            for rowIdx in xrange(0, self.rowsNum()):
                if rowIdx != pivotIdx:
                    r = self.getRow(rowIdx)
                    t = tmpRow.clone()
                    t.mulNumSelf(r.getComponent(pivotIdx))
                    self.__setRow(r.subVec(t), rowIdx)
            
        # step 3
        c = self.colsNum() / 2
        for row in xrange(0, self.rowsNum()):
            self.__getRow(row).removeFirstNSelf(c)
                
    def invertSelf(self , invMethod = INV_GAUSS_JORDAN):
        if invMethod == INV_GAUSS_JORDAN:
            self.invertGaussJordan()
        else:
            self.__initMatrix(self.invert())
        return(self)
    
    def det(self, inMatrix = None):
        # calculates the determinant of the current matrix
        # recursive algorithm
        
        if(inMatrix == None):
            inMatrix = self
            
        if(not Matrix.isQuadratic(inMatrix)):
            # we can get det for quadratic matrix only
            raise SizeMismatchException()
        
        # for 3x3 matrix we can instantly get the determinant by well-known formula
        if(inMatrix.rowsNum() == 3):
            det = inMatrix.getElement(0, 0) * inMatrix.getElement(1, 1) * inMatrix.getElement(2, 2) + \
            inMatrix.getElement(0, 1) * inMatrix.getElement(1, 2) * inMatrix.getElement(2, 0) + \
            inMatrix.getElement(0, 2) * inMatrix.getElement(1, 0) * inMatrix.getElement(2, 1) - \
            inMatrix.getElement(0, 2) * inMatrix.getElement(1, 1) * inMatrix.getElement(2, 0) - \
            inMatrix.getElement(0, 0) * inMatrix.getElement(1, 2) * inMatrix.getElement(2, 1) - \
            inMatrix.getElement(0, 1) * inMatrix.getElement(1, 0) * inMatrix.getElement(2, 2)
            return(det)
        
        # for other cases to all the calculation needed
        det = 0
        if(inMatrix.rowsNum() == 2):
            # if we have 2x2 matrix we can get the det for it by using the well known formula
            subDet = inMatrix.getElement(0,0) * inMatrix.getElement(1,1) - inMatrix.getElement(0,1) * inMatrix.getElement(1,0)
            return(subDet)        
        for colIdx in xrange(0, inMatrix.colsNum()):
                subMatrix = inMatrix.getSubMatrix(0, colIdx)
                res = ((-1)**(2 + colIdx)) * inMatrix.getElement(0, colIdx) * self.det(subMatrix)
                det += res
        return(det)
    
    def transpose(self, inMatrix):
        # check if it's ok
        if(inMatrix == None):
            raise NullPointerException()
        
        # there are special cases for quadratic and non-quadratic matrix
        if(Matrix.isQuadratic(inMatrix)):
            auxMatrix = Matrix(inMatrix)
            # in case of quadratic matrix
            for row in xrange(0, auxMatrix.rowsNum()):
                for col in xrange(row + 1, auxMatrix.colsNum()):
                    tmpElement = auxMatrix.getElement(col, row)
                    auxMatrix.setElement(col, row, auxMatrix.getElement(row, col))
                    auxMatrix.setElement(row, col, tmpElement)
            return(auxMatrix)
        else:
            # other cases
            tmpMatrix = []
            for colIdx in xrange(0, inMatrix.colsNum()):
                tmpArr = []
                for row in inMatrix.__getRawRepresentation():
                    tmpArr.append(row.getComponent(colIdx))
                tmpMatrix.append(Vector(tmpArr))
            return(Matrix(tmpMatrix))
    # make it static
    transpose = classmethod(transpose)

    def transposeSelf(self):
        # saves the result matrix instead of the current matrix
        self.__initMatrix(self.transpose(self))
        return(self)

    def getAugmentedMatrix(self, matrix):
        # returns an augmented matrix constructed from the given one
        matrix.clone().augmentSelf()    
    # make it static
    getAugmentedMatrix = classmethod(getAugmentedMatrix)
    
    def augmentSelf(self):
        # extends self matrix to be augmented
        # be careful as this method doesn't check whether matrix is augmented already!
        colsNum = self.colsNum()
        for j in xrange(0, self.rowsNum()):
            self.__getRow(j).appendComponents([float(x == j) for x in xrange(0, colsNum)])
        return self
