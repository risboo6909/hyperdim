# @Boris Tatarintsev
# mailto: ttyv00@gmail.com

import sys
sys.path += ['.']

from ctypes import util
try:
    from OpenGL.platform import win32
except AttributeError:
    pass

# standart Python libraries
import time
import sys
import math
import copy

# extern libraries
from OpenGL     import GL, GLU, GLUT
from OpenGL.GL.shaders import *
from myexcept   import *
from matrix     import *
from vector     import *
from camera3d	import *
from camera4d	import *
from quaternion import *
from tools      import *
from utils3d    import *
from utests     import *
from geometry 	import *
from matrixlib  import *

RENDER_MODE_1, RENDER_MODE_2 = 0, 1

renderingMode = RENDER_MODE_1
camerasStack = {}					# each camera has its own position in space and also projection matrix
sceneObjects = {}					# contains all the objects on the scene

negZ = Vector([0.0, 0.0, -1.0])
posZ = Vector([0.0, 0.0, 1.0])

shaders = []

def initGL(width, height):
	# setup clear color
	GL.glClearColor(0.0, 0.0, 0.0, 0.0)
	# init depth buffer
	GL.glClearDepth(1.0)
	GL.glDepthFunc(GL.GL_LESS)
	GL.glEnable(GL.GL_DEPTH_TEST)
	# enable lighting
	GL.glEnable(GL.GL_LIGHTING)
	# enable light 0
	GL.glEnable(GL.GL_LIGHT0)
	# enable materials
	GL.glEnable(GL.GL_COLOR_MATERIAL)
	# projection matrix
	GL.glMatrixMode(GL.GL_PROJECTION)	
	GL.glLoadIdentity()    
	aspectRatio = float(width) / float(height)
	GLU.gluPerspective(45.0, aspectRatio, 0.1, 50.0)	
	# matrix mode
	GL.glMatrixMode(GL.GL_MODELVIEW)
	GL.ERROR_CHECKING = False	
	# setup shaders
	shaders.append(compileProgram(
	        compileShader('''
	            varying vec3 normal;
	            void main() {
	                normal = gl_NormalMatrix * gl_Normal;
	                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	            }
	        ''',GL.GL_VERTEX_SHADER),
	        compileShader('''
	            varying vec3 normal;
	            void main() {
	                float intensity;
	                vec4 color;
	                vec3 n = normalize(normal);
	                vec3 l = normalize(gl_LightSource[0].position).xyz;
	            
	                // quantize to 5 steps (0, .25, .5, .75 and 1)
	                intensity = (floor(dot(l, n) * 2.0) + 1.0)/4.0;
	                color = vec4(intensity*1.0, intensity*1.5, intensity*0.5,
	                    intensity*1.0);
	            
	                gl_FragColor = color;
	            }
	    ''',GL.GL_FRAGMENT_SHADER),))	

def initGLWindow(width, height):
	# init GL window
	GLUT.glutInit(sys.argv)
	GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_ALPHA | GLUT.GLUT_DEPTH)
	GLUT.glutInitWindowSize(width, height)
	GLUT.glutInitWindowPosition(0, 0)
	GLUT.glutCreateWindow("Hyper Dimensions v1.0 (beta)")
	# set callback functions
	GLUT.glutDisplayFunc(drawGLScene)	# rendering function
	GLUT.glutIdleFunc(drawGLScene)		# idle function
	GLUT.glutTimerFunc(10, updateScene, 1);
	GLUT.glutPassiveMotionFunc(mousePassiveMotion)

def addCameraToStack(camera):
	global camerasStack
	camerasStack[camera.getCameraDim()] = camera
	# he he ;]
	return addCameraToStack
	
def applyCameraTransform3D(cam):
	# applies camera transformation
	if cam != None:	
		transMat = cam.getOGLCameraTransformation()
		GL.glMultMatrixf(transMat)		

def iterateCameras3D():
	# apply 3D transform of each camera
	if camerasStack.has_key(3):		
		applyCameraTransform3D(camerasStack[3])

def applyCameraTransformD(cam):
	# camera transformation for D > 3D
	if cam != None:
		for object in sceneObjects.values():
			if object.getDim() > 3:
				cam.compute(object)

def iterateCamerasD():
	# iterate over > 3D cameras
	for key in camerasStack.keys():
		if key > 3:
			applyCameraTransformD(camerasStack[key])			
			
def projectFromHigherDimensions(object):
	# project vertices from the higher dimensions to 3D
	# we do this by iterating through the cameras and choosing
	# ones which can help us to project from the current dimensions (D) to 
	# the lower ones (D-1)
	if object.getDim() > 3:
		vData = object.getVertexTempData()
		for j in xrange(object.getDim(), 3, -1):
			vData = camerasStack[j].applyProjectionMatrix(vData)
		# we've got 3D data here :)
		object.setVertexData3D(vData)
				
