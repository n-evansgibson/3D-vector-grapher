from cmu_graphics import * 
import string

def onAppStart(app):
    app.input = ''
    app.inputList = []
    app.boxWidth = app.width/4
    app.boxHeight = app.height/12
    app.x = app.width/2 - app.boxWidth/2
    app.y = app.height/2 - app.boxHeight/2
    app.crossX = app.x + 15*app.boxWidth/16
    app.crossY = app.y + 1*app.boxHeight/4
    app.cursorPos = app.width/2 - app.boxWidth/2 + 10
    app.cursor = True
    app.time = 0

def redrawAll(app):
    drawRect(app.width/2 - app.boxWidth/2, app.height/2 - app.boxHeight/2, app.boxWidth, app.boxHeight, fill = None, 
             border = 'black', borderWidth = 2)
    drawLabel(f'{app.input}', app.width/2 - app.boxWidth/2 + 5, app.height/2, align = 'left', size = 12)
    drawCircle(app.crossX, app.crossY, 5)

def onStep(app):
    app.time += 1
    if app.time % 15 == 0:
        app.cursor = not app.cursor

def onKeyPress(app, key):
    if key in string.printable:
        app.input = app.input + key
        app.cursorPos += 7
    elif key == 'space':
        app.input = app.input + ' '
        app.cursorPos += 7
    elif key == 'backspace':
        app.input = app.input[:-1]
        app.cursorPos -= 7
    elif key == 'enter':
        app.inputList.append(app.input)
        app.input = ''
        app.cursorPos = app.width/2 - app.boxWidth/2 + 10
        print('current list: ', app.inputList)

runApp(width = 1200, height = 800)