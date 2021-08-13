# Name: Saumya Bhandarkar (ssbhanda)
# Assignment: TP3
# Description: holds all the information for the sandbox mode

from cmu_112_graphics import *
import basic_graphics, math, random, time
from tp_classes import *
from appStarted import *

# handles all the keypresses in the sandbox
def sandboxKeypresses(app, event):
    for item in app.objects:
        if item.selected and isinstance(item, Ball):
            if event.key == 'g':
                item.lockGraph = not item.lockGraph
    if event.key == 's':
        doSandboxStep(app)
    elif event.key == 'r':
        app.objects = []
        app.buttonIndex = None
    elif event.key == 'l':
        for item in app.objects:
            if isinstance(item, Ball):
                item.loseKE(1)
                item.recalculate(app)
    elif event.key == 'c':
        changeItem(app)
    switchRampOrientation(app, event)

# switches the ramp orientation from left to right with keypresses when selected
def switchRampOrientation(app, event):
    for ramp in app.objects:
        if isinstance(ramp, Ramp):
            if ramp.selected and event.key == 'Right' or event.key == 'Left':
                ramp.orientation = not ramp.orientation

# handles mouseclicks and places the appropriate items
def sandboxMouseClicks(app, event):
    if app.buttonIndex == 0:
        placeRamp(app, event)
        app.buttonIndex = None
    elif app.buttonIndex == 1:
        placeBall(app, event)
        app.buttonIndex = None
    elif app.buttonIndex == 2:
        placeSpring(app, event)
        app.buttonIndex = None
    elif app.buttonIndex == 3:
        placeBlock(app, event)
        app.buttonIndex = None
    elif app.buttonIndex == 4:
        placeFriction(app, event)
        app.buttonIndex = None
    if app.buttonIndex != None:
        app.sandbox[app.buttonIndex] = False
    for i in range(len(app.sandbox)):
        button = app.buttonCoordinates[i]
        if clickInButton(event.x, event.y, button):
            for j in range(len(app.sandbox)):
                app.sandbox[j] = False if j != i else True
            app.buttonIndex = i

# changes item values for ramps and balls
def changeItem(app):
    item = app.objects[-1]
    if isinstance(item, Ball):
        radius = float(app.getUserInput('Enter a new radius: '))
        mass = float(app.getUserInput('Enter a new mass: '))
        coeff = float(app.getUserInput('Enter a coeff: '))
        item.radius, item.mass = radius * 5, mass
        item.coeffOfRestitution = coeff
    elif isinstance(item, Ramp):
        angle = float(app.getUserInput('Enter a new angle: ')) 
        item.angle = angle * math.pi/180
        item.height = float(app.getUserInput('Enter a new height: ')) * 50

# places ball at event.x, event.y
def placeBall(app, event):
    x, y = event.x, event.y
    if not pointInGrid(app, x, y):
        return
    radius = 20
    app.objects.append(Ball(x, y, mass=20, radius=radius, app=app))

# places ramp in the selected row, col
def placeRamp(app, event):
    row, col = getCell(app, event.x, event.y)
    if row != -1:
        app.objects.append(Ramp(row, col, height=200, angle=45))

# places friction in the grid
def placeFriction(app, event):
    x, y = event.x, event.y
    if not pointInGrid(app, x, y):
        return
    app.objects.append(Friction())
    row, col = getCell(app, x, y)
    app.objects[-1].row, app.objects[-1].col = row, col
    app.objects[-1].distance = 150

# moves all balls onscreen and checks for collisions, called by timerFired
def doSandboxStep(app):
    for item in app.objects:
        if isinstance(item, Ball):
            # move the ball per its accel + velocity and recalculate energy values
            item.move()
            item.recalculate(app)
            # check if ball collides with anything + adjust values as necessary
            checkBallAndRamp(app, item)
            if not item.onRamp:
                checkBallAndSidesOfRamp(app, item)
            checkBallAndSpring(app, item)
            checkBallAndBlock(app, item)
            checkBallAndFriction(app, item)
            checkBallAndGround(app, item)
            checkBallAndSides(app, item)
    sandboxCheckBalls(app)

