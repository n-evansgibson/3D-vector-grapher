from cmu_graphics import *
import numpy as np
import math
import copy
import random

# Synopsis: learning how to change the location of points on the cube

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
    app.projectionMatrix = np.array([[1, 0, 0], [0, 1, 0]])
    app.projectedPoints = [None for _ in range(len(app.points))]
    app.pointRGB = [200, 200, 200]
    app.pointRad = 5

    # selecting and editing points
    app.selectedPoint = None

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
    app.stepsPerSecond = 30
    app.rSpeed = 0.02

    # basic controls
    app.paused = False

def onStep(app):
    if not app.paused: 
        takeStep(app)

def takeStep(app):

    # resets to original points
    app.points = [copy.copy(point) for point in app.basePoints]

    # rotate x
    app.rX += app.rSpeed
    xMatrix = np.array([
        [1, 0, 0],
        [0, math.cos(app.rX), -math.sin(app.rX)],
        [0, math.sin(app.rX), math.cos(app.rX)]
    ])
    # applies x rotation
    rotatePoints(app, xMatrix)

    # rotate y
    app.rY += app.rSpeed
    yMatrix = np.array([
        [math.cos(app.rY), 0, math.sin(app.rY)],
        [0, 1, 0],
        [-math.sin(app.rY), 0, math.cos(app.rY)]
    ])
    # applies y rotation
    rotatePoints(app, yMatrix)

    # rotate z
    app.rZ += app.rSpeed
    zMatrix = np.array([
        [math.cos(app.rZ), -math.sin(app.rZ), 0],
        [math.sin(app.rZ), math.cos(app.rZ), 0],
        [0, 0, 1]
    ])
    # applies z rotation
    rotatePoints(app, zMatrix)


def redrawAll(app):

    # project points onto 2D plane
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
    r, g, b = app.pointRGB
    randomColor = rgb(r, g, b)
    for a, b, c, d in app.faces:
        xA, yA = app.projectedPoints[a].x, app.projectedPoints[a].y
        xB, yB = app.projectedPoints[b].x, app.projectedPoints[b].y
        xC, yC = app.projectedPoints[c].x, app.projectedPoints[c].y
        xD, yD = app.projectedPoints[d].x, app.projectedPoints[d].y

        drawPolygon(xA, yA, xB, yB, xC, yC, xD, yD, fill = randomColor)

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

    drawLabel('aneuryism cube', app.width/2, app.height/20, size = 16)
    drawLabel('press p to pause, up/down arrows to change rotation speed', app.width/2, app.height/20 + 20, size = 12)
    drawLabel('you can drag it around I guess', app.width/2, app.height/20 + 40, size = 12)
    drawLabel(f'speed: {app.rSpeed}', app.width/2, app.height - 20, size = 12)


# Applies rotation matrix to points (x, y or z)
def rotatePoints(app, matrix):
    for i in range(len(app.points)):
        point = app.points[i].reshape((3,1))
        rotatedPoint = np.dot(matrix, point)
        app.points[i] = rotatedPoint.flatten()
    
def onKeyPress(app, key):
    # pause button
    if key == 'p':
        app.paused = not app.paused

    # cube speed controls
    if key == 'up':
        app.rSpeed += 0.005
    if key == 'down':
        app.rSpeed -= 0.005

def onMouseDrag(app, mouseX, mouseY):

    # move the cube around
    if not app.paused:
        xMin = yMin = app.scale
        xMax = app.width - app.scale
        yMax = app.height - app.scale
        if xMin <= mouseX <= xMax:
            app.circlePos[0] = mouseX
        if yMin <= mouseY <= yMax:
            app.circlePos[1] = mouseY
    
    # editing position of points
    if app.selectedPoint != None:
        pointIndex = app.selectedPoint.label
        app.basePoints[pointIndex][0] = app.points[pointIndex][0] = (mouseX - app.circlePos[0]) / app.scale
        app.basePoints[pointIndex][1] = app.points[pointIndex][1] = (mouseY - app.circlePos[1]) / app.scale

def onMousePress(app, mouseX, mouseY):

    # allows a point to be moved if it is pressed on
    for point in app.projectedPoints:
        print(point)
        if point != app.selectedPoint and distance(point.x, point.y, mouseX, mouseY) <= app.pointRad:
            app.selectedPoint = point
            print('^selected')
            return
    app.selectedPoint = None
        
def main():
    runApp(width = 800, height = 800)

main()

# Sources:
#   https://www.youtube.com/watch?v=qw0oY6Ld-L0 (referenced to initialize points and use numpy with matrices)
#   https://en.wikipedia.org/wiki/Rotation_matrix (got x, y, and z rotation matrices from here)
#   chatGPT used to debug problem with rotation matrices compounding on one another, causing excess rot speed