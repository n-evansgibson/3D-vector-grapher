from cmu_graphics import * 
import numpy as np
import math


# Synopsis: FML

def onAppStart(app):

    # points of cube
    app.points = [
    np.matrix([-1, -1, 1]),
    np.matrix([1, -1, 1]),
    np.matrix([1, 1, 1]),
    np.matrix([-1, 1, 1]),
    np.matrix([-1, -1, -1]),
    np.matrix([1, -1, -1]),
    np.matrix([1, 1, -1]),
    np.matrix([-1, 1, -1])
    ]

    # projection
    app.projectionMatrix = np.array([[1, 0, 0], [0, 1, 0]])
    app.projectedPoints = [[0, 0] for _ in range(len(app.points))]

    # scales to size of screen
    app.scale = 100
    app.circlePos = [app.width/2, app.height/2]

    # rotation controls
    app.rot = 0
    app.stepsPerSecond = 30

    # extra rotation matrices
    app.yMatrix = np.array([[math.cos(app.rot), 0, math.sin(app.rot)], [0, 1, 0], [-math.sin(app.rot), 0, math.cos(app.rot)]])
    app.zMatrix = np.array([[math.cos(app.rot), -math.sin(app.rot), 0], [math.sin(app.rot), math.cos(app.rot), 0], [0, 0, 1]])

def onStep(app):
    # Increase rotation angle
    app.rot += 0.2
    xMatrix = np.array([
        [1, 0, 0],
        [0, math.cos(app.rot), -math.sin(app.rot)],
        [0, math.sin(app.rot), math.cos(app.rot)]
    ])
    
    # rotate all points across x axis
    for i in range(len(app.points)):
        app.points[i] = np.dot(xMatrix, app.points[i].reshape((3,1))).flatten()

def redrawAll(app):

    # Projects each point
    for i in range(len(app.points)):
        point = app.points[i]

        # note: point.reshape turns any 1D list into an n*m 2D matrix
        rotatedPoint = point.reshape((3, 1))
        projectedPoint = np.dot(app.projectionMatrix, rotatedPoint)

        # note: why do I need to convert to an int to get out of brackets?
        x = int(projectedPoint[0][0]) * app.scale + app.circlePos[0]
        y = int(projectedPoint[1][0]) * app.scale + app.circlePos[1]

        app.projectedPoints[i] = [x, y]
    
    # Draws each projected point
    for x, y in app.projectedPoints:
        drawCircle(x , y, 5)


def main():
    runApp(width = 800, height = 800)

main()