# checks if ball interacts with friction
def checkBallAndFriction(app, ball):
    for item in app.objects:
        if isinstance(item, Friction):
            x0, y0, m, n = getCellBounds(app, item.row, item.col)
            x1, y1 = x0 + item.distance, y0 + 50
            if ball.cx + ball.radius > x1 and ball.onGround:
                if x0 <= ball.cx - ball.radius <= x1: # hits the right
                    if y1 > ball.cy > y0:
                        ball.cx = x1 + ball.radius
                        ball.velocityX = -1 * ball.velocityX
            elif ball.cx - ball.radius < x0 and ball.onGround:
                if x0 <= ball.cx + ball.radius <= x1: # hits the left
                    if y1 > ball.cy > y0:
                        ball.cx = x0 - ball.radius
                        ball.velocityX = -1 * ball.velocityX
            elif ball.cy - ball.radius < y0 and not ball.onGround:
                if y1 >= ball.cy + ball.radius >= y0: # hits the top
                    if x0 < ball.cx < x1:
                        ball.cy = y0 - ball.radius
                        ball.velocityY = 0
                        friction = item.coeff/(item.distance * 50)
                        ball.loseKE(friction)
            elif ball.cy + ball.radius > y1 and not ball.onGround:
                if y1 >= ball.cy - ball.radius >= y0: # hits the bottom
                    if x0 < ball.cx < x1:
                        ball.cy = y1 + ball.radius
                        ball.velocityY *= -1 * ball.coeffOfRestitution

# checks if ball lands on ramp, called by doStep
def checkBallAndRamp(app, ball):
    result = ballCollidesWithRamp(app, ball)
    if result != None:
        ramp, (px, py) = result[0:2]
        angle = ramp.angle
        if ramp.orientation:
            ball.cx = px + ball.radius * math.cos(math.pi/2 - angle)
            ball.cy = py - ball.radius * math.sin(math.pi/2 - angle)
            ball.accelX = app.gravity * math.cos(angle)
        else:
            ball.cx = px - ball.radius * math.cos(math.pi/2 - angle)
            ball.cy = py - ball.radius * math.sin(math.pi/2 - angle)
            ball.accelX = - 1 * app.gravity * math.cos(angle)
        ball.accelY = (app.gravity) * math.sin(angle)
        ball.onRamp = True
        ball.recalculate(app)
    else: ball.onRamp = False

# adjusts graph values
def checkGraphTime(app, ball):
    if Ball.end - ball.start > 5:
        for ballCoords in Ball.balls:
            if ball == ballCoords[0]: # in the correct list
                ballCoords = [ballCoords[0]] + ballCoords[100:]

# checks if ball bumps into sides of ramp, called by doStep
def checkBallAndSidesOfRamp(app, ball):
    for item in app.objects:
        if isinstance(item, Ramp):
            x0, y0, x1, y1, x2, y2 = getRampPoints(app, item)
            if ball.cx < x0: # hits LH
                if ball.cx - ball.radius < x0 and item.orientation:
                    if ball.cx + ball.radius >= x0 and y1 > ball.cy > y2:
                        ball.cx = x0 - ball.radius
                        ball.velocityX *= -1
            if ball.cx > x1: # hits RH
                if ball.cx + ball.radius > x1 and not item.orientation:
                    if ball.cx - ball.radius <= x1 and y1 > ball.cy > y2:
                        ball.cx = x1 + ball.radius
                        ball.velocityX *= -1
            if ball.cy + ball.radius > y0: # hits the bottom
                if y1 <= ball.cy - ball.radius <= y0 and item.orientation:
                    if x0 <= ball.cx <= x1:
                        ball.cy = y0 + ball.radius
                        ball.velocityY = abs(ball.velocityY) 
                elif y2 <= ball.cy - ball.radius <= y0 and not item.orientation:
                    if x0 <= ball.cx <= x1:
                        ball.cy = y0 + ball.radius
                        ball.velocityY = abs(ball.velocityY)

# checks ball collision with spring
def checkBallAndSpring(app, ball):
    for item in app.objects:
        if isinstance(item, Spring):
            m, n, x1, y1 = getCellBounds(app, item.row, item.col)
            length = item.initLength
            height = 50
            x0, y0 = x1 - length, y1 - height
            if ball.cx - ball.radius < x0:
                if x0 <= ball.cx + ball.radius <= x1: # hits the left
                    if y1 > ball.cy > y0:
                        if not item.isCompressed:
                            ball.compressSpring(item, app)
                        else:
                            item.decompressSpring(ball, app)
                        ball.cx = x0 - ball.radius
        checkBallAroundSpring(app, ball)

