from termwindow import Window, Thing
from random import randint, choice
from time import sleep
from copy import deepcopy
import os
import pdb

window = Window('cyan', left='_--', right='_--', top='|::', bottom='|::')

window.stage[0][0] = 'x'
window.stage[window.mx][0] = 'x'
window.stage[0][window.my] = 'x'
window.stage[window.mx][window.my] = 'x'

import math

def sin_x(x):
	return 1.0 * math.sin(1.0 * x)
def sin_x_over_x(x):
	return 1.0 * (math.sin(1.0 * x) / x) 

CL, orig = window.graph(sin_x, origin=(50,30), scale=[1.0/6, 1.0/6], 
	image='..', delay=0.001, color='magenta', axis_color='white')
window.draw_under(CL, character='|', color='blue', origin=orig, delay=0.001)

sleep(1)
window.erase()

bounds=[-10,25,-0.3,1.1]
CL, orig = window.graph(sin_x_over_x, bounds=bounds, connect_dots=True,
	image='*', delay=0.001, color='red', axis_color='white')
fill = window.draw_under(CL, character='|', color='yellow', origin=orig, delay=0.001)

window.display()
sleep(1)

window.erase_list(fill, delay=0.001)
window.plot_list(CL, '*', 'red')
window.display()
window.exit()
sleep(0.5)

for i in range(window.width):
	sin_pt = 12.0*math.sin(i/12.0)
	cos_pt = 12.0*math.cos(i/12.0)
	#if math.sin((i-6)/10.0) > math.cos((i-6)/10.0):
	if math.sin((i)) > math.sin((i-1)):
		window.draw((i, sin_pt + window.cy), '#*----', 'red')
		window.draw((i, cos_pt + window.cy), '@*----', 'yellow')
	else:
		window.draw((i, cos_pt + window.cy), '@*----', 'yellow')
		window.draw((i, sin_pt + window.cy), '#*----', 'red')
	sleep(0.001)
	window.display()
#window.background = deepcopy(window.stage)

window.exit()

def block_show(DELAY):
	#draw
	x1 = randint(-5, window.mx+5)
	x2 = randint(-5, window.mx+5)
	y1 = randint(-5, window.my+5)
	y2 = randint(-5, window.my+5)
	#erase
	x3 = randint(-5, window.mx+5)
	x4 = randint(-5, window.mx+5)
	y3 = randint(-5, window.my+5)
	y4 = randint(-5, window.my+5)
	# DRAW AND ERASE
	character = choice(['x','o','.','-','/','\\','#'])
	color = choice(['red', 'yellow', 'magenta', 'green', 'cyan', 'blue', 'white'])
	window.plot_area( (x1,y1), (x2,y2), character, color)
	window.erase_area( (x3,y3), (x4,y4) )
	#window.draw( (window.cx,window.cy), cat, ignore='R', color='white')

	sleep(DELAY)
	window.display()


cat = Thing(window, (window.cx, window.cy), color='white')

cat.image = [
				['            '],
				[' ^^       \ '],
				['("")~~~~~~/ '],
				['  (_______) '],
				['  /\    / \ '],
			]

cat.ignore = 'R'
cat.draw()
window.display()
sleep(1)

while True:
	cat.move(direction=[1,1], speed=1)
	window.display()
	sleep(0.2)

