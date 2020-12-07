from .Bias import Bias
from .Source import Source
from .View import View

import itertools


class Article(object):
	"""Single article from a media source"""

	a_id = itertools.count().__next__
	articles = []

	def __init__(self, title, source, topic, description="", url=None, rating=Bias.UNKNOWN, opinion=False):
		super(Article, self).__init__()
		self.id = Article.a_id()
		self.title = title
		self.description = description
		self.url = url
		self.source = source.id
		self.is_an_opinion = opinion

		self.name = "the Article"

		self.rating = self.set_rating(rating)
		self.view = View(self.rating.value, self.rating.value)
		self.topic = self.add_topic(topic)

		self.__class__.articles.append(self)


	def add_topic(self, topic):
		if not hasattr(self, 'topic') or self.topic != topic.id:
			return topic.id


	@property
	def rating(self):
		return self._rating

	@rating.setter
	def rating(self, rating):
		rating = Bias.set_bias(rating)

		if not hasattr(self, 'rating'):
			self._rating = rating

		# Check whether the source it came from has the same rating
		# For instance, an Opinion piece from NYT may have different rating than NYT itself
		# If the rating of the source is different from this article then either
		# a) Change the rating of the source (if it's still unrated) OR
		# b) Add this as an additional rating to the source, implying that this source could have multiple ratings

		source = Source.get_source(self.source)

		if rating is not source.rating:
			# Unrated source, give it this first rating
			if source.rating is Bias.UNKNOWN:
				source.rating = self.rating

			# if the source is not unrated, it could be rated or mixed-rated and so we only add the
			# new rating to the other_ratings list
			elif self._rating is not source.rating:
				source.other_ratings.add(self.rating)


	@classmethod
	def get_article_by_title(cls, title):
		possible_articles = [article for article in cls.articles if article.title == title]
		if len(possible_articles) > 0:
			return possible_articles[0]
		else:
			return None

	@classmethod
	def filter_articles_by_source(cls, source):
		source_id = source.id
		return [article for article in cls.articles if article.source == source_id]


	@classmethod
	def filter_articles_by_rating(cls, rating):
		rating = Bias.set_bias_article(rating)
		print(("Searching for articles with rating: ", rating))
		return [article for article in cls.articles if article.rating is rating]


	@classmethod
	def filter_articles_by_topic(cls, topic):
		return [article for article in cls.articles if topic in article.topics]


	@classmethod
	def get_article(cls, id):
		return cls.articles[id]


	def set_rating(self, bias):
		return Bias.set_bias(bias)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def __hash__(self):
		return self.id

	def __str__(self):
		return "%s (%s)" % (self.title, self.rating)

	def __repr__(self):
		return "%s (%s)" % (self.title, self.rating)
