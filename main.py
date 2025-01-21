from cmu_graphics import *  # type: ignore
from axesInit import (makeGrid, axesPoints, cubePoints, cubeLines, cubeFaces,
boxPoints, boxLines, boxFaces)
from utils import (makeNewBox, addOutput, rotatePoints, drawLines, projectPoints, 
                   removeBox, mouseInBox, inputBox, meshgrid)
from PIL import Image # type: ignore
import numpy as np # type: ignore
import math
import copy
import string
    
def onAppStart(app):

    # defines points, lines, and faces for box
    app.boxPoints = boxPoints
    app.boxLines = boxLines
    app.boxFaces = boxFaces
    app.originalBoxPoints = [copy.deepcopy(point) for point in app.boxPoints]
    app.projectedBoxPoints = [None for _ in range(len(app.boxPoints))]

    # define points for axes
    app.axisSize = 5
    app.axesPoints = axesPoints
    app.originalAxesPoints = [copy.deepcopy(point) for  point in app.axesPoints]

    # defines points for xy grid
    app.gridSize = 1     # Number of grid divisions in each direction
    app.gridPoints = []
    makeGrid(app)
    app.originalGridPoints = [copy.deepcopy(point) for point in app.gridPoints]
    
    # angle of axes rotation
    app.viewerAngle = math.pi/4

    # points of demo cube
    app.cubePoints = cubePoints
    app.originalCubePoints = [copy.copy(point) for point in app.cubePoints]

    # projection matrix and projected points: these points are stored as a Point2D class
    app.projectionMatrix = np.array([[0, 1, 0], [0, 0, -1]])
    app.projectedCubePoints = [None for _ in range(len(app.cubePoints))]
    app.pointRad = 5

    # cube lines and faces
    app.lines = cubeLines
    app.faces = cubeFaces

    # stores user input (stored within boxes of inputBox class) and output points (numpy arrays)
    app.userInputs = []
    app.userOutputs = []
    app.originalUserOutputs = []
    # makes first user box
    app.userInputs.append(inputBox(25, 150, 1))
    app.userInputs[0].selected = True
    makeNewBox(app)

    # scales axes and cube
    app.scale = 50
    app.centerPos = [11*app.width/16, app.height/2]

    # cube rotation
    app.rX = 0
    app.rY = 0
    app.rZ = 0
    app.rSpeed = 0.02
    app.viewerAngleZ = app.viewerAngleY = math.pi/8
    app.dragAngleZ = app.dragAngleY = 0
    app.originalDragAngleZ = app.originalDragAngleY = 0
    app.boxRotation = False

    # basic controls
    app.paused = True
    app.mouseInBox = False
    app.holdCount = 0

    # mesh
    X = [-4, -2, 0, 2, 4]
    Y = [-4, -2, 0, 2, 4]
    Z = [-4, -2, 0, 2, 4]
    app.mesh = meshgrid(X, Y, Z)
    app.originalMesh = [copy.deepcopy(point) for point in app.mesh]
    app.projectedMeshPoints = [None for _ in range(len(app.originalMesh))]

def onStep(app):

    # if box is being rotated automatically, increase dragAngleZ and dragAngleY
    if app.boxRotation:
        app.dragAngleZ += app.fixedDragZ * 0.015
        app.dragAngleY += app.fixedDragY * 0.015

    bigAngleZ = app.viewerAngleZ + app.dragAngleZ
    bigAngleY = app.viewerAngleY + app.dragAngleY

    # copies original points
    app.boxPoints = [copy.copy(point) for point in app.originalBoxPoints]
    app.axesPoints = [copy.copy(point) for point in app.originalAxesPoints]
    app.gridPoints = [copy.copy(point) for point in app.originalGridPoints]
    app.cubePoints = [copy.copy(point) for point in app.originalCubePoints]
    app.userOutputs = [copy.deepcopy(output) for output in app.originalUserOutputs]
    app.mesh = [copy.deepcopy(point) for point in app.originalMesh]

    # updates grid
    makeGrid(app)

    axisRotMatrixZ = np.array([
        [math.cos(bigAngleZ), -math.sin(bigAngleZ), 0],
        [math.sin(bigAngleZ), math.cos(bigAngleZ), 0],
        [0, 0, 1]
    ])
    axisRotMatrixY = np.array([
        [math.cos(bigAngleY), 0, math.sin(bigAngleY)],
        [0, 1, 0],
        [-math.sin(bigAngleY), 0, math.cos(bigAngleY)]

    ])

    bigRotMatrix = np.dot(axisRotMatrixY, axisRotMatrixZ)
    
    # rotates axis, grid, and cube
    rotatePoints(app, app.boxPoints, bigRotMatrix)
    rotatePoints(app, app.axesPoints, bigRotMatrix)
    rotatePoints(app, app.gridPoints, bigRotMatrix)
    rotatePoints(app, app.cubePoints, bigRotMatrix)
    rotatePoints(app, app.userOutputs, bigRotMatrix)
    rotatePoints(app, app.mesh, bigRotMatrix)

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
    rotatePoints(app, app.cubePoints, xMatrix)
    rotatePoints(app, app.cubePoints, yMatrix)
    rotatePoints(app, app.cubePoints, zMatrix)


