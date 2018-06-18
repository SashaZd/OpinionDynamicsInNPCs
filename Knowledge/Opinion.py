# To do work on modifying opinions to ratings 

class Opinion(object):
	"""docstring for Opinion"""
	def __init__(self, attitude=None, opinion=None, unc=None, pub_thr=None, pri_thr=None):
		super(Opinion, self).__init__()
		self.attitude = attitude		
		self.opinion = opinion		
		self.unc = unc		
		self.pub_thr = pub_thr		
		self.pri_thr = pri_thr		


	def set_opinion_from_opinion(self, opinion):
		self.attitude	 = opinion.attitude		
		self.opinion	 = opinion.opinion		
		self.unc		 = opinion.unc		
		self.pub_thr	 = opinion.pub_thr		
		self.pri_thr	 = opinion.pri_thr		


	def generate_random_opinion(self):
		""" Init Random Opinion to Start
			Different from having no opinion, 
				or inheriting the biases of the people who first introduce the topic to you  
				This is for facts that are introduced to you in school (perhaps) 
				or that you don't get from any other person (i.e. the internet when you're doing a random search)
		"""
		self.attitude 	= round(random.uniform(-1.0, 1.0), 2)
		
		opinion			= random.uniform(self.attitude-0.7, self.attitude+0.7)
		self.opinion	= -1.0 if opinion < -1.0 else opinion
		self.opinion	= 1.0 if opinion > 1.0 else opinion
		
		self.unc		 = round(abs(self.attitude - self.opinion), 2)
		self.pub_thr	 = 0.6
		self.pri_thr	 = round(random.uniform(0.0, 1.0), 2)

 
	def get_opinion(self):
		return {
			'attitude': self.attitude,
			'opinion': self.opinion,
			'unc': self.unc,
			'pub_thr': self.pub_thr,
			'pri_thr': self.pri_thr,
		}

	def __str__(self):
		return "attitude: %s | opinion: %s | unc: %s"%(self.attitude, self.opinion, self.unc)

	def __repr__(self):
		return "attitude: %s | opinion: %s | unc: %s"%(self.attitude, self.opinion, self.unc)








