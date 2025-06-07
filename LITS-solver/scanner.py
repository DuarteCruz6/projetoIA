from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from clicker import BOARDSIZE

#returns the elements in a list
def getCellsSite(driver):
    cells = driver.find_elements(By.CSS_SELECTOR, "div.cell.selectable")
    return cells

#returns the matrix of elements of the website
def createMatrix(cells):
    matrix = []
    index = 0
    for r in range(BOARDSIZE):
        row = []
        for c in range(BOARDSIZE):
            cell = cells[index]
            index += 1
            row.append(cell)
        matrix.append(row)
    return matrix

def getNext(visited):
    for row in range(BOARDSIZE):
        for col in range(BOARDSIZE):
            if (row,col) not in visited:
                return (row,col)
            
def doDFS(firstCoord, matrixElements):
    visited = set()
    
    queue = [firstCoord]
    
    while queue:
        #while the queue has elements
        coordToCheck = queue.pop()

        visited.add(coordToCheck) 
        row, col = coordToCheck
        element = matrixElements[row][col]
        classes = element.get_attribute("class").split()
        
        if "br" not in classes and col!=BOARDSIZE-1:
            #go to the right
            coordToAdd = (row,col+1)
            if coordToAdd not in visited:
                queue.append(coordToAdd)
        if "bl" not in classes and col!=0:
            #go to the left
            coordToAdd = (row,col-1)
            if coordToAdd not in visited:
                queue.append(coordToAdd)
        if "bt" not in classes and row!=0:
            #go up
            coordToAdd = (row-1,col)
            if coordToAdd not in visited:
                queue.append(coordToAdd)
        if "bb" not in classes and row!=BOARDSIZE-1:
            #go down
            coordToAdd = (row+1,col)
            if coordToAdd not in visited:
                queue.append(coordToAdd)
    return visited
            
        
    

#returns the table as expected
def createTable(matrixElements):
    table = [[0 for _ in range(BOARDSIZE)] for _ in range(BOARDSIZE)]
    visited = set()
    regionValue = 1
    
    while len(visited) != BOARDSIZE*BOARDSIZE:
        #while not every cell visited        
        coordToCheck = getNext(visited)
        
        regionCoords = doDFS(coordToCheck,matrixElements)
        
        for coord in regionCoords:
            visited.add(coord)
            row,col = coord
            table[row][col] = regionValue
            
        regionValue +=1 
            
    return table

def getMatrix(driver):
    cells = getCellsSite(driver)
    matrixElements = createMatrix(cells)
    return matrixElements
    
def scanInstance(matrixElements):
    finalTable = createTable(matrixElements)
    return finalTable
    

        


