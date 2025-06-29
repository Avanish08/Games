import random

def play_rps():
    options = ['rock', 'paper', 'scissors']
    while True:
        user = input("Enter rock, paper or scissors (or 'quit' to exit): ").lower()
        if user == 'quit':
            break
        if user not in options:
            print("Invalid choice.")
            continue
        computer = random.choice(options)
        print(f"Computer chose: {computer}")
        if user == computer:
            print("It's a tie!")
        elif (user == 'rock' and computer == 'scissors') or \
             (user == 'paper' and computer == 'rock') or \
             (user == 'scissors' and computer == 'paper'):
            print("You win!")
        else:
            print("You lose!")

play_rps()
