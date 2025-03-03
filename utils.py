from cmu_graphics import *  # type: ignore
from shapely.geometry import Point, Polygon # type: ignore
from calculator import evalExpression
import numpy as np # type: ignore
import copy
import string

# classes

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
        self.width = 1200/3 # 1200 = app.width
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
    
    def hasDrawableVector(self):
        return ((self.input[0] == '[' and self.input [-1] == ']') and
                (self.input.count(',') == 2 or self.input.count(' ') == 2))
    
    def hasDrawableVectorField(self):
        if (self.input.count('f(x,y,z)') == 1) or (self.input.count('f(x, y, z)') == 1):
            eqIndex = self.input.find('=')
            expr = self.input[eqIndex + 1:].strip()
            return ((expr[0] == '[' and expr[-1] == ']') and 
                    (expr.count(',') == 2 or expr.count(' ') == 2))
        return False
    
    def hasDrawableCurve(self):
        if (self.input.count('f(t)') == 1) or (self.input.count('r(t)') == 1):
            eqIndex = self.input.find('=')
            expr = self.input[eqIndex+1:].strip()
            return ((expr[0] == '[' and expr[-1] == ']') and 
                    (expr.count(',') == 2 or expr.count(' ') == 2))
        return False

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
    
    # recognizes points if written as (x, y, z)
    print(f'input: {input}')
    if box.hasDrawablePoint():
        print('added point')
        input = input[1:-1]
        for s in input.split(','):
            s.strip()
            coords.append(float(s))
        dataType = 'point'
        # updates user output and copy of user output
        newOutputBox = [box.id, dataType, []]
        newOutputBox[2].append(np.array([coords[0], coords[1], coords[2]]))
        app.userOutputs.append(newOutputBox)
        app.originalUserOutputs.append(copy.deepcopy(newOutputBox))

    # recognizes vectors if written as [x, y, z] or [x y z]
    elif box.hasDrawableVector():
        print('added vector')
        input = input[1:-1]
        splitter = ',' if input.count(',') > 0 else ' '
        for s in input.split(splitter):
            s.strip()
            coords.append(float(s))
        dataType = 'vector'
        # updates user output and copy of user output
        initialPt = np.array([0, 0, 0])
        newOutputBox = [box.id, dataType, [initialPt]]
        newOutputBox[2].append(np.array([coords[0], coords[1], coords[2]]))
        app.userOutputs.append(newOutputBox)
        app.originalUserOutputs.append(copy.deepcopy(newOutputBox))
    elif box.hasDrawableVectorField():
        print('added vector field')
        eqIndex = input.find('=')
        vector = input[eqIndex+1:]
        dataType = 'vector field'
        X = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        Y = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        Z = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        app.mesh = meshgrid(X, Y, Z)
        vectorFieldPts = []
        for point in app.mesh:
            x, y, z = float(point[0]), float(point[1]), float(point[2])
            vectorFieldPts.append(evalVector(vector, x, y, z))
        # finds new vector points based on mesh
        newOutputBox = [box.id, dataType, vectorFieldPts]
        app.userOutputs.append(newOutputBox)
        app.originalUserOutputs.append(copy.deepcopy(newOutputBox))
    else:
        box.input = 'Incorrect formatting. Try again.'

# applies rotation matrix to points (x, y or z)
def rotatePoints(app, pointList, matrix):
    # Rotates the points in the list within app.userOutputs, keeping index and dataType unaltered
    if pointList == app.userOutputs:
        for i in range(len(pointList)):
            outputList = pointList[i][2]
            for j in range(len(outputList)):
                point = outputList[j].reshape((3,1))
                rotatedPoint = np.dot(matrix, point)
                outputList[j] = rotatedPoint.flatten()
    # Rotates a direct list (all lists except app.userOutputs)
    else:
        for i in range(len(pointList)):
            point = pointList[i].reshape((3,1))
            rotatedPoint = np.dot(matrix, point)
            pointList[i] = rotatedPoint.flatten()

def drawLines(app, pointList):
        
        if pointList == app.axesPoints:
            color = 'darkSlateBlue'
            thicc = 2
            arrows = True
            scale = app.scale
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
            drawLine(x1, y1, x2, y2, fill = color, lineWidth = thicc, arrowStart = arrows, arrowEnd = arrows) # type: ignore
            if labels:
                x1 += 10
                y1 += 10
                label = 'X' if i == 0 else ('Y' if i == 2 else 'Z')
                drawLabel(label, x1, y1, align = 'center', bold = True, size = 20) # type: ignore

# projects all 3D points in a pointList into 2D points, stored in projectedPointList
def projectPoints(app, pointList, projectedPointList):

    # Projects the points in each list for app.userOutputs, keeping index and data type unaltered
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

def removeBox(app, box):
    # removes input box
    removedBoxID = box.id - 1
    app.userInputs.pop(removedBoxID)
    # removes output 
    for output in app.originalUserOutputs:
        # checks if the output box has the same ID as the input box
        print(output[0])
        if output[0] == box.id:
            outputToRemove = output
        elif output[0] > box.id:
            print('updated output')
            output[0] -= 1
    app.originalUserOutputs.remove(outputToRemove)
    # updates boxes below removed box
    for i in range(removedBoxID, len(app.userInputs)):
        box = app.userInputs[i]
        box.id -= 1
        # shifts boxes upwards (800/12 = box.height)
        box.y -= 800/12 
        box.crossY -= 800/12


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

# returns a list of all the points created by combining values of X, Y, and Z
def meshgrid(X, Y, Z):
    mesh = []
    for x in X:
        for y in Y:
            for z in Z:
                mesh.append(np.array([x, y, z]))
    return mesh

# solves for the value of a vector [a, b, c] at point (x, y, z)
# output: point where the vector ends
def evalVector(v, x, y, z):

    # find components a, b, and c of vector
    splitter = ',' if ',' in v else ' '
    vectorStripped = v.strip()[1:-1]
    vectorScale = 0.1
    components = vectorStripped.split(splitter)
    a = components[0].strip()
    b = components[1].strip()
    c = components[2].strip()
    print(a, b, c)
    # checks if vector is all constants (otherwise solves expression)
    # if str(abs(int(a))) in string.digits and str(abs(int(b))) in string.digits and str(abs(int(b))) in string.digits:
    #         newX, newY, newZ = float(a), float(b), float(c)
    # else:
    newX = evalExpression(a, x, y, z)
    newY = evalExpression(b, x, y, z)
    newZ = evalExpression(c, x, y, z)
    # add starting point to new ending point to get vector
    return np.array([x + newX*vectorScale, y + newY*vectorScale, z + newZ*vectorScale])

