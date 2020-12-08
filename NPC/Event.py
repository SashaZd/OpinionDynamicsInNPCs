import itertools
from .Person import Person
from VirtualWorld import World
from Knowledge.Article import Article
from Knowledge.Source import Source
from Knowledge.Discussion import Discussion
from Knowledge.View import View
from Knowledge.Topic import Topic
import random
from configs import *
import names
from copy import deepcopy

from Knowledge.Bias import Bias


class Event(object):
	"""parent class for all the Events
	Allows ability to add details of the event to a journal maintained
	"""
	e_id = itertools.count().__next__

	def __init__(self, date, participants=[]):
		super(Event, self).__init__()
		self.id = Event.e_id()
		self.date = date
		self.participants = set(participants)

	def add_participant(self, participant):
		if not isinstance(participant, Person): 
			return 

		self.participants.add(participant)
		if self not in participant.events:
			participant.events.append(self)

	def add_to_journal(self, participant, message):
		if not isinstance(participant, Person): 
			return 
		if participant not in self.participants:
			self.add_participant(participant)
		participant.journal.append("%s - %s " % (self.date.format('DD-MM-YYYY'), message))


class UpdateSchoolMembership(Event):
	"""Enrolling in school"""
	def __init__(self, date, child, membership="enroll", school=None):
		super(UpdateSchoolMembership, self).__init__(date)
		self.add_participant(child)
		self.child = child
		self.school = school

		if membership == "enroll":
			self.enroll()

		else:
			self.unenroll()			


	def enroll(self):
		# Enroll
		self.child.current_school = self.school
		self.child.flag_activate_school = True
		self.school.enroll_student(self.child)

		# Child/Student's journal event updated
		enrolling_message = "Enrolled in %s School at age %s" % (self.school.name, self.child.age)
		self.add_to_journal(self.child, enrolling_message)
		self.child.events.append(self)

	def unenroll(self):

		# Child/Student's journal event updated
		unenrolling_message = "Graduated from %s School at age %s" % (self.child.current_school.name, self.child.age)
		self.add_to_journal(child, unenrolling_message)
		self.child.events.append(self)

		# Unenroll
		self.child.flag_activate_school = False
		self.child.current_school.unenroll_student(self.child)
		self.child.past_schools.append(self.child.current_school)
		self.child.current_school = None


