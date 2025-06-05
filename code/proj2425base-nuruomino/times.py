######################## PARA FAZER O EXCEL ########################

import time, os, io, __main__

searches = {
    "DFS Tree": depth_first_tree_search,
    "DFS Graph": depth_first_graph_search,
    "BFS Tree": breadth_first_tree_search,
    "BFS Graph": breadth_first_graph_search,
    "Uniform Cost": uniform_cost_search,
    "Greedy": greedy_search,
    "A*": astar_search
}


def solveNuruomino(search) -> bool:
    board = Board.parse_instance()
    problem = Nuruomino(board)
    board.preProcess() #does the pre process
    
    solution_node = search(problem)
    if isinstance(solution_node,str) or solution_node == None:
        print("No solution found")
        return False
    else:
        #found solution
        solution_state = solution_node.state
        solution_state.board.print()
        return True
        

def testBoard(path: str, file: str) -> str:
    with open(f"{path}/{file}", "r") as f: return f.read()
        

# Get test files
path = "../sample-nuruominoboards"
files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))] # Get files
files = [f for f in files if f.endswith(".txt") and not f.endswith(".out.txt")] # Filter out the ones that are not the initial board
files.sort()

with open("../timesSearches.csv", "a") as f:
    for search in searches:
        first_iter = True
        line = search + ','
        for file in files:
            print(f"\nA TESTAR: {file} com a {search}")
            start = time.time()
            board_str = testBoard(path, file)
            __main__.stdin = io.StringIO(board_str)
            if solveNuruomino(searches[search]):
                end = time.time()
                elapsed = end - start
                print("Tempo: ", elapsed , "s", sep="")
                line += f"{str(round(elapsed, 3))},"
            else: line += "-,"
        line = line.rstrip(",")
        line += "\n"
        f.write(line)
