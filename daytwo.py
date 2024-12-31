from cmu_graphics import *
import numpy as np
import math
import copy
import random

# Synopsis: rotating 3D cube that gives you a headache!

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

    app.originalPoints = [copy.copy(point) for point in app.points]
    
    # projection matrix and projected points
    app.projectionMatrix = np.array([[1, 0, 0], [0, 1, 0]])
    app.projectedPoints = [[0, 0] for _ in range(len(app.points))]
    app.pointRGB = [255, 0, 0]

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

    # changes color of dots
    app.pointRGB[0] = random.randint(0, 255)
    app.pointRGB[1] = random.randint(0, 255)
    app.pointRGB[2] = random.randint(0, 255)

    # resets to original points
    app.points = [copy.copy(point) for point in app.originalPoints]

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

    # x and y axis
    drawLine(0, app.height/2, app.width, app.height/2, lineWidth = 1, fill = 'grey')
    drawLine(app.width/2 + 200, app.height/2 - 10, app.width/2 + 200, app.height/2 + 10, lineWidth = 1, fill = 'grey')
    drawLabel('x', app.width - 20, app.height/2)
    drawLine(app.width/2, 0, app.width/2, app.height, lineWidth = 1, fill = 'grey')
    drawLine(app.width/2 - 200, app.height/2 - 10, app.width/2 - 200, app.height/2 + 10, lineWidth = 1, fill = 'grey')
    drawLabel('y', app.width/2, 20)


    # project points onto 2D plane
    for i in range(len(app.points)):
        point = app.points[i]

        rotatedPoint = point.reshape((3, 1))
        projectedPoint = np.dot(app.projectionMatrix, rotatedPoint)
        x = int(projectedPoint[0] * app.scale) + app.circlePos[0]
        y = int(projectedPoint[1] * app.scale) + app.circlePos[1]
        app.projectedPoints[i] = [x, y]


    # draws each face
    r, g, b = app.pointRGB
    randomColor = rgb(r, g, b)
    for a, b, c, d in app.faces:
        xA, yA = app.projectedPoints[a]
        xB, yB = app.projectedPoints[b]
        xC, yC = app.projectedPoints[c]
        xD, yD = app.projectedPoints[d]

        drawPolygon(xA, yA, xB, yB, xC, yC, xD, yD, fill = randomColor)

    # draws each line
    for i, j in app.lines:
        
        # gets points to make line
        x1, y1 = app.projectedPoints[i]
        x2, y2 = app.projectedPoints[j]

        # draws line
        drawLine(x1, y1, x2, y2)

    # draws each point
    for x, y in app.projectedPoints:
        drawCircle(x, y, 5, fill = 'black')

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