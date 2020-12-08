#File containing code for AI

from cmu_112_graphics import *
from TP_main import *
import os, random, time

#cooldown check for AI, added 0.1 sec for smoother gameplays
def checkSheepReadyAI(self):

        if self.blackCurrTime == None or (self.blackCurrTime + self.blackTimePassed + 3.1) <= time.time():
            self.blackSheepReady = True
        else:
            self.blackSheepReady = False
        if self.whiteCurrTime == None or (self.whiteCurrTime + self.whiteTimePassed + 3.1) <= time.time():
            self.whiteSheepReady = True
        else:
            self.whiteSheepReady = False

def AI(self):

    checkSheepReadyAI(self)
    if self.whiteSheepReady:
        
        nextWhiteSheepSize = self.nextWhiteSheep[0]
        nextWhiteSheepPoints = 6 - nextWhiteSheepSize

        #add up "danger points" of opponent (non-collided black sheep), check if close to winning
        nonCollidedScore = 0
        for blackSheep in self.activeBlackSheep:
            if blackSheep.collided == False:
                nonCollidedScore += blackSheep.points


        #if so, play defensively
        if nonCollidedScore + self.blackPlayer.score >= self.pointsToWin:
            
            sendOnRowOrColWithBlackPriority(self)

        #check if AI would score if next sheep in queue reached other side 
        #if so, play aggressively
        elif (self.whitePlayer.score + nextWhiteSheepPoints) >= self.pointsToWin:

            if sendEmptyRowsOrCols(self) == False:

                if sendOnlyWhiteRowOrCol(self) == False:

                    if sendBestCollidedRowOrCol(self) == False:

                        sendAnywhere(self)

        #neither player near winning so case on sheep size
        else:

            spreadOutOrFavoredRowCol = False
            sendOnBestNetRowCol = False

            nextWhiteSheepSize = self.nextWhiteSheep[0]
            checkRelativeStrength(self)

            if spreadOutOrFavoredRowCol:

                if sendBestCollidedRowOrCol(self) == False:

                    if sendEmptyRowsOrCols(self) == False:

                        checkNetPointsAndSend(self)

            elif sendOnBestNetRowCol:

                checkNetPointsAndSend(self)

            elif nextWhiteSheepSize == 1:
                
                if sendOnlyWhiteRowOrCol(self) == False:

                    if sendEmptyRowsOrCols(self) == False:

                        if sendBestCollidedRowOrCol(self,nextWhiteSheepSize) == False:

                            sendAnywhere(self)

            elif nextWhiteSheepSize == 2:

                if sendOnlyWhiteRowOrCol(self) == False:

                    if sendEmptyRowsOrCols(self) == False:
                        
                        if sendBestCollidedRowOrCol(self,nextWhiteSheepSize) == False:
                            
                            checkNetPointsAndSend(self)

            elif nextWhiteSheepSize == 3:

                if sendOnlyWhiteRowOrCol(self) == False:
                
                    if sendBestCollidedRowOrCol(self,nextWhiteSheepSize) == False:

                        checkNetPointsAndSend(self)
            
            elif nextWhiteSheepSize == 4 or nextWhiteSheepSize == 5:

                checkNetPointsAndSend(self)

            self.spreadOutOrFavoredRowCol = False
            self.sendOnBestNetRowCol = False

