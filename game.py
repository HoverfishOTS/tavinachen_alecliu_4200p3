import random
import time

BOARD_DEPTH = 8
bitboards = [0, 0]
end_time = None # value is updated 

# enums
AI = 0
HUMAN = 1

# score values
FOUR_IN_A_ROW = 9999999999
OPEN_THREE = 100000
POTENTIAL_FOUR = 15000
OPEN_TWO = 8000
POTENTIAL_THREE = 5000
CENTER_BONUS = 10
CENTER_RING_BONUS = 5
FEAR_FACTOR = 1.5

# Bitboard selection masks
FULL_BOARD = 0xFFFFFFFFFFFFFFFF # is a special number that sets all 64 bits into 1
COL_0_MASK = 0x0101010101010101 # is a special number that selects every 8 bits, selecting col 0
L_SHIFT_MASK = ~COL_0_MASK & FULL_BOARD # cuts off overflow in col 0 for left 1 bit shift
L_SHIFT2_MASK = L_SHIFT_MASK & (~COL_0_MASK << 1) # cuts off overflow in col 0, 1 for left 2 bit shift
L_SHIFT3_MASK = L_SHIFT2_MASK & (~COL_0_MASK << 2) # cuts off overflow in col 0, 1, 2 for left 3 bit shift
R_SHIFT_MASK = ~(COL_0_MASK << 7) & FULL_BOARD # cuts off overflow in col 7 for right 1 bit shift
CENTER2X2_MASK = ((1 << 27) | (1 << 28) | (1 << 35) | (1 << 36))
CENTER4X4RING_MASK = ((1 << 18) | (1 << 19) | (1 << 20) | (1 << 21) |
                      (1 << 26) | (1 << 29) |
                      (1 << 34) | (1 << 37) |
                      (1 << 42) | (1 << 43) | (1 << 44) | (1 << 45)) 

# this maps each index of the bitboard to a priority based on how far it is from the edges
INDEX_PRIORITY_MAP = [
    min(row, col, (BOARD_DEPTH - 1) - row, (BOARD_DEPTH - 1) - col) #checking each side
    for row in range(BOARD_DEPTH)
    for col in range(BOARD_DEPTH)
]

# expected maping of priority to index
# 0, 0, 0, 0, 0, 0, 0, 0  A  0  1  2  3  4  5  6  7
# 0, 1, 1, 1, 1, 1, 1, 0  B  8  9 10 11 12 13 14 15
# 0, 1, 2, 2, 2, 2, 1, 0  C 16 17 18 19 20 21 22 23
# 0, 1, 2, 3, 3, 2, 1, 0  D 24 25 26 27 28 29 30 31
# 0, 1, 2, 3, 3, 2, 1, 0  E 32 33 34 35 36 37 38 39
# 0, 1, 2, 2, 2, 2, 1, 0  F 40 41 42 43 44 45 46 47
# 0, 1, 1, 1, 1, 1, 1, 0  G 48 49 50 51 52 53 54 55
# 0, 0, 0, 0, 0, 0, 0, 0  H 56 57 58 59 60 61 62 63

