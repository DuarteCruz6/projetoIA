# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 32:
# 110181 Duarte Cruz
# 110239 André Pagaime

from sys import stdin
from search import *  # Import the classes from search.py
import numpy as np

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
    length = len(directions)
    if length == 3 and allEqual(directions): return "I"
    elif length == 3 and directions[0] == directions[-1]: return "S"
    elif length == 3 and (directions[0] == directions[1] or directions[-1] == directions[-2]): return "L"
    elif length == 4 and (directions[0] == directions[1] and directions[2] == -directions[0]
        and abs(directions[-1]) != abs(directions[0])): return "T"
    else: return ""

##################################################################


#struct Cell
class Cell:
    def __init__(self, regionValue:int, row:int, col:int):
        self.regionValue = regionValue #region which the cell belongs
        self.row = row #cell's row (x-coordinate)
        self.col = col #cell's column (y-coordinate)
        self.shape = "" #cell's shape
        self.flagOccupied = False
    
    #used to use this cell but with new reference
    def copy(self) -> 'Cell':
        copied = Cell(self.regionValue, self.row, self.col)
        copied.shape = self.shape
        copied.flagOccupied = self.flagOccupied
        return copied
    
    def getRow(self) -> int:
        return self.row
    
    def getRow0(self) -> int:
        return self.row - 1

    def getCol(self) -> int:
        return self.col
    
    def getCol0(self) -> int:
        return self.col - 1
    
    def getRegionCell(self) -> int:
        return self.regionValue
    
    def get_value(self):
        if self.flagOccupied:
            #the cell is occupied
            return self.shape
        return str(self.getRegionCell())

    def get_region(self):
        return self.getRegionCell()
    
    def putShape(self,shape):
        self.shape = shape
        self.flagOccupied = True
        
    # Definition of == operator between cells
    def __eq__(self, other: 'Cell'):
        if other is None: return False
        return self.getRow() == other.getRow() and self.getCol() == other.getCol()
    
    # Make Cell hashable
    def __hash__(self):
        return hash((self.getRow(), self.getCol()))
    
    def __repr__(self):
        return f"({self.row}, {self.col})"

