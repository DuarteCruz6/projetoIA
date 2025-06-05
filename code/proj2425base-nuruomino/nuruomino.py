# Grupo 32:
# 110181 Duarte Cruz
# 110239 André Pagaime

from sys import stdin
from search import *  # Import the classes from search.py
import numpy as np

####################### Auxiliar Functions #######################

#returns true if all elements from the list are the same
def allEqual(lst: list|tuple) -> bool:
    if not lst: return True
    last_elem = lst[0]
    for elem in lst:
        if elem != last_elem: return False
    return True

#returns the shape based on the directionList
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
        self.flagOccupied = False #true if it is occupied
    
    #used to use this cell but with new reference
    def copy(self) -> 'Cell':
        copied = Cell(self.regionValue, self.row, self.col)
        copied.shape = self.shape
        copied.flagOccupied = self.flagOccupied
        return copied
    
    #returns the cell's shape if it is occupied, otherwise returns the region
    def get_value(self) -> str:
        if self.flagOccupied:
            #the cell is occupied
            return self.shape
        return str(self.regionValue)
    
    #puts a shape on the cell
    def putShape(self,shape) -> None:
        self.shape = shape
        self.flagOccupied = True
        
    # Make Cell hashable
    def __hash__(self) -> int:
        return hash((self.row, self.col))

