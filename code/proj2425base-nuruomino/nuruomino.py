# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 110181 Duarte Cruz
# 110239 André Pagaime

from sys import stdin
from search import *  # Import the classes from search.py
import numpy as np

 
shapeDict=  {  
                "L":[   
                        [
                            [1,0],
                            [1,0],
                            [1,1]
                        ],
                        [
                            [1,1],
                            [1,0],
                            [1,0]
                        ],
                        [
                            [0,1],
                            [0,1],
                            [1,1]
                        ],
                        [
                            [1,1],
                            [0,1],
                            [0,1]
                        ],
                        [
                            [1,1,1],
                            [1,0,0]
                        ],
                        [
                            [1,1,1],
                            [0,0,1]
                        ],
                        [
                            [1,0,0],
                            [1,1,1]
                        ],
                        [
                            [0,0,1],
                            [1,1,1]
                        ]
                    ],
                "T":[
                        [
                            [0,1,0],
                            [1,1,1]
                        ],
                        [
                            [1,1,1],
                            [0,1,0]
                        ],
                        [
                            [1,0],
                            [1,1],
                            [1,0]
                        ],
                        [
                            [0,1],
                            [1,1],
                            [0,1]
                        ]
                    ],
                "S":[
                        [
                            [1,0],
                            [1,1],
                            [0,1]
                        ],
                        [
                            [0,1],
                            [1,1],
                            [1,0]
                        ],
                        [
                            [0,1,1],
                            [1,1,0]
                        ],
                        [
                            [1,1,0],
                            [0,1,1]
                        ]
                    ],
                "I":[
                        [
                            [1,1,1,1]
                        ],
                        [
                            [1],
                            [1],
                            [1],
                            [1]
                        ]
                    ]
            }

#struct Cell
class Cell:
    def __init__(self, regionValue:int, row:int, col:int):
        self.regionValue = regionValue #region which the cell belongs
        self.row = row #cell's row (x-coordinate)
        self.col = col #cell's column (y-coordinate)
        self.flagOccupied = False #true if the cell is occupied
        self.restrictions = set() #all shapes that the cell is touching, so the cell cant be
        self.shape = ""  #shape contained in the cell
    
    #used to use this cell but with new reference
    def copy(self) -> 'Cell':
        copied = Cell(self.regionValue, self.row, self.col)
        copied.flagOccupied = self.flagOccupied
        copied.shape = self.shape
        copied.restrictions = self.restrictions
        return copied
    
    def getRow(self) -> int:
        return self.row

    def getCol(self) -> int:
        return self.col
    
    def getRegionCell(self) -> int:
        return self.regionValue
        
    def occupyCell(self) -> bool:
        if self.flagOccupied: return False
        self.flagOccupied = True
        self.shape = "X"
        return True
        
    def putShapeCell(self, shape:str) -> None:
        if self.flagOccupied: return False
        if shape in self.restrictions: return False
        self.shape = shape
        self.flagOccupied = True
        return True
        
    def get_value(self):
        if self.flagOccupied:
            #the cell is occupied
            return self.shape
        return str(self.getRegionCell())
    
    def desoccupyCell(self):
        self.flagOccupied = False
        self.shape = ""
        
    def addRestriction(self,shape):
        if self.flagOccupied: return
        self.restrictions.add(shape)
        if len(self.restrictions) == 4:
            #the cell has to be an X
            self.occupyCell()
            return 1

