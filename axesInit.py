from cmu_graphics import * 
import numpy as np
import math

app.axisSize = 4

# box

boxPoints = [
    np.array([-app.axisSize, -app.axisSize, app.axisSize]),
    np.array([app.axisSize, -app.axisSize, app.axisSize]),
    np.array([app.axisSize, app.axisSize, app.axisSize]),
    np.array([-app.axisSize, app.axisSize, app.axisSize]),
    np.array([-app.axisSize, -app.axisSize, -app.axisSize]),
    np.array([app.axisSize, -app.axisSize, -app.axisSize]),
    np.array([app.axisSize, app.axisSize, -app.axisSize]),
    np.array([-app.axisSize, app.axisSize, -app.axisSize])
]

boxLines = [
    (0, 1), #0
    (0, 3), #1
    (0, 4), #2
    (1, 5), #3
    (2, 1), #4
    (2, 3), #5
    (2, 6), #6
    (3, 7), #7
    (4, 5), #8
    (4, 7), #9
    (6, 5), #10
    (6, 7)  #11
    ]

# Each tuple represents a face of the cube, defined by the lines bordering it
boxFaces = [
    (0, 8, 3, 2),
    (1, 9, 2, 7),
    (5, 11, 6, 7),
    (4, 10, 6, 3),
    (1, 4, 0, 5),
    (9, 10, 8, 11)
]

# axes
axesPoints = [
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

# grid

def makeGrid(app):
    app.gridPoints = []
    numDivisions = int(app.axisSize/app.gridSize)
    for i in range(numDivisions):
        # makes x gridline in positive dir
        newY = (i + 1) * app.gridSize
        newStartPoint  = np.array([app.axisSize, newY, 0])
        newEndPoint = np.array([-app.axisSize, newY, 0])
        app.gridPoints.append(newStartPoint)
        app.gridPoints.append(newEndPoint)
        # makes x gridline in opposite dir
        oppositeY = -newY
        oppStartPoint = np.array([app.axisSize, oppositeY, 0])
        oppEndPoint = np.array([-app.axisSize, oppositeY, 0])
        app.gridPoints.append(oppStartPoint)
        app.gridPoints.append(oppEndPoint)
    # y grid
    for i in range(numDivisions):
        # makes y gridline in positive dir
        newX = (i + 1) * app.gridSize
        newStartPoint = np.array([newX, app.axisSize, 0])
        newEndPoint = np.array([newX, -app.axisSize, 0])
        app.gridPoints.append(newStartPoint)
        app.gridPoints.append(newEndPoint)
        # makes y gridline in opposite dir
        oppositeX = -newX
        oppStartPoint = np.array([oppositeX, app.axisSize, 0])
        oppEndPoint = np.array([oppositeX, -app.axisSize, 0])
        app.gridPoints.append(oppStartPoint)
        app.gridPoints.append(oppEndPoint)

# test cube (hardcoded)

cubePoints = [
    np.array([-1, -1, 1]),
    np.array([1, -1, 1]),
    np.array([1, 1, 1]),
    np.array([-1, 1, 1]),
    np.array([-1, -1, -1]),
    np.array([1, -1, -1]),
    np.array([1, 1, -1]),
    np.array([-1, 1, -1])
]

cubeLines = [
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

cubeFaces = [
    (0, 1, 2, 3), 
    (4, 5, 6, 7),
    (0, 3, 7, 4),
    (1, 2, 6, 5),
    (2, 3, 7, 6),
    (0, 1, 5, 4)
    ]