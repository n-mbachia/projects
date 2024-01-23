#!/usr/bin/python3

import random
import time
import turtle

# Parameters to set up animation
background_colour = 50, 50, 50 # RGB
screen_size = 800, 800

grid_size = 16, 16 # tuple containg two values for x and y coordinates
grid_scale = (
    screen_size[0] / grid_size[0],
    screen_size[1] / grid_size[1]
) # tuples cocntaing two values for x and y coordinates
fraction_of_grid_points_used = 0.35
n_tiles = int(
    fraction_of_grid_points_used * grid_size[0] * grid_size[1]
)

ball_colour = 0, 191, 255
new_ball_interval = 2
max_ball_speed = 2
ball_speed_step = 0.2

# Functions to convert between grid and screen coordinates
def convert_grid_to_screen_coords(grid_coords):
    return (
        grid_coords[0] * grid_scale[0] - screen_size[0]/2 + grid_scale[0]/2,
        grid_coords[1] * grid_scale[1] - screen_size[1]/2 + grid_scale[1]/2,
    )

def convert_screen_to_grid_coords(screen_coords):
    return (
        round(
            (screen_coords[0] - grid_scale[0]/2 + screen_size[0]/2) / grid_scale[0]
        ),
        round(
            (screen_coords[1] - grid_scale[1]/2 + screen_size[1]/2) / grid_scale[1]
        ),
    )

# Create window settings
window = turtle.Screen()
window.tracer(0) # control when things are drawn on screen
window.colormode(255)
window.setup(*screen_size) # set size of window uses unpacking operator
window.bgcolor(background_colour)

tile_grid_coords = set() # Emplty set initiated
while len(tile_grid_coords) < n_tiles: # Ebsures required number of coordinates is reached
    tile_grid_coords.add(
        (
            random.randint(0, grid_size[0] - 1),
            random.randint(0, grid_size[1] - 1)
        )
    )
    """The grid coordinates that the program chooses range from (0,0) to (15, 15)"""

# Define actions based on grid point colour
def speed_up(ball: turtle.Turtle):
    """Increase ball speed until it reached max_ball_speed"""
    ball.ball_speed += ball_speed_step
    if ball.ball_speed > max_ball_speed:
        ball.ball_speed = max_ball_speed
        
def slow_down(ball: turtle.Turtle):
    """Decrease ball speed. Hide and remove from list when stationary"""
    ball.ball_speed -= ball_speed_step
    if ball.ball_speed < ball_speed_step:
        ball.hideturtle()
        balls.remove(ball)

def change_direction(ball: turtle.Turtle):
    """Rotate Turtle object by a random angle in [-90, 90] range"""
    ball.left(random.randint(-90, 90))

# Map colours to ball actions
actions = {
    (144, 238, 144): speed_up,
    (220, 20,60): slow_down,
    (255, 127, 80): change_direction,
}

# Create tiles
tiles = {
    coord: random.choice(tuple(actions.keys()))
    for coord in tile_grid_coords
}

# Create balls
balls = [] # Empty list for balls

def change_ball_colour(ball):
    fraction_of_max_speed = ball.ball_speed / max_ball_speed
    ball.fillcolor(
        int(ball_colour[0] * fraction_of_max_speed),
        int(ball_colour[1] * fraction_of_max_speed),
        int(ball_colour[2] * fraction_of_max_speed),
    )

def create_new_ball():
    ball = turtle.Turtle() # Creates an instance
    ball.penup() # ensures no line is drawn when object moves
    ball.shape("circle") # defines shape of displayed object
    ball.pencolor("white") # outlines the defined object in white colour
    ball.setposition(
        random.randint(-screen_size[0] // 2, screen_size[0] // 2),
        random.randint(-screen_size[1] // 2, screen_size[1] // 2)
    ) # x & y coordinates as arguments set by floor division
    ball.setheading(random.randint(0, 359)) # changes orientation of the Turtle object
    ball.ball_speed = 0.5
    ball.current_grid = None
    change_ball_colour(ball)
    
    balls.append(ball)
    
create_new_ball() # starts animation with one 

# Draw tiles on screen
grid_draw = turtle.Turtle()
grid_draw.penup()
grid_draw.hideturtle()

for coord, colour in tiles.items():
    coords = convert_grid_to_screen_coords(coord)
    grid_draw.setposition(
        coords[0] - grid_scale[0] / 2 *0.9,
        coords[1] - grid_scale[1] /2 * 0.9
    )
    grid_draw.color(colour)
    grid_draw.pendown()
    for _ in range(2):
        grid_draw.forward(grid_scale[0] * 0.8)
        grid_draw.left(90)
        grid_draw.forward(grid_scale[1] * 0.8)
        grid_draw.left(90)
    grid_draw.penup()

# Main animation loop
start_timer = time.time()
while True:
    # Create new ball every time interval elapses
    if time.time() - start_timer > new_ball_interval:
        create_new_ball()
        start_timer= time.time()
        
    for ball in balls: # iterates through list that contains balls
        # Move ball
        ball.forward(ball.ball_speed)
        # If ball leaves screen, it moves to any other side of screen
        if abs(ball.xcor()) > screen_size[0] / 2:
            ball.setx(-ball.xcor())
        if abs(ball.ycor()) > screen_size[1] / 2:
            ball.sety(-ball.ycor())
            
        # Check whether ball hit tile and perform required action
        ball_grid_coords = convert_screen_to_grid_coords(ball.position())
        if (
                ball_grid_coords in tiles.keys()
                and ball_grid_coords != ball.current_grid
        ):
            colour = tiles[ball_grid_coords]
            actions[colour](ball)
            ball.current_grid = ball_grid_coords
            change_ball_colour(ball)
            
    window.update() # refreshes the image once per frame
    time.sleep(0.001) # introduces a delay in the loop

