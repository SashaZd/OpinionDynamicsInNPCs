import itertools

class Topic(object):
	"""docstring for Topic"""

	t_id = itertools.count().next
	topics = []

	def __init__(self, title, description="", url=""):
		super(Topic, self).__init__()
		self.title = title
		self.description = description
		self.url = url
		self.id = Topic.t_id()

		self.__class__.topics.append(self)


	@classmethod
	def get_topic_by_title(cls, title):
		possible_topics = [topic for topic in cls.topics if topic.title == title]
		if len(possible_topics)>0: 
			return possible_topics[0]
		else:
			return None
			

	@classmethod
	def get_topic(cls, id):
		return cls.topics[id]


	def __repr__(self):
		return "Topic: %s"%(self.title)

	def __str__(self):
		return "Topic: %s"%(self.title)

	def __eq__(self, other):
		return self.title == other.title

	def __hash__(self):
		return hash(self.title)


