import random
import time

gameover = False
end_time = None

bitboards = {}
board_depth = 8

# 0x0101010101010101 is a special number that selects every 8 bits, making a column selection
col_masks = [0x0101010101010101 << i for i in range(8)] 

# 0xFF is a special number that selects the bits 0-7
row_masks = [0xFF << (i * board_depth) for i in range(8)]

# A  0  1  2  3  4  5  6  7
# B  8  9 10 11 12 13 14 15
# C 16 17 18 19 20 21 22 23
# D 24 25 26 27 28 29 30 31
# E 32 33 34 35 36 37 38 39
# F 40 41 42 43 44 45 46 47
# G 48 49 50 51 52 53 54 55
# H 56 57 58 59 60 61 62 63

def start_game(humanFirst:bool, thinkTimeInSeconds:int) -> None:
    global bitboards
    bitboards["ai"] = bitboards["human"] = 0
    print("\nGame Started!\n")
    print_board()
    if humanFirst:
        human_move()
    
    while not isGameOver():
        ai_move(thinkTimeInSeconds)
        if isGameOver(): break
        human_move()
    
    print("Game Over!\n")

def print_board() -> None:
    print("  1 2 3 4 5 6 7 8")
    for row in range(8):
        r = []
        for col in range(8):
            if (bitboards['ai'] >> col + row*board_depth) & 1:
                r.append("X")
            elif (bitboards['human'] >> col + row*board_depth) & 1:
                r.append("O")
            else:
                r.append("-")

        print(chr(ord('A')+row), " ".join(r))

def ai_move(thinkTimeInSeconds: int):
    global end_time
    print("\nAI thinking...")

    depth = 1
    bestMove = None
    bestScore = float('-inf')

    end_time = time.time() + thinkTimeInSeconds

    while time.time() < end_time:
        score, move = alpha_beta_pruning(float('-inf'), float('inf'), depth)
        if score > bestScore:
            bestScore = score
            bestMove = move
        depth +=1
    make_move(bestMove[0], bestMove[1], "ai")
    col = chr(bestMove[0] + ord('a')).upper()
    row = bestMove[1] + 1
    print(f"\nAI chose: {col}{row}")
    # print("Start Time: ", start_time)
    # print("End Time: ", time.time())
    print_board()

def alpha_beta_pruning(a:int, b:int, maxDepth:int) -> tuple[int, int]:
    bestScore = float('-inf')
    bestMove = None

    for x, y in generate_successors():
        make_move(x, y, "ai")
        score = MIN(a, b, maxDepth-1)
        undo_move(x, y, "ai")
        if score > bestScore:
            bestScore = score
            bestMove = (x, y)
        if time.time() > end_time:
            break
    return bestScore, bestMove

def MAX(a:int, b:int, depth:int) -> int:
    eval = eval_func()
    if eval != 0:
        return eval
    
    if depth == 0 or len(generate_successors()) == 0:
        return eval

    bestScore = float('-inf')
    
    for x, y in generate_successors():
        make_move(x, y, "ai")
        score = MIN(a, b, depth-1)
        bestScore = max(score, bestScore)
        a = max(a, bestScore)
        undo_move(x, y, "ai")
        if bestScore>= b or time.time() > end_time:
            return bestScore
    return bestScore

def MIN(a:int, b:int, depth:int) -> int:
    eval = eval_func()
    if eval != 0:
        return eval
    
    if depth == 0 or len(generate_successors()) == 0:
        return eval_func()

    bestScore = float('inf')

    for x, y in generate_successors():
        make_move(x, y, "human")
        score = MAX(a, b, depth-1)
        bestScore = min(score, bestScore)        
        b = min(b, bestScore)
        undo_move(x, y ,"human")
        if bestScore<= a or time.time() > end_time:
            return bestScore
    return bestScore

def eval_func():
    if isWin("ai"):
        return 5000
    if isWin("human"):
        return -5000
    # 1 for draw
    # 
    return 0

def isWin(currPlayer:str):    
    for i in range(8):
        # checking each row for a connect 4
        row = bitboards[currPlayer] & row_masks[i]
        if row & row >> 1 & row >> 2 & row >> 3 != 0: return True 

        # checking each col for a connect 4
        col = bitboards[currPlayer] & col_masks[i]
        if col & col >> 1*board_depth & col >> 2*board_depth & col >> 3*board_depth != 0: return True

    return False

def isGameOver():
    if isWin('ai'):
        print("\nYou Lose!")
        return True
    if isWin('human'):
        print("\nYou Win!")
        return True
    
    return False


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

            make_move(row, col, "human")
            print_board()
            break
        else: 
            print("Invalid Move")

def make_move(row:int, col:int, currPlayer):
    # sets the bit
    bitboards[currPlayer] |= (1 << col + row*board_depth)

def undo_move(row: int, col:int, currPlayer):
    # clears the bit
    bitboards[currPlayer] &= ~(1 << col + row*board_depth)

def isMoveTaken(row:int, col:int) -> bool:
    combined_board = bitboards['ai'] | bitboards['human']
    return (combined_board >> col + row*board_depth) & 1

def generate_successors():
    # maybe get high priority successors first, aka any adjacent squares
    # the more pieces they are touching the higher priority they are
    # then randomize the rest
    successors = []
    for i in range(8):
        for j in range(8):
            if not isMoveTaken(i,j):
                successors.append((i, j))
    random.shuffle(successors)
    return successors

# note to self
# continue making eval func
# make successor function better; prioritize all the rows or cols with more pieces placed