class Birth(Event):
	"""docstring for Birth"""
	def __init__(self, world, mother=None, father=None, date=None):
		super(Birth, self).__init__(world.current_date)
		self.world = world
		self.baby = Person(world, self)
		self.baby.father = father
		self.baby.mother = mother

		# because the biological parents may be different if adopted?
		self.baby.parents = [father, mother]
		self.date = self.world.current_date

		self.birthdate = date if date else self.world.current_date

		self.gender = None

		self._set_baby_name()
		self.set_sexual_preference()
		self.set_inherited_attr()

		parent_message = []

		if mother:
			self.baby.generation_num = mother.generation_num+1
			self.baby.birth_location = mother.town
			self.baby.town = mother.town
			self.baby.town.add_citizen(self.baby, mother.house_number)
			parent_message.append("My mother is %s." % (mother.name))

			# Mother's Journal
			self.add_to_journal(mother, "Had child with %s. Decided to name baby, %s" % (father.name, self.baby.name))
			mother.events.append(self)


		if father:
			parent_message.append("My father is %s" % (father.name))

			# Father's Journal
			self.add_to_journal(father, "Had child with %s. Decided to name baby, %s" % (mother.name, self.baby.name))
			father.events.append(self)


		if not father and not mother:
			self.baby.birth_location = self.world.towns['Area 51']
			self.baby.town = self.world.towns['Area 51']
			self.baby.town.add_citizen(self.baby)
			# print(self.baby.town)


		elif not mother and not father:
			parent_message.append("I had no parents.")

		birth_journal_entry = "I was born on %s. %s" % (self.date, ''.join(parent_message))
		self.add_to_journal(self.baby, birth_journal_entry)
		self.baby.events.append(self)

		self.set_biases(mother, father)
		

	# Birthdate: if unknown, set to current date
	@property
	def birthdate(self):
		return self.baby.birthdate

	@birthdate.setter
	def birthdate(self, birthdate=None):
		if hasattr(self, 'birthdate'):
			if birthdate != self.baby.birthdate: 		# changing the year to age?
				# Remove from older birthday list in the world (used for aging)
				# old_birthday = (self.baby.birthdate.day,self.baby.birthdate.month)
				# if old_birthday in self.world.birthdays and self.baby in self.world.birthdays[old_birthday]:
				# 	self.world.birthdays[old_birthday].remove(self.baby)
				self.baby.birthdate = birthdate

		elif birthdate:
			self.baby.birthdate = birthdate			# take the date from the simulation?

		self.baby.age = abs(self.baby.birthdate - self.world.current_date).days / 365
		self.date = birthdate

	# Everything reg. the Name
	def _set_baby_name(self):
		self.first_name = None
		self.last_name = None

	# Last Name
	@property
	def last_name(self):
		return self.baby.last_name


	@last_name.setter
	def last_name(self, last_name=None):
		""" Initializing a last name
		If given a last name, assume marriage/birth/etc and assign it to the sim
		If there are no parents, choose random last name, otherwise take the last name of the parents
		Uses Trey Hunner's Random Name Generator: http://treyhunner.com/2013/02/random-name-generator/
		"""
		if not hasattr(self.baby, 'last_name'):
			if self.baby.father:
				self.baby.last_name = self.baby.father.last_name
			elif self.baby.mother:
				self.baby.last_name = self.baby.mother.last_name
			else:
				self.baby.last_name = names.get_last_name()


	# First Name
	@property
	def first_name(self):
		return self.baby.first_name

	@first_name.setter
	def first_name(self, first_name=None):
		""" Initializing a last name
		If no name from before, then assign a name from the random name generator
		If changing your name, then add to known aliases
		Uses Trey Hunner's Random Name Generator: http://treyhunner.com/2013/02/random-name-generator/
		"""
		# if not hasattr(self.baby, 'first_name'):
		if not first_name:
			self.baby.first_name = names.get_first_name(gender=self.baby.gender)
		else:
			self.baby.first_name = first_name

	# Everything reg. Gender
	@property
	def gender(self):
		return self.baby.gender


	@gender.setter
	def gender(self, gender=None):
		"""allows the gender to be set only during birth"""
		if not hasattr(self.baby, 'gender') or not self.baby.gender:
			self.baby.gender = random.choice(POSSIBLE_GENDERS)

		if self.baby.gender == "female":
			self.baby.pregnant = False

		# 	self.baby.gender = self.baby.gender


	# Inherited attributes during birth
	# Includes physical attributes from the parents (if they exist) or random (if they don't)
	# In our case that could also include knowledge of topics/rules? Maybe introduce these at a later age? Unsure?
	# May need to define topics with age limits? On when they are discussed?
	# Otherwise we may get 5yr olds debating the death penalty during kindergarten
	def set_inherited_attr(self):
		"""Inherited Physical Characteristics
		Setting inherited physical, or other characteristics
		"""
		pass


	def set_sexual_preference(self):
		"""Setting Sexual Preferences: Randomly at the moment
		Using the statistics from Wikipedia's Demographics of Sexual Orientation: https://en.wikipedia.org/wiki/Demographics_of_sexual_orientation
		Demographics from the United States used....
		Thought: Eventually, could change the statistics based on regional preferences?
		"""
		chance = random.random()
		if chance <= 0.017:
			self.baby.sexual_preference = 'homosexual'
		elif chance <= 0.035:
			self.baby.sexual_preference = 'bisexual'
		else:
			self.baby.sexual_preference = 'heterosexual'


	def set_biases(self, mother: Person = None, father: Person = None):
		""" Some inherent biases that you inherit
		"""
		articles = set([])
		if mother: 
			[articles.add(a_key) for a_key in mother.knowledge.articles.keys()]
			# articles.add(tuple())

		if father: 
			[articles.add(a_key) for a_key in father.knowledge.articles.keys()]

		if len(articles) >= 1:
			sel_num = random.randint(1, len(articles))
			selected_knowledge = random.sample(articles, sel_num)
			for article_id in selected_knowledge:   
				article = self.world.get_article_by_id(article_id)
				self.baby.knowledge.add_article(article)