# checks if ball collides with sides of spring
def checkBallAroundSpring(app, ball):
    for item in app.objects:
        if isinstance(item, Spring):
            m, n, x1, y1 = getCellBounds(app, item.row, item.col)
            length = item.initLength
            height = 50
            x0, y0 = x1 - length, y1 - height
            if ball.cx + ball.radius > x1:
                if x0 <= ball.cx - ball.radius <= x1: # hits the right
                    if y1 > ball.cy > y0:
                        ball.cx = x1 + ball.radius
                        ball.velocityX = -1 * ball.velocityX
            elif ball.cy - ball.radius < y0:
                if y1 >= ball.cy + ball.radius >= y0: # hits the top
                    if x0 < ball.cx < x1:
                        ball.cy = y0 - ball.radius
                        ball.velocityY *= -1 * ball.coeffOfRestitution

# checks if ball collides with block
def checkBallAndBlock(app, ball):
    for item in app.objects:
        if isinstance(item, Block):
            x0, y0 = item.x, item.y
            length, height = item.length, item.height
            x1, y1 = x0 + length, y0 + height
            if ball.cx + ball.radius > x1 and ball.onGround:
                if x0 <= ball.cx - ball.radius <= x1: # hits the right
                    if y1 > ball.cy > y0:
                        ball.cx = x1 + ball.radius
                        ball.velocityX = -1 * ball.velocityX
            elif ball.cx - ball.radius < x0:
                if x0 <= ball.cx + ball.radius <= x1 and ball.onGround: # left
                    if y1 > ball.cy > y0:
                        ball.cx = x0 - ball.radius
                        ball.velocityX = -1 * ball.velocityX
            elif ball.cy - ball.radius < y0:
                if y1 >= ball.cy + ball.radius >= y0: # hits the top
                    if x0 < ball.cx < x1:
                        ball.cy = y0 - ball.radius
                        ball.velocityY *= -1 * ball.coeffOfRestitution
            elif ball.cy + ball.radius > y1:
                if y1 >= ball.cy - ball.radius >= y0: # hits the bottom
                    if x0 < ball.cx < x1:
                        ball.cy = y1 + ball.radius
                        ball.velocityY *= -1 * ball.coeffOfRestitution   

# returns point of collision if collides, else None
def ballCollidesWithRamp(app, ball):
    for item in app.objects:
        if isinstance(item, Ramp):
            x0, y0, x1, y1, x2, y2 = getRampPoints(app, item)
            if (ballInRamp(app, ball, item) and 
               ballOnCorrectSide(app, ball, item)):
                if round(ball.velocityX) == 0:
                    if item.orientation: # right angle is on the left
                        newX, newY = pointOnLine((x1, y1), (x2, y2), 
                                                (ball.cx, ball.cy))
                    else: # right angle is on the right
                        newX, newY = pointOnLine((x0, y0), (x2, y2), 
                                                (ball.cx, ball.cy))
                    return item, (newX, newY)
                else:
                    m1 = ball.velocityY/ball.velocityX
                    b1 = ball.cy - m1 * ball.cx
                    if item.orientation:
                        m2 = (y2 - y1)/(x2 - x1)
                    else:
                        m2 = (y2 - y0)/(x2 - x0)
                    b2 = y2 - m2 * x2
                    if m1 != m2:
                        x = (b1 - b2)/(m2 - m1)
                        y = m2 * x + b2
                        newX, newY = x, y
                        return item, (newX, newY)
    return None

# checks if ball is on the right side of the ramp (the vertical side)
def ballOnCorrectSide(app, ball, ramp):
    x0, y0, x1, y1, x2, y2 = getRampPoints(app, ramp)
    if ramp.orientation: # right angle on the left side
        return ball.cx > x0
    else: # right angle on the right side
        return ball.cx < x1

# returns True if the ball has moved into the ramp, so the main fx can reset pos
def ballInRamp(app, ball, ramp):
    x0, y0, x1, y1, x2, y2 = getRampPoints(app, ramp)
    if x0 <= ball.cx <= x1 and y1 >= ball.cy >= y2:
        if ramp.orientation: # right angle on the left, regular orientation
            p1, p2 = pointOnLine((x1, y1), (x2, y2), (ball.cx, ball.cy))
        else: # right angle on the right, opposite orientation
            p1, p2 = pointOnLine((x0, y0), (x2, y2), (ball.cx, ball.cy))
        if distance(ball.cx, ball.cy, p1, p2) <= ball.radius:
            return True
        elif pointInRamp(app, ramp, ball.cx, ball.cy, ball.radius):
            return True
        elif ballIntersectsRamp(app, ramp, ball):
            return True
    return False

