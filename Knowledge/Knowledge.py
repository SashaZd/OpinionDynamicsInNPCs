from typing import List
import random
from copy import deepcopy
from statistics import mean, median, mode, StatisticsError

from .Source import Source
from .Bias import Bias
from .Topic import Topic
from .Article import Article
from .Discussion import Discussion

from .View import View

from collections import defaultdict

import sys, os

# decorater used to block function printing to the console
def blockPrinting(func):
    def func_wrapper(*args, **kwargs):
        # block all printing to the console
        sys.stdout = open(os.devnull, 'w')
        # call the method in question
        value = func(*args, **kwargs)
        # enable all printing to the console
        sys.stdout = sys.__stdout__
        # pass the return value of the method back
        return value
    return func_wrapper


class Knowledge(object):
	"""docstring for Knowledge"""

	world = None

	def __init__(self, world, owner=None):
		super(Knowledge, self).__init__()
		self.sources = {}		# source_id		: {view, historical_views}
		self.topics = {}			# topic_id		: {view, historical_views}
		self.articles = {}		# article_id 	: {view, historical_views}

		self.owner = owner

		self.historical_views = []

		self.reevaluate_flag = False

		if not self.__class__.world: 
			self.__class__.world = world

		# Default value. Can be changed later. 
		self.set_political_affiliation(Bias.UNKNOWN)


	def set_political_affiliation(self, bias: Bias):
		"""Set politcal affiliations 
				Aggregating their opinions on each individual issue
		"""
		self.view = View()
		self.view.generate_view_based_on_bias(bias)


	def reevaluate_political_affiliation(self):
		self.make_opinions_on_topics()
		topic_views = [views['view'] for views in self.topics.values()]

		# Assuming all topics are weighed equally
		# To do: change weight to influence Political Aff? 

		t_ops = [view.opinion for view in topic_views]
		t_att = [view.attitude for view in topic_views]

		mean_op = round(mean(t_ops), 2)
		mean_att = round(mean(t_att), 2)

		new_view = View(mean_att, mean_op)
		self.historical_views.append(deepcopy(self.view))
		self.view = new_view


	def make_opinions_on_topics(self):
		for topic_id in self.topics: 
			topic = self.world.get_topic_by_id(topic_id)
			self.make_opinion_for_topic(topic)


	def make_opinion_for_topic(self, topic: Topic):
		# """Get Opinion for Topic
		# 		Get the mean opinion of all the articles known under this topic in this KB.
		# """
		if not isinstance(topic, Topic):
			if type(topic) == int: 
				topic = self.world.get_topic_by_id(topic)
			else: 
				raise Exception(
					"Expected <Knowledge.Topic.Topic> instance. Received: %s instead." %
					(type(topic)))

		views_on_topic = [view['view'] for articleID, view in self.articles.items() if self.world.get_article_by_id(articleID).topic == topic.id]
		if not views_on_topic:
			new_view = deepcopy(self.view)
			old_view = None
			self.add_topic(topic, new_view)

		else:
			opinions = [view.opinion for view in views_on_topic]
			attitudes = [view.attitude for view in views_on_topic]
			uncs = [view.unc for view in views_on_topic]
			mean_op = round(mean(opinions), 2)
			mean_att = round(mean(attitudes), 2)
			mean_unc = round(mean(uncs), 2)

			new_view = View(mean_att, mean_op)
			new_view.unc = mean_unc
			old_view = deepcopy(self.topics[topic.id]['view'])

		if old_view and old_view != new_view: 
			self.topics[topic.id]['historical_views'].append(old_view)
			self.topics[topic.id]['view'] = new_view

		# print("%s articles on %s. View: %s" % (len(views_on_topic), topic, new_view))

		# for articleID, aviews in self.articles.items():
		# 	article = self.world.get_article_by_id(articleID)
		# 	if article.topic == topicID: 
		# 		print(aviews['view'], article)

		# article_views.insert(0, self.view)
		# discussion = Discussion(article_views)

		# # Randomly simulate the duration of the consideration of the article. 
		# # The longer the duration, the more the opinions and attitudes of the person may change reg. the article
		# discussion_duration = 1 #random.randint(1, 5)
		# for minute in range(discussion_duration):
		# 	discussion.discuss(contemplation=True)

		# views = discussion.get_views(contemplation=True)
		# # print(len(views), len(self.topics[topic.id]['historical_views']))
		# if self.topics[topic.id]['historical_views'] and views[0] != self.topics[topic.id]['historical_views'][-1]:
		# 	self.topics[topic.id]['historical_views'].append(self.topics[topic.id]['view'])
		# 	self.topics[topic.id]['view'] = views[0]
		# pass


	def get_opinion_for_knowledge(self):

		views = [self.view]
		other_views = [self.topics[topic_id]['view'] for topic_id in sorted(self.topics.keys())]
		views.extend(other_views)

		discussion = Discussion(views, contemplation=True)


		# Randomly simulate the duration of the consideration of the article. 
		# The longer the duration, the more the opinions and attitudes of the person may change reg. the article
		discussion_duration = 1 # random.randint(1, 5)
		for minute in range(discussion_duration):
			discussion.discuss()

		new_views = discussion.get_views()
		if new_views[0] != self.view: 
			self.historical_views.append(self.view)
			self.view = new_views[0]


		index = 1
		for topic_id in sorted(self.topics.keys()): 
			if self.topics[topic_id]['historical_views'] and new_views[index] != self.topics[topic_id]['historical_views'][-1]:
				self.topics[topic_id]['historical_views'].append(self.topics[topic_id]['view'])
				self.topics[topic_id]['view'] = new_views[index]
			index += 1 

		# print("New: \n", self.view)


	def add_source(self, source: Source):
		"""Media Source
				Add to the list of sources that this knowledge base is aware of
				Note: this does not mean that the NPC subscribes to the knowledge source
		"""
		# if provided with the source instance
		if not isinstance(source, Source):
			raise Exception(
				"Expected <Knowledge.Source.Source> instance. Received: %s instead." % (type(topic)))

		if source.id not in self.sources:
			self.sources[source.id] = {'view': deepcopy(self.view), 'historical_views': []}

	def add_topic(self, topic: Topic, view: View = None):
		"""Topic or Issue
				Topic of discussion
				Until AllSides data, we're using: Media Bias and Immigration as sample topics
		"""
		if not isinstance(topic, Topic):
			raise Exception(
				"Expected <Knowledge.Topic.Topic> instance. Received: %s instead." % (type(topic)))

		if topic.id not in self.topics:
			if not view: 
				self.topics[topic.id] = {'view': deepcopy(self.view), 'historical_views': []}
			else:
				self.topics[topic.id] = {'view': view, 'historical_views': []}

	def add_article(self, article: Article):
		"""A single article
				From a source/media with an associated bias
		"""
		if not isinstance(article, Article):
			raise Exception(
				"Expected <Knowledge.Article.Article> instance. Received: %s instead." % (type(topic)))

		if article.id not in self.articles:
			article_view = self.consider_article(article=article)
			self.articles[article.id] = {'view': article_view, 'historical_views': []}     # {'view': deepcopy(self.view), 'historical_views': []}

		# In case this is a new topic/source introduced, add the topic/source to the knowledge base
		# for topic_id in article.topics:
		if article.topic not in self.topics:
			self.add_topic(self.world.get_topic_by_id(article.topic))

		if article.source not in self.sources:
			self.add_source(self.world.get_source_by_id(article.source))


	# @blockPrinting
	def consider_article(self, article: Article):
		""" Consideration of the article while adding to the knowledge base

		Involves the NPC looking at the view presented by the article, and the changing it's own opinion/mind
		accordingly based on acceptance of that view. 

		Note: Currently every article is taken with your overall view 
		Currently don't have a view on every article in the knowledge base
		However, in the future we could have the same.
		Currently, the NPC just considers all the articles in their knowledge base while deciding on their own view on the topic

		Todo: Change the default view to the Topic view?
		""" 

		if self.owner == None: 
			self.make_opinion_for_topic(article.topic)
			view = self.topics[article.topic]['view']
			return view 	# deepcopy(self.view)


		# Just uncomment all the lines below this one in the method to calculate a view on every topic
		article_view = View(article.rating.value, article.rating.value)
		article_view.unc = 0.0
		self.make_opinion_for_topic(article.topic)
		view = deepcopy(self.topics[article.topic]['view'])
		views = [view, article_view]
		participants = [self.owner, article]

		discussion = Discussion(views, participants, contemplation=True)

		# # Randomly simulate the duration of the consideration of the article. 
		# # The longer the duration, the more the opinions and attitudes of the person may change reg. the article
		discussion_duration = random.randint(1, 5)
		for minute in range(discussion_duration):
			discussion.discuss()


		[view] = discussion.get_views()
		return view

		# this
		# 


	def get_random_article(self) -> Article:
		return self.world.get_article_by_id(random.choice(list(self.articles.keys())))


	def get_topic_by_title(self, title):
		"""Get topic
				Return a specific topic/issue that matches the title.
		"""
		topic = self.world.get_topic_by_title(title)
		if topic.id in self.topics:
			return topic
		else:
			return None

	def get_source_by_title(self, title):
		"""Get source
				Return a source/media
		"""
		source = self.world.get_source_by_title(title)
		if source.id in self.sources:
			return source
		else:
			return None

	def filter_articles_by_topic(self, topic: Topic) -> List[Article]:
		topic_id = topic.id
		return [self.world.get_article_by_id(article_id) for article_id in self.articles if topic_id == self.world.articles[article_id].topic]


	def show_knowledge_on_topic(self, topicID):
		topic = self.world.get_topic_by_id(topicID)
		self.make_opinion_for_topic(topic)

		articles_on_topic_in_KB = [view['view'] for articleID, view in self.articles.items() if self.world.get_article_by_id(articleID).topic == topicID]
		# articles_on_topic_in_KB = [(self.world.get_article_by_id(articleID), view['view']) for articleID, view in self.articles.items() if self.world.get_article_by_id(articleID).topic == topicID]
		opinions = [view.opinion for view in articles_on_topic_in_KB]

		_mean = round(mean(opinions), 2)
		_median = round(median(opinions), 2)

		try: 
			_mode = round(mode(opinions), 2)

		except StatisticsError:
			numeral = [[opinions.count(nb), nb] for nb in opinions]
			numeral.sort(key=lambda x: x[0], reverse=True)
			_mode = numeral[0][1]

		_topic_view = self.topics[topicID]['view']
		print("""Current view influenced by reading %s articles on %s.\nCurrent position:-\t attitude: %s(%s) | opinion: %s(%s) | uncertainty: %s"""
								% (len(articles_on_topic_in_KB), topic, Bias.get_bias_text(Bias.get_bias(_topic_view.attitude).value), _topic_view.attitude, Bias.get_bias_text(Bias.get_bias(_topic_view.opinion).value), _topic_view.opinion, _topic_view.unc))
		# print("#%s articles in knowledge on %s. \nView on topic: %s" # \nOpinions - Mean: %s | Median: %s | Mode: %s " 
		# 			% (len(articles_on_topic_in_KB), topic, self.topics[topicID]['view'])) #, _mean, _median, _mode))


	def __str__(self):
		return """KB:\n
			Topics: %s\n
			Sources: %s\n
			Articles: %s""" % (list(self.topics), len(self.sources), len(self.articles))

	def __repr__(self):
		return "KB:\n\tTopics: %s\n\tSources: %s\n\tArticles: %s" % (list(self.topics), len(self.sources), len(self.articles))
