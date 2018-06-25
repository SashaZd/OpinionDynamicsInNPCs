import simpy, arrow, random, itertools
from configs import *
from Knowledge.Knowledge import Knowledge
from collections import defaultdict
from VirtualWorld.Town import Town

from NPC.Person import Person
from VirtualWorld.Organization import Organization

from setup_utils import * 


class World(object):		# the sim will run for 50 years by default
	"""docstring for World"""
	current_date = arrow.get('%s-%s-%s'%(START_SIM_DATE[0],START_SIM_DATE[1],START_SIM_DATE[2]))

	def __init__(self, until_year=10):
		super(World, self).__init__()
		
		self.until_year=until_year
		self.knowledge = Knowledge(self)
		self.topics = Topic.topics
		self.sources = Source.sources
		self.articles = Article.articles


		self.towns = {}

		# Populations related attributes and properties
		self.population = []
		self.organizations = Organization.current_organizations
		# self.deceased_population = []
		self.person_id = 0
		self.birthdays = None
		self.conception_dates = defaultdict(list)

		self.setup_world()


	def setup_world(self):
		self.initilize_world_knowledge()

		# Initialize population and so on
		for town_name in TOWNS: 
			town = Town(town_name, self)
			self.towns[town_name] = town


		# Area 51 - Will be the default town
		# If a person leaves the simulation entirely (eg. dies, or gets kidnapped by aliens, 
		# then we move them to Area 51)
		self.towns["Area 51"] = Town("Area 51", self)
		self.towns["Area 51"].area_51_setup()


	def initilize_world_knowledge(self):
		# Gets the sources and their bias rankings from AllSides
		# Adds the sources to the world's knowledge base
		add_initial_media_sources(self.knowledge)
		add_initial_topics(self.knowledge)
		add_initial_articles(self.knowledge)

		# print "World knowledge has been initialized"
		# print "Topics/Issues: #Articles associated"
		# for topic in self.topics: 
			
		# 	print topics, 

	def get_article_by_id(self,
	                      article_id : int = 0):
		return self.articles[article_id]

	def get_topic_by_id(self, topic_id=0):
		return self.topics[topic_id]

	def get_source_by_id(self, source_id):
		return self.sources[source_id]

	def get_source_by_title(self, source_title):
		possible_source = [source for source in self.sources.values() if source.title == source_title]
		if possible_source: 
			return possible_source[0]
		else:
			return None


	def get_npc(self, id):
		return self.population[id]



	@property
	def random_location(self):
		# return self.towns[random.choice(LOCATIONS)]
		return self.towns['Raleigh']


	# Sample with replacement
	def sample_wr(self, population, _choose=random.choice):
		while True: yield _choose(population)

	def conceive_babies(self, day, month):
		if (day,month) in self.conception_dates:
			for mother in self.conception_dates[(day,month)]: 
				mother.have_baby()


	@property
	def birthdays(self):
		# if not hasattr(self, 'birthdays'): 
		# 	self.__birthdays = defaultdict(list)
		return self.__birthdays


	@birthdays.setter
	def birthdays(self, new_birth=None):
		if new_birth: 
			[day, month, baby] = new_birth
			if not hasattr(self, 'birthdays'): 
				self.__birthdays = defaultdict(list)
			
			self.__birthdays[(day, month)].append(baby)
		
		

	
				




