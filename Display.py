import pygame
from pygame.locals import QUIT, KEYDOWN
from pygame.draw import arc
from random import randrange
import time
from math import pi

class Screen(object):
	"""has a screen, takes in models to draw, keyboard control, if applicable"""
	def __init__(self, model, size):
		self.model = model
		self.screen = pygame.display.set_mode(size)
		self.base_rect = (100,100,800,800)

	def draw(self):
		self.screen.fill(pygame.Color('white'))
		for arc in self.model.get_arcs():
			pygame.draw.arc(
				self.screen,
				arc['color'],
				self.base_rect, 
				arc['start_angle'],
				arc['stop_angle'],
				400)
		pygame.display.update()

class PieGraph(object):
	"""Stores the data for the graph to display (as a dictionary)"""
	def __init__(self):
		self.data = {}
		self.raw_total = 0
		self.arcs = []

	def add_slice(self, label, value):
		"""Takes a label as String and a value as a float or int. Adds to 
			raw_total and data
			>>> pg = PieGraph()
			>>> pg.add_slice('one', 1)
			>>> str(pg)
			"[('one', 1.0)]"
			>>> pg.add_slice('three', 3)
			>>> str(pg)
			"[('three', 0.75), ('one', 0.25)]"
		""" 
		self.data[label]=value
		self.raw_total+=value

	def modify_slice(self, label, dv):
		"""Takes a label as String and a value as a float or int. Adds to 
			existing data entry and raw_total
			>>> pg = PieGraph()
			>>> pg.add_slice('one', 1)
			>>> pg.add_slice('three', 3)
			>>> pg.modify_slice('one', 4)
			>>> str(pg)
			"[('one', 0.625), ('three', 0.375)]"
		""" 
		self.data[label]+=dv
		self.raw_total+=dv

	def calculate_percent(self):
		"""Calculates what percentage of the graph each label is. Returns a list of tuples
			in the format (label, percent), sorted from greatest to least.
			No doctest; this function is called by other functions and is tested through 
			their doctests"""
		perc = {}
		for k in self.data.keys():
			perc[k]=(float(self.data[k])/self.raw_total)
		return sorted(perc.items(),key=lambda x:x[1],)

	def update_arcs(self):
		"""makes a new list of dictionaries based on the current data in the PieGraph.
			Stores a list of dictionaries.
			keys: color, label, start_angle, stop_angle"""
		self.arcs = []
		curr_angle = pi/2
		for t in self.calculate_percent():
			d = {}
			d['color'] = (randrange(256),randrange(256),randrange(256), 255)
			d['label'] = t[0]
			d['start_angle']=curr_angle
			d['stop_angle']=curr_angle+(2*pi*t[1])
			curr_angle = d['stop_angle']
			self.arcs.append(d)
			self.arcs[-1]['stop_angle']=5*pi/2+.04

	def get_arcs(self):
		"""Returns a list of dictionaries.
			keys: color, label, start_angle, stop_angle,"""
		return self.arcs

	def __str__(self):
		"""Returns the String representation of the graph"""
		return str(self.calculate_percent())

class EventController(object):
	"""handles keyboard and mouse input, using the handle_event method"""
	def __init__(self, model):
		self.model = model



if __name__ == '__main__':
	import doctest
	doctest.testmod()
	pg = PieGraph()
	pg.add_slice('one', 1)
	pg.add_slice('three', 3)
	pg.modify_slice('one', 4)
	print pg
	pg.update_arcs()
	print pg.get_arcs()

	pygame.init()
	size = (1000, 1000)

	model = pg
	view = Screen(model, size)
	controller = EventController(model)
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == QUIT:
				running = False
			#else:
			#	EventController.handle_event()
		view.draw()
		time.sleep(float(1/60))