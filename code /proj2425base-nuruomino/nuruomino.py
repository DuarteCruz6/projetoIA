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
        self.regionValue = regionValue
        self.row = row
        self.col = col
        self.flagOccupied = False #true if the cell is occupied
        self.shape = ""  #shape contained in the cell
    
    def getRow(self) -> int:
        return self.row

    def getCol(self) -> int:
        return self.col
        
    def occupyCell(self) -> None:
        self.flagOccupied = True
        
    def putShapeCell(self, shape:str) -> None:
        self.shape = shape
    
    def getRegionCell(self) -> int:
        return self.regionValue

class Region:
    def __init__(self, value:int, cells:list):
        self.value = value
        self.cells = cells
        
    def addCell(self, newCell:Cell) -> None:
        self.cells.append(newCell)
        
    def getValue(self) -> int:
        return self.value
    
    def getCells(self) -> list:
        return self.cells
    

class NuruominoState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = Nuruomino.state_id
        Nuruomino.state_id += 1

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro do Puzzle Nuruomino."""
    
    def __init__(self, boardList, size, regionList):
        self.boardList = boardList #inicializado como [] (lista vazia)
        self.size = size
        self.regionList = regionList

    def adjacent_regions(self, regionValue:int) -> list:
        """Devolve uma lista das regiões que fazem fronteira com a região enviada no argumento."""
        listAdjacentRegions = []
        print("looking for region value:",regionValue)
        for region in self.regionList:
            print("valor da regiao:", region.getValue())
            if region.getValue() == regionValue:
                print("found!, value:",regionValue)
                #found the region
                for cell in region.getCells():
                    listAdjacentValues = self.adjacent_values(cell.getRow(),cell.getCol())
                    for value in listAdjacentValues:
                        if value != regionValue and value not in listAdjacentRegions:
                            print(f"for position {cell.getRow()} {cell.getCol()}, found region",value)
                            listAdjacentRegions.append(value)
                break
                    
        return sorted(listAdjacentRegions)
    
    def adjacent_positions(self, row:int, col:int) -> list:
        """Devolve as posições adjacentes à região, em todas as direções, incluindo diagonais."""
        
        listAdjacentPos = []
        
        if row!=0:
            if col!=0:
                listAdjacentPos.append([row-1,col-1]) #top left corner
            if col!=self.size-1:
                listAdjacentPos.append([row-1,col+1]) #top right corner
            listAdjacentPos.append([row-1,col]) #position above
            
        if row!=self.size-1:
            if col!=0:
                listAdjacentPos.append([row+1,col-1]) #bottom left corner
            if col!=self.size-1:
                listAdjacentPos.append([row+1,col+1]) #bottom right corner
            listAdjacentPos.append([row+1,col]) #position under
        
        if col!=0:
                listAdjacentPos.append([row,col-1]) #position on the left
        if col!=self.size-1:
            listAdjacentPos.append([row,col+1]) #position on the right 
            
        return listAdjacentPos

    def adjacent_values(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, incluindo diagonais."""
        listAdjacentValues = []
        
        listAdjacentPos = self.adjacent_positions(row,col)
        
        for row,col in listAdjacentPos:
            cell = self.boardList[row][col]
            listAdjacentValues.append(cell.getRegionCell())
        
        return listAdjacentValues
            
        
    
    def addLine(self, line:list) -> None:
        "Recebe a lista do board"
        self.boardList.append(line)
        
    def addRegion(self, region:Region) -> None:
        #adds a new region to the list of regions
        self.regionList.append(region)
    
    
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
        regionsCreated = []
    
        line = stdin.readline().split() #lê a primeira linha
        n = len(line) #o board é nxn
        board = Board([],n,[]) #cria a instancia
        
        firstLineCells = [] #lists of Cells from the first line
        #creates cells from the first line
        col = 0
        for number in line:
            number = int(number)
            newCell = Cell(number,0,col)
            firstLineCells.append(newCell)
            if number not in valuesUsed:
                #new region
                newRegion = Region(number,[newCell])
                board.addRegion(newRegion)
                regionsCreated.append(newRegion)
                valuesUsed.append(number)
                print(f"created region {number} with position {0} {col}")
            else:
                #region already created
                for region in regionsCreated:
                    if region.getValue() == number:
                        #found the region
                        region.addCell(newCell)
                        print(f"added to region {number} position {0} {col}")
                        break
            col+=1
                
            
        board.addLine(firstLineCells) #adiciona a primeira linha ao board
        
        #recebe todo o input e adiciona ao board
        for row in range(1,n):
            col = 0
            lineCells = []
            line = stdin.readline().split()
            for number in line:
                number = int(number)
                newCell = Cell(number,row,col)
                lineCells.append(newCell)
                if number not in valuesUsed:
                    #new region
                    newRegion = Region(number,[newCell])
                    board.addRegion(newRegion)
                    regionsCreated.append(newRegion)
                    valuesUsed.append(number)
                    print(f"created region {number} with position {row} {col}")
                else:
                    #region already created
                    for region in regionsCreated:
                        if region.getValue() == number:
                            #found the region
                            region.addCell(newCell)
                            print(f"added to region {number} position {row} {col}")
                            break
                col+=1
            board.addLine(lineCells)
            
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

        #TODO
        pass 
        

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
    
    
board = Board.parse_instance()
print(board.adjacent_regions(1))
print(board.adjacent_regions(3))