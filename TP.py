from cmu_112_graphics import *
import os, random, time

#Super Bump Sheep 

class Sheep():

    def __init__(self,size,x,y,row,color):
        self.size = size
        self.points = 6 - size
        self.x = x
        self.y = y
        self.row = row
        self.collided = False
        self.speed = 5
        self.color = color

class Row():

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

        self.rows = 5
        self.cols = 15
        self.topMargin = 150
        self.sideMargin = 30
        self.rowObjects = []
        
        for i in range(self.rows):
            row = Row()
            self.rowObjects.append(row)

        self.sheepImagePaths = []

        for image in os.listdir('sheep'):
            self.sheepImagePaths.append('sheep/'+image)
        
        
        self.blackSheepImagePaths = self.sheepImagePaths[:5]
        self.whiteSheepImagePaths = self.sheepImagePaths[5:]
        
        self.loadedBlackImages = []
        self.loadedWhiteImages = []

        for imagePath in self.blackSheepImagePaths:
            self.tempImage = self.loadImage(imagePath)
            width, height = self.tempImage.size
            scaleFactor = 40/width
            self.scaledImage = self.scaleImage(self.tempImage,scaleFactor)
            self.loadedBlackImages.append(self.scaledImage)

        for imagePath in self.whiteSheepImagePaths:
            self.tempImage = self.loadImage(imagePath)
            width, height = self.tempImage.size
            scaleFactor = 40/width
            self.scaledImage = self.scaleImage(self.tempImage,scaleFactor)
            self.loadedWhiteImages.append(self.scaledImage)


        self.nextBlackSheep = []
        self.nextWhiteSheep = []

        self.activeBlackSheep = []
        self.activeWhiteSheep = []

        self.buttonPositions = []
        self.createButtons()
        
        self.blackPlayer = Player()
        self.whitePlayer = Player()

        self.blackCurrTime = None
        self.whiteCurrTime = None

    def getCellBounds(self,row,col):
        colWidth = (self.width-2*self.sideMargin)/self.cols
        rowHeight = (self.height-self.topMargin)/self.rows
        x1, y1 = self.sideMargin + col*colWidth, self.topMargin + row*rowHeight
        x2, y2 = x1 + colWidth, y1 + rowHeight
        return x1, y1, x2, y2 

    def createButtons(self):
        
        rowHeight = (self.height-self.topMargin)/self.rows

        for row in range(self.rows):
            
            y1 = self.topMargin + row*rowHeight
            y2 = y1 + rowHeight

            x1Left = 0
            x2Left = self.sideMargin

            self.buttonPositions.append((x1Left,y1,x2Left,y2))

            x1Right = self.width - self.sideMargin
            x2Right = self.width

            self.buttonPositions.append((x1Right,y1,x2Right,y2))

    def distance(self,x1,y1,x2,y2):

        return ((x1-x2)**2 + (y1-y2)**2)**0.5

    def getRowCy(self,row):

        buttonIndex = row*2 - 1
        x1,y1,x2,y2 = self.buttonPositions[buttonIndex]
        cy = (y1+y2)/2

        return cy

    def keyPressed(self,event):

        try:
            if self.blackCurrTime == None or (self.blackCurrTime + 3) <= time.time():
                self.blackSheepReady = True
            else:
                self.blackSheepReady = False

            row = self.rowObjects[int(event.key)-1]
            for sheep in row.collidingSheep:
                if sheep.collided == True and sheep.color == 'black' and sheep.x - 20 <= self.sideMargin:
                    self.blackSheepReady = False
            
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
        
        if not self.blackPlayer.win and not self.whitePlayer.win:

            x,y = event.x,event.y

            if self.blackCurrTime == None or (self.blackCurrTime + 3) <= time.time():
                self.blackSheepReady = True
            else:
                self.blackSheepReady = False
            if self.whiteCurrTime == None or (self.whiteCurrTime + 3) <= time.time():
                self.whiteSheepReady = True
            else:
                self.whiteSheepReady = False
            
            for i in range(len(self.buttonPositions)):
                
                x1,y1,x2,y2 = self.buttonPositions[i]

                cx = (x1+x2)/2
                cy = (y1+y2)/2
                if self.distance(x,y,cx,cy) <= self.sideMargin/2:
                    
                    row = self.rowObjects[i//2]
                    for sheep in row.collidingSheep:
                        if sheep.collided == True and sheep.color == 'black' and sheep.x - 20 <= self.sideMargin:
                            self.blackSheepReady = False
                        elif sheep.collided == True and sheep.color == 'white' and sheep.x + 20 >= self.width - self.sideMargin:
                            self.whiteSheepReady = False

                    if i % 2 == 0 and self.blackSheepReady:
                        size = self.nextBlackSheep.pop(0)
                        blackSheep = Sheep(size,x2+20,cy,i//2,'black')
                        self.activeBlackSheep.append(blackSheep)
                        self.blackCurrTime = time.time()
                        # print(blackSheep.size)

                    elif i % 2 == 1 and self.whiteSheepReady:
                        size = self.nextWhiteSheep.pop(0)
                        whiteSheep = Sheep(size,x1-20,cy,i//2,'white')
                        self.activeWhiteSheep.append(whiteSheep)
                        self.whiteCurrTime = time.time()
                        # print(whiteSheep.size)

                
    def timerFired(self):
        
        self.generateNextSheep()
        self.moveActiveSheep()
        self.checkCollision()
        self.addPoints()
        self.checkWin()

    
    def addPoints(self):

        for blackSheep in self.activeBlackSheep:

            if blackSheep.x + 20 >= (self.width - self.sideMargin):
                
                if blackSheep.collided == True:
                
                    row = self.rowObjects[blackSheep.row]
                    row.collisionNetPower -= blackSheep.size
                    row.collisionTotalPower -= blackSheep.size
                    row.collidingSheep.remove(blackSheep)
                    print(row.collisionNetPower)
                    self.activeBlackSheep.remove(blackSheep)
                    self.blackPlayer.score += blackSheep.points

                else:

                    self.activeBlackSheep.remove(blackSheep)
                    self.blackPlayer.score += blackSheep.points
            
            elif blackSheep.x + 20 <= self.sideMargin:

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


        for whiteSheep in self.activeWhiteSheep:

            if whiteSheep.x - 20 <= self.sideMargin:

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

            elif whiteSheep.x - 20 >= (self.width - self.sideMargin):

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

    def checkCollision(self):

        for blackSheep in self.activeBlackSheep:

            for otherBlackSheep in self.activeBlackSheep:

                if (blackSheep.row == otherBlackSheep.row and blackSheep.collided == False and
                    otherBlackSheep.collided == True and blackSheep.x+20 >= otherBlackSheep.x-20):

                    
                    row = self.rowObjects[blackSheep.row]
                    row.collisionNetPower += blackSheep.size
                    row.collisionTotalPower += blackSheep.size
                    row.collidingSheep.append(blackSheep)
                    print(row.collisionNetPower)

                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    for sheep in row.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                    blackSheep.collided = True


            for whiteSheep in self.activeWhiteSheep:

                if (blackSheep.y == whiteSheep.y and whiteSheep.x - blackSheep.x <= 40
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
        
        for whiteSheep in self.activeWhiteSheep:

            for otherWhiteSheep in self.activeWhiteSheep:

                if (whiteSheep.row == otherWhiteSheep.row and whiteSheep.collided == False and
                    otherWhiteSheep.collided == True and whiteSheep.x-20 <= otherWhiteSheep.x+20):

                    row = self.rowObjects[whiteSheep.row]
                    row.collisionNetPower -= whiteSheep.size
                    row.collisionTotalPower += whiteSheep.size
                    row.collidingSheep.append(whiteSheep)
                    print(row.collisionNetPower)

                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    for sheep in row.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                    whiteSheep.collided = True

    def moveActiveSheep(self):

        if not self.blackPlayer.win and not self.whitePlayer.win:

            for sheep in self.activeBlackSheep:

                sheep.x += sheep.speed

            for sheep in self.activeWhiteSheep:

                sheep.x -= sheep.speed

    def generateNextSheep(self):
        
        while len(self.nextBlackSheep) < 3:
            randomSize = random.randint(1,5)
            self.nextBlackSheep.append(randomSize)

        while len(self.nextWhiteSheep) < 3:
            randomSize = random.randint(1,5)
            self.nextWhiteSheep.append(randomSize)

    def checkWin(self):

        if self.blackPlayer.score >= 50:
            self.blackPlayer.win = True

        elif self.whitePlayer.score >= 50:
            self.whitePlayer.win = True

    def drawButtons(self,canvas):

        for x1,y1,x2,y2 in self.buttonPositions:

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

    def drawActiveSheep(self,canvas):

        for sheep in self.activeBlackSheep:

            photoImage = self.getCachedPhotoImage(self.loadedBlackImages[sheep.size-1])
            canvas.create_image(sheep.x,sheep.y, image=photoImage)

        for sheep in self.activeWhiteSheep:

            photoImage = self.getCachedPhotoImage(self.loadedWhiteImages[sheep.size-1])
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

        if self.blackCurrTime == None:
            canvas.create_arc(80,70,120,110,extent=120,start=-30,fill='green')
            canvas.create_arc(80,70,120,110,extent=120,start=90,fill='green')
            canvas.create_arc(80,70,120,110,extent=120,start=210,fill='green')

        elif self.blackCurrTime + 3 <= time.time():
            canvas.create_arc(80,70,120,110,extent=120,start=-30,fill='green')
            canvas.create_arc(80,70,120,110,extent=120,start=-150,fill='green')
            canvas.create_arc(80,70,120,110,extent=120,start=-270,fill='green')

        elif self.blackCurrTime + 2 <= time.time():
            canvas.create_arc(80,70,120,110,extent=120,start=-30,fill='green')
            canvas.create_arc(80,70,120,110,extent=120,start=-150,fill='green')
        
        elif self.blackCurrTime + 1 <= time.time():
            canvas.create_arc(80,70,120,110,extent=120,start=-30,fill='green')

        if self.whiteCurrTime == None:
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=-30,fill='green')
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=90,fill='green')
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=210,fill='green')

        elif self.whiteCurrTime + 3 <= time.time():
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=-30,fill='green')
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=-150,fill='green')
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=-270,fill='green')

        elif self.whiteCurrTime + 2 <= time.time():
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=-30,fill='green')
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=-150,fill='green')
        
        elif self.whiteCurrTime + 1 <= time.time():
            canvas.create_arc(self.width-120,70,self.width-80,110,extent=120,start=-30,fill='green')

    def redrawAll(self,canvas):
        self.drawGrid(canvas)
        self.drawButtons(canvas)
        self.drawNextSheep(canvas)
        self.drawActiveSheep(canvas)
        self.drawScore(canvas)
        self.drawTimers(canvas)



# def main():
#     # This runs the app
#     runApp(width=400, height=300)

if __name__ == '__main__':
    obj = MyApp()