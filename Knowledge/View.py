import random
from .Bias import Bias
from copy import deepcopy
from math import fabs
# To do work on modifying opinions to ratings


class View(object):
	"""NPC View

		View value is based originally on the bias class to which they're assigned. 

		arguments: 
			attitude: 	An agent's private views on a specific topic/article
			opinion: 	An agent's expressed opinions on a specific topic/article
			pri_thr: 	Private Acceptance threshold value. When the public opinion strength remains below pri_thr, 
						an agent will not change its opinion. No default value. 
			pub_thr: 	Public Compliance threshold value. When public opinion strength exceeds pub_thr, 
						an agent will choose public compliance. Default value=0.6
	"""

	def __init__(self,
				attitude: float = 0.00,
				opinion: float = 0.00,
				pri_thr: float = round(random.uniform(0.0, 1.0), 2),
				unc: float = 0.7):

		super(View, self).__init__()
		self.attitude = attitude		
		self.opinion = opinion		
		self.pri_thr = pri_thr		

		self.past_views = []

		# Calculated based on the attitude and opinion
		self.unc = round(random.uniform(0.0, 1.0), 2) 		  # default based on the original paper	# round(abs(self.attitude - self.opinion), 2)		
		self.pub_thr = 0.6,   # default based on the original paper


	@property
	def opinion(self):
		return round(self.__opinion, 2)


	@opinion.setter
	def opinion(self, opinion: float = 0.00):
		_op = round(opinion, 2)
		if _op > 1: 
			opinion = 1.0
		elif _op < -1:
			opinion = -1.0

		if not hasattr(self, 'opinion'): 
			self.__opinion = opinion

		elif opinion != self.__opinion:
			old_view = deepcopy(self)		# make a copy of the current view
			self.past_views.append(old_view)
			self.__opinion = opinion

		self.calculate_unc()


	@property
	def attitude(self):
		return round(self.__attitude, 2)

	@attitude.setter
	def attitude(self, attitude: float = 0.00):
		_att = round(attitude, 2)
		if _att > 1: 
			attitude = 1.0
		elif _att < -1:
			attitude = -1.0

		if not hasattr(self, 'attitude'): 
			self.__attitude = attitude

		elif attitude != self.__attitude:
			old_view = deepcopy(self)		# make a copy of the current view
			self.past_views.append(old_view)
			self.__attitude = attitude

			self.calculate_unc()


	def calculate_unc(self):
		self.unc = round(fabs(self.attitude - self.opinion), 2)


	def accept_opinion(self, other_opinion):
		self.attitude = other_opinion.attitude		
		self.opinion = other_opinion.opinion		
		self.unc = other_opinion.unc		
		self.pub_thr = other_opinion.pub_thr		
		self.pri_thr = other_opinion.pri_thr		

	def generate_random_view(self):
		""" Init Random View to Start
			Different from having no opinion, 
				or inheriting the biases of the people who first introduce the topic to you  
				This is for facts that are introduced to you in school (perhaps) 
				or that you don't get from any other person (i.e. the internet when you're doing a random search)
		"""
		self.attitude = round(random.uniform(-1.0, 1.0), 2)
		self.pri_thr = round(random.uniform(0.0, 1.0), 2)

		opinion = random.uniform(self.attitude - 0.6, self.attitude + 0.6)
		self.opinion = -1.0 if opinion < -1.0 else opinion
		self.opinion = 1.0 if opinion > 1.0 else opinion

		self.unc = round(random.uniform(0.0, 1.0), 2) 			# round(abs(self.attitude - self.opinion), 2)
		self.pub_thr = 0.6


	def generate_view_based_on_bias(self, bias: Bias):
		self.attitude = bias.value

		opinion = random.uniform(self.attitude - 0.7, self.attitude + 0.7)
		self.opinion = -1.0 if opinion < -1.0 else opinion
		self.opinion = 1.0 if opinion > 1.0 else opinion

		self.unc = round(random.uniform(0.0, 1.0), 2) 					# 0.7
		self.pub_thr = 0.6


	def get_opinion(self):
		return {
			'attitude': self.attitude,
			'opinion': self.opinion,
			'unc': self.unc,
			'pub_thr': self.pub_thr,
			'pri_thr': self.pri_thr,
		}

	def __eq__(self, other): 
		return self.attitude == other.attitude and self.opinion == other.opinion 	
							# and self.unc == other.unc

	def display_opinion_verbose(self):
		op = round(self.opinion, 2)
		op_verbose = Bias.get_bias_text(Bias.get_bias(op).value)
		return "%s (%s)" % (op_verbose, op)


	def display_verbose(self):
		att = round(self.attitude, 2)
		op = round(self.opinion, 2)
		att_verbose = Bias.get_bias_text(Bias.get_bias(att).value)
		op_verbose = Bias.get_bias_text(Bias.get_bias(op).value)
		unc = round(self.unc, 2)
		return "attitude: %s(%s) | opinion: %s(%s) | uncertainty: %s" % (att_verbose, att, op_verbose, op, unc)


	def display_change_from(self, other):
		# or (self.attitude == other.attitude and self.opinion == other.opinion):
		if self == other:
			return "Unchanged"

		att = "**%s**" % (other.attitude) if self.attitude != other.attitude else other.attitude
		op = "**%s**" % (other.opinion) if self.opinion != other.opinion else other.opinion
		unc = "**%s**" % (other.unc) if self.unc != other.unc else other.unc
		att_verbose = Bias.get_bias_text(Bias.get_bias(other.attitude).value)
		op_verbose = Bias.get_bias_text(Bias.get_bias(other.opinion).value)

		return "attitude: %s(%s) | opinion: %s(%s) | uncertainty: %s" % (att_verbose, att, op_verbose, op, unc)

		# return "attitude: %s | opinion: %s | uncertainty: %s" % (att, op, unc)

	def __str__(self):
		return "attitude: %s | opinion: %s | uncertainty: %s" % (round(self.attitude, 2), round(self.opinion, 2), round(self.unc, 2))

	def __repr__(self):
		return "attitude: %s | opinion: %s | uncertainty: %s" % (round(self.attitude, 2), round(self.opinion, 2), round(self.unc, 2))
