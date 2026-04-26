import sys
import time
import random
import game
import game_old

def get_new_move(bitboards, think_time):
    game.bitboards = list(bitboards)
    game.end_time = time.time() + think_time
    depth = 1
    bestMove = None
    
    while depth < 64 and time.time() <= game.end_time:
        move = game.alpha_beta_pruning(float('-inf'), float('inf'), depth, bestMove)
        if time.time() < game.end_time:
            bestMove = move
        depth += 1
            
    return bestMove

def get_old_move(bitboards, think_time):
    game_old.bitboards = list(bitboards)
    game_old.end_time = time.time() + think_time
    depth = 1
    bestMove = None
    
    while depth < 64 and time.time() <= game_old.end_time:
        move = game_old.alpha_beta_pruning(float('-inf'), float('inf'), depth)
        if time.time() < game_old.end_time:
            bestMove = move
        depth += 1
            
    return bestMove

def print_board(bitboards):
    print("\n  1 2 3 4 5 6 7 8", end="")
    row = 0
    for i in range(64):
        if i % 8 == 0:
            print(f"\n{chr(ord('A')+row)}", end="")
            row+=1
        if (bitboards[0] >> i) & 1:
            print(f" X", end="")
        elif (bitboards[1] >> i) & 1:
            print(f" O" , end="")
        else:
            print(f" -", end="")
    print()

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['new_first', 'old_first']:
        print("Usage: python arena.py [new_first|old_first]")
        return
        
    mode = sys.argv[1]
    think_time = 5.0
    bitboards = [0, 0] # P1 is X (bitboards[0]), P2 is O (bitboards[1])
    
    # Initialize separate Transposition Tables for both AIs
    game.tt = {}
    game_old.tt = {}
    
    if mode == 'new_first':
        p1_name = "New AI"
        p2_name = "Old AI"
    else:
        p1_name = "Old AI"
        p2_name = "New AI"
        
    print(f"Match: {p1_name} (X) vs {p2_name} (O)")
    print(f"Think time: {think_time} seconds per move")
    print_board(bitboards)
    
    turn = 0
    while True:
        # Check win using the new game module's logic
        game.bitboards = bitboards
        is_terminal = game.isWin()
        occupied = bitboards[0] | bitboards[1]
        
        if is_terminal == game.FOUR_IN_A_ROW:
            print(f"\n{p1_name} (X) Wins!")
            break
        elif is_terminal == -game.FOUR_IN_A_ROW:
            print(f"\n{p2_name} (O) Wins!")
            break
        elif occupied == game.FULL_BOARD:
            print("\nTie!")
            break
            
        current_player = turn % 2
        
        if (mode == 'new_first' and current_player == 0) or (mode == 'old_first' and current_player == 1):
            print(f"\nNew AI thinking...")
            # If New AI is player 2, it evaluates from the swapped perspective
            if current_player == 1:
                move = get_new_move([bitboards[1], bitboards[0]], think_time)
            else:
                move = get_new_move(bitboards, think_time)
            player_label = "New AI"
        else:
            print(f"\nOld AI thinking...")
            # If Old AI is player 2, it evaluates from the swapped perspective
            if current_player == 1:
                move = get_old_move([bitboards[1], bitboards[0]], think_time)
            else:
                move = get_old_move(bitboards, think_time)
            player_label = "Old AI"
            
        # Fallback if no move is somehow returned
        if move is None:
            move = random.choice([i for i in range(64) if not ((occupied >> i) & 1)])
            
        row = chr(move // 8 + ord('a')).upper()
        col = move % 8 + 1
        print(f"{player_label} played {row}{col}")
            
        # Apply move
        bitboards[current_player] |= (1 << move)
        print_board(bitboards)
        turn += 1

if __name__ == '__main__':
    main()