def start_game(humanFirst:bool, thinkTimeInSeconds:int) -> None:
    global bitboards, FEAR_FACTOR
    bitboards = [0, 0]

    print("\nGame Started!\n")
    print_board()
    if humanFirst:
        FEAR_FACTOR = 2
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

    while time.time() <= end_time:
        score, move = alpha_beta_pruning(float('-inf'), float('inf'), depth)
        if time.time() < end_time and score > bestScore:
            bestScore = score
            bestMove = move
        depth +=1

    make_move(bestMove, AI)
    row = chr(bestMove//8 + ord('a')).upper()
    col = bestMove%8 + 1
    print(f"\nAI chose: {row}{col}")
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
        a = max(a, bestScore)
        if time.time() > end_time:
            break
    return bestScore, bestMove

def MAX(a:int, b:int, depth:int) -> int:
    isTerminal = isWin()
    if isTerminal != 0:
        return isTerminal
    
    # cut off test
    if depth == 0 or len(generate_successors()) == 0:
        return eval_func()

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
    isTerminal = isWin()
    if isTerminal != 0:
        return isTerminal
    
    # cut off test
    if depth == 0 or len(generate_successors()) == 0:
        return eval_func()

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
    isTerminal = isWin()

    if occupied != FULL_BOARD and isTerminal == 0:
        return False
    
    if isTerminal == FOUR_IN_A_ROW: print("\nYou Lose!") 
    elif isTerminal == -FOUR_IN_A_ROW: print("\nYou Win!")
    else: print("\nIt's A Tie!")
    
    print("Game Over!\n")
    return True

def eval_func():
    return score(AI) - score(HUMAN)*FEAR_FACTOR

def score(player):
    score = 0

    directions = {'horizontal': (1, True), 'vertical':(BOARD_DEPTH, False)}

    for direction, overflow in directions.values():
        score += get_score(player, direction, overflow) 
    
    #add bonus for central placements
    score += bin(bitboards[player] & CENTER2X2_MASK).count('1')*CENTER_BONUS
    score += bin(bitboards[player] & CENTER4X4RING_MASK).count('1')*CENTER_RING_BONUS

    return score

def get_score(player, direction, overflow:bool):
    occupied = bitboards[AI] | bitboards[HUMAN]
    unoccupied = ~occupied & FULL_BOARD
    p = bitboards[player]

    L1 = L2 = L3 = R1 = FULL_BOARD

    if overflow:
        L1 = L_SHIFT_MASK
        L2 = L_SHIFT2_MASK
        L3 = L_SHIFT3_MASK
        R1 = R_SHIFT_MASK

    # 4 in a row
    two_in_a_row = p & (p << 1*direction) & L1
    three_in_a_row = two_in_a_row & (p << 2*direction) & L2
    
    # potential 4s [- X X X], [X - X X], [X X - X], [X X X -], [- X X X -]
    # "move" unoccupied spaces to where our anchor is so we can combine this later
    p4_left = three_in_a_row & (unoccupied >> 1*direction) & R1     # [- X X X]
    p4_right = three_in_a_row & (unoccupied << 3*direction) & L3    # [X X X -]
    # we replace one of the pieces with an unoccupied space to create a pseudo 4 in a row
    p4_gap = (((p & (unoccupied << 1*direction) & (p << 2*direction) & (p << 3*direction)) & L3) | #[X - X X]
              ((p & (p << 1*direction) & (unoccupied << 2*direction) & (p << 3*direction)) & L3))  #[X X - X]
    open_3s = bin(p4_left & p4_right).count('1') # [- X X X -]

    potential_fours = bin(p4_left).count('1')+bin(p4_right).count('1') - 2*open_3s + bin(p4_gap).count('1')

    # potential 3s [- X X], [X - X], [X X -], [- X X -], #[X - - X]
    p3_left = two_in_a_row & (unoccupied >> 1*direction) & R1     # [- X X]
    p3_right = two_in_a_row & (unoccupied << 2*direction) & L2    # [X X -]
    p3_gap = ((p & (unoccupied << 1*direction) & (p << 2*direction) & L2) | #[X - X] 
               p & (unoccupied << 1*direction) & (unoccupied << 2*direction) & (p << 3*direction) & L3)   # [X - - X]
    open_2s = bin(p3_left & p3_right).count('1') # [- X X -]

    potential_threes = bin(p3_left).count('1')+bin(p3_right).count('1') - 2*open_2s + bin(p3_gap).count('1')

    return open_3s*OPEN_THREE + potential_fours*POTENTIAL_FOUR + open_2s*OPEN_TWO + potential_threes*POTENTIAL_THREE

def isWin():
    directions = {'horizontal': (1, True), 'vertical':(BOARD_DEPTH, False)}
    L3 = FULL_BOARD

    for i in range(2): 
        p = bitboards[i]
        for direction, overflow in directions.values():
            if overflow: L3 = L_SHIFT3_MASK

            # found 4 in a row
            if p & (p << 1*direction) & (p << 2*direction) & (p << 3*direction) & L3:
                return FOUR_IN_A_ROW if i == AI else -FOUR_IN_A_ROW
            
    return 0 # Tie

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

    if occupied == 0:
        successors = [27, 28, 35, 36]
        random.shuffle(successors)
        return successors
    
    # neighbors of all pieces
    neighbors = ((occupied << BOARD_DEPTH) | # UP
                 (occupied >> BOARD_DEPTH) | # DOWN
                 ((occupied << 1) & L_SHIFT_MASK)| #LEFT
                 ((occupied >> 1) & R_SHIFT_MASK)) & FULL_BOARD #RIGHT
    
    # all unoccupied neighbors
    neighbors &= ~occupied

    # all unoccupied squares that is not a neighbor
    others = FULL_BOARD & ~occupied & ~neighbors

    return get_selected_indexs(neighbors) + get_selected_indexs(others)

def get_selected_indexs(selection):
    indexes = []
    while selection:
        lsb = selection & -selection #2's complement isolates lsb

        index = lsb.bit_length() - 1
        indexes.append(index)

        selection ^= lsb # use XOR to cancel out the overlaping lsb

    #sorts the direct_successors by each square's priority 
    indexes.sort(key=lambda index: INDEX_PRIORITY_MAP[index], reverse=True)

    return indexes
