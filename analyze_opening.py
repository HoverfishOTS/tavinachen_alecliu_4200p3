import game
from time import time

def get_pv(depth):
    pv = []
    bitboards = list(game.bitboards)
    player = game.AI
    for _ in range(depth):
        state_key = (bitboards[0], bitboards[1], player)
        if state_key in game.tt:
            tt_depth, tt_flag, tt_score, tt_move = game.tt[state_key]
            if tt_move is not None:
                pv.append((player, tt_move))
                bitboards[player] |= (1 << tt_move)
                player = 1 - player
            else:
                break
        else:
            break
    return pv

def main():
    game.bitboards = [0, 0]
    
    # Apply D4 (X) and C3 (O)
    d4_index = 27 # Row D (3), Col 4 (3)
    c3_index = 18 # Row C (2), Col 3 (2)
    
    game.make_move(d4_index, game.AI)
    game.make_move(c3_index, game.HUMAN)
    
    print("Initial Board (X played D4, O played C3):")
    
    # game.print_board() doesn't take arguments, uses global bitboards
    print("  1 2 3 4 5 6 7 8")
    for r in range(8):
        print(f"{chr(ord('A')+r)}", end="")
        for c in range(8):
            i = r*8 + c
            if (game.bitboards[game.AI] >> i) & 1:
                print(" X", end="")
            elif (game.bitboards[game.HUMAN] >> i) & 1:
                print(" O", end="")
            else:
                print(" -", end="")
        print()
    
    think_time = 15
    game.end_time = time() + think_time
    
    depth = 1
    bestMove = None
    
    print(f"\nAnalyzing D4 C3 opening for {think_time} seconds...")
    while time() <= game.end_time and depth < 64:
        move = game.alpha_beta_pruning(float('-inf'), float('inf'), depth)
        if time() <= game.end_time:
            bestMove = move
            pv = get_pv(depth)
            
            pv_str = []
            for p, m in pv:
                row = chr(m // 8 + ord('a')).upper()
                col = m % 8 + 1
                label = "X" if p == game.AI else "O"
                pv_str.append(f"{label}:{row}{col}")
                
            # If PV doesn't start with the root move, insert it
            if len(pv) == 0 or pv[0][1] != bestMove:
                row = chr(bestMove // 8 + ord('a')).upper()
                col = bestMove % 8 + 1
                pv_str.insert(0, f"X:{row}{col}*")
                
            print(f"Depth {depth:2d} | Best Move: {chr(bestMove // 8 + ord('a')).upper()}{bestMove % 8 + 1} | PV: {' '.join(pv_str)}")
        depth += 1

if __name__ == '__main__':
    main()
