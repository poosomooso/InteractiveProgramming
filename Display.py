import pygame
from pygame.locals import QUIT, KEYDOWN


class Screen(object):
	"""has a screen, takes in models to draw, keyboard control, if applicable"""
	def __init__(self, model, size):
		self.model = model
		self.screen = pygame.display.set_mode(size)

	def draw(self):
		self.screen.fill(pygame.Color('black'))
		for arc in self.model.arcs:
			arc = pygame.draw.arc()
			
class PieGraph(object):
	"""Stores the data for the graph to display (as a dictionary?), creates the model
		for drawing arcs"""

class EventController(object):
	"""handles keyboard and mouse input, using the handle_event method"""
	def __init__(self, model):
		self.model = model

if __name__ == '__main__':
	pygame.init()
	size = (1000, 800)

	model = PieGrapherModel(size)
	view = Screen(model, size)
	controller = EventController(model)
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == QUIT:
				running = False
			#else:
			#	EventController.handle_event()