#consider points each side has invested in row/cols and send on row/col 
#to maximise gain/minimize loss
def checkNetPointsAndSend(self):

    rows = self.rowObjects
    cols = self.colObjects

    bestRow = None
    bestRowNetPoints = None
    for i in range(len(rows)):

        netPoints = 0
        for blackSheep in self.activeBlackSheep:
            if blackSheep.row == i:
                netPoints += blackSheep.points
        
        for whiteSheep in self.activeWhiteSheep:
            if whiteSheep.row == i:
                netPoints += whiteSheep.points

        if bestRow == None:
            bestRow = i
            bestRowNetPoints = netPoints
        elif netPoints > bestRowNetPoints:
            bestRow = i
            bestRowNetPoints = netPoints

    bestCol = None
    bestColNetPoints = None
    for i in range(len(cols)):

        netPoints = 0
        for blackSheep in self.activeBlackSheep:
            if blackSheep.col == i:
                netPoints += blackSheep.points
        
        for whiteSheep in self.activeWhiteSheep:
            if whiteSheep.col == i:
                netPoints += whiteSheep.points

        if bestCol == None:
            bestCol = i
            bestColNetPoints = netPoints
        elif netPoints > bestColNetPoints:
            bestCol = i
            bestColNetPoints = netPoints

    if bestRowNetPoints >= bestColNetPoints:
        rowToSend = bestRow
        size = self.nextWhiteSheep.pop(0)

        image = self.loadedWhiteImages[size-1]
        width, height = image.size

        y = self.getRowCy(rowToSend+1)
        whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,y,'white',False,rowToSend,None,width,height)
        self.activeWhiteSheep.append(whiteSheep)
        self.whiteCurrTime = time.time()
        self.whiteTimePassed = 0
    
    else:
        colToSend = bestCol
        size = self.nextWhiteSheep.pop(0)
        cx = self.getColCx(colToSend)

        image = self.loadedTransposedWhiteImages[size-1]
        width, height = image.size

        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-height/2,'white',True,None,colToSend,width,height)
        self.activeWhiteSheep.append(whiteSheep)
        self.whiteCurrTime = time.time()
        self.whiteTimePassed = 0


#send on row/col with black sheep (priority given to those row/col with only black 
# sheep - no white sheep to counter)
def sendOnRowOrColWithBlackPriority(self):

    highPriorityRows = set()
    highPriorityCols = set()

    for blackSheep in self.activeBlackSheep:
        if blackSheep.collided == False:

            #gather rows and cols with non-collided black
            if blackSheep.row != None:
                highPriorityRows.add(blackSheep.row)
            elif blackSheep.col != None:
                highPriorityCols.add(blackSheep.col)

    highPriorityRows = list(highPriorityRows)
    highPriorityCols = list(highPriorityCols)

    lowPriorityRows = set()
    lowPriorityCols = set()

    #move to low priority if already have white sheep in row/col
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

    #send on high priority rows/cols
    if len(highPriorityRows) > 0:

        gen = random.randint(1,len(highPriorityRows))
        rowToSend = highPriorityRows[gen-1]
        size = self.nextWhiteSheep.pop(0)

        image = self.loadedWhiteImages[size-1]
        width, height = image.size

        y = self.getRowCy(rowToSend+1)
        whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,y,'white',False,rowToSend,None,width,height)
        self.activeWhiteSheep.append(whiteSheep)
        self.whiteCurrTime = time.time()
        self.whiteTimePassed = 0

    elif len(highPriorityCols) > 0:

        gen = random.randint(1,len(highPriorityCols))
        colToSend = highPriorityCols[gen-1]
        size = self.nextWhiteSheep.pop(0)
        cx = self.getColCx(colToSend)

        image = self.loadedTransposedWhiteImages[size-1]
        width, height = image.size

        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-height/2,'white',True,None,colToSend,width,height)
        self.activeWhiteSheep.append(whiteSheep)
        self.whiteCurrTime = time.time()
        self.whiteTimePassed = 0

    #send on low priority rows/cols
    elif len(lowPriorityRows) > 0:
        gen = random.randint(1,len(lowPriorityRows))
        rowToSend = lowPriorityRows[gen-1]
        size = self.nextWhiteSheep.pop(0)
        y = self.getRowCy(rowToSend+1)

        image = self.loadedWhiteImages[size-1]
        width, height = image.size

        whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,y,'white',False,rowToSend,None,width,height)
        self.activeWhiteSheep.append(whiteSheep)
        self.whiteCurrTime = time.time()
        self.whiteTimePassed = 0
    
    elif len(lowPriorityCols) > 0:

        gen = random.randint(1,len(lowPriorityCols))
        colToSend = lowPriorityCols[gen-1]
        size = self.nextWhiteSheep.pop(0)
        cx = self.getColCx(colToSend)

        image = self.loadedTransposedWhiteImages[size-1]
        width, height = image.size

        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-height/2,'white',True,None,colToSend,width,height)
        self.activeWhiteSheep.append(whiteSheep)
        self.whiteCurrTime = time.time()
        self.whiteTimePassed = 0

