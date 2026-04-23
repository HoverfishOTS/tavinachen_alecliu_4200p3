# Tavina Chen & Alec Liu: CS 4800 Project 3
# This program provides a user interface for the game 4-in-a-line.

from game import start_game

humanFirst = True
thinkTimeInSeconds = 5
maxThinkTimeInSeconds = 30
minThinkTimeInSeconds = 1

def main() -> None:
    print("CS4200 Project 3: 4-in-a-line")

    while True:
        selection_prompt()
        start_game(humanFirst, thinkTimeInSeconds)
        if not is_yes("Would you like to play again? (y/n): "):
            break
    
def selection_prompt() -> None:
    global humanFirst, thinkTimeInSeconds, maxThinkTimeInSeconds, minThinkTimeInSeconds

    humanFirst = is_yes("Would you like to go first? (y/n): ")

    while True:
        try:
            thinkTimeInSeconds = int(input("How long should the computer think about its moves (in seconds)?: "))
            if thinkTimeInSeconds < minThinkTimeInSeconds or thinkTimeInSeconds > maxThinkTimeInSeconds:
                print(f"Selection out of range ({minThinkTimeInSeconds}-{maxThinkTimeInSeconds}).")
                continue
            break
        except ValueError:
            print("Please input integers only")
    
def is_yes(text) -> bool:
    while True: 
        yes = input(text)
        if yes.lower() != 'y' and yes.lower() != 'n':
            print("Please input 'y' or 'n'")
        else:
            return yes.lower() == 'y'

             
if __name__ == "__main__":
    main()