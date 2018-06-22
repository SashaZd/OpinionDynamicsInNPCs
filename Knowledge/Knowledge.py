from .Source import Source
from .Bias import Bias
from .Topic import Topic

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
	def set_political_affiliation(self, affiliation):
		# print "Affliation"
		pass



	##################################################



	def add_source(self, source):
		"""Media Source
			Add to the list of sources that this knowledge base is aware of
			Note: this does not mean that the NPC subscribes to the knowledge source
		""" 
		# if provided with the source instance
		if isinstance(source, Source):
			self.sources.add(source.id)

		# in case provided with just the source id 
		elif type(source) == int: 
			self.sources.add(source)


	def add_topic(self, topic):
		"""Topic or Issue
			Topic of discussion 
			Until AllSides data, we're using: Media Bias and Immigration as sample topics
		"""
		self.topics.add(topic.id)


	def add_article(self, article):
		"""A single article
			From a source/media with an associated bias
		"""
		self.articles.add(article.id)

		# In case this is a new topic/source introduced, add the topic/source to the knowledge base
		for topic_id in article.topics: 
			self.topics.add(topic_id)

		self.add_source(article.source)


	def get_topic_by_title(self, title):
		"""Get topic 
			Return a specific topic/issue that matches the title.
		"""
		for topic in list(self.topics):
			if topic.title == title: 
				return topic
		return None


	def get_source_by_title(self, title):
		"""Get source 
			Return a source/media
		"""
		for source in list(self.sources):
			if source.title == title: 
				return source
		return None


	def filter_articles_by_topic(self, topic):
		topic_id = topic.id
		return [self.world.get_article_by_id(article_id) for article_id in self.articles if topic_id in self.world.articles[article_id].topics]


	def __str__(self):
		return "KB:\n\tTopics: %s\n\tSources: %s\n\tArticles: %s"%(list(self.topics), len(self.sources), len(self.articles)) 

	def __repr__(self):
		return "KB:\n\tTopics: %s\n\tSources: %s\n\tArticles: %s"%(list(self.topics), len(self.sources), len(self.articles)) 






			