# based on math algorithm from:
# https://doubleroot.in/lessons/circle/intersection-line-circle-1/
def ballIntersectsRamp(app, ramp, ball):
    x0, y0, x1, y1, x2, y2 = getRampPoints(app, ramp)
    if ramp.orientation:
        m = (y2 - y1)/(x2 - x1)
    else:
        m = (y2 - y0)/(x2 - x0)
    b = y2 - m * x2
    a = (1 + m**2)
    b = (1 + m**2) * (-2) * ball.cx + 2 * (b - ball.cy) * m
    c = (1 + m**2) * ball.cx ** 2 + (b - ball.cy)**2 + ball.radius**2
    discriminant = b**2 - 4*a*c
    if discriminant >= 0:
        return True
    else:
        return False

# draws all objects on screen
def drawObjects(app, canvas):
    for item in app.objects:
        if item.selected:
            width = 3
            outline = 'green yellow'
        else:
            width = 1
            outline = 'black'

        if isinstance(item, Ball):
           drawSandboxBall(app, canvas, item, width, outline)
        
        elif isinstance(item, Ramp):
            drawRamp(app, canvas, item, width, outline)

        elif isinstance(item, Spring):
            drawSpring(app, canvas, item, width, outline)

        elif isinstance(item, Block):
            x, y = item.x, item.y
            length, height = item.length, item.height
            canvas.create_rectangle(x, y, x + length, y + height, fill='orange',
                                                   width=width, outline=outline)
        
        elif isinstance(item, Friction):
            row, col = item.row, item.col
            distance = item.distance
            x0, y0, m, n = getCellBounds(app, row, col)
            x1 = x0 + distance
            y1 = y0 + 50
            canvas.create_rectangle(x0, y0, x1, y1, fill='gray', width=width,
                                                                outline=outline)

# draws spring
def drawSpring(app, canvas, item, width, outline):
    m, n, x1, y1 = getCellBounds(app, item.row, item.col)
    length = item.length
    height = 50
    x0, y0 = x1 - length, y1 - height
    width = length//10
    for i in range(1, 6):
        mini = x0 + width
        canvas.create_rectangle(x0, y0, mini, y1, fill = 'purple')
        newX0 = x0 + 2 * width
        if i % 2 == 1:
            canvas.create_rectangle(mini, y0, newX0, y0 + height//5, 
                                                                fill = 'purple')
        else:
            canvas.create_rectangle(mini, y1, newX0, y1 - height//5,
                                                                fill = 'purple')
        x0 = newX0
    

# draws ball
def drawSandboxBall(app, canvas, item, width, outline):
    cx, cy, r = item.cx, item.cy, item.radius
    if item.onGround and not 0 < item.velocityY < app.gravity:
        # animates the ball squishing as a fx of the coeff of resti
        squash = r - r * item.coeffOfRestitution
        canvas.create_oval(cx - r, cy - squash, cx+r, cy+r, fill='cyan',
                                            width=width, outline=outline)
        canvas.create_text(cx, (cy - squash + cy + r)//2, 
                                                    text = f'{item.mass}')
    else:
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill='cyan',
                                            width=width, outline=outline)
        canvas.create_text(cx, cy, text = f'{item.mass}')
    displayGraph(app, canvas, item)

# draws ramp
def drawRamp(app, canvas, item, width, outline):
    x0, y0, x1, y1, x2, y2 = getRampPoints(app, item)
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, fill='red',
                                            width=width, outline=outline)

# selects item if it's being dragged and updates its location
def sandboxMouseDrags(app, event):
    for item in app.objects:
        if isinstance(item, Ball):
            if pointInBall(app, item, event.x, event.y):
                item.selected = True
            if item.selected:
                item.cx, item.cy = event.x, event.y
                item.velocityX, item.velocityY = 0, 0
                item.recalculate(app)
        elif isinstance(item, Ramp):
            if pointInRamp(app, item, event.x, event.y):
                item.selected = True
            if item.selected:
                row, col = getCell(app, event.x, event.y)
                item.row, item.col = row, col
        elif isinstance(item, Block):
            if pointInBlock(app, item, event.x, event.y):
                item.selected = True
            if item.selected:
                row, col = getCell(app, event.x, event.y)
                x, y, m, n = getCellBounds(app, row, col)
                item.x, item.y = x, y
        elif isinstance(item, Spring):
            if pointInSpring(app, item, event.x, event.y):
                item.selected = True
            if item.selected:
                row, col = getCell(app, event.x, event.y)
                item.row, item.col = row, col
        elif isinstance(item, Friction):
            if pointInFriction(app, item, event.x, event.y):
                item.selected = True
            if item.selected:
                row, col = getCell(app, event.x, event.y)
                item.row, item.col = row, col
        if item.selected:
            app.isPaused = True

