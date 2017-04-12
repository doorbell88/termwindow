""" WINDOW
A module that will create a bordered window that matches the size of your
terminal window.  Plots ASCII characters in an [x][y] coordinate system.

"""

# Import modules
import os
from copy import deepcopy
from subprocess import Popen, PIPE
from termcolor import colored, cprint
from time import sleep

# Get size of terminal
#width
stdout = Popen('tput cols', shell=True, stdout=PIPE).stdout
WIDTH = int( stdout.read() )
#height
stdout = Popen('tput lines', shell=True, stdout=PIPE).stdout
HEIGHT = int( stdout.read() ) - 1

# Display of the window
class Window(object):
	def __init__(self, border_color=None, top='=', bottom='=', left='|', right='|'):
		self.width = WIDTH - 1
		self.height = HEIGHT - 2

		# Convenience constants
		self.mx = self.width
		self.my = self.height
		self.cx = self.width / 2
		self.cy = self.height / 2

		# For getting color arguments
		self.colors       = ['red','green','blue','cyan','magenta','yellow','white','grey']
		self.on_colors    = ['on_red','on_green','on_blue','on_cyan','on_magenta',
						     'on_yellow','on_white','on_grey']
		self.color_attrs  = ['bold','dark','underline','blink','reverse','concealed']

		# empty lists that will be filled with window content
		self.stage = []
		self.blank = []
		self.background = []

		# clear screen
		os.system('clear')

		# Hide the cursor
		self.hide_cursor()

		# create blank window stage
		for x in range(self.width+1):
			self.stage.append([" "] * (self.height+1))

		#draw window border
		for y in range(self.height+1):
			for x in range(self.width+1):
				#top
				pos = x % len(top)
				self.stage[x][self.height] = colored( top[pos], border_color )
				#bottom
				pos = x % len(bottom)
				self.stage[x][0] = colored( bottom[pos], border_color )
				#left 
				pos = y % len(left)
				self.stage[0][y] = colored( left[pos], border_color )
				#right
				pos = y % len(right)
				self.stage[self.width][y] = colored( right[pos], border_color )
	
		# make a copy of the blank, bordered background
		self.blank = deepcopy(self.stage)
		self.background = deepcopy(self.stage)

	# make cursor invisible
	def hide_cursor(self):
		os.system('echo "\x1b[?25l"')
		return

	# make cursor visible again
	def show_cursor(self):
		os.system('echo "\x1b[?25h"')
		return

	# show cursor and exit gracefully
	def exit(self):
		self.show_cursor()
		exit()

	# set background so self.erase() will just erase the foreground
	def set_background(self):
		self.background = deepcopy(self.stage)
		return

	# print the window in terminal
	def display(self):
		# Bring cursor back up to top left corner
		os.system('tput cup 0 0')
		# print
		for row in range(self.height+1):
			col_string = ''
			for col in range(self.width+1):
				col_string += self.stage[col][(self.height - row)]
			print col_string

	def _get_character_args(self, *args, **kwargs):
		# Blank variables to start
		color_arg = None
		on_color_arg = None
		character = '.'
		attrs_arg = []

		# get args
		for arg in args:
			if arg in self.colors:
				color_arg = arg
			elif arg in self.on_colors:
				on_color_arg = arg
			elif type(arg) == type('') and len(arg) == 1:
				character = arg

		# get kwargs
		color_arg = kwargs.get('color', color_arg)
		on_color_arg = kwargs.get('on_color', on_color_arg)
		attrs_arg = kwargs.get('attrs', attrs_arg)
		character = kwargs.get('character', character)

		return color_arg, on_color_arg, attrs_arg, character

	# plot a coordinate in a window list
	def plot_point(self, coordinate, *args, **kwargs):
		x = coordinate[0]
		y = coordinate[1]
		
		# get color arguments
		color_arg, on_color_arg, attrs_arg, character = \
		self._get_character_args(*args, **kwargs)

		if color_arg not in self.colors:
			color_arg = None
		if on_color_arg not in self.on_colors:
			on_color_arg = None
		if attrs_arg not in self.color_attrs:
			attrs_arg = None

		if 0 < x < self.width and 0 < y < self.height:
			try:
				self.stage[int(x)][int(y)] = colored(character,
												   color=color_arg,
												   on_color=on_color_arg,
												   attrs=attrs_arg)
			except:
				self.stage[int(x)][int(y)] = character
	
	# refresh a coordinate point back to its background
	def erase_point(self, coordinate):
		x = coordinate[0]
		y = coordinate[1]
		try:
			self.stage[x][y] = self.background[x][y]
		except:
			pass
	
	# refresh a coordinate point back to its background
	def delete_point(self, coordinate):
		x = coordinate[0]
		y = coordinate[1]
		try:
			self.stage[x][y] = self.blank[x][y]
		except:
			pass
	
	# generate a list of points inside a rectangular area defined by 2 corners
	def _define_area(self, c1, c2):
		x1, y1 = c1[0], c1[1]
		x2, y2 = c2[0], c2[1]
		x_range = [min([x1,x2]), max([x1,x2])+1]
		y_range = [min([y1,y2]), max([y1,y2])+1]
		area = []
		for x in range( x_range[0], x_range[1] ):
			for y in range( y_range[0], y_range[1] ):
				area.append( (x,y) )
		return area

	# plot a rectangular area defined by two corners
	def plot_area(self, c1, c2, *args, **kwargs):
		area = self._define_area(c1, c2)
		for coordinate in area:
			self.plot_point(coordinate, *args, **kwargs)

	# erase a rectangular area defined by two corners
	def erase_area(self, c1, c2):
		area = self._define_area(c1, c2)
		for coordinate in area:
			self.erase_point(coordinate)

	# erase a rectangular area defined by two corners
	def delete_area(self, c1, c2):
		area = self._define_area(c1, c2)
		for coordinate in area:
			self.delete_point(coordinate)

	# draw a multi-character "image"
	def draw(self, coordinate, image, *args, **kwargs):
		x = coordinate[0]
		y = coordinate[1]

		# Get an igore character (to avoid drawing blank spaces)
		ignore = kwargs.get('ignore', None)

		# list of lists
		if type(image) == type([0]) and type(image[0]) == type([0]):
			for j in range( len(image) ):
				for i in range( len(image[j][0]) ):
					if image[j][0][i] != ignore:
						self.plot_point( ((x+i), (y-j)), image[j][0][i], *args, **kwargs)
		# list of strings
		elif type(image) == type([0]) and type(image[0]) == type(''):
			for j in range( len(image) ):
				for i in range( len(image[j]) ):
					if image[j][i] != ignore:
						self.plot_point( ((x+i), (y-j)), image[j][i], *args, **kwargs)
		# string
		elif type(image) == type(''):
			for i in range( len(image) ):
				if image[i] != ignore:
					self.plot_point( ((x+i), y), image[i], *args, **kwargs)
		# invalid
		else:
			return
			
	# return True if inside the border, False otherwise
	def _in_bounds(self, x,y):
		if  int(x) > 0 and int(x) < self.width and \
			int(y) > 0 and int(y) < self.height:
				return True
		else:
			return False

	# get direction of 'a' (x or y) --> (+1 or -1)
	def _a_dir(self, a1,a2):
		if a2 - a1 > 0:
			a_dir = 1
		elif a2 - a1 < 0:
			a_dir = -1
		else:
			a_dir = 0

		return a_dir

	# Get endpoints for line segments, rays, and lines
	def _endpoints(self, f, a1,a2, domain='x', line='segment'):
		# plot line from (x1,y1) to (x2,y2)
		if line == 'segment':
			a_min = min([a1,a2])
			a_max = max([a1,a2])
			b_min = f(a_min)
			b_max = f(a_max)

		# begin at (a1,b1) and go through to edge of window			
		elif line == 'ray':
			# get a and b directions -- which way does ray extend
			a_dir = self._a_dir(a1,a2)

			# determine a_dir and b_dir
			if a_dir > 0:
				a_min = a1
				if domain == 'x':
					a_max = self.mx-1
				elif domain == 'y':
					a_max = self.my-1
			elif a_dir < 0:
				a_min = 1
				a_max = a1
			else:
				a_min = a1
				a_max = a1
			b_min = min( f(a_min), f(a_max) )
			b_max = max( f(a_min), f(a_max) )

		# line goes through from end-to-end
		else:
			a_min = 1
			if domain == 'x':
				a_max = self.mx-1
			elif domain == 'y':
				a_max = self.my-1
			b_min = f(a_min)
			b_max = f(a_max)

		return a_min, a_max, b_min, b_max

	# create a function for evaluating this specific slope-intercept
	def _f(self, x1,x2,y1,y2):
		# slope and y-intercept
		m = float((y2-y1)) / float((x2-x1))
		y0 = y1 - float(m * x1)

		# pass along to create a function in terms of x alone
		slope_intercept = [m, y0]
		def ret(x):
			m, y0 = slope_intercept
			y = m*x + y0
			return y
		return ret

	# plot a line given coordinates, character, line type, and step type
	def plot_line(self, p1, p2, *args, **kwargs):
		# get first coordinate
		(x1, y1) = p1

		# get line and step arguments
		line = kwargs.get('line', 'segment')
		step = kwargs.get('step', 'step')

		# define x2 and y2 if p2 is not a coordinate
		if p2 == 'vertical':
			x2 = x1
			y2 = y1 + 1
			line = 'line'
			step = 'step'
		elif p2 == 'horizontal':
			x2 = x1 + 1
			y2 = y1
			line = 'line'
			step = 'step'
		else:
			(x2, y2) = p2

		# get in order of min and max so range() works
		x_min = min(x1,x2)
		x_max = max(x1,x2)
		y_min = min(y1,y2)
		y_max = max(y1,y2)
		
		# create f(x) if x_domain is greater
		if (x_max - x_min) >= (y_max - y_min):
			f = self._f(x1,x2,y1,y2)
			x_min, x_max, y_min, y_max = self._endpoints(f, x1,x2, 'x', line)
			x_domain = range(x_min, x_max+1)
			for x in x_domain:
				y = f(x)
				if self._in_bounds(x,y):
					if step == 'step':
							self.plot_point( (x,y), *args, **kwargs ) 
					else:
						if int(f(x)) != int(f(x+1)):
							self.plot_point( (x,y), *args, **kwargs ) 

		# create f(y) if y_domain is greater
		elif (x_max - x_min) < (y_max - y_min):
			f = self._f(y1,y2,x1,x2)
			y_min, y_max, x_min, x_max = self._endpoints(f, y1,y2, 'y', line)
			y_domain = range(y_min, y_max+1)
			for y in y_domain:
				x = f(y)
				if self._in_bounds(x,y):
					if step == 'step':
							self.plot_point( (x,y), *args, **kwargs ) 
					else:
						if int(f(y)) != int(f(y+1)):
							self.plot_point( (x,y), *args, **kwargs ) 


