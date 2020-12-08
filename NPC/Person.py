import random
import names
import itertools
from configs import *
from collections import defaultdict
from collections import Counter
import itertools

from .Relationship import Relationship
from Knowledge.Knowledge import Knowledge
from Knowledge.Bias import Bias


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

		self.generation_num = 0

		# Stores a list of Relationship objects, per person interacted with
		# current_relationships = relationships currently in progress 
		# past_relationships = if the person stops meeting this person, then after a set time, we demote them
		# Future goal: consider how to renew past relationship? Need to track that, but future goal.
		self.current_relationships = {}
		self.past_relationships = {}

		# self.partner = None
		self.spouse = None
		self.children = []

		# Sexually active at the age 18 
		self.flag_sexually_active = False

		# Names and aliases for this person
		# Known aliases, in case of change of name during wedding, etc to track family?
		self.aliases = set()
		self.last_name = None
		self.first_name = None

		# Academic details 
		# ToDo: Represent the knowledge or degree topic? If related to society topic it could 
		#  		represent an increase in the confidence of the topic 
		self.flag_education = False  # if the person is too old, or not interested in school, don't check
		self.flag_activate_school = False
		self.current_school = None
		self.past_schools = []
		self.flag_activate_university = False
		self.university = None
		self.past_universities = None
		self.events = []

		# Age for the person 
		# age is set as a @property. If it changes, it triggers flags in the person.
		self.age = 0		# increments every year 

		# Knowledge
		self.knowledge = Knowledge(self.world, self)



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
		if other in list(self.current_relationships.keys()):
			relationship = self.current_relationships[other]

		# Don't have a relationship with this person
		# Creating a new relationship with this person
		else: 
			relationship = Relationship(self, other)
			self.current_relationships[other] = relationship

		relationship.update_relationship(relationship_type, 1)


	def set_political_affiliation(self, bias: Bias):
		self.political_affiliation = bias
		self.knowledge.set_political_affiliation(bias)

	##################################################
	# Everything to do with Names
	##################################################
	@property
	def name(self):
		return "%s %s" % (self.first_name, self.last_name)

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

	##################################################
	# Aging and everything that comes with growing old
	##################################################

	def do_age(self):
		self.age += 1
		# Todo: Recalculate your political views?
		# print(self.name)
		self.knowledge.reevaluate_political_affiliation()

	@property
	def age(self):
		return self.__age

	@age.setter
	def age(self, age):
		"""Aging the person a year at a time. 

		@property age will allow for changes in flags... 
		Eg. allowing for school, work, sexually active behaviour, etc
		"""

		# if not hasattr(self, 'age') and age: 
		# 	self.__age = age

		if isinstance(age, int):
			self.__age = age


		# if self.town == self.world.towns['Area 51']:
		# 	return

		# print "Otherwise here.... ", self.town
		# Check if age is old enough for sexual partners
		if not self.flag_sexually_active and age > 18 and age <= 44: 
			self.flag_sexually_active = True

		if self.flag_sexually_active and age > 45: 
			self.flag_sexually_active = False

		if self.spouse and not self.pregnant and self.flag_sexually_active: 
			self.consider_having_baby()

		# if self.pregnant and self.world.current_date >= self.conception_date: 
		# 	self.have_baby()

		# Education Loops
		if age > 5 and age <= 17:  # 17 because we've not simulated universities yet
			if not self.current_school: 
				self.flag_education = True
				self.enroll_in_school()

		elif self.flag_education:
			self.flag_education = False
			self.unenroll_from_school()

		# if self.flag_education and not self.school: 
		# 	self.enroll_in_school()


		# if self.spouse and self.gender=="female" and not self.pregnant: 
		# 	# homosexual couple, toss coin to see who gets pregnant? 
		# 	# can be changed later
		# 	if self.spouse.gender == "female" and not self.spouse.pregnant: 
		# 		# should you get pregnant 
		# 		if random.random() < 0.5: 

		# 				self.pregnant_in_marriage()
		# 	else: 

	##################################################
	# Everything to do with Marriage and Babies
	##################################################

	@property
	def pregnant(self):
		if self.gender == "female": 
			return self.__pregnant
		else: 
			return False

	@pregnant.setter
	def pregnant(self, pregnant):
		if self.gender == "female":
			self.__pregnant = pregnant

	def have_baby(self):
		# old = len(self.children)
		from .Event import Birth
		born = Birth(self.world, self, self.spouse)
		self.pregnant = False
		current_date = self.world.current_date

		self.world.conception_dates[(current_date.day, current_date.month)].remove(self)

		self.children.append(born.baby)
		born.baby.add_to_census()
		# new = len(self.children)

		# born.birthdate = birthdate

	def get_pregnant(self):
		self.pregnant = True
		# print self.world.current_date, self, " is pregnant"

		conception_date = self.world.current_date 
		conception_date = conception_date.shift(days=270)
		self.world.conception_dates[(conception_date.day, conception_date.month)].append(self)

		journal_message = "Announcement - We're pregnant! ", self.name, self.spouse.name
		self.journal.append(journal_message)
		self.spouse.journal.append(journal_message)	


	def consider_having_baby(self):
		""" Some probability of having a baby 
		"""
		n_kids = 0
		if self.children: 
			n_kids = len([child for child in self.children if self in child.parents and self.spouse in child.parents])

		probability_of_a_child = 0.35 / (n_kids + 1)

		# print self, "Thinking about a baby", probability_of_a_child

		# Decided to have a child
		if random.random() < probability_of_a_child: 
			if self.gender == "female":
				self.get_pregnant()

			elif self.spouse.gender == "female":
				self.spouse.get_pregnant()

			else:
				print("Want to adopt, but no such feature in game yet")

	##################################################
	# Everything to do with Academia - Schools and Universities 
	##################################################

	# Possibility of enrolling in school -- some may choose not to? 
	# ToDo: Change probability of enrollment occurring from 1 to some percentage chance
	# Future: Could change this per region based on real stats? 
	# ToDo: Need to move this to the events class? 
	def enroll_in_school(self):
		from .Event import UpdateSchoolMembership

		# If there's a school
		if self.town.schools:
			chosen_school = random.choice(self.town.schools)
			enroll = UpdateSchoolMembership(self.world.current_date, self, "enroll", chosen_school)

		else: 
			print("%s district has no school to enroll in. Relocate?" % (self.town))


	def unenroll_from_school(self):
		from .Event import UpdateSchoolMembership
		unenroll = UpdateSchoolMembership(self.world.current_date, self, "unenroll")


	##################################################
	# Relationships with other people 
	##################################################

	def simple_interaction(self, group, relationship_type):
		"""Power up relationship with a person""" 
		# group_to_interact_with = list(set(group) - set([self]))

		for person in [person for person in group if person != self]: 
			self.update_relationship(person, relationship_type)


	def update_relationship(self, other, relationship_type):
		# Don't have a relationship with this person
		# Creating a new relationship with this person
		if other not in self.current_relationships.keys():
			self.current_relationships[other] = Relationship(self, other)

		self.current_relationships[other].update_relationship(relationship_type, 1)



	##################################################
	# Everything to do with Addressses and Locations 
	##################################################

	# To Do
	def relocate_home(self, town=None, house_number=None, with_household=[]):
		"""Relocation of Home
			Used to change the location of the Person's home 
			If the actual address changes - compare house_number and city only? 
			@param tuple address : (house_number, city)
			@param Person[] with_household : True (household moving with person) | False (moving out alone)
		""" 

		# If moving to another house in the same town
		# if town == self.town and house_number != self.house_number: 
		# 	clear


		# self.past_addresses.append("%s, %s"%(self.house_number, self.town.name))

		# if address != self.address: 
		# 	self.past_addresses.append(self.current_home)
		
		# if self.town != town:
		# 	town.find_unoccupied_home()

		pass



	# @property
	# def town(self):
	# 	# print "Getting town"
	# 	if not hasattr(self, 'town'):
	# 		self.__town = None
	# 	return self.__town
			


	# @town.setter
	# def town(self, town=None):
	# 	print "Setting town"
	# 	""" Initializing a last name
	# 	If given a last name, assume marriage/birth/etc and assign it to the sim
	# 	If there are no parents, choose random last name, otherwise take the last name of the parents
	# 	Uses Trey Hunner's Random Name Generator: http://treyhunner.com/2013/02/random-name-generator/
	# 	""" 
	# 	# if not hasattr(self, 'town'): 
	# 	self.__town = town

		# # Changing the last name
		# elif town and town != self.__town: 
		# 	self.aliases.add(self.name)
		# 	self.__town = town

		

		# else: 
		# 	print "Error! Use the relocate_home method to move independently or with household"


	def __str__(self):
		return "%s" % (self.name)

	def __repr__(self):
		return "%s" % (self.name)
