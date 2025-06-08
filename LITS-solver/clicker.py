import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
from scanner import getMatrix, scanInstance
from nuruomino import getSolution

BOARDSIZE = None
URL = None

#clicks on the correct cells
def clickSolution(driver, matrixElements, solution):
    for r in range(BOARDSIZE):
        for c in range(BOARDSIZE):
            value = solution[r][c]
            if value in ["L","I","T","S"]:
                element = matrixElements[r][c]
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element) 
                element.click()
                
#opens the driver
def openDriver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

#opens the url
def openUrl(driver, firstFlag):
    driver.get(URL)  # Your puzzle page
    driver.maximize_window()
    
    if firstFlag:
        #click on cookies buttons
        reject_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'sn-b-custom'))
        )
        reject_button.click()

        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'sn-b-save'))
        )
        confirm_button.click()


#waits for 30 seconds then closes the driver
def closeDriver(driver):
    driver.quit()
    
#asks the user what he wants to do
def console():
    global BOARDSIZE, URL
    validAns = False
    while not validAns:
        print("Games available:")
        print("1- 6x6 Normal LITS")
        print("2- 6x6 Hard LITS")
        print("3- 8x8 Normal LITS")
        print("4- 8x8 Hard LITS")
        print("5- 10x10 Normal LITS")
        print("6- 10x10 Hard LITS")
        print("7- 15x15 Normal LITS")
        print("8- 15x15 Hard LITS")
        print("9- 20x20 Normal LITS")
        print("10- 20x20 Hard LITS")
        print("11- Special Daily LITS")
        print("12- Special Weekly LITS")
        print("13- Special Monthly LITS")
        print(r"\q for quitting")
        ans = input("Select Mode: ")
        try:
            ans = int(ans)
            if ans>0 and ans<14:
                validAns = True
                BOARDSIZE = [0,6,6,8,8,10,10,15,15,20,20,30,40,50][ans]
                URL = f"https://www.puzzle-lits.com/?size={ans-1}"
        except ValueError:
            if ans == r"\q":
                return True
    return False
    

def playStart(driver, first):
    if not console():
        openUrl(driver, first)
        startScanner = time.time()
        matrixElements = getMatrix(BOARDSIZE, driver)
        table = scanInstance(matrixElements)
        endScanner = time.time()
        print(f"scan finished in {endScanner-startScanner}, finding solution")
        startSolution = time.time()
        solution = getSolution(table)
        endSolution = time.time()
        print(f"found solution in {endSolution-startSolution}, clicking all correct cells!")
        startClicking = time.time()
        clickSolution(driver, matrixElements,solution)
        endClicking = time.time()
        print(f"clicking finished in {endClicking-startClicking}")
        return True
    return False

def playAgain():
    while True:
        ans = input("Play agai? Y/n ")
        if ans == "Y":
            return True
        if ans == "n":
            return False

def clear_console():
    # Para Windows
    if os.name == 'nt':
        os.system('cls')
    # Para Linux e macOS
    else:
        os.system('clear')
        
if __name__ == "__main__":
    start = time.time()
    driver = openDriver()
    first = True
    clear_console()
    while True:
        if playStart(driver, first):
            if not playAgain():
                break
            else:
                clear_console()
        else:
            break
        first = False
    end = time.time()
    print(f"process finished in {end-start}")
    closeDriver(driver)