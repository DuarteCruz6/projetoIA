# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 110181 Duarte Cruz
# 110239 André Pagaime

from sys import stdin
from search import Problem, Node  # Import the classes from search.py

#struct Cell
class Cell:
    def __init__(self, regionValue:int, row:int, col:int):
        self.regionValue = regionValue #region which the cell belongs
        self.row = row #cell's row (x-coordinate)
        self.col = col #cell's column (y-coordinate)
        self.flagOccupied = False #true if the cell is occupied
        self.shape = ""  #shape contained in the cell
    
    #used to use this cell but with new reference
    def copy(self) -> 'Cell':
        copied = Cell(self.regionValue, self.row, self.col)
        copied.flagOccupied = self.flagOccupied
        copied.shape = self.shape
        return copied
    
    def getRow(self) -> int:
        return self.row

    def getCol(self) -> int:
        return self.col
    
    def getRegionCell(self) -> int:
        return self.regionValue
        
    def occupyCell(self) -> None:
        self.flagOccupied = True
        self.shape = "X"
        
    def putShapeCell(self, shape:str) -> None:
        self.shape = shape
        self.flagOccupied = True
        
    def get_value(self):
        if self.flagOccupied:
            #the cell is occupied
            return self.shape
        return str(self.getRegionCell())

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
     
    #adds a new cell to the region   
    def addCell(self, newCell:Cell) -> None:
        self.cells.append(newCell) 
        self.numSquares += 1
    
    def putShape(self,shape,shapeForm) -> None:
        firstCell = self.cells[0]
        rowNow = firstCell.getRow()
        beginningCol = firstCell.getCol()
        cellsFromOtherRegions = []
        for r in shapeForm:
            colNow = beginningCol
            for c in r:
                if c == 1:
                    #we want to occupy this cell
                    cell = self.findCell(rowNow,colNow)
                    cell.putShapeCell(shape)
                elif c == "X":
                    #this cell is a cross
                    cell = self.findCell(rowNow,colNow)
                    if cell == None:
                        #its from another region
                        cellsFromOtherRegions.append((rowNow,colNow,"X"))
                    else:    
                        cell.occupyCell()
                    print(rowNow,colNow)
                colNow+=1
            rowNow+=1
        self.flagOccupied = True
        self.numSquares = 0
        self.numRestrictions = 0
        return cellsFromOtherRegions
    
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
        copied_cellList = [cell.copy() for cell in self.cellList]
        copied_regionList = []
        for region in self.regionList:
            newCellList = []
            for cell in region.cells:
                newCellList.append(copied_cellList[cell.row-1][cell.col-1])
            newRegion = region.copy(newCellList)
            copied_regionList.append(newRegion)
        return Board(copied_cellList, self.size, copied_regionList,self.priorityQueueScores)
        
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
                        #goes through every region value
                        if value != regionValue and value not in listAdjacentRegions:
                            #adds the value if it wasnt added before and if it is different than the region that the current cell is in
                            listAdjacentRegions.append(value)
                break
                    
        return sorted(listAdjacentRegions) #returns it sorted in ascending order [5,2,4,1] -> [1,2,4,5]
    
    def adjacent_positions(self, row:int, col:int) -> list:
        """Devolve as posições adjacentes à região, em todas as direções, incluindo diagonais."""
        
        listAdjacentPos = []
        
        if row!=1: #checks if the cell is on the first row
            if col!=1:
                listAdjacentPos.append([row-1,col-1]) #top left corner
            listAdjacentPos.append([row-1,col]) #position above
            if col!=self.size:
                listAdjacentPos.append([row-1,col+1]) #top right corner
            
        if col!=1: #checks if the cell is on the left side of the board
                listAdjacentPos.append([row,col-1]) #position on the left
                
        if col!=self.size: #checks if the cell is on the right side of the board
            listAdjacentPos.append([row,col+1]) #position on the right 
            
        if row!=self.size: #checks if the cell is on the last row
            if col!=1:
                listAdjacentPos.append([row+1,col-1]) #bottom left corner
            listAdjacentPos.append([row+1,col]) #position under
            if col!=self.size:
                listAdjacentPos.append([row+1,col+1]) #bottom right corner
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
    def print(self) -> None:
        for row in self.cellList:
            print(" ".join([cell.get_value() for cell in row]))
    
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
            if priority!=0:
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
        
    def putShapeRegion(self,regionValue,shape,shapeForm):
        region = self.findRegion(regionValue)
        if shape in ["L","S","T"]:
            crosses = self.findCrosses(shapeForm)
            if(crosses!=[]):
                for (r,c) in crosses:
                    shapeForm[r][c] = "X"
                print("crosses! ",shape)
        cellsFromOtherRegion = region.putShape(shape,shapeForm)
        for (row,col,shape) in cellsFromOtherRegion:
            cell = self.cellList[row-1][col-1]
            cell.occupyCell()
            region = self.findRegion(cell.regionValue)
            region.numSquares -=1
        self.updatePriorityQueue()
       
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
        #TODO
        pass 

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        board = state.board
        
        region = board.getRegionBiggestPriority()
        print(" ".join([str(i) for i in board.priorityQueueScores]))
        
        if region.numSquares == 4:
            #we can simply put the supposed piece
            print("4 piece region -> fill automatically")
        pass 

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        #action -> (regionValue, shape, form of shape)
        self.actions(state)
        regionValue = action[0]
        shape = action[1]
        shapeForm = action[2]
        newState = NuruominoState(state.board.copy()) #copies the board, but with new reference
        newState.board.putShapeRegion(regionValue,shape,shapeForm)
        return  newState
        

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
#s3 = problem.result(s2, (3,'T', [[1, 0],[1, 1],[1, 0]]))
#s4 = problem.result(s3, (4,'L', [[1, 1, 1],[1, 0, 0]]))
#s5 = problem.result(s4, (5,'I', [[1],[1],[1],[1]]))
# Verificar se foi atingida a solução
print("Is goal?", problem.goal_test(s1))
print("Is goal?", problem.goal_test(s2))
#print("Is goal?", problem.goal_test(s3))
#print("Is goal?", problem.goal_test(s4))
#print("Is goal?", problem.goal_test(s5))

print("Solution:\n", s2.board.print(), sep="")