def rotateInLocalBasis(object, anlgle1, angle2, angle3, e1 = None, e2 = None, e3 = None):
	vertexBuffer = object.getVertexData3D()
	centerOfMass = object.getCenterOfMass()
	if vertexBuffer != None:		
		# rotatees an object around its local center of coordinates
		for vertex in [ [key, vertexBuffer[key]] for key in vertexBuffer.keys() ]:
			# translate to the center
			translate(vertex[1], centerOfMass.getComponents(), True)
			# use quaternions for rotation
			ang_rad = math.radians(4)
			if e1 != None:
				vertex[1] = rotateH(vertex[1], ang_rad, e1)
			if e2 != None:
				vertex[1] = rotateH(vertex[1], ang_rad, e2)
			if e3 != None:
				vertex[1] = rotateH(vertex[1], ang_rad, e3)
			# translate back
			translate(vertex[1], centerOfMass.getComponents(), False)
			# copy
			vertexBuffer[vertex[0]] = vertex[1]
			
def rotateInLocalBasis4D(object):
	vertexBuffer = object.getVertexData()
	centerOfMass = object.getCenterOfMass()
	ang_rad = math.radians(1)
	if vertexBuffer != None:
		# create rotation matrix
		R1 = getRotXU_4D(ang_rad).transposeSelf()
		R2 = getRotZU_4D(ang_rad).transposeSelf()
		#R1 = getRotXY_4D(ang_rad).transposeSelf()
		#R2 = getRotYU_4D(ang_rad).transposeSelf()
		#R2 = Matrix.getIdentityMatrix(4)
		R3 = getRotYU_4D(ang_rad).transposeSelf()
		R = Matrix.mul(Matrix.mul(R1, R2), R3)
		#R = Matrix.getIdentityMatrix(4)
 	    # rotatees an object around its local center of coordinates
		for vertex in [ [key, vertexBuffer[key]] for key in vertexBuffer.keys() ]:
			# translate to the center
			translate(vertex[1], centerOfMass.getComponents(), True)
			# rotation matrix 4D			
			vertex[1] = Matrix.mul(Vector(vertex[1]), R).getRow(0).getComponents()
			# translate back
			translate(vertex[1], centerOfMass.getComponents(), False)
			# copy
			vertexBuffer[vertex[0]] = vertex[1]

def updateScene(value):	
	# rotate geometry
	ang_rad = math.radians(1)
	for object in sceneObjects.values():
		if object.getDim() == 3:
			# 3d rotation
			rotateInLocalBasis(object, ang_rad, ang_rad, ang_rad, e1, e2, e3)
		else:
			rotateInLocalBasis4D(object)
	GLUT.glutTimerFunc(20, updateScene, 1);

def mousePassiveMotion(x, y):	
	#if (GLUT.glutGetModifiers() & GLUT.GLUT_ACTIVE_ALT) == True:
	#print "Hello"
	pass

def renderString(x, y, font, s, rgb):
	GL.glViewport(0, 0, int(800), int(600))
	GL.glClearColor(0.0, 0.0, 0.0, 0.0)
	GL.glClear(GL.GL_COLOR_BUFFER_BIT)
	GL.glColor4f(1.0, 1.0, 0.5, 1.0)
	
	GL.glMatrixMode(GL.GL_PROJECTION)
	GL.glLoadIdentity()
	GL.glMatrixMode(GL.GL_MODELVIEW)
	GL.glLoadIdentity()
	GL.glTranslate(-1.0, 1.0, 0.0)
	scale = 1.0/800.0
	GL.glScale(scale, -scale*800.0/640.0, 1.0)
	GL.glTranslate(1.0, 1.0, 0.0)
	
	GL.glColor3f(rgb[0], rgb[1], rgb[2]); 	
	GL.glRasterPos(x, y)		
	for c in s:
		GLUT.glutBitmapCharacter(font, ord(c))


