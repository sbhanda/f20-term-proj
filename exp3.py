# Name: Saumya Bhandarkar (ssbhanda)
# Assignment: TP3
# Description: holds all functions for experiment 3

from appStarted import *
from tp_classes import *

# handles button clicks and changes appropriate objects
def exp3MouseClicks(app, event):
    for i in range(app.numButtons[app.mode]):
        button = app.buttonCoordinates[i]
        if clickInButton(event.x, event.y, button):
            for j in range(len(app.exp3)):
                app.exp3[j] = False if j != i else True
    if True not in app.exp3 and pointInGrid(app, event.x, event.y):
        if getCell(app, event.x, event.y)[0] == app.rows - 1:
            # no button was selected and click is in last row
            placeTarget(app, event)
    if app.exp3[0]: # adjust height!
        newHeight = int(app.getUserInput('Enter a new height in meters: '))
        newHeight *= 50
        app.exp3Table.y0 = app.height - app.margin - newHeight
        app.exp3Ball.cy = app.exp3Table.y0 -  app.exp3Ball.radius 
        app.exp3Ball.oldPoints[0] = (app.exp3Ball.cx, app.exp3Ball.cy)
        app.exp3[0] = False
    elif app.exp3[1]: # adjust angle
        angle = int(app.getUserInput('Enter a new angle in degrees: '))
        angle *= math.pi/180
        app.exp3Angle = angle
        app.exp3[1] = False
    elif app.exp3[2]: # adjust velocity
        vel = int(app.getUserInput('Enter a new velocity: ')) * 10
        app.exp3Ball.velocity = vel
        app.exp3[2] = False
    app.exp3Ball.projectileMotion(app.exp3Angle)

# responds to keypresses in experiment 3   
def exp3Keypresses(app, event):
    if event.key == 'p':
        app.isPaused = not app.isPaused
    elif event.key == 'r':
        app.exp3Table = Table(app)
        app.exp3Target = None
        app.exp3Table.x0 = app.margin
        app.exp3Table.x1 = app.width//3
        app.exp3Angle = math.pi/4
        app.exp3 = [False] * app.numButtons[2]
        app.exp3Ball = Ball(app.exp3Table.x1 - 20,
                                             app.exp3Table.y0 - 20, 20, 20, app)
        app.exp3Ball.velocity = 50
        app.exp3Ball.projectileMotion(app.exp3Angle)

# animates experiment 3 if the experiment is unpaused
def doExperiment3(app):
    ball = app.exp3Ball
    if not app.exp3[3] and not ball.onGround:
        ball.projectileMotion(app.exp3Angle)
    elif app.exp3[3]:
        app.exp3Old.append((ball.cx, ball.cy))
        if not ball.onGround:
            ball.move()
        ball.recalculate(app)
        checkBallAndGround(app, ball)
        checkBallAndSides(app, ball)
        if ball.onGround:
            ball.cx -= abs(ball.velocityX)
            if app.exp3Target != None:
                checkBallAndTarget(app, ball)
    app.exp3Table.recalculate(app)
    if ball.onGround:
        app.exp3[3] = False

# draws experiment 3
def drawExp3(app, canvas):
    drawTable(app, canvas)
    if app.exp3Target != None:
        drawTarget(app, canvas)
    drawBall(app, canvas)
    drawScore(app, canvas)

# draws the table in experiment 3
def drawTable(app, canvas):
    table = app.exp3Table
    x0, y0, x1, y1 = table.x0, table.y0, table.x1, table.y1
    canvas.create_rectangle(x0, y0, x1, y1, fill = 'pink')

# draws the ball in experiment 3
def drawBall(app, canvas):
    ball = app.exp3Ball
    cx, cy, r = ball.cx, ball.cy, ball.radius
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'cyan')
    oldCx, oldCy = ball.oldPoints[0]
    for (cx, cy) in ball.oldPoints[1:]:
        if pointInGrid(app, cx, cy):
            canvas.create_line(cx, cy, oldCx, oldCy, width = 2)
            oldCx, oldCy = cx, cy
    if not ball.onGround and not app.exp3[3]:
        # show the angle and velocity vector!
        drawVelocityVector(app, canvas, ball)

# draws the velocity vector
def drawVelocityVector(app, canvas, ball):
    cx, cy, theta = ball.cx, ball.cy, app.exp3Angle # radians
    velocity = ball.velocity
    r = velocity
    cx1, cy1 = cx + r * math.cos(theta), cy - r * math.sin(theta)
    canvas.create_line(cx, cy, cx1, cy1, width = 3)
    theta1 = theta//2 + math.pi
    theta2 = - math.pi/2 - theta//2
    x0, y0 = cx1 + 15 * math.cos(theta1), cy1 - 15 * math.sin(theta1)
    x1, y1 = cx1 + 15 * math.cos(theta2), cy1 - 15 * math.sin(theta2)
    canvas.create_line(cx1, cy1, x0, y0, width = 3)
    canvas.create_line(cx1, cy1, x1, y1, width = 3)

# place or move target on screen
def placeTarget(app, event):
    if app.exp3Target == None: # no target placed
        app.exp3Target = Target(event.x, event.y)
    else: # change position of target
        app.exp3Target.cx, app.exp3Target.cy = event.x, event.y

# draws target if visible
def drawTarget(app, canvas):
    cx, cy = app.exp3Target.cx, app.exp3Target.cy
    xr, yr = app.exp3Target.xRad, app.exp3Target.yRad
    canvas.create_oval(cx - xr, cy - yr, cx + xr, cy + yr, fill = 'red')
    xr *= 2/3
    yr *= 2/3
    canvas.create_oval(cx - xr, cy - yr, cx + xr, cy + yr, fill = 'white')
    xr *= 1/2
    yr *= 1/2
    canvas.create_oval(cx - xr, cy - yr, cx + xr, cy + yr, fill = 'red')

# checks if the ball and target collide
def checkBallAndTarget(app, ball):
    x0 = app.exp3Target.cx - app.exp3Target.xRad
    x1 = app.exp3Target.cx + app.exp3Target.xRad
    if x0 * 1/3 <= ball.cx <= x1 * 1/3: # lands in center
        app.exp3Score += 100
    elif x0 * 2/3 <= ball.cx <= x1 * 2/3: # lands in 2nd ring
        app.exp3Score += 50
    elif x0 <= ball.cx <= x1: # lands in 3rd ring
        app.exp3Score += 25
    else: # lands outside target
        app.exp3Score += 0

# draws current score
def drawScore(app, canvas):
    canvas.create_text(app.width - 2 * app.margin, app.margin//2,
                      text = f'Score = {app.exp3Score}', font = 'Arial 12 bold')