#struct Region
class Region:
    def __init__(self, value:int, cells:list):
        self.value = value #region value
        self.cells = cells #list of cells inside of the region
        self.numRestrictions = 0 #number of restrictions of the region
        self.numSquares = len(cells) #number of squares of the region
        self.flagOccupied = False #only true if it has a shape inside
    
    #used to use this region but with new reference
    def copy(self, copied_cells) -> 'Region':
        copied = Region(self.value, copied_cells)
        copied.numRestrictions = self.numRestrictions
        copied.numSquares = self.numSquares
        copied.flagOccupied = self.flagOccupied
        return copied
        
    def getValue(self) -> int:
        return self.value
    
    def getCells(self) -> list:
        return self.cells
    
    def updateSquares(self):
        self.numSquares = 0
        numShape = 0
        for cell in self.cells:
            if cell.shape == "":
                self.numSquares+=1
            elif cell.shape != "X":
                #it is a shape, since it is not X or empty
                numShape+=1
                
        if self.numSquares == 0 or numShape==4:
            self.flagOccupied = True
        else:
            self.flagOccupied = False
            
    def updateRestriction(self):
        self.numRestrictions = 0
        for cell in self.cells:
            self.numRestrictions += len(cell.restrictions)
            
            
    #adds a new cell to the region   
    def addCell(self, newCell:Cell) -> None:
        self.cells.append(newCell) 
        self.updateSquares()
    
    def putShape(self,startIndex,shape,shapeForm) -> None:
        worked = False
        firstCell = self.cells[startIndex]
        rowNow = firstCell.getRow()
        beginningCol = firstCell.getCol()
        cellsFromOtherRegions = []
        cellsOccupied = []
        cellsWithX = []
        cellsFilledWithShape = []
        for r in shapeForm:
            colNow = beginningCol
            for c in r:
                if c == 1:
                    #we want to occupy this cell
                    cell = self.findCell(rowNow,colNow)
                    
                    if cell == None:
                        return [],cellsOccupied,worked,[],[]
                    if not cell.putShapeCell(shape):
                        self.desoccupyCells(cellsOccupied)
                        return [],cellsOccupied,worked,[],[]
                    else:
                        cellsOccupied.append(cell)
                        cellsFilledWithShape.append(cell)
                        self.updateSquares()
                        
                elif c == "X":
                    #this cell is a cross
                    cell = self.findCell(rowNow,colNow)
                    if cell == None:
                        #its from another region
                        cellsFromOtherRegions.append((rowNow,colNow))
                    else:    
                        if not cell.occupyCell():
                            #the cell was already occupied
                            self.desoccupyCells(cellsOccupied)
                            return [],cellsOccupied,worked,[],[]
                        else:
                            cellsOccupied.append(cell)
                            cellsWithX.append(cell)
                            self.updateSquares()
                colNow+=1
            rowNow+=1
        worked = True
        self.flagOccupied = True
        self.numSquares = 0
        self.numRestrictions = 0
        return cellsFromOtherRegions,cellsOccupied,worked,cellsFilledWithShape,cellsWithX

    def desoccupyCells(self,cellsOccupied):
        for cell in cellsOccupied:
            cell.desoccupyCell()
            self.updateSquares()
    
    def findCell(self,row,col) -> Cell:
        for cell in self.cells:
            if cell.getRow() == row and cell.getCol() == col:
                return cell
        return None
    
    #calculates the score for the priority queue
    def calculateScore(self) -> int:
        return self.numSquares - self.numRestrictions

    def isOccupied(self) -> bool:
        return self.flagOccupied
    
    def getShape(self):
        #return the shape for the 4 squares regions
        diffRows = 0
        rows = []
        diffCols = 0
        cols = []
        perCol = {}
        perRow = {}
        for cell in self.cells:
            if cell.shape == "":
                if cell.row not in rows:
                    perRow[diffRows] = 1
                    rows.append(cell.row)
                    diffRows += 1
                else:
                    index = rows.index(cell.row)
                    perRow[index] += 1
                if cell.col not in cols:
                    perCol[diffCols] = 1
                    cols.append(cell.col)
                    diffCols += 1
                else:
                    index = cols.index(cell.col)
                    perCol[index] += 1
            
        shape = ""
        if diffRows==4 or diffCols==4:
            shape = "I"
        
        if perRow[max(perRow, key=perRow.get)] == 3 or perCol[max(perCol, key=perCol.get)] == 3:
            #either a L or T
            if perRow[1] == 2 or perCol[1] == 2:
                #the middle row/col has 2 cells, so it is a T
                shape = "T"
            else:
                shape = "L"
        if shape == "": shape = "S"
        shapeForm = []
        for row in perRow:
            rowForm = []
            for col in perCol:
                if perCol[col] != 0:
                    rowForm.append(1)
                    perCol[col]-=1
                else: 
                    rowForm.append(0)
            shapeForm.append(rowForm)
        return (shape,shapeForm)
                    
                         

