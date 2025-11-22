import turtle as t
import random
import time

delay = 0.1
score = 10000000000000000
high_score = 0

# Setup screen
sc = t.Screen()
sc.title("Snake Game")
sc.bgcolor("black")
sc.setup(width=600, height=600)
sc.tracer(0)

# Snake head
head = t.Turtle()
head.shape("square")
head.color("green")
head.penup()
head.goto(0, 0)
head.direction = "up"

# Food
food = t.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0, 100)

segments = []

# Score display
pen = t.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score : 0  High Score : 0", align="center", font=("candara", 24, "bold"))

# Directions
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
    if head.direction == "up":
        head.sety(head.ycor() + 20)
    if head.direction == "down":
        head.sety(head.ycor() - 20)
    if head.direction == "left":
        head.setx(head.xcor() - 20)
    if head.direction == "right":
        head.setx(head.xcor() + 20)

sc.listen()
sc.onkeypress(go_up, "Up")
sc.onkeypress(go_down, "Down")
sc.onkeypress(go_left, "Left")
sc.onkeypress(go_right, "Right")

# Function to reset game
def reset_game():
    global score, delay
    time.sleep(1)
    head.goto(0, 0)
    head.direction = "Stop"

    # Hide the segments
    for segment in segments:
        segment.goto(1000, 1000)
    segments.clear()

    score = 0
    delay = 0.1
    pen.clear()
    pen.write("Score : {}  High Score : {}".format(score, high_score), align="center", font=("candara", 24, "bold"))

# Main game loop
while True:
    sc.update()

    # Boundary collision
    if (head.xcor() > 290 or head.xcor() < -290 or head.ycor() > 290 or head.ycor() < -290):
        pen.goto(0, 0)
        pen.write("GAME OVER", align="center", font=("candara", 36, "bold"))
        reset_game()
        pen.goto(0, 260)

    # Food collision
    if head.distance(food) < 20:
        x = random.randint(-290, 290)
        y = random.randint(-290, 290)
        food.goto(x, y)

        # Add a segment
        new_segment = t.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("orange")
        new_segment.penup()
        segments.append(new_segment)

        delay -= 0.001
        score += 10
        if score > high_score:
            high_score = score
        pen.clear()
        pen.write("Score : {}  High Score : {}".format(score, high_score), align="center", font=("candara", 24, "bold"))

    # Move the segments
    for i in range(len(segments) - 1, 0, -1):
        x = segments[i - 1].xcor()
        y = segments[i - 1].ycor()
        segments[i].goto(x, y)

    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x, y)

    move()

    # Check for collision with self
    for segment in segments:
        if segment.distance(head) < 20:
            pen.goto(0, 0)
            pen.write("GAME OVER", align="center", font=("candara", 36, "bold"))
            reset_game()
            pen.goto(0, 260)

    time.sleep(delay)

sc.mainloop()