class Marriage(Event):
	""" Marriage Event
		Marries two people, and changes their last names (sometimes) accordingly
		Also adds a marriage event to the person's journal.
		Can also decide on a child policy during the wedding?
	"""
	def __init__(self, date, person, significant_other):
		super(Marriage, self).__init__(date)
		self.person = person
		self.significant_other = significant_other
		self.marriage()
		self.change_last_name()
		self.children_from_this_marriage = []


	def marriage(self):
		"""Get married
		Again, this is an exception case since otherwise many social relationship factors are involved
		"""
		self.person.update_relationship(self.significant_other, "Spouse")
		self.significant_other.update_relationship(self.person, "Spouse")

		p_journal_message = "Got married to %s." % (self.significant_other.name)
		self.add_to_journal(self.person, p_journal_message)
		s_journal_message = "Got married to %s." % (self.person.name)
		self.add_to_journal(self.significant_other, s_journal_message)

		self.person.spouse = self.significant_other
		self.significant_other.spouse = self.person



	def change_last_name(self):
		s_journal_message = ""
		p_journal_message = ""
		# Probability of changing last name
		choice = random.random()

		if choice > 0.295:
			if self.person.gender == 'male':
				self.significant_other.last_name = self.person.last_name
				s_journal_message = "I took his last name. I'm now %s" % (self.significant_other.last_name)
			elif self.significant_other.gender == 'male':
				self.person.last_name = self.significant_other.last_name
				p_journal_message = "I took his last name. I'm now %s" % (self.person.last_name)
			else:
				self.significant_other.last_name = self.person.last_name
				s_journal_message = "I took her last name. I'm now %s" % (self.significant_other.last_name)

		# This is probably not true. Need to check stats and rules?
		elif choice <= 0.295 and choice > 0.105:
			couple = [self.person, self.significant_other]
			random.shuffle(couple)
			new_last_name = "%s-%s" % (couple[0].last_name, couple[1].last_name)
			self.person.last_name = new_last_name
			self.significant_other.last_name = new_last_name
			s_journal_message = "We hyphenated our names! I'm now %s" % (self.significant_other.last_name)
			p_journal_message = "We hyphenated our names! I'm now %s" % (self.person.last_name)

		else:
			s_journal_message = "We decided to keep our names."
			p_journal_message = "We decided to keep our names."

		self.add_to_journal(self.person, p_journal_message)
		self.add_to_journal(self.significant_other, s_journal_message)
		self.person.events.append(self)
		self.significant_other.events.append(self)