def redrawAll(app):

    # projects box and cube points, mesh points
    projectPoints(app, app.boxPoints, app.projectedBoxPoints)
    projectPoints(app, app.cubePoints, app.projectedCubePoints)
    projectPoints(app, app.mesh, app.projectedMeshPoints)

    # If there are outputs, projects each set of user outputs into a 2D list of projected outputs, where
    # each outer list represents a user output, and the inner list contains the points for that output

    if len(app.userOutputs) != 0:
        projectedUserOutputs = [[None, None, []] for _ in range(len(app.userOutputs))]
        for i in range(len(app.userOutputs)):
            projectedUserOutputs[i][0] = app.userOutputs[i][0]
            projectedUserOutputs[i][1] = app.userOutputs[i][1]
            outputList = copy.deepcopy(app.userOutputs[i][2])
            projectedUserOutputs[i][2] = [None for _ in range(len(outputList))]
            projectPoints(app, copy.deepcopy(outputList), projectedUserOutputs[i][2])

    # draws each box line
    for i, j in app.boxLines:
        x1, y1 = app.projectedBoxPoints[i].x, app.projectedBoxPoints[i].y
        x2, y2 = app.projectedBoxPoints[j].x, app.projectedBoxPoints[j].y
        drawLine(x1, y1, x2, y2, fill = 'grey', lineWidth = 0.5) # type: ignore

    # draw each cube face
    for a, b, c, d in app.faces:
        xA, yA = app.projectedCubePoints[a].x, app.projectedCubePoints[a].y
        xB, yB = app.projectedCubePoints[b].x, app.projectedCubePoints[b].y
        xC, yC = app.projectedCubePoints[c].x, app.projectedCubePoints[c].y
        xD, yD = app.projectedCubePoints[d].x, app.projectedCubePoints[d].y
        drawPolygon(xA, yA, xB, yB, xC, yC, xD, yD, fill = 'grey') # type: ignore
 
    # draws axes and grid lines
    drawLines(app, app.axesPoints)
    drawLines(app, app.gridPoints)

    # draws each cube line
    for i, j in app.lines:
        # gets points to make line
        x1, y1 = app.projectedCubePoints[i].x, app.projectedCubePoints[i].y
        x2, y2 = app.projectedCubePoints[j].x, app.projectedCubePoints[j].y
        # draws line
        drawLine(x1, y1, x2, y2) # type: ignore

    # draws each cube point
    for point in app.projectedCubePoints:
        radius = app.pointRad * app.scale/100
        drawCircle(point.x, point.y, radius, fill = 'black') # type: ignore

    # draws the points for each user output
    if len(app.userOutputs) != 0:
        for output in projectedUserOutputs:
            outputList = output[2]
            dataType = output[1]
            if dataType == 'point':
                for point in outputList:
                    radius = app.pointRad * app.scale/ 100
                    drawCircle(point.x, point.y, radius, fill = 'red') # type: ignore
                    # drawImage(app.cowCircle, point.x, point.y, width = radius*10, height = radius*8, align = 'center')
            elif dataType == 'vector':
                    x1, y1 = outputList[0].x, outputList[0].y
                    x2, y2 = outputList[1].x, outputList[1].y
                    drawLine(x1, y1, x2, y2, fill = 'red', arrowEnd = True) # type: ignore
            elif dataType == 'vector field':
                for i in range(len(outputList)):
                    x1, y1 = app.projectedMeshPoints[i].x, app.projectedMeshPoints[i].y
                    x2, y2 = outputList[i].x, outputList[i].y
                    drawLine(x1, y1, x2, y2, fill = 'red', arrowEnd = True, lineWidth = 1) #type: ignore


    #draws background
    drawRect(0, 0, 9*app.width/24, app.height, fill = 'lavender') # type: ignore

    # draws input boxes
    for box in app.userInputs:

        # highlights selected box
        borderW = 2 if box.selected else 1
        borderColor = 'darkSlateBlue' if box.selected else 'black'
        opacitea = 40 if box.id == len(app.userInputs) else 100
        # makes selected cross red
        crossColor = 'red' if box.crossSelected else 'black'

        # draws box, input, id, and x
        drawRect(box.x, box.y, box.width, box.height, fill = None, border = borderColor, borderWidth = borderW, opacity = opacitea) # type: ignore
        drawLabel(box.input, box.x + 15, box.y + box.height/2, size = 16, align = 'left') # type: ignore
        drawLabel('X', box.crossX, box.crossY, size = 16, opacity = opacitea, fill = crossColor) # type: ignore
        drawLabel(f'{box.id}', box.x + 10, box.crossY, size = 16, opacity = opacitea) # type: ignore
        
    # title and instructions
    drawLabel('3D Vector Grapher', app.width/5, app.height/20, size = 20, font = 'montserrat', bold = True) # type: ignore
    drawLabel('Click and drag graph to view. Press P to spin cube.', app.width/5, app.height/20 + 30, size = 16, font = 'montserrat') # type: ignore
    drawLabel('Add points as (x,y,z) or vectors as [x y z].', app.width/5, app.height/20 + 50, size = 16, font = 'montserrat') # type: ignore
    drawLabel('Add constant vector fiends as f(x, y, z) = [a, b, c].', app.width/5, app.height/20 + 70, size = 16, font = 'montserrat') # type: ignore
    

