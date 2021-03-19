import pygame
from random import randint
BLACK = (0,0,0)

class Ball(pygame.sprite.Sprite):
	# Ball class derives from Sprite class in pygame

	def __init__(self, colour, width, height):
		# Call to parent class, Sprite, constructor
		super().__init__()

		# Pass in the colour of the ball, its width and height.
		# Set the background colour to transparent
		self.image = pygame.Surface([width, height])
		self.image.fill(BLACK)
		self.image.set_colorkey(BLACK)

		# Draw a rectangle for the ball
		pygame.draw.rect(self.image, colour, [0, 0, width, height])

		self.velocity = [randint(4,8), randint(-8,7)]

		# Fetch the rectangle object that has the dimentions of the image. 
		self.rect = self.image.get_rect()

	def update(self):
		self.rect.x += int(self.velocity[0])
		self.rect.y += int(self.velocity[1])

		# Stop ball from just bouncing off the side walls.
		self.velocity[1] += 0.00001

	def bounce(self):
		self.velocity[0] = -self.velocity[0]
		self.velocity[1] = randint(-8,8)