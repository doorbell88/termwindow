""" WINDOW
A module that will create a bordered window that matches the size of your
terminal window.  Plots ASCII characters in an [x][y] coordinate system.

"""

# Import modules
import os
import subprocess
from time import sleep
from copy import deepcopy
from termcolor import colored, cprint

# Get size of terminal
WIDTH = int( subprocess.check_output(['tput','cols']) )
HEIGHT = int( subprocess.check_output(['tput','lines']) ) - 1


# Display of the window
class Window(object):
	"""
	An object with a size equal to the size of the terminal window upon
	instantiation.  The Window has a colored border that can be customized.
	
	Points can be plotted using (x,y) coordinate tuples, where:
		(0,0) -- lower left corner of the border
		(1,1) -- lower left corner of the drawable area
		(self.width, self.height)     -- upper right corner of the border
		(self.width-1, self.height-1) -- upper right corner of the drawing area
	
	Some easy reference coordinate values:
		self.mx -- max x-value (same as self.width)
		self.my -- max y-value (same as self.height)
		self.cx -- center x-value
		self.cy -- center y-value
	
	Window also has methods for drawing lines and ASCII-text "images"

	"""

	def __init__(self, border_color=None, top='=', bottom='=', left='|', right='|'):
		"""
		Initialize Window
		
		Clears terminal window and sets the cursor to invisible.
		Draws a colored border, and creates 3 lists that embody the  x-y-space:
			
			self.stage      -- The actual space to be printed to terminal
			self.blank		-- A blank area that has only a border
			self.background -- The list that holds the background image
							   (when you erase a point, the background is shown)
							   This list must be set once you have your
							   background drawn on self.stage using
							   self.set_background()
		
		"""
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

	# set stage as background
	def erase(self):
		"""Return entire stage to background."""
		self.stage = deepcopy(self.background)
	
	# set stage as blank
	def delete(self):
		"""Make entire stage blank."""
		self.stage = deepcopy(self.blank)

	# make cursor invisible
	def hide_cursor(self):
		"""Sets cursor to invisible."""
		os.system('echo "\x1b[?25l"')
		return

	# make cursor visible again
	def show_cursor(self):
		"""Sets cursor back to visible."""
		os.system('echo "\x1b[?25h"')
		return

	# show cursor and exit gracefully
	def exit(self):
		"""Sets cursor visible and exits."""
		self.show_cursor()
		exit()

	# set background so self.erase() will just erase the foreground
	def set_background(self):
		"""Sets the background as what is currently shown on self.stage"""
		self.background = deepcopy(self.stage)
		return

	# print the window in terminal
	def display(self):
		"""Refreshes the image of the stage."""
		# Bring cursor back up to top left corner
		os.system('tput cup 0 0')
		# print
		for row in range(self.height+1):
			col_string = ''
			for col in range(self.width+1):
				col_string += self.stage[col][(self.height - row)]
			print col_string

	def _get_character_args(self, *args, **kwargs):
		"""Gets character, color, on_color, and attributes from *args, **kwargs"""
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
		"""Plots a character at an (x,y) coordinate of self.stage"""
		x = coordinate[0]
		y = coordinate[1]
		
		# get color arguments
		color_arg, on_color_arg, attrs_arg, character = \
		self._get_character_args(*args, **kwargs)

		if color_arg not in self.colors:
			color_arg = None
		if on_color_arg not in self.on_colors:
			on_color_arg = None

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
		"""Returns a coordinate to its background value."""
		x = int(coordinate[0])
		y = int(coordinate[1])
		try:
			self.stage[x][y] = self.background[x][y]
		except:
			self.stage[x][y] = ' '
	
	# refresh a coordinate point back to its background
	def delete_point(self, coordinate):
		"""Deletes a point on the stage (so it is a single space: ' ')."""
		x = int(coordinate[0])
		y = int(coordinate[1])
		try:
			self.stage[x][y] = self.blank[x][y]
		except:
			self.stage[x][y] = ' '
	
	# generate a list of points inside a rectangular area defined by 2 corners
	def _define_area(self, c1, c2):
		"""Returns a list containting all coordinates of a rectangular area
		given the coordinates of two opposite corners."""
		x1, y1 = c1[0], c1[1]
		x2, y2 = c2[0], c2[1]
		x_range = [min([x1,x2]), max([x1,x2])+1]
		y_range = [min([y1,y2]), max([y1,y2])+1]
		area = []
		for x in range( x_range[0], x_range[1] ):
			for y in range( y_range[0], y_range[1] ):
				area.append( (x,y) )
		return area

	# Draw image at each coordinate in a list of coordinates
	def plot_list(self, coordinate_list, *args, **kwargs):
		"""Draws image at each point in coordinate_list.
		This is useful for drawing something and then being able to clear
		or delete every point.
		"""
		# get character arguments
		color_arg, on_color_arg, attrs_arg, character = \
		self._get_character_args(*args, **kwargs)

		# get image (or character) to draw at each point
		image = kwargs.pop('image', character)
		delay = kwargs.get('delay', None)
		
		# draw image at each coordinate in the list
		for coordinate in coordinate_list:
			self.draw(coordinate, image, *args, **kwargs)
			if delay is not None:
				sleep(delay)
				self.display()

	# plot a rectangular area defined by two corners
	def plot_area(self, c1, c2, *args, **kwargs):
		"""Plot points in a rectangular area defined by the coordinates of two
		opposite corners of the rectangle"""
		area = self._define_area(c1, c2)
		for coordinate in area:
			self.plot_point(coordinate, *args, **kwargs)

	# erase a rectangular area defined by two corners
	def erase_area(self, c1, c2):
		"""Erase points in a rectangular area defined by the coordinates of two
		opposite corners of the rectangle"""
		area = self._define_area(c1, c2)
		for coordinate in area:
			self.erase_point(coordinate)

	# erase a rectangular area defined by two corners
	def delete_area(self, c1, c2):
		"""Delete points in a rectangular area defined by the coordinates of two
		opposite corners of the rectangle"""
		area = self._define_area(c1, c2)
		for coordinate in area:
			self.delete_point(coordinate)

	# draw a multi-character "image"
	def draw(self, coordinate, image, *args, **kwargs):
		"""Draw an ASCII-text image at a coordinate.
		An image can be of three forms:
		
		(1) String:
			image = 'example'

		(2) List of Strings:
			image = [' _--.-^---_____/',
					 '(__`______===== ',
					 '    V          \\']

		(3) List of Lists of Strings:
			image = [[' _--.-^---_____/'],
					 ['(__`______===== '],
					 ['    V          \\']]

		NOTE:  In forms (2) and (3), each string should be the same length.

		"""
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
			
	# return True if inside the defined area, False otherwise
	def is_in_area(self, coordinate, x_min, x_max, y_min, y_max):
		"""Returns True if coordinate is inside the area."""
		(x,y) = coordinate
		if x_min <= int(x) <= x_max and y_min <= int(y) <= y_max:
			return True
		else:
			return False
		
	# return True if inside the border, False otherwise
	def is_in_bounds(self, coordinate):
		"""Returns True if coordinate is inside the border."""
		return self.is_in_area(coordinate, 1, self.width-1, 1, self.height-1)

	# get direction of 'a' (x or y) --> (+1 or -1)
	def _a_dir(self, a1,a2):
		"""Returns direction of a1 and a2:
				+1 if a2 > a1
				-1 if a2 < a1
				0  if a2 == a1
		"""
		if a2 - a1 > 0:
			a_dir = 1
		elif a2 - a1 < 0:
			a_dir = -1
		else:
			a_dir = 0

		return a_dir

	# Get endpoints for line segments, rays, and lines
	def _endpoints(self, f, a1,a2, domain='x', line='segment'):
		"""Returns the domain values in order from smallest to largest.
		
		Used for plotting lines, rays, and line segments.
		
		"""
		# plot line from (x1,y1) to (x2,y2)
		if line == 'segment':
			a_min = min([a1,a2])
			a_max = max([a1,a2])

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

		# line goes through from end-to-end
		else:
			a_min = 1
			if domain == 'x':
				a_max = self.mx-1
			elif domain == 'y':
				a_max = self.my-1

		return a_min, a_max

	# create a function for evaluating this specific slope-intercept
	def _f(self, x1,x2,y1,y2):
		"""Returns a function in slope-intercept form which only takes one
		argument.

		Used in plotting lines, rays, and line segments.
		
		"""
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

	# define a line given coordinates, character, line type, and step type
	def _define_line(self, p1, p2, *args, **kwargs):
		"""Returns a list of coordinates in a line defined by points p1 and p2.

		If p2='vertical' or 'horiontal': a vertical or horizontal line will be
		drawn that passes through coordinate p1

		line can by 'line', 'segment', or 'ray'
			line='segment'  --  Plots from p1 to p2 [DEFAULT]
			line='ray'		--  Plots from p1 to the border
			line='line'		--  Plots from border to border
		
		step can be 'step' or ''
			step='step'		--  Plots every point along the way, appearing like
								a staircase. [DEFAULT]
			step=''			--	Plots just points along the defined line, so it
								doesn't look like a staircase, but the points
								are more spaced out.

		"""
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
		
		# create a list for holding all coordinates of line
		coordinate_list = []

		# create f(x) if x_domain is greater
		if (x_max - x_min) >= (y_max - y_min):
			f = self._f(x1,x2,y1,y2)
			x_min, x_max = self._endpoints(f, x1,x2, 'x', line)
			x_domain = range(x_min, x_max+1)
			for x in x_domain:
				y = f(x)
				if self.is_in_bounds((x,y)):
					if step == 'step':
							coordinate_list.append((x,y))
					else:
						if int(f(x)) != int(f(x+1)):
							coordinate_list.append((x,y))

		# create f(y) if y_domain is greater
		elif (x_max - x_min) < (y_max - y_min):
			f = self._f(y1,y2,x1,x2)
			y_min, y_max = self._endpoints(f, y1,y2, 'y', line)
			y_domain = range(y_min, y_max+1)
			for y in y_domain:
				x = f(y)
				if self.is_in_bounds((x,y)):
					if step == 'step':
							coordinate_list.append((x,y))
					else:
						if int(f(y)) != int(f(y+1)):
							coordinate_list.append((x,y))

		return coordinate_list
	
	# plot a line given coordinates, character, line type, and step type
	def plot_line(self, p1, p2, *args, **kwargs):
		"""Plots a line defined by points p1 and p2.

		If p2='vertical' or 'horiontal': a vertical or horizontal line will be
		drawn that passes through coordinate p1

		line can by 'line', 'segment', or 'ray'
			line='segment'  --  Plots from p1 to p2 [DEFAULT]
			line='ray'		--  Plots from p1 to the border
			line='line'		--  Plots from border to border
		
		step can be 'step' or ''
			step='step'		--  Plots every point along the way, appearing like
								a staircase. [DEFAULT]
			step=''			--	Plots just points along the defined line, so it
								doesn't look like a staircase, but the points
								are more spaced out.

		"""
		coordinate_list = self._define_line(p1, p2, *args, **kwargs)
		self.plot_list(coordinate_list, *args, **kwargs)

	# plot a line given coordinates, character, line type, and step type
	def erase_line(self, p1, p2, *args, **kwargs):
		"""Erases a line defined by points p1 and p2.

		If p2='vertical' or 'horiontal': a vertical or horizontal line will be
		drawn that passes through coordinate p1

		line can by 'line', 'segment', or 'ray'
			line='segment'  --  Plots from p1 to p2 [DEFAULT]
			line='ray'		--  Plots from p1 to the border
			line='line'		--  Plots from border to border
		
		step can be 'step' or ''
			step='step'		--  Plots every point along the way, appearing like
								a staircase. [DEFAULT]
			step=''			--	Plots just points along the defined line, so it
								doesn't look like a staircase, but the points
								are more spaced out.

		"""
		coordinate_list = self._define_line(p1, p2, *args, **kwargs)
		for coordinate in coordinate_list:
			self.erase_point( coordinate ) 

	# plot a line given coordinates, character, line type, and step type
	def delete_line(self, p1, p2, *args, **kwargs):
		"""Deletes a line defined by points p1 and p2.

		If p2='vertical' or 'horiontal': a vertical or horizontal line will be
		drawn that passes through coordinate p1

		line can by 'line', 'segment', or 'ray'
			line='segment'  --  Plots from p1 to p2 [DEFAULT]
			line='ray'		--  Plots from p1 to the border
			line='line'		--  Plots from border to border
		
		step can be 'step' or ''
			step='step'		--  Plots every point along the way, appearing like
								a staircase. [DEFAULT]
			step=''			--	Plots just points along the defined line, so it
								doesn't look like a staircase, but the points
								are more spaced out.

		"""
		coordinate_list = self._define_line(p1, p2, *args, **kwargs)
		for coordinate in coordinate_list:
			self.delete_point( coordinate ) 

	# draw an x-axis or y-axis
	def draw_axis(self, axis='x', position=0, *args, **kwargs):
		"""Draws a simple x- or y-axis."""
		if axis.lower() == 'x':
			x = 1
			y = position
			self.plot_line( (x,y), 'horizontal', '-', *args, **kwargs )
		elif axis.lower() == 'y':
			x = position
			y = 1
			self.plot_line( (x,y), 'vertical', '|', *args, **kwargs )
		else:
			return False

	# draw x and y axes and a 0 at the origin
	def draw_axes(self, origin, *args, **kwargs):
		"""Draws axes at the given origin."""
		# get origin
		(x,y) = origin
		
		# draw lines
		self.draw_axis('x', y, *args, **kwargs)
		self.draw_axis('y', x, *args, **kwargs)

		# draw origin
		self.plot_point( origin, '0', *args, **kwargs)

		# draw tic marks
		pass

	# generate a list of coordinates for plotting a function
	def graph_coordinates(self, function, origin=(0,0), scale=[2,1], bounds=None):
		"""
		Generate coordinate list for a function at the specified origin or in the
		specified x and y range.

		returns: coordinate_list, (x0,y0)

		"""
		# get origin and axis scale
		if type(bounds) == type([]) and len(bounds) == 4:
			x_min, x_max, y_min, y_max, = bounds
			scale_x = 1.0 * (x_max-x_min) / self.width
			scale_y = 1.0 * (y_max-y_min) / self.height
			x0 = -1.0 * (x_min / scale_x)
			y0 = -1.0 * (y_min / scale_y)
		else:
			(x0,y0) = origin
			[scale_x, scale_y] = scale

		# graph function (shifted and scaled)
		coordinate_list = []
		for i in range(self.width):
			try:
				x = (i - x0) * scale_x
				y = function(x)
				j = (y / scale_y) + y0
				coordinate_list.append((i,j))
			except:
				pass

		return coordinate_list, (x0,y0)

	# graph a function
	def graph(self, function, origin=(0,0), scale=[2,1],
			  bounds=None, axis='xy', axis_color=None, delay=None,
			  *args, **kwargs):
		"""
		Graph a function at the specified origin or in the specified
		x and y range.

		If delay is a non-zero number, then the graph will "animate" with the 
		specified delay after each "frame".

		returns: coordinate_list, (x0,y0)

		"""
		# get character arguments
		color_arg, on_color_arg, attrs_arg, character = \
		self._get_character_args(*args, **kwargs)

		# get image (or character) to draw at each point
		image = kwargs.pop('image', character)
		
		# generate list of coordinates for plotting
		coordinate_list, (x0,y0) = self.graph_coordinates(function,
														  origin=origin,
														  scale=scale,
														  bounds=bounds)
		
		# Drax axes (or axis)
		if axis is None:
			pass
		elif axis.lower() == 'x':
			self.draw_axis( axis='x', position=y0, color=axis_color )
		elif axis.lower() == 'y':
			self.draw_axis( axis='y', position=x0, color=axis_color )
		elif axis.lower() in ['xy', 'yx']:
			self.draw_axes( (x0,y0), color=axis_color )
		else:
			pass
		
		self.plot_list(coordinate_list, image, delay=delay, *args, **kwargs)

	# draw lines under a function (ex: for integral)
	def draw_under(self, function, origin=(0,0)):
		pass


