#!/usr/bin/python

#imports required
import RPi.GPIO as GPIO
import Adafruit_MCP3008
import time
import os
import spidev
import sys
import datetime
import subprocess as sp

#Global Variables
time_array = []
timer_array = []
pot_array = []
tempre_array =[]
light_array = []
values =[0]*8
stop_start = True
sleeptime=0.5
timer=0

#GPIO19/PIN35=reset
#GPIO26/PIN37=frequency
#GPIO16/PIN36=stop
#GPIO20/PIN38=display

#interrupt configured for the push buttons
def init_pushbuttons():
	GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def init_event_detect():
	GPIO.add_event_detect(19,GPIO.FALLING,callback=reset ,bouncetime=300)
    	GPIO.add_event_detect(26,GPIO.FALLING,callback=frequency,bouncetime=300)
    	GPIO.add_event_detect(16,GPIO.FALLING,callback=stop, bouncetime=300)
	GPIO.add_event_detect(20,GPIO.FALLING,callback=display,bouncetime=300)

#initialization of SPI for communication to the ADC
def init_spi(SPIMOSI, SPIMISO, SPICLK,SPICS):
	GPIO.setup(SPIMOSI, GPIO.OUT)
	GPIO.setup(SPIMISO, GPIO.IN)
	GPIO.setup(SPICLK, GPIO.OUT)
	GPIO.setup(SPICS, GPIO.OUT)

#when reset button is pressed, the timer,sleeptime and stop_start values are reset to default values
#and the command line is cleared
def reset(channel):
	global timer
	global sleeptime
	global stop_start
	timer =0.0
	sleeptime=0.5
	stop_start=True
	ter=sp.call('clear' ,shell=True)
	print('{:9} {:7} {:6} {:6} {:5}'.format("Time", "Timer", "Pot","Temp","Light"))
	time.sleep(1)

#when the frequency button is pressed, it toggles between 0.5, 1 and 2
def frequency(channel):
	global sleeptime
	if (sleeptime == 0.5):
      		sleeptime = 1
  	elif (sleeptime == 1):
      		sleeptime = 2
    	elif (sleeptime==2):
      		sleeptime = 0.5

#when the stop button is pressed, it toggles the stop_start between 
def stop(channel):
	global stop_start
	if (stop_start == True):
		stop_start=False
	else:
		stop_start=True

#display function used to display the Time, Timer, POT, TEMP, LIGHT
def display(channel):
	ter=sp.call('clear' ,shell=True)
	print('{:9} {:7} {:6} {:6} {:5}'.format("Time", "Timer", "Pot","Temp","Light"))
	for i in range (5):
		print('{:9} {:<7.2f} {:<3.1f} {:2} {:<3.0f} {:2} {:<3.0f} {:2}'.format(time_array.pop(), timer_array.pop(), pot_array.pop(),"V", tempre_array.pop(),"C",light_array.pop(),"%"))

def conversion(values):
	#Converts ADC value into LDR light percentage
	values[0] =(values[0]/float(970))*100
	values[0] = round(values[0],1)

	#Converts ADC to Voltage of POT
	values[1] = (values[1]*3.3/float(1023))
	values[1] = round(values[1],1)

	#Converts ADC to Tempreature
	values[2] = (values[2]*3.3)/float(1023)
	values[2] = (values[2]-0.5)/0.01
	values[2] = round(values[2],1)

def main():
	try:
		global timer

		# Call initialization
		GPIO.setmode(GPIO.BCM)
		init_pushbuttons()
		init_event_detect()
		
		# SPI pin definitions
		SPICLK=11
		SPIMISO = 9
		SPIMOSI = 10
		SPICS = 8
		
		# SPI configuration
		init_spi(SPIMOSI,SPIMISO,SPICLK,SPICS)
		mcp = Adafruit_MCP3008.MCP3008(clk=SPICLK, cs=SPICS, mosi=SPIMOSI, miso=SPIMISO)
		
		# Coloumn layout
		print('{:9} {:9} {:6} {:6} {:5}'.format("Time", "Timer", "Pot","Temp","Light"))
		start_time=datetime.datetime.now()

		while (True):
			if (stop_start == True):
				for i in range(3):
					values[i]=mcp.read_adc(i)

				# Converts ADC values
				conversion(values)
				current_time =datetime.datetime.now()
				time_array.append(current_time.strftime('%H:%M:%S'))

				# Stores current values in array
				timer_array.append(timer)
				timer+=sleeptime
				pot_array.append(values[1])
				tempre_array.append(values[2])
				light_array.append(values[0])
				
				# Print output values
				print('Xformat(time_array[-1], timer_array[-1], pot_array[-1],"V", tempre_array[-1],"C",light_array[-1], "%"))
				time.sleep(sleeptime)
			else:
				timer += sleeptime
				time.sleep(sleeptime)
	except KeyboardInterrupt:
		GPIO.cleanup()
	GPIO.cleanup()

if __name__ == '__main__':
	main()
