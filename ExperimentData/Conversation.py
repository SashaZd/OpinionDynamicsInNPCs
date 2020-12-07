
class Conversation(object):
	"""docstring for Conversation"""

	def __init__(self, id):
		super(Conversation, self).__init__()
		self.id = id
		self.most_believable = []
		self.least_believable = []
		self.reasoning = []
		self.reasoning2 = []
		self.feedback = []
