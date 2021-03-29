import pygame
import multiprocessing

import common as c
from paddle import Paddle
from ball import Ball
from brick import Brick
from myo_raw import MyoRaw
from predictor import Predictor

pygame.init()
 
score = 0
lives = 6
 
# Open a new window
size = (c.WIN_X, c.WIN_Y)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Breakout Game")

# Functions
def make_wall():
	all_bricks = pygame.sprite.Group()
	bx = 80 * c.SCALE
	by = 30 * c.SCALE
	for i in range(7):
		brick = Brick(c.RED, bx, by)
		brick.rect.x = 60*c.SCALE + i*100*c.SCALE
		brick.rect.y = 60*c.SCALE
		all_sprites_list.add(brick)
		all_bricks.add(brick)
	for i in range(7):
		brick = Brick(c.ORANGE, bx, by)
		brick.rect.x = 60*c.SCALE + i*100*c.SCALE
		brick.rect.y = 100 * c.SCALE
		all_sprites_list.add(brick)
		all_bricks.add(brick)
	for i in range(7):
		brick = Brick(c.YELLOW, bx, by)
		brick.rect.x = 60*c.SCALE + i*100*c.SCALE
		brick.rect.y = 140 * c.SCALE
		all_sprites_list.add(brick)
		all_bricks.add(brick)
	return all_bricks
 
# This will be a list that will contain all the sprites we intend to use in our game.
all_sprites_list = pygame.sprite.Group()
 
# Create the Paddle
paddle = Paddle(c.LIGHTBLUE, c.PADDLE_X, c.PADDLE_Y)
paddle.rect.x = (c.WIN_X - c.PADDLE_X)//2
paddle.rect.y = int((c.WIN_Y * 7/8))
 
# Create the ball sprite
ball = Ball(c.WHITE, c.BALL_SIZE, c.BALL_SIZE)
ball.rect.x = (c.WIN_X - c.BALL_SIZE)//2
ball.rect.y = int(6/8 * c.WIN_Y)
 
# Add the paddle to the list of sprites
all_sprites_list.add(paddle)
all_sprites_list.add(ball)

# Make the wall of bricks
all_bricks = make_wall()
 
# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True
 
# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

m = MyoRaw(raw=False, filtered=True)
m.connect()

def worker(q):
	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	"""worker function"""
	while carryOn:
		m.run(1)
	print("Worker Stopped")

def print_battery(bat):
	print("Battery level:", bat)

m.add_battery_handler(print_battery)

 # Orange logo and bar LEDs
m.set_leds([128, 0, 0], [128, 0, 0])
# Vibrate to know we connected okay
m.vibrate(1)

# -------- Main Program Loop -----------
p = multiprocessing.Process(target=worker, args=(q,))
p.start()

# Make a predictor
pred_paddle_pos = c.WIN_X / 2
predictor = Predictor()


while carryOn:
	# --- Main event loop
	for event in pygame.event.get(): # User did something
		if event.type == pygame.QUIT: # If user clicked close
			  carryOn = False # Flag that we are done so we exit this loop

	# Moving the paddle when the use uses the arrow keys
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		paddle.moveLeft(c.PADDLE_SPEED)
	if keys[pygame.K_RIGHT]:
		paddle.moveRight(c.PADDLE_SPEED)

	# Paddle prediction
	left_data = []
	right_data = []

	while not(q.empty()):
		# Get the new data from the Myo queue
		d = list(q.get())
		left_data.append(d[7])
		right_data.append(d[2])

	if (len(right_data) > 0):
		# If we got new data, make a prediction
		pred_paddle_pos = predictor.predict(left_data, right_data)

	paddle.rect.x = pred_paddle_pos
	# --- Game logic should go here
	all_sprites_list.update()

	# Check if the ball is bouncing against any of the 4 walls:
	if ball.rect.x >= c.WIN_X - c.BALL_SIZE:
		ball.velocity[0] = -ball.velocity[0]
		ball.velocity[1] += 1
	elif ball.rect.x <= 0:
		ball.velocity[0] = -ball.velocity[0]
		ball.velocity[1] += 1
	
	if ball.rect.y >= c.WIN_Y - c.BALL_SIZE:
		ball.velocity[1] = -1* abs(ball.velocity[1])
		lives -= 1
		if lives == 0:
			#Display Game Over Message for 3 seconds
			font = pygame.font.Font(None, 74)
			text = font.render("GAME OVER", 1, c.WHITE)
			screen.blit(text, (c.WIN_X/2 - 74, c.WIN_Y/2 ))
			pygame.display.flip()
			pygame.time.wait(3000)
 
			#Stop the Game
			carryOn=False
	elif ball.rect.y < 40:
		ball.velocity[1] = abs(ball.velocity[1])

	# Stop it from getting stuck veritcally
	if ball.velocity[1] == 0: ball.velocity[1] = 1

	# Detect collisions between the ball and the paddles
	if pygame.sprite.collide_mask(ball, paddle):
	  ball.rect.x -= ball.velocity[0]
	  ball.rect.y -= ball.velocity[1]
	  ball.bounce()

	# Check if there is the ball collides with any of bricks
	brick_collision_list = pygame.sprite.spritecollide(ball,all_bricks,False)
	
	for brick in brick_collision_list:
		ball.bounce()
		score += 1
		brick.kill()
		if len(all_bricks)==0: 
		# Display Level Complete Message for 3 seconds
			font = pygame.font.Font(None, 74)
			text = font.render("LEVEL COMPLETE", 1, c.WHITE)
			screen.blit(text, (200*c.SCALE, 300*c.SCALE))
			pygame.display.flip()

			pygame.time.wait(3000)

			#Stop the Game
			carryOn=False
 
	# --- Drawing code should go here
	# First, clear the screen to dark blue.
	screen.fill(c.DARKBLUE)
	pygame.draw.line(screen, c.WHITE, [0, 38], [c.WIN_X, 38], 2)
 
	#Display the score and the number of lives at the top of the screen
	font = pygame.font.Font(None, 34)
	text = font.render("Score: " + str(score), 1, c.WHITE)
	screen.blit(text, (int(c.WIN_X * 1/8),10))
	text = font.render("Lives: " + str(lives), 1, c.WHITE)
	screen.blit(text, (int(c.WIN_X * 7/8),10))
 
	#Now let's draw all the sprites in one go. (For now we only have 2 sprites!)
	all_sprites_list.draw(screen)
 
	# --- Go ahead and update the screen with what we've drawn.
	pygame.display.flip()
 
	# --- Limit to 60 frames per second
	clock.tick(60)
 
# Once we have exited the main program loop we can stop the game engine:
pygame.quit()