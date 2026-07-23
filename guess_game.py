import random
secretNumber=random.randint(1,20)
print("I am thinking of anumber between 1 and 20.")
for guessesTaken in range(1,7):
    print("Take a guess.")
    guess=int(input())
    if guess<secretNumber:
        print("Your guess is too low.")
    elif guess>secretNumber:
        print("Your guess is too high.")
    else:
        break
print("Good job! You guessed my number in " + str(guessesTaken) + " guesses!")    