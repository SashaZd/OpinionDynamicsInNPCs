import random
import names
import itertools
from configs import *
from collections import defaultdict
from collections import Counter
import itertools

from .Relationship import Relationship
from Knowledge.Knowledge import Knowledge

class Person(object):
	"""docstring for Person"""

	# Incremental ID for all persons of this class
	person_id = itertools.count().__next__
	living_population = []
	deceased_population = []


	def __init__(self, world, birth=None):
		super(Person, self).__init__()
		self.p_id = self.__class__.person_id()
		self.world = world
		self.events = []
		self.journal = []			# journal tracking all events in this Sim's life


		# Stores a list of Relationship objects, per person interacted with
		# current_relationships = relationships currently in progress 
		# past_relationships = if the person stops meeting this person, then after a set time, we demote them
		# Future goal: consider how to renew past relationship? Need to track that, but future goal.
		self.current_relationships = {}
		self.past_relationships = {}

		# Names and aliases for this person
		# Known aliases, in case of change of name during wedding, etc to track family?
		self.aliases = set()
		self.last_name = None
		self.first_name = None

		# Knowledge
		self.knowledge = Knowledge(self.world)


	@classmethod
	def get_population_living(cls):
		return cls.living_population

	@classmethod
	def get_population_deceased(cls):
		return cls.deceased_population

	@classmethod
	def get_npc(cls, id):
		return cls.living_population[id]


	def set_random_knowledge(self):
		pass

		
	def add_to_census(self):
		self.__class__.living_population.append(self)
		self.census_index = len(self.__class__.living_population)
		self.world.population.append(self) 
		self.world.birthdays = [self.birthdate.day, self.birthdate.month, self]


	def update_relationship(self, other, relationship_type):
		if other in self.current_relationships.keys():
			relationship = self.current_relationships[other]

		# Don't have a relationship with this person
		# Creating a new relationship with this person
		else: 
			relationship = Relationship(self, other)
			self.current_relationships[other] = relationship
		
		relationship.update_relationship(relationship_type, 1)



	def set_political_affiliation(self, affiliation):
		self.knowledge.set_political_affiliation(affiliation)


	##################################################
	# Everything to do with Names
	##################################################
	@property
	def name(self):
		return "%s %s"%(self.first_name, self.last_name)

	# Last Name
	@property
	def last_name(self):
		return self.__last_name


	@last_name.setter
	def last_name(self, last_name=None):
		""" Initializing a last name
		If given a last name, assume marriage/birth/etc and assign it to the sim
		If there are no parents, choose random last name, otherwise take the last name of the parents
		Uses Trey Hunner's Random Name Generator: http://treyhunner.com/2013/02/random-name-generator/
		""" 
		if not hasattr(self, 'last_name') and last_name: 
			self.__last_name = last_name

		# Changing the last name
		elif last_name and last_name != self.__last_name: 
			self.aliases.add(self.name)
			self.__last_name = last_name


	@property
	def first_name(self):
		return self.__first_name


	@first_name.setter
	def first_name(self, first_name=None):
		""" Changing existing first name
		If the person already has a name and is changing it, then add it to the aliases
		"""

		if not hasattr(self, 'first_name') and first_name: 
			self.__first_name = first_name

		elif first_name and first_name != self.first_name:
			self.aliases.add(self.name)
			self.__first_name = first_name


	def __str__(self):
		return "%s"%(self.name)

	def __repr__(self):
		return "%s"%(self.name)

		