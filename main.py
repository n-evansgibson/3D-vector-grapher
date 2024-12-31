from cmu_graphics import * 
from axesInit import (makeGrid, axesPoints, cubePoints, cubeLines, cubeFaces,
boxPoints, boxLines, boxFaces)
from shapely.geometry import Point, Polygon
import numpy as np
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
    app.scale = 60
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

# classes are down here because inputBox requires onAppStart vars

class Point2D:

    def __init__(self, label, x, y):
        self.label = label
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point {self.label} is at ({self.x}, {self.y})'
    
    def __eq__(self, other):
        return isinstance(other, Point2D) and self.label == other.label
    
class inputBox:

    def __init__(self, x, y, ID):
        self.x = x
        self.y = y
        self.width = 1200/4 # 1200 = app.width
        self.height = 800/12 # 800 = app.height
        self.crossX = self.x + 15*self.width/16
        self.crossY = self.y + self.height/4
        self.input = ''
        self.id = ID
        self.selected = False
        self.crossSelected = False
        self.drawable = False

    def __repr__(self):
        return f'Input box at ({self.x}, {self.y})'
    
    def __eq__(self, other):
        return isinstance(other, inputBox) and self.id == other.id
    
    def isSelected(self, mouseX, mouseY):
        left = self.x
        right = self.x + self.width
        top = self.y
        bottom = self.y + self.height
        return (left <= mouseX <= right) and (top <= mouseY <= bottom)

    def crossIsSelected(self, mouseX, mouseY):
        left = self.crossX - 10
        right = self.crossX + 10
        top = self.crossY - 10
        bottom = self.crossY + 10
        return (left <= mouseX <= right) and (top <= mouseY <= bottom)

    def hasDrawablePoint(self):
        return self.input[0] == '(' and self.input[-1] == ')' and self.input.count(',') == 2

    
# Adds a new box to the list if the last box was selected
def makeNewBox(app):
    lastBox = app.userInputs[-1]
    lastBoxY = lastBox.y
    newY = lastBoxY + lastBox.height
    newID = lastBox.id + 1
    app.userInputs[-1].selected = True
    app.userInputs.append(inputBox(lastBox.x, newY, newID))

# Adds point to graph if a point is entered
def addOutput(app, box):
    input = box.input
    coords = []
    if box.hasDrawablePoint:
        input = input[1:-1]
        for s in input.split(','):
            s.strip()
            coords.append(float(s))
        dataType = 'point'
        # updates user output and copy of user output
        newOutputBox = [box.id, dataType, []]
        app.userOutputs[2].append(np.array([coords[0], coords[1], coords[2]]))
        app.originalUserOutputs.append(np.array([coords[0], coords[1], coords[2]]))



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
    app.userOutputs = [copy.copy(point) for point in app.originalUserOutputs]

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
    rotatePoints(app.boxPoints, bigRotMatrix)
    rotatePoints(app.axesPoints, bigRotMatrix)
    rotatePoints(app.gridPoints, bigRotMatrix)
    rotatePoints(app.cubePoints, bigRotMatrix)
    rotatePoints(app.userOutputs, bigRotMatrix)

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
    if len(app.userOutputs) != 0:
        projectedUserPoints = [None for _ in range(len(app.userOutputs))]
        projectPoints(app, app.userOutputs, projectedUserPoints)

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

    # draws each cube point
    for point in app.projectedCubePoints:
        radius = app.pointRad * app.scale/100
        drawCircle(point.x, point.y, radius, fill = 'black')

    # draws each user point
    if len(app.userOutputs) != 0:
        for point in projectedUserPoints:
            radius = app.pointRad * app.scale/ 100
            drawCircle(point.x, point.y, radius, fill = 'red')

    #draws input boxes
    for box in app.userInputs:
        # highlights selected box
        borderW = 2 if box.selected else 1
        borderColor = 'red' if box.selected else 'black'
        opacitea = 40 if box.id == len(app.userInputs) else 100
        # makes selected cross red
        crossColor = 'red' if box.crossSelected else 'black'
        # draws box, input, id, and x
        drawRect(box.x, box.y, box.width, box.height, fill = None, border = borderColor, borderWidth = borderW, opacity = opacitea)
        drawLabel(box.input, box.x + 10, box.y + box.height/2, size = 16, align = 'left')
        drawLabel('X', box.crossX, box.crossY, size = 16, opacity = opacitea, fill = crossColor)
        drawLabel(f'{box.id}', box.x + 10, box.crossY, size = 16, opacity = opacitea)
        
    # title and instructions
    drawLabel('desmoo', app.width/2, app.height/20, size = 16)
    drawLabel('press p to pause, up/down arrows to adjust grid', app.width/2, app.height/20 + 20, size = 12)
    drawLabel('left/right arrows to change view', app.width/2, app.height/20 + 30, size = 12)
    
    # test: mouse-cube intersection
    drawLabel(f'mouse-cube intersection: {app.mouseInBox}', app.width/2 - 40, app.height - 20, size = 12)

def onKeyPress(app, key):
    # general controls
    if key == 'p':
        app.paused = not app.paused

    # testing controls
    if key == 'up':
        app.gridSize -= 0.1
    if key == 'down':
        app.gridSize += 0.1
    if key == 'j':
        app.scale += 5
    if key == 'k':
        app.scale -= 5

    # writing
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
    print(app.userOutputs)

def removeBox(app, box):
    removedBoxID = box.id - 1
    app.userInputs.pop(removedBoxID)
    app.originalUserOutputs.pop(removedBoxID)
    for i in range(removedBoxID, len(app.userInputs)):
        box = app.userInputs[i]
        box.id -= 1
        # shifts boxes upwards (800/12 = box.height)
        box.y -= 800/12 
        box.crossY -= 800/12

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
        

# mouse in polygon algorithm 
def mouseInBox(app, mouseX, mouseY):
    for i, j, k, l in app.boxFaces:
        intersections = 0
        for lineIndex in [i, j, k, l]:
            p1, p2 = app.boxLines[lineIndex]
            x1, y1 = app.projectedBoxPoints[p1].x, app.projectedBoxPoints[p1].y
            x2, y2 = app.projectedBoxPoints[p2].x, app.projectedBoxPoints[p2].y
            # checks if a ray coming from the left of the point intersects the polygon face
            if ((mouseY < y1) != (mouseY < y2)) and (mouseX < x1 + ((mouseY-y1)/(y2-y1))*(x2-x1)):
                intersections += 1
        if intersections % 2 == 1:
            return True
    return False

# mouse in polygon algorithm using shapely (better)
def mouseInBox(app, mouseX, mouseY):
    pt = Point(mouseX, mouseY)
    for i, j, k, l in app.faces:
        # adds each point in the face to the polygon
        pointList = []
        for pointIndex in [i, j, k, l]:
            point = app.projectedBoxPoints[pointIndex].x, app.projectedBoxPoints[pointIndex].y
            pointList.append(point)
        face = Polygon(pointList)
        if face.contains(pt):
            return True
    return False


def main():
    runApp(width = 1200, height = 800)

main()

# Sources:
#   https://www.youtube.com/watch?v=qw0oY6Ld-L0 (referenced to initialize points and use numpy with matrices)
#   https://en.wikipedia.org/wiki/Rotation_matrix (got x, y, and z rotation matrices from here)
#   https://www.youtube.com/watch?v=RSXM9bgqxJM (mouse in polygon algorithm)
#   chatGPT uses:
#       used to debug problem with rotation matrices compounding on one another, causing excess rot speed
#       used to debug infinte loop with creating new input boxes
