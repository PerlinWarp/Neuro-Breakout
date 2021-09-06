import pygame
import multiprocessing

import common as c
from paddle import Paddle
from myo import Myo, emg_mode

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

def worker(shared_array):
	m = MyoRaw(emg_mode.PREPROCESSED)
	m.connect()

	def add_to_queue(emg, movement):
		for i in range(8):
			shared_array[i] = emg[i]

	m.add_emg_handler(add_to_queue)
	 # Orange logo and bar LEDs
	m.set_leds([128, 0, 128], [128, 0, 128])
	# Vibrate to know we connected okay
	m.vibrate(1)

	"""worker function"""
	while carryOn:
		m.run()
	print("Worker Stopped")

# -------- Main Program Loop -----------
p = multiprocessing.Process(target=worker, args=(arr,))
p.start()

# Take a moving average
left_data = []
right_data = []
paddle_predicted_pos = 0

while carryOn:
	# --- Main event loop
	for event in pygame.event.get(): # User did something
		if event.type == pygame.QUIT: # If user clicked close
			  carryOn = False # Flag that we are done so we exit this loop


	# A very simple prediction
	left_data.append(arr[7] / 500)
	right_data.append(arr[2] / 700)
	
	print(f" 2 = {arr[2]}, 7 = {arr[7]}")

	# --- Put your model here.
	pred_paddle_pos = ((sum(arr[:])/3000) * c.WIN_X) - c.PADDLE_X
	
	# Stop small gitters
	if ( abs(pred_paddle_pos-paddle.rect.x) /c.WIN_X > 0.03 ):
		# We have made a big change, so its worth updating the position
		paddle.rect.x = pred_paddle_pos

	# --- Game logic should go here
	all_sprites_list.update()

	# --- Drawing code should go here
	# First, clear the screen to dark blue.
	screen.fill(c.DARKBLUE)
 
	# Display message about training data
	font = pygame.font.Font(None, 82)
	text = font.render("Use your wrist to move the paddle", 10, c.WHITE)
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