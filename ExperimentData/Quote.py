
class Quote(object):
	"""docstring for Quote"""
	def __init__(self, index, quote, respondent, type, codes):
		super(Quote, self).__init__()
		self.index = index
		self.quote = quote
		self.respondent = respondent
		self.type = type
		self.codes = codes
		