class TheBeginning(Event):
	"""The start of the world
		Settlers are generated in Area 51. They divide into couples (if at all), and
		then relocate to another town.
	"""
	def __init__(self, world):
		super(TheBeginning, self).__init__(world.current_date)
		self.world = world
		print("Big Bang!")

		# Makes a seed population of settlers to populate the world with
		self.settler_babies(50)

		# Find partners - not based on affinity at the moment. Totally random
		# Consider it after effects of alien abduction
		self.random_match_couples()


	def settler_babies(self, num=100):
		"""Initial seed population for the world
		@param int num
			Choose random birthdays for the first people in the world
			They will pair up and then migrate to other cities.
		"""

		# Choosing the number of NPCs in each category from the 2016 US Presidential elections voting data 
		num_right = round(0.4647 * num * 0.33)
		num_lean_right = round(0.4647 * num * 0.67)
		num_left = round(0.4859 * num * 0.378)
		num_lean_left = round(0.4859 * num * 0.622)
		num_cent = num - num_right - num_lean_right - num_left - num_lean_left

		categories = [num_right, num_lean_right, num_cent, num_lean_left, num_left]

		biases = [Bias.RIGHT, Bias.LEAN_RIGHT, Bias.CENTER, Bias.LEAN_LEFT, Bias.LEFT]

		sim_date = self.world.current_date


		_dates = itertools.islice(self.world.sample_wr(list(range(365))), num)

		categ_count, categ_chosen = 0, 0
		for i, day in enumerate(_dates):
			bias = biases[categ_chosen]

			birthdate = sim_date.shift(days=day)
			_year = 20 + random.choice(list(range(10)))
			birthdate = birthdate.shift(years=-_year)
			born = Birth(self.world, None, None, birthdate)

			born.baby.set_political_affiliation(bias)
			self.set_initial_views(born.baby, bias)
			born.baby.add_to_census()

			if categ_count >= categories[categ_chosen]:
				categ_chosen += 1
				categ_count = 0
			else:
				categ_count += 1


	def set_initial_views(self, baby, bias):
		baby.set_political_affiliation(bias)

		articles = self.world.filter_articles_by_rating(bias)
		articles.extend(self.world.filter_articles_close_to_rating(bias))
		num_articles_known = random.randint(1, len(articles))

		for article in random.sample(articles, num_articles_known):
			baby.knowledge.add_article(article)


	def random_match_couples(self):
		"""Maybe make settler couples based on some probability
			Unlike the rest of the cases, this is not based on initial interaction.
		"""

		while self.world.towns['Area 51'].citizens:
			person = self.world.towns['Area 51'].random_citizen

			matches = [self.world.get_npc(match) for match in self.world.towns['Area 51'].citizens if abs(self.world.get_npc(match).age - person.age) <= 5]
			matches.remove(person)

			if person.sexual_preference == 'homosexual':
				matches = [match for match in matches if match.gender == person.gender]
			elif person.sexual_preference == 'heterosexual':
				matches = [match for match in matches if match.gender != person.gender]

			if matches and random.random() >= 0.452:
				significant_other = random.choice(matches)
				# choose wedding date?
				sim_date = self.world.current_date
				wedding_date = sim_date.shift(days=random.choice(list(range(365))))
				# marriage =
				Marriage(wedding_date, person, significant_other)

				# print "Couple! %s and %s" % (person.name, significant_other.name)
				self.random_relocate(person, significant_other)

			else:
				self.random_relocate(person)


	def random_relocate(self, person, significant_other=None):
		"""Choose a random town to relocate to"""
		new_town = self.world.random_location

		# Change journal entry
		if not significant_other:
			person.town.remove_citizen(person)
			new_town.add_citizen(person)
			journal_message = "Moving to %s. (singing) Alone again... naturally." % (new_town.name)
			self.add_to_journal(person, journal_message)

		else:
			house_number = new_town.find_unoccupied_home()
			person.town.remove_citizen(person)
			significant_other.town.remove_citizen(significant_other)
			new_town.add_citizen(person, house_number)
			new_town.add_citizen(significant_other, house_number)
			journal_message = "This place is spooky. Moving to a new town, %s." % (new_town.name)
			self.add_to_journal(person, journal_message)
			self.add_to_journal(significant_other, journal_message)


class Relocate(Event):
	""" Marriage Event
		Marries two people, and changes their last names (sometimes) accordingly
		Also adds a marriage event to the person's journal.
		Can also decide on a child policy during the wedding?
	"""
	def __init__(self, date, person, household=[]):
		super(Relocate, self).__init__(date)



