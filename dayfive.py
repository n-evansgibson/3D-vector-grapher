from cmu_graphics import * 
import numpy as np
import math
import copy

class Point2D:

    def __init__(self, label, x, y):
        self.label = label
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point {self.label} is at ({self.x}, {self.y})'
    
    def __eq__(self, other):
        return isinstance(other, Point2D) and self.label == other.label
    
def onAppStart(app):

    # define points for axes
    app.axisSize = 4
    app.axesPoints = [
        np.array([app.axisSize, 0, 0]),
        np.array([-app.axisSize, 0, 0]),
        # y axis
        np.array([0, app.axisSize, 0]),
        np.array([0, -app.axisSize, 0]),
        # z axis
        np.array([0, 0, app.axisSize]),
        np.array([0, 0, -app.axisSize]),
    ]

    app.originalAxesPoints = [copy.deepcopy(point) for  point in app.axesPoints]

    # defines points for xy grid
    app.gridSize = app.axisSize
    app.gridPoints = []
    makeGrid(app)

    app.originalGridPoints = [copy.deepcopy(point) for point in app.gridPoints]
    
    # angle of axes rotation
    app.viewerAngle = math.pi/4

    # points of cube
    app.cubePoints = [
    np.array([-1, -1, 1]),
    np.array([1, -1, 1]),
    np.array([1, 1, 1]),
    np.array([-1, 1, 1]),
    np.array([-1, -1, -1]),
    np.array([1, -1, -1]),
    np.array([1, 1, -1]),
    np.array([-1, 1, -1])
    ]

    app.originalCubePoints = [copy.copy(point) for point in app.cubePoints]

    # projection matrix and projected points: these points are stored as a Point2D class
    app.projectionMatrix = np.array([[0, 1, 0], [0, 0, 1]])
    app.projectedPoints = [None for _ in range(len(app.cubePoints))]
    app.pointRad = 5

    # cube lines
    app.lines = [
        (0, 1),
        (0, 3),
        (0, 4),
        (1, 5),
        (2, 1), 
        (2, 3),
        (2, 6),
        (3, 7),
        (4, 5), 
        (4, 7),
        (6, 5),
        (6, 7)
    ]

    # cube faces
    app.faces = [
        (0, 1, 2, 3), 
        (4, 5, 6, 7),
        (0, 3, 7, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (0, 1, 5, 4)
    ]

    # scales whole cube
    app.scale = 100
    app.circlePos = [app.height/2, app.width/2]

    # cube rotation
    app.rX = 0
    app.rY = 0
    app.rZ = 0
    app.rSpeed = 0.02
    app.viewerAngleZ = app.viewerAngleY = math.pi/8

    # basic controls
    app.paused = True

def makeGrid(app):
    app.gridPoints = []
    for i in range(app.axisSize):
        # makes x gridline in positive dir
        newY = (i + 1) * app.axisSize / app.axisSize
        newStartPoint  = np.array([app.gridSize, newY, 0])
        newEndPoint = np.array([-app.gridSize, newY, 0])
        app.gridPoints.append(newStartPoint)
        app.gridPoints.append(newEndPoint)
        # makes x gridline in opposite dir
        oppositeY = -newY
        oppStartPoint = np.array([app.gridSize, oppositeY, 0])
        oppEndPoint = np.array([-app.gridSize, oppositeY, 0])
        app.gridPoints.append(oppStartPoint)
        app.gridPoints.append(oppEndPoint)
    # y grid
    for i in range(app.axisSize):
        # makes y gridline in positive dir
        newX = (i + 1) * app.axisSize / app.axisSize
        newStartPoint = np.array([newX, app.gridSize, 0])
        newEndPoint = np.array([newX, -app.gridSize, 0])
        app.gridPoints.append(newStartPoint)
        app.gridPoints.append(newEndPoint)
        # makes y gridline in opposite dir
        oppositeX = -newX
        oppStartPoint = np.array([oppositeX, app.gridSize, 0])
        oppEndPoint = np.array([oppositeX, -app.gridSize, 0])
        app.gridPoints.append(oppStartPoint)
        app.gridPoints.append(oppEndPoint)

def onStep(app):
    # axis rotation
    app.axesPoints = [copy.copy(point) for point in app.originalAxesPoints]
    app.gridPoints = [copy.copy(point) for point in app.originalGridPoints]
    app.cubePoints = [copy.copy(point) for point in app.originalCubePoints]

    axisRotMatrixZ = np.array([
        [math.cos(app.viewerAngleZ), -math.sin(app.viewerAngleZ), 0],
        [math.sin(app.viewerAngleZ), math.cos(app.viewerAngleZ), 0],
        [0, 0, 1]
    ])
    axisRotMatrixY = np.array([
        [math.cos(app.viewerAngleY), 0, math.sin(app.viewerAngleY)],
        [0, 1, 0],
        [-math.sin(app.viewerAngleY), 0, math.cos(app.viewerAngleY)]

    ])
    rotatePoints(app.axesPoints, axisRotMatrixZ)
    rotatePoints(app.axesPoints, axisRotMatrixY)
    rotatePoints(app.gridPoints, axisRotMatrixZ)
    rotatePoints(app.gridPoints, axisRotMatrixY)
    rotatePoints(app.cubePoints, axisRotMatrixZ)
    rotatePoints(app.cubePoints, axisRotMatrixY)

    # rotates cube if unpaused
    if not app.paused:
        takeStep(app)
                 
def takeStep(app):

    # rotate cube x
    app.rX += app.rSpeed
    app.rY += app.rSpeed
    app.rZ += app.rSpeed

    xMatrix = np.array([
        [1, 0, 0],
        [0, math.cos(app.rX), -math.sin(app.rX)],
        [0, math.sin(app.rX), math.cos(app.rX)]
    ])    
    # rotate y
    yMatrix = np.array([
        [math.cos(app.rY), 0, math.sin(app.rY)],
        [0, 1, 0],
        [-math.sin(app.rY), 0, math.cos(app.rY)]
    ])    
    # rotate z
    zMatrix = np.array([
        [math.cos(app.rZ), -math.sin(app.rZ), 0],
        [math.sin(app.rZ), math.cos(app.rZ), 0],
        [0, 0, 1]
    ])

    # applies rotation to cube points
    rotatePoints(app.cubePoints, xMatrix)
    rotatePoints(app.cubePoints, yMatrix)
    rotatePoints(app.cubePoints, zMatrix)

# applies rotation matrix to points (x, y or z)
def rotatePoints(pointList, matrix):
    for i in range(len(pointList)):
        point = pointList[i].reshape((3,1))
        rotatedPoint = np.dot(matrix, point)
        pointList[i] = rotatedPoint.flatten()

def drawLines(app, pointList):
        
        if pointList == app.axesPoints:
            color = 'navy'
            thicc = 2
            arrows = True
        else:
            color = 'grey'
            thicc = 1
            arrows = False
        
        for i in range(0, len(pointList), 2):

            # find projection of start and end points
            startPoint = pointList[i].reshape((3,1))
            endPoint = pointList[i + 1].reshape((3,1))
            projStart = np.dot(app.projectionMatrix, startPoint)
            projEnd = np.dot(app.projectionMatrix, endPoint)

            # get coordinates from projection
            x1 = int(projStart[0] * app.scale) + app.circlePos[0]
            y1 = int(projStart[1] * app.scale) + app.circlePos[1]
            x2 = int(projEnd[0] * app.scale) + app.circlePos[0]
            y2 = int(projEnd[1] * app.scale) + app.circlePos[1]

            # draws primary axis
            drawLine(x1, y1, x2, y2, fill = color, lineWidth = thicc, arrowStart = arrows, arrowEnd = arrows)

def redrawAll(app):

    # converts 3D cube points into 2D point classes
    for i in range(len(app.cubePoints)):
        point = app.cubePoints[i]

        # actual matrix multiplication
        rotatedPoint = point.reshape((3,1))
        projectedPoint = np.dot(app.projectionMatrix, rotatedPoint)

        # get coordinates from projection
        x = int(projectedPoint[0] * app.scale) + app.circlePos[0]
        y = int(projectedPoint[1] * app.scale) + app.circlePos[1]

        # add point to list
        app.projectedPoints[i] = Point2D(i, x, y)



    # draw each face
    for a, b, c, d in app.faces:
        xA, yA = app.projectedPoints[a].x, app.projectedPoints[a].y
        xB, yB = app.projectedPoints[b].x, app.projectedPoints[b].y
        xC, yC = app.projectedPoints[c].x, app.projectedPoints[c].y
        xD, yD = app.projectedPoints[d].x, app.projectedPoints[d].y
        drawPolygon(xA, yA, xB, yB, xC, yC, xD, yD, fill = 'grey')
 
    drawLines(app, app.axesPoints)
    drawLines(app, app.gridPoints)

    # draws each line
    for i, j in app.lines:
        # gets points to make line
        x1, y1 = app.projectedPoints[i].x, app.projectedPoints[i].y
        x2, y2 = app.projectedPoints[j].x, app.projectedPoints[j].y
        # draws line
        drawLine(x1, y1, x2, y2)

    # draws each point
    for point in app.projectedPoints:
        drawCircle(point.x, point.y, app.pointRad, fill = 'black')

    # labels
    drawLabel('kill me cube', app.width/2, app.height/20, size = 16)
    drawLabel('press p to pause, up/down arrows to change rotation speed', app.width/2, app.height/20 + 20, size = 12)
    drawLabel('left/right arrows to change view', app.width/2, app.height/20 + 30, size = 12)
    drawLabel(f'cube speed: {app.rSpeed}', app.width/2, app.height - 20, size = 12)

def onKeyPress(app, key):
    # pause button
    if key == 'p':
        app.paused = not app.paused
    
def onKeyHold(app, keys):
    # cube speed controls
    if 'up' in keys:
        app.rSpeed += 0.005
    if 'down' in keys:
        app.rSpeed -= 0.005
    
    # rotate viewer angle
    if 'left' in keys:
        app.viewerAngleZ -= math.pi/36
    if 'right' in keys: 
        app.viewerAngleZ += math.pi/36
    
def onMouseDrag(app, mouseX, mouseY):
    xMin = yMin = app.scale
    xMax = app.width - app.scale
    yMax = app.height - app.scale
    if xMin <= mouseX <= xMax:
        app.circlePos[0] = mouseX
    if yMin <= mouseY <= yMax:
        app.circlePos[1] = mouseY


def main():
    runApp(width = 800, height = 800)

main()

# Sources:
#   https://www.youtube.com/watch?v=qw0oY6Ld-L0 (referenced to initialize points and use numpy with matrices)
#   https://en.wikipedia.org/wiki/Rotation_matrix (got x, y, and z rotation matrices from here)
#   chatGPT used to debug problem with rotation matrices compounding on one another, causing excess rot speed
