from enum import Enum


class Bias(Enum):
    LEFT = -1
    MODERATELY_LEFT = -0.75
    LEAN_LEFT = -0.5
    SLIGHTLY_LEAN_LEFT = -0.25
    CENTER = 0
    SLIGHTLY_LEAN_RIGHT = 0.25
    LEAN_RIGHT = 0.5
    MODERATELY_RIGHT = 0.75
    RIGHT = 1

    # Unknown rating or Mixed rating
    UNKNOWN = 0
    MIXED = 0

    # Based on Pew Research
    # http://www.people-press.org/quiz/political-typology/?utm_source=AdaptiveMailer&utm_medium=email&utm_campaign=17-10-24%20Typology&org=982&lvl=100&ite=1874&lea=398369&ctr=0&par=1&trk=
    # SOLID_LIBERAL 			= -1
    # OPPORTUNISTIC_DEM 	= -0.25
    # DISAFFECTED_DEM 	= -0.5
    # DEVOUT_DIVERSE		= -0.25
    # # CENTER 		= 0
    # NEW_ERA_ENTERPRISE	= 0.25
    # MARKET_SKEPTIC 		= 0.5
    # COUNTRY_FIRST_CONS	= 0.75
    # CORE_CONS 			= 1

    # Can be marked as Bystander, but doesn't contribute to the mean views
    # BYSTANDERS 			= 0

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

    @classmethod
    def set_bias(cls, bias):
        if isinstance(bias, Bias):
            return bias

        elif (isinstance(bias, int) or isinstance(bias, float)):
            return Bias(cls.round_to_nearest_bias(bias))

        elif type(bias) != str and type(bias) != str:
            print(bias)
            raise ValueError(
                "Expecting either a string (eg. \"Right\" or \"lean right\") or instance of class Bias (eg. Bias.RIGHT)")

        else:
            bias = bias.upper().strip()
            return {
                'UNKNOWN': Bias.UNKNOWN,
                'UNRATED': Bias.UNKNOWN,
                'LEFT': Bias.LEFT,
                'MODERATELY LEFT': Bias.MODERATELY_LEFT,
                'LEAN LEFT': Bias.LEAN_LEFT,
                'SLIGHTLY LEAN LEFT': Bias.SLIGHTLY_LEAN_LEFT,
                'CENTER': Bias.CENTER,
                'LEAN RIGHT': Bias.LEAN_RIGHT,
                'SLIGHTLY LEAN RIGHT': Bias.SLIGHTLY_LEAN_RIGHT,
                'MODERATELY RIGHT': Bias.MODERATELY_RIGHT,
                'RIGHT': Bias.RIGHT,
                'MIXED': Bias.MIXED
            }[bias]

    @classmethod
    def get_bias_text(cls, bias_value):
        # if isinstance(bias, Bias):
        return {
            -1: 'LEFT',
            -0.75: 'MODERATELY LEFT',
            -0.5: 'LEAN LEFT',
            -0.25: 'SLIGHTLY LEAN LEFT',
            0: 'CENTERIST',
            0.25: 'SLIGHTLY LEAN RIGHT',
            0.5: 'LEAN RIGHT',
            0.75: 'MODERATELY RIGHT',
            1: 'RIGHT'
        }[bias_value]

    # @classmethod
    # def set_bias_npc(cls, bias):
    # 	if isinstance(bias, Bias):
    # 		return bias

    # 	elif isinstance(bias, int):
    # 		return Bias(cls.round_to_nearest_bias_npc(bias))

    # 	elif type(bias) != str and type(bias) != str:
    # 		raise ValueError("Expecting either a string (eg. \"Right\" or \"lean right\") or instance of class Bias (eg. Bias.RIGHT)")

    # 	else:
    # 		bias = bias.upper().strip()
    # 		return {
    # 			'CENTER': Bias.CENTER,
    # 			'SOLID LIBERAL' : Bias.SOLID_LIBERAL,
    # 			'OPPORTUNISTIC DEM' : Bias.OPPORTUNISTIC_DEM,
    # 			'DISAFFECTED DEM' : Bias.DISAFFECTED_DEM,
    # 			'DEVOUT DIVERSE' : Bias.DEVOUT_DIVERSE,
    # 			'NEW ERA ENTERPRISE' : Bias.NEW_ERA_ENTERPRISE,
    # 			'MARKET SKEPTIC' : Bias.MARKET_SKEPTIC,
    # 			'COUNTRY FIRST CONS' : Bias.COUNTRY_FIRST_CONS,
    # 			'CORE CONS' : Bias.CORE_CONS
    # 		}[bias]

    @classmethod
    def round_to_nearest_bias(cls, val):
        val = round(val * 4) / 4
        if val > 1: 
            return 1 
        elif val < -1: 
            return -1    
        return val

    # @classmethod
    # def round_to_nearest_bias_npc(cls, val):
    # 	return round(val*4)/4

    @classmethod
    def get_bias(cls, val):
        return Bias(cls.round_to_nearest_bias(val))

    @classmethod
    def is_left(cls, val):
        """
        Checks to see if the opinion value is of type Bias.LEFT

        :param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -1.0
        :returns: True if -1.0 else False
        :raises ValueError: raises an exception if the value provided is not a float between -1.0 and 1.0

        """
        if not type(val) == float and val <= -1 and val >= 1:
            raise ValueError(
                "ValueError: is_left expects a float value between -1 and 1")

        return cls.get_bias(val) is Bias.LEFT

    @classmethod
    def is_leaning_left(cls, val):
        """
        Checks to see if the opinion value is of type Bias.LEAN_LEFT

        :param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -0.5
        :returns: True if -0.5 else False
        :raises keyError: raises an exception

        """
        if not type(val) == float and val <= -1 and val >= 1:
            raise ValueError(
                "ValueError: is_left expects a float value between -1 and 1")

        return cls.get_bias(val) is Bias.LEAN_LEFT

    @classmethod
    def is_center(cls, val):
        """
        Checks to see if the opinion value is of type Bias.LEAN_LEFT

        :param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -0.5
        :returns: True if 0.0 else False
        :raises keyError: raises an exception

        """
        if not type(val) == float and val <= -1 and val >= 1:
            raise ValueError(
                "ValueError: is_left expects a float value between -1 and 1")

        return cls.get_bias(val) is Bias.CENTER

    @classmethod
    def is_leaning_right(cls, val):
        """
        Checks to see if the opinion value is of type Bias.LEFT

        :param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -1.0
        :returns: True if 0.5 else False
        :raises ValueError: raises an exception if the value provided is not a float between -1.0 and 1.0

        """
        if not type(val) == float and val <= -1 and val >= 1:
            raise ValueError(
                "ValueError: is_left expects a float value between -1 and 1")

        return cls.get_bias(val) is Bias.LEAN_RIGHT

    @classmethod
    def is_right(cls, val):
        """
        Checks to see if the opinion value is of type Bias.LEAN_LEFT

        :param val: the value of the opinion or the attitude of the person that must be decoded into their Bias. Example -0.5
        :returns: True if 1.0 else False
        :raises keyError: raises an exception

        """
        if not type(val) == float and val <= -1 and val >= 1:
            raise ValueError(
                "ValueError: is_left expects a float value between -1 and 1")

        return cls.get_bias(val) is Bias.RIGHT
