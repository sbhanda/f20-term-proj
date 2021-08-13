# Name: Saumya Bhandarkar (ssbhanda)
# Assignment: TP3
# Description: holds all functions for experiment 1

from appStarted import *
import time

# I used equations from these websites for the velocities after the collision:
# http://hyperphysics.phy-astr.gsu.edu/hbase/elacol2.html
# http://hyperphysics.phy-astr.gsu.edu/hbase/inecol.html
def exp1CheckBalls(app):
    ball1, ball2 = app.exp1Balls
    if (distance(ball1.cx, ball1.cy, ball2.cx, ball2.cy) <= 
        ball1.radius + ball2.radius):
        m1, m2 = ball1.mass, ball2.mass
        v1, v2 = ball1.velocityX, ball2.velocityX
        if app.collisionType == 'Elastic':
            nextV1 = (2 * m2 * v2)/(m1 + m2) + ((m1 - m2) * v1)/(m1 + m2)
            nextV2 = (2 * m1 * v1)/(m1 + m2) - ((m1 - m2) * v2)/(m1 + m2)
            if m2 * v2 >= m1 * v1: # move ball 1
                ball1.cx = ball2.cx - ball2.radius - ball1.radius
            else:
                ball2.cx = ball1.cx + ball1.radius + ball2.radius
        elif app.collisionType == 'Perfectly Inelastic':
            nextV1 = (m1 * v1 + m2 * v2)/(m1 + m2)
            nextV2 = nextV1
            ball1.cx = ball2.cx - ball2.radius - ball1.radius
        if not app.collision:
            ball1.initVelocity = ball1.velocityX
            ball2.initVelocity = ball2.velocityX
            ball1.velocityX = (nextV1)
            ball2.velocityX = (nextV2)
            app.collision = True
        return True
    return False

# moves ball and checks for collisions for experiment 1 animation
def doExperiment1(app):
    for ball in app.exp1Balls:
        ball.move()
        ball.recalculate(app)
        checkBallAndGround(app, ball)
        checkBallAndSides(app, ball)
        exp1CheckBalls(app)

# deals with button clicks and setting values for balls in experiment 1
def exp1MouseClicks(app, event):
    for i in range(len(app.buttonLabels[app.mode - 1])):
        button = app.buttonCoordinates[i]
        if clickInButton(event.x, event.y, button):
            for j in range(len(app.exp1)):
                app.exp1[j] = False if j != i else True
    for j in [0, 1]: # only [0, 1] because those are the two Ball buttons
        if app.exp1[j]:
            if app.exp1Balls[j] == None:
                mass = int(app.getUserInput('Enter a mass (in kg): '))
                velocity = int(app.getUserInput('Enter a velocity (in m/s): '))
                velocity *= 10 * (-1)**j
                radius = 20
                spaceBetween = app.width - 2 * app.margin - 2 * radius
                app.exp1Balls[j] = Ball(
                                app.margin + radius + j * spaceBetween, 
                                app.height - app.margin - radius,
                                radius=radius, mass=mass, app=app)
                app.exp1Balls[j].velocityX = (velocity)
            else:
                mass = int(app.getUserInput('Enter a new mass (in kg): '))
                velocity = (
                    int(app.getUserInput('Enter a new velocity (in m/s): ')))
                velocity *= 10
                app.exp1Balls[j].mass = mass
                app.exp1Balls[j].velocityX = (velocity)
            app.exp1[j] = False

# handles all keypresses (changing collision types and reset)
def exp1Keypresses(app, event):
    if event.key == 'k':
        if app.collisionType == 'Elastic':
            app.collisionType = 'Perfectly Inelastic'
        else:
            app.collisionType = 'Elastic'
    elif event.key == 'r':
        # restart the app and de-select all the buttons, reset the collision
        app.exp1Balls = [None, None]
        app.exp1 = [False] * len(app.exp1)
        app.collision = False

# draws experiment title
def drawExp1Titles(app, canvas):
    canvas.create_text(app.width//2, app.margin//2 + 20, 
                text = app.collisionType + ' Collision')

# draws the balls in experiment 1 once they're defined
def drawExp1Balls(app, canvas):
    for i in range(2):
        if app.exp1Balls[i] != None:
            ball = app.exp1Balls[i]
            cx, cy, r = ball.cx, ball.cy, ball.radius
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'cyan')
            canvas.create_text(cx, cy, text = f'{ball.mass}')

# draws the equations for experiment 1
def drawExp1Equations(app, canvas):
    ball1, ball2 = app.exp1Balls
    v1 = round(ball1.initVelocity/10, 2)
    v2 = round(ball2.initVelocity/10, 2)
    m1, m2 = ball1.mass, ball2.mass
    newV1 = round(ball1.velocityX/10, 2)
    newV2 = round(ball2.velocityX/10, 2)
    canvas.create_rectangle(app.width//2 - 150, app.margin + 25,
                            app.width//2 + 150, app.margin + 75, 
                            fill='lightgreen')
    canvas.create_text(app.width//2, app.margin + 55,
            text = f'''\
            Conservation of Momentum (p = mv):
            (m1)(v1) + (m2)(v2) = (m1)(v1') + (m2)(v2')
            ({m1})({v1}) + ({m2})({v2}) = ({m1})({newV1}) + ({m2})({newV2})
            ''', justify = 'center')

# draws the collision text upon collision
def drawCollision(app, canvas):
    if None not in app.exp1Balls and app.collision:
        ball1, ball2 = app.exp1Balls
        x1, x2, y1, y2 = ball1.cx, ball2.cx, ball1.cy, ball2.cy
        font = (ball1.mass + ball2.mass) * 3
        canvas.create_text((x1+x2)//2, (y1+y2)//2, text = 'Boom!', 
                            font = str(font))