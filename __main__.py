# Name: Saumya Bhandarkar (ssbhanda)
# Assignment: TP3
# Description: main file - run this file to access application

from cmu_112_graphics import *
import basic_graphics, math, random, time
from tp_classes import *
from appStarted import *
from splashScreen import *
from exp1 import *
from exp2 import *
from exp3 import *
from sandbox import *

# checks for ball collisions
def checkBalls(app):
    if app.mode == 0:
        exp1CheckBalls(app)
    elif app.mode == 3:
        sandboxCheckBalls(app)

# timer is fired every 100ms, performs experiment animations depending on mode
def timerFired(app):
    if app.mode == 0 and None not in app.exp1Balls and app.exp1[2]:
        doExperiment1(app)
    elif app.mode == 1 and app.exp2[2]:
        doExperiment2(app)
    elif app.mode == 2:
        if app.exp3[3]:
            doExperiment3(app)
    elif app.mode == 3:
        if not app.isPaused:
            doSandboxStep(app)
    if app.mode != 2:
        for L in Ball.balls:
            if L[0] == app.exp3Ball:
                Ball.balls.remove(L)

# calls appropriate mouse function depending on mode
def mousePressed(app, event):
    if app.mode == 0:
        exp1MouseClicks(app, event)
    elif app.mode == 1:
        exp2MouseClicks(app, event)
    elif app.mode == 2:
        exp3MouseClicks(app, event)
    elif app.mode == 3:
        sandboxMouseClicks(app, event)

# responds to mouse drags in sandbox
def mouseDragged(app, event):
    if app.mode == 3:
        sandboxMouseDrags(app, event)

# responds to mouse releases in sandbox
def mouseReleased(app, event):
    if app.mode == 3:
        sandboxMouseReleased(app, event)

# controls key presses to change modes and calls exp/sandbox keypress functions
def keyPressed(app, event):
    if event.key == 'Up':
        if app.mode == None: app.mode = 0
        else:
            app.mode += 1
            if app.mode >= 3: app.mode = 3
    elif event.key == 'Down':
        if app.mode == None: app.mode = None
        else:
            app.mode -= 1
            if app.mode <= -1: app.mode = None
    elif event.key == 'p':
        app.isPaused = not app.isPaused
        app.exp2[2] = not app.exp2[2]
        if app.isPaused:
            app.start = time.time()
    elif app.mode == 0:
        exp1Keypresses(app, event)
    elif app.mode == 1:
        exp2Keypresses(app, event)
    elif app.mode == 2:
        exp3Keypresses(app, event)
    elif app.mode == 3:
        sandboxKeypresses(app, event)

# draws experiment titles for all the modes
def drawExperimentTitle(app, canvas):
    if app.mode != None:
        title = app.modeLabels[app.mode]
        canvas.create_text(app.width//2, app.margin//2 - 10, text = title,
                            font = 'Arial 12 bold')
        if app.mode == 0:
            drawExp1Titles(app, canvas)

# draws the app screen depending on mode
def redrawAll(app, canvas):
    if app.mode != None:
        drawGrid(app, canvas)
        drawButtons(app, canvas)
        drawExperimentTitle(app, canvas)
    else: 
        drawSplashScreen(app, canvas)
    if app.mode == 0:
        drawExp1Balls(app, canvas)
        drawCollision(app, canvas)
    elif app.mode == 1:
        drawExp2(app, canvas)
    elif app.mode == 2:
        drawExp3(app, canvas)
    elif app.mode == 3:
        drawObjects(app, canvas)
    drawEquations(app, canvas)

# draws equations for experiments 0 and 1
def drawEquations(app, canvas):
    if app.mode == 0 and app.exp1[3] and None not in app.exp1Balls:
        drawExp1Equations(app, canvas)
    elif app.mode == 1 and not app.exp2[2]:
        drawExp2Equations(app, canvas)

runApp(width = 1285, height = 785)