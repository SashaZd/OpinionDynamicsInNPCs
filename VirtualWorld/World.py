
import simpy, arrow, random, itertools
from configs import *
from Knowledge.Knowledge import Knowledge
from Knowledge.Bias import Bias
from collections import defaultdict
from VirtualWorld.Town import Town

from NPC.Person import Person
from VirtualWorld.Organization import Organization

from setup_utils import *


class World(object):		# the sim will run for 50 years by default
	"""docstring for World"""
	current_date = arrow.get('%s-%s-%s' % (START_SIM_DATE[0], START_SIM_DATE[1], START_SIM_DATE[2]))

	def __init__(self, until_year=10):
		super(World, self).__init__()

		self.until_year = until_year
		self.knowledge = Knowledge(self)
		self.topics = Topic.topics
		self.sources = Source.sources
		self.articles = Article.articles
		self.discussions = []


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

	def get_article_by_id(self, article_id: int = 0):
		return self.articles[article_id]


	def get_topic_by_id(self, topic_id=0):
		return self.topics[topic_id]


	def get_source_by_id(self, source_id):
		return self.sources[source_id]


	def get_source_by_title(self, source_title):
		possible_source = [source for source in list(self.sources.values()) if source.title == source_title]
		if possible_source:
			return possible_source[0]
		else:
			return None


	def filter_articles_by_rating(self, rating: Bias):
		return [article for article in self.articles if article.rating is rating]

	def filter_articles_close_to_rating(self, rating: Bias):
		return [article for article in self.articles if (article.rating is Bias.set_bias(rating.value+0.5) or article.rating is Bias.set_bias(rating.value-0.5)) ]


	def filter_sources_by_rating(self, rating):
		return [source for source in self.sources if source.rating is rating]


	def get_npc(self, index):
		return self.population[index]

	def get_npc_by_name(self, name):
		return [person for person in self.population if person.name == name][0]


	def do_things(self):
		born = []
		while True: 		# self.env.now <= self.until_year:
			World.current_date = World.current_date.shift(days=1)
			day, month = World.current_date.day, World.current_date.month
			weekday = World.current_date.weekday() 			# returns day of the week, 0-6 0=Monday

			self.age_living_population(day, month)
			self.conceive_babies(day, month)

			if weekday <= 4: 
				self.go_to_school()

			yield self.env.timeout(1)


	def age_living_population(self, day, month):
		if hasattr(self, 'birthdays'):
			if (day, month) in self.birthdays.keys(): 
				# print "Aging: ", len(self.birthdays[(day, month)]), " children"
				for npc in self.birthdays[(day, month)]:
					npc.do_age()

					if npc.knowledge.reevaluate_flag: 
						print("Reevaluating Opinion: %s"%(npc.name))
						npc.knowledge.make_opinions_on_topics()
						npc.knowledge.get_opinion_for_knowledge()


	def conceive_babies(self, day, month):
		if (day, month) in self.conception_dates:
			for mother in self.conception_dates[(day, month)]: 
				mother.have_baby()


	def go_to_school(self):
		for school in self.organizations['school']:
			if random.random() > 0.6:
				school.teach_students_about_article()
				school.members_interact('classmate_school')



	@property
	def random_location(self):
		# return self.towns[random.choice(LOCATIONS)]
		return self.towns['Raleigh']


	# Sample with replacement
	def sample_wr(self, population, _choose=random.choice):
		while True:
			yield _choose(population)


	def conceive_babies(self, day, month):
		if (day, month) in self.conception_dates:
			for mother in self.conception_dates[(day, month)]: 
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


	def simulate_time(self, years=None):
		# until = 365*self.until_year
		# while until > 0: 
		# 	self.do_things()
		# 	until -= 1

		if not years: 
			years = self.until_year

		print("Simulating %s years" % (years))
		self.env = simpy.Environment()
		self.env.process(self.do_things())
		self.env.run(until=365 * years) 


	def show_population_by_generation(self):
		temp_pop = defaultdict(list)
		for person in self.population: 
			temp_pop[person.generation_num].append(person)

		for gen, pop in temp_pop.items(): 
			print("Generation: ", gen, "[", len(pop), "]")
			print(pop)
