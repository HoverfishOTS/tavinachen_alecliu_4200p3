import time

gameIsDone = False
board = [["-" for _ in range(8)] for _ in range(8)]

def start_game(humanFirst:bool, thinkTimeInSeconds:int) -> None:
    global currPlayer
    print("Game Started!")
    print_board()
    if humanFirst:
        currPlayer = "O"
        human_move()
    
    while not gameIsDone:
        ai_move(thinkTimeInSeconds)
        if gameIsDone:
            break
        human_move()

def print_board() -> None:
    print("  1 2 3 4 5 6 7 8")
    for i in range(len(board)):
        print(chr(ord('A')+i), " ".join(board[i]))

def ai_move(thinkTimeInSeconds: int):
    print("AI thinking...")

    depth = 1
    start_time = time.time()
    while time.time() < start_time + thinkTimeInSeconds:
        bestMove = alpha_beta_pruning(float('-inf'), float('inf'), depth)
        depth +=1
    make_move(bestMove[0], bestMove[1], "X")
    print("AI chose: ", bestMove[0], bestMove[1])
    print_board()
    check_win_condition()

def alpha_beta_pruning(a:int, b:int, maxDepth:int):
    bestScore = a
    for i in range(8):
        for j in range(8):
            if board[i][j] != "-":
                continue
            make_move(i, j, "X")
            score = max(a, b, maxDepth-1)
            if score > bestScore:
                bestScore = score
                bestMove = (i, j)
            undo_move(i, j)
    return bestMove

def max(a:int, b:int, depth:int):
    if depth == 0:
        return eval_func()

    bestScore = float('-inf')
    for i in range(8):
        for j in range(8):
            if board[i][j] != "-":
                continue
            make_move(i, j, "X")
            score = min(a, b, depth-1)
            bestScore = max(score, bestScore)
            if bestScore>= b:
                return bestScore
            a = max(a, bestScore)
            undo_move(i, j)
    return bestScore

def min(a:int, b:int, depth:int):
    if depth == 0:
        return eval_func()
    
    bestScore = float('inf')
    for i in range(8):
        for j in range(8):
            if board[i][j] != "-":
                continue
            make_move(i, j, "X")
            score = max(a, b, depth-1)
            bestScore = min(score, bestScore)
            if bestScore <= b:
                return bestScore
            b = min(b, bestScore)
            undo_move(i, j)
    return bestScore

def eval_func():
    pass

def check_win_condition():
    global gameIsDone
    pass

def human_move():
    while True: 
        humanMove = input("Choose your next move: ")
        if (len(humanMove) == 2 
            and ('a' <= humanMove[0].lower() <= 'h') 
            and ('1' <= humanMove[1] <= '8')):

            row = ord(humanMove[0].lower()) - ord('a')
            col = int(humanMove[1])

            if isMoveTaken(row, col):
                print("Move already taken!")
                continue

            make_move(row, col, "O")
            print_board()
            check_win_condition()
            break
        else: 
            print("Invalid Move")

def make_move(row:int, col:int, currPlayer):
    board[row][col] = currPlayer

def undo_move(row: int, col:int):
    make_move(row, col, "-")

def isMoveTaken(row:int, col:int) -> bool:
    return board[row][col] != "-"