from cmu_112_graphics import *
import os, random, time, math
from TP_AI import *

#Super Bump Sheep 

class Sheep():

    fixedSpeed = 5

    def __init__(self,size,x,y,color,transposed,row,col,width,height):
        self.size = size
        self.points = 6 - size
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        self.collided = False
        self.transposed = transposed
        self.speed = 5
        self.color = color
        self.width = width
        self.height = height

class Row():

    def __init__(self):
        self.collisions = []

class Col():

    def __init__(self):
        self.collisions = []

class Player():

    def __init__(self):
        self.score = 0
        self.win = False

class Bump():

    def __init__(self):
        self.collidingSheep = []

# Main class
class MyApp(App):

    def appStarted(self):

        self.rows = 9
        self.cols = 12
        self.topMargin = 153
        self.bottomMargin = 91
        self.sideMargin = 44
        self.sideMargin2 = 50
        self.colWidth = math.floor((self.width-2*self.sideMargin)/self.cols)
        self.rowHeight = math.floor((self.height-self.topMargin-self.bottomMargin)/self.rows)
        self.paused = False

        self.rowObjects = []
        
        for i in range(self.rows):
            row = Row()
            self.rowObjects.append(row)

        self.colObjects = []

        for i in range(self.cols):
            col = Col()
            self.colObjects.append(col)

        self.sheepImagePaths = []

        for image in os.listdir('sheep'):
            self.sheepImagePaths.append('sheep/'+image)
        
        
        self.blackSheepImagePaths = self.sheepImagePaths[:5]
        self.whiteSheepImagePaths = self.sheepImagePaths[5:]
        
        self.loadedBlackImages = []
        self.loadedWhiteImages = []

        self.loadedTransposedBlackImages = []
        self.loadedTransposedWhiteImages = []

        self.grassGrid = self.loadImage('grassGrid.png')

        self.logo = self.loadImage('logo.jpeg')
        width, height = self.logo.size
        scaleFactor = 300/width
        self.scaledLogo = self.scaleImage(self.logo,scaleFactor)

        self.sheep1 = self.loadImage('sheep1.png')
        width, height = self.sheep1.size
        scaleFactor = 200/height
        self.scaledSheep1 = self.scaleImage(self.sheep1,scaleFactor)
        
        self.sheep2 = self.loadImage('sheep2.png')
        width, height = self.sheep2.size
        scaleFactor = 200/height
        self.scaledSheep2 = self.scaleImage(self.sheep2,scaleFactor)

        self.button = self.loadImage('button.png')
        width, height = self.button.size
        scaleFactor = self.rowHeight/height
        self.scaledButton = self.scaleImage(self.button,scaleFactor)

        for imagePath in self.blackSheepImagePaths:
            self.tempImage = self.loadImage(imagePath)
            width, height = self.tempImage.size
            scaleFactor = self.rowHeight/height
            self.scaledImage = self.scaleImage(self.tempImage,scaleFactor)
            self.loadedBlackImages.append(self.scaledImage)


            self.transposedImage = self.tempImage.transpose(Image.ROTATE_270)
            width_t, height_t = self.transposedImage.size
            scaleFactor = self.colWidth/width_t
            self.scaledImage = self.scaleImage(self.transposedImage,scaleFactor)
            self.loadedTransposedBlackImages.append(self.scaledImage)

        for imagePath in self.whiteSheepImagePaths:
            self.tempImage = self.loadImage(imagePath)
            width, height = self.tempImage.size
            scaleFactor = self.rowHeight/height
            self.scaledImage = self.scaleImage(self.tempImage,scaleFactor)
            self.loadedWhiteImages.append(self.scaledImage)


            self.transposedImage = self.tempImage.transpose(Image.ROTATE_270)
            width_t, height_t = self.transposedImage.size
            scaleFactor = self.colWidth/width_t
            self.scaledImage = self.scaleImage(self.transposedImage,scaleFactor)
            self.loadedTransposedWhiteImages.append(self.scaledImage)

        self.nextBlackSheep = []
        self.nextWhiteSheep = []

        self.activeBlackSheep = []
        self.activeWhiteSheep = []

        self.vertButtonPositions = []
        self.horizButtonPositions = []
        self.createButtons()
        
        self.blackPlayer = Player()
        self.whitePlayer = Player()

        self.blackCurrTime = None
        self.whiteCurrTime = None
        self.blackTimePassed = 0
        self.whiteTimePassed = 0

        self.pointsToWin = 15
        self.AImode = False
        self.disappearMode = False
        self.setupComplete = False
        self.gameStarted = False

    def getCellBounds(self,row,col):

        x1, y1 = self.sideMargin + col*self.colWidth, self.topMargin + row*self.rowHeight
        x2, y2 = x1 + self.colWidth, y1 + self.rowHeight
        return x1, y1, x2, y2 

    def createButtons(self):

        for row in range(self.rows):
            
            x2Left = self.sideMargin - 4.6
            x1Left = self.sideMargin - self.rowHeight + 4.6
            
            y1 = self.topMargin + row*self.rowHeight + 4.6
            y2 = self.topMargin + (row+1)*self.rowHeight - 4.6

            self.vertButtonPositions.append((x1Left,y1,x2Left,y2))

            x1Right = self.width - self.sideMargin2 + 4.6
            x2Right = self.width - self.sideMargin2 + self.rowHeight - 4.6

            self.vertButtonPositions.append((x1Right,y1,x2Right,y2))

        for col in range(self.cols):

            y2Top = self.topMargin
            y1Top = self.topMargin - self.colWidth + 9.2
            
            x1 = self.sideMargin + col*self.colWidth + 4.6
            x2 = self.sideMargin + (col+1)*self.colWidth - 4.6
            self.horizButtonPositions.append((x1,y1Top,x2,y2Top))
            y1Bottom = self.height - self.bottomMargin + 4.6
            y2Bottom = self.height - self.bottomMargin + self.colWidth - 4.6

            self.horizButtonPositions.append((x1,y1Bottom,x2,y2Bottom))

    def distance(self,x1,y1,x2,y2):

        return ((x1-x2)**2 + (y1-y2)**2)**0.5

    def getRowCy(self,row):

        buttonIndex = row*2 - 1
        x1,y1,x2,y2 = self.vertButtonPositions[buttonIndex]
        cy = (y1+y2)/2

        return cy

    def keyPressed(self,event):

        if event.key == 'p' and self.gameStarted:
            self.paused = not self.paused
            if self.paused:
                self.pausedTime = time.time()
            else:
                self.blackTimePassed += (time.time() - self.pausedTime)
                self.whiteTimePassed += (time.time() - self.pausedTime)

        #ready
        elif event.key == 'r' and not self.gameStarted:
            self.gameStarted = True

        #restart
        elif event.key == 'r':
            self.appStarted()

        elif event.key == 'a' and not self.setupComplete:
            self.AImode = not self.AImode
            print('AI activated')

        elif event.key == 'd' and not self.setupComplete:
            self.disappearMode = not self.disappearMode
            print('Disappear mode activated')

        elif event.key == 's' and not self.setupComplete:
            self.setupComplete = True

        elif self.gameStarted:

            try:
                
                row = self.rowObjects[int(event.key)-1]
                self.checkSheepReady()
                
                if self.blackSheepReady:
                    rowToSend = int(event.key)
                    if 1 <= rowToSend <= 9:
                        size = self.nextBlackSheep.pop(0)

                        image = self.loadedBlackImages[size-1]
                        width, height = image.size

                        x = self.sideMargin + width/2
                        y = self.getRowCy(rowToSend)
                        blackSheep = Sheep(size,x,y,'black',False,rowToSend-1,None,width,height)

                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        self.blacktimePassed = 0
                    else:
                        print(f'Press a number from 1 to {self.rows}')

            except:
                print(f'Press a number from 1 to {self.rows}')
            

    def mousePressed(self,event):
        
        if (not self.blackPlayer.win and not self.whitePlayer.win 
        and not self.paused and self.gameStarted):

            x,y = event.x,event.y
            
            for i in range(len(self.vertButtonPositions)):
                
                x1,y1,x2,y2 = self.vertButtonPositions[i]

                cx = (x1+x2)/2
                cy = (y1+y2)/2
                if self.distance(x,y,cx,cy) <= self.rowHeight/2:
                    
                    row = self.rowObjects[i//2]
                    self.checkSheepReady()

                    if i % 2 == 0 and self.blackSheepReady:
                        size = self.nextBlackSheep.pop(0)

                        image = self.loadedBlackImages[size-1]
                        width, height = image.size

                        blackSheep = Sheep(size,self.sideMargin+width/2,cy,'black',False,i//2,None,width,height)
                        print(blackSheep.row)
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        self.blackTimePassed = 0

                    elif i % 2 == 1 and self.whiteSheepReady:
                        size = self.nextWhiteSheep.pop(0)

                        image = self.loadedWhiteImages[size-1]
                        width, height = image.size

                        whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,cy,'white',False,i//2,None,width,height)
                        print(whiteSheep.row)
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        self.whiteTimePassed = 0

            for i in range(len(self.horizButtonPositions)):
                
                x1,y1,x2,y2 = self.horizButtonPositions[i]

                cx = (x1+x2)/2
                cy = (y1+y2)/2
                if self.distance(x,y,cx,cy) <= self.colWidth/2:
                    
                    col = self.colObjects[i//2]
                    self.checkSheepReady()

                    if i % 2 == 0 and self.blackSheepReady:
                        size = self.nextBlackSheep.pop(0)

                        image = self.loadedTransposedBlackImages[size-1]
                        width, height = image.size

                        blackSheep = Sheep(size,cx,self.topMargin+height/2,'black',True,None,i//2,width,height)
                        print(blackSheep.col)
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        self.blackTimePassed = 0

                    elif i % 2 == 1 and self.whiteSheepReady:
                        size = self.nextWhiteSheep.pop(0)

                        image = self.loadedTransposedWhiteImages[size-1]
                        width, height = image.size

                        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-height/2,'white',True,None,i//2,width,height)
                        print(whiteSheep.col)
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        self.whiteTimePassed = 0


    def checkSheepReady(self):

        if self.blackCurrTime == None or (self.blackCurrTime + self.blackTimePassed + 3) <= time.time():
            self.blackSheepReady = True
        else:
            self.blackSheepReady = False
        if self.whiteCurrTime == None or (self.whiteCurrTime + self.whiteTimePassed + 3) <= time.time():
            self.whiteSheepReady = True
        else:
            self.whiteSheepReady = False

    def timerFired(self):
        
        self.generateNextSheep()

        if not self.blackPlayer.win and not self.whitePlayer.win and not self.paused and self.gameStarted:

            self.moveActiveSheep()
            self.checkCollision()
            self.addPoints()
            self.checkWin()
            self.playAI()

    def playAI(self):

        if self.AImode:

            AI(self)

    def getColCx(self,col):

        index = col*2+1
        x1,y1,x2,y2 = self.horizButtonPositions[index]
        cx = (x1+x2)/2

        return cx

    def addPoints(self):

        for blackSheep in self.activeBlackSheep:

            if blackSheep.x + blackSheep.width/2 >= (self.width - self.sideMargin) and blackSheep.row != None:

                    self.activeBlackSheep.remove(blackSheep)
                    self.blackPlayer.score += blackSheep.points
            
            elif blackSheep.x - blackSheep.width/2 < self.sideMargin and blackSheep.row != None:

                row = self.rowObjects[blackSheep.row]
                for bump in row.collisions:
                    if blackSheep in bump.collidingSheep:
                        bump.collisionNetPower -= blackSheep.size
                        bump.collisionTotalPower -= blackSheep.size
                        bump.collidingSheep.remove(blackSheep)
                        self.activeBlackSheep.remove(blackSheep)

                        # if bump.collisionTotalPower != 0:
                        speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'black':
                                sheep.speed = speedFactor*sheep.fixedSpeed
                            else:
                                sheep.speed = -speedFactor*sheep.fixedSpeed

                        bump.doneColliding = True
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'black':
                                bump.doneColliding = False
                        
                        if bump.doneColliding:
                            for whiteSheep in bump.collidingSheep:
                                whiteSheep.collided = False
            
            elif blackSheep.y + blackSheep.height/2 >= (self.width - self.bottomMargin) and blackSheep.col != None:

                    self.activeBlackSheep.remove(blackSheep)
                    self.blackPlayer.score += blackSheep.points

            elif blackSheep.y - blackSheep.height/2 < self.topMargin and blackSheep.col != None:

                col = self.colObjects[blackSheep.col]
                for bump in col.collisions:
                    if blackSheep in bump.collidingSheep:
                        bump.collisionNetPower -= blackSheep.size
                        bump.collisionTotalPower -= blackSheep.size
                        bump.collidingSheep.remove(blackSheep)
                        self.activeBlackSheep.remove(blackSheep)

                        # if bump.collisionTotalPower != 0:
                        speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'black':
                                sheep.speed = speedFactor*sheep.fixedSpeed
                            else:
                                sheep.speed = -speedFactor*sheep.fixedSpeed
                
                        bump.doneColliding = True
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'black':
                                bump.doneColliding = False
                        
                        if bump.doneColliding:
                            for whiteSheep in bump.collidingSheep:
                                whiteSheep.collided = False

        for whiteSheep in self.activeWhiteSheep:

            if whiteSheep.x - whiteSheep.width/2 <= self.sideMargin and whiteSheep.row != None:

                    self.activeWhiteSheep.remove(whiteSheep)
                    self.whitePlayer.score += whiteSheep.points

            elif whiteSheep.x + whiteSheep.width/2 > (self.width - self.sideMargin) and whiteSheep.row != None:

                row = self.rowObjects[whiteSheep.row]
                for bump in row.collisions:
                    if whiteSheep in bump.collidingSheep:
                        bump.collisionNetPower += whiteSheep.size
                        bump.collisionTotalPower -= whiteSheep.size
                        bump.collidingSheep.remove(whiteSheep)
                        self.activeWhiteSheep.remove(whiteSheep)

                        if bump.collisionTotalPower != 0:
                            speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                            for sheep in bump.collidingSheep:
                                if sheep.color == 'black':
                                    sheep.speed = speedFactor*sheep.fixedSpeed
                                else:
                                    sheep.speed = -speedFactor*sheep.fixedSpeed

                        bump.doneColliding = True
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'white':
                                bump.doneColliding = False
                        
                        if bump.doneColliding:
                            for blackSheep in bump.collidingSheep:
                                blackSheep.collided = False

            elif whiteSheep.y - whiteSheep.height/2 <= self.topMargin and whiteSheep.col != None:

                    self.activeWhiteSheep.remove(whiteSheep)
                    self.whitePlayer.score += whiteSheep.points

            elif whiteSheep.y + whiteSheep.height/2 > (self.height - self.bottomMargin) and whiteSheep.col != None:

                col = self.colObjects[whiteSheep.col]
                for bump in col.collisions:
                    if whiteSheep in bump.collidingSheep:
                        bump.collisionNetPower += whiteSheep.size
                        bump.collisionTotalPower -= whiteSheep.size
                        bump.collidingSheep.remove(whiteSheep)
                        self.activeWhiteSheep.remove(whiteSheep)

                        if bump.collisionTotalPower != 0:
                            speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                            for sheep in bump.collidingSheep:
                                if sheep.color == 'black':
                                    sheep.speed = speedFactor*sheep.fixedSpeed
                                else:
                                    sheep.speed = -speedFactor*sheep.fixedSpeed

                        bump.doneColliding = True
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'white':
                                bump.doneColliding = False
                        
                        if bump.doneColliding:
                            for blackSheep in bump.collidingSheep:
                                blackSheep.collided = False


    def checkCollision(self):

        for blackSheep in self.activeBlackSheep:

            for otherBlackSheep in self.activeBlackSheep:

                if (blackSheep.row == otherBlackSheep.row != None and blackSheep.collided == False and
                    otherBlackSheep.collided == True and blackSheep.x+blackSheep.width/2 >= otherBlackSheep.x-otherBlackSheep.width/2 and blackSheep.x < otherBlackSheep.x):

                    row = self.rowObjects[blackSheep.row]
                    for bump in row.collisions:
                        if otherBlackSheep in bump.collidingSheep:
                            bump.collisionNetPower += blackSheep.size
                            bump.collisionTotalPower += blackSheep.size
                            bump.collidingSheep.append(blackSheep)

                            speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                            for sheep in bump.collidingSheep:
                                if sheep.color == 'black':
                                    sheep.speed = speedFactor*sheep.fixedSpeed
                                else:
                                    sheep.speed = -speedFactor*sheep.fixedSpeed

                    blackSheep.collided = True

                elif (blackSheep.col == otherBlackSheep.col != None and blackSheep.collided == False and
                    otherBlackSheep.collided == True and blackSheep.y+blackSheep.height/2 >= otherBlackSheep.y-otherBlackSheep.height/2):

                    col = self.colObjects[blackSheep.col]
                    for bump in col.collisions:
                        if otherBlackSheep in bump.collidingSheep:
                            bump.collisionNetPower += blackSheep.size
                            bump.collisionTotalPower += blackSheep.size
                            bump.collidingSheep.append(blackSheep)

                            speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                            for sheep in bump.collidingSheep:
                                if sheep.color == 'black':
                                    sheep.speed = speedFactor*sheep.fixedSpeed
                                else:
                                    sheep.speed = -speedFactor*sheep.fixedSpeed

                    blackSheep.collided = True

            for whiteSheep in self.activeWhiteSheep:


                if (blackSheep.col == whiteSheep.col != None and (whiteSheep.y - blackSheep.y) <= (whiteSheep.height/2+blackSheep.height/2)
                    and blackSheep.collided == False and whiteSheep.collided == False):
                    
                    blackSheep.collided = True
                    whiteSheep.collided = True

                    bump = Bump()
                    bump.collidingSheep.append(blackSheep)
                    bump.collidingSheep.append(whiteSheep)

                    bump.collisionNetPower = blackSheep.size - whiteSheep.size
                    bump.collisionTotalPower = blackSheep.size + whiteSheep.size
                    speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                    blackSheep.speed = speedFactor*blackSheep.fixedSpeed
                    whiteSheep.speed = -blackSheep.speed

                    col = self.colObjects[blackSheep.col]
                    col.collisions.append(bump)

                elif (blackSheep.row == whiteSheep.row != None and whiteSheep.x - blackSheep.x <= whiteSheep.width/2+blackSheep.width/2
                    and blackSheep.collided == False and whiteSheep.collided == False and whiteSheep.x > blackSheep.x):
                    
                    blackSheep.collided = True
                    whiteSheep.collided = True

                    bump = Bump()
                    bump.collidingSheep.append(blackSheep)
                    bump.collidingSheep.append(whiteSheep)

                    bump.collisionNetPower = blackSheep.size - whiteSheep.size
                    bump.collisionTotalPower = blackSheep.size + whiteSheep.size
                    speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                    blackSheep.speed = speedFactor*blackSheep.fixedSpeed
                    whiteSheep.speed = -blackSheep.speed

                    row = self.rowObjects[blackSheep.row]
                    row.collisions.append(bump)

                 

                #row-col collision
                elif (((blackSheep.row == None and whiteSheep.row != None) or (blackSheep.row != None and whiteSheep.row == None))
                and blackSheep.collided == False and whiteSheep.collided == False):

                    #check for disappear mode
                    if self.disappearMode:

                        if (blackSheep.x - blackSheep.width/2 - whiteSheep.width <= whiteSheep.x - whiteSheep.width/2 <= blackSheep.x + blackSheep.width/2
                        and blackSheep.y - blackSheep.height/2 - whiteSheep.height <= whiteSheep.y - whiteSheep.height/2 <= blackSheep.y + blackSheep.height/2):
                            
                            print('disappear!')
                            self.activeWhiteSheep.remove(whiteSheep)
                            self.activeBlackSheep.remove(blackSheep)
                    
                    else:

                        #check for if they collide
                        if (blackSheep.x - blackSheep.width/2 - whiteSheep.width <= whiteSheep.x - whiteSheep.width/2 <= blackSheep.x + blackSheep.width/2
                        and blackSheep.y - blackSheep.height/2 - whiteSheep.height <= whiteSheep.y - whiteSheep.height/2 <= blackSheep.y + blackSheep.height/2):
                            print("cross collision")

                            if whiteSheep.col != None:
                            
                                self.activeWhiteSheep.remove(whiteSheep)
                                movedWhiteSheep = Sheep(whiteSheep.size,blackSheep.x+blackSheep.width/2+whiteSheep.height/2,blackSheep.y,'white',False,blackSheep.row,None,whiteSheep.width,whiteSheep.height)
                                self.activeWhiteSheep.append(movedWhiteSheep)

                            elif blackSheep.col != None:

                                self.activeBlackSheep.remove(blackSheep)
                                movedBlackSheep = Sheep(blackSheep.size,whiteSheep.x-whiteSheep.width/2-blackSheep.height/2,whiteSheep.y,'black',False,whiteSheep.row,None,blackSheep.width,blackSheep.height)
                                self.activeBlackSheep.append(movedBlackSheep)
                
                elif (blackSheep.row == whiteSheep.row != None and blackSheep.x - blackSheep.width/2 <= whiteSheep.x + whiteSheep.width/2
                    and blackSheep.collided == True and whiteSheep.collided == True and blackSheep.x > whiteSheep.x):

                        row = self.rowObjects[blackSheep.row]
                        for bump in row.collisions:
                            if blackSheep in bump.collidingSheep:
                                for bump2 in row.collisions:
                                    if whiteSheep in bump2.collidingSheep and bump2 != bump:
                                        
                                        bump2.collisionNetPower += bump.collisionNetPower
                                        bump2.collisionTotalPower += bump.collisionTotalPower
                                        bump2.collidingSheep.extend(bump.collidingSheep)
                                        speedFactor = bump2.collisionNetPower/bump2.collisionTotalPower
                                        for sheep in bump2.collidingSheep:
                                            if sheep.color == 'black':
                                                sheep.speed = speedFactor*sheep.fixedSpeed
                                            else:
                                                sheep.speed = -speedFactor*sheep.fixedSpeed
                                        row.collisions.remove(bump)
        
        for whiteSheep in self.activeWhiteSheep:

            for otherWhiteSheep in self.activeWhiteSheep:

                if (whiteSheep.row == otherWhiteSheep.row != None and whiteSheep.collided == False and
                    otherWhiteSheep.collided == True and whiteSheep.x-whiteSheep.width/2 <= otherWhiteSheep.x+otherWhiteSheep.width/2 and whiteSheep.x >= otherWhiteSheep.x):

                    row = self.rowObjects[whiteSheep.row]
                    for bump in row.collisions:

                        if otherWhiteSheep in bump.collidingSheep:

                            bump.collisionNetPower -= whiteSheep.size
                            bump.collisionTotalPower += whiteSheep.size
                            bump.collidingSheep.append(whiteSheep)

                            speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                            for sheep in bump.collidingSheep:
                                if sheep.color == 'black':
                                    sheep.speed = speedFactor*sheep.fixedSpeed
                                else:
                                    sheep.speed = -speedFactor*sheep.fixedSpeed

                    whiteSheep.collided = True

                elif (whiteSheep.col == otherWhiteSheep.col != None and whiteSheep.collided == False and
                    otherWhiteSheep.collided == True and whiteSheep.y-whiteSheep.height/2 <= otherWhiteSheep.y+whiteSheep.height/2):

                    col = self.colObjects[whiteSheep.col]
                    for bump in col.collisions:
                        if otherWhiteSheep in bump.collidingSheep:
                            bump.collisionNetPower -= whiteSheep.size
                            bump.collisionTotalPower += whiteSheep.size
                            bump.collidingSheep.append(whiteSheep)

                            speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                            for sheep in bump.collidingSheep:
                                if sheep.color == 'black':
                                    sheep.speed = speedFactor*sheep.fixedSpeed
                                else:
                                    sheep.speed = -speedFactor*sheep.fixedSpeed

                    whiteSheep.collided = True

    def moveActiveSheep(self):

            for sheep in self.activeBlackSheep:

                if sheep.transposed:
                    sheep.y += sheep.speed
                else:
                    sheep.x += sheep.speed

            for sheep in self.activeWhiteSheep:

                if sheep.transposed:
                    sheep.y -= sheep.speed
                else:
                    sheep.x -= sheep.speed

    def generateNextSheep(self):
        
        while len(self.nextBlackSheep) < 3:
            randomSize = random.randint(1,5)
            self.nextBlackSheep.append(randomSize)

        while len(self.nextWhiteSheep) < 3:
            randomSize = random.randint(1,5)
            self.nextWhiteSheep.append(randomSize)

    def checkWin(self):

        if self.blackPlayer.score >= self.pointsToWin:
            self.blackPlayer.win = True
            self.pausedTime = time.time()

        elif self.whitePlayer.score >= self.pointsToWin:
            self.whitePlayer.win = True
            self.pausedTime = time.time()

    def drawWin(self,canvas):

        centreRow = self.rows // 2
        cy = self.getRowCy(centreRow)
        cy2 = self.getRowCy(centreRow+1)

        if self.blackPlayer.win:

            canvas.create_text(self.width/2,cy,text='Black wins!!!',font='Arial 24 bold',fill='orange')
            canvas.create_text(self.width/2,cy2,text='Press "R" to restart',font='Arial 16 bold',fill='orange')
        
        else:

            canvas.create_text(self.width/2,cy,text='White wins!!!',font='Arial 24 bold',fill='orange')
            canvas.create_text(self.width/2,cy2,text='Press "R" to restart',font='Arial 16 bold',fill='orange')

    def drawButtons(self,canvas):

        for x1,y1,x2,y2 in self.vertButtonPositions:

            image = self.scaledButton
            photoImage = self.getCachedPhotoImage(image)
            canvas.create_image((x1+x2)/2,(y1+y2)/2,image=photoImage)

        for x1,y1,x2,y2 in self.horizButtonPositions:

            image = self.scaledButton
            photoImage = self.getCachedPhotoImage(image)
            canvas.create_image((x1+x2)/2,(y1+y2)/2,image=photoImage)

        # for x1,y1,x2,y2 in self.vertButtonPositions:

        #     canvas.create_oval(x1,y1,x2,y2,fill='grey')
        #     canvas.create_text((x1+x2)//2,(y1+y2)//2,text='GO!')

        # for x1,y1,x2,y2 in self.horizButtonPositions:

        #     canvas.create_oval(x1,y1,x2,y2,fill='grey')
        #     canvas.create_text((x1+x2)//2,(y1+y2)//2,text='GO!')

    def drawGrid(self,canvas):
        for row in range(self.rows):
            for col in range(self.cols):
                if (row+col)%2 == 0: 
                    canvas.create_rectangle(MyApp.getCellBounds(self,row,col),fill='#2ade2a')
                else:
                    canvas.create_rectangle(MyApp.getCellBounds(self,row,col),fill='#086608')

    def drawNextSheep(self,canvas):

        x = 30

        for i in range(len(self.nextBlackSheep)):

            image = self.loadedBlackImages[self.nextBlackSheep[i]-1]
            width, height = image.size

            photoImage = self.getCachedPhotoImage(image)
            if x > 30:
                x += width/2
            canvas.create_image(x, 40, image=photoImage)

            x += width/2

        x = self.width-30

        for i in range(len(self.nextWhiteSheep)):

            image = self.loadedWhiteImages[self.nextWhiteSheep[i]-1]
            width, height = image.size

            photoImage = self.getCachedPhotoImage(self.loadedWhiteImages[self.nextWhiteSheep[i]-1])
            if x < self.width - 30:
                x -= width/2
            canvas.create_image(x, 40, image=photoImage)

            x -= width/2

            # photoImage = self.getCachedPhotoImage(self.loadedWhiteImages[self.nextWhiteSheep[i]-1])
            # canvas.create_image(self.width-20-i*40, 40, image=photoImage)

    def getWidthAndHeight(self,sheep,image):

        width, height = image.size
        sheep.width = width
        sheep.height = height

    def drawGrassGrid(self,canvas):

        photoImage = self.getCachedPhotoImage(self.grassGrid)
        canvas.create_image(self.width/2,self.height/2+45,image=photoImage)

    def drawActiveSheep(self,canvas):

        for sheep in self.activeBlackSheep:

            if sheep.transposed == False:
                image = self.loadedBlackImages[sheep.size-1]
                self.getWidthAndHeight(sheep,image)
                photoImage = self.getCachedPhotoImage(self.loadedBlackImages[sheep.size-1])
                canvas.create_image(sheep.x,sheep.y, image=photoImage)
            else:
                image = self.loadedTransposedBlackImages[sheep.size-1]
                self.getWidthAndHeight(sheep,image)
                photoImage = self.getCachedPhotoImage(self.loadedTransposedBlackImages[sheep.size-1])
                canvas.create_image(sheep.x,sheep.y, image=photoImage)

        for sheep in self.activeWhiteSheep:

            if sheep.transposed == False:
                image = self.loadedWhiteImages[sheep.size-1]
                self.getWidthAndHeight(sheep,image)
                photoImage = self.getCachedPhotoImage(self.loadedWhiteImages[sheep.size-1])
                canvas.create_image(sheep.x,sheep.y, image=photoImage)
            else:
                image = self.loadedTransposedWhiteImages[sheep.size-1]
                self.getWidthAndHeight(sheep,image)
                photoImage = self.getCachedPhotoImage(self.loadedTransposedWhiteImages[sheep.size-1])
                canvas.create_image(sheep.x,sheep.y, image=photoImage)

    def drawScore(self,canvas):

        canvas.create_text(40,10,text=f"Black score: {self.blackPlayer.score}")
        canvas.create_text(self.width-40,10,text=f"White score: {self.whitePlayer.score}")
        canvas.create_text(self.width/2,30,text=f"Points to win: {self.pointsToWin}",font='Arial 16 bold')
        if not self.gameStarted:
            canvas.create_text(self.width/2,80,text="Press 'R' when ready to start!",font='Arial 16 bold')

    def getCachedPhotoImage(self, image):
        # stores a cached version of the PhotoImage in the PIL/Pillow image
        if ('cachedPhotoImage' not in image.__dict__):
            image.cachedPhotoImage = ImageTk.PhotoImage(image)
        return image.cachedPhotoImage

    def drawTimers(self,canvas):

        # add this line back in and remove pausedTime in checkWin to make timers disappear after win
        # if not self.blackPlayer.win and not self.whitePlayer.win:

            if self.paused or self.blackPlayer.win or self.whitePlayer.win:

                canvas.create_text(30,70,text='Cooldown')
                canvas.create_text(self.width-30,70,text='Cooldown')

                if self.blackCurrTime == None:
                    canvas.create_arc(10,80,50,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=90,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=210,fill='green')

                elif self.blackCurrTime + self.blackTimePassed + 3 <= self.pausedTime:
                    canvas.create_arc(10,80,50,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=-150,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=-270,fill='green')

                elif self.blackCurrTime + self.blackTimePassed + 2 <= self.pausedTime:
                    canvas.create_arc(10,80,50,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=-150,fill='green')
                
                elif self.blackCurrTime + self.blackTimePassed + 1 <= self.pausedTime:
                    canvas.create_arc(10,80,50,120,extent=120,start=-30,fill='green')

                if self.whiteCurrTime == None:
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=90,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=210,fill='green')

                elif self.whiteCurrTime + self.whiteTimePassed + 3 <= self.pausedTime:
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-150,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-270,fill='green')

                elif self.whiteCurrTime + self.whiteTimePassed + 2 <= self.pausedTime:
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-150,fill='green')
                
                elif self.whiteCurrTime + self.whiteTimePassed + 1 <= self.pausedTime:
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-30,fill='green')

            else:

                canvas.create_text(30,70,text='Cooldown')
                canvas.create_text(self.width-30,70,text='Cooldown')

                if self.blackCurrTime == None:
                    canvas.create_arc(10,80,50,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=90,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=210,fill='green')

                elif self.blackCurrTime + self.blackTimePassed + 3 <= time.time():
                    canvas.create_arc(10,80,50,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=-150,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=-270,fill='green')

                elif self.blackCurrTime + self.blackTimePassed + 2 <= time.time():
                    canvas.create_arc(10,80,50,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,80,50,120,extent=120,start=-150,fill='green')
                
                elif self.blackCurrTime + self.blackTimePassed + 1 <= time.time():
                    canvas.create_arc(10,80,50,120,extent=120,start=-30,fill='green')

                if self.whiteCurrTime == None:
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=90,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=210,fill='green')

                elif self.whiteCurrTime + self.whiteTimePassed + 3 <= time.time():
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-150,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-270,fill='green')

                elif self.whiteCurrTime + self.whiteTimePassed + 2 <= time.time():
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-150,fill='green')
                
                elif self.whiteCurrTime + self.whiteTimePassed + 1 <= time.time():
                    canvas.create_arc(self.width-50,80,self.width-10,120,extent=120,start=-30,fill='green')

    def drawSplash(self,canvas):
            
            photoLogo = self.getCachedPhotoImage(self.scaledLogo)
            canvas.create_image(self.width/2,110, image=photoLogo)

            photoSheep1 = self.getCachedPhotoImage(self.scaledSheep1)
            canvas.create_image(45,self.height-75, image=photoSheep1)

            photoSheep2 = self.getCachedPhotoImage(self.scaledSheep2)
            canvas.create_image(self.width-50,self.height-75, image=photoSheep2)

            centreRow = self.rows//2

            cyn2 = self.getRowCy(centreRow-1) 
            cyn1 = self.getRowCy(centreRow) 
            cy = self.getRowCy(centreRow+1) #real centre
            cy1 = self.getRowCy(centreRow+2)
            cy2 = self.getRowCy(centreRow+3)
            cy3 = self.getRowCy(centreRow+4)
            cy4 = self.getRowCy(centreRow+5)

            canvas.create_text(self.width/2,cyn2,text="Send sheep and cross your opponent's line to score points!",font='Arial 9 bold')
            canvas.create_text(self.width/2,cyn1,text="Smaller sheep are weaker in collisions but count for more points!",font='Arial 9 bold')
            canvas.create_text(self.width/2,cy,text="Once you have activated all the modes you want, press 'S' to start!",font='Arial 9 bold')
            canvas.create_text(self.width/2,cy1,text="Press 'A' to activate/deactivate AI mode",font='Arial 9 bold',fill='blue')
            if self.AImode:
                canvas.create_text(self.width/2,cy2,text="(activated)",font='Arial 9 bold',fill='blue')
            else:
                canvas.create_text(self.width/2,cy2,text="(deactivated)",font='Arial 9 bold',fill='blue')
            canvas.create_text(self.width/2,cy3,text="Press 'D' to activate/deactivate disappear mode",font='Arial 9 bold',fill='red')
            if self.disappearMode:
                canvas.create_text(self.width/2,cy4,text="(activated)",font='Arial 9 bold',fill='red')
            else:
                canvas.create_text(self.width/2,cy4,text="(deactivated)",font='Arial 9 bold',fill='red')

    def redrawAll(self,canvas):
        
        if not self.setupComplete:
            self.drawSplash(canvas)
        
        else:
            self.drawGrassGrid(canvas)
            self.drawButtons(canvas)
            self.drawNextSheep(canvas)
            self.drawScore(canvas)
            self.drawTimers(canvas)
            if self.blackPlayer.win or self.whitePlayer.win:
                self.drawWin(canvas)
            else:
                self.drawActiveSheep(canvas)

if __name__ == '__main__':
    obj = MyApp()