def drawGLScene():
	
	GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
	for object in sceneObjects.values():

		# apply camera transform for > 3 dimensions
		iterateCamerasD()
		
		# apply 3D camera transform
		iterateCamerasD()
		
		# first we need to project geometry from > 3 dimensions to 3D
		projectFromHigherDimensions(object)

		vertexBuffer = object.getVertexData3D()
		edgesData = object.getEdgesData()		
		
		#print "edges:", edgesData
		#print "vertex:", vertexBuffer
		
		if vertexBuffer != None:		
		
			if renderingMode == RENDER_MODE_1:
				# in this rendering mode we represent edges as
				# cylinders and vertices as spheres
				
				if len(vertexBuffer) == 0: return
				
				# draw vertices (spheres)
				quadObj1 = GLU.gluNewQuadric()
				GLU.gluQuadricDrawStyle(quadObj1, GLU.GLU_FILL)
				#GLU.gluQuadricDrawStyle(quadObj1, GL.GL_WIREFRAME)
				
				for vertex in vertexBuffer.values():
					GL.glLoadIdentity()
					iterateCameras3D()			
					GL.glTranslatef(vertex[0], vertex[1], vertex[2])		
					GLU.gluSphere(quadObj1, 0.1, 15, 15)

				# draw faces
				GL.glBegin(GL.GL_TRIANGLES)
				
				GL.glEnd()
				
				# draw edges (cylinders)
				# initially all the cylinders must points towards the positive z
				# direction
				quadObj2 = GLU.gluNewQuadric()
				GLU.gluQuadricDrawStyle(quadObj2, GLU.GLU_FILL)
				for edge in edgesData.values():
                    
					GL.glLoadIdentity()
					
					iterateCameras3D()			
                    
					#modelview = GL.glGetDouble(GL.GL_MODELVIEW_MATRIX)
					#print "before"
					#dumpOGLMatrix(modelview)
					
					# get 'from' and 'to' vectors for the edge
					x0, y0, z0 = vertexBuffer[int(edge[0])]
					x1, y1, z1 = vertexBuffer[int(edge[1])]
                   
					# position a cylinder
					GL.glTranslatef(x0, y0, z0)
					
					# calculate edge length
					length = math.sqrt( (x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2 )
					
					tmp = Vector([x1 - x0, y1 - y0, z1 - z0])	
                    
					# get the cross products
					if (negZ == tmp.inv().normalize()):
						axis1 = Vector([0,1.0,0])						
					else:
						axis1 = Matrix.crossProduct3D(negZ, tmp.normalize())
					axis2 = Matrix.crossProduct3D(negZ, axis1)				
					axis3 = posZ
                    
					# get the angle we need to rotate to
					cos_angle = posZ.dotProduct(tmp.normalize())
					angle = math.degrees(math.acos(cos_angle))
					
					# calculate the transformation
					axis1.normalizeSelf()
					axis2.normalizeSelf()
                    
					# we need an inverse matrix and we know that the transpose of the rotation matrix is equal to its inverse
					a1, a2, a3 = axis1.getComponents(), axis2.getComponents(), axis3.getComponents()
					v1 = [ a1[0], a2[0], a3[0], 0 ]
					v2 = [ a1[1], a2[1], a3[1], 0 ]
					v3 = [ a1[2], a2[2], a3[2], 0 ]							
					axis1, axis2, axis3 = v1, v2, v3
					
					# feed to openGL				
					rotTransform = createOGLMatrixFromLists(axis1, axis2, axis3)
					rotTransform.extend(homogenousVec)				
					GL.glMultMatrixf(rotTransform)
					
					# rotate a cylinder around axis1
					GL.glRotatef(angle, 1.0, 0.0, 0.0)
				
					# draw a cylinder
					GLU.gluCylinder(quadObj2, 0.05, 0.05, length, 12, 12)					
				
				GLU.gluDeleteQuadric(quadObj1)
				GLU.gluDeleteQuadric(quadObj2)
				
	GL.glUseProgram(shaders[0])
				
	#renderString(100, 100, GLUT.GLUT_BITMAP_8_BY_13, "Hello World", (1.0, 0.0, 0.0))
	
	GLUT.glutSwapBuffers()
	

print "Initializing openGL...",
initGLWindow(800, 600)
initGL(800, 600)
addCameraToStack(Camera3D(Vector([0,0,10.0]), Vector([0,1.0,0]), Vector([0,0,1.0])))
print "done!"
print "Reading geometry data...",
#loadModelFromFile("TETRA", "data/tetrahedron.dat", sceneObjects)
#loadModelFromFile("CUBE", "data\\cube.dat", sceneObjects)
loadModelFromFile("HCUBE", "data/hypercube.dat", sceneObjects)
print "done!"
print "Computing 4D stuff...",
# construct 4D camera
#cam4d = Camera4D(Vector([-0.5,-0.5,0,0]), Vector([0,1,0,0]), Vector([0,0,1,0]), Vector([0,0,0,1]))
cam4d = Camera4D(Vector([-0.5,-0.5,0,0]), Vector([0,1,0,0]), Vector([0,0,1,0]), Vector([0,0,0,1]))
projMat = cam4d.buildProjectionMatrix4D(-0.2, 0.2, -0.2, 0.2, -0.2, 0.2)
cam4d.setupProjectionMatrix(projMat)
addCameraToStack(cam4d)
print "done!"
print "Generating faces...",
#sceneObjects['CUBE'].generateFacesData()
print "done!"
#print sceneObjects['CUBE'].facesData;
GLUT.glutMainLoop()