#struct Region
class Region:
    def __init__(self, value:int, cells:list):
        self.value = value #region value
        self.cells = cells #list of cells inside of the region
        self.possibilities = [] #list of actions that are possible in this region
        self.isFilled = False #flag for when the region is filled
        
    #used to use this region but with new reference
    def copy(self, copied_cells) -> 'Region':
        copied = Region(self.value, copied_cells)
        copied.possibilities = self.possibilities.copy()
        copied.isFilled = self.isFilled
        return copied
        
    def getValue(self) -> int:
        return self.value
    
    def getCells(self) -> list:
        return self.cells
            
    #adds a new cell to the region   
    def addCell(self, newCell:Cell) -> None:
        self.cells.append(newCell) 
    
    def findCell(self,row,col) -> Cell:
        for cell in self.cells:
            if cell.getRow() == row and cell.getCol() == col:
                return cell
        return None  
    
    #adds a possibility to the region
    def addPossibility(self,possibility):
        #possibility = (shape, cellsOccupied, regionTouching)
        if not self.isFilled:
            self.possibilities.append(possibility)
        
    def removePossibility(self,possibility):
        if not self.isFilled:
            self.possibilities.remove(possibility)
        
    def getPossibilities(self):
        return self.possibilities
    
    def putShape(self,shapeFinal,coords):
        if not self.isFilled:
            finalActions = []
            cells = []
            for shape,cellsOccupied, regionTouching in self.possibilities:
                if shape == shapeFinal and coords == cellsOccupied:
                    finalActions.append((shape,cellsOccupied,regionTouching))

            if len(finalActions) == 1:
                #only one action remains
                regionTouching = finalActions[0][2]
                cells = self.fillRegion()
            else:
                self.possibilities = finalActions

            return regionTouching, cells

    #if there is only one action left
    def fillRegion(self):
        self.isFilled = True
        action = self.possibilities[0]
        self.possibilities = []
        return action[1]
        
        

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
    def __init__(self, cellList, size, regionList):
        self.cellList = cellList #list of cells (Cell struct)
        self.size = size #size of the board
        self.regionList = regionList #list of regions (Region struct)
    
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
        return Board(copied_cellList, self.size, copied_regionList)
        
    def addLine(self, line:list) -> None:
        "Recebe a lista do board"
        self.cellList.append(line) #adds a list of cells corresponding to a row (cell struct)
        
    def addRegion(self, region:Region) -> None:
        #adds a new region to the list of regions
        self.regionList.append(region)
    
    def get_value(self, row:int, col:int) -> int:
        cell = self.cellList[row-1][col-1]
        return cell.get_value()

    def get_region_cell(self,row,col):
        cell = self.cellList[row-1][col-1]
        return cell.get_region()
     
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
            listAdjacentPos.append((row-1,col)) #position above
            
        if col!=1: #checks if the cell is on the left side of the board
                listAdjacentPos.append((row,col-1)) #position on the left
                
        if col!=self.size: #checks if the cell is on the right side of the board
            listAdjacentPos.append((row,col+1)) #position on the right 
            
        if row!=self.size: #checks if the cell is on the last row
            listAdjacentPos.append((row+1,col)) #position under
            
        return listAdjacentPos

    def adjacent_values(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, incluindo diagonais."""
        listAdjacentValues = []
        
        listAdjacentPos = self.adjacent_positions(row,col) #gets all adjacent position of the cell
        
        for row,col in listAdjacentPos:
            #goes through every adjacent cell
            listAdjacentValues.append(self.get_value(row,col)) #gets the region value from the adjacent cell
        
        return listAdjacentValues
    
    def adjacent_values_without_diagonals(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, sem diagonais."""
        listAdjacentValues = []
        
        listAdjacentPos = self.adjacents_positions_without_diagonals(row,col) #gets all adjacent position of the cell
        
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
        board = Board([],n,[]) #creates the board
        
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
                    res+= f"{cell.regionValue}\t"
                else:
                    res+= f"{value}\t"
            res += "\n"
        return res       
        
    def madeSquares(self,cellsOccupied):
        max = self.size
        for row,col in cellsOccupied:
            #we need to check above, under, right and left values 
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
    
    def verifyConnectivity(self):
        rows = self.size
        cols = self.size
        
        for r in range(1,rows+1):
            for c in range(1,cols+1):
                if self.get_value(r,c) in ["L","I","T","S"]:
                    #we found the first cell with shape
                    start = (r,c)
                    break
        
        visitted = set() 
        queue = [start]    
        
        while queue:
            r,c = queue.pop()
            if (r,c) in visitted:
                #cell already seen
                continue    
            visitted.add((r,c))
            for newR, newC in self.adjacents_positions_without_diagonals(r,c):
                if self.get_value(newR,newC) in ["L","I","T","S"] and (newR,newC) not in visitted:
                    #new cell to check
                    queue.append((newR,newC))
                    
        return len(visitted) == len(self.regionList) * 4
    
    def getAdjacentCells(self, cell: Cell, same_region_only: bool = False, exclude: list[Cell] = None):
        if exclude is None: exclude = []
        adjacent_cells = []
        row_var = -1,  0,  1,  0
        col_var =  0,  1,  0, -1
        max = self.size - 1

        # Check up, right, down and left, respectively
        for i in range(len(row_var)):
            row = cell.getRow0() + row_var[i]
            col = cell.getCol0() + col_var[i]
            if row < 0 or col < 0 or row > max or col > max: continue
            new_cell: Cell = self.cellList[row][col]
            if (not same_region_only or cell.getRegionCell() == new_cell.getRegionCell()) and new_cell not in exclude:
                adjacent_cells.append(new_cell)

        return adjacent_cells
    

    def addShape(self, shapes: list, shape: list, directions: list, already_found_shapes: set[frozenset[Cell]]):
        
        frozen_shape = frozenset(shape)
        if frozen_shape in already_found_shapes: return
        shape_type = whichShape(directions)
        if not shape_type: return
        already_found_shapes.add(frozen_shape)
        new_elem = (shape_type, frozen_shape)
        shapes.append(new_elem)
    

    def cellDirection(self, cell1: Cell, cell2: Cell) -> int:
        '''
        Returns the direction from cell1 to cell2 if they are adjacent, excluding diagonals.

        Up: 1  
        Down: -1  
        Left: 2  
        Right: -2  

        Returns 0 if the cells are not adjacent.
        '''
        row_diff = cell1.getRow0() - cell2.getRow0()
        col_diff = cell1.getCol0() - cell2.getCol0()
        if abs(row_diff) + abs(col_diff) != 1: return 0 # The cells are not adjacent
        if row_diff: return row_diff
        else: return col_diff * 2


    def getPossibleShapesStartingOnCell(self, cell: Cell, already_found_shapes: set[frozenset[Cell]]) -> list:
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
        stack.append(self.getAdjacentCells(current_cell, same_region_only=True))

        # Search for shapes
        while stack:

            if num_cells == 4 or not stack[-1]:
                if num_cells == 4: self.addShape(shapes, shape, directions, already_found_shapes)
                else: stack.pop()
                if directions: directions.pop()
                assert current_cell == shape[-1]
                shape.pop()
                num_cells -= 1
                if shape: current_cell = shape[-1]

            elif num_cells == 3 and allEqual(directions) and tuple(shape) not in possible_T_verified: # Try to add T shapes
                possible_T_verified.add(tuple(shape))
                possible_cells = self.getAdjacentCells(shape[-2], same_region_only=True, exclude=shape)
                for possible_cell in possible_cells:
                    t_directions = directions.copy()
                    t_directions.append(-t_directions[-1])
                    t_directions.append(self.cellDirection(shape[-2], possible_cell))
                    t_shape = shape.copy()
                    t_shape.append(possible_cell)
                    self.addShape(shapes, t_shape, t_directions, already_found_shapes)

            else:
                direction = self.cellDirection(current_cell, stack[-1][-1])
                assert direction != 0
                directions.append(direction)
                current_cell = stack[-1][-1]
                stack[-1].pop()
                shape.append(current_cell)
                num_cells += 1
                if num_cells < 4: stack.append(self.getAdjacentCells(current_cell, same_region_only=True, exclude=shape))

        return shapes


        
    def possibleShapes(self, region: Region) -> list:
        '''
        Returns a list of (shape, cellsWithShape)
        '''
        possible_shapes = []
        already_found_shapes = set()
        region_cells = region.getCells()

        for cell in region_cells:
            possible_shapes.extend(self.getPossibleShapesStartingOnCell(cell, already_found_shapes))

        return possible_shapes
    
    def fillCell(self,row,col,shape):
        cell = self.cellList[row-1][col-1]
        cell.putShape(shape)
    
    def addActionsToRegions(self,region):
        possibleActions = board.possibleShapes(region) 
        for shape,cellsOccupied in possibleActions:
            coords = set()
            for cell in cellsOccupied:
                coords.add((cell.row,cell.col))
            adjacentRegions = set()
            for cell in cellsOccupied:
                #gets the adjacent regions for the shape
                adjacentValues = board.adjacent_values_without_diagonals(cell.row,cell.col)
                for value in adjacentValues:
                    if value not in ["L","I","T","S"]:
                        value = int(value)
                        if value != region.value:
                            adjacentRegions.add(value)
            if len(adjacentRegions) == 0:
                #its impossible for the shape to touch any other shape
                continue
            region.addPossibility((shape,coords,adjacentRegions))
            
    def doOverlapRegion(self,region):
        first = True
        sameShape = True
        shapeOverlap = ""
        overlappedCoords = set()
        possibilities = region.getPossibilities()
        #possibility = (shape, cellsOccupied, regionTouching)
        for possibility in possibilities:
            shape = possibility[0]
            coords = possibility[1]
            if first:
                overlappedCoords = coords
                first = False
            else:
                overlappedCoords = overlappedCoords.intersection(coords)
            if shapeOverlap == "" and sameShape:
                #first cell
                shapeOverlap = shape
            elif shapeOverlap != shape and sameShape:
                #found the first different shape
                sameShape = False
        
        if sameShape:
            return overlappedCoords,shapeOverlap
        
        return overlappedCoords,"F"
    
    def removeTouching(self,regionToRemove,shapeToRemove,coordsToCheck):
        region = self.findRegion(regionToRemove)
        possibleActions = region.getPossibilities()
        actionsAfterCheck = []
        
        touching = set() #set of coords that the original shape is touching
        for row,col in coordsToCheck:
            touchingPos = self.adjacents_positions_without_diagonals(row,col)
            for coord in touchingPos:
                if coord not in coordsToCheck:
                    touching.add(coord)
                
        for possibility in possibleActions:
            found = False
            if possibility[0] == shapeToRemove:
                #need to check if they are touching
                for coord in possibility[1]:
                    if coord in touching:
                        #they are touching -> remove
                        found = True
                        break 
            if not found:
                actionsAfterCheck.append(possibility)
                
        region.possibilities = actionsAfterCheck
        
    def verifyShapes(self,regionToRemove):
        region = self.findRegion(regionToRemove)
        possibleActions = region.getPossibilities()
        actionsAfterCheck = []
        
        for action in possibleActions:
            if not self.madeSquares(action[1]):
                actionsAfterCheck.append(action)
        region.possibilities = actionsAfterCheck
        
        
    def addActions(self):
        for region in self.regionList:
            self.addActionsToRegions(region)
            
    def getRegionTouching(self,coords,originalRegionValue):
        touching = set() #set of regions that the original shape is touching
        for r,c in coords:
            touchingPos = self.adjacents_positions_without_diagonals(r,c)
            for row,col in touchingPos:
                region = self.get_region_cell(row,col)
                if region!=originalRegionValue:
                    touching.add(region)

        return touching
            
    def doOverlap(self):
        for region in self.regionList:
            overlappedCoords, overlappedShape = self.doOverlapRegion(region)
            if overlappedShape in ["L","I","T","S"]:
                #the region has a shape
                regionTouching, _ = region.putShape(overlappedShape,overlappedCoords) #puts the shape on region
                for regionToRemove in regionTouching:
                    self.removeTouching(regionToRemove, overlappedShape, overlappedCoords) #verifies all actions of the adjacent regions -> checks for touching with same shape
            elif len(overlappedCoords)>0:
                regionTouching = self.getRegionTouching(overlappedCoords,region.value)

            for row,col in overlappedCoords:
                self.fillCell(row,col,overlappedShape)
                
            for regionToCheck in regionTouching:   
                self.verifyShapes(regionToCheck) #verifies all actions of the adjacent regions -> checks for squares
                
            

    
    def preProcess(self):
        #goes through every region andc
        self.addActions() #1- checks every possible action 
        self.doOverlap() #2- does overlap and #3- removes possibilities from adjacent regions
  
                
    def solve(self):
        #chooses the region with the less possibilities
        minPossibilities = 0
        regionToSolve = None
        first = True
        
        for region in self.regionList:
            if not region.isFilled:
                if first:
                    minPossibilities = len(region.possibilities)
                    regionToSolve = region
                    first = False
                else:
                    if len(region.possibilities) < minPossibilities:
                        minPossibilities = len(region.possibilities)
                        regionToSolve = region
        
        if minPossibilities == 1:
            print(f"solve region {regionToSolve.value} with only one action")
        else:
            print(regionToSolve.possibilities)
            print(f"solve region {regionToSolve.value} with {minPossibilities} actions")
            
        return regionToSolve
            
          
        
        

class Nuruomino(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.initial = NuruominoState(board)

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        
        return None       

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        return None
        

    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        return None

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    
if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    board.preProcess()
    board.solve()
    
    #solution_node = depth_limited_search(problem)
    #if isinstance(solution_node,str) or solution_node == None:
    #    print("No solution found")
    #else:
    #    #found solution
    #    solution_state = solution_node.state
    #    print(solution_state.board.print())
