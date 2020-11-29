from cmu_112_graphics import *
import os, random, time

#Super Bump Sheep 

class Sheep():

    def __init__(self,size,x,y,color,transposed,row=None,col=None):
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
        self.width = None
        self.height = None

class Row():

    def __init__(self):
        self.collision = False
        self.collidingSheep = []

class Col():

    def __init__(self):
        self.collision = False
        self.collidingSheep = []

class Player():

    def __init__(self):
        self.score = 0
        self.win = False

# Main class

class MyApp(App):


    def appStarted(self):

        self.rows = 10
        self.cols = 10
        self.topMargin = 120
        self.bottomMargin = 60
        self.sideMargin = 50
        self.colWidth = (self.width-2*self.sideMargin)/self.cols
        self.rowHeight = (self.height-self.topMargin-self.bottomMargin)/self.rows
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
            scaleFactor = 40/width
            self.scaledImage = self.scaleImage(self.tempImage,scaleFactor)
            # print(self.scaledImage.size)
            self.transposedImage = self.scaledImage.transpose(Image.ROTATE_270)
            # print(self.transposedImage.size)
            self.loadedBlackImages.append(self.scaledImage)
            self.loadedTransposedBlackImages.append(self.transposedImage)

        for imagePath in self.whiteSheepImagePaths:
            self.tempImage = self.loadImage(imagePath)
            width, height = self.tempImage.size
            scaleFactor = 40/width
            self.scaledImage = self.scaleImage(self.tempImage,scaleFactor)
            self.transposedImage = self.scaledImage.transpose(Image.ROTATE_270)
            self.loadedWhiteImages.append(self.scaledImage)
            self.loadedTransposedWhiteImages.append(self.transposedImage)

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

    def getCellBounds(self,row,col):

        colWidth = (self.width-2*self.sideMargin)/self.cols
        rowHeight = (self.height-self.topMargin-self.bottomMargin)/self.rows
        x1, y1 = self.sideMargin + col*colWidth, self.topMargin + row*rowHeight
        x2, y2 = x1 + colWidth, y1 + rowHeight
        return x1, y1, x2, y2 

    def createButtons(self):
        
        rowHeight = (self.height-self.topMargin-self.bottomMargin)/self.rows

        for row in range(self.rows):
            
            x2Left = self.sideMargin - 10
            x1Left = x2Left - rowHeight
            
            y1 = self.topMargin + row*rowHeight
            y2 = y1 + rowHeight

            self.vertButtonPositions.append((x1Left,y1,x2Left,y2))

            x1Right = self.width - self.sideMargin + 10
            x2Right = x1Right + rowHeight

            self.vertButtonPositions.append((x1Right,y1,x2Right,y2))

        colWidth = (self.width-2*self.sideMargin)/self.cols

        for col in range(self.cols):

            y2Top = self.topMargin - 10
            y1Top = y2Top - colWidth
            
            x1 = self.sideMargin + col*colWidth
            x2 = x1 + colWidth

            self.horizButtonPositions.append((x1,y1Top,x2,y2Top))

            y1Bottom = self.width - self.bottomMargin + 10
            y2Bottom = y1Bottom + colWidth

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
            self.paused = True

        if not self.blackPlayer.win and not self.whitePlayer.win:

            try:
                
                row = self.rowObjects[int(event.key)-1]
                self.checkSheepReady(row)
                
                if self.blackSheepReady:
                    rowToSend = int(event.key)
                    if 1 <= rowToSend <= 5:
                        size = self.nextBlackSheep.pop(0)
                        x = self.sideMargin + 20
                        y = self.getRowCy(rowToSend)
                        blackSheep = Sheep(size,x,y,rowToSend,'black')
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
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
                    self.checkSheepReady(row)

                    if i % 2 == 0 and self.blackSheepReady:
                        size = self.nextBlackSheep.pop(0)
                        blackSheep = Sheep(size,self.sideMargin+20,cy,'black',False,i//2,None)
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        # print(blackSheep.size)

                    elif i % 2 == 1 and self.whiteSheepReady:
                        size = self.nextWhiteSheep.pop(0)
                        whiteSheep = Sheep(size,self.width-self.sideMargin-20,cy,'white',False,i//2,None)
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        # print(whiteSheep.size)

            for i in range(len(self.horizButtonPositions)):
                
                x1,y1,x2,y2 = self.horizButtonPositions[i]

                cx = (x1+x2)/2
                cy = (y1+y2)/2
                if self.distance(x,y,cx,cy) <= self.colWidth/2:
                    
                    col = self.colObjects[i//2]
                    self.checkSheepReady(col)

                    if i % 2 == 0 and self.blackSheepReady:
                        size = self.nextBlackSheep.pop(0)
                        blackSheep = Sheep(size,cx,self.topMargin+20,'black',True,None,i//2)
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        # print(blackSheep.size)

                    elif i % 2 == 1 and self.whiteSheepReady:
                        size = self.nextWhiteSheep.pop(0)
                        whiteSheep = Sheep(size,cx,self.width-self.bottomMargin-20,'white',True,None,i//2)
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        # print(whiteSheep.size)

    def checkSheepReady(self,rowOrCol):

        if self.blackCurrTime == None or (self.blackCurrTime + 3) <= time.time():
            self.blackSheepReady = True
        else:
            self.blackSheepReady = False
        if self.whiteCurrTime == None or (self.whiteCurrTime + 3) <= time.time():
            self.whiteSheepReady = True
        else:
            self.whiteSheepReady = False

        if rowOrCol in self.rowObjects:
            for sheep in rowOrCol.collidingSheep:
                if sheep.collided == True and sheep.color == 'black' and sheep.x - 20 <= self.sideMargin:
                    self.blackSheepReady = False
                elif sheep.collided == True and sheep.color == 'white' and sheep.x + 20 >= self.width - self.sideMargin:
                    self.whiteSheepReady = False

        elif rowOrCol in self.colObjects:
            for sheep in rowOrCol.collidingSheep:
                if sheep.collided == True and sheep.color == 'black' and sheep.y - 20 <= self.topMargin:
                    self.blackSheepReady = False
                elif sheep.collided == True and sheep.color == 'white' and sheep.y + 20 >= self.width - self.bottomMargin:
                    self.whiteSheepReady = False

    def timerFired(self):
        
        if not self.blackPlayer.win and not self.whitePlayer.win and not self.paused:

            self.generateNextSheep()
            self.moveActiveSheep()
            self.checkCollision()
            self.addPoints()
            self.checkWin()

    
    def addPoints(self):

        for blackSheep in self.activeBlackSheep:

            if blackSheep.x + 20 >= (self.width - self.sideMargin) and blackSheep.row != None:
                
                if blackSheep.collided == True:
                
                    row = self.rowObjects[blackSheep.row]
                    row.collisionNetPower -= blackSheep.size
                    row.collisionTotalPower -= blackSheep.size
                    row.collidingSheep.remove(blackSheep)
                    # print(row.collisionNetPower)
                    self.activeBlackSheep.remove(blackSheep)
                    self.blackPlayer.score += blackSheep.points

                else:

                    self.activeBlackSheep.remove(blackSheep)
                    self.blackPlayer.score += blackSheep.points
            
            elif blackSheep.x + 20 <= self.sideMargin and blackSheep.row != None:

                row = self.rowObjects[blackSheep.row]
                row.collisionNetPower -= blackSheep.size
                # print(row.collisionNetPower)
                row.collisionTotalPower -= blackSheep.size
                row.collidingSheep.remove(blackSheep)
                self.activeBlackSheep.remove(blackSheep)

                if row.collisionTotalPower != 0:
                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    for sheep in row.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5
            
            elif blackSheep.y + 20 >= (self.width - self.bottomMargin) and blackSheep.col != None:
                
                if blackSheep.collided == True:
                
                    col = self.colObjects[blackSheep.col]
                    col.collisionNetPower -= blackSheep.size
                    col.collisionTotalPower -= blackSheep.size
                    col.collidingSheep.remove(blackSheep)
                    # print(col.collisionNetPower)
                    self.activeBlackSheep.remove(blackSheep)
                    self.blackPlayer.score += blackSheep.points

                else:

                    self.activeBlackSheep.remove(blackSheep)
                    self.blackPlayer.score += blackSheep.points

            elif blackSheep.y + 20 <= self.topMargin and blackSheep.col != None:

                col = self.colObjects[blackSheep.col]
                col.collisionNetPower -= blackSheep.size
                # print(col.collisionNetPower)
                col.collisionTotalPower -= blackSheep.size
                col.collidingSheep.remove(blackSheep)
                self.activeBlackSheep.remove(blackSheep)

                if col.collisionTotalPower != 0:
                    speedFactor = col.collisionNetPower/col.collisionTotalPower
                    for sheep in col.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

        for whiteSheep in self.activeWhiteSheep:

            if whiteSheep.x - 20 <= self.sideMargin and whiteSheep.row != None:

                if whiteSheep.collided == True:

                    row = self.rowObjects[whiteSheep.row]
                    row.collisionNetPower += whiteSheep.size
                    row.collisionTotalPower -= whiteSheep.size
                    # print(row.collisionNetPower)
                    row.collidingSheep.remove(whiteSheep)
                    self.activeWhiteSheep.remove(whiteSheep)
                    self.whitePlayer.score += whiteSheep.points
            
                else:

                    self.activeWhiteSheep.remove(whiteSheep)
                    self.whitePlayer.score += whiteSheep.points

            elif whiteSheep.x - 20 >= (self.width - self.sideMargin) and whiteSheep.row != None:

                row = self.rowObjects[whiteSheep.row]
                row.collisionNetPower += whiteSheep.size
                # print(row.collisionNetPower)
                row.collisionTotalPower -= whiteSheep.size
                row.collidingSheep.remove(whiteSheep)
                self.activeWhiteSheep.remove(whiteSheep)

                if row.collisionTotalPower != 0:
                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    for sheep in row.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

            elif whiteSheep.y - 20 <= self.topMargin and whiteSheep.col != None:

                if whiteSheep.collided == True:

                    col = self.colObjects[whiteSheep.col]
                    col.collisionNetPower += whiteSheep.size
                    col.collisionTotalPower -= whiteSheep.size
                    # print(col.collisionNetPower)
                    col.collidingSheep.remove(whiteSheep)
                    self.activeWhiteSheep.remove(whiteSheep)
                    self.whitePlayer.score += whiteSheep.points
            
                else:

                    self.activeWhiteSheep.remove(whiteSheep)
                    self.whitePlayer.score += whiteSheep.points

            elif whiteSheep.y - 20 >= (self.height - self.bottomMargin) and whiteSheep.col != None:

                col = self.colObjects[whiteSheep.col]
                col.collisionNetPower += whiteSheep.size
                # print(col.collisionNetPower)
                col.collisionTotalPower -= whiteSheep.size
                col.collidingSheep.remove(whiteSheep)
                self.activeWhiteSheep.remove(whiteSheep)

                if col.collisionTotalPower != 0:
                    speedFactor = col.collisionNetPower/col.collisionTotalPower
                    for sheep in col.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

    def checkCollision(self):

        for blackSheep in self.activeBlackSheep:

            for otherBlackSheep in self.activeBlackSheep:

                if (blackSheep.row == otherBlackSheep.row != None and blackSheep.collided == False and
                    otherBlackSheep.collided == True and blackSheep.x+20 >= otherBlackSheep.x-20):

                    
                    row = self.rowObjects[blackSheep.row]
                    row.collisionNetPower += blackSheep.size
                    row.collisionTotalPower += blackSheep.size
                    row.collidingSheep.append(blackSheep)
                    # print(row.collisionNetPower)

                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    for sheep in row.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                    blackSheep.collided = True

                elif (blackSheep.col == otherBlackSheep.col != None and blackSheep.collided == False and
                    otherBlackSheep.collided == True and blackSheep.y+20 >= otherBlackSheep.y-20):

                    
                    col = self.colObjects[blackSheep.col]
                    col.collisionNetPower += blackSheep.size
                    col.collisionTotalPower += blackSheep.size
                    col.collidingSheep.append(blackSheep)
                    # print(col.collisionNetPower)

                    speedFactor = col.collisionNetPower/col.collisionTotalPower
                    for sheep in col.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                    blackSheep.collided = True


            for whiteSheep in self.activeWhiteSheep:

                if (blackSheep.col == whiteSheep.col != None and whiteSheep.y - blackSheep.y <= 40
                    and blackSheep.collided == False and whiteSheep.collided == False):
                    
                    blackSheep.collided = True
                    whiteSheep.collided = True

                    col = self.colObjects[blackSheep.col]
                    col.collision = True
                    col.collisionNetPower = blackSheep.size - whiteSheep.size
                    # print(row.collisionNetPower)
                    col.collisionTotalPower = blackSheep.size + whiteSheep.size
                    col.collidingSheep.append(blackSheep)
                    col.collidingSheep.append(whiteSheep)
                    

                    speedFactor = col.collisionNetPower/col.collisionTotalPower
                    blackSheep.speed = speedFactor*5
                    whiteSheep.speed = -blackSheep.speed

                elif (blackSheep.row == whiteSheep.row != None and whiteSheep.x - blackSheep.x <= 40
                    and blackSheep.collided == False and whiteSheep.collided == False):
                    
                    blackSheep.collided = True
                    whiteSheep.collided = True

                    row = self.rowObjects[blackSheep.row]
                    row.collision = True
                    row.collisionNetPower = blackSheep.size - whiteSheep.size
                    # print(row.collisionNetPower)
                    row.collisionTotalPower = blackSheep.size + whiteSheep.size
                    row.collidingSheep.append(blackSheep)
                    row.collidingSheep.append(whiteSheep)
                    

                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    blackSheep.speed = speedFactor*5
                    whiteSheep.speed = -blackSheep.speed

                elif blackSheep.width != None and whiteSheep.width != None and blackSheep.collided == False and whiteSheep.collided == False:

                    if (blackSheep.x - blackSheep.width/2 - whiteSheep.width <= whiteSheep.x - whiteSheep.width/2 <= blackSheep.x + blackSheep.width/2
                    and blackSheep.y - blackSheep.height/2 - whiteSheep.height <= whiteSheep.y - whiteSheep.height/2 <= blackSheep.y + blackSheep.height/2):
                        print("cross collision")

                        if whiteSheep.col != None:
                        
                            self.activeWhiteSheep.remove(whiteSheep)
                            movedWhiteSheep = Sheep(whiteSheep.size,blackSheep.x+40,blackSheep.y,'white',False,blackSheep.row,None)
                            self.activeWhiteSheep.append(movedWhiteSheep)

                        elif blackSheep.col != None:

                            self.activeBlackSheep.remove(blackSheep)
                            movedBlackSheep = Sheep(blackSheep.size,whiteSheep.x-40,whiteSheep.y,'black',False,whiteSheep.row,None)
                            self.activeBlackSheep.append(movedBlackSheep)

        
        for whiteSheep in self.activeWhiteSheep:

            for otherWhiteSheep in self.activeWhiteSheep:

                if (whiteSheep.row == otherWhiteSheep.row != None and whiteSheep.collided == False and
                    otherWhiteSheep.collided == True and whiteSheep.x-20 <= otherWhiteSheep.x+20):

                    row = self.rowObjects[whiteSheep.row]
                    row.collisionNetPower -= whiteSheep.size
                    row.collisionTotalPower += whiteSheep.size
                    row.collidingSheep.append(whiteSheep)
                    # print(row.collisionNetPower)

                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    for sheep in row.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                    whiteSheep.collided = True

                elif (whiteSheep.col == otherWhiteSheep.col != None and whiteSheep.collided == False and
                    otherWhiteSheep.collided == True and whiteSheep.y-20 <= otherWhiteSheep.y+20):

                    col = self.colObjects[whiteSheep.col]
                    col.collisionNetPower -= whiteSheep.size
                    col.collisionTotalPower += whiteSheep.size
                    col.collidingSheep.append(whiteSheep)
                    # print(col.collisionNetPower)

                    speedFactor = col.collisionNetPower/col.collisionTotalPower
                    for sheep in col.collidingSheep:
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

        if self.blackPlayer.score >= 15:
            self.blackPlayer.win = True

        elif self.whitePlayer.score >= 15:
            self.whitePlayer.win = True

    def drawWin(self,canvas):

        if self.blackPlayer.win:
            canvas.create_text(150,150,text='Black wins!!!')
        else:
            canvas.create_text(150,150,text='White wins!!!')

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

        for i in range(len(self.nextBlackSheep)):

            photoImage = self.getCachedPhotoImage(self.loadedBlackImages[self.nextBlackSheep[i]-1])
            canvas.create_image(20+i*40, 40, image=photoImage)

        for i in range(len(self.nextWhiteSheep)):

            photoImage = self.getCachedPhotoImage(self.loadedWhiteImages[self.nextWhiteSheep[i]-1])
            canvas.create_image(self.width-20-i*40, 40, image=photoImage)

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

        if not self.blackPlayer.win or self.whitePlayer.win and not self.paused:

            if self.blackCurrTime == None:
                canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                canvas.create_arc(10,70,50,110,extent=120,start=90,fill='green')
                canvas.create_arc(10,70,50,110,extent=120,start=210,fill='green')

            elif self.blackCurrTime + 3 <= time.time():
                canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                canvas.create_arc(10,70,50,110,extent=120,start=-150,fill='green')
                canvas.create_arc(10,70,50,110,extent=120,start=-270,fill='green')

            elif self.blackCurrTime + 2 <= time.time():
                canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')
                canvas.create_arc(10,70,50,110,extent=120,start=-150,fill='green')
            
            elif self.blackCurrTime + 1 <= time.time():
                canvas.create_arc(10,70,50,110,extent=120,start=-30,fill='green')

            if self.whiteCurrTime == None:
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=90,fill='green')
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=210,fill='green')

            elif self.whiteCurrTime + 3 <= time.time():
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-150,fill='green')
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-270,fill='green')

            elif self.whiteCurrTime + 2 <= time.time():
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-150,fill='green')
            
            elif self.whiteCurrTime + 1 <= time.time():
                canvas.create_arc(self.width-50,70,self.width-10,110,extent=120,start=-30,fill='green')

    def redrawAll(self,canvas):
        self.drawGrid(canvas)
        self.drawButtons(canvas)
        self.drawNextSheep(canvas)
        self.drawActiveSheep(canvas)
        self.drawScore(canvas)
        self.drawTimers(canvas)
        if self.blackPlayer.win or self.whitePlayer.win:
            self.drawWin(canvas)



# def main():
#     # This runs the app
#     runApp(width=400, height=300)

if __name__ == '__main__':
    obj = MyApp()