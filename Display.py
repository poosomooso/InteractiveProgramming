import pygame
from pygame.locals import QUIT, KEYDOWN
from pygame.draw import arc
from random import randrange
import time
from math import pi, sin, cos
from numpy import arange
import doctest
import Tkinter as t
import tkMessageBox


class Screen(object):
	"""Creates the screen and defines base variables for the arcs"""
	def __init__(self, model, size):
		self.model = model
		self.screen = pygame.display.set_mode(size)
		self.radius = 400
		self.base_rect = pygame.Rect(100,100,self.radius*2,self.radius*2)

	def draw(self):
		"""This function redraws the screen and updates it"""
		self.screen.fill((0,0,0))
		for arc in self.model.get_arcs():
			col = arc['color']
			pygame.draw.arc(
				self.screen,
				col,
				self.base_rect, 
				arc['start_angle'],
				arc['stop_angle'],
				self.radius/2)
			cx = self.base_rect.centerx
			cy = self.base_rect.centery
			for theta in arange(arc['start_angle'],arc['stop_angle'],.00005):
				pygame.draw.line(self.screen, col, (cx,cy), (self.radius*cos(theta)+cx,-1*self.radius*sin(theta)+cy))
			font = pygame.font.Font('DINOT-Bold.otf',30)
			words = font.render(arc['label'],True, (0,0,0))

			pos = (cx + int(self.radius*cos((arc['start_angle']+arc['stop_angle'])/2.0)/2),
					cy - int(self.radius*sin((arc['start_angle']+arc['stop_angle'])/2.0)/2))
			pygame.draw.rect(self.screen, (col[0]+20,col[1]+20,col[2]+20), (pos[0],pos[1],words.get_width(),words.get_height()))
			
			self.screen.blit(words,pos)
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
			"[('one', 0.25), ('three', 0.75)]"
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
			"[('three', 0.375), ('one', 0.625)]"
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
			#ensure darker colors
			d['color'] = (randrange(40,210),randrange(40,210),randrange(40,210), 255)
			d['label'] = t[0]
			d['start_angle']=curr_angle
			d['stop_angle']=curr_angle+(2*pi*t[1])
			curr_angle = d['stop_angle']
			self.arcs.append(d)
		self.arcs[-1]['stop_angle']=5*pi/2

	def get_arcs(self):
		"""Returns a list of dictionaries.
			keys: color, label, start_angle, stop_angle,"""
		return self.arcs

	def __str__(self):
		"""Returns the String representation of the graph"""
		return str(self.calculate_percent())

class input_menu(object):
	'''Creates a Tkinter screen for the user to input data'''
	def __init__(self, pg, view):
		self.main_window = t.Tk()

		self.frame = t.Frame(self.main_window)
		self.name_var = t.StringVar()
		self.val_var = t.DoubleVar()

		self.tbox = t.Entry(self.frame, width=7, textvariable=self.name_var, text = 'Name: ')
		self.val = t.Entry(self.frame, width = 4, textvariable=self.val_var, text = 'Value: ')
		self.bt1 = t.Button(self.frame, text = 'Enter', command = self.add)

		self.tbox.pack()
		self.val.pack()
		self.bt1.pack()
		self.frame.pack()
		t.mainloop()

	def add(self):
		''' This method is called when the enter button is pressed

			If the data is invalid or a variable is missing, it will display an error message
			Eg: if the user enters nothing for the first data point, if the user enters a string for the value
		'''
		try:
			pg.add_slice(self.name_var.get(), self.val_var.get())
			pg.update_arcs()
			self.main_window.destroy()
			view.draw()
		except:
			tkMessageBox.showwarning(
            "!!Error!!",
            "Invalid Data"
        )

def deal_with_event(event):
	''' This function takes an event and returns true if the event type is quit

		If the key press is enter, it pulls up the data menu
		If the key press is s, it saves the current graph

		Otherwise, it returns false
	'''
	if event.type == QUIT:
		return True
	if event.type == pygame.KEYDOWN:
		if event.key == pygame.K_RETURN:
			input_menu(pg, view)
		elif event.key == pygame.K_s:
			pygame.image.save(view.screen, "screenshot.jpeg")

if __name__ == '__main__':
	doctest.testmod()
	pg = PieGraph()
	pygame.init()
	view = Screen(pg, (1000, 1000))
	running = True
	menu = input_menu(pg, view)
	while running:
		for event in pygame.event.get():
			running = not deal_with_event(event)
		time.sleep(float(1/30))