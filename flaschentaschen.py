#!/usr/bin/python3

import socket
from time import sleep
import sys, os

x = 5
y = 8

import sounddevice as sd
import math
import numpy as np



try:
    ip = sys.argv[1]
except:
    ip = '10.14.10.67'

class Canvas:
	def __init__(self, x, y):
		self.canvas_width = x
		self.canvas_height = y
		self.body = [[3*[0] for _ in range(y)]  for _ in range(x)]


	def point(self, xy,color=[255,255,255]):
		self.body[int(xy[0])][int(xy[1])] = color

	def line(self, a,b,color=[255,255,255]):
		self.point(a, color)
		self.point(b, color)
		x = a[0]
		y = a[1]
		if (a[0] < b[0]):
			xi = 1
			dx = b[0] - a[0]
		else:
			xi = -1
			dx = a[0] - b[0]

		if (a[1] < b[1]):
			yi = 1
			dy = b[1] - a[1]
		else:
			yi = -1
			dy = a[1] - b[1]
		
		if (dx > dy):
			ai = (dy - dx) * 2
			bi = dy * 2
			d = bi - dx
			while (x != b[0]):
				if (d >= 0):
					x += xi
					y += yi
					d += ai
				else:
					d += bi
					x += xi
				self.point([x,y], color)
		else:     
			ai = ( dx - dy ) * 2
			bi = dx * 2
			d = bi - dy
			while (y != b[1]):
				if (d >= 0):
					x += xi
					y += yi
					d += ai
				else:
					d += bi
					y += yi
				self.point([x, y], color)
		
	def square(self, a,b,color=[255,255,255]):
		for y in range(b[1] - a[1]):
			for x in range(b[0] - a[0]):
				self.body[a[0]+x+1][a[1]+y+1] = color

	def rainbow(self, stage):
		t = stage % 768
		if(stage < 256):
			color = [255-t,t,0]
			
		if(stage > 255 & stage < 512):
			t -= 256
			color = [0,255-t,t]

		if(stage > 511 & stage < 768):
			t -= 256
			color = [t,0,255-t] 

		return color

	def color(self, color):
		for y in range(self.canvas_height):
			for x in range(self.canvas_width):  
				self.body[x][y] = color

	def clear(self):
		self.color([0,0,0])

	def print(self):
		return self.body

class Screen:
	def __init__(self, ip, port, x, y):
		self.screen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.ip = ip
		self.port = port
		self.screen_width = x
		self.screen_height = y
		
	def mock_display(self, data, frame):
		string = ''
		for row in range(self.screen_height):
			for col in range(self.screen_width):
				if(data[col][row] != [0,0,0]):
					string += '#'
				else:
					string += '_'
			string += '\n'
		frame.set(string)

	def screen_matrix_to_bytes(self, data):
		result = bytearray()
		for row in range(self.screen_height):
			for col in range(self.screen_width):
				for color in range(3):
					result.append(data[col][row][color])
		return result
	
	def push(self, data):
		header = b"P6\n%d %d\n255\n" % (self.screen_width, self.screen_height)
		b = self.screen_matrix_to_bytes(data)
		self.screen.sendto(header + b, (self.ip, self.port))

from math import sin,floor, pi

def get_color_by_phase(phase:float)->list:
	max_bri = 127
	return[
		127+floor(max_bri*sin(phase)),
		0,
		127+floor(max_bri*sin(phase+3.14))
		#127+floor(-1*max_bri*sin(phase))
	]

def get_ip_list()->list:
	ips_strings = os.popen('sudo arp-scan --interface=wlp1s0 --localnet | grep Espressif | awk \'{split($0,a); print a[1]}\'').readlines()
	ips = [ip[:-1] for ip in ips_strings]
	print(ips)
	return ips

def get_static_ip_list() -> list:
	return ["10.14.10.18",
			"10.14.10.22",
			"10.14.10.66",
			"10.14.10.76"]

bins = [0]

samplerate = 44100.0
high=4000
low=50
columns = 10

delta_f = (high - low) / (columns - 1)
fftsize = math.ceil(samplerate / delta_f)
low_bin = math.floor(low / delta_f)

try:
	devnum = int([s for s in str(sd.query_devices()).split('\n')
					if s.find("monitor")!=-1][0].split(" ")[2])
except:
	"couldnt find proper monitor device."
def main():
	
	canvas = Canvas(x, y)
	c1 = Canvas(x, y)
	c2 = Canvas(x, y)

	#screen = Screen(ip, 1337, x, y)
	#screens = [Screen(ip,1337,x,y) for ip in get_static_ip_list()]

	i = 0
	period_s = 5

	s1 = Screen("10.14.10.22", 1337, x, y)

	def callback(indata, frames, time, status):
		if status:
			text = ' ' + str(status) + ' '
			print('\x1b[34;40m', text.center(columns, '#'),
				'\x1b[0m', sep='')
		if any(indata):
			magnitude = np.abs(np.fft.rfft(indata[:, 0], n=32))
			magnitude *= 5000 / fftsize
			#print(magnitude[0])
			global bins
			bins = [math.floor(m)%255 for m in magnitude][0:10]
		else:
			print('no input')

	with sd.InputStream(device=devnum, channels=1, callback=callback,
						blocksize=int(samplerate * 50 / 1000),
						samplerate=samplerate):
		while True:	
			try:
				#print(get_color_by_phase(i))
				print(bins)
				#canvas.color([bins[0],0,0])
				#[screen.push(canvas.print()) for screen in screens]
				for i in range (0,8):
					c1.line([0,i],[4,i],[bins[i],128-bins[i],0])
					
				s1.push(c1.print())
				sleep(0.03) 
				i+=0.02
			except (IndexError, ValueError):
				print("lel")
				pass


if __name__ == "__main__":
	main()