#if manage to find empty row/col, send on that; otherwise return False
def sendEmptyRowsOrCols(self):

    emptyRows = [i for i in range(self.rows)]

    for blackSheep in self.activeBlackSheep:
        if blackSheep.row in emptyRows:
            emptyRows.remove(blackSheep.row)

    for whiteSheep in self.activeWhiteSheep:
        if whiteSheep.row in emptyRows:
            emptyRows.remove(whiteSheep.row)

    emptyCols = [i for i in range(self.rows)]

    for blackSheep in self.activeBlackSheep:
        if blackSheep.col in emptyCols:
            emptyCols.remove(blackSheep.col)

    for whiteSheep in self.activeWhiteSheep:
        if whiteSheep.col in emptyCols:
            emptyCols.remove(whiteSheep.col)

    emptyRowsCols = len(emptyRows) + len(emptyCols)

    #check if there's empty row/col
    if emptyRowsCols > 0:
        gen = random.randint(1,emptyRowsCols)
        if gen <= len(emptyRows):
            rowToSend = emptyRows[gen-1]
            size = self.nextWhiteSheep.pop(0)
            y = self.getRowCy(rowToSend+1)

            image = self.loadedWhiteImages[size-1]
            width, height = image.size

            whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,y,'white',False,rowToSend,None,width,height)
            self.activeWhiteSheep.append(whiteSheep)
            self.whiteCurrTime = time.time()
            self.whiteTimePassed = 0

        else:
            colToSend = emptyCols[gen-len(emptyRows)-1]
            size = self.nextWhiteSheep.pop(0)
            cx = self.getColCx(colToSend)

            image = self.loadedTransposedWhiteImages[size-1]
            width, height = image.size

            whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-height/2,'white',True,None,colToSend,width,height)
            self.activeWhiteSheep.append(whiteSheep)
            self.whiteCurrTime = time.time()
            self.whiteTimePassed = 0
    else:
        return False

#if manage to find row/col with only white sheep, send on that; otherwise, return False
def sendOnlyWhiteRowOrCol(self):

    onlyWhiteRows = []
    for i in range(len(self.rowObjects)):
        add = True
        for blackSheep in self.activeBlackSheep:
            if blackSheep.row == i:
                add = False
        if add:
            onlyWhiteRows.append(i)

    onlyWhiteCols = []
    for i in range(len(self.colObjects)):
        add = True
        for blackSheep in self.activeBlackSheep:
            if blackSheep.col == i:
                add = False
        if add:
            onlyWhiteCols.append(i)

    onlyWhiteRowsCols = len(onlyWhiteRows) + len(onlyWhiteCols)

    #check if there's row/col with only white sheep
    if onlyWhiteRowsCols > 0:
        gen = random.randint(1,onlyWhiteRowsCols)
        if gen <= len(onlyWhiteRows):
            rowToSend = onlyWhiteRows[gen-1]
            size = self.nextWhiteSheep.pop(0)
            y = self.getRowCy(rowToSend+1)

            image = self.loadedWhiteImages[size-1]
            width, height = image.size

            whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,y,'white',False,rowToSend,None,width,height)
            self.activeWhiteSheep.append(whiteSheep)
            self.whiteCurrTime = time.time()
            self.whiteTimePassed = 0
        else:
            colToSend = onlyWhiteCols[gen-len(onlyWhiteRows)-1]
            size = self.nextWhiteSheep.pop(0)
            cx = self.getColCx(colToSend)

            image = self.loadedTransposedWhiteImages[size-1]
            width, height = image.size

            whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-height/2,'white',True,None,colToSend,width,height)
            self.activeWhiteSheep.append(whiteSheep)
            self.whiteCurrTime = time.time()
            self.whiteTimePassed = 0

    else:
        return False

