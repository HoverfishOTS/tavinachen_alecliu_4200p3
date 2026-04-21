import time

gameIsDone = False

def start_game(humanFirst:bool, thinkTimeInSeconds:int) -> None:
    print("Game Started!")
    print_board()
    if humanFirst:
        human_move()
    
    while not gameIsDone:
        ai_move(thinkTimeInSeconds)
        if gameIsDone:
            break
        human_move()

def print_board() -> None:
    pass

def ai_move(thinkTimeInSeconds: int):
    print("AI thinking...")
    start_time = time.time()
    while time.time() < start_time + thinkTimeInSeconds:
        # insert algorithm here
        pass
    # make_move()
    print_board()
    check_win_condition()

def check_win_condition():
    global gameIsDone
    pass

def human_move():
    while True: 
        humanMove = input("Choose your next move: ")
        if (len(humanMove) == 2 
            and ('a' <= humanMove[0].lower() <= 'h') 
            and ('1' <= humanMove[1] <= '8')):

            row = ord(humanMove[0].lower()) - ord('a')
            col = int(humanMove[1])

            if isMoveTaken(row, col):
                print("Move already taken!")
                continue

            make_move(row, col)
            print_board()
            check_win_condition()
            break
        else: 
            print("Invalid Move")

def make_move(row:int, col:int):
    pass

def isMoveTaken(row:int, col:int) -> bool:
    return False
    pass