# Name: Saumya Bhandarkar (ssbhanda)
# Assignment: TP3
# Description: this file holds all the defined classes

from cmu_112_graphics import *
import basic_graphics, math, random

########################### ALL DEFINED CLASSES #############################

# defines the Ramp class
class Ramp(object):
    import math
    # initializing a Ramp
    def __init__(self, row, col, height, angle=None):
        angle *= math.pi/180

        # calculate and/or assign values of attributes if unspecified
        self.height = height
        self.length = height/math.tan(angle)
        self.angle = angle

        # stores the left bottom corner of every ramp as a row, col value
        self.row, self.col = row, col

        # whether the user has this piece selected or not
        self.selected = False

        # orientation of ramp, where True has right angle on LH and False is RH
        self.orientation = True 

# defines the Ball class
class Ball(object):
    import math, time
    balls = []
    end = 0
    # initializing a Ball
    def __init__(self, cx, cy, mass, radius, app):
        import time
        self.cx, self.cy = cx, cy
        self.mass = mass
        self.radius = radius
        self.velocityX = 0
        self.velocityY = 0
        self.velocity = math.sqrt(self.velocityX**2 + self.velocityY**2)
        self.initVelocity = 0
        self.accelX = 0
        self.accelY = 4.9
        self.oldPoints = [(cx, cy)]
        self.initGPE = (((app.height - app.margin - self.radius) 
                            - self.cy)/50 * 9.8 * self.mass)
        self.initKE = 1/2 * self.mass * (self.velocity/500)**2
        self.GPE = self.initGPE
        self.KE = self.initKE
        self.onGround = False
        self.coeffOfRestitution = 0
        self.selected = False
        self.onRamp = False
        self.start = time.time()
        vel = round(self.velocity, 2)
        Ball.balls.append([self, vel])
        self.lockGraph = False

    # getHashables and hash function are both from:
    # https://www.cs.cmu.edu/~112/notes/notes-oop-part4.html
    def getHashables(self):
        return (self.cx, self.cy, self.radius, self.velocityX, self.velocityY)

    # getHashables and hash function are both from:
    # https://www.cs.cmu.edu/~112/notes/notes-oop-part4.html
    def __hash__(self):
        return hash(self.getHashables())
    
    # function to check equality
    def __eq__(self, other):
        return isinstance(other, Ball) and self.cx == other.cx and (
                self.cy == other.cy and self.radius == other.radius and
                self.mass == other.mass)

    # increments velocity by acceleration and moves ball cx, cy by velocity
    def move(self):
        self.velocityX += self.accelX
        if not self.onGround:
            self.velocityY += self.accelY
        self.cx += self.velocityX
        self.cy += self.velocityY
        if not self.onGround:
            self.oldPoints.append((self.cx, self.cy))

    # recalculates overall velocity, GPE, and KE; resets accel if not on surface
    def recalculate(self, app):
        self.velocity = math.sqrt(self.velocityX**2 + self.velocityY**2)
        if app.mode == 3:
            self.updateCoordinates(app)
        self.GPE = ((app.height - app.margin - self.radius - self.cy)/50 * 
                                                    app.gravity * 2 * self.mass)
        self.KE = 1/2 * self.mass * (self.velocity/500)**2
        if not self.onRamp and app.mode == 3:
            self.accelY = app.gravity
            self.accelX = 0 

    # calculates velocityX and velocityY for exp3 based on the angle provided
    def projectileMotion(self, angle):
        v = self.velocity
        self.velocityX = v * math.cos(angle)
        self.velocityY = -1 * (v * math.sin(angle))

    # compresses spring when ball and spring collide
    def compressSpring(self, spring, app):
        self.recalculate(app)
        totEnergy = self.KE + self.GPE
        if totEnergy < 0:
            spring.displacement = 0
        else: spring.displacement = math.sqrt(2 * totEnergy/spring.constant)
        spring.compressSpring(self)
        self.recalculate(app)

    # static method that adds velocity values to the coordinate list
    @staticmethod
    def updateCoordinates(app):
        import time
        if not app.isPaused:
            Ball.end = time.time() - (app.pauseEnd - app.pauseStart)
            app.pauseStart = 0
        else:
            if app.pauseStart == 0:
                app.pauseStart = time.time()
            app.pauseEnd = time.time()
        for i in range(len(Ball.balls)):
            ball = Ball.balls[i][0]
            vel = round(ball.velocity, 2)
            if app.isPaused:
                vel = 0
            Ball.balls[i].append(vel)

    # causes the ball to lose energy over time
    def loseKE(self, energy=1):
        self.KE -= energy
        if self.KE > 0:
            self.velocityX = math.sqrt(2*self.KE/self.mass) * 500
        else:
            self.velocityX = 0
        if self.velocityX != 0:
            angle = math.atan(self.velocityY/self.velocityX)
        else: angle = math.pi/2
        self.velocityX = self.velocity * math.cos(angle)
        self.velocityY = self.velocity * math.sin(angle)

# defines the spring class
class Spring(object):
    def __init__(self, row, col, constant=300):
        self.constant = constant
        self.displacement = 0
        self.initLength = 150
        self.length = self.initLength
        self.row, self.col = row, col
        self.isCompressed = False
        self.energy = 0
        self.selected = False
    
    # compresses the spring
    def compressSpring(self, ball):
        self.length -= self.displacement * 500
        self.energy = 1/2 * self.constant * self.displacement**2
        self.isCompressed = True
    
    # decompresses the spring
    def decompressSpring(self, ball, app):
        self.length = self.initLength
        ball.KE = self.energy
        ball.recalculate(app)
        ball.velocityX = -1 * abs(ball.velocityX)
        self.isCompressed = False

# defines the Friction class
class Friction(object):
    # initializes values
    def __init__(self):
        self.coeff = 0.35
        self.distance = 200
        self.x, self.y = -1, -1
        self.selected = False

# defines the block class
class Block(object):
    # initializes values
    def __init__(self, x, y, mass=5):
        self.length = 100
        self.height = 50
        self.x, self.y = x, y
        self.mass = mass
        self.onTable = False
        self.normalForce = None
        self.accel = 0
        self.velocityX = 0
        self.velocityY = 0
        self.force = 0
        self.selected = False

# defines the Table class     
class Table(object):
    # initializes values
    def __init__(self, app):
        self.x0, self.y0 = app.width//2 - 300, app.height//3 + 50
        self.x1, self.y1 = app.width//2 + 300, app.height - app.margin
        self.selected = False
    
    # resets table values
    def recalculate(self, app):
        # app.exp3Table.x0 = app.margin
        # app.exp3Table.x1 = app.width//4
        pass

# defines Target class
class Target(object):
    # initializes values
    def __init__(self, cx, cy):
        self.cx, self.cy = cx, cy
        self.xRad, self.yRad = 120, 15