#find row/col with netCollisionPower that favours white most and send there
#if unable to find row/col with collision, return False
def sendBestCollidedRowOrCol(self,sheepSize):

    rowsAndCols = self.rowObjects.extend(self.colObjects)

    bestRowOrCol = None
    bestCollision = None

    for rowOrCol in rowsAndCols:
        
        bestBump = None
        for bump in rowOrCol.collisions:
            if bestBump == None:
                bestBump = bump.collisionNetPower
            elif bump.collisionNetPower < bestBump:
                bestBump = bump.collisionNetPower

        if bestBump != None and bestRowOrCol == None:
            bestRowOrCol = rowOrCol
            bestCollision = bestBump
        elif bestBump != None and bestBump < bestCollision:
            bestRowOrCol = rowOrCol
            bestCollision = bestBump

    #check if row/col with collision exists

    if bestRowOrCol != None and bestCollision - sheepSize <= 0:
            
        if type(bestRowOrCol) == Row:

            size = self.nextWhiteSheep.pop(0)
            rowNum = self.rowObjects.index(bestRowOrCol)
            y = self.getRowCy(rowNum)

            image = self.loadedWhiteImages[size-1]
            width, height = image.size

            whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,y,'white',False,rowNum,None,width,height)
            self.activeWhiteSheep.append(whiteSheep)
            self.whiteCurrTime = time.time()
            self.whiteTimePassed = 0

        else:

            size = self.nextWhiteSheep.pop(0)
            colNum = self.colObjects.index(bestRowOrCol)
            x = self.getColCx(colNum)

            image = self.loadedTransposedWhiteImages[size-1]
            width, height = image.size

            whiteSheep = Sheep(size,x,self.height-self.bottomMargin-height/2,'white',False,None,colNum,width,height)
            self.activeWhiteSheep.append(whiteSheep)
            self.whiteCurrTime = time.time()
            self.whiteTimePassed = 0

    else:
        return False

#send on any row/col
def sendAnywhere(self):

    totalRowCols = self.rows + self.cols
    gen = random.randint(1,totalRow&Cols)
    if gen <= self.rows:
        rowToSend = gen
        size = self.nextWhiteSheep.pop(0)
        y = self.getRowCy(rowToSend+1)

        image = self.loadedWhiteImages[size-1]
        width, height = image.size

        whiteSheep = Sheep(size,self.width-self.sideMargin-width/2,y,'white',False,rowToSend,None,width,height)
        self.activeWhiteSheep.append(whiteSheep)
        self.whiteCurrTime = time.time()
        self.whiteTimePassed = 0
    else:
        colToSend = gen-self.rows
        size = self.nextWhiteSheep.pop(0)
        x = self.getColCx(colToSend)

        image = self.loadedTransposedWhiteImages[size-1]
        width, height = image.size

        whiteSheep = Sheep(size,cx,self.height-self.bottomMargin-height/2,'white',True,None,colToSend,width,height)
        self.activeWhiteSheep.append(whiteSheep)
        self.whiteCurrTime = time.time()
        self.whiteTimePassed = 0

def checkRelativeStrength(self):

    blackStrength = 0
    for size in self.nextBlackSheep:
        blackStrength += size

    whiteStrength = 0
    for size in self.nextWhiteSheep:
        whiteStrength += size

    if blackStrength >= whiteStrength + 5:
        spreadOutOrFavoredRowCol = True

    elif whiteStrength >= blackStrength + 5:
        sendOnBestNetRowCol = True










