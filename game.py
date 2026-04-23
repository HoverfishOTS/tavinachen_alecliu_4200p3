import random
import time

gameIsDone = False
board = [["-" for _ in range(8)] for _ in range(8)]
maxDepth = 64
end_time = None

def start_game(humanFirst:bool, thinkTimeInSeconds:int) -> None:
    global currPlayer
    print("\nGame Started!\n")
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
    global end_time
    print("\nAI thinking...")

    depth = 1
    bestMove = None
    bestScore = float('-inf')

    end_time = time.time() + thinkTimeInSeconds

    while depth <= maxDepth and time.time() < end_time:
        score, move = alpha_beta_pruning(float('-inf'), float('inf'), depth)
        if score > bestScore:
            bestScore = score
            bestMove = move
        depth +=1
    make_move(bestMove[0], bestMove[1], "X")
    col = chr(bestMove[0] + ord('a')).upper()
    row = bestMove[1] + 1
    print(f"\nAI chose: {col}{row}")
    # print("Start Time: ", start_time)
    # print("End Time: ", time.time())
    print_board()
    check_win_condition()

def alpha_beta_pruning(a:int, b:int, maxDepth:int) -> tuple[int, int]:
    bestScore = float('-inf')
    bestMove = None

    for x, y in generate_successors():
        make_move(x, y, "X")
        score = MIN(a, b, maxDepth-1)
        undo_move(x, y)
        if score > bestScore:
            bestScore = score
            bestMove = (x, y)
        if time.time() > end_time:
            break
    return bestScore, bestMove

def MAX(a:int, b:int, depth:int) -> int:
    if depth == 0 or len(generate_successors()) == 0:
        return eval_func()

    bestScore = float('-inf')
    
    for x, y in generate_successors():
        make_move(x, y, "X")
        score = MIN(a, b, depth-1)
        bestScore = max(score, bestScore)
        a = max(a, bestScore)
        undo_move(x, y)
        if bestScore>= b or time.time() > end_time:
            return bestScore
    return bestScore

def MIN(a:int, b:int, depth:int) -> int:
    if depth == 0 or len(generate_successors()) == 0:
        return eval_func()

    bestScore = float('inf')

    for x, y in generate_successors():
        make_move(x, y, "O")
        score = MAX(a, b, depth-1)
        bestScore = min(score, bestScore)        
        b = min(b, bestScore)
        undo_move(x, y)
        if bestScore<= a or time.time() > end_time:
            return bestScore
    return bestScore

def eval_func():
    # -5000 lose
    # 5000 win
    # 1 for draw
    # look in windows of 4 for each row and col
    # 
    return 0
    pass

def check_win_condition():
    global gameIsDone
    pass

def human_move():
    while True: 
        humanMove = input("\nChoose your next move: ")
        if (len(humanMove) == 2 
            and ('a' <= humanMove[0].lower() <= 'h') 
            and ('1' <= humanMove[1] <= '8')):

            row = ord(humanMove[0].lower()) - ord('a')
            col = int(humanMove[1])-1

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
    board[row][col] = "-"

def isMoveTaken(row:int, col:int) -> bool:
    return board[row][col] != "-"

def generate_successors():
    # maybe get high priority successors first, aka any adjacent squares
    # the more pieces they are touching the higher priority they are
    # then randomize the rest
    successors = []
    for i in range(8):
        for j in range(8):
            if board[i][j] == "-":
                successors.append((i, j))
    random.shuffle(successors)
    return successors

# note to self
# make a proper eval function
# check winning condition stuff check_win_condition()
# add check_game_over() func