# Thing to be drawn in the window
class Thing(object):
	"""
	An Object with methods that allow it to draw itself in a Window object.

	POSITION, DIRECTION, SPEED
	self.position can be plotted using (x,y) coordinate tuples, where:
		(0,0) -- lower left corner of the Window border
		(1,1) -- lower left corner of the drawable area
		(Window.width, Window.height)     -- upper right corner of the Window border
		(Window.width-1, Window.height-1) -- upper right corner of the drawing area
	self.direction is a list: [x_direction, y_direction]
	self.speed should be a positive integer
	
	COLORS
	self.color    -- Foreground text color
	self.on_color -- Background text color
	self.attrs    -- Text attributes ('bold', 'underline', 'blink',
									  'reverse', 'concealed', 'dark')
	self.ignore   -- Character to ignore when drawing self.image
					 (This avoids drawing dark rectangles around an object
					 that is not so rectangular)

	"""
	def __init__(self, window, position, *args, **kwargs):
		"""
		Initializes a Thing object given the window, position, and any arguments
		given (like color, direction, image, etc.)

		"""
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
		"""Returns the size of an image as a list [x-size, y-size]"""
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
		"""Get position, direction, and speed from *args, **kwargs"""
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
		"""Draw self.image at coordinate self.position"""
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
		"""Erase own image at coordinate self.position"""
		self._get_size()
		window = self.window
		c1 = (self.position[0], self.position[1]+1)
		c2 = (self.position[0]+self.size[0], self.position[1]-self.size[1])
		window.erase_area(c1, c2)

	# erase current position, and draw on a new coordinate
	def place(self, coordinate):
		"""Simply place the image at a new location."""
		self.erase()
		self.position = coordinate
		self.draw()

	# move image from one location to another
	def move(self, *args, **kwargs):
		"""Move the Thing.

		move() can be given a new position, direction, or speed.

		If move() is given no arguments, it will move the Thing from its current
		position to a new position defined by translating over by
			self.direction * self.speed

		"""
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