class Contemplate(Event):
	"""Contemplation of Knowledge

	The NPC tries to figure out where they stand on the political spectrum based on all the knowledge they learnt in the past year
	For every topic, find the mean view of the NPC based on the NPC's views of the topic
	Once all topics have adjusted views, recalculate the NPCs original views (mean/wtd mean of all topics)
	Check political bias
	""" 

	def __init__(self, world: World, person: Person):
		super(Contemplate, self).__init__(world.current_date)
		self.world = world
		self.person = person

	def contemplate_knowledge(self):
		"""Recalculate overall views""" 
		views = [self.person.knowledge.view]
		views.extend([topic['view'] for topic in self.person.knowledge.topics.keys()])
		new_view = self.contemplate(views)




	# Afternoon continue
	def contemplate_all_topics(self):
		"""Recalculate overall NPC views on topics""" 
		for topic_id, view_objects in self.person.knowledge.topics.items():
			# topic = self.world.get_topic_by_id(topic_id)
			topic_views = [view_objects['view']]
			topic_views.extend([article.view for article in self.person.knowledge.filter_articles_by_topic(topic)])
			new_view = self.contemplate(topic_views)

			# Has the NPCs views on the topic changed?
			if new_view != topic_views[0]:
				self.person.knowledge.topic['historical_views'] = self.person.knowledge.topic['view']
				self.person.knowledge.topic['view'] = new_view
				print(self.person.name, " changed their mind about topic: ", topic.name)


	def contemplate(self, views):
		"""Get Opinion for views
			Todo: (Questions)
				Currently doing another "discusssion". 
				Should we do the mean instead? - Get the mean opinion of all the articles known under this topic in this KB.
		"""

		discussion = Discussion(views)

		# Randomly simulate the duration of the consideration of the article. 
		# The longer the duration, the more the opinions and attitudes of the person may change reg. the article
		discussion_duration = 1				# random.randint(1, 5)
		for minute in range(discussion_duration):
			discussion.discuss(contemplation=True)

		view = discussion.get_views(contemplation=True)[0]

		return view


class Agree(Event):
	"""Agreement Event
		Tracks when NPCs agree with one another during the course of a discussion and does the following: 
		1. Increases/Decreases the agreement relationship between the NPCs
		2. Tracks the change in the journal
	"""
	def __init__(self, group: [Person]):
		super(Agree, self).__init__()
		self.group = group

		for person in group: 
			person.simple_interaction(group, "agree")



	def get_speaker_rest(self):
		speaker = random.choice(self.group)
		rest = [person for person in group if person != speaker]

		return speaker, rest