class NuruominoState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NuruominoState.state_id
        NuruominoState.state_id += 1

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro do Puzzle Nuruomino."""                       
    def __init__(self, cellList, size, regionList, priorityQueueScores):
        self.cellList = cellList #list of cells (Cell struct)
        self.size = size #size of the board
        self.regionList = regionList #list of regions (Region struct)
        self.priorityQueueScores = priorityQueueScores  #priority queue of regions to solve -> lowest score means biggest priority
                                                        #score = number of blocks - number of restrictions
    
    #for creating new states with the same board, but with new references
    def copy(self):
        copied_cellList = []
        for r in self.cellList:
            row = []
            for cell in r:
                row.append(cell.copy())
            copied_cellList.append(row)
        copied_regionList = []
        for region in self.regionList:
            newCellList = []
            for cell in region.cells:
                newCellList.append(copied_cellList[cell.row-1][cell.col-1])
            newRegion = region.copy(newCellList)
            copied_regionList.append(newRegion)
        return Board(copied_cellList, self.size, copied_regionList,self.priorityQueueScores.copy())
        
    def addLine(self, line:list) -> None:
        "Recebe a lista do board"
        self.cellList.append(line) #adds a list of cells corresponding to a row (cell struct)
        
    def addRegion(self, region:Region) -> None:
        #adds a new region to the list of regions
        self.regionList.append(region)
    
    def get_value(self, row:int, col:int) -> int:
        cell = self.cellList[row-1][col-1]
        return cell.get_value()

    def adjacent_regions(self, regionValue:int) -> list:
        """Devolve uma lista das regiões que fazem fronteira com a região enviada no argumento."""
        listAdjacentRegions = []
        for region in self.regionList:
            if region.getValue() == regionValue:
                #found the region
                for cell in region.getCells():
                    #goes through every cell in the region and gets all region values of adjacent cells of the current cell
                    listAdjacentValues = self.adjacent_values(cell.getRow(),cell.getCol()) 
                    for value in listAdjacentValues:
                        value = int(value)
                        #goes through every region value
                        if value != regionValue and value not in listAdjacentRegions:
                            #adds the value if it wasnt added before and if it is different than the region that the current cell is in
                            listAdjacentRegions.append(value)
                break
                    
        return sorted(listAdjacentRegions) #returns it sorted in ascending order [5,2,4,1] -> [1,2,4,5]
    
    def adjacent_positions(self, row:int, col:int) -> list:
        """Devolve as posições adjacentes à região, em todas as direções, incluindo diagonais."""
        listAdjacentPos = []
        noDiagonals = self.adjacents_positions_without_diagonals(row,col) #all adjacents, without diagonals
        noDiagonalsIndex = 0
        
        if row!=1: #checks if the cell is on the first row
            if col!=1:
                listAdjacentPos.append([row-1,col-1]) #top left corner
            listAdjacentPos.append(noDiagonals[noDiagonalsIndex]) #above position
            noDiagonalsIndex+=1
            if col!=self.size:
                listAdjacentPos.append([row-1,col+1]) #top right corner
        
        if col!=1: #checks if the cell is on the left side of the board
            listAdjacentPos.append(noDiagonals[noDiagonalsIndex]) #left position
            noDiagonalsIndex+=1
            
        if col!=self.size: #checks if the cell is on the right side of the board
            listAdjacentPos.append(noDiagonals[noDiagonalsIndex]) #right position
            noDiagonalsIndex+=1
            
        if row!=self.size: #checks if the cell is on the last row
            if col!=1:
                listAdjacentPos.append([row+1,col-1]) #bottom left corner
            listAdjacentPos.append(noDiagonals[noDiagonalsIndex]) #under position
            if col!=self.size:
                listAdjacentPos.append([row+1,col+1]) #bottom right corner
                
        return listAdjacentPos
    
    def adjacents_positions_without_diagonals(self, row:int, col:int):
        listAdjacentPos = []
        
        if row!=1: #checks if the cell is on the first row
            listAdjacentPos.append([row-1,col]) #position above
            
        if col!=1: #checks if the cell is on the left side of the board
                listAdjacentPos.append([row,col-1]) #position on the left
                
        if col!=self.size: #checks if the cell is on the right side of the board
            listAdjacentPos.append([row,col+1]) #position on the right 
            
        if row!=self.size: #checks if the cell is on the last row
            listAdjacentPos.append([row+1,col]) #position under
            
        return listAdjacentPos

    def adjacent_values(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, incluindo diagonais."""
        listAdjacentValues = []
        
        listAdjacentPos = self.adjacent_positions(row,col) #gets all adjacent position of the cell
        
        for row,col in listAdjacentPos:
            #goes through every adjacent cell
            listAdjacentValues.append(self.get_value(row,col)) #gets the region value from the adjacent cell
        
        return listAdjacentValues
            
    
    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        
        valuesUsed = []
    
        line = stdin.readline().split() #reads the first line
        n = len(line) #gets the board size (NxN)
        board = Board([],n,[],[]) #creates the board
        
        firstLineCells = [] #lists of Cells from the first line
        col = 1
        for number in line:
            #goes through every value in the input, which corresponds to a region value
            number = int(number) 
            newCell = Cell(number,1,col) #creates the new cell -> regionValue = number, row = 0, col = col
            firstLineCells.append(newCell) #adds the cell to the list
            
            if number not in valuesUsed:
                #new region found
                newRegion = Region(number,[newCell]) #creates the region with the new cell
                board.addRegion(newRegion) #adds the region to board instance
                valuesUsed.append(number) #adds the region value to the list of regionValues found
            else:
                #region already created
                for region in board.regionList:
                    #goes through every region already created
                    if region.getValue() == number:
                        #found the region
                        region.addCell(newCell) #adds the cell to the region instance
                        break
                    
            col+=1 
                
        board.addLine(firstLineCells) #adds the first row of cells to the board instance
        
        for row in range(2,n+1):
            #goes through every row left
            col = 1
            lineCells = []
            line = stdin.readline().split()
            for number in line:
                #goes through every value in the input, which corresponds to a region value
                number = int(number)
                newCell = Cell(number,row,col) #creates the new cell -> regionValue = number, row = row, col = col
                lineCells.append(newCell) #adds the cell to the list of cells from this line/row
                
                if number not in valuesUsed:
                    #new region found
                    newRegion = Region(number,[newCell]) #creates the region with the new cell
                    board.addRegion(newRegion) #adds the region to board instance
                    valuesUsed.append(number) #adds the region value to the list of regionValues found
                else:
                    #region already created
                    for region in board.regionList:
                        #goes through every region already created
                        if region.getValue() == number:
                            #found the region
                            region.addCell(newCell) #adds the cell to the region instance
                            break
                col+=1
            board.addLine(lineCells) #adds the row to the board instance
        
        board.updatePriorityQueue()
        return board
    
    def findRegion(self,regionValue) -> Region:
        for region in self.regionList:
            if region.value == regionValue:
                return region
        return None
    
    #prints the board
    def print(self) -> str:
        res = ""
        for row in self.cellList:
            for cell in row:
                value = cell.get_value()
                if value == "X":
                    res+= f"{cell.regionValue} "
                else:
                    res+= f"{value} "
            res += "\n"
        return res
    
    def updatePriorityQueue(self):
        newQueue = []
        for region in self.regionList:
            newQueue.append(region.calculateScore())
        self.priorityQueueScores = newQueue
        
    def getRegionBiggestPriority(self):
        lowestScore = 0
        index = 0
        indexNow = 0
        for priority in self.priorityQueueScores:
            if priority>0:
                if(lowestScore == 0 or priority<lowestScore):
                    lowestScore = priority
                    index = indexNow
                elif(lowestScore == priority):
                    #if there is a tie in the scores, we chose the region with less blocks
                    regionNow = self.regionList[indexNow]
                    regionWinning = self.regionList[index]
                    if(regionNow.numSquares < regionWinning.numSquares):
                        index = indexNow
            indexNow+=1
        return self.regionList[index]
        
    def shapeRegion(self,regionValue,shape,shapeForm,isToInsert):
        region = self.findRegion(regionValue)
        if region.isOccupied():
            return False, [], []
        if shape in ["L","S","T"]:
            crosses = self.findCrosses(shapeForm)
            if(crosses):
                for (r,c) in crosses:
                    shapeForm[r][c] = "X"
                    
        possibleSpots = []
        startIndex = -1
        maxIndex = len(region.cells)
        stop = False
        cellsWithShape = []
        cellsWithX = []
        while startIndex<maxIndex:   
            worked = False
            while not worked:
                #while its empty, it keeps going -> stops when we occupy all 4 cells
                startIndex+=1   
                if startIndex == maxIndex:
                    stop = True 
                    break   
                cellsFromOtherRegion,cellsOccupied,worked,cellsFilledWithShape,cellsFilledWithX = region.putShape(startIndex,shape,shapeForm)
                if not worked: 
                    self.desocuppyCells(cellsOccupied)
                
            if not stop:
                desocupyFlag = False
                
                #checks if there were any squares made, desocupyFlag = True if so
                desocupyFlag = self.madeSquares(cellsOccupied)
                
                if desocupyFlag:
                    #made a square
                    self.desocuppyCells(cellsOccupied)
                else:
                    #checks if we are going to put an X in a filled cell
                    for (row,col) in cellsFromOtherRegion:
                        cell = self.cellList[row-1][col-1]
                        if not cell.occupyCell():
                            #the cell was previously occupied
                            self.desocuppyCells(cellsOccupied)
                            desocupyFlag = True
                            break
                        else:
                            cellsFilledWithX.append(cell)
                            cellsOccupied.append(cell)
                            regionToRemove = self.findRegion(cell.regionValue)
                            regionToRemove.updateSquares()
                    

                if not desocupyFlag: 
                    #we save the spot in a list and clear the cells -> we need to choose the best spot (the one with the best score)
                    score = len(cellsFromOtherRegion) #the less the better
                    possibleSpots.append(((startIndex,shape,shapeForm),score))
                    self.desocuppyCells(cellsOccupied)
                    for cell in cellsFilledWithShape:
                        cellsWithShape.append(cell)
                    for cell in cellsFilledWithX:
                        cellsWithX.append(cell)

        if isToInsert and len(possibleSpots) > 0:      
            bestInfo = self.getBestScoreShape(possibleSpots)
            self.putShapeRegion(bestInfo,region)
            self.updatePriorityQueue()
        else:
            if len(possibleSpots) > 0:
                return True, cellsWithShape, cellsWithX
            return False, [], []
        
    def madeSquares(self,cellsOccupied):
        max = self.size-1
        for cell in cellsOccupied:
            #we need to check above, under, right and left values
            row = cell.row
            col = cell.col 
            if cell.shape!="X":
                if row>1:
                    #we need to check the above position
                    if self.get_value(row-1,col) in ["L","S","T","I"]:
                        #the above position is occupied, so now we need to check the left and the right
                        if col>1:
                            if self.get_value(row,col-1) in ["L","S","T","I"]:
                                #the left position is occupied, so now we need to check the top left corner
                                if self.get_value(row-1,col-1) in ["L","S","T","I"]:
                                    #it made a square
                                    return True
                        if col<max:
                            if self.get_value(row,col+1) in ["L","S","T","I"]:
                                #the right position is occupied, so now we need to check the top right corner
                                if self.get_value(row-1,col+1) in ["L","S","T","I"]:
                                    #it made a square
                                    return True
                if row<max:
                    #we need to check the under position
                    if self.get_value(row+1,col) in ["L","S","T","I"]:
                        #the under position is occupied, so now we need to check the left and the right
                        if col>1:
                            if self.get_value(row,col-1) in ["L","S","T","I"]:
                                #the left position is occupied, so now we need to check the bottom left corner
                                if self.get_value(row+1,col-1) in ["L","S","T","I"]:
                                    #it made a square
                                    return True
                        if col<max:
                            if self.get_value(row,col+1) in ["L","S","T","I"]:
                                #the right position is occupied, so now we need to check the bottom right corner
                                if self.get_value(row+1,col+1) in ["L","S","T","I"]:
                                    #it made a square
                                    return True
        return False   
    
    def putShapeRegion(self,info,region):
        startIndex = info[0]
        shape = info[1]
        shapeForm = info[2]
        cellsFromOtherRegion,cellsOccupied,_,_,_ = region.putShape(startIndex,shape,shapeForm)
        for (row,col) in cellsFromOtherRegion:
            cell = self.cellList[row-1][col-1]
            cell.occupyCell()
            region = self.findRegion(cell.regionValue)
            region.updateSquares()
        self.restrictAdjacents(cellsOccupied,shape)
        
    def restrictAdjacents(self,cellsOccupied,shape):
        visited = set()
        for cell in cellsOccupied:
            listAdjacentPos = self.adjacents_positions_without_diagonals(cell.row,cell.col)
            for [row,col] in listAdjacentPos:
                cell = self.cellList[row-1][col-1]
                visited.add(cell)
        
        for cell in visited:
            region = self.findRegion(cell.regionValue)
            if cell.addRestriction(shape) == 1:
                #the cell is now an X since it has all restrictions
                region.updateSquares()
            else:    
                region.updateRestriction()
            
    
    def getBestScoreShape(self,possibleSpots):
        #possibleSpots = startIndex,shape,shapeForm,score
        minScore = possibleSpots[0][1]
        best = possibleSpots[0][0]
        for (info,score) in possibleSpots:
            if score < minScore:
                minScore = score
                best = (info)
        return best
    
    def desocuppyCells(self,cellsOccupied):
        for cell in cellsOccupied:
            cell.desoccupyCell()
            region = self.findRegion(cell.regionValue)
            region.updateSquares()
       
    def findCrosses(self,shapeForm):
        crossesIndexes = []
        rowNum = 0
        for row in shapeForm:
            colNum = 0
            for value in row:
                if value == 0:
                    #we need to check above, under, right and left values
                    if rowNum!=0:
                        if shapeForm[rowNum-1][colNum] == 1:
                            if colNum!=len(row)-1:
                                if shapeForm[rowNum][colNum+1] == 1:
                                    if shapeForm[rowNum-1][colNum+1] == 1: #topRightCorner
                                        crossesIndexes.append((rowNum,colNum))
                            if colNum!=0:
                                if shapeForm[rowNum][colNum-1] == 1:
                                    if shapeForm[rowNum-1][colNum-1] == 1: #topLeftCorner
                                        crossesIndexes.append((rowNum,colNum))
                    if rowNum!=len(shapeForm)-1:
                        if shapeForm[rowNum+1][colNum] == 1:
                            if colNum!=len(row)-1:
                                if shapeForm[rowNum][colNum+1] == 1:
                                    if shapeForm[rowNum+1][colNum+1] == 1:
                                        crossesIndexes.append((rowNum,colNum))#bottomRightCorner
                            if colNum!=0:            
                                if shapeForm[rowNum][colNum-1] == 1:
                                    if shapeForm[rowNum+1][colNum-1] == 1:
                                        crossesIndexes.append((rowNum,colNum))#bottomLeftCorner
                colNum += 1
            rowNum += 1
        return crossesIndexes
    
    def isCross(self,shapeForm,rowNum,colNum):
        if shapeForm[rowNum-1][colNum] == 1:
            if shapeForm[rowNum][colNum+1] == 1:
                if shapeForm[rowNum-1][colNum+1] == 1:
                    return True
            if shapeForm[rowNum][colNum-1] == 1:
                if shapeForm[rowNum-1][colNum-1] == 1:
                    return True
        if shapeForm[rowNum+1][colNum] == 1:
            if shapeForm[rowNum][colNum+1] == 1:
                if shapeForm[rowNum+1][colNum+1] == 1:
                    return True
            if shapeForm[rowNum][colNum-1] == 1:
                if shapeForm[rowNum+1][colNum-1] == 1:
                    return True
        return False
                

