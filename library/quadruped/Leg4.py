#!/usr/bin/env python
##############################################
# The MIT License (MIT)
# Copyright (c) 2016 Kevin Walchko
# see LICENSE for full details
##############################################

from __future__ import print_function
from __future__ import division
# import numpy as np
from math import sin, cos, acos, atan2, sqrt, pi, fabs
from math import radians as d2r
from math import degrees as r2d
# import logging
from .Servo import Servo

# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.ERROR)

class Servo(object):
	"""
	Servo hold the parameters of a servo, it doesn't talk to real servos. This
	class does the conversion between DH angles to real servo angles
	"""
	# _angle = 0.0  # current angle
	offset = 150.0  # angle offset default, see above for explaination
	minAngle = -150.0
	maxAngle = 150.0
	# ID = 0

	def __init__(self, minmax, offset):
		self.offset = offset
		self.minAngle = minmax[0]
		self.maxAngle = minmax[1]

	# @property
	# def angle(self):
	# 	"""
	# 	Returns the current servo angle
	# 	"""
	# 	return self._angle

	# @angle.setter
	def DH2Servo(self, angle):
		"""
		Sets the servo angle and clamps it between [limitMinAngle, limitMaxAngle].
		"""
		# saturates the angle if it is outside of the limits
		if self.minAngle > angle or angle > self.maxAngle:
			# raise Exception('@angle.setter {} > {} > {}'.format(self.minAngle, angle, self.maxAngle))
			print('@angle.setter error {} > {} > {}'.format(self.minAngle, angle, self.maxAngle))

			if self.minAngle > angle:
				angle = self.minAngle
			elif self.maxAngle < angle:
				angle = self.maxAngle

		return angle-self.offset


class LegException(Exception):
	pass

# length: how long is the link
# limits: min/max limits so we don't hit something
# offset: match servo frame and DH frame up
# data = {    # [ length, (limits), offset]
# 	'coxa': [28, [-45,45], 150],
# 	'femur': [90, [-90,90], 150],
# 	'tibia': [84, [-90,90], 150],
# 	'tarsus': [98, [-90,90], 150],
# 	'stand': [0, -110, -40, 90],
# 	'sit': [0,90,90,90]
# }