# Thing to be drawn in the window
class Thing(object):
	def __init__(self, window, position, *args, **kwargs):
		self.window = window
		self.position = tuple(position)
		
		# Get color arguments
		colors       = ['red','green','blue','cyan','magenta','yellow','white','grey']
		on_colors    = ['on_red','on_green','on_blue','on_cyan','on_magenta',
					    'on_yellow','on_white','on_grey']
		color_attrs  = ['bold','dark','underline','blink','reverse','concealed']

		# get args
		self.color = None
		self.on_color = None
		for arg in args:
			if arg in colors:
				self.color = arg
			elif arg in on_colors:
				self.on_color = arg

		# get kwargs
		self.color = kwargs.get('color', self.color)
		self.on_color = kwargs.get('on_color', self.on_color)
		self.attrs = kwargs.get('attrs', None)
		self.image = kwargs.get('image', [['']])
		self.size = self._get_size()
		self.ignore = kwargs.get('ignore', None)
		self.direction = kwargs.get('direction', [0,0])
		self.speed = kwargs.get('speed', 1)

	# get size of Thing's image
	def _get_size(self):
		self.size = [0,0]
		image = self.image

		# list of lists
		if type(image) == type([0]) and type(image[0]) == type([0]):
			self.size[0] = len(self.image[0][0])
			self.size[1] = len(self.image)
		# list of strings
		elif type(image) == type([0]) and type(image[0]) == type(''):
			self.size[0] = len(self.image[0])
			self.size[1] = len(self.image)
		# string
		elif type(image) == type(''):
			self.size[0] = len(self.image)
			self.size[1] = 1
		# invalid
		else:
			return
			
	# get position, direction, and speed from arguments
	def _get_pds(self, *args, **kwargs):
		# new position, direction, and speed
		p2 = None
		d2 = None
		s2 = None
		
		# get args
		for arg in args:
			# tuple -- position
			if type(arg) == type(()):
				p2 = arg
			elif type(arg) == type([]):
				d2 = arg
			elif type(arg) == type(0):
				s1 = arg

		# get kwargs
		p2 = kwargs.get('position', p2)
		d2 = kwargs.get('direction', d2)
		s2 = kwargs.get('speed', s2)

		return p2, d2, s2

	# draw Thing's image
	def draw(self, *args, **kwargs):
		# get position, direction, and speed from *args, **kwargs
		p2, d2, s2 = self._get_pds(*args, **kwargs)
		if p2 is not None:
			self.position = p2
		if d2 is not None:
			self.direction = d2
		if s2 is not None:
			self.speed = s2

		window = self.window
		window.draw(self.position, self.image,
					color=self.color,
					on_color=self.on_color,
					attrs=self.attrs,
					ignore=self.ignore)

	# erase Thing's image at current position (refresh to background)
	def erase(self):
		self._get_size()
		window = self.window
		c1 = (self.position[0], self.position[1]+1)
		c2 = (self.position[0]+self.size[0], self.position[1]-self.size[1])
		window.erase_area(c1, c2)

	# erase current position, and draw on a new coordinate
	def place(self, coordinate):
		self.erase()
		self.position = coordinate
		self.draw()

	# move image from one location to another
	def move(self, *args, **kwargs):
		# get position, direction, and speed from *args, **kwargs
		p2, d2, s2 = self._get_pds(*args, **kwargs)

		# erase current image
		self.erase()

		# set any new kwargs given
		if d2 is not None:
			self.direction = d2
		if s2 is not None:
			self.speed = s2

		# if a new position is given draw there
		if p2 is not None:
			self.position = p2
		# otherwise, add the direction and speed to the previous position
		else:
			x = self.position[0]
			y = self.position[1]
			x += int( self.direction[0] * self.speed )
			y += int( self.direction[1] * self.speed )
			self.position = (x,y)

		self.draw()







