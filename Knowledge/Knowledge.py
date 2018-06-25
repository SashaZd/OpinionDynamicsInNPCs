from .Source import Source
from .Bias import Bias
from .Topic import Topic
from .Article import Article

from collections import defaultdict

class Knowledge(object):
	"""docstring for Knowledge"""
	def __init__(self, world):
		super(Knowledge, self).__init__()
		self.sources = set([])
		self.topics = set([])
		self.articles = set([])
		self.world = world



	##################################################
	# Political Affliation
	##################################################
	def set_political_affiliation(self, affiliation=None):
		# 
		pass


	##################################################
	
	# def create_source(self, 
	# 			title: str, 
	# 			rating: Bias = Bias.UNKNOWN, 
	# 			url: str = ""):

	# 	source = self.world.get_source_by_title(title)
	# 	if not source: 
	# 		source = Source(title, rating, url)
	# 	return source

	def add_source(self, 
				source: Source):
		"""Media Source
			Add to the list of sources that this knowledge base is aware of
			Note: this does not mean that the NPC subscribes to the knowledge source
		""" 
		# if provided with the source instance
		if isinstance(source, Source):
			self.sources.add(source.id)

	def create_topic():
		pass


	def add_topic(self, 
				topic: Topic):
		"""Topic or Issue
			Topic of discussion 
			Until AllSides data, we're using: Media Bias and Immigration as sample topics
		"""
		if isinstance(topic, Topic):
			self.topics.add(topic.id)


	def add_article(self, 
				article: Article):
		"""A single article
			From a source/media with an associated bias
		"""
		if isinstance(article, Article):
			self.articles.add(article.id)

		# In case this is a new topic/source introduced, add the topic/source to the knowledge base
		for topic_id in (topic_id for topic_id in article.topics if topic_id not in self.topics):
			self.topics.add(topic_id)

		if article.source not in self.sources:
			self.add_source(article.source)


	def get_topic_by_title(self, title):
		"""Get topic 
			Return a specific topic/issue that matches the title.
		"""
		topic = self.world.get_topic_by_title(title)
		if topic.id in self.topics: 
			return topic
		else:
			return None


	def get_source_by_title(self, title):
		"""Get source 
			Return a source/media
		"""
		source = self.world.get_source_by_title(title)
		if source.id in self.sources: 
			return source
		else:
			return None


	def filter_articles_by_topic(self, topic):
		topic_id = topic.id
		return [self.world.get_article_by_id(article_id) for article_id in self.articles if topic_id in self.world.articles[article_id].topics]


	def __str__(self):
		return "KB:\n\tTopics: %s\n\tSources: %s\n\tArticles: %s"%(list(self.topics), len(self.sources), len(self.articles)) 

	def __repr__(self):
		return "KB:\n\tTopics: %s\n\tSources: %s\n\tArticles: %s"%(list(self.topics), len(self.sources), len(self.articles)) 






			


