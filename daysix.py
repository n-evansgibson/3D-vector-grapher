from cmu_graphics import * 
from axesInit import (makeGrid, axesPoints, cubePoints, cubeLines, cubeFaces,
boxPoints, boxLines)
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

    # defines points and lines for box
    app.boxPoints = boxPoints
    app.boxLines = boxLines
    app.originalBoxPoints = [copy.deepcopy(point) for point in app.boxPoints]
    app.projectedBoxPoints = [None for _ in range(len(app.boxPoints))]

    # define points for axes
    app.axisSize = 4
    app.axesPoints = axesPoints
    app.originalAxesPoints = [copy.deepcopy(point) for  point in app.axesPoints]

    # defines points for xy grid
    app.gridSize = 1     # Number of grid divisions in each direction
    app.gridPoints = []
    makeGrid(app)
    app.originalGridPoints = [copy.deepcopy(point) for point in app.gridPoints]
    
    # angle of axes rotation
    app.viewerAngle = math.pi/4

    # points of cube
    app.cubePoints = cubePoints

    app.originalCubePoints = [copy.copy(point) for point in app.cubePoints]

    # projection matrix and projected points: these points are stored as a Point2D class
    app.projectionMatrix = np.array([[0, 1, 0], [0, 0, -1]])
    app.projectedCubePoints = [None for _ in range(len(app.cubePoints))]
    app.pointRad = 5

    # cube lines and faces
    app.lines = cubeLines
    app.faces = cubeFaces

    # scales axes and cube
    app.scale = 60
    app.centerPos = [11*app.width/16, app.height/2]

    # cube rotation
    app.rX = 0
    app.rY = 0
    app.rZ = 0
    app.rSpeed = 0.02
    app.viewerAngleZ = app.viewerAngleY = math.pi/8

    # basic controls
    app.paused = True

def onStep(app):
     
    # axis rotation
    app.boxPoints = [copy.copy(point) for point in app.originalBoxPoints]
    app.axesPoints = [copy.copy(point) for point in app.originalAxesPoints]
    app.gridPoints = [copy.copy(point) for point in app.originalGridPoints]
    app.cubePoints = [copy.copy(point) for point in app.originalCubePoints]

    # updates grid
    makeGrid(app)

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

    bigRotMatrix = np.dot(axisRotMatrixY, axisRotMatrixZ)
    
    # rotates axis, grid, and cube
    rotatePoints(app.boxPoints, bigRotMatrix)
    rotatePoints(app.axesPoints, bigRotMatrix)
    rotatePoints(app.gridPoints, bigRotMatrix)
    rotatePoints(app.cubePoints, bigRotMatrix)

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
            scale = 75
            labels = True
        else:
            color = 'grey'
            thicc = 1
            arrows = False
            scale = app.scale
            labels = False
        
        for i in range(0, len(pointList), 2):

            # find projection of start and end points
            startPoint = pointList[i].reshape((3,1))
            endPoint = pointList[i + 1].reshape((3,1))
            projStart = np.dot(app.projectionMatrix, startPoint)
            projEnd = np.dot(app.projectionMatrix, endPoint)

            # get coordinates from projection
            x1 = int(projStart[0] * scale) + app.centerPos[0]
            y1 = int(projStart[1] * scale) + app.centerPos[1]
            x2 = int(projEnd[0] * scale) + app.centerPos[0]
            y2 = int(projEnd[1] * scale) + app.centerPos[1]

            # draws primary axis
            drawLine(x1, y1, x2, y2, fill = color, lineWidth = thicc, arrowStart = arrows, arrowEnd = arrows)
            if labels:
                x1 += 10
                y1 += 10
                label = 'X' if i == 0 else ('Y' if i == 2 else 'Z')
                drawLabel(label, x1, y1, align = 'center', bold = True, size = 20)
            

