import pygame
import multiprocessing
import numpy as np


import common as c
from paddle import Paddle
from myo_raw import MyoRaw

pygame.init()
 
score = 0
lives = 3
MOVE_SPEED = 10
 
# Open a new window
size = (c.WIN_X, c.WIN_Y)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Breakout Game")
 
# This will be a list that will contain all the sprites we intend to use in our game.
all_sprites_list = pygame.sprite.Group()
 
# Create the Paddle
paddle = Paddle(c.LIGHTBLUE, c.PADDLE_X, c.PADDLE_Y)
paddle.rect.x = (c.WIN_X - c.PADDLE_X)//2
paddle.rect.y = int((c.WIN_Y * 7/8))
 
# Add the paddle to the list of sprites
all_sprites_list.add(paddle)

# The loop will carry on until the user exit the game (e.g. clicks the close button).
carryOn = True
 
# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()

paddle_dir = MOVE_SPEED

# ------------ Myo Setup ---------------
arr = multiprocessing.Array('i', range(8))

m = MyoRaw(filtered=False)
m.connect()

def worker(shared_array):
	def add_to_queue(emg, movement):
		for i in range(8):
			shared_array[i] = emg[i]

	m.add_emg_handler(add_to_queue)

	"""worker function"""
	while carryOn:
		m.run(1)
	print("Worker Stopped")

 # Orange logo and bar LEDs
m.set_leds([128, 0, 128], [128, 0, 128])
# Vibrate to know we connected okay
m.vibrate(1)

# -------- Main Program Loop -----------
p = multiprocessing.Process(target=worker, args=(arr,))
p.start()

while carryOn:
	# --- Main event loop
	for event in pygame.event.get(): # User did something
		if event.type == pygame.QUIT: # If user clicked close
			  carryOn = False # Flag that we are done so we exit this loop


	# A very simple prediction
	if not(arr[2] == 0):
		left = abs(arr[7]) / 50
		right = abs(arr[2]) / 70
	
	print(f" 2 = {arr[2]}, 7 = {arr[7]}")
	print(f"L{left}, R{right}")
	# if (left > right):
	# 	paddle.rect.x = 100
	# else:
	# 	paddle.rect.x = 800
	pred_paddle_pos = (left*-c.WIN_X) + (right*c.WIN_X) - c.PADDLE_X
	paddle.rect.x = pred_paddle_pos
	#paddle.rect.x = (sum(arr[:])/3000) * c.WIN_X
	#paddle.rect.x = (arr[4]/100) * c.WIN_X
		
	# --- Game logic should go here
	all_sprites_list.update()

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
 
	# Display message about training data
	font = pygame.font.Font(None, 82)
	text = font.render("Keeping your arm still", 10, c.WHITE)
	screen.blit(text, (int(c.WIN_X * 1/4) - 41, int(c.WIN_Y/2) - 60 ))
	text = font.render("Use your wrist to follow the paddle", 10, c.WHITE)
	screen.blit(text, (int(c.WIN_X * 1/4) - 41,int(c.WIN_Y/2)))

	#Now let's draw all the sprites in one go. (For now we only have 2 sprites!)
	all_sprites_list.draw(screen)
 
	# --- Go ahead and update the screen with what we've drawn.
	pygame.display.flip()
 
	# --- Limit to 60 frames per second
	clock.tick(60)

	# Moving the paddle when the use uses the arrow keys
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		paddle.moveLeft(c.PADDLE_SPEED)
	if keys[pygame.K_RIGHT]:
		paddle.moveRight(c.PADDLE_SPEED)
	if keys[pygame.K_SPACE]:
		# Shut down Myo Worker
		carryOn = False

		m.disconnect()
		print("Myo Disconnected")

		pygame.quit()
		p.terminate()
		p.join()
		
 
# Once we have exited the main program loop we can stop the game engine:
pygame.quit()