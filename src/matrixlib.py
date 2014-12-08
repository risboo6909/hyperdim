from vector     import *
from matrix     import *
from math       import *   

def getRotXY_4D(angle):
    return Matrix([[cos(angle), sin(angle), 0, 0], [-sin(angle), cos(angle), 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]])

def getRotYZ_4D(angle):
    return Matrix([[1.0, 0, 0, 0], [0, cos(angle), sin(angle), 0], [0, -sin(angle), cos(angle), 0], [0, 0, 0, 1.0]])

def getRotXZ_4D(angle):
    return Matrix([[cos(angle), 0, -sin(angle), 0], [0, 1.0, 0, 0], [sin(angle), 0, cos(angle), 0], [0, 0, 0, 1.0]])

def getRotXU_4D(angle):
    return Matrix([[cos(angle), 0, 0, sin(angle)], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [-sin(angle), 0, 0, cos(angle)]])

def getRotYU_4D(angle):
    return Matrix([[1.0, 0, 0, 0], [0, cos(angle), 0, -sin(angle)], [0, 0, 1.0, 0], [0, sin(angle), 0, cos(angle)]])

def getRotZU_4D(angle):
    return Matrix([[1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, cos(angle), -sin(angle)], [0, 0, sin(angle), cos(angle)]])