#struct Region
class Region:
    def __init__(self, value:int, cells:list):
        self.value = value #region value
        self.cells = cells #list of cells inside of the region
        self.possibilities = [] #list of actions that are possible in this region
        self.isFilled = False #flag for when the region is filled
        self.canTouch = set() #regions that the region can touch
        self.adjacentPossibilities = {} #dictionary that is [regionAdjacent] = number of possibilities that touch the region
        self.isIsland = False
        
    #used to use this region but with new reference
    def copy(self, copied_cells) -> 'Region':
        copied = Region(self.value, copied_cells)
        copied.possibilities = self.possibilities.copy()
        copied.isFilled = self.isFilled
        copied.canTouch = self.canTouch.copy()
        copied.adjacentPossibilities = self.adjacentPossibilities.copy()
        copied.isIsland = self.isIsland
        return copied
            
    #adds a new cell to the region   
    def addCell(self, newCell:Cell) -> None:
        self.cells.append(newCell) 
    
    #adds a possibility to the region
    def addPossibility(self,possibility) -> None:
        #possibility = (shape, cellsOccupied, regionTouching)
        if not self.isFilled:
            self.possibilities.append(possibility) #adds possibility
            for regionAdjacent in possibility[2]:
                self.canTouch.add(regionAdjacent) #adds regionAdjacent to canTouch and to the dictionary
                if regionAdjacent in self.adjacentPossibilities:
                    self.adjacentPossibilities[regionAdjacent]+=1
                else:
                    self.adjacentPossibilities[regionAdjacent]= 1
    
    #puts shape on a region and its cells
    def putShape(self,shapeFinal,coords):
        if not self.isFilled:
            finalActions = []
            for shape,cellsOccupied, regionTouching in self.possibilities:
                if shape == shapeFinal:
                    corresponds = True
                    for coordinate in coords:
                        if coordinate not in cellsOccupied:
                           corresponds = False 
                    if corresponds:
                        finalActions.append((shape,cellsOccupied,regionTouching))

            if len(finalActions) == 1:
                #only one action remains
                regionTouching = finalActions[0][2]
                self.isFilled = True

            return regionTouching, finalActions

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
    
    #adds a list of cells corresponding to a row (cell struct)
    def addLine(self, line:list) -> None:
        "Recebe a lista do board"
        self.cellList.append(line)
    
    #adds a new region to the list of regions
    def addRegion(self, region:Region) -> None:
        self.regionList.append(region)
    
    #returns a cell's value (shape, if occupied. regionValue if not)
    def get_value(self, row:int, col:int) -> str:
        cell = self.cellList[row-1][col-1]
        return cell.get_value()

    #returns a cell's region
    def get_region_cell(self,row,col) -> int:
        cell = self.cellList[row-1][col-1]
        return cell.regionValue
    
    #returns the coordinates of the cell received adjacents (inclunding diagonals)
    def adjacent_positions(self, row:int, col:int) -> list:
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
    
    #returns the coordinates of the cell received adjacents (without diagonals)
    def adjacents_positions_without_diagonals(self, row:int, col:int) -> list:
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

    #returns the value of the adjacents cells of the cell received (inclunding diagonals)
    def adjacent_values(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, incluindo diagonais."""
        listAdjacentValues = []
        
        listAdjacentPos = self.adjacent_positions(row,col) #gets all adjacent position of the cell
        
        for row,col in listAdjacentPos:
            #goes through every adjacent cell
            listAdjacentValues.append(self.get_value(row,col)) #gets the region value from the adjacent cell
        
        return listAdjacentValues
    
    #returns the value of the adjacents cells of the cell received (without diagonals)
    def adjacent_values_without_diagonals(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, sem diagonais."""
        listAdjacentValues = []
        
        listAdjacentPos = self.adjacents_positions_without_diagonals(row,col) #gets all adjacent position of the cell
        
        for row,col in listAdjacentPos:
            #goes through every adjacent cell
            listAdjacentValues.append(self.get_value(row,col)) #gets the region value from the adjacent cell
        
        return listAdjacentValues
            
    
    @staticmethod
    #reads the input and creates the board
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
                    if region.value == number:
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
                        if region.value == number:
                            #found the region
                            region.addCell(newCell) #adds the cell to the region instance
                            break
                col+=1
            board.addLine(lineCells) #adds the row to the board instance

        return board
    
    #returns the region that corresponds to the regionValue
    def findRegion(self,regionValue) -> Region:
        for region in self.regionList:
            if region.value == regionValue:
                return region
        return None
    
    #prints the board
    def print(self) -> None:
        max = self.size
        for row in self.cellList:
            r = ""
            c = 0
            for cell in row:
                c+=1
                value = cell.get_value()
                if value == "X":
                    value = cell.regionValue
                    
                if c != max:
                    r+= f"{value}\t"
                else:
                    r+= f"{value}"
            print(r)     
    
    #returns true if the shape received makes a square  
    def madeSquares(self,cellsOccupied) -> bool:
        max = self.size
        for row,col in cellsOccupied:
            #we need to check above, under, right and left values 
            if row>1:
                #we need to check the above position
                if self.get_value(row-1,col) in ["L","S","T","I"] or (row-1,col) in cellsOccupied:
                    #the above position is occupied, so now we need to check the left and the right
                    if col>1:
                        if self.get_value(row,col-1) in ["L","S","T","I"] or (row,col-1) in cellsOccupied:
                            #the left position is occupied, so now we need to check the top left corner
                            if self.get_value(row-1,col-1) in ["L","S","T","I"] or (row-1,col-1) in cellsOccupied:
                                #it made a square
                                return True
                    if col<max:
                        if self.get_value(row,col+1) in ["L","S","T","I"] or (row,col+1) in cellsOccupied:
                            #the right position is occupied, so now we need to check the top right corner
                            if self.get_value(row-1,col+1) in ["L","S","T","I"] or (row-1,col+1) in cellsOccupied:
                                #it made a square
                                return True
            if row<max:
                #we need to check the under position
                if self.get_value(row+1,col) in ["L","S","T","I"] or (row+1,col) in cellsOccupied:
                    #the under position is occupied, so now we need to check the left and the right
                    if col>1:
                        if self.get_value(row,col-1) in ["L","S","T","I"] or (row,col-1) in cellsOccupied:
                            #the left position is occupied, so now we need to check the bottom left corner
                            if self.get_value(row+1,col-1) in ["L","S","T","I"] or (row+1,col-1) in cellsOccupied:
                                #it made a square
                                return True
                    if col<max:
                        if self.get_value(row,col+1) in ["L","S","T","I"] or (row,col+1) in cellsOccupied:
                            #the right position is occupied, so now we need to check the bottom right corner
                            if self.get_value(row+1,col+1) in ["L","S","T","I"] or (row+1,col+1) in cellsOccupied:
                                #it made a square
                                return True
        return False   
    
    #checks if every region's shape is touching
    def verifyConnectivity(self) -> bool:
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
    
    #returns the cell's adjacent without diagonals
    #if same_region_only == True: returns the cell's adjacent FROM THE SAME REGION without diagonals  
    #exclude: returns the cell's adjacent without diagonals and without the cells in exclude
    def getAdjacentCells(self, cell: Cell, same_region_only: bool = False, exclude: list[Cell] = None) -> list:
        if exclude is None: exclude = []
        adjacent_cells = []
        row_var = -1,  0,  1,  0
        col_var =  0,  1,  0, -1
        max = self.size - 1

        # Check up, right, down and left, respectively
        for i in range(len(row_var)):
            row = cell.row - 1 + row_var[i]
            col = cell.col - 1 + col_var[i]
            if row < 0 or col < 0 or row > max or col > max: continue
            new_cell: Cell = self.cellList[row][col]
            if (not same_region_only or cell.regionValue == new_cell.regionValue) and new_cell not in exclude:
                adjacent_cells.append(new_cell)

        return adjacent_cells
    
    #adds a shape to the possible shapes of a region
    def addShape(self, shapes: list, shape: list, directions: list, already_found_shapes: set[frozenset[Cell]]) -> None:
        frozen_shape = frozenset(shape)
        if frozen_shape in already_found_shapes: return
        shape_type = whichShape(directions)
        if not shape_type: return
        already_found_shapes.add(frozen_shape)
        new_elem = (shape_type, frozen_shape)
        shapes.append(new_elem)
    
    #Returns the direction from cell1 to cell2 if they are adjacent, excluding diagonals. 
    def cellDirection(self, cell1: Cell, cell2: Cell) -> int:
        #Up: 1  
        #Down: -1  
        #Left: 2  
        #Right: -2  
        #Returns 0 if the cells are not adjacent.
        row_diff = cell1.row - cell2.row
        col_diff = cell1.col - cell2.col
        if abs(row_diff) + abs(col_diff) != 1: return 0 # The cells are not adjacent
        if row_diff: return row_diff
        else: return col_diff * 2

    #returns all possible shapes that start on cell
    #This function does not return all possible shapes that include the cell!
    def getPossibleShapesStartingOnCell(self, cell: Cell, already_found_shapes: set[frozenset[Cell]]) -> list:
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

            if num_cells == 3 and allEqual(directions) and frozenset(shape) not in possible_T_verified: # Try to add T shapes
                possible_T_verified.add(frozenset(shape))
                possible_cells = self.getAdjacentCells(shape[-2], same_region_only=True, exclude=shape)
                for possible_cell in possible_cells:
                    t_directions = directions.copy()
                    t_directions.append(-t_directions[-1])
                    t_directions.append(self.cellDirection(shape[-2], possible_cell))
                    t_shape = shape.copy()
                    t_shape.append(possible_cell)
                    self.addShape(shapes, t_shape, t_directions, already_found_shapes)

            elif num_cells == 4 or not stack[-1]:
                if num_cells == 4: self.addShape(shapes, shape, directions, already_found_shapes)
                else: stack.pop()
                if directions: directions.pop()
                assert current_cell == shape[-1]
                shape.pop()
                num_cells -= 1
                if shape: current_cell = shape[-1]

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


    #Returns a list of (shape, cellsWithShape)
    def possibleShapes(self, region: Region) -> list:
        possible_shapes = []
        already_found_shapes = set()
        region_cells = region.cells

        for cell in region_cells:
            possible_shapes.extend(self.getPossibleShapesStartingOnCell(cell, already_found_shapes))

        return possible_shapes
    
    #puts shape on the cell
    def fillCell(self,row,col,shape) -> None:
        cell = self.cellList[row-1][col-1]
        cell.putShape(shape)
    
    #adds all possible actions to the region
    def addActionsToRegions(self,region) -> None:
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
    
    #does overlaps on region's shape       
    def doOverlapRegion(self,region) -> tuple:
        first = True
        sameShape = True
        shapeOverlap = ""
        overlappedCoords = set()
        possibilities = region.possibilities
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
    
    #removes actions that touches the same shape
    def removeTouching(self,regionToRemove,shapeToRemove,coordsToCheck) -> None:
        region = self.findRegion(regionToRemove)
        possibleActions = region.possibilities
        actionsToRemove = []
        
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
            if found:
                actionsToRemove.append(possibility)
        
        for action in actionsToRemove:     
            self.removePossibility(action, region)
    
    #removes every possibility from region that makes squares   
    def verifyShapes(self,regionToRemove) -> None:
        region = self.findRegion(regionToRemove)
        possibleActions = region.possibilities
        actionsToRemove = []
        
        for action in possibleActions:
            if self.madeSquares(action[1]):
                actionsToRemove.append(action)
                
        for action in actionsToRemove:     
            self.removePossibility(action, region)
        
    #adds action to every region  
    def addActions(self) -> None:
        for region in self.regionList:
            self.addActionsToRegions(region)
    
    #returns the regions that the shape is touching        
    def getRegionTouching(self,coords,originalRegionValue) -> set:
        touching = set() #set of regions that the original shape is touching
        for r,c in coords:
            touchingPos = self.adjacents_positions_without_diagonals(r,c)
            for row,col in touchingPos:
                region = self.get_region_cell(row,col)
                if region!=originalRegionValue:
                    touching.add(region)

        return touching
    
    #does overlap in every region     
    def doOverlap(self) -> None:
        for region in self.regionList:
            if not region.isFilled:
                regionTouching = []
                overlappedCoords, overlappedShape = self.doOverlapRegion(region)
                if overlappedShape in ["L","I","T","S"]:
                    #the region has a shape
                    regionTouching, updatedPossibilities = region.putShape(overlappedShape,overlappedCoords) #puts the shape on region
                    for possibility in region.possibilities:
                        if possibility not in updatedPossibilities:
                            self.removePossibility(possibility, region)
                    
                    for regionToRemove in regionTouching:
                        self.removeTouching(regionToRemove, overlappedShape, overlappedCoords) #verifies all actions of the adjacent regions -> checks for touching with same shape
                elif len(overlappedCoords)>0:
                    regionTouching = self.getRegionTouching(overlappedCoords,region.value)

                for row,col in overlappedCoords:
                    self.fillCell(row,col,overlappedShape)

                for regionToCheck in regionTouching:   
                    self.verifyShapes(regionToCheck) #verifies all actions of the adjacent regions -> checks for squares

    #removes every possibility that only touches region's that are not in regionToRemove.canTouch
    def touchingPossibilities(self, regionToRemove) -> None:
        removePossibilities = []
        for possibility in regionToRemove.possibilities:
            if not self.everyRegionIsIsland():
                remove = True
                for regionCheck in possibility[2]:
                    if regionCheck in regionToRemove.canTouch:
                        remove = False
                        break
                    
                if remove:
                    removePossibilities.append(possibility)
        
        for possibility in removePossibilities:
            self.removePossibility(possibility, regionToRemove)
                
    #removes a possibility from regionToRemove
    def removePossibility(self,possibility, regionToRemove) -> None:
        updatedPossibilities = []
        for checkPossibility in regionToRemove.possibilities:
            if checkPossibility != possibility:
                updatedPossibilities.append(checkPossibility)
        
        regionToRemove.possibilities = updatedPossibilities
        
        for touchingRegionValue in possibility[2]:
            regionToRemove.adjacentPossibilities[touchingRegionValue] -= 1 
            if regionToRemove.adjacentPossibilities[touchingRegionValue] == 0:
                #there are no connections regionToRemove -> touchingRegion
                #so we can remove every possibility from touchingRegion that only touches regionToRemove
                touchingRegion = self.findRegion(touchingRegionValue)
                if touchingRegion.value in regionToRemove.canTouch:
                    regionToRemove.canTouch.remove(touchingRegion.value) #removes the connection regionToRemove -> touchingRegion
                if regionToRemove.value in touchingRegion.canTouch:
                    touchingRegion.canTouch.remove(regionToRemove.value) #removes the connection touchingRegion -> regionToRemove
                self.touchingPossibilities(touchingRegion)
                if self.isIsland(touchingRegion):
                    #touchingRegion is an island
                    self.dealIsland(touchingRegion)
                    
        if self.isIsland(regionToRemove):
            #this region became an island
            self.dealIsland(regionToRemove)
                    
    #returns true if every region except one is an island
    def everyRegionIsIsland(self) -> bool:
        nonIsland = 0
        for region in self.regionList:
            if not region.isIsland:
                nonIsland += 1
        return nonIsland == 1
    
    #transforms a region into a bridge
    def becomeBridge(self, bridgeRegion, islandRegionValue) -> None:
        if islandRegionValue in bridgeRegion.canTouch:
            bridgeRegion.canTouch.remove(islandRegionValue) #removes the connection bridge -> island
            
        removePossibilities = []
        for possibility in bridgeRegion.possibilities:
            #removes every possibility that is not in touch with islandRegion or that only touches in islandRegion
            touchingRegions = possibility[2]
            if islandRegionValue not in touchingRegions:
                #this possibility doesn't touch the islandRegion
                removePossibilities.append(possibility)
                
            elif not self.everyRegionIsIsland():
                remove = True
                for regionCheck in touchingRegions:
                    if regionCheck in bridgeRegion.canTouch:
                        remove = False
                        break
                
                if remove:
                    removePossibilities.append(possibility)
                
        for possibility in removePossibilities:
            self.removePossibility(possibility, bridgeRegion)
            
        if self.isIsland(bridgeRegion):
            self.dealIsland(bridgeRegion)
    
    #does the treatment of an island region (makes its only adjacent a bridge)
    def dealIsland(self,islandRegion) -> None:
        islandRegion.isIsland = True
        bridgeRegion = self.findRegion(list(islandRegion.canTouch)[0])
        self.becomeBridge(bridgeRegion, islandRegion.value) #transforms the only adjacent region into a bridge
    
    #returns true if the region is an island
    def isIsland(self,region) -> bool:
        if region.isIsland:
            #already checked
            return False
        return len(region.canTouch) == 1
    
    #deals with all islands on the board
    def checkIslands(self) -> None:
        for region in self.regionList:
            if self.isIsland(region):
                #this region is an island
                self.dealIsland(region)
                
    #does the pre process
    def preProcess(self) -> None:
        #1 -> adds every action possible to each region
        self.addActions()
        #2 -> checks for islands
        self.checkIslands()
        #3 -> does overlaps
        self.doOverlap()
        
        
    #chooses the region with the less possibilities and returns the possibilities        
    def solve(self) -> list:
        minPossibilities = 0
        regionToSolve = None
        first = True
        touching = 0
        
        for region in self.regionList:
            if not region.isFilled:
                numPossibilities = len(region.possibilities)
                numTouching = len(region.canTouch)
                if first:
                    minPossibilities = numPossibilities
                    regionToSolve = region
                    touching = numTouching
                    first = False
                else:
                    if (numPossibilities < minPossibilities) or (numPossibilities == minPossibilities and numTouching > touching):
                        touching = numTouching
                        minPossibilities = numPossibilities
                        regionToSolve = region 
        if first:
            #no possibilities in any region
            return []
        return regionToSolve.possibilities
    
    #does an action 
    def doAction(self,action) -> None: 
        #possibility = (shape, cellsOccupied, regionTouching)
        shape = action[0]
        cellsOccupied = action[1]
        
        coords = list(cellsOccupied)[0]
        
        row,col = coords
        regionValue = self.get_region_cell(row,col)
        region = self.findRegion(regionValue)
        
        _ , updatedPossibilities = region.putShape(shape,cellsOccupied) #puts the shape on region
        
        for possibility in region.possibilities:
            if possibility not in updatedPossibilities:
                self.removePossibility(possibility, region) #removes the possibilities that are now impossible
        
        regionTouching = action[2]
        for regionToRemove in regionTouching:
            self.removeTouching(regionToRemove, shape, cellsOccupied) #verifies all actions of the adjacent regions -> checks for touching with same shape
            
        for row,col in cellsOccupied:
            self.fillCell(row,col,shape) #fills the cells
        
        for regionToCheck in regionTouching:   
                self.verifyShapes(regionToCheck) #verifies all actions of the adjacent regions -> checks for squares  
        
        for regionAdjacentValue in region.canTouch:
            if regionAdjacentValue not in regionTouching:
                regionAdjacent = self.findRegion(regionAdjacentValue)
                self.touchingPossibilities(regionAdjacent) #removes all possibilities from adjacents that only touched the original region
            
            

class Nuruomino(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.initial = NuruominoState(board)

    def actions(self, state: NuruominoState):
        """Retorna a lista de ações da região com menos possibilidades"""
        
        board = state.board
        return board.solve()    

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        board = state.board.copy()
        board.doAction(action)
        return NuruominoState(board)
        

    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #checks if every region is occupied 
        for region in state.board.regionList:
            if not region.isFilled:
                return False
            
        #checks if every shape is touching
        return state.board.verifyConnectivity()

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

import time, os
    
if __name__ == "__main__":
    start = time.time()
    board = Board.parse_instance()
    problem = Nuruomino(board)
    board.preProcess() #does the pre process
    
    solution_node = depth_first_tree_search(problem)
    if isinstance(solution_node,str) or solution_node == None:
        print("No solution found")
    else:
        #found solution
        solution_state = solution_node.state
        solution_state.board.print()
    end = time.time()
    final = end - start
    
    # Fazedor de Excel
    
