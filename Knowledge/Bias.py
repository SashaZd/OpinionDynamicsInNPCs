from enum import Enum

class Bias(Enum):
	LEFT 		= -1
	LEAN_LEFT 	= -0.5
	CENTER 		= 0
	LEAN_RIGHT 	= 0.5
	RIGHT 		= 1

	# Unknown rating or Mixed rating
	UNKNOWN 	= 0
	MIXED 		= 0 


	@classmethod
	def set_bias(cls, bias):
		if type(bias) != str and type(bias) != str:
			if isinstance(bias, Bias):
				return bias
			else:
				raise ValueError("Expecting either a string (eg. \"Right\" or \"lean right\") or instance of class Bias (eg. Bias.RIGHT)")

		bias = bias.upper().strip()
		
		return {
			'UNKNOWN': Bias.UNKNOWN,
			'UNRATED': Bias.UNKNOWN,
			'LEFT': Bias.LEFT,
			'LEAN LEFT': Bias.LEAN_LEFT,
			'CENTER': Bias.CENTER,
			'LEAN RIGHT': Bias.LEAN_RIGHT,
			'RIGHT': Bias.RIGHT,
			'MIXED': Bias.MIXED
		}[bias]

	
	def is_left(self, val):
		"""
		Checks to see if the opinion value is of type Bias.LEFT
	
		:param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -1.0
		:returns: True if -1.0 else False
		:raises ValueError: raises an exception if the value provided is not a float between -1.0 and 1.0

		"""
		if not type(val) == float and val <= -1 and val >= 1: 
			raise ValueError("ValueError: is_left expects a float value between -1 and 1")

		return Bias(self.__class__.round_to_nearest_bias(val)) is Bias.LEFT
		
			

	def is_leaning_left(self, val):
		"""
		Checks to see if the opinion value is of type Bias.LEAN_LEFT
	
		:param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -0.5
		:returns: True if -0.5 else False
		:raises keyError: raises an exception

		"""
		if not type(val) == float and val <= -1 and val >= 1: 
			raise ValueError("ValueError: is_left expects a float value between -1 and 1")

		return Bias(self.__class__.round_to_nearest_bias(val)) is Bias.LEAN_LEFT


	def is_center(self, val):
		"""
		Checks to see if the opinion value is of type Bias.LEAN_LEFT
	
		:param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -0.5
		:returns: True if 0.0 else False
		:raises keyError: raises an exception

		"""
		if not type(val) == float and val <= -1 and val >= 1: 
			raise ValueError("ValueError: is_left expects a float value between -1 and 1")

		return Bias(self.__class__.round_to_nearest_bias(val)) is Bias.CENTER


	def is_leaning_right(self, val):
		"""
		Checks to see if the opinion value is of type Bias.LEFT
	
		:param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -1.0
		:returns: True if 0.5 else False
		:raises ValueError: raises an exception if the value provided is not a float between -1.0 and 1.0

		"""
		if not type(val) == float and val <= -1 and val >= 1: 
			raise ValueError("ValueError: is_left expects a float value between -1 and 1")

		return Bias(self.__class__.round_to_nearest_bias(val)) is Bias.LEAN_RIGHT
		
			

	def is_leaning_left(self, val):
		"""
		Checks to see if the opinion value is of type Bias.LEAN_LEFT
	
		:param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -0.5
		:returns: True if 1.0 else False
		:raises keyError: raises an exception

		"""
		if not type(val) == float and val <= -1 and val >= 1: 
			raise ValueError("ValueError: is_left expects a float value between -1 and 1")

		return Bias(self.__class__.round_to_nearest_bias(val)) is Bias.RIGHT


	@classmethod
	def round_to_nearest_bias(cls, val):
		return round(val*2)/2

	@classmethod
	def get_bias(cls, val):
		return Bias(cls.round_to_nearest_bias(val))




		