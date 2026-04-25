# Tavina Chen & Alec Liu: CS 4800 Project 3
# This program provides a user interface for the game 4-in-a-line.

from game import start_game

# default values
humanFirst = True
thinkTimeInSeconds = 5
maxThinkTimeInSeconds = 30
minThinkTimeInSeconds = 5

def main() -> None:
    print("CS4200 Project 3: 4-in-a-line")

    # starts and continues the game
    while True:
        selection_prompt()
        start_game(humanFirst, thinkTimeInSeconds)
        if not is_yes("Would you like to play again? (y/n): "):
            break

# this method prompts the user for their preferences for the game
def selection_prompt() -> None:
    global humanFirst, thinkTimeInSeconds

    humanFirst = is_yes("Would you like to go first? (y/n): ")

    # prompt and validates integer input for ai think time
    while True:
        try:
            thinkTimeInSeconds = int(input("How long should the computer think about its moves (in seconds)?: "))
            if thinkTimeInSeconds < minThinkTimeInSeconds or thinkTimeInSeconds > maxThinkTimeInSeconds:
                print(f"Selection out of range ({minThinkTimeInSeconds}-{maxThinkTimeInSeconds}).")
                continue
            break
        except ValueError:
            print("Please input integers only")
    
# this method validates yes and no question inputs
def is_yes(text) -> bool:
    while True: 
        yes = input(text)
        if yes.lower() != 'y' and yes.lower() != 'n':
            print("Please input 'y' or 'n'")
        else:
            return yes.lower() == 'y'

             
if __name__ == "__main__":
    main()