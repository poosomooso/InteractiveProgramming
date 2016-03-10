"""
Carl Moser and Serena Chen

Creates a GUI that allows you to make a pie graph with data that you'd like.
"""
import pygame
from pygame.locals import QUIT, KEYDOWN
from random import randrange
import time
from math import pi, sin, cos, hypot, atan2
from numpy import arange
import doctest
import Tkinter as t
import tkMessageBox


class Screen(object):
	"""Has a screen, takes in models to draw, keyboard control, if applicable"""
	def __init__(self, model, size):
		self.model = model
		self.screen = pygame.display.set_mode(size)
		self.radius = 400
		self.base_rect = pygame.Rect(100,150,self.radius*2,self.radius*2)
		self.raw=False

	def draw(self):
		"""This function redraws the screen and updates it"""
		self.screen.fill((0,0,0))

		#Creates the command label at the top of the screen
		font = pygame.font.Font('DINOT-Bold.otf',30)
		commands_line1 = font.render('Press \'ENTER\' to add a sdata entry',True,(255,255,255))
		commands_line2 = font.render('Click on a slice to modify it\'s existing value',True,(255,255,255))
		commands_line3 = font.render('Press \'S\' to save a screenshot',True,(255,255,255))
		commands_line4 = font.render('Press \'V\' to see data values',True,(255,255,255))

		self.screen.blit(commands_line1,(10,10))
		self.screen.blit(commands_line2,(10,45))
		self.screen.blit(commands_line3,(10,80))
		self.screen.blit(commands_line4,(10,115))

		#draw slices
		for arc in self.model.get_arcs():
			col = arc['color']
			#draw an arc with thickness of the radius
			pygame.draw.arc(
				self.screen,
				col,
				self.base_rect, 
				arc['start_angle'],
				arc['stop_angle'],
				self.radius/2)
			cx = self.base_rect.centerx
			cy = self.base_rect.centery
			#draw lines coming out of the center to make up for some of the bad graphics
			for theta in arange(arc['start_angle'],arc['stop_angle'],.00005):
				pygame.draw.line(self.screen, col, (cx,cy), (self.radius*cos(theta)+cx,-1*self.radius*sin(theta)+cy))

			#draw slice label
			font_slice = pygame.font.Font('DINOT-Bold.otf',30)
			words = font_slice.render(arc['label'],True, (0,0,0))
			font_raw = pygame.font.Font('DINOT-Bold.otf',20)
			data = font_raw.render(str(arc['val']),True, (0,0,0))

			pos = (cx + int(self.radius*cos((arc['start_angle']+arc['stop_angle'])/2.0)/2) - words.get_width()/2,
					cy - int(self.radius*sin((arc['start_angle']+arc['stop_angle'])/2.0)/2) - words.get_height()/2)
			pygame.draw.rect(self.screen, (col[0]+20,col[1]+20,col[2]+20), (pos[0],pos[1],words.get_width(),words.get_height()))
			self.screen.blit(words,pos)

			if self.raw:
				pygame.draw.rect(self.screen, (col[0]+20,col[1]+20,col[2]+20), (pos[0],pos[1]+40,data.get_width(),data.get_height()))
				self.screen.blit(data,(pos[0],pos[1]+40))

		pygame.display.update()

	def set_raw(self,b):
		self.raw=b
		self.draw()

	def in_arc(self,x,y):
		"""Determines which slice the point is in, with x and y as coordinates in the screen.
			Returns the label of the corresponding slice, or None is it doesn't correspond to any slice"""
		dx = x-self.base_rect.centerx
		dy = self.base_rect.centery-y
		hypotenuse = hypot(dx, dy)
		if hypotenuse<=self.radius:
			angle = atan2(dx,dy)
			#normalizing angle to weird pygame unit circles
			if angle<0:
				angle+=2*pi
			angle = 5*pi/2 - angle

			for arc in self.model.get_arcs():
				if arc['start_angle']<=angle<=arc['stop_angle']:
					return arc['label']
		
			return None

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
		if value<=0:
			raise ValueError('Data entry requires a positive value')
		elif label in self.data.keys():
			raise KeyError('That entry already exists')
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
		if self.data[label] + dv<=0:
			del self.data[label]
		else:
			self.data[label]+=dv
			self.raw_total+=dv

	def has_slice(self, label):
		return label in self.data.keys()

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
			d['val'] = self.data[t[0]]
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
	"""Creates the menu for wither modifying a slice or addinga  slice"""
	def __init__(self, pg, view, modifylabel=None,repeat=1):
		"""Creates a new TK window. Depending on whether modifylabel has a value or not, it
			will make a window for modification or adding"""
		self.main_window = t.Tk()
		self.main_window.title('Input Data')
		x=480 if modifylabel==None else 350
		self.main_window.geometry('+{}+500'.format(x))

		#attributes
		res_func = self.add if modifylabel==None else self.modify
		self.num_iter=repeat
		self.pg = pg
		self.view=view

		#variables gathered from window
		self.frame = t.Frame(self.main_window)
		if modifylabel==None:
			self.name_var = t.StringVar()
		else:
			self.name_var = modifylabel
		self.val_var = t.DoubleVar()

		#actaul containers
		if modifylabel==None:
			self.tbox = t.Entry(self.frame, width=10, textvariable=self.name_var, text = 'Name: ')
		else:
			self.tbox = t.Label(self.frame, text='Modifying \''+modifylabel+'\'\nInput amount to add to existing value (negative to subtract)\nIf the value becomes less than 0, the entry will be deleted')
		self.val = t.Entry(self.frame, width = 8, textvariable=self.val_var, text = 'Value: ')
		self.bt1 = t.Button(self.frame, text = 'Enter', command = res_func)
		#self.main_window.bind('<Return>', res_func)

		#create window
		self.tbox.pack(padx=10)
		self.val.pack(padx=10)
		self.bt1.pack(padx=10)
		self.frame.pack(padx=40)
		
		t.mainloop()

	def add(self):
		''' Method for adding slices, repeats if there should be multiple in succession

			If the data is invalid or a variable is missing, it will display an error message
			Eg: if the user enters nothing for the first data point, if the user enters a string for the value
		'''
		try:
			self.pg.add_slice(self.name_var.get(), self.val_var.get())
			self.pg.update_arcs()
			self.main_window.destroy()
			self.view.draw()
			if self.num_iter>1:
				input_menu(self.pg,self.view,repeat=self.num_iter-1)
		except (ValueError, KeyError) as e:
			tkMessageBox.showwarning(
			"!!Error!!",
			"Invalid Data\n"+str(e)
		)
	def modify(self):
		"""Method for modifying a slice, will not repeat"""
		try:
			self.pg.modify_slice(self.name_var, self.val_var.get())
			self.pg.update_arcs()
			self.main_window.destroy()
			self.view.draw()
		except (ValueError, KeyError) as e:
			tkMessageBox.showwarning(
			"!!Error!!",
			"Invalid Data\n"+str(e)
		)