class Nuruomino(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.initial = NuruominoState(board)

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        board = state.board
        listActions = []
        overlappedCellsShape = []
        overlappedCellsX = []
        cellsShapeDict = {}
        for region in board.regionList:
            if region.numSquares == 4:
                #we can simply put the supposed piece, since it is a 4 piece region
                action = region.getShape() #action = (shape,shapeForm)
                listActions.append((region.value,action))
            else:
                #print("for region",region.value)
                #the region has more than 4 squares, so we need to test each shape and shapeForm
                firstFlag = True
                for shape in shapeDict:
                    for shapeForm in shapeDict[shape]:
                        worked, cellsWithShape, cellsWithX = board.shapeRegion(region.value,shape,[row[:] for row in shapeForm],False)  
                        if worked:
                            listActions.append((region.value,(shape,shapeForm)))
                            if firstFlag:
                                firstFlag = False
                                overlappedCellsShape = cellsWithShape
                                overlappedCellsX = cellsWithX
                                for cell in overlappedCellsShape:
                                   cellsShapeDict[cell] = [shape]
                            else:
                                #check for overlaps in shaped  cells
                                overlappedCellsShape = [cell for cell in overlappedCellsShape if cell in cellsWithShape]
                                for cell in overlappedCellsShape:
                                    if shape not in cellsShapeDict[cell]:
                                        cellsShapeDict[cell].append(shape)
                                        
                                #check for overlap in X cells
                                overlappedCellsX = [cell for cell in overlappedCellsX if cell in cellsWithX]
                                        
            #print("found shape overlap at:")   
            #for cell in overlappedCellsShape:
            #    print(cell.row,cell.col, "with shapes", cellsShapeDict[cell])
            #print("found X overlap at:")   
            #for cell in overlappedCellsX:
            #    print(cell.row,cell.col)
        return listActions       

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        listActions = self.actions(state) #listActions = [(regionValue,(shape,shapeForm))]
        
        if len(action) == 2:
            #action -> (regionValue, (shape, form of shape))
            regionValue = action[0]
            shape = action[1][0]
            shapeForm = action[1][1]
        else:
            #action -> (regionValue, shape, form of shape)
            regionValue = action[0]
            shape = action[1]
            shapeForm = action[2]
            
        newState = NuruominoState(state.board.copy()) #copies the board, but with new reference
        if (regionValue,(shape,shapeForm)) in listActions:
            #the action is in listActions, so we do it
            newState.board.shapeRegion(regionValue,shape,shapeForm,True)
            return newState
        else:
            #the action is not in listActions, so it is not a possible action
            return newState
        

    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #checks if every region is occupied 
        for region in state.board.regionList:
            if not region.isOccupied():
                return False
            
        #checks if every shape is touching
        
        return True 

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        #region = board.getRegionBiggestPriority()
        #print(" ".join([str(i) for i in board.priorityQueueScores]))
        
        #if region.numSquares == 4:
        #    #we can simply put the supposed piece
        #    #print("4 piece region -> fill automatically")
        #    #(shape,shapeForm) = region.getShape()
        #    # board.shapeRegion(region.value,shape,shapeForm,True)
        #    pass
        # TODO
        pass
        
# Ler grelha do figura 1a:
board = Board.parse_instance()
# Criar uma instância de Nuruomino:
problem = Nuruomino(board)
# Criar um estado com a configuração inicial:
s0 = NuruominoState(board)
# Aplicar as ações que resolvem a instância
s1 = problem.result(s0, (1,'L', [[1, 1],[1, 0],[1, 0]]))
s2 = problem.result(s1, (2,'S', [[1, 0], [1, 1],[0, 1]]))
s3 = problem.result(s2, (3,'T', [[1, 0],[1, 1],[1, 0]]))
s4 = problem.result(s3, (4,'L', [[1, 1, 1],[1, 0, 0]]))
s5 = problem.result(s4, (5,'I', [[1],[1],[1],[1]]))
# Verificar se foi atingida a solução
print("Is goal?", problem.goal_test(s2))
print("Is goal?", problem.goal_test(s5))
print("Solution:\n", s5.board.print(), sep="")