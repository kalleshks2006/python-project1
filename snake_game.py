"""Simple Snake game using only Python's built-in turtle module.

Run with: python snake_game.py
Use the arrow keys to move. Close the window to quit.
"""

import random
import time
import turtle

WIDTH, HEIGHT = 600, 600
STEP = 20
DELAY = 0.1

screen = turtle.Screen()
screen.title("Snake Game")
screen.bgcolor("#101820")
screen.setup(WIDTH, HEIGHT)
screen.tracer(0)

head = turtle.Turtle()
head.shape("square")
head.color("#63e6be")
head.penup()
head.direction = "stop"

food = turtle.Turtle()
food.shape("circle")
food.color("#ff6b6b")
food.penup()
food.goto(0, 100)

segments = []
score = 0

label = turtle.Turtle()
label.hideturtle()
label.color("white")
label.penup()
label.goto(0, 260)


def update_score():
    label.clear()
    label.write(f"Score: {score}", align="center", font=("Arial", 18, "bold"))


def go_up():
    if head.direction != "down":
        head.direction = "up"


def go_down():
    if head.direction != "up":
        head.direction = "down"


def go_left():
    if head.direction != "right":
        head.direction = "left"


def go_right():
    if head.direction != "left":
        head.direction = "right"


def move():
    x, y = head.xcor(), head.ycor()
    if head.direction == "up":
        head.sety(y + STEP)
    elif head.direction == "down":
        head.sety(y - STEP)
    elif head.direction == "left":
        head.setx(x - STEP)
    elif head.direction == "right":
        head.setx(x + STEP)


def reset_game():
    global score
    time.sleep(0.6)
    head.goto(0, 0)
    head.direction = "stop"
    for segment in segments:
        segment.goto(1000, 1000)
    segments.clear()
    score = 0
    update_score()


screen.listen()
screen.onkeypress(go_up, "Up")
screen.onkeypress(go_down, "Down")
screen.onkeypress(go_left, "Left")
screen.onkeypress(go_right, "Right")

update_score()

while True:
    screen.update()

    # Hit a wall.
    if abs(head.xcor()) >= 290 or abs(head.ycor()) >= 290:
        reset_game()

    # Eat food and add one body segment.
    if head.distance(food) < 18:
        food.goto(random.randrange(-270, 271, STEP), random.randrange(-250, 251, STEP))
        segment = turtle.Turtle()
        segment.shape("square")
        segment.color("#38d9a9")
        segment.penup()
        segments.append(segment)
        score += 10
        update_score()

    # Move tail first, then the head.
    for index in range(len(segments) - 1, 0, -1):
        segments[index].goto(segments[index - 1].position())
    if segments:
        segments[0].goto(head.position())
    move()

    # Hit own body.
    if any(head.distance(segment) < 12 for segment in segments):
        reset_game()

    time.sleep(DELAY)