class Leg4(object):
	"""
	Leg class outputs the servo angles for some requested foot location (x,y,z)

	Leg knows:
	- leg dimensions
	- number of servos and their parameters/limits
	- fk/ik equations
	- sit/stand sequence
	"""
	# these are fixed by the 3D printing, not changing
	coxaLength = None
	tibiaLength = None
	femurLength = None
	tarsusLength = None
	# s_limits = []
	# s_offsets = []  # angle offsets to line up with fk

	# sit_raw = (150, 270, 100)
	# stand_raw = (150, 175, 172)
	sit_angles = None
	stand_angles = None

	def __init__(self, params):
		"""
		Each leg has 4 servos/channels
		"""

		# if not len(channels) == 4:
		# 	raise LegException('len(channels) != 4')

		# setup kinematics and servos
		self.servos = []
		for seg in ['coxa', 'femur', 'tibia', 'tarsus']:
			self.coxaLength = params[seg][0]
			self.servos.append(Servo(params[seg][1]), params[seg][2]))  # do i need to store these?

		self.sit_angles = params['sit']
		self.stand_angles = params['stand']

		# Servo.bulkServoWrite = True

		# # angle offsets to line up with fk
		# spl = data['servos per leg']  # do better? if tarsus in params?
		# for i in range(0, 4):  # 4 legs
		# 	channel = i*spl  # x servos per leg
		# 	if spl == 3:
		# 		self.legs.append(
		# 			Leg3([channel+1, channel+2, channel+3])
		# 		)
		# 	elif spl == 4:
		# 		self.legs.append(
		# 			Leg4([channel+1, channel+2, channel+3, channel+4])
		# 		)
		# 	else:
		# 		raise Exception('Engine() invalid number of servos per leg:', spl)

		# self.sit_angles = self.convertRawAngles(*self.sit_raw)
		# initAngles = self.convertRawAngles(*self.stand_raw)
		# self.stand_angles = initAngles
		# self.foot0 = self.fk(*initAngles)  # rest/idle position of the foot/leg
		# self.foot0 = self.fk = self.stand_angles

	def __del__(self):
		pass

	def sit(self):
		# TODO: animate this or slow down the motion so we don't break anything
		# self.moveFootAngles(*self.sit_angles)
		pass

	def stand(self):
		# TODO: animate this or slow down the motion so we don't break anything
		# self.moveFootAngles(*self.stand_angles)
		pass

	# def convertRawAngles(self, a, b, c):
	# 	return (a-self.s_offsets[0], b-self.s_offsets[1], c-self.s_offsets[2])

	def fk(self, t1, t2, t3, t4, degrees=True):
		"""
		Forward kinematics of the leg, note, default angles are all degrees.
		The input angles are referenced to the DH frame arrangement.
		"""
		l1 = self.coxaLength
		l2 = self.femurLength
		l3 = self.tibiaLength
		l4 = self.tarsusLength

		if degrees:
			t1 = d2r(t1)
			t2 = d2r(t2)
			t3 = d2r(t3)
			t4 = d2r(t4)

		x = (l1 + l2*cos(t2) + l3*cos(t2 + t3) + l4*cos(t2 + t3 + t4))*cos(t1),
		y = (l1 + l2*cos(t2) + l3*cos(t2 + t3) + l4*cos(t2 + t3 + t4))*sin(t1),
		z = l2*sin(t2) + l3*sin(t2 + t3) + l4*sin(t2 + t3 + t4),

		return (x, y, z,)

	def inverse(self, x, y, z, o=90, degrees=True):
		"""
		Azimuth angle is between x and w and lies in the x-y plane

				   ^ x
			 w     |
			   \   |
			 l1 \  |
				 \ |
				  \|
		<----------+ (z is out of the page - right hand rule)
		y

		Most of the robot arm move in the plane defined by w-z

		^ z      l3
		|      o-----o
		|     /       \ l4
		|    / l2      E
		|   /
		+--o-------------> w
		 l1

		l1: coxa
		l2: femur
		l3: tibia
		l4: tarsus

		All joint angles returned are in degrees: (t1, t2, t3, t4)
		"""
		def cosinelaw(a, b, c):
			# cosine law only used by this function
			# cos(g) = (a^2+b^2-c^2)/2ab
			return acos((a**2+b**2-c**2)/(2*a*b))

		l1 = self.coxaLength
		l2 = self.femurLength
		l3 = self.tibiaLength
		l4 = self.tarsusLength

		t1 = atan2(y, x)

		if degrees:
			o = o*pi/180

		w = sqrt(x**2 + y**2) - l1
		j4w = w + l4*cos(o)
		j4z = z + l4*sin(o)
		r = sqrt(j4w**2 + j4z**2)
		g1 = atan2(j4z, j4w)
		g2 = cosinelaw(l2, r, l3)
		t2 = g1+g2

		t3 = pi+cosinelaw(l2, l3, r)

		j2w = l2*cos(t2)
		j2z = l2*sin(t2)
		c = sqrt((w-j2w)**2 + (z-j2z)**2)
		t4 = pi+cosinelaw(l3, l4, c)

		if degrees:
			t1 *= 180/pi
			t2 *= 180/pi
			t3 *= 180/pi
			t4 *= 180/pi

		return (t1, t2, t3, t4)

	def generateServoAngles(self, footLoc):
		"""
		This is a bulk process and takes all of the foot locations for an entire
		sequence of a gait cycle. It handles all legs at once.

		footLoc: locations of feet from gait
		[
			[id, leg, pos], ...
		]

		[   step0      step1   ...
			[(x,y,z), (x,y,z), ...] # leg0
			[(x,y,z), (x,y,z), ...] # leg1
			...
		]

		return
		[   step 0          step 1         ...
			[[t1,t2,t3,t4], [t1,t2,t3,t4], ...] # leg0
			[[t1,t2,t3,t4], [t1,t2,t3,t4], ...] # leg1
			...
		]
		"""
		# TODO: fix this to handle N legs, right now it only does 4

		# angles = []
		# for _ in len(footLoc)  # this is equal to the number of feet
		# 	angles.append([])
		angles = [[], [], [], []]

		for a,b,c,d in zip(*footLoc):
			# calculate the inverse DH angles
			a = self.inverse(*a)
			b = self.inverse(*b)
			c = self.inverse(*c)
			d = self.inverse(*d)

			# correct DH for servo mounting and double check servo limits
			angles[0].append(self.servos[0].DH2Servo(a))
			angles[1].append(self.servos[1].DH2Servo(b))
			angles[2].append(self.servos[2].DH2Servo(c))
			angles[3].append(self.servos[3].DH2Servo(d))

		return angles

	def moveFoot(self, x, y, z):
		"""
		generates servo angles to move the foot to coordinates [x,y,z]. This
		is individual and not intended for walking, but something else.
		"""
		pass

	def getNeutralPos(self):
		return self.forward(*self.stand)

	# 	try:
	# 		# a, b, c = self.ik(x, y, z)  # inverse kinematics
	# 		# angles = [a, b, c]
	# 		angles = self.ik(x, y, z)  # inverse kinematics
	# 		# return angles
	# 		if angles is None:
	# 			print('something bad')
	# 			return
	# 		# print('angles: {:.2f} {:.2f} {:.2f}'.format(*angles))
	# 		for i, servo in enumerate(self.servos):
	# 			# print('i, servo:', i, servo)
	# 			angle = angles[i]
	# 			# print('servo {} angle {}'.format(i, angle))
	# 			servo.angle = angle
	# 		return angles
	#
	# 	except Exception as e:
	# 		print (e)
	# 		raise
	#
	# def moveFootAngles(self, a, b, c):
	# 	"""
	# 	Attempts to move it's foot to coordinates [x,y,z]
	# 	"""
	# 	try:
	# 		for servo, angle in zip(self.servos, (a, b, c)):
	# 			servo.angle = angle
	#
	# 	except Exception as e:
	# 		print('Leg::moveFootAngles() error:', e)
	# 		raise

	# def reset(self):
	# 	# self.angles = self.resting_position
	# 	self.move(*self.foot0)