class GroupDiscussion(Event):
	"""Group Discussion Event 
	Makes the group have a discussion about a specific topic
	Either the topic is give, or found based on common/maximum knowledge in the group
	"""
	g_id = itertools.count().__next__

	def __init__(self, world: World, group: [Person], article: Article = None, discussion_type=None):
		super(GroupDiscussion, self).__init__(world.current_date)

		# Don't always have group discussions
		# Todo: Change this to a default/global/modifiable number

		self.id = GroupDiscussion.g_id()
		self.group = group
		self.discussion_type = discussion_type

		# If discussion starts in school, then it's set 
		if not article: 
			article = self.find_common_knowledge_article()

		self.article = article

		self.old_views = self.get_views()

		if len(group) >= 4 and len(group) < 10:
			self.STUDY_CASE_short_duration()
			# self.STUDY_CASE_long_duration()

		else: 
			# self.STUDY_CASE_Random()
			return

		self.discussion.show_final_change_in_views()
		self.new_views = self.discussion.get_views()
		self.update_views()



	def find_common_knowledge_article(self):
		"""Get the topic of discussion
			Try to choose an article to discuss that everyone in the group is interested in/knows about.article
			Choose one of the most frequently occuring article in their knowledge base. 
		"""

		# All articles known to the group
		count = Counter(list(itertools.chain.from_iterable([person.knowledge.articles.keys() for person in self.group])))

		# What articles are the most common
		common_max = max(count.values())
		(chosen_article_for_discussion, frequency) = random.choice([fact for fact in count.most_common(common_max)])

		print("## Common Knowledge Article ##\n Discussion of %s: Known to %s/%s people" % (chosen_article_for_discussion, frequency, len(group)))
		return chosen_article_for_discussion


	def get_views(self):
		group_views = []
		for person in self.group: 
			if self.article.id not in person.knowledge.articles:
				# Currently new articles are added with the person's default overall views. 
				# Todo: Change that to topic view?
				person.knowledge.add_article(self.article)
			group_views.append(person.knowledge.articles[self.article.id]['view'])

		return group_views



	def STUDY_CASE_Random(self):
		# RANDOM CONDITION
		# Randomly simulate the duration of the conversation. 
		# The longer the duration, the more the opinions and attitudes of the group may change 
		self.discussion_duration = random.randint(1, 5)
		self.initiate_group_discussion()


	def STUDY_CASE_short_duration(self):
		# RANDOM CONDITION
		# Randomly simulate the duration of the conversation. 
		# The longer the duration, the more the opinions and attitudes of the group may change 
		self.discussion_duration = 3 
		self.initiate_group_discussion()


	def STUDY_CASE_long_duration(self):
		# RANDOM CONDITION
		# Randomly simulate the duration of the conversation. 
		# The longer the duration, the more the opinions and attitudes of the group may change 
		self.discussion_duration = 6
		self.initiate_group_discussion()


	def get_current_group_knowledge(self):
		print("\n----- FAMILIARITY WITH THE ISSUE -------")
		for participant in [person for person in self.group]: 
			if not isinstance(participant, Person):
				continue
			print("\n%s" % (participant.name))
			participant.knowledge.show_knowledge_on_topic(self.article.topic)
		print("------------------------------------\n")


	def initiate_group_discussion(self):
		participants = [person for person in self.group]

		self.discussion = Discussion(self.old_views, participants)
		self.discussion.article = self.article

		print("------- Discussion #%s Details --------" % (self.id))
		print("%d debate participants: #%s" % (len(self.group), ', '.join([str(person.name) for person in self.group])))
		print("Discussion on %s" % (Topic.get_topic(self.article.topic)))
		print("Debating merits of article, \"%s\" (%s)." % (self.article.title, Source.get_source(self.article.source)))
		print("""The %s participants were given the article to read, and %s rounds to discuss the same."""
			 % (len(self.group), self.discussion_duration))

		# \nEach participant could express their opinion of the article in question, after which the next person would be given a chance. 
		# 	\nParticipants could change their mind over subsequent rounds. 
		# 	\nAt the end of each minute, participants were asked to rate their current views of the article on a scale from -1.0 (LEFT) to +1.0 (RIGHT) so that the change in their opinions could be tracked.

		self.get_current_group_knowledge()

		self.discussion.add_article_into_conversation()
		self.discussion.describe_views_template()

		self.journal_start_discussion(participants)
		for minute in range(self.discussion_duration):
			print("\n----- Round %s -----" % (minute+1))
			self.discussion.discuss()


	def journal_start_discussion(self, participants):
		members_message = "Participants: " + ', '.join([participant.name for participant in participants])
		journal_message = "Had a group discussion on \"%s\" for %s minutes. (%s). " % (self.article.title, self.discussion_duration, members_message)

		for person in participants: 
			self.add_to_journal(person, journal_message)


	def journal_end_discussion(self, person: Person, change=True, old_view=None, new_view=None):
		if change: 
			journal_message = "I changed my opinions about Article:#%s after the discussion." % (self.article.id)
			journal_message += "My view changed from %s to %s" % (old_view, old_view.display_change_from(new_view))

		else:
			journal_message = "The discussion did not change my opinions on Article:#%s." % (self.article.id)

		self.add_to_journal(person, journal_message)


	def update_views(self):
		conversationalists = [person.name for person in self.discussion.participants]

		person = None
		for index, person in enumerate(self.discussion.participants): 
			if not isinstance(person, Person):
				continue
			new_view = self.new_views[index]
			old_view = person.knowledge.articles[self.article.id]['view']

			# Continue here
			if new_view != old_view: 
				# Updating the person's views on a topic post discussion
				person.knowledge.articles[self.article.id]['historical_views'].append(deepcopy(old_view))
				person.knowledge.articles[self.article.id]['view'] = new_view
				self.journal_end_discussion(person, change=True, old_view=old_view, new_view=new_view)
			else: 
				self.journal_end_discussion(person, change=False)