class init_menu(object):
	"""Initial window for choosing how many initial data entries to input"""
	def __init__(self, pg, view):
		"""Creates a new window that allows the user to input a number for the number of entries to put in initially
			Calls the input_menu class with the repeat field filled in"""
		self.main_window = t.Tk()
		self.main_window.title('Input Data')
		self.main_window.geometry('+380+500')

		#class attributes
		self.pg = pg
		self.view=view

		#one data point to get
		self.frame = t.Frame(self.main_window)
		self.val_var = t.IntVar()

		#creates containers
		self.tbox = t.Label(self.frame, text='How many data entries would you like to input?')
		self.val = t.Entry(self.frame, width = 8, textvariable=self.val_var, text = 'Value: ')
		self.bt1 = t.Button(self.frame, text = 'Enter', command = self.enter_data)
		#self.main_window.bind('<Return>', res_func)

		#creates frame layout
		self.tbox.pack(padx=10)
		self.val.pack(padx=10)
		self.bt1.pack(padx=10)
		self.frame.pack(padx=40)
		
		t.mainloop()

	def enter_data(self):
		"""Method that makes the initial call to input_menu"""
		try:
			self.main_window.destroy()
			input_menu(self.pg, self.view,repeat=self.val_var.get())
			
		except (ValueError) as e:
			tkMessageBox.showwarning(
			"!!Error!!",
			"INITInvalid Data\n"+str(e)
		)
def deal_with_event(event,pie,screen):
		"""Handles events such as exiting, saving a screenshot, inputting a new entry, and modifying an existing entry"""
		if event.type == QUIT:
			return True
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				#input a new entry
				input_menu(pie, screen)
			elif event.key == pygame.K_s:
				#remove the commands
				pygame.draw.rect(screen.screen, (0,0,0), (0,0,1000,150))
				#screenshot
				pygame.image.save(screen.screen, "screenshot.jpeg")
				#redraw commands
				screen.draw()
			elif event.key == pygame.K_v:
				screen.set_raw(not screen.raw)
		if event.type == pygame.MOUSEBUTTONDOWN:
			#modify a slice (if the user clicks in the right place, otherwise this doesn't do anything)
			pos = pygame.mouse.get_pos()
			label = screen.in_arc(pos[0],pos[1])
			if label != None:
				input_menu(pie,screen,label)

if __name__ == '__main__':
	doctest.testmod()
	#creates the main Pie Graph object
	pg = PieGraph()
	pygame.init()
	view = Screen(pg, (1000, 1000))
	running = True
	menu = init_menu(pg, view)
	#run forever. or quit. if that's what you want.
	while running:
		for event in pygame.event.get():
			running = not deal_with_event(event,pg,view)
		time.sleep(float(1/30))
