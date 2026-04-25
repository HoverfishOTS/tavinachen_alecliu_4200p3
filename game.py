# This program contains all methods needed to play the game 4-in-a-line against an AI.
# The AI performs iterative deepening search with alpha beta pruning.

from random import shuffle
from time import time

# gameboard and timer
bitboards = [0, 0]
end_time = None

# used for bit shifts to check pieces in a row for vertical and horizontal directions 
BOARD_DEPTH = 8
DIRECTIONS = {'horizontal': (1, True), 'vertical':(BOARD_DEPTH, False)}

# "enums"
AI = 0
HUMAN = 1

# score values; modify these for different AI behavior
FOUR_IN_A_ROW = 9999999999
OPEN_THREE = 100000
POTENTIAL_FOUR = 15000
OPEN_TWO = 8000
POTENTIAL_THREE = 5000
CENTER_BONUS = 10
CENTER_RING_BONUS = 5
FEAR_FACTOR = 1.5 # higher value = more defensive

# Bitboard selection masks
FULL_BOARD = 0xFFFFFFFFFFFFFFFF # sets all 64 bits into 1
COL_0_MASK = 0x0101010101010101 # selects every 8 bits, selecting col 0
L_SHIFT_MASK = ~COL_0_MASK & FULL_BOARD # cuts off overflow in col 0 for left 1 bit shift
L_SHIFT2_MASK = L_SHIFT_MASK & (~COL_0_MASK << 1) # cuts off overflow in col 0, 1 for left 2 bit shift
L_SHIFT3_MASK = L_SHIFT2_MASK & (~COL_0_MASK << 2) # cuts off overflow in col 0, 1, 2 for left 3 bit shift
R_SHIFT_MASK = ~(COL_0_MASK << 7) & FULL_BOARD # cuts off overflow in col 7 for right 1 bit shift
CENTER2X2_MASK = ((1 << 27) | (1 << 28) | (1 << 35) | (1 << 36))
CENTER4X4RING_MASK = ((1 << 18) | (1 << 19) | (1 << 20) | (1 << 21) |
                      (1 << 26) | (1 << 29) | (1 << 34) | (1 << 37) | 
                      (1 << 42) | (1 << 43) | (1 << 44) | (1 << 45)) 

# maps each index of the bitboard to a priority based on how far it is from the edges
INDEX_PRIORITY_MAP = [
    min(row, col, (BOARD_DEPTH - 1) - row, (BOARD_DEPTH - 1) - col) #checking each side
    for row in range(BOARD_DEPTH)
    for col in range(BOARD_DEPTH)

    # expected maping of priority to index
    # 0, 0, 0, 0, 0, 0, 0, 0  A  0  1  2  3  4  5  6  7
    # 0, 1, 1, 1, 1, 1, 1, 0  B  8  9 10 11 12 13 14 15
    # 0, 1, 2, 2, 2, 2, 1, 0  C 16 17 18 19 20 21 22 23
    # 0, 1, 2, 3, 3, 2, 1, 0  D 24 25 26 27 28 29 30 31
    # 0, 1, 2, 3, 3, 2, 1, 0  E 32 33 34 35 36 37 38 39
    # 0, 1, 2, 2, 2, 2, 1, 0  F 40 41 42 43 44 45 46 47
    # 0, 1, 1, 1, 1, 1, 1, 0  G 48 49 50 51 52 53 54 55
    # 0, 0, 0, 0, 0, 0, 0, 0  H 56 57 58 59 60 61 62 63
]

# this methods initializes the game and prompts the user until either the AI or player wins.
def start_game(humanFirst:bool, thinkTimeInSeconds:int) -> None:
    # game set up
    global bitboards, FEAR_FACTOR
    bitboards = [0, 0]
    print("\nGame Started!\n")
    print_board()

    if humanFirst:
        FEAR_FACTOR = 2 # AI plays more defensively if the human plays first
        human_move()
    
    # continue until game is over
    while not isGameOver():
        ai_move(thinkTimeInSeconds)
        if isGameOver(): break
        human_move()

# this method prints the game board
def print_board() -> None:
    print("\n  1 2 3 4 5 6 7 8", end="")
    row = 0
    for i in range(64):
        if i % 8 == 0:
            # prints the row header
            print(f"\n{chr(ord('A')+row)}", end="")
            row+=1
        if (bitboards[AI] >> i) & 1:
            print(f" X", end="")
        elif (bitboards[HUMAN] >> i) & 1:
            print(f" O" , end="")
        else:
            print(f" -", end="")
    print()