def onKeyPress(app, key):
    # general controls
    if key == 'p':
        app.paused = not app.paused

    # testing controls
    if key == 'up':
        app.gridSize -= 0.1
    if key == 'down':
        app.gridSize += 0.1
    if key == 'nah':
        app.scale += 5
    if key == 'nah':
        app.scale -= 5

    # writing in input boxes
    for box in app.userInputs:
        if box.selected:
            if key in string.printable:
                box.input = box.input + key
            elif key == 'space':
                box.input = box.input + ' '
            elif key == 'backspace':
                box.input = box.input[:-1]
            elif key == 'enter':
                addOutput(app, box)

    
def onKeyHold(app, keys):

    # rotate viewer angle
    if 'left' in keys:
        app.viewerAngleZ -= math.pi/36
    if 'right' in keys: 
        app.viewerAngleZ += math.pi/36

    # controls backspace when held
    if 'backspace' in keys:
        app.holdCount += 1
        for box in app.userInputs:
            # if backspace has been held in a box for more than a second, allow backspace hold
            if box.selected and box.input == '':
                app.holdCount = 0
            elif box.selected and app.holdCount > 19 and app.holdCount % 2 == 0:
                box.input = box.input[:-1]
    

# dragging the box to rotate
def onMousePress(app, mouseX, mouseY):

    # stops box rotation, resets mouse drag
    if app.boxRotation:
        app.boxRotation = False
        app.originalDragAngleZ = app.dragAngleZ
        app.originalDragAngleY = app.dragAngleY
    else:
        app.dragging = True
        app.dragStartX, app.dragStartY = mouseX, mouseY

    # checks for selected box or cross
    lastBoxID = len(app.userInputs)
    for box in app.userInputs:
        box.selected = box.isSelected(mouseX, mouseY)
        box.crossSelected = box.crossIsSelected(mouseX, mouseY)
        # creates a new box if the last box is currently (but not previously) selected
        if box.id == lastBoxID and box.selected:
            makeNewBox(app)
            break
        # removes a box and adjusts IDS if a cross is selected
        if box.crossSelected and len(app.userInputs) > 2: 
            removeBox(app, box)



# If the mouse is in the box, stop rotation. If the mouse is outside of the box, rotate until mouse is pressed
def onMouseRelease(app, mouseX, mouseY):

    app.dragging = False
    if mouseInBox(app, mouseX, mouseY):
        # reset mouse drag
        app.originalDragAngleZ = app.dragAngleZ
        app.originalDragAngleY = app.dragAngleY
    else:
        # initiate cube rotation
        app.boxRotation = True
        app.fixedDragZ = app.dragAngleZ - app.originalDragAngleZ
        app.fixedDragY = app.dragAngleY - app.originalDragAngleY

def onMouseDrag(app, mouseX, mouseY):
    if app.dragging: 
        dragX = mouseX - app.dragStartX
        dragY = mouseY - app.dragStartY
        app.dragAngleZ = app.originalDragAngleZ + dragX * 0.005
        app.dragAngleY = app.originalDragAngleY + dragY * 0.005

def onMouseMove(app, mouseX, mouseY):
    app.mouseInBox = mouseInBox(app, mouseX, mouseY)

    # checks if cross is being hovered over
    lastBoxID = len(app.userInputs)
    for box in app.userInputs:
        box.crossSelected = box.crossIsSelected(mouseX, mouseY) and box.id != lastBoxID
        
def main():
    runApp(width = 1200, height = 800) # type: ignore

main()

# Sources:
#   https://www.youtube.com/watch?v=qw0oY6Ld-L0 (referenced to initialize points and use numpy with matrices)
#   https://en.wikipedia.org/wiki/Rotation_matrix (got x, y, and z rotation matrices from here)
#   https://www.youtube.com/watch?v=RSXM9bgqxJM (mouse in polygon algorithm)
#   chatGPT uses:
#       used to debug problem with rotation matrices compounding on one another, causing excess rot speed
#       used to debug infinte loop with creating new input boxes