# returns if a point is in the frictional surface
def pointInFriction(app, item, x, y):
    x0, y0, m, n = getCellBounds(app, item.row, item.col)
    x1, y1 = x0 + item.distance, y0 + 50
    if x0 <= x <= x1 and y0 <= y <= y1:
        return True
    return False

# returns if the point is in the spring
def pointInSpring(app, item, x, y):
    m, n, x1, y1 = getCellBounds(app, item.row, item.col)
    length = item.initLength
    height = 50
    x0, y0 = x1 - length, y1 - height
    if x0 <= x <= x1 and y0 <= y <= y1:
        return True
    return False

# shows the graph and updates values
def displayGraph(app, canvas, ball):
    checkGraphTime(app, ball)
    drawVelocityGraph(app, canvas, ball)

# dynamically displays velocity data if locked onscreen or the ball is selected
def drawVelocityGraph(app, canvas, ball):
    if not ball.selected and not ball.lockGraph:
        return # only display graph if locked onscreen or ball selected
    window = 200
    x0, y0 = 2 * app.width//4, app.height//6
    x1, y1 = x0 + window, y0 + window
    acc = 15 # so the points on graph aren't exactly touching the edges
    for L in Ball.balls:
        if L[0] == ball:
            canvas.create_rectangle(x0 - acc, y0 - acc, x1 + acc, y1 + acc, 
                                                            fill = 'lightblue1')
            canvas.create_line(x0, y1, x1, y1, width = 2)
            canvas.create_line(x0, y1, x0, y0, width = 2)
            canvas.create_text((x0 + x1)//2, y1 + acc//2, text = 'Time')
            canvas.create_text(x0 - acc//2, (y0 + y1)//2, text = 'Velocity',
                                                                     angle = 90)
            maxT = Ball.end - ball.start
            maxV = max(L[1:])
            scaleX = window//(len(L) - 1)
            scaleY = window//maxV
            x = x0
            y0 = y0 + window
            for v in L[1:]: # velocity
                y = y1 - v/maxV * window
                canvas.create_line(x0, y0, x, y, width = 2, fill = 'red')
                x0, y0 = x, y
                x += scaleX

# deselects item when mouse is released and unpauses the app
def sandboxMouseReleased(app, event):
    for item in app.objects:
        if item.selected:
            app.isPaused = False
        item.selected = False

# places spring in row, col
def placeSpring(app, event):
    if not pointInGrid(app, event.x, event.y):
        return
    row, col = getCell(app, event.x, event.y)
    app.objects.append(Spring(row, col))

# places block in row, col
def placeBlock(app, event):
    if not pointInGrid(app, event.x, event.y):
        return
    row, col = getCell(app, event.x, event.y)
    x, y, m, n = getCellBounds(app, row, col)
    app.objects.append(Block(x, y))
    app.objects[-1].height = 50

# returns if a point is in a block
def pointInBlock(app, block, x, y):
    x1, y1 = block.x, block.y
    length, height = block.length, block.height
    if x1 <= x <= x1 + length and y1 <= y <= y1 + height:
        return True
    return False

# I used equations from these websites for the velocities after the collision:
# http://hyperphysics.phy-astr.gsu.edu/hbase/elacol2.html
def sandboxCheckBalls(app):
    for ball1 in app.objects:
        for ball2 in app.objects:
            if isinstance(ball1, Ball) and (isinstance(ball2, Ball) and 
                                                                ball1 != ball2):
                if not ball1.onGround or not ball2.onGround:
                    pass # used pass here to avoid long if statements
                if ball1.cx > ball2.cx:
                    ball1, ball2 = ball2, ball1
                if (distance(ball1.cx, ball1.cy, ball2.cx, ball2.cy) <= 
                                                    ball1.radius + ball2.radius):
                    m1, m2 = ball1.mass, ball2.mass
                    v1, v2 = ball1.velocityX, ball2.velocityX
                    nextV1 = (2 * m2 * v2)/(m1 + m2) + ((m1 - m2) * v1)/(m1 + m2)
                    nextV2 = (2 * m1 * v1)/(m1 + m2) - ((m1 - m2) * v2)/(m1 + m2)
                    if m2 * v2 >= m1 * v1:
                        ball1.cx = ball2.cx - ball2.radius - ball1.radius
                    else:
                        ball2.cx = ball1.cx + ball1.radius + ball2.radius
                    ball1.velocityX = nextV1
                    ball2.velocityX = nextV2