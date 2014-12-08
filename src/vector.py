# 2009 Boris Tatarintsev
# mailto: ttyv00@gmail.com


"""
Math vectors implementation
"""

import math

from exceptions import *

epsilon = 1.0 / (10 ** 10)

class Vector:

	def __init__(self, components = None):
		self.__initVector(components)

	def __initVector(self, components = None):
		if(components != None):
			self.__components = components[0:]
		else:
			self.__components = []
			
		self.__old_components = []
		self.__last_normalized = []
	
	def __eq__(self, b):
		return self.isEqual(b)
	
	def __ne__(self, b):
		return not self.isEqual(b)
	
	def __sub__(self, b):
		return self.subVec(b)
		
	def toString(self):
		outStr = ""
		if(self.getComponents() != None):
			outStr = str(self.getComponents())
		return(outStr)

	def initFromVec(self, vec2):
		# initializes current vector with another
		if(not isinstance(vec2, Vector)):
			raise WrongTypeException()
		if(self.numComponents() != vec2.numComponents()):
			raise SizeMismatchException()
		for idx in xrange(0, vec2.numComponents()):
			self.setComponent(idx, vec2.getComponent(idx))

	def isEqual(self, b):
		if self.numComponents() != b.numComponents():
			return False
		for idx in xrange(0, self.numComponents()):
			if abs(self.getComponent(idx) - b.getComponent(idx)) > epsilon:
				return False
		return True

	def numComponents(self):
		return(len(self.getComponents()))

	def getComponent(self, idx):
		if(idx < 0 or idx >= self.numComponents()):
			raise WrongIndexException()
		return(self.__components[idx])
	
	def removeFirstNSelf(self, N):
		# remove first N components from vector
		self.__initVector(self.__components[N:])
		return self
	
	def appendComponent(self, value):
		self.__components.append(value)

	def appendComponents(self, values):
		self.__components.extend(values)
		
	def insertHead(self, value):
		# inserts a component into the beginning of a vector
		self.__components.insert(0, value)
	
	def setComponent(self, idx, value):
		if(idx < 0 or idx >= self.numComponents()):
			raise WrongIndexException()
		self.__components[idx] = value
		return(self)

	def getComponents(self):
		# returns copy of vector components
		return(self.__components[:])
		
	def cutLastComponent(self):
		# deletes the last component of the vector and returns a result
		return(Vector(self.__components[:self.numComponents()-1]))
	
	def cutLastComponentSelf(self):
		# deletes the last component of the vector itself
		self.__initVector(Vector(self.__components[:self.numComponents()-1]).getComponents())

	def clone(self):
		# returns an independent copy of the current vector
		return(Vector(self.__components))

	def inv(self):
		return Vector(map(lambda x: -x, self.getComponents()))

	def length(self):
		# calculate the length of the vector

		# check wether the vector has at least 1 component
		if(self.numComponents() <= 0):
			raise SizeMismatchException()
		# the length is 1 then return the first component itself
		elif(self.numComponents() == 1):
			return(self.getComponent(0))

		# lazy calculations model
		if(self.__old_components != self.getComponents()):
			self.__old_components = self.getComponents()
		else:
			return(self.last_length)

		sum = 0
		for item in self.getComponents():
			sum += (item * item)

		self.last_length = math.sqrt(sum)
		return(self.last_length)

	def getDistance(self, vec1, vec2):
		# returns the distance between two points represented as vectors
		# vec1 and vec2
		if(vec1.numComponents() != vec2.numComponents()):
			raise SizeMismatchException()
		sum = 0
		for idx in xrange(0, vec1.numComponents()):
			sum += math.fabs(vec1.getComponent(idx) - vec2.getComponent(idx))
		# warning: we dont calculate the square root for the optimization
		# purposes. It must be done outside if needed
		return(sum)
	# make it static
	getDistance = classmethod(getDistance)

	def normalizeSelf(self):
		self.__initVector(self.normalize().getComponents())
		return self

	def normalize(self):
		# vector normalization
		
		# check wether the vector has at least 1 component
		if(self.numComponents() <= 0):
			# negative value indicates that there is something wrong with out vector
			raise SizeMismatchException()

		# lazy calculations model
		if(self.__old_components != self.getComponents()):
			tmp_len = self.length()
		else:
			if(len(self.__last_normalized) != 0):		# check the logic
				return(Vector(self.__last_normalized))

		self.__last_normalized = self.getComponents()
		
        # normalization 
		if tmp_len != 0.0:
			for idx in xrange(0, self.numComponents()):
				self.__last_normalized[idx] = self.__last_normalized[idx] / tmp_len

		return(Vector(self.__last_normalized))

	def dotProduct(self, secondVector):
		# calculates dot product of two vectors
		
		# check consistency
		if(self.numComponents() != secondVector.numComponents()):
			raise SizeMismatchException()
		
		result = 0
		for idx in xrange(0, self.numComponents()):
			result += self.getComponent(idx) * secondVector.getComponent(idx)

		return(result)

	def addVec(self, secondAdditiveVec):
		# adds one vector to another one

		# both vectors MUST have the same length
		if(self.numComponents() != secondAdditiveVec.numComponents()):
			raise SizeMismatchException()
		product = []
		for idx in xrange(0, self.numComponents()):
			product.append(self.getComponent(idx) + secondAdditiveVec.getComponent(idx))
		return(Vector(product))
	
	def subVec(self, vectorToSubstract):
		# substracts one vector from another one
		
		# both vectors MUST have the same length
		if(self.numComponents() != vectorToSubstract.numComponents()):
				raise SizeMismatchException()
		product = []
		for idx in xrange(0, self.numComponents()):
			product.append(self.getComponent(idx) - vectorToSubstract.getComponent(idx))
		return(Vector(product))
		
	def addVecSelf(self, secondAdditiveVec):
		# adds one vector to another and saves the result in the current vector
		self.__initVector(self.addVec(secondAdditiveVec).getComponents())
		return(self)

	def mulNum(self, multiplier):
		# multiplies the vector by a given number
		if(self.numComponents() <= 0):
			raise SizeMismatchException()
		product = [0] * self.numComponents()
		idx = 0
		for item in self.getComponents():
			product[idx] = (item * multiplier)
			idx += 1
		return(product)
	
	def mulNumSelf(self, multiplier):
		# multiplies the vector by a number and saves the result in the current vector
		self.__initVector(self.mulNum(multiplier))
		return(self)
