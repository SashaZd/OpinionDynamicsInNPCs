from configs import *
import random
import itertools
from Knowledge.Knowledge import Knowledge
from Knowledge.Article import Article
from collections import defaultdict

from NPC.Person import Person
from NPC.Event import GroupDiscussion

class Organization(object):
	"""docstring for Organization
	"""

	o_id = itertools.count()
	current_organizations = defaultdict(list)
	past_organizations = defaultdict(list)

	def __init__(self, world, name, type=None, location=None, founding_date=None):
		super(Organization, self).__init__()
		# self.arg = arg

		# if name: 
		# 	self.name = name
		# else:
		# 	self.assign_name()

		self.id = next(self.__class__.o_id)
		self.name = name
		self.type = type
		self.founding_date = founding_date
		self.terminate_date = None
		self.world = world

		if location: 
			self.location = location
		else:
			self.location = random.choice(LOCATIONS)

		self.current_members = set()
		self.past_members = set()
		self.days_of_meet = [0, 1, 2, 3, 4]  # Python dates start on Monday=0

		self.knowledge = Knowledge(self.world)
		self.__class__.current_organizations[self.type].append(self)


	def assign_name(self, newname):
		self.name = newname


	def add_member(self, person: Person):
		self.current_members.add(person)


	def remove_member(self, person):
		if person in self.current_members: 
			self.past_members.add(person)
			self.current_members.remove(person)


	def calculate_avg_opinion(self, topic):
		# if topic in self.topics_of_interest: 
		# 	# for member in self.current_members: 
		# 	# 	pass
		# 	print "To Do"

		# else:
		# 	print "No opinion"
		pass


	def members_interact(self, type_interaction: str):
		# Updates relationship

		if len(self.current_members) > 1: 
			for student in self.current_members:
				student.simple_interaction(self.current_members, type_interaction)

			# Currently a 50% chance that you'll have a discussion with the group you're interacting with
			# If you choose not to have a discussion, the NPCs still update their simple relationships with each other 
			# i.e. social interaction only or discussion also

			# Unnecessary: Randomly choose one student that begins a discussion: 
			# discussion_leader = random.choice(list(self.current_members))
			# discussion_leader.initiate_group_discussion(self.current_members)

	def members_discuss_article(self, article: Article=None, event_title=None):
		# No topic in mind at the moment, so choose a common one?

		if len(self.current_members) > 1 and random.random() < 0.2:
			print("Starting discussion in the school")
			group_discussion = GroupDiscussion(world=self.world, group=self.current_members, article=article, discussion_type=event_title)
			self.world.discussions.append(group_discussion)
			# self.members_interact()


	def set_articles_discussed(self, articles=None):
		"""Subjects taught by this school
			Will be used to decide how much knowledge about a topic a person has
			Can be used to form opinions
		""" 
		if not articles: 
			all_articles = self.world.knowledge.articles.keys()
			random.sample(all_articles, random.randint(1, len(all_articles)))

		# topics_chosen = random.sample(topics, random.choice(list(range(4, len(topics)))))
		for article in articles: 
			self.knowledge.add_article(article)

		# print("%s: %d articles taught" % (self.name, len(self.knowledge.articles.keys())))


	def __str__(self):
		return "%s" % (self.name)

	def __repr__(self):
		return "%s" % (self.name)

	def __unicode__(self):
		return "%s" % (self.name)

	""" TODO: add members to past_member when they leave"""


class School(Organization):
	"""Local schools
	Currently there's only 2 schools, can change that in the world later. 
	Allows for simulation of people interacting growing up. 
	"""

	def __init__(self, world, name, location=None, founding_date=None):
		super(School, self).__init__(world, name, 'school', location, founding_date)


	def enroll_student(self, student):
		# print("School: %s | Student Enrolled: %s" % (self.name, student.name))
		self.add_member(student)


	def unenroll_student(self, student):
		self.remove_member(student)


	def teach_students_about_article(self, article: Article = None):
		# Currently assuming that teachers don't already have opinions 
		if not article: 
			article = self.knowledge.get_random_article()

		for student in self.current_members: 
			student.knowledge.add_article(article)

		event_title = "%s Discussion"%(self.type)
		self.members_discuss_article(article=article, event_title=event_title)


class University(Organization):
	""" Grad schools
	"""
	def __init__(self, world, name):
		super(University, self).__init__(name)
		self.days_of_meet = [0,1,2,3,4,5]
		pass


class Club(Organization):

	""" Interest Clubs
	"""
	def __init__(self, world, name, topics_of_interest=[]):
		super(Club, self).__init__(name)

		# Example: "sci-fi", "doctor who", "baking", etc
		self.topics_of_interest = topics_of_interest

		pass


class Hospital(Organization): 
	"""
		For babies to be born in 
	""" 
	def __init__(self, world, name, location, founding_date=None):
		super(Hospital, self).__init__(name, 'hospital', location, founding_date)
		pass


class Company(Organization):

	""" Company
	"""
	def __init__(self, world, name):
		super(Company, self).__init__(name)
		self.owner = None

		# List of topic names that are required for a position here
		self.knowledge_required = []
		
		self.positions = {}




class Restaurant(Company):
	"""docstring for Restaurant"""
	def __init__(self, world, name):
		super(Restaurant, self).__init__(name)
		# self.name = name
		pass
		



