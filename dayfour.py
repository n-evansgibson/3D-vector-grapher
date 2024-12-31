from cmu_graphics import *
import numpy as np
import math
import copy


# Synopsis: At the start of the program, I want to show the cube and the axes properly oriented. The should be projected and an initial
# rotation should be applied across the z axis. After the app starts, only the cube can rotate. 

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

    # points of axes
    app.axisSize = 12
    app.axesPoints = [
        # x axis
        np.array([app.axisSize, 0, 0]),
        np.array([-app.axisSize, 0, 0]),
        # y axis
        np.array([0, app.axisSize, 0]),
        np.array([0, -app.axisSize, 0]),
        # z axis
        np.array([0, 0, app.axisSize]),
        np.array([0, 0, -app.axisSize]),
    ]
    app.baseAxesPoints = [copy.deepcopy(point) for point in app.axesPoints]
    app.axesLines = [
        (0, 1),
        (2, 3),
        (4, 5)
    ]

    # points of cube
    app.points = [
    np.array([-1, -1, 1]),
    np.array([1, -1, 1]),
    np.array([1, 1, 1]),
    np.array([-1, 1, 1]),
    np.array([-1, -1, -1]),
    np.array([1, -1, -1]),
    np.array([1, 1, -1]),
    np.array([-1, 1, -1])
    ]

    app.basePoints = [copy.copy(point) for point in app.points]
    
    # projection matrix and projected points
    app.projectionMatrix = np.array([[0, 1, 0], [0, 0, 1]])
    app.projectedPoints = [None for _ in range(len(app.points))]
    app.pointRad = 5

    # point indices that create lines of cube
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

    # point indices that create faces of cube
    app.faces = [
        (0, 1, 2, 3), 
        (4, 5, 6, 7),
        (0, 3, 7, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (0, 1, 5, 4)
    ]

    # scales to size of screen
    app.scale = 100
    app.circlePos = [app.height/2, app.width/2]

    # rotation controls
    app.rX = 0
    app.rY = 0
    app.rZ = 0
    app.rSpeed = 0.02
    app.viewerAngleZ = app.viewerAngleY = math.pi/8

    # basic controls
    app.paused = True

def onStep(app):

    # axis rotation (stays the same unless viewing angle is adjusted)
    app.axesPoints = [copy.copy(point) for point in app.baseAxesPoints]
    app.points = [copy.copy(point) for point in app.basePoints]

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
    rotatePoints(app.points, axisRotMatrixZ)
    rotatePoints(app.points, axisRotMatrixY)

    # rotates cube if unpaused
    if not app.paused: 
        takeStep(app)

def takeStep(app):

    # resets to original points
    

    # rotate cube x
    app.rX += app.rSpeed
    xMatrix = np.array([
        [1, 0, 0],
        [0, math.cos(app.rX), -math.sin(app.rX)],
        [0, math.sin(app.rX), math.cos(app.rX)]
    ])    
    # rotate y
    app.rY += app.rSpeed
    yMatrix = np.array([
        [math.cos(app.rY), 0, math.sin(app.rY)],
        [0, 1, 0],
        [-math.sin(app.rY), 0, math.cos(app.rY)]
    ])    
    # rotate z
    app.rZ += app.rSpeed
    zMatrix = np.array([
        [math.cos(app.rZ), -math.sin(app.rZ), 0],
        [math.sin(app.rZ), math.cos(app.rZ), 0],
        [0, 0, 1]
    ])

    # applies rotation to cube points
    rotatePoints(app.points, xMatrix)
    rotatePoints(app.points, yMatrix)
    rotatePoints(app.points, zMatrix)

# Applies rotation matrix to points (x, y or z)
def rotatePoints(pointList, matrix):
    for i in range(len(pointList)):
        point = pointList[i].reshape((3,1))
        rotatedPoint = np.dot(matrix, point)
        pointList[i] = rotatedPoint.flatten()

def redrawAll(app):

    # project cube points onto 2D plane
    for i in range(len(app.points)):
        point = app.points[i]

        # actual matrix multiplication
        rotatedPoint = point.reshape((3, 1))
        projectedPoint = np.dot(app.projectionMatrix, rotatedPoint)

        #get coordinates from projection
        x = int(projectedPoint[0] * app.scale) + app.circlePos[0]
        y = int(projectedPoint[1] * app.scale) + app.circlePos[1]

        # add point to list
        app.projectedPoints[i] = Point2D(i, x, y)

    # draws each face
    for a, b, c, d in app.faces:
        xA, yA = app.projectedPoints[a].x, app.projectedPoints[a].y
        xB, yB = app.projectedPoints[b].x, app.projectedPoints[b].y
        xC, yC = app.projectedPoints[c].x, app.projectedPoints[c].y
        xD, yD = app.projectedPoints[d].x, app.projectedPoints[d].y
        drawPolygon(xA, yA, xB, yB, xC, yC, xD, yD, fill = 'grey')

    # projects axes onto 2D plane
    for startIndex, endIndex in app.axesLines:

        # find projection of start and end points
        startPoint = app.axesPoints[startIndex].reshape((3,1))
        endPoint = app.axesPoints[endIndex].reshape((3,1))
        projStart = np.dot(app.projectionMatrix, startPoint)
        projEnd = np.dot(app.projectionMatrix, endPoint)
        
        # get coordiantes from projection
        x1 = int(projStart[0] * app.scale) + app.circlePos[0]
        y1 = int(projStart[1] * app.scale) + app.circlePos[1]
        x2 = int(projEnd[0] * app.scale) + app.circlePos[0]
        y2 = int(projEnd[1] * app.scale) + app.circlePos[1]

        drawLine(x1, y1, x2, y2, fill = 'red', lineWidth = 1)

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

    # cube speed controls
    if key == 'up':
        app.rSpeed += 0.005
    if key == 'down':
        app.rSpeed -= 0.005
    
    # rotate viewer angle
    if key == 'left':
        app.viewerAngleZ -= math.pi/12
    if key == 'right':
        app.viewerAngleZ += math.pi/12

def main():
    runApp(width = 800, height = 800)

main()

# Sources:
#   https://www.youtube.com/watch?v=qw0oY6Ld-L0 (referenced to initialize points and use numpy with matrices)
#   https://en.wikipedia.org/wiki/Rotation_matrix (got x, y, and z rotation matrices from here)
#   chatGPT used to debug problem with rotation matrices compounding on one another, causing excess rot speed