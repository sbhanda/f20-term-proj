# Name: Saumya Bhandarkar (ssbhanda)
# Assignment: TP3
# Description: holds info for drawing the splash screen

from appStarted import *
from tp_classes import *

# draws the intro splash screen + directions
def drawSplashScreen(app, canvas):
    x, y = app.width, app.height
    canvas.create_rectangle(0, 0, x, y, fill = 'salmon')
    canvas.create_text(x//2, y//4, text = '15112 Physics Mechanics Lab!',
                       font = 'Arial 40 bold')
    canvas.create_text(x//2, y//2, text = '''\
        Welcome to the 15112 Physics Mechanics Laboratory. Press the up and
        down keys to toggle between three set experiments and the open sandbox!
        ''', font = 'Arial 14 bold')
    canvas.create_text(x//2, y//4 * 3, text = '''\
        Experiment Controls - all experiments use buttons, but a few respond to
        other keypresses
        Exp 1:
        - 'k' to switch collision type
        Sandbox:
        - 'p' to pause/unpause
        - 'g' while selecting ball to lock/unlock the graph
        ''', font = 'Arial 14 bold')