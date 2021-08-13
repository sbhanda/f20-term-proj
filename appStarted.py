# Name: Saumya Bhandarkar (ssbhanda)
# Assignment: TP3
# Description: holds appStarted and shared/common functions

from cmu_112_graphics import *
import basic_graphics, math, random, time
from tp_classes import *

def appStarted(app):
    # initialize the app window info
    app.margin = 80
    app.rows, app.cols = 25, 45

    # keeping track of all the items on the board
    app.objects = []

    # gravity timer info
    app.gravity = 4.9

    # experiment mode info
    app.mode = None
    app.numButtons = [4, 5, 4, 6]
    app.buttonLabels = buttonLabels()
    app.buttonCoordinates = buttonCoordinates()
    app.modeLabels = modes()
    app.exp1 = [False] * len(app.buttonLabels[0])
    app.exp2 = [False] * len(app.buttonLabels[1])
    app.exp3 = [False] * len(app.buttonLabels[2])
    app.sandbox = [False] * len(app.buttonLabels[3])
    app.exps = [app.exp1, app.exp2, app.exp3, app.sandbox]

    # experiment 1
    app.exp1Balls = [None, None]
    app.collisionType = 'Elastic'
    app.collision = False

    # experiment 2
    app.buttonIndex = None
    app.exp2Blocks = [None, None]
    app.mu = 0
    app.drawException = False

    # experiment 3
    app.exp3Table = Table(app)
    app.exp3Table.x0, app.exp3Table.x1 = app.margin, app.width//4
    app.exp3Angle = math.pi/4
    app.exp3Ball = Ball(app.exp3Table.x1 - 20, app.exp3Table.y0 - 20, 20, 20, app)
    app.exp3Ball.velocity = 50
    app.exp3Ball.projectileMotion(app.exp3Angle)
    app.exp3Old = []
    app.exp3Target = None
    app.exp3Score = 0

    # timer
    app.pauseEnd = 0
    app.pauseStart = 0

    # other/debugging
    app.isPaused = True

def buttonCoordinates():
    coords = [(5, 150, 75, 220),
              (5, 250, 75, 320),
              (5, 350, 75, 420),
              (5, 450, 75, 520),
              (5, 550, 75, 620)]
    return coords

def buttonLabels():
    labels = [['Ball 1', 'Ball 2', 'Go!', 'Show\nEquation'],
              ['Block 1', 'Block 2', 'Go!', 'Friction', 'Show Forces'],
              ['Adjust\nHeight', 'Adjust\nAngle', 'Adjust\nVelocity', 'Go!'],
              ['Ramp', 'Ball', 'Spring', 'Block', 'Friction']]
    return labels

def modes():
    modes = ['Experiment 1: Collisions',
             'Experiment 2: Forces',
             'Experiment 3: Projectile Motion',
             'Open Sandbox!']
    return modes

# draws the main environment grid, function from
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
def drawGrid(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            x0, y0, x1, y1 = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1, fill = 'lavender')

# returns coordinates for a given row, col pair; function from 
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
def getCellBounds(app, row, col):
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + col * cellWidth
    x1 = app.margin + (col+1) * cellWidth
    y0 = app.margin + row * cellHeight
    y1 = app.margin + (row+1) * cellHeight
    return (x0, y0, x1, y1)

# returns the distance between two points
def distance(x0, y0, x1, y1):
    return math.sqrt((x0-x1) ** 2 + (y0-y1) ** 2)

# checks if ball collides with ground, sets the new accel/vel/cy
def checkBallAndGround(app, ball):
    if ball.cy + ball.radius >= app.height - app.margin:
        ball.onGround = True
        ball.cy = app.height - app.margin - ball.radius
        ball.velocityY *= -1 * ball.coeffOfRestitution
        ball.accelX = 0
    else:
        ball.onGround = False

# checks if ball collides with sides, sets new cx and velocityX (bounces walls)
def checkBallAndSides(app, ball):
    if ball.cx + ball.radius >= app.width - app.margin:
        ball.cx = app.width - app.margin - ball.radius
        ball.velocityX *= -1
    elif ball.cx - ball.radius <= app.margin:
        ball.cx = app.margin + ball.radius
        ball.velocityX *= -1

# returns True if a point is within a button
def clickInButton(x, y, button):
    x0, y0, x1, y1 = button
    if x0 <= x <= x1 and y0 <= y <= y1:
        return True
    return False

# returns the row, col pair of a given point; from
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
def getCell(app, x, y):
    if (not pointInGrid(app, x, y)):
        return (-1, -1)
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth  = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    row = int((y - app.margin) / cellHeight)
    col = int((x - app.margin) / cellWidth)
    return (row, col)

# returns nearest point on line formed by p1/p2 starting at p3
# I got the function from:
# https://stackoverflow.com/questions/47177493/python-point-on-a-line-closest-to-
# third-point
def pointOnLine(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    dx, dy = x2 - x1, y2 - y1
    det = dx * dx + dy * dy
    a = (dy * (y3 - y1) + dx * (x3 - x1)) / det
    return x1 + a * dx, y1 + a * dy

# returns True if point is inside of ramp (triangle)
def pointInRamp(app, ramp, x, y, r=0):
    x0, y0, x1, y1, x2, y2 = getRampPoints(app, ramp)
    if ramp.orientation:
        m = (y2 - y1)/(x2 - x1)
    else:
        m = (y2 - y0)/(x2 - x0)
    b = y2 - m * x2
    if (m * x + b <= y and x0 <= x <= x1 and y2 <= y - r <= y0):
        return True
    if (m * x + b <= y - r or m * x + b <= y or m * x + b <= y + r):
        if (x0 <= x <= x1 and y2 <= y - r <= y0 or y2 <= y <= y0 or 
            y2 <= y + r <= y0):
            if r != 0:
                return True
    return False

# returns True if point is inside of the ball
def pointInBall(app, ball, x, y):
    return distance(x, y, ball.cx, ball.cy) <= ball.radius

# draws each button on the screen
def drawButtons(app, canvas):
    if app.mode != None:
        numButtons = app.numButtons[app.mode]
        for i in range(len(app.buttonCoordinates[:numButtons])):
            button = app.buttonCoordinates[i]
            x0, y0, x1, y1 = button
            title = app.buttonLabels[app.mode][i]
            color = 'orange' if app.exps[app.mode][i] == True else 'purple'
            canvas.create_rectangle(x0, y0, x1, y1, fill = color)
            canvas.create_text((x0+x1)//2, (y0+y1)//2, text = title)
    
# returns True if point is inside the the app grid from
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
def pointInGrid(app, x, y):
    return ((app.margin <= x <= app.width-app.margin) and
            (app.margin <= y <= app.height-app.margin))

# returns three points that define the ramp (for both orientations)
def getRampPoints(app, ramp):
    if ramp.orientation:
        x0, m, n, y0 = getCellBounds(app, ramp.row, ramp.col)
        x1, y1 = x0 + ramp.length, y0
        x2, y2 = x0, y0 - ramp.height
    else:
        x0, m, n, y0 = getCellBounds(app, ramp.row, ramp.col)
        x1, y1 = x0 + ramp.length, y0
        x2, y2 = x0 + ramp.length, y0 - ramp.height
    return x0, y0, x1, y1, x2, y2