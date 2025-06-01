# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 110181 Duarte Cruz
# 110239 André Pagaime

from sys import stdin
from search import Problem, Node  # Import the classes from search.py


####################### Auxiliar Functions #######################

def zigzagOrder(lst: list) -> list:
    '''
    [1, 2, 3, 4] -> [1, 4, 2, 3]\n
    [1, 2, 3, 4, 5, 6, 7] -> [1, 7, 2, 6, 3, 5, 4]
    '''
    zigzag_order = []
    i = 0
    j = len(lst) - 1

    while i < j:
        zigzag_order.append(lst[i])
        zigzag_order.append(lst[j])
        i += 1
        j -= 1
    
    if i == j: zigzag_order.append(lst[i])

    return zigzag_order


def allEqual(lst: list|tuple) -> bool:
    if not lst: return True
    last_elem = lst[0]
    for elem in lst:
        if elem != last_elem: return False
    return True


def whichShape(directions: list[int]) -> str:
    '''
    This function cannot recognise the T shape! 
    '''
    if len(directions) != 3: return ""

    if allEqual(directions): return "I"
    elif directions[0] == directions[-1]: return "S"
    elif directions[0] == directions[1] or directions[-1] == directions[-2]: return "L"
    else: return ""


def shapesTypesSetToStr(shapes: set) -> str:
    shapes_str = ""
    shape_types = "LITS"
    for shape_type in shape_types:
        if shape_type in shapes: shapes_str += shape_type
    return shapes_str