# projects all 3D points in a pointList into 2D points, stored in projectedPointList
def projectPoints(app, pointList, projectedPointList):
    for i in range(len(pointList)):
        point = pointList[i]

        # actual matrix multiplication
        rotatedPoint = point.reshape((3,1))
        projectedPoint = np.dot(app.projectionMatrix, rotatedPoint)

        # get coordinates from projection
        x = int(projectedPoint[0] * app.scale) + app.centerPos[0]
        y = int(projectedPoint[1] * app.scale) + app.centerPos[1]

        # add point to list
        projectedPointList[i] = Point2D(i, x, y)

def redrawAll(app):

    # projects box and cube points
    projectPoints(app, app.boxPoints, app.projectedBoxPoints)
    projectPoints(app, app.cubePoints, app.projectedCubePoints)

    # draws each box line
    for i, j in app.boxLines:
        x1, y1 = app.projectedBoxPoints[i].x, app.projectedBoxPoints[i].y
        x2, y2 = app.projectedBoxPoints[j].x, app.projectedBoxPoints[j].y
        drawLine(x1, y1, x2, y2, fill = 'grey', lineWidth = 0.5)

    # draw each cube face
    for a, b, c, d in app.faces:
        xA, yA = app.projectedCubePoints[a].x, app.projectedCubePoints[a].y
        xB, yB = app.projectedCubePoints[b].x, app.projectedCubePoints[b].y
        xC, yC = app.projectedCubePoints[c].x, app.projectedCubePoints[c].y
        xD, yD = app.projectedCubePoints[d].x, app.projectedCubePoints[d].y
        drawPolygon(xA, yA, xB, yB, xC, yC, xD, yD, fill = 'grey')
 
    # draws axes and grid lines
    drawLines(app, app.axesPoints)
    drawLines(app, app.gridPoints)

    # draws each cube line
    for i, j in app.lines:
        # gets points to make line
        x1, y1 = app.projectedCubePoints[i].x, app.projectedCubePoints[i].y
        x2, y2 = app.projectedCubePoints[j].x, app.projectedCubePoints[j].y
        # draws line
        drawLine(x1, y1, x2, y2)

    # draws each point
    for point in app.projectedCubePoints:
        radius = app.pointRad * app.scale/100
        drawCircle(point.x, point.y, radius, fill = 'black')

    # title and instructions
    drawLabel('shitty desmos', app.width/2, app.height/20, size = 16)
    drawLabel('press p to pause, up/down arrows to adjust grid', app.width/2, app.height/20 + 20, size = 12)
    drawLabel('left/right arrows to change view', app.width/2, app.height/20 + 30, size = 12)

    # center
    drawCircle(app.centerPos[0], app.centerPos[1], 5)

def onKeyPress(app, key):
    # pause button
    if key == 'p':
        app.paused = not app.paused
    if key == 'up':
        app.gridSize -= 0.1
    if key == 'down':
        app.gridSize += 0.1
    if key == 'j':
        app.scale += 20
    if key == 'k':
        app.scale -= 20
    
def onKeyHold(app, keys):
    # rotate viewer angle
    if 'left' in keys:
        app.viewerAngleZ -= math.pi/36
    if 'right' in keys: 
        app.viewerAngleZ += math.pi/36

    
def onMouseDragNAH(app, mouseX, mouseY):
    xMin = yMin = app.axisSize * app.scale
    xMax = app.width - app.axisSize * app.scale
    yMax = app.height - app.axisSize * app.scale
    if xMin <= mouseX <= xMax:
        app.centerPos[0] = mouseX
    if yMin <= mouseY <= yMax:
        app.centerPos[1] = mouseY


def main():
    runApp(width = 1200, height = 800)

main()

# Sources:
#   https://www.youtube.com/watch?v=qw0oY6Ld-L0 (referenced to initialize points and use numpy with matrices)
#   https://en.wikipedia.org/wiki/Rotation_matrix (got x, y, and z rotation matrices from here)
#   chatGPT used to debug problem with rotation matrices compounding on one another, causing excess rot speed
