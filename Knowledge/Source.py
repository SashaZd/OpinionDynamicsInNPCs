from Bias import Bias
import itertools

class Source(object):
	"""docstring for Source"""

	s_id = itertools.count().next
	sources = []

	def __init__(self, title, rating=Bias.UNKNOWN, url=""):
		super(Source, self).__init__()
		self.id = Source.s_id()
		self.title = title
		self.url = url
		self.other_ratings = set([])
		self.rating = rating

		# Add to list of sources
		self.__class__.sources.append(self)


	@classmethod
	def get_source_by_title(cls, title):
		possible_sources = [source for source in cls.sources if source.title == title]
		if len(possible_sources)>0: 
			return possible_sources[0]
		else:
			return None


	@classmethod
	def get_source(cls, id):
		return cls.sources[id]


	def set_rating(self, rating):
		return Bias.set_bias(rating)
		

	@property
	def rating(self):
		return self._rating

	@rating.setter
	def rating(self, rating):
		rating = Bias.set_bias(rating)

		if not hasattr(self, 'rating') or self._rating is Bias.UNKNOWN: 
			self._rating = rating
		
		elif rating not in self.other_ratings:
			self.other_ratings.add(self._rating)
			
	

	def __str__(self):
		return "Source: %s | %s"%(self.title, self.rating)

	def __repr__(self):
		return "Source: %s | %s"%(self.title, self.rating)

	def __eq__(self, other):
		return self.title == other.title

	def __hash__(self):
		return hash(self.title)

