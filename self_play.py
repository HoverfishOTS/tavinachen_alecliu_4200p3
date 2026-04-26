import game
import random
import time

def get_best_move(think_time):
    end_time = time.time() + think_time
    game.end_time = end_time
    depth = 1
    bestMove = None
    
    while depth < 64 and time.time() <= end_time:
        move = game.alpha_beta_pruning(float('-inf'), float('inf'), depth, bestMove)
        depth += 1
        if time.time() < end_time:
            bestMove = move
            
    return bestMove

def play_match(match_id, num_random_moves=4, think_time=1.0):
    print(f"\n--- Match {match_id} ---")
    game.bitboards = [0, 0]
    game.tt = {}
    
    # Apply random starting positions
    available_moves = list(range(64))
    for i in range(num_random_moves):
        move = random.choice(available_moves)
        available_moves.remove(move)
        player = game.AI if i % 2 == 0 else game.HUMAN
        game.make_move(move, player)
        
    print(f"Starting board after {num_random_moves} random moves:")
    game.print_board()
    
    turn = 0
    while True:
        is_terminal = game.isWin()
        occupied = game.bitboards[game.AI] | game.bitboards[game.HUMAN]
        if is_terminal == game.FOUR_IN_A_ROW:
            print("Player 1 (X) Wins!")
            return 1
        elif is_terminal == -game.FOUR_IN_A_ROW:
            print("Player 2 (O) Wins!")
            return 2
        elif occupied == game.FULL_BOARD:
            print("Tie!")
            return 0
            
        if turn % 2 == 0:
            # Player 1 (AI)
            move = get_best_move(think_time)
            if move is None:
                # Fallback if no move found (shouldn't happen)
                move = random.choice([i for i in range(64) if not game.isMoveTaken(i)])
            game.make_move(move, game.AI)
            row = chr(move // 8 + ord('a')).upper()
            col = move % 8 + 1
            print(f"P1 (X) played {row}{col}")
        else:
            # Player 2 (HUMAN, but played by AI logic via board swapping)
            # Swap boards so the AI evaluates from Player 2's perspective
            game.bitboards[0], game.bitboards[1] = game.bitboards[1], game.bitboards[0]
            move = get_best_move(think_time)
            if move is None:
                move = random.choice([i for i in range(64) if not game.isMoveTaken(i)])
            game.make_move(move, game.AI) # Plays as AI on the swapped board
            # Swap back
            game.bitboards[0], game.bitboards[1] = game.bitboards[1], game.bitboards[0]
            
            row = chr(move // 8 + ord('a')).upper()
            col = move % 8 + 1
            print(f"P2 (O) played {row}{col}")
            
        turn += 1

def main():
    num_matches = 1
    think_time = 5.0 # 5 seconds per move
    
    results = {1: 0, 2: 0, 0: 0}
    
    for i in range(num_matches):
        winner = play_match(i + 1, num_random_moves=0, think_time=think_time)
        results[winner] += 1
        print("Final Board:")
        game.print_board()
        
    print("\n--- Final Results ---")
    print(f"Player 1 (X) Wins: {results[1]}")
    print(f"Player 2 (O) Wins: {results[2]}")
    print(f"Ties: {results[0]}")

if __name__ == '__main__':
    main()
