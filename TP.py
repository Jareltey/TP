from cmu_112_graphics import *
import os, random

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

    def __eq__(self,other):
        if isinstance(other,Sheep) and self.x == other.x and self.y == other.y:
            return True

class Row():

    def __init__(self):
        self.collision = False
        self.collidingSheep = []

class Collison():

    def __init__(self,xleft,xright):
        self.xleft = xleft
        self.xright = xright




#Create grid for sheep

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
        # print(self.blackSheepImagePaths)
        self.whiteSheepImagePaths = self.sheepImagePaths[5:]
        # print(self.whiteSheepImagePaths)

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
        self.rowBounds = []
        self.createButtons()
        

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

            self.rowBounds.append((y1,y2))

    def distance(self,x1,y1,x2,y2):

        return ((x1-x2)**2 + (y1-y2)**2)**0.5

    def keyPressed(self,event):

        pass

    def mousePressed(self,event):
        
        x,y = event.x,event.y
        
        for i in range(len(self.buttonPositions)):
            
            x1,y1,x2,y2 = self.buttonPositions[i]

            cx = (x1+x2)/2
            cy = (y1+y2)/2
            if self.distance(x,y,cx,cy) <= self.sideMargin/2:
                
                if i % 2 == 0:
                    size = self.nextBlackSheep.pop(0)
                    blackSheep = Sheep(size,x2+20,cy,i//2,'black')
                    print(i//2)
                    self.activeBlackSheep.append(blackSheep)

                else:
                    size = self.nextWhiteSheep.pop(0)
                    whiteSheep = Sheep(size,x1-20,cy,i//2,'white')
                    print(i//2)
                    self.activeWhiteSheep.append(whiteSheep)

                
    def timerFired(self):
        
        self.generateNextSheep()
        self.moveActiveSheep()
        self.checkCollision()

    
    def checkCollision(self):

        for blackSheep in self.activeBlackSheep:


            for otherBlackSheep in self.activeBlackSheep:

                if (blackSheep != otherBlackSheep and blackSheep.row == otherBlackSheep.row and 
                    otherBlackSheep.collided == True and blackSheep.x+20 >= otherBlackSheep.collisionBound):

                    row = self.rowObjects[blackSheep.row]
                    row.collisionNetPower += blackSheep.size
                    row.collisionTotalPower += blackSheep.size
                    row.collidingSheep.append(blackSheep)

                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    for sheep in row.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                    blackSheep.collisionBound = blackSheep.x-20
                    
                    blackSheep.friendlyCollided = True
                    blackSheep.collided = True

                    print('Black Friendly collided')

            for whiteSheep in self.activeWhiteSheep:

                if blackSheep.y == whiteSheep.y and whiteSheep.x - blackSheep.x <= 40:
                    
                    blackSheep.collided = True
                    whiteSheep.collided = True

                    blackSheep.collisionBound = blackSheep.x-20
                    whiteSheep.collisionBound = whiteSheep.x+20

                    row = self.rowObjects[blackSheep.row]
                    row.collision = True
                    row.collisionNetPower = blackSheep.size - whiteSheep.size
                    row.collisionTotalPower = blackSheep.size + whiteSheep.size
                    row.collidingSheep.append(blackSheep)
                    row.collidingSheep.append(whiteSheep)

                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    blackSheep.speed = speedFactor*5
                    whiteSheep.speed = -blackSheep.speed
                        


                    # for i in range(len(self.rowBounds)):
                        
                    #     if self.rowBounds[i][0] < blackSheep.y < self.rowBounds[i][1]:

                    #         self.rowObjects[i].collision = True

                    #         print(f'Collided on row {i}')
        
        for whiteSheep in self.activeWhiteSheep:

            for otherWhiteSheep in self.activeWhiteSheep:

                if (whiteSheep != otherWhiteSheep and whiteSheep.row == otherWhiteSheep.row and 
                    otherWhiteSheep.collided == True and whiteSheep.x-20 <= otherWhiteSheep.collisionBound):

                    row = self.rowObjects[whiteSheep.row]
                    row.collisionNetPower -= whiteSheep.size
                    row.collisionTotalPower += whiteSheep.size
                    row.collidingSheep.append(whiteSheep)

                    speedFactor = row.collisionNetPower/row.collisionTotalPower
                    for sheep in row.collidingSheep:
                        if sheep.color == 'black':
                            sheep.speed = speedFactor*5
                        else:
                            sheep.speed = -speedFactor*5

                    whiteSheep.collisionBound = whiteSheep.x+20
                    
                    whiteSheep.friendlyCollided = True
                    whiteSheep.collided = True

                    print('White friendly collided') 



    def moveActiveSheep(self):

        for sheep in self.activeBlackSheep:

            sheep.x += sheep.speed

        for sheep in self.activeWhiteSheep:

            sheep.x -= sheep.speed

    def generateNextSheep(self):
        
        while len(self.nextBlackSheep) < 3:
            randomSize = random.randint(0,4)
            self.nextBlackSheep.append(randomSize)

        while len(self.nextWhiteSheep) < 3:
            randomSize = random.randint(0,4)
            self.nextWhiteSheep.append(randomSize)

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

            photoImage = self.getCachedPhotoImage(self.loadedBlackImages[self.nextBlackSheep[i]])
            canvas.create_image(20+i*40, 20, image=photoImage)

        for i in range(len(self.nextWhiteSheep)):

            photoImage = self.getCachedPhotoImage(self.loadedWhiteImages[self.nextWhiteSheep[i]])
            canvas.create_image(self.width-100+i*40, 20, image=photoImage)

    def drawActiveSheep(self,canvas):

        for sheep in self.activeBlackSheep:

            photoImage = self.getCachedPhotoImage(self.loadedBlackImages[sheep.size])
            canvas.create_image(sheep.x,sheep.y, image=photoImage)

        for sheep in self.activeWhiteSheep:

            photoImage = self.getCachedPhotoImage(self.loadedWhiteImages[sheep.size])
            canvas.create_image(sheep.x,sheep.y, image=photoImage)

    def getCachedPhotoImage(self, image):
        # stores a cached version of the PhotoImage in the PIL/Pillow image
        if ('cachedPhotoImage' not in image.__dict__):
            image.cachedPhotoImage = ImageTk.PhotoImage(image)
        return image.cachedPhotoImage

    def redrawAll(self,canvas):
        self.drawGrid(canvas)
        self.drawButtons(canvas)
        self.drawNextSheep(canvas)
        self.drawActiveSheep(canvas)



# def main():
#     # This runs the app
#     runApp(width=400, height=300)

if __name__ == '__main__':
    obj = MyApp()