import simpy, arrow, random, itertools
from configs import *
from Knowledge.Knowledge import Knowledge
from collections import defaultdict

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

		self.setup_world()


	def setup_world(self):
		self.initilize_world_knowledge()

		# Initialize population and so on


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

	def get_article_by_id(self, article_id=0):
		return self.articles[article_id]

	def get_topic_by_id(self, topic_id=0):
		return self.topics[topic_id]

	def get_source_by_id(self, source_id):
		return self.sources[source_id]
		
		

	
				