# this method prompts the AI to think for x seconds, then makes the move
def ai_move(thinkTimeInSeconds: int) -> None:
    global end_time
    print("\nAI thinking...")
    end_time = time() + thinkTimeInSeconds

    depth = 1
    bestMove = None

    # ai performs alpha beta pruning with IDFS until time is up
    while depth < 64 and time() <= end_time:
        move = alpha_beta_pruning(float('-inf'), float('inf'), depth)
        depth +=1
        # only update bestScore if AI is done searching at x depth
        if time() < end_time:
            bestMove = move

    # make the move and print the board
    make_move(bestMove, AI)
    row = chr(bestMove//8 + ord('a')).upper()
    col = bestMove%8 + 1
    print(f"\nAI chose: {row}{col}")
    print_board()

# performs alpha beta pruning and returns the best calculated move
def alpha_beta_pruning(a:int, b:int, maxDepth:int) -> int:
    bestScore = float('-inf')
    bestMove = None

    for move in generate_moves():
        #perform move to calculate potential score
        make_move(move, AI)
        score = MIN(a, b, maxDepth-1)
        undo_move(move, AI)

        # update if score is better than a previous move
        if score > bestScore:
            bestScore = score
            bestMove = move
        a = max(a, bestScore)

        # timeout
        if time() > end_time:
            break

    return bestMove

# the AI in the minimax algorithm
def MAX(a:int, b:int, depth:int) -> int:

    # terminal state
    isTerminal = isWin()
    if isTerminal != 0:
        return isTerminal
    
    moves = generate_moves()

    # cut off test
    if depth == 0 or len(moves) == 0:
        return eval_func()

    bestScore = float('-inf')
    for move in moves:
        # get score for this move
        make_move(move, AI)
        score = MIN(a, b, depth-1)
        undo_move(move, AI)

        # update values
        bestScore = max(score, bestScore)
        a = max(a, bestScore)

        # pruning or timeout
        if bestScore>= b or time() > end_time:
            break

    return bestScore

# the human in the minimax algorithm
def MIN(a:int, b:int, depth:int) -> int:

    # terminal state
    isTerminal = isWin()
    if isTerminal != 0:
        return isTerminal
    
    moves = generate_moves()
    
    # cut off test
    if depth == 0 or len(moves) == 0:
        return eval_func()

    bestScore = float('inf')
    for move in moves:
        # get score for this move
        make_move(move, HUMAN)
        score = MAX(a, b, depth-1)
        undo_move(move, HUMAN)

        # update values
        bestScore = min(score, bestScore)        
        b = min(b, bestScore)

        #purning or timeout
        if bestScore<= a or time() > end_time:
            break

    return bestScore

# this method checks if AI or HUMAN has 4 in a row and prints gameover messages
def isGameOver() -> bool:
    occupied = bitboards[AI] | bitboards[HUMAN]
    isTerminal = isWin()

    if occupied != FULL_BOARD and isTerminal == 0:
        return False
    
    # Game is over
    if isTerminal == FOUR_IN_A_ROW: 
        print("\nYou Lose!") 
    elif isTerminal == -FOUR_IN_A_ROW: 
        print("\nYou Win!")
    else: 
        print("\nIt's A Tie!")
    
    print("Game Over!\n")
    return True

# this function evalues the score of the current board
def eval_func() -> int:
    return int(score(AI) - score(HUMAN)*FEAR_FACTOR)

# this function evalues and returns the score of `player`
def score(player:int) -> int:
    score = 0

    # tally up scores horizontally and vertically
    for direction, overflow in DIRECTIONS.values():
        score += get_score(player, direction, overflow) 
    
    #add bonus for central placements
    score += bin(bitboards[player] & CENTER2X2_MASK).count('1')*CENTER_BONUS
    score += bin(bitboards[player] & CENTER4X4RING_MASK).count('1')*CENTER_RING_BONUS

    return score

# this function returns the score of `player` in one direction
# horizontal directions have overflow
def get_score(player:int, direction:int, overflow:bool) -> int:
    # calculate initialize values
    unoccupied = ~(bitboards[AI] | bitboards[HUMAN]) & FULL_BOARD
    p = bitboards[player]
    L1 = L_SHIFT_MASK if overflow else FULL_BOARD
    L2 = L_SHIFT2_MASK if overflow else FULL_BOARD
    L3 = L_SHIFT3_MASK if overflow else FULL_BOARD
    R1 = R_SHIFT_MASK if overflow else FULL_BOARD
    # anchor bit is 1st bit of where the pattern appears
    two_in_a_row = p & (p << 1*direction) & L1 
    three_in_a_row = two_in_a_row & (p << 2*direction) & L2
    
    # potential 4s
    # unoccupied is shifted in the opposite direction because 
    # it is shifting to where the anchor is instead of shifting the anchor to the unoccupied spot
    p4_left = three_in_a_row & (unoccupied >> 1*direction) & R1     # [- X X X]
    p4_right = three_in_a_row & (unoccupied << 3*direction) & L3    # [X X X -]
    p4_gap = (((p & (unoccupied << 1*direction) & (p << 2*direction) & (p << 3*direction)) & L3) | #[X - X X]
              ((p & (p << 1*direction) & (unoccupied << 2*direction) & (p << 3*direction)) & L3))  #[X X - X]
    
    # count up open 3s and potential fours
    # (converts it to binary and counts the 1s to get total #)
    open_3s = bin(p4_left & p4_right).count('1') # [- X X X -]
    potential_fours = bin(p4_left).count('1')+bin(p4_right).count('1') - 2*open_3s + bin(p4_gap).count('1')

    # potential 3s
    p3_left = two_in_a_row & (unoccupied >> 1*direction) & R1     # [- X X]
    p3_right = two_in_a_row & (unoccupied << 2*direction) & L2    # [X X -]
    p3_gap = ((p & (unoccupied << 1*direction) & (p << 2*direction) & L2) | #[X - X] 
               p & (unoccupied << 1*direction) & (unoccupied << 2*direction) & (p << 3*direction) & L3)   # [X - - X]
    open_2s = bin(p3_left & p3_right).count('1') # [- X X -]

    # count up open 2s and potential threes
    potential_threes = bin(p3_left).count('1')+bin(p3_right).count('1') - 2*open_2s + bin(p3_gap).count('1')

    # multiply counts by the multipliers
    return open_3s*OPEN_THREE + potential_fours*POTENTIAL_FOUR + open_2s*OPEN_TWO + potential_threes*POTENTIAL_THREE

# this function detects if there is a 4-in-a-row
def isWin() -> int:
    # check each player
    for i in range(2): 
        p = bitboards[i]

        for direction, overflow in DIRECTIONS.values():
            mask = L_SHIFT3_MASK if overflow else FULL_BOARD
            # found 4 in a row
            if p & (p << 1*direction) & (p << 2*direction) & (p << 3*direction) & mask:
                return FOUR_IN_A_ROW if i == AI else -FOUR_IN_A_ROW
            
    return 0 # Tie or no win yet

# this function prompts the user for their next move 
def human_move() -> None:
    while True: 
        humanMove = input("\nChoose your next move: ")

        # input validation
        if (len(humanMove) == 2 
            and ('a' <= humanMove[0].lower() <= 'h') 
            and ('1' <= humanMove[1] <= '8')):

            # convert input to index
            row = ord(humanMove[0].lower()) - ord('a') # 0 indexed row
            col = int(humanMove[1])-1 # 0 indexed column
            index = col + row*BOARD_DEPTH

            # check if taken
            if isMoveTaken(index): 
                print("Move already taken!")
                continue
            
            # make the move
            make_move(index, HUMAN)
            print_board()
            break
        else: 
            print("Invalid Move")

# the following functions perform actions on the gameboard
def make_move(index:int, player:int) -> None:
    # sets the bit
    bitboards[player] |= (1 << index) # bit shifts a 1 to the correct index, then OR with bitboard to add it 

def undo_move(index:int, player:int) -> None:
    # clears the bit
    bitboards[player] ^= (1 << index) # bit shifts a 1 to the correct index, then XOR to remove bit 

# checks if the move at 'index' is taken
def isMoveTaken(index:int) -> bool:
    occupied = bitboards[AI] | bitboards[HUMAN]
    return (occupied >> index) & 1

# this function generates all moves and orders it based on priority
def generate_moves():
    occupied = bitboards[AI] | bitboards[HUMAN]

    # if board is empty
    if occupied == 0:
        successors = [27, 28, 35, 36]
        shuffle(successors)
        return successors
    
    # neighbors of all pieces on the board
    neighbors = ((occupied << BOARD_DEPTH) | # UP
                 (occupied >> BOARD_DEPTH) | # DOWN
                 ((occupied << 1) & L_SHIFT_MASK)| #LEFT
                 ((occupied >> 1) & R_SHIFT_MASK)) & FULL_BOARD #RIGHT
    
    # all unoccupied neighbors
    neighbors &= ~occupied

    # all unoccupied squares that is not a neighbor
    others = FULL_BOARD & ~occupied & ~neighbors

    return get_selected_indexs(neighbors) + get_selected_indexs(others)

# helper function to get the index of all moves in a given selection
def get_selected_indexs(selection:int):
    indexes = []
    while selection:
        lsb = selection & -selection #2's complement isolates lsb

        # calculate index
        index = lsb.bit_length() - 1
        indexes.append(index)

        selection ^= lsb # use XOR to cancel out the overlaping lsb

    #sorts the indexes by each square's priority 
    indexes.sort(key=lambda index: INDEX_PRIORITY_MAP[index], reverse=True)

    return indexes
