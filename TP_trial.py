from cmu_112_graphics import *
import os, random, time, math

#Super Bump Sheep 

class Sheep():

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
        self.cols = 9
        self.topMargin = 120
        self.bottomMargin = 70
        self.sideMargin = 70
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

    def getCellBounds(self,row,col):

        x1, y1 = self.sideMargin + col*self.colWidth, self.topMargin + row*self.rowHeight
        x2, y2 = x1 + self.colWidth, y1 + self.rowHeight
        return x1, y1, x2, y2 

    def createButtons(self):

        for row in range(self.rows):
            
            x2Left = self.sideMargin - 10
            x1Left = x2Left - self.rowHeight
            
            y1 = self.topMargin + row*self.rowHeight
            y2 = y1 + self.rowHeight

            self.vertButtonPositions.append((x1Left,y1,x2Left,y2))

            x1Right = self.width - self.sideMargin + 10
            x2Right = x1Right + self.rowHeight

            self.vertButtonPositions.append((x1Right,y1,x2Right,y2))

        for col in range(self.cols):

            y2Top = self.topMargin - 10
            y1Top = y2Top - self.colWidth
            
            x1 = self.sideMargin + col*self.colWidth
            x2 = x1 + self.colWidth

            self.horizButtonPositions.append((x1,y1Top,x2,y2Top))

            y1Bottom = self.height - self.bottomMargin + 10
            y2Bottom = y1Bottom + self.colWidth

            self.horizButtonPositions.append((x1,y1Bottom,x2,y2Bottom))

    def distance(self,x1,y1,x2,y2):

        return ((x1-x2)**2 + (y1-y2)**2)**0.5

    def getRowCy(self,row):

        buttonIndex = row*2 - 1
        x1,y1,x2,y2 = self.vertButtonPositions[buttonIndex]
        cy = (y1+y2)/2

        return cy

    def keyPressed(self,event):

        if event.key == 'p':
            self.paused = not self.paused
            if self.paused:
                self.pausedTime = time.time()
            else:
                self.blackTimePassed += (time.time() - self.pausedTime)
                self.whiteTimePassed += (time.time() - self.pausedTime)

        elif event.key == 'r':
            self.appStarted()

        elif event.key == 'a':
            self.AImode = True
            print('AI activated')

        elif not self.blackPlayer.win and not self.whitePlayer.win:

            try:
                
                row = self.rowObjects[int(event.key)-1]
                self.checkSheepReady()
                
                if self.blackSheepReady:
                    rowToSend = int(event.key)
                    if 1 <= rowToSend <= 9:
                        size = self.nextBlackSheep.pop(0)
                        x = self.sideMargin + 20
                        y = self.getRowCy(rowToSend)
                        blackSheep = Sheep(size,x,y,'black',False,rowToSend-1,None)
                        print(blackSheep.row)
                        print(blackSheep.collided)
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        self.blacktimePassed = 0
                    else:
                        print(f'Press a number from 1 to {self.rows}')

            except:
                print(f'Press a number from 1 to {self.rows}')
            

    def mousePressed(self,event):
        
        if not self.blackPlayer.win and not self.whitePlayer.win and not self.paused:

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
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        self.blackTimePassed = 0

                    elif i % 2 == 1 and self.whiteSheepReady:
                        size = self.nextWhiteSheep.pop(0)

                        image = self.loadedWhiteImages[size-1]
                        width, height = image.size

                        whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,cy,'white',False,i//2,None,width,height)
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
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        self.blackTimePassed = 0

                    elif i % 2 == 1 and self.whiteSheepReady:
                        size = self.nextWhiteSheep.pop(0)

                        image = self.loadedTransposedWhiteImages[size-1]
                        width, height = image.size

                        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-height/2,'white',True,None,i//2,width,height)
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

        # if rowOrCol in self.rowObjects:
        #     for bump in rowOrCol.collisions:
        #         for sheep in bump.collidingSheep:
        #             if sheep.collided == True and sheep.color == 'black' and sheep.x - 20 <= self.sideMargin:
        #                 self.blackSheepReady = False
        #             elif sheep.collided == True and sheep.color == 'white' and sheep.x + 20 >= self.width - self.sideMargin:
        #                 self.whiteSheepReady = False

        # elif rowOrCol in self.colObjects:
        #     for bump in rowOrCol.collisions:
        #         for sheep in bump.collidingSheep:
        #             if sheep.collided == True and sheep.color == 'black' and sheep.y - 20 <= self.topMargin:
        #                 self.blackSheepReady = False
        #             elif sheep.collided == True and sheep.color == 'white' and sheep.y + 20 >= self.width - self.bottomMargin:
        #                 self.whiteSheepReady = False


    def timerFired(self):
        
        if not self.blackPlayer.win and not self.whitePlayer.win and not self.paused:

            self.generateNextSheep()
            self.moveActiveSheep()
            self.checkCollision()
            self.addPoints()
            self.checkWin()
            self.playAI()

    def playAI(self):

        if self.AImode:

            self.checkSheepReady()
            if self.whiteSheepReady:

                # nextBlackSheepSize = self.nextBlackSheep[0]
                # nextBlackSheepPoints = 6 - nextBlackSheepSize
                # if self.blackPlayer.score + nextBlackSheepPoints >= self.pointsToWin:

                nextWhiteSheepSize = self.nextWhiteSheep[0]
                nextWhiteSheepPoints = 6 - nextWhiteSheepSize
                print(nextWhiteSheepPoints)

                #Non-collided blackSheep
                nonCollidedScore = 0
                for blackSheep in self.activeBlackSheep:
                    if blackSheep.collided == False:
                        nonCollidedScore += blackSheep.points

                if nonCollidedScore + self.blackPlayer.score >= self.pointsToWin:
                    #defensive

                    highPriorityRows = []
                    highPriorityCols = []
                    #send on row/col with only black, non-collided
                    for blackSheep in self.activeBlackSheep:
                        if blackSheep.collided == False:
                            #checkRow for white
                            if blackSheep.row != None:
                                highPriorityRows.append(blackSheep.row)
                            elif blackSheep.col != None:
                                highPriorityCols.append(blackSheep.col)

                    lowPriorityRows = set()
                    lowPriorityCols = set()

                    for whiteSheep in self.activeWhiteSheep:
                        if whiteSheep.row in highPriorityRows:
                            lowPriorityRows.add(whiteSheep.row)
                            highPriorityRows.remove(whiteSheep.row)

                    for whiteSheep in self.activeWhiteSheep:
                        if whiteSheep.col in highPriorityCols:
                            lowPriorityCols.add(whiteSheep.col)
                            highPriorityCols.remove(whiteSheep.col)

                    lowPriorityRows = list(lowPriorityRows)
                    lowPriorityCols = list(lowPriorityCols)

                    if len(highPriorityRows) > 0:

                        gen = random.randint(1,len(highPriorityRows))
                        rowToSend = highPriorityRows[gen-1]
                        size = self.nextWhiteSheep.pop(0)
                        y = self.getRowCy(rowToSend)
                        whiteSheep = Sheep(size,self.width-self.sideMargin-20,y,'white',False,rowToSend,None)
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        self.whiteTimePassed = 0

                    elif len(highPriorityCols) > 0:

                        gen = random.randint(1,len(highPriorityCols))
                        colToSend = highPriorityCols[gen-1]
                        size = self.nextWhiteSheep.pop(0)
                        cx = self.getColCx(colToSend)
                        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-20,'white',True,None,colToSend)
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        self.whiteTimePassed = 0

                    elif len(lowPriorityRows) > 0:
                        gen = random.randint(1,len(lowPriorityRows))
                        rowToSend = lowPriorityRows[gen-1]
                        size = self.nextWhiteSheep.pop(0)
                        y = self.getRowCy(rowToSend)
                        whiteSheep = Sheep(size,self.width-self.sideMargin-20,y,'white',False,rowToSend,None)
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        self.whiteTimePassed = 0
                    
                    elif len(lowPriorityCols) > 0:

                        gen = random.randint(1,len(lowPriorityCols))
                        colToSend = lowPriorityCols[gen-1]
                        size = self.nextWhiteSheep.pop(0)
                        cx = self.getColCx(colToSend)
                        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-20,'white',True,None,colToSend)
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        self.whiteTimePassed = 0

                elif self.whitePlayer.score + nextWhiteSheepPoints >= self.pointsToWin:

                    knownEmptyRows = self.getKnownEmptyRows()
                    knownEmptyCols = self.getKnownEmptyCols()
                    
                    knownEmptyRowsCols = len(knownEmptyRows) + len(knownEmptyCols)
                    if knownEmptyRowsCols > 0:
                        gen = random.randint(1,knownEmptyRowsCols)
                        if gen <= len(knownEmptyRows):
                            rowToSend = knownEmptyRows[gen-1]
                            size = self.nextWhiteSheep.pop(0)
                            y = self.getRowCy(rowToSend)
                            whiteSheep = Sheep(size,self.width-self.sideMargin-20,y,'white',False,rowToSend,None)
                            self.activeWhiteSheep.append(whiteSheep)
                            self.whiteCurrTime = time.time()
                            self.whiteTimePassed = 0
                        else:
                            colToSend = knownEmptyCols[gen-len(knownEmptyRows)-1]
                            size = self.nextWhiteSheep.pop(0)
                            cx = self.getColCx(colToSend)
                            whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-20,'white',True,None,colToSend)
                            self.activeWhiteSheep.append(whiteSheep)
                            self.whiteCurrTime = time.time()
                            self.whiteTimePassed = 0

                    else:

                        noCollisionRows = []
                        for row in self.rowObjects:
                            if row.collisions == []:
                                noCollisionRows.append(row)

                        noCollisionCols = []
                        for col in self.colObjects:
                            if col.collisions == []:
                                noCollisionCols.append(col)

                        noCollisionRowsCols = len(noCollisionRows) + len(noCollisionCols)
                        if noCollisionRowsCols > 0:
                            gen = random.randint(1,noCollisionRowsCols)
                            if gen <= len(noCollisionRows):
                                rowToSend = noCollisionRows[gen-1]
                                size = self.nextWhiteSheep.pop(0)
                                y = self.getRowCy(rowToSend)
                                whiteSheep = Sheep(size,self.width-self.sideMargin-20,y,'white',False,rowToSend,None)
                                self.activeWhiteSheep.append(whiteSheep)
                                self.whiteCurrTime = time.time()
                                self.whiteTimePassed = 0
                            else:
                                colToSend = noCollisionCols[gen-len(knownEmptyRows)-1]
                                size = self.nextWhiteSheep.pop(0)
                                cx = self.getColCx(colToSend)
                                whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-20,'white',True,None,colToSend)
                                self.activeWhiteSheep.append(whiteSheep)
                                self.whiteCurrTime = time.time()
                                self.whiteTimePassed = 0

                        else:
                            
                            bestRow = None
                            bestCollision = None
                            for row in self.rowObjects:
                                
                                bestBump = None
                                for bump in row.collisions:
                                    if bestBump == None:
                                        bestBump = bump.collisionNetPower
                                    elif bump.collisionNetPower < bestBump:
                                        bestBump = bump.collisionNetPower

                                if bestBump != None and bestRow == None:
                                    bestRow = row
                                    bestCollision = bestBump
                                elif bestBump != None and bestBump < bestCollision:
                                    bestRow = row
                                    bestCollision = bestBump

                            if bestRow != None:
                                size = self.nextWhiteSheep.pop(0)
                                y = self.getRowCy(bestRow)
                                whiteSheep = Sheep(size,self.width-self.sideMargin-20,y,'white',False,bestRow,None)
                                self.activeWhiteSheep.append(whiteSheep)
                                self.whiteCurrTime = time.time()
                                self.whiteTimePassed = 0

                            else:

                                bestCol = None
                                bestCollision = None
                                for col in self.colObjects:
                                    
                                    bestBump = None
                                    for bump in col.collisions:
                                        if bestBump == None:
                                            bestBump = bump.collisionNetPower
                                        elif bump.collisionNetPower < bestBump:
                                            bestBump = bump.collisionNetPower

                                    if bestBump != None and bestCol == None:
                                        bestCol = col
                                        bestCollision = bestBump
                                    elif bestBump != None and bestBump < bestCollision:
                                        bestCol = col
                                        bestCollision = bestBump

                                if bestCol != None:
                                    size = self.nextWhiteSheep.pop(0)
                                    cx = self.getRowCx(bestCol)
                                    whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-20,'white',True,None,bestCol)
                                    self.activeWhiteSheep.append(whiteSheep)
                                    self.whiteCurrTime = time.time()
                                    self.whiteTimePassed = 0

                                else:
                                    totalRowCols = self.rows + self.cols
                                    gen = random.randint(1,totalRow&Cols)
                                    if gen <= self.rows:
                                        rowToSend = gen
                                        size = self.nextWhiteSheep.pop(0)
                                        y = self.getRowCy(rowToSend)
                                        whiteSheep = Sheep(size,self.width-self.sideMargin-20,y,'white',False,rowToSend,None)
                                        self.activeWhiteSheep.append(whiteSheep)
                                        self.whiteCurrTime = time.time()
                                        self.whiteTimePassed = 0
                                    else:
                                        colToSend = gen-self.rows
                                        size = self.nextWhiteSheep.pop(0)
                                        x = self.getColCx(colToSend)
                                        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-20,'white',True,None,colToSend)
                                        self.activeWhiteSheep.append(whiteSheep)
                                        self.whiteCurrTime = time.time()
                                        self.whiteTimePassed = 0

    def getColCx(self,col):

        index = col*2+1
        x1,y1,x2,y2 = self.horizButtonPositions[index]
        cx = (x1+x2)/2

        return cx

    def getKnownEmptyRows(self):

        emptyRows = [i for i in range(self.rows)]

        for blackSheep in self.activeBlackSheep:
            if blackSheep.row in emptyRows:
                emptyRows.remove(blackSheep.row)

        for whiteSheep in self.activeWhiteSheep:
            if whiteSheep.row in emptyRows:
                emptyRows.remove(whiteSheep.row)

        return emptyRows

    def getKnownEmptyCols(self):

        emptyCols = [i for i in range(self.rows)]

        for blackSheep in self.activeBlackSheep:
            if blackSheep.col in emptyCols:
                emptyCols.remove(blackSheep.col)

        for whiteSheep in self.activeWhiteSheep:
            if whiteSheep.col in emptyCols:
                emptyCols.remove(whiteSheep.col)

        return emptyCols



    def addPoints(self):

        for blackSheep in self.activeBlackSheep:

            if blackSheep.x + blackSheep.width/2 >= (self.width - self.sideMargin) and blackSheep.row != None:

                if blackSheep.collided == True:

                    #make whiteSheep.collided = False
                    row = self.rowObjects[blackSheep.row]
                    for bump in row.collisions:
                        if blackSheep in bump.collidingSheep:
                            bump.collisionNetPower -= blackSheep.size
                            bump.collisionTotalPower -= blackSheep.size
                            bump.collidingSheep.remove(blackSheep)
                            self.activeBlackSheep.remove(blackSheep)
                            self.blackPlayer.score += blackSheep.points

                    if bump.collisionTotalPower != 0:
                        speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'black':
                                sheep.speed = speedFactor*5
                            else:
                                sheep.speed = -speedFactor*5
            
                else:

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
                        self.blackPlayer.score += blackSheep.points

                if bump.collisionTotalPower != 0:
                    speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                    for sheep in bump.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                bump.doneColliding = True
                for sheep in bump.collidingSheep:
                    if sheep.color == 'black':
                        bump.doneColliding = False
                
                print(bump.doneColliding)
                if bump.doneColliding:
                    for whiteSheep in bump.collidingSheep:
                        whiteSheep.collided = False
            
            elif blackSheep.y + blackSheep.height/2 >= (self.width - self.bottomMargin) and blackSheep.col != None:
                
                if blackSheep.collided == True:

                    col = self.colObjects[blackSheep.col]
                    for bump in col.collisions:
                        if blackSheep in bump.collidingSheep:
                            bump.collisionNetPower -= blackSheep.size
                            bump.collisionTotalPower -= blackSheep.size
                            bump.collidingSheep.remove(blackSheep)
                            self.activeBlackSheep.remove(blackSheep)

                    if bump.collisionTotalPower != 0:
                        speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'black':
                                sheep.speed = speedFactor*5
                            else:
                                sheep.speed = -speedFactor*5
            
                else:

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

                if bump.collisionTotalPower != 0:
                    speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                    for sheep in bump.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5
                
                bump.doneColliding = True
                for sheep in bump.collidingSheep:
                    if sheep.color == 'black':
                        bump.doneColliding = False
                
                print(bump.doneColliding)
                if bump.doneColliding:
                    for whiteSheep in bump.collidingSheep:
                        whiteSheep.collided = False

        for whiteSheep in self.activeWhiteSheep:

            if whiteSheep.x - whiteSheep.width/2 <= self.sideMargin and whiteSheep.row != None:

                if whiteSheep.collided == True:

                    row = self.rowObjects[whiteSheep.row]
                    for bump in row.collisions:
                        if whiteSheep in bump.collidingSheep:
                            bump.collisionNetPower += whiteSheep.size
                            bump.collisionTotalPower -= whiteSheep.size
                            bump.collidingSheep.remove(whiteSheep)
                            self.activeWhiteSheep.remove(whiteSheep)
                            self.whitePlayer.score += whiteSheep.points

                    if bump.collisionTotalPower != 0:
                        speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'black':
                                sheep.speed = speedFactor*5
                            else:
                                sheep.speed = -speedFactor*5
            
                else:

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
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                bump.doneColliding = True
                for sheep in bump.collidingSheep:
                    if sheep.color == 'white':
                        bump.doneColliding = False
                
                print(bump.doneColliding)
                if bump.doneColliding:
                    for blackSheep in bump.collidingSheep:
                        blackSheep.collided = False

            elif whiteSheep.y - whiteSheep.height/2 <= self.topMargin and whiteSheep.col != None:

                if whiteSheep.collided == True:
                    
                    col = self.colObjects[whiteSheep.col]
                    for bump in col.collisions:
                        if whiteSheep in bump.collidingSheep:
                            bump.collisionNetPower += whiteSheep.size
                            bump.collisionTotalPower -= whiteSheep.size
                            bump.collidingSheep.remove(whiteSheep)
                            self.activeWhiteSheep.remove(whiteSheep)
                            self.whitePlayer.score += whiteSheep.points

                    if bump.collisionTotalPower != 0:
                        speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                        for sheep in bump.collidingSheep:
                            if sheep.color == 'black':
                                sheep.speed = speedFactor*5
                            else:
                                sheep.speed = -speedFactor*5
            
                else:

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
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                bump.doneColliding = True
                for sheep in bump.collidingSheep:
                    if sheep.color == 'white':
                        bump.doneColliding = False
                
                print(bump.doneColliding)
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
                                    sheep.speed = speedFactor*5
                                else:
                                    sheep.speed = -speedFactor*5

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
                                    sheep.speed = speedFactor*5
                                else:
                                    sheep.speed = -speedFactor*5

                    blackSheep.collided = True

            for whiteSheep in self.activeWhiteSheep:


                if (blackSheep.col == whiteSheep.col != None and whiteSheep.y - blackSheep.y <= whiteSheep.height/2+blackSheep.height/2
                    and blackSheep.collided == False and whiteSheep.collided == False):
                    
                    blackSheep.collided = True
                    whiteSheep.collided = True

                    bump = Bump()
                    bump.collidingSheep.append(blackSheep)
                    bump.collidingSheep.append(whiteSheep)

                    bump.collisionNetPower = blackSheep.size - whiteSheep.size
                    bump.collisionTotalPower = blackSheep.size + whiteSheep.size
                    speedFactor = bump.collisionNetPower/bump.collisionTotalPower
                    blackSheep.speed = speedFactor*5
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
                    blackSheep.speed = speedFactor*5
                    whiteSheep.speed = -blackSheep.speed

                    row = self.rowObjects[blackSheep.row]
                    row.collisions.append(bump)

                # elif (blackSheep.width != None and whiteSheep.width != None and blackSheep.collided == False and whiteSheep.collided == False):
                elif (((blackSheep.row == None and whiteSheep.row != None) or (blackSheep.row != None and whiteSheep.row == None))
                and blackSheep.collided == False and whiteSheep.collided == False):

                    if (blackSheep.x - blackSheep.width/2 - whiteSheep.width <= whiteSheep.x - whiteSheep.width/2 <= blackSheep.x + blackSheep.width/2
                    and blackSheep.y - blackSheep.height/2 - whiteSheep.height <= whiteSheep.y - whiteSheep.height/2 <= blackSheep.y + blackSheep.height/2):
                        print("cross collision")

                        if whiteSheep.col != None:
                        
                            self.activeWhiteSheep.remove(whiteSheep)

                            movedWhiteSheep = Sheep(whiteSheep.size,blackSheep.x+blackSheep.width/2+whiteSheep.width/2,blackSheep.y,'white',False,blackSheep.row,None,whiteSheep.width,whiteSheep.height)
                            self.activeWhiteSheep.append(movedWhiteSheep)

                        elif blackSheep.col != None:

                            self.activeBlackSheep.remove(blackSheep)
                            movedBlackSheep = Sheep(blackSheep.size,whiteSheep.x-whiteSheep.width/2-blackSheep.width/2,whiteSheep.y,'black',False,whiteSheep.row,None,blackSheep.width,blackSheep.height)
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
                                            sheep.speed = speedFactor*5
                                        else:
                                            sheep.speed = -speedFactor*5
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
                                    sheep.speed = speedFactor*5
                                else:
                                    sheep.speed = -speedFactor*5

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
                                    sheep.speed = speedFactor*5
                                else:
                                    sheep.speed = -speedFactor*5

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

        elif self.whitePlayer.score >= self.pointsToWin:
            self.whitePlayer.win = True

    def drawWin(self,canvas):

        if self.blackPlayer.win:
            canvas.create_text(250,243,text='Black wins!!!',font='Arial 24 bold',fill='orange')
            canvas.create_text(250,280,text='Press "R" to restart',font='Arial 16 bold',fill='orange')
        else:
            canvas.create_text(250,243,text='White wins!!!',font='Arial 24 bold',fill='orange')
            canvas.create_text(250,280,text='Press "R" to restart',font='Arial 16 bold',fill='orange')

    def drawButtons(self,canvas):

        for x1,y1,x2,y2 in self.vertButtonPositions:

            canvas.create_oval(x1,y1,x2,y2,fill='grey')
            canvas.create_text((x1+x2)//2,(y1+y2)//2,text='GO!')

        for x1,y1,x2,y2 in self.horizButtonPositions:

            canvas.create_oval(x1,y1,x2,y2,fill='grey')
            canvas.create_text((x1+x2)//2,(y1+y2)//2,text='GO!')

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

            photoImage = self.getCachedPhotoImage(self.loadedBlackImages[self.nextBlackSheep[i]-1])
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

        canvas.create_text(50,10,text=f"Black score: {self.blackPlayer.score}")
        canvas.create_text(self.width-50,10,text=f"White score: {self.whitePlayer.score}")


    def getCachedPhotoImage(self, image):
        # stores a cached version of the PhotoImage in the PIL/Pillow image
        if ('cachedPhotoImage' not in image.__dict__):
            image.cachedPhotoImage = ImageTk.PhotoImage(image)
        return image.cachedPhotoImage

    def drawTimers(self,canvas):

        if not self.blackPlayer.win and not self.whitePlayer.win:

            if self.paused:

                if self.blackCurrTime == None:
                    canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=90,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=210,fill='green')

                elif self.blackCurrTime + self.blackTimePassed + 3 <= self.pausedTime:
                    canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=-150,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=-270,fill='green')

                elif self.blackCurrTime + self.blackTimePassed + 2 <= self.pausedTime:
                    canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=-150,fill='green')
                
                elif self.blackCurrTime + self.blackTimePassed + 1 <= self.pausedTime:
                    canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')

                if self.whiteCurrTime == None:
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=90,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=210,fill='green')

                elif self.whiteCurrTime + self.whiteTimePassed + 3 <= self.pausedTime:
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-150,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-270,fill='green')

                elif self.whiteCurrTime + self.whiteTimePassed + 2 <= self.pausedTime:
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-150,fill='green')
                
                elif self.whiteCurrTime + self.whiteTimePassed + 1 <= self.pausedTime:
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')

            else:

                if self.blackCurrTime == None:
                    canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=90,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=210,fill='green')

                elif self.blackCurrTime + self.blackTimePassed + 3 <= time.time():
                    canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=-150,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=-270,fill='green')

                elif self.blackCurrTime + self.blackTimePassed + 2 <= time.time():
                    canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(10,70,50,110,extent=120,start=-150,fill='green')
                
                elif self.blackCurrTime + self.blackTimePassed + 1 <= time.time():
                    canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')

                if self.whiteCurrTime == None:
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=90,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=210,fill='green')

                elif self.whiteCurrTime + self.whiteTimePassed + 3 <= time.time():
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-150,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-270,fill='green')

                elif self.whiteCurrTime + self.whiteTimePassed + 2 <= time.time():
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-150,fill='green')
                
                elif self.whiteCurrTime + self.whiteTimePassed + 1 <= time.time():
                    canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')

    # def drawSplash(self,canvas):

    #     canvas.create_text(250,50,text="Get your sheep to opponent's side of the board to score points!",font='Arial 12 bold')
    #     canvas.create_text(250,75,text="Beware of collisions!",font='Arial 12 bold')
    #     canvas.create_text(250,100,text='Press "A" to select AI mode',font='Arial 12 bold')
    #     canvas.create_text(250,125,text='Press "M" to select multiplayer mode',font='Arial 12 bold')

    #     canvas.create_text(250,175,text='For multiplayer mode:',font='Arial 12 bold')
    #     canvas.create_text(250,200,text='Black can send sheep on rows using "1","2",...,"9"',font='Arial 12 bold')
    #     canvas.create_text(250,225,text='Black can send sheep on columns using "Q","W","E"...,"P"',font='Arial 12 bold')
    #     canvas.create_text(250,250,text='White can send sheep on rows/columns',font='Arial 12 bold')
    #     canvas.create_text(250,275,text='by clicking "GO!" buttons next to grid',font='Arial 12 bold')


    def redrawAll(self,canvas):
        self.drawGrid(canvas)
        self.drawButtons(canvas)
        self.drawNextSheep(canvas)
        if not self.blackPlayer.win and not self.whitePlayer.win:
            self.drawActiveSheep(canvas)
        self.drawScore(canvas)
        self.drawTimers(canvas)
        if self.blackPlayer.win or self.whitePlayer.win:
            self.drawWin(canvas)
        # self.drawSplash(canvas)

if __name__ == '__main__':
    obj = MyApp()