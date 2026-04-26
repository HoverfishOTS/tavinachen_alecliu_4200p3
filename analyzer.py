import os
import re
import msvcrt

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_moves_from_input():
    print("Paste your moves here.")
    print("Example: 'P1 (X) played D4' or 'New AI played E4'")
    print("Press Enter twice on a blank line to finish:")
    
    lines = []
    blank_count = 0
    while True:
        try:
            line = input()
            if not line.strip():
                blank_count += 1
                if blank_count >= 2:
                    break
            else:
                blank_count = 0
                lines.append(line)
        except EOFError:
            break
            
    moves = []
    # Regex to extract moves like "played D4"
    pattern = re.compile(r'played\s+([A-H][1-8])', re.IGNORECASE)
    
    player_turn = 0 
    
    for line in lines:
        match = pattern.search(line)
        if match:
            coord = match.group(1).upper()
            row = ord(coord[0]) - ord('A')
            col = int(coord[1]) - 1
            
            # Determine player symbol (X or O)
            if '(X)' in line or 'P1' in line or 'New AI' in line and player_turn == 0:
                player = 'X'
            elif '(O)' in line or 'P2' in line or 'Old AI' in line and player_turn == 1:
                player = 'O'
            else:
                player = 'X' if player_turn == 0 else 'O'
                
            moves.append({'player': player, 'coord': coord, 'r': row, 'c': col})
            player_turn = 1 - player_turn
            
    return moves

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def format_moves(moves, current_ply):
    words = []
    for i, m in enumerate(moves):
        if i % 2 == 0:
            words.append(f"{i//2 + 1}.")
        
        coord = m['coord']
        if i == current_ply - 1:
            words.append(f"\033[92m{coord}\033[0m")
        else:
            words.append(coord)
            
    # Wrap words into neat lines
    lines = []
    current_line = []
    current_len = 0
    
    for w in words:
        w_len = len(strip_ansi(w)) + 1 # +1 for the space
        if current_len + w_len > 60:
            lines.append(" ".join(current_line))
            current_line = [w]
            current_len = w_len
        else:
            current_line.append(w)
            current_len += w_len
            
    if current_line:
        lines.append(" ".join(current_line))
        
    return "\n".join(lines)

def draw_board(moves, current_ply):
    # Initialize empty board
    board = [['-' for _ in range(8)] for _ in range(8)]
    
    # Apply moves up to current_ply
    for i in range(current_ply):
        m = moves[i]
        r = m['r']
        c = m['c']
        
        # Highlight the most recently placed piece in green
        if i == current_ply - 1:
            board[r][c] = f"\033[92m{m['player']}\033[0m"
        else:
            board[r][c] = m['player']
            
    # Print the board
    print("  1 2 3 4 5 6 7 8")
    for r in range(8):
        row_str = " ".join(board[r])
        print(f"{chr(ord('A')+r)} {row_str}")

def main():
    os.system('') # Enable ANSI escape sequences in Windows terminal
    clear_screen()
    
    moves = get_moves_from_input()
    
    if not moves:
        print("No moves parsed. Exiting.")
        return
        
    current_ply = len(moves)
    max_ply = len(moves)
    
    while True:
        clear_screen()
        print(f"Game Analyzer (Ply {current_ply}/{max_ply})")
        print("Use Left/Right arrow keys to scrub. Press 'Q' or 'Esc' to quit.\n")
        
        draw_board(moves, current_ply)
        print("\n" + format_moves(moves, current_ply))
        
        # Wait for keypress
        key = msvcrt.getch()
        
        # Arrow keys return a prefix byte (\xe0 or \x00), then a key code
        if key in (b'\xe0', b'\x00'):
            subkey = msvcrt.getch()
            if subkey == b'K': # Left arrow
                if current_ply > 0:
                    current_ply -= 1
            elif subkey == b'M': # Right arrow
                if current_ply < max_ply:
                    current_ply += 1
            # You could add Up/Down to jump to start/end if desired
            elif subkey == b'H': # Up arrow
                current_ply = 0
            elif subkey == b'P': # Down arrow
                current_ply = max_ply
        elif key.lower() == b'q' or key == b'\x1b': # 'q' or Esc
            break
            
    clear_screen()
    print("Exited Analyzer.")

if __name__ == '__main__':
    main()
