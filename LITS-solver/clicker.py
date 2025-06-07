import time
from nuruomino import *

BOARDSIZE = 30

#clicks on the correct cells
def clickSolution(matrixElements, solution):
    for r in range(BOARDSIZE):
        for c in range(BOARDSIZE):
            value = solution[r][c]
            if value in ["L","I","T","S"]:
                element = matrixElements[r][c]
                element.click()

#opens the driver
def openDriver():
    driver = webdriver.Chrome()
    driver.get("https://www.puzzle-lits.com/?size=10")  # Your puzzle page
    driver.maximize_window()
    
    #click on cookies buttons
    reject_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'sn-b-custom'))
    )
    reject_button.click()
    
    confirm_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'sn-b-save'))
    )
    confirm_button.click()
    
    return driver

#waits for 30 seconds then closes the driver
def closeDriver(driver):
    time.sleep(30)
    driver.quit()

import time
if __name__ == "__main__":
    driver = openDriver()
    start = time.time()
    print("scanning board...")
    matrixElements = getMatrix(driver)
    table = scanInstance(matrixElements)
    end = time.time()
    print(f"scan finished in {end-start}, finding solution")
    start = time.time()
    solution = getSolution(table)
    end = time.time()
    print(f"found solution in {end-start}, clicking all correct cells!")
    start = time.time()
    clickSolution(matrixElements,solution)
    end = time.time()
    print(f"process finished in {end-start}")
    closeDriver(driver)