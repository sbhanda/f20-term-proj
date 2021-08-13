# Name: Saumya Bhandarkar (ssbhanda)
# Assignment: TP3
# Description: holds all functions for experiment 2

from appStarted import *
from tp_classes import *

# handles all the mouse clicks in experiment 2, buttons and setting values
def exp2MouseClicks(app, event):
    app.exp2[4] = False # turn of show vectors if you click anywhere
    for i in range(app.numButtons[app.mode]):
        button = app.buttonCoordinates[i]
        if clickInButton(event.x, event.y, button):
            for j in range(len(app.exp2)):
                app.exp2[j] = False if j != i else True
    for j in [0, 1]: # for the 2 block buttons
        if app.exp2[j]:
            if app.exp2Blocks[j] == None:
                mass = int(app.getUserInput('Enter a mass (in kg): '))
                x, y = (app.width//2 - 50) + 353 * j, (app.height//3) + 150 * j
                app.exp2Blocks[j] = Block(x, y, mass=mass)
                if j == 0:
                    app.exp2Blocks[j].onTable = True
            else:
                mass = int(app.getUserInput('Enter a new mass (in kg): '))
                app.exp2Blocks[j].mass = mass
            app.exp2[j] = False
    if app.exp2[3]: # friction
        app.mu = float(app.getUserInput('Enter a coefficient of friction' + 
                                        ' between 0 and 1'))
        app.exp2[3] = False

# handles resetting the app
def exp2Keypresses(app, event):
    if event.key == 'r':
        app.exp2Blocks = [None, None]
        app.exp2 = [False] * app.numButtons[app.mode]
        app.drawException = False

# draws the exp2 equations once the blocks are defined
def drawExp2Equations(app, canvas):
    if None not in app.exp2Blocks:
        if not app.exp2[2]:
            b1, b2 = app.exp2Blocks[0], app.exp2Blocks[1]
            canvas.create_rectangle(app.width//2 - 150, 
                            app.height - app.margin - 200,
                            app.width//2 + 150, app.height - app.margin, 
                            fill='lightgreen')
            accel = round(b1.accel, 2)
            if app.mu == 0:
                canvas.create_text(app.width//2 - 25, 
                                   app.height - app.margin - 100,
                        text = f'''\
                        Forces on a Pulley:
                        Block 1 = {b1.mass}, Block 2 = {b2.mass}
                        Acceleration of both blocks: (m1 + m2) * a
                        ({b1.mass} + {b2.mass}) * a = {b2.mass} * g
                        a = {b2.mass}/({b1.mass} + {b2.mass})''', 
                        justify = 'center')
            else:
                canvas.create_text(app.width//2 - 25, 
                                   app.height - app.margin - 100,
                        text = f'''\
                        Forces on a Pulley (With Friction):
                        Block 1 = {b1.mass}, Block 2 = {b2.mass}
                        Acceleration of the system: (m1 + m2) * a
                        Friction = {app.mu}
                        ({b1.mass} + {b2.mass}) * a = {b2.mass} * g - {app.mu} * {b1.mass} * g
                        a = ({b2.mass} - {app.mu}*{b1.mass}) * g / ({b1.mass} + {b2.mass})''', 
                        justify = 'center')

# draws the exp2 blocks once they are defined and draws the pulley between
# them when both blocks are visible
def drawExp2Blocks(app, canvas):
    coords = []
    for block in app.exp2Blocks:
        if block != None:
            x0, y0 = block.x, block.y
            if block.onTable:
                x1, y1 = x0 + block.length, y0 + block.height
            else:
                x1, y1 = x0 + block.height, y0 + block.length
            canvas.create_rectangle(x0, y0, x1, y1, fill = 'brown')
            coords.extend([x0, y0, x1, y1])
            cx, cy = (x0 + x1)/2, (y0 + y1)/2
            width = 10
            canvas.create_rectangle(cx - width, cy - width, cx + width, 
                                                     cy + width, fill = 'white')
            canvas.create_text(cx, cy, text = f'{block.mass}')
    if None not in app.exp2Blocks:
        canvas.create_line(coords[2], (coords[1] + coords[3])/2,
                        (coords[4] + coords[6])/2, (coords[1] + coords[3])/2,
                        width = 4)
        canvas.create_line((coords[4] + coords[6])/2, coords[5],
                          (coords[4] + coords[6])/2, (coords[1] + coords[3])/2,
                        width = 4)

# animates experiment 2 when the GO button is clicked
def doExperiment2(app):
    if app.exp2[2]:
        calculateAccel(app)
        moveBlocks(app)

# calculates the acceleration of the block system
def calculateAccel(app):
    if None not in app.exp2Blocks:
        block1, block2 = app.exp2Blocks[0], app.exp2Blocks[1]
        # block1 on table, block2 is hanging mass
        gravity = 9.8
        accel = block2.mass/(block1.mass + block2.mass) * gravity
        accel -= app.mu * gravity * block1.mass / (block1.mass + block2.mass)
        accel /= 2 # scaling it to fit our model
        if accel < 0 or round(accel) == 0:
            accel = 0
            app.exp2[2] = False
            app.drawException = True
        block1.accel, block2.accel = accel, accel

# moves blocks as per the system's acceleration
def moveBlocks(app):
    for block in app.exp2Blocks:
        if block != None:
            if block.onTable: # accel is horizontal
                block.velocityX += block.accel
                block.x += block.velocityX
            else: # accel is vertical
                block.velocityY += block.accel
                block.y += block.velocityY
                if block.y + block.length >= app.height - app.margin:
                    block.y = app.height - app.margin - block.length
                    app.exp2[2] = False

# draws friction visually
def drawExp2Friction(app, canvas):
    if app.mu > 0:
        canvas.create_rectangle(app.width//2 - 300, app.height//3 + 50,
                                app.width//2 + 300, app.height//3 + 100,
                                fill = 'gray')

# draws the table in experiment 2
def drawExp2Table(app, canvas):
    table = Table(app)
    x0, y0, x1, y1 = table.x0, table.y0, table.x1, table.y1
    canvas.create_rectangle(x0, y0, x1, y1, fill = 'pink')

# draws exception if the friction value is too great for the system
def drawExp2Exception(app, canvas):
    if app.drawException:
        x, y = app.width//2, app.height//2
        canvas.create_rectangle(x - 100, y - 50, x + 100, y + 50, fill = 'cyan')
        canvas.create_text(x, y, 
            text = '''\
                    Uh-oh! Looks like your friction/mass value
                    is too high for the system to move! Try
                    picking another value, or pressing "r"
                    to restart''', justify = 'center')

# draws exp2 force vectors when the button is pressed
def drawExp2ForceVectors(app, canvas):
    if None not in app.exp2Blocks and app.exp2[4]:
        block1, block2 = app.exp2Blocks # block1 on table, block2 hanging
        drawNormalVector(app, canvas, block1)
        drawGravityVector(app, canvas, block1)
        drawGravityVector(app, canvas, block2)
        drawTensionVectors(app, canvas, block1, block2)
        if app.mu != 0:
            drawFrictionVector(app, canvas, block1)

# draws the normal vector
def drawNormalVector(app, canvas, block):
    r = 15
    theta1, theta2 = 5 * math.pi/4, 7 * math.pi/4
    x, y = block.x, block.y # center of mass
    length, height = block.length, block.height
    cx, cy = x + length//2, y + height//2
    vectorLen = block.mass * 10
    cx1, cy1 = cx, cy - vectorLen
    fill = 'red'
    canvas.create_line(cx, cy, cx1, cy1, width = 3, fill = fill)
    x0, y0 = cx1 + r * math.cos(theta1), cy1 - r * math.sin(theta1)
    x1, y1 = cx1 + r * math.cos(theta2), cy1 - r * math.sin(theta2)
    canvas.create_line(cx1, cy1, x0, y0, width = 3, fill = fill)
    canvas.create_line(cx1, cy1, x1, y1, width = 3, fill = fill)

# draws the gravity vectors
def drawGravityVector(app, canvas, block):
    r = 15
    theta1, theta2 = math.pi/4, 3 * math.pi/4
    x, y = block.x, block.y # center of mass
    length, height = block.length, block.height
    if not block.onTable:
        length, height = height, length
    cx, cy = x + length//2, y + height//2
    vectorLen = block.mass * 10
    cx1, cy1 = cx, cy + vectorLen
    fill = 'blue'
    canvas.create_line(cx, cy, cx1, cy1, width = 3, fill = fill)
    x0, y0 = cx1 + r * math.cos(theta1), cy1 - r * math.sin(theta1)
    x1, y1 = cx1 + r * math.cos(theta2), cy1 - r * math.sin(theta2)
    canvas.create_line(cx1, cy1, x0, y0, width = 3, fill = fill)
    canvas.create_line(cx1, cy1, x1, y1, width = 3, fill = fill)

# draws equal length tension vectors
def drawTensionVectors(app, canvas, block1, block2):
    r = 15
    theta1, theta2 = 3 * math.pi/4, 5 * math.pi/4
    x, y = block1.x, block1.y # center of mass
    length, height = block1.length, block1.height
    cx, cy = x + length//2, y + height//2
    vectorLen = 50
    cx1, cy1 = cx + vectorLen, cy
    fill = 'lime green'
    canvas.create_line(cx, cy, cx1, cy1, width = 3, fill = fill)
    x0, y0 = cx1 + r * math.cos(theta1), cy1 - r * math.sin(theta1)
    x1, y1 = cx1 + r * math.cos(theta2), cy1 - r * math.sin(theta2)
    canvas.create_line(cx1, cy1, x0, y0, width = 3, fill = fill)
    canvas.create_line(cx1, cy1, x1, y1, width = 3, fill = fill)
    # hanging tension vector
    r = 15
    theta1, theta2 = 5 * math.pi/4, 7 * math.pi/4
    x, y = block2.x, block2.y # center of mass
    length, height = block2.height, block2.length
    cx, cy = x + length//2, y + height//2
    vectorLen = 50
    cx1, cy1 = cx, cy - vectorLen
    fill = 'lime green'
    canvas.create_line(cx, cy, cx1, cy1, width = 3, fill = fill)
    x0, y0 = cx1 + r * math.cos(theta1), cy1 - r * math.sin(theta1)
    x1, y1 = cx1 + r * math.cos(theta2), cy1 - r * math.sin(theta2)
    canvas.create_line(cx1, cy1, x0, y0, width = 3, fill = fill)
    canvas.create_line(cx1, cy1, x1, y1, width = 3, fill = fill)

# draws friction vector, scaled by app.mu
def drawFrictionVector(app, canvas, block):
    r = 15
    theta1, theta2 = math.pi/4, 7 * math.pi/4
    x, y = block.x, block.y # center of mass
    length, height = block.length, block.height
    cx, cy = x + length//2, y + height//2
    vectorLen = block.mass * 100 * app.mu
    cx1, cy1 = cx - vectorLen, cy
    fill = 'magenta'
    canvas.create_line(cx, cy, cx1, cy1, width = 3, fill = fill)
    x0, y0 = cx1 + r * math.cos(theta1), cy1 - r * math.sin(theta1)
    x1, y1 = cx1 + r * math.cos(theta2), cy1 - r * math.sin(theta2)
    canvas.create_line(cx1, cy1, x0, y0, width = 3, fill = fill)
    canvas.create_line(cx1, cy1, x1, y1, width = 3, fill = fill)

# draws the entire experiment 2
def drawExp2(app, canvas):
    drawExp2Table(app, canvas)
    drawExp2Blocks(app, canvas)
    drawExp2Friction(app, canvas)
    drawExp2Exception(app, canvas)
    drawExp2ForceVectors(app, canvas)