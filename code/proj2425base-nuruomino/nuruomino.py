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
    
    def getRow(self) -> int:
        return self.row

    def getCol(self) -> int:
        return self.col
    
    def getRegionCell(self) -> int:
        return self.regionValue
        
    def occupyCell(self) -> None:
        self.flagOccupied = True
        
    def putShapeCell(self, shape:str) -> None:
        self.shape = shape
        self.flagOccupied = True

#struct Region
class Region:
    def __init__(self, value:int, cells:list):
        self.value = value #region value
        self.cells = cells #list of cells inside of the region
        
    def getValue(self) -> int:
        return self.value
    
    def getCells(self) -> list:
        return self.cells
     
    #adds a new cell to the region   
    def addCell(self, newCell:Cell) -> None:
        self.cells.append(newCell) 
    
    def putShape(self,shape,shapeForm) -> None:
        firstCell = self.cells[0]
        beginningRow = firstCell.getRow()
        beginningCol = firstCell.getCol()
        
        for r in shapeForm:
            colNow = beginningCol
            for c in r:
                if c == 1:
                    #we want to occupy this cell
                    cell = self.findCell(beginningRow,colNow)
                    cell.putShapeCell(shape)
                colNow+=1
            beginningRow+=1
    
    def findCell(self,row,col) -> Cell:
        for cell in self.cells:
            if cell.getRow() == row and cell.getCol() == col:
                return cell

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
    
    def __init__(self, boardList, size, regionList):
        self.boardList = boardList #list of cells (Cell struct)
        self.size = size #size of the board
        self.regionList = regionList #list of regions (Region struct)
        
    def addLine(self, line:list) -> None:
        "Recebe a lista do board"
        self.boardList.append(line) #adds a list of cells corresponding to a row (cell struct)
        
    def addRegion(self, region:Region) -> None:
        #adds a new region to the list of regions
        self.regionList.append(region)
    
    def get_value(self, row:int, col:int) -> int:
        cell = self.boardList[row-1][col-1]
        if cell.flagOccupied:
            #the cell is occupied
            return cell.shape
        return cell.getRegionCell()

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
        
        if row!=0: #checks if the cell is on the first row
            if col!=0:
                listAdjacentPos.append([row-1,col-1]) #top left corner
            listAdjacentPos.append([row-1,col]) #position above
            if col!=self.size-1:
                listAdjacentPos.append([row-1,col+1]) #top right corner
            
        if col!=0: #checks if the cell is on the left side of the board
                listAdjacentPos.append([row,col-1]) #position on the left
                
        if col!=self.size-1: #checks if the cell is on the right side of the board
            listAdjacentPos.append([row,col+1]) #position on the right 
            
        if row!=self.size-1: #checks if the cell is on the last row
            if col!=0:
                listAdjacentPos.append([row+1,col-1]) #bottom left corner
            listAdjacentPos.append([row+1,col]) #position under
            if col!=self.size-1:
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
        board = Board([],n,[]) #creates the board
        
        firstLineCells = [] #lists of Cells from the first line
        col = 0
        for number in line:
            #goes through every value in the input, which corresponds to a region value
            number = int(number) 
            newCell = Cell(number,0,col) #creates the new cell -> regionValue = number, row = 0, col = col
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
        
        for row in range(1,n):
            #goes through every row left
            col = 0
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


class Nuruomino(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        #TODO
        pass 

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        #TODO
        pass 

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        #action -> (regionValue, shape, form of shape)
        regionValue = action[0]
        shape = action[1]
        shapeForm = action[2]
        region = state.board.regionList[regionValue-1]
        region.putShape(shape,shapeForm)
        return  state
        

    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #TODO
        pass 

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass
    
    
# Ler grelha do figura 1a:
board = Board.parse_instance()
# Criar uma instância de Nuruomino:
problem = Nuruomino(board)
# Criar um estado com a configuração inicial:
initial_state = NuruominoState(board)
# Mostrar valor na posição (2, 1):
print(initial_state.board.get_value(2, 1))
# Realizar ação de colocar a peça L, cuja forma é [[1, 1],[1, 0],[1, 0]] na região 1
result_state = s1 = problem.result(initial_state, (1,'L', [[1, 1],[1, 0],[1, 0]]))
# Mostrar valor na posição (2, 1):
print(result_state.board.get_value(2, 1))
# Mostrar os valores de posições adjacentes
print(result_state.board.adjacent_values(2,2))