# This program contains all methods needed to play the game 4-in-a-line against an AI.
# The AI performs iterative deepening search with alpha beta pruning.

from random import shuffle
from time import time

# gameboard and timer
bitboards = [0, 0]
end_time = None
tt = {} # transposition table for move ordering
history_heuristic = [[0] * 64, [0] * 64]
killer_moves = [[-1, -1] for _ in range(64)]

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
R_SHIFT_MASK = ~(COL_0_MASK << 7) & FULL_BOARD # cuts off overflow in col 7 for right 1 bit shift
L_SHIFT3_MASK = (~COL_0_MASK & FULL_BOARD) & (~COL_0_MASK << 1) & (~COL_0_MASK << 2) # cuts off overflow in col 0, 1, 2 for left 3 bit shift
CENTER2X2_MASK = ((1 << 27) | (1 << 28) | (1 << 35) | (1 << 36))
CENTER4X4RING_MASK = ((1 << 18) | (1 << 19) | (1 << 20) | (1 << 21) |
                      (1 << 26) | (1 << 29) | (1 << 34) | (1 << 37) | 
                      (1 << 42) | (1 << 43) | (1 << 44) | (1 << 45)) 

# Precalculate the 80 winning lines (windows) of length 4
WINDOWS = []
for r in range(8):
    for c in range(5):
        w = 0
        for i in range(4): w |= (1 << (r * 8 + c + i))
        WINDOWS.append(w)
for c in range(8):
    for r in range(5):
        w = 0
        for i in range(4): w |= (1 << ((r + i) * 8 + c))
        WINDOWS.append(w)

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
    global bitboards, FEAR_FACTOR, tt, history_heuristic, killer_moves
    bitboards = [0, 0]
    tt = {} # clear transposition table for new game
    history_heuristic = [[0] * 64, [0] * 64]
    killer_moves = [[-1, -1] for _ in range(64)]
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
        move = alpha_beta_pruning(float('-inf'), float('inf'), depth, bestMove)
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
def alpha_beta_pruning(a:int, b:int, maxDepth:int, prevBestMove=None) -> int:
    bestScore = float('-inf')
    bestMove = None

    moves = generate_moves()
    if prevBestMove is not None and prevBestMove in moves:
        moves.remove(prevBestMove)
        moves.insert(0, prevBestMove)

    for move in moves:
        #perform move to calculate potential score
        make_move(move, AI)
        score = MIN(a, b, maxDepth-1, 1, False)
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
def MAX(a:int, b:int, depth:int, ply:int, is_null_move=False) -> int:
    original_a = a
    # terminal state
    isTerminal = isWin()
    if isTerminal != 0:
        return isTerminal - ply if isTerminal > 0 else isTerminal + ply
    
    state_key = (bitboards[0], bitboards[1], AI)
    tt_move = None
    if state_key in tt:
        tt_depth, tt_flag, tt_score, tt_move = tt[state_key]
        
        # Un-normalize mate scores from TT
        if tt_score > FOUR_IN_A_ROW - 1000:
            eval_score = tt_score - ply
        elif tt_score < -FOUR_IN_A_ROW + 1000:
            eval_score = tt_score + ply
        else:
            eval_score = tt_score

        if tt_depth >= depth:
            if tt_flag == 'EXACT':
                return eval_score
            elif tt_flag == 'LOWERBOUND':
                a = max(a, eval_score)
            elif tt_flag == 'UPPERBOUND':
                b = min(b, eval_score)
            if a >= b:
                return eval_score

    # Null Move Pruning
    R = 2
    if depth >= 3 and not is_null_move:
        score = MIN(a, b, depth - 1 - R, ply + 1, is_null_move=True)
        if score >= b:
            return score

    moves = generate_moves()
    
    # Sort by history heuristic
    moves.sort(key=lambda m: history_heuristic[AI][m], reverse=True)
    
    ordered_moves = []
    if tt_move is not None and tt_move in moves:
        ordered_moves.append(tt_move)
        moves.remove(tt_move)
        
    for k_move in killer_moves[depth]:
        if k_move != -1 and k_move in moves:
            ordered_moves.append(k_move)
            moves.remove(k_move)
            
    ordered_moves.extend(moves)
    moves = ordered_moves

    # cut off test
    if depth == 0 or len(moves) == 0:
        return eval_func()

    bestScore = float('-inf')
    bestMove = None
    for move in moves:
        # get score for this move
        make_move(move, AI)
        score = MIN(a, b, depth-1, ply+1, False)
        undo_move(move, AI)

        # update values
        if score > bestScore:
            bestScore = score
            bestMove = move
            if not is_null_move:
                history_heuristic[AI][move] += depth * depth
                
        a = max(a, bestScore)

        # pruning or timeout
        if bestScore >= b or time() > end_time:
            if time() <= end_time and not is_null_move:
                if killer_moves[depth][0] != move:
                    killer_moves[depth][1] = killer_moves[depth][0]
                    killer_moves[depth][0] = move
            break

    if time() <= end_time and bestMove is not None:
        if bestScore <= original_a:
            flag = 'UPPERBOUND'
        elif bestScore >= b:
            flag = 'LOWERBOUND'
        else:
            flag = 'EXACT'
            
        # Normalize mate scores before storing
        store_score = bestScore
        if store_score > FOUR_IN_A_ROW - 1000:
            store_score += ply
        elif store_score < -FOUR_IN_A_ROW + 1000:
            store_score -= ply

        tt[state_key] = (depth, flag, store_score, bestMove)

    return bestScore

# the human in the minimax algorithm
def MIN(a:int, b:int, depth:int, ply:int, is_null_move=False) -> int:
    original_b = b
    # terminal state
    isTerminal = isWin()
    if isTerminal != 0:
        return isTerminal - ply if isTerminal > 0 else isTerminal + ply
    
    state_key = (bitboards[0], bitboards[1], HUMAN)
    tt_move = None
    if state_key in tt:
        tt_depth, tt_flag, tt_score, tt_move = tt[state_key]
        
        # Un-normalize mate scores from TT
        if tt_score > FOUR_IN_A_ROW - 1000:
            eval_score = tt_score - ply
        elif tt_score < -FOUR_IN_A_ROW + 1000:
            eval_score = tt_score + ply
        else:
            eval_score = tt_score

        if tt_depth >= depth:
            if tt_flag == 'EXACT':
                return eval_score
            elif tt_flag == 'LOWERBOUND':
                a = max(a, eval_score)
            elif tt_flag == 'UPPERBOUND':
                b = min(b, eval_score)
            if a >= b:
                return eval_score

    # Null Move Pruning
    R = 2
    if depth >= 3 and not is_null_move:
        score = MAX(a, b, depth - 1 - R, ply + 1, is_null_move=True)
        if score <= a:
            return score

    moves = generate_moves()
    
    # Sort by history heuristic
    moves.sort(key=lambda m: history_heuristic[HUMAN][m], reverse=True)
    
    ordered_moves = []
    if tt_move is not None and tt_move in moves:
        ordered_moves.append(tt_move)
        moves.remove(tt_move)
        
    for k_move in killer_moves[depth]:
        if k_move != -1 and k_move in moves:
            ordered_moves.append(k_move)
            moves.remove(k_move)
            
    ordered_moves.extend(moves)
    moves = ordered_moves
    
    # cut off test
    if depth == 0 or len(moves) == 0:
        return eval_func()

    bestScore = float('inf')
    bestMove = None
    for move in moves:
        # get score for this move
        make_move(move, HUMAN)
        score = MAX(a, b, depth-1, ply+1, False)
        undo_move(move, HUMAN)

        # update values
        if score < bestScore:
            bestScore = score
            bestMove = move
            if not is_null_move:
                history_heuristic[HUMAN][move] += depth * depth
                
        b = min(b, bestScore)

        # pruning or timeout
        if bestScore <= a or time() > end_time:
            if time() <= end_time and not is_null_move:
                if killer_moves[depth][0] != move:
                    killer_moves[depth][1] = killer_moves[depth][0]
                    killer_moves[depth][0] = move
            break

    if time() <= end_time and bestMove is not None:
        if bestScore >= original_b:
            flag = 'LOWERBOUND'
        elif bestScore <= a:
            flag = 'UPPERBOUND'
        else:
            flag = 'EXACT'
            
        store_score = bestScore
        if store_score > FOUR_IN_A_ROW - 1000:
            store_score += ply
        elif store_score < -FOUR_IN_A_ROW + 1000:
            store_score -= ply

        tt[state_key] = (depth, flag, store_score, bestMove)

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
    opponent = 1 - player
    p_board = bitboards[player]
    o_board = bitboards[opponent]
    
    score_val = 0
    winning_squares = set()

    for w in WINDOWS:
        p_pieces = p_board & w
        o_pieces = o_board & w
        
        # If the window is unblocked by the opponent
        if o_pieces == 0 and p_pieces != 0:
            count = bin(p_pieces).count('1')
            if count == 3:
                score_val += POTENTIAL_FOUR
                winning_squares.add(w & ~p_pieces) # Track the exact empty square needed to win
            elif count == 2:
                score_val += POTENTIAL_THREE
            elif count == 1:
                score_val += 1000 # POTENTIAL_TWO
                
    # If there are multiple unique winning squares, it's an unstoppable fork (like an OPEN_THREE)
    if len(winning_squares) >= 2:
        score_val += 500000
    
    # add bonus for central placements
    score_val += bin(p_board & CENTER2X2_MASK).count('1')*CENTER_BONUS
    score_val += bin(p_board & CENTER4X4RING_MASK).count('1')*CENTER_RING_BONUS

    return score_val

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