##################################################################


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
        
    def occupyCell(self) -> bool:
        if self.flagOccupied: return False
        self.flagOccupied = True
        self.shape = "X"
        return True
        
    def putShapeCell(self, shape:str) -> None:
        if self.flagOccupied: return False
        self.shape = shape
        self.flagOccupied = True
        return True
        
    def get_value(self):
        if self.flagOccupied:
            #the cell is occupied
            return self.shape
        return str(self.getRegionCell())
    
    def desoccupy(self):
        self.flagOccupied = False
        self.shape = ""

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
    
    def addSquare(self):
        self.numSquares += 1
        if self.flagOccupied:
            self.flagOccupied = False
    
    def removeSquare(self):
        self.numSquares -= 1
        if self.numSquares == 0:
            self.flagOccupied = True
     
    #adds a new cell to the region   
    def addCell(self, newCell:Cell) -> None:
        self.cells.append(newCell) 
        self.addSquare()
    
    def putShape(self,shape,shapeForm) -> None:
        firstCell = self.cells[0]
        rowNow = firstCell.getRow()
        beginningCol = firstCell.getCol()
        cellsFromOtherRegions = []
        cellsOccupied = []
        for r in shapeForm:
            colNow = beginningCol
            for c in r:
                if c == 1:
                    #we want to occupy this cell
                    cell = self.findCell(rowNow,colNow)
                    if not cell.putShapeCell(shape):
                        self.desocuppyCells(cellsOccupied)
                        return [],[]
                    else:
                        cellsOccupied.append(cell)
                        self.removeSquare()
                        
                elif c == "X":
                    #this cell is a cross
                    cell = self.findCell(rowNow,colNow)
                    if cell == None:
                        #its from another region
                        cellsFromOtherRegions.append((rowNow,colNow,"X"))
                    else:    
                        if not cell.occupyCell():
                            #the cell was already occupied
                            self.desocuppyCells(cellsOccupied)
                            return [],[]
                        else:
                            cellsOccupied.append(cell)
                            self.removeSquare()
                colNow+=1
            rowNow+=1
        self.flagOccupied = True
        self.numSquares = 0
        self.numRestrictions = 0
        return cellsFromOtherRegions,cellsOccupied

    def desocuppyCells(self,cellsOccupied):
        for cell in cellsOccupied:
            cell.desoccupy()
            self.addSquare()
    
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
            
   
        if diffRows==4 or diffCols==4:
            shape = "I"
        
        if perRow[max(perRow, key=perRow.get)] == 3 or perCol[max(perCol, key=perCol.get)] == 3:
            #either a L or T
            if perRow[1] == 2 or perCol[1] == 2:
                #the middle row/col has 2 cells, so it is a T
                shape = "T"
            else:
                shape = "L"
        shape = "S"
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
    def print(self) -> str:
        res = ""
        for row in self.cellList:
            res += " ".join([cell.get_value() for cell in row])
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
        
    def putShapeRegion(self,regionValue,shape,shapeForm):
        region = self.findRegion(regionValue)
        if region.isOccupied():
            return 
        if shape in ["L","S","T"]:
            crosses = self.findCrosses(shapeForm)
            if(crosses!=[]):
                for (r,c) in crosses:
                    shapeForm[r][c] = "X"
                    
        cellsFromOtherRegion,cellsOccupied = region.putShape(shape,shapeForm)
        for (row,col,shape) in cellsFromOtherRegion:
            cell = self.cellList[row-1][col-1]
            if not cell.occupyCell():
                #the cell was previously occupied
                self.desocuppyCells(cellsOccupied)
                break
            else:
                cellsOccupied.append(cell)
                region = self.findRegion(cell.regionValue)
                region.removeSquare()
        self.updatePriorityQueue()
    
    def desocuppyCells(self,cellsOccupied):
        for cell in cellsOccupied:
            cell.desoccupy()
            region = self.findRegion(cell.regionValue)
            region.addSquare()
       
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
    

    
    def getAdjacentCellsSameRegion(self, cell: Cell, exclude: list[Cell] = []):
        adjacent_cells_same_region = []
        row_var = -1, 0, 1, 0
        col_var = 0, 1, 0, -1
        max = self.size - 1

        # Check up, right, down and left, respectively
        for i in range(4):
            row = cell.getRow() + row_var[i]
            col = cell.getCol() + col_var[i]
            if row < 0 or col < 0 or row > max or col > max: continue
            new_cell = self.cellList[row][col]
            if cell.getRegionCell() == new_cell.getRegionCell() and new_cell not in exclude:
                adjacent_cells_same_region.append(new_cell)

        return adjacent_cells_same_region
    

    def cellDirection(self, cell1: Cell, cell2: Cell) -> int:
        '''
        Returns the direction from cell1 to cell2 if they are adjacent, excluding diagonals.

        Up: 1  
        Down: -1  
        Left: 2  
        Right: -2  

        Returns 0 if the cells are not adjacent.
        '''
        row_diff = cell1.getRow() - cell2.getRow()
        col_diff = cell1.getCol() - cell2.getCol()
        if abs(row_diff) + abs(col_diff) != 1: return 0 # The cells are not adjacent
        if row_diff: return row_diff
        else: return col_diff * 2


    def getPossibleShapesStartingOnCell(self, cell: Cell) -> list[tuple[str, set[Cell]]]: # example: [("L", {c1, c2, c3, c4}), ("I", {c2, c3, c4, c5}), ...]
        '''
        This function does not return all possible shapes that include the cell!
        '''

        # Initialize variables
        stack = []
        shapes = []
        direction = 0 # up: 1, down: -1, left: 2, right: -2
        directions = [] # Directions are used to determine the shape
        current_cell = cell
        shape = [current_cell]
        num_cells = 1
        possible_T_verified = set()
        stack.append(self.getAdjacentCellsSameRegion(current_cell))

        # Search for shapes
        while stack:

            if num_cells == 4:
                shape_type = whichShape(directions)
                if shape_type in "LITS":
                    new_elem = (shape_type, set(shape))
                    if new_elem not in shapes: shapes.append(new_elem)
                if directions: directions.pop()
                shape.pop()
                num_cells -= 1
                if shape: current_cell = shape[-1]

            elif not stack[-1]:
                stack.pop()
                if directions: directions.pop()
                shape.pop()
                num_cells -= 1
                if shape: current_cell = shape[-1]

            elif num_cells == 3 and allEqual(directions) and shape not in possible_T_verified: # Try to add T shapes
                possible_T_verified.add(shape)
                possible_cells = self.getAdjacentCellsSameRegion(shape[-2], shape)
                for possible_cell in possible_cells:
                    t_shape = shape
                    t_shape.append(possible_cell)
                    shapes.append(("T", set(t_shape)))

            else:
                direction = self.cellDirection(current_cell, stack[-1][-1])
                assert direction != 0
                current_cell = stack[-1][-1]
                stack[-1].pop()
                shape.append(current_cell)
                num_cells += 1
                if num_cells < 4: stack.append(self.getAdjacentCellsSameRegion(current_cell, shape))

        return shapes
    


    def fillRegionOverlap(self, region: Region):
        '''
        Calculates all possible shapes that fit in the region and adds to the board the cells that are present in all shapes
        '''
        first_iter = True
        region_cells = zigzagOrder(region.getCells()) # To fail faster in bigger regions
        overlap = set()
        shape_types = set()

        # Calculate the overlap
        for cell in region_cells:
            possible_shapes = self.getPossibleShapesStartingOnCell(cell)
            for shape in possible_shapes:
                shape_type, cells = shape
                shape_types.add(shape_type)
                if first_iter:
                    overlap = cells
                    first_iter = False
                    continue
                overlap = overlap.intersection(cells)
                if not overlap: return

        # Apply to the board
        for cell in overlap: cell.putShapeCell(shapesTypesSetToStr(shape_types)) # ? É assim que se faz?



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
            #print("4 piece region -> fill automatically")
            #(shape,shapeForm) = region.getShape()
            # board.putShapeRegion(region.value,shape,shapeForm)
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
#s1 = problem.result(s0, (1,'L', [[1, 1],[1, 0],[1, 0]]))
#s2 = problem.result(s1, (2,'S', [[1, 0], [1, 1],[0, 1]]))
#s3 = problem.result(s2, (3,'T', [[1, 0],[1, 1],[1, 0]]))
#s4 = problem.result(s3, (4,'L', [[1, 1, 1],[1, 0, 0]]))
#s5 = problem.result(s4, (5,'I', [[1],[1],[1],[1]]))

s1 = problem.result(s0, (1,'L', [[1, 1],[1, 0],[1, 0]]))
s2 = problem.result(s1, (2,'S', [[1, 0], [1, 1],[0, 1]]))
s3 = problem.result(s2, (4,'L', [[1, 1, 1],[1, 0, 0]]))
s4 = problem.result(s3, (5,'I', [[1],[1],[1],[1]]))
s5 = problem.result(s4, (3,'T', [[1, 0],[1, 1],[1, 0]]))
# Verificar se foi atingida a solução
print("Is goal?", problem.goal_test(s1))
print("Is goal?", problem.goal_test(s2))
print("Is goal?", problem.goal_test(s3))
print("Is goal?", problem.goal_test(s4))
print("Is goal?", problem.goal_test(s5))

print("Solution:\n", s5.board.print(), sep="")