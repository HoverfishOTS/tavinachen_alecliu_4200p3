import random
import time
from collections import deque

BOARD_DEPTH = 8

# an empty board is all the bits set to 0
EMPTY_BOARD = 0
# 0xFFFFFFFFFFFFFFFF is a special number that sets all 64 bits into 1
FULL_BOARD = 0xFFFFFFFFFFFFFFFF
# 0x0101010101010101 is a special number that selects every 8 bits, making a column selection starting from 0
COL_0_MASK = 0x0101010101010101
# 0x00000000000000FF is a special number that selects bits 0-7, making a row
ROW_0_MASK = 0x00000000000000FF

# shifting it 7 times yields the last column
COL_7_MASK = COL_0_MASK << 7

CENTER2X2_MASK = (( (COL_0_MASK << 4) | 
                   (COL_0_MASK << 5)) & 
                   ((ROW_0_MASK << 4*BOARD_DEPTH) |
                    (ROW_0_MASK << 5*BOARD_DEPTH))) 

CENTER4X4RING_MASK = (((COL_0_MASK << 2) | 
                   (COL_0_MASK << 3)) & 
                   ((ROW_0_MASK << 2*BOARD_DEPTH) |
                    (ROW_0_MASK << 3*BOARD_DEPTH)))

# this maps each index of the bitboard, giving priority to center moves
INDEX_PRIORITY_MAP = [
    0, 0, 0, 0, 0, 0, 0, 0, # A  0  1  2  3  4  5  6  7
    0, 1, 1, 1, 1, 1, 1, 0, # B  8  9 10 11 12 13 14 15
    0, 1, 2, 2, 2, 2, 1, 0, # C 16 17 18 19 20 21 22 23
    0, 1, 2, 3, 3, 2, 1, 0, # D 24 25 26 27 28 29 30 31
    0, 1, 2, 3, 3, 2, 1, 0, # E 32 33 34 35 36 37 38 39
    0, 1, 2, 2, 2, 2, 1, 0, # F 40 41 42 43 44 45 46 47
    0, 1, 1, 1, 1, 1, 1, 0, # G 48 49 50 51 52 53 54 55
    0, 0, 0, 0, 0, 0, 0, 0, # H 56 57 58 59 60 61 62 63
]

FOUR_IN_A_ROW = 9999999999
OPEN_THREE = 50000
POTENTIAL_FOUR = 10000
OPEN_TWO = 1000
POTENTIAL_THREE = 500
CENTER_BONUS = 20
CENTER_RING_BONUS = 10

AI = 0
HUMAN = 1

bitboards = [0, 0]
end_time = None

def start_game(humanFirst:bool, thinkTimeInSeconds:int) -> None:
    global bitboards
    bitboards = [0, 0]

    print("\nGame Started!\n")
    print_board()
    if humanFirst:
        human_move()
    
    while not isGameOver():
        ai_move(thinkTimeInSeconds)
        if isGameOver(): break
        human_move()

def print_board() -> None:
    print("\n  1 2 3 4 5 6 7 8", end="")
    row = 0
    for i in range(64):
        if i % 8 == 0:
            print(f"\n{chr(ord('A')+row)}", end="")
            row+=1
        if (bitboards[AI] >> i) & 1:
            print(f" X", end="")
        elif (bitboards[HUMAN] >> i) & 1:
            print(f" O" , end="")
        else:
            print(f" -", end="")
    print()

def ai_move(thinkTimeInSeconds: int):
    global end_time
    depth = 1
    bestMove = None
    bestScore = float('-inf')

    print("\nAI thinking...")
    end_time = time.time() + thinkTimeInSeconds

    while time.time() < end_time:
        score, move = alpha_beta_pruning(float('-inf'), float('inf'), depth)
        if score > bestScore:
            bestScore = score
            bestMove = move
        depth +=1
    make_move(bestMove, AI)
    col = chr(bestMove%8 + ord('a')).upper()
    row = bestMove//8 + 1
    print(f"\nAI chose: {col}{row}")
    print_board()

def alpha_beta_pruning(a:int, b:int, maxDepth:int) -> tuple[int, int]:
    bestScore = float('-inf')
    bestMove = None

    for i in generate_successors():
        make_move(i, AI)
        score = MIN(a, b, maxDepth-1)
        undo_move(i, AI)
        if score > bestScore:
            bestScore = score
            bestMove = i
        if time.time() > end_time:
            break
    return bestScore, bestMove

def MAX(a:int, b:int, depth:int) -> int:
    curr_score = eval_func()

    # terminal state
    if curr_score == FOUR_IN_A_ROW:
        return curr_score
    
    # cut off test
    if depth == 0 or len(generate_successors()) == 0:
        return curr_score

    bestScore = float('-inf')
    for move in generate_successors():
        make_move(move, AI)
        score = MIN(a, b, depth-1)
        bestScore = max(score, bestScore)
        a = max(a, bestScore)
        undo_move(move, AI)
        if bestScore>= b or time.time() > end_time:
            return bestScore
    return bestScore

def MIN(a:int, b:int, depth:int) -> int:

    curr_score = eval_func()

    # terminal state
    if curr_score == FOUR_IN_A_ROW:
        return curr_score

    # cut off test
    if depth == 0 or len(generate_successors()) == 0:
        return curr_score

    bestScore = float('inf')
    for move in generate_successors():
        make_move(move, HUMAN)
        score = MAX(a, b, depth-1)
        bestScore = min(score, bestScore)        
        b = min(b, bestScore)
        undo_move(move, HUMAN)
        if bestScore<= a or time.time() > end_time:
            return bestScore
    return bestScore

def isGameOver():
    occupied = bitboards[AI] | bitboards[HUMAN]
    if occupied == FULL_BOARD:
        print("\nIt's A Tie!\n")
        print("Game Over!\n")
        return True
    if score(AI) == FOUR_IN_A_ROW:
        print("\nYou Lose!\n")
        print("Game Over!\n")
        return True
    if score(HUMAN) == FOUR_IN_A_ROW:
        print("\nYou Win!\n")
        print("Game Over!\n")
        return True
    return False

def eval_func():
    ai_score = score(AI)
    if ai_score == FOUR_IN_A_ROW: return FOUR_IN_A_ROW
    human_score = score(HUMAN)
    if human_score == FOUR_IN_A_ROW: return FOUR_IN_A_ROW

    return ai_score - human_score

def score(player):
    score = 0
    directions = {'horizontal':(1, ~COL_0_MASK), 'vertical':(BOARD_DEPTH, FULL_BOARD)}
    unoccupied = ~(bitboards[AI] | bitboards[HUMAN]) & FULL_BOARD

    for shift_amount, mask in directions.values():

        #detect consecutive pieces
        two_in_a_row = bitboards[player] & (bitboards[player] >> shift_amount) & mask
        three_in_a_row = two_in_a_row & (bitboards[player] >> shift_amount*2) & mask
        if three_in_a_row & (bitboards[player] >> shift_amount*3) & mask:
            return FOUR_IN_A_ROW

        #detect potential 4s [- X X X], [X - X X], [X X - X], [X X X -]
        potential_four_left = (three_in_a_row << shift_amount) & unoccupied & mask
        potential_four_right = (three_in_a_row << shift_amount*3) & unoccupied
        if shift_amount == 1:
            potential_four_right & (COL_7_MASK  | COL_7_MASK >> 1 | COL_7_MASK >> 2)
        #detect open three [- X X X -]
        open_three = potential_four_right & potential_four_left

        # tally up 3 in a row scores
        score += bin(open_three).count('1') * OPEN_THREE
        score += (bin(potential_four_left).count('1') + 
                  bin(potential_four_right).count('1')) * POTENTIAL_FOUR

        #detect potential 3s [- X X], [X - X], [X X -]
        potential_three_left = (two_in_a_row << shift_amount) & unoccupied & mask
        potential_three_right = (two_in_a_row << shift_amount*2) & unoccupied
        if shift_amount == 1:
            potential_three_right & (COL_7_MASK  | COL_7_MASK >> 1)
        #detect open two [- X X -]
        open_two = potential_three_left & potential_three_right

        # tally up 2 in a row scores
        score += bin(open_two).count('1') * OPEN_TWO
        score += (bin(potential_three_left).count('1') + 
                  bin(potential_three_right).count('1')) * POTENTIAL_THREE
    
    #add bonus for central placements
    center = bitboards[player] & CENTER2X2_MASK
    center_ring = bitboards[player] & CENTER4X4RING_MASK

    score += bin(center).count('1')*CENTER_BONUS
    score += bin(center_ring).count('1')*CENTER_RING_BONUS

    return score

def human_move():
    while True: 
        humanMove = input("\nChoose your next move: ")
        if (len(humanMove) == 2 
            and ('a' <= humanMove[0].lower() <= 'h') 
            and ('1' <= humanMove[1] <= '8')):

            row = ord(humanMove[0].lower()) - ord('a') # 0 indexed row
            col = int(humanMove[1])-1 # 0 indexed column
            index = col + row*BOARD_DEPTH
            if isMoveTaken(index):
                print("Move already taken!")
                continue

            make_move(index, HUMAN)
            print_board()
            break
        else: 
            print("Invalid Move")

def make_move(index:int, player):
    # sets the bit
    bitboards[player] |= (1 << index) # bit shifts a 1 to the correct index, then OR with bitboard to add it 

def undo_move(index:int, player):
    # clears the bit
    bitboards[player] ^= (1 << index) # bit shifts a 1 to the correct index, then XOR to remove bit 

def isMoveTaken(index:int) -> bool:
    occupied = bitboards[AI] | bitboards[HUMAN]
    return (occupied >> index) & 1

def generate_successors():
    occupied = bitboards[AI] | bitboards[HUMAN]
    empty_squares = FULL_BOARD & ~occupied #all empty squares are marked with a 1 bit

    successors = []

    while empty_squares:
        lsb = empty_squares & -empty_squares #2's complement isolates lsb

        index = lsb.bit_length() - 1
        successors.append(index)

        empty_squares ^= lsb # use XOR to cancel out the overlaping lsb

    #sorts the successors by each square's priority 
    successors.sort(key=lambda index: INDEX_PRIORITY_MAP[index], reverse=True)

    return successors