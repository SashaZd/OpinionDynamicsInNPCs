from typing import List
from .View import View, Bias
# from sklearn.cluster import KMeans
# import numpy as np

from copy import deepcopy
from math import exp, fabs
from statistics import mean
from collections import defaultdict
import jenkspy
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd

import random

class Discussion(object):
	"""docstring for Discussion"""

	def __init__(self, views, participants=[], contemplation=False):
		"""Init for the discussions
		Arguments:
		views: View[]
		"""
		super(Discussion, self).__init__()

		# How many groups of opinions are formed by the clustering process based on the similarity of the opinions
		# If number of groups formed < NSI then the public opinion on the topic has been formed. 
		self.NSI_THR = 2  # Normative social influence threshold
		self.UNC_THR = 0.8
		self.original_views = [deepcopy(views)]
		self.views = deepcopy(views)
		self.new_views = deepcopy(views)
		self.contemplation = contemplation
		self.coalitions = []
		self.participants = participants 

		# Todo: Account for the article's bias and 100% confidence? / No change?
		# self.describe_views_template()

	def add_article_into_conversation(self):
		article = deepcopy(self.article)
		article.name = "the Article"
		article_view = View(article.rating.value, article.rating.value)
		article_view.unc = 0.0
		self.participants.append(article)
		self.views.append(article_view)
		self.original_views[0].append(article_view)
		self.new_views.append(article_view)


	def describe_views_template(self):
		from NPC.Person import Person
		biases = defaultdict(list)

		print("INSTRUCTION: The participants were asked to read and evaluate the article with its %s bias." % (Bias.get_bias_text(self.article.rating.value)))
		print("INSTRUCTION: They were asked to publicly declare their opinions on the issue as influenced by the article and any prior familiarity with the issue.")

		for participant in self.participants: 
			if not isinstance(participant, Person):
				continue
			print ("--> %s's response to the article indicated their opinions were %s" % (participant.name, self.get_participant_opinion(participant)))

		print("The participants gave their opening statements to persuade the others to their views.")



	def discuss(self):
		"""A single discussion
		Equivalent to one unit of time/beat in the narrative. 
		A longer duration makes it more likely for the group to reach a consensus

		Arguments: 
			contemplation: boolean (default: False). 
				If an NPC is merely contemplating his views, we don't change the values for the views themselves, 
				instead, the NPC decides whether there is an adjustment in his own views, and the 
				algorithm ends early. 
		""" 

		views = deepcopy(self.new_views)
		self.views = self.adjust_unc(views)
		self.group_discussion()
		self.original_views.append(deepcopy(views))
		# print(self.new_views)


	def get_actual_cluster_count(self):
		""" Don't want to include the article as a view group at the moment """ 
		num_clusters = len(self.opinion_grouping.keys())
		for mean, group in self.participant_grouping.items():
			if len(group) == 1 and group[0].name == "the Article":
				num_clusters = len(self.opinion_grouping.keys()) - 1
		return num_clusters


	def group_discussion(self):
		from NPC.Person import Person

		self.opinion_grouping, self.participant_grouping = self.find_best_grouping_of_opinions()
		if not self.contemplation:
			print("\nINSTRUCTION: Participants were asked to make a short argument to persuade the other debaters to adopt their position.")
			print("\nINSTRUCTION: Participants were asked to select all debaters whose arguments resonated with them.")
			print("\n%s groups of like minded individuals formed:" % (self.get_actual_cluster_count()))
			self.template_participant_grouping_journal()

		# Conversation template for participant grouping
		# To show movement between characters in the conversation via vis?
		self.coalitions.append(deepcopy(self.opinion_grouping))

		# NSI_THR is the normative social influence thresh.
		# 	Check how many distinct groups of opinions have formed by clustering
		# 	NSI_THR dictates the min number of groups of opinions that opinions need to 
		# 	cluster on for us to decide whether public opinions have formed.
		newer_views = []

		if not self.contemplation: 
			print("\n### Round Event Summary ###")

		num_clusters = self.get_actual_cluster_count()

		if num_clusters <= self.NSI_THR:
			if not self.contemplation: 
				print("Since there were only %s distinct clusters of opinions, it seemed as though Public Opinion had formed." % (num_clusters))
			largest_group = max(self.opinion_grouping.values(), key=len) 
			# print("Original Cluster Length: %s\nLargest opinon cluster: %s\n\n" % (len(self.original_views), largest_group))

			for index, view in enumerate(self.new_views): 
				person = self.participants[index]
				if not isinstance(person, Person): 
					continue
				newer_views.append(deepcopy(self.public_opinion_formed(person, view, largest_group=largest_group)))
				if self.contemplation: 
					break

		# Public opinion not yet formed
		else:
			if not self.contemplation: 
				print("Too many differing opinion groups present. Public Opinion not formed on the matter.")
			for index, view in enumerate(self.new_views): 
				person = self.participants[index]
				if not isinstance(person, Person): 
					newer_views.append(deepcopy(view))
					continue
				newer_views.append(deepcopy(self.no_public_opinion(person, view)))
				if self.contemplation: 
					break

		# Do not delete. Reducing verbosity for study
		# if not self.contemplation: 
		# 	print("Delete from Survey")
		# 	# print("\nINSTRUCTION: Participants were asked to update their view ratings to express any change in their positions.")
		# 	for index, old_view in enumerate(self.views): 
		# 		person = self.participants[index]
		# 		if not isinstance(person, Person):
		# 			continue

		# 		self.did_view_change(old_view, newer_views[index], person, show=True)
		# 		if self.contemplation: 
		# 			break

		self.new_views = deepcopy(newer_views)
		# for index, view in enumerate(newer_views): 
		# 	self.new_views[index] = view


	def adjust_unc(self, views):
		# Todo: Is this correct? Check how to change the uncertainty in views overtime? 
		for view in views: 
			uncertainty = round(fabs(view.attitude - view.opinion), 2)

			if view.unc != uncertainty: 
				view.unc = round(uncertainty, 2)

			if self.contemplation: 
				break

		return views

	def get_participant_opinion(self, person) -> str:
		index = self.participants.index(person)
		view = self.views[index]
		return view.display_opinion_verbose()


	def get_views(self)->[View]:
		"""Signals the end of discussion, returns the final changed views

		If the agent is contemplating their own views, then only the 
			[modified] agent's views are returned
		""" 

		if self.contemplation: 
			return [self.new_views[0]]
		else:
			return self.new_views


	def closest_group_to_view(self, view: View = None):
		""" Returns the group with the opinion closest to this one
		""" 
		if view:
			mean_closest, diff, closest_group = float("Inf"), float("Inf"), None
			for mean, group in self.opinion_grouping.items():
				new_diff = abs(view.opinion - mean)
				if new_diff < diff: 
					mean_closest, diff, closest_group = mean, new_diff, group

		# print("Closest group_mean to %s is %s"%(view.opinion, mean))
		return closest_group, mean_closest


	def public_opinion_formed(self, person, view, largest_group=None):
		"""Public opinion is formed
			Since pub_op is formed, any agents that retain their ideas risk rejection. 
		"""
		# if not isinstance(person, Person):
		# 	return view

		# Agents with high levels of uncertainty will follow the largest groups opinions
		temp_view = deepcopy(view)
		view = deepcopy(view)
		if view.unc > self.UNC_THR:
			if not self.contemplation: 
				print("%s looked for the group with the largest majority." % (person))
			# print("%s has high uncertainty of views. Will follow the mean majority opinion." % (person))
			self.template_highunc_journal(person)
			view.opinion = round(mean(largest_group), 2)
			view.attitude = round(mean(largest_group), 2)
			# max_group, min_group = max(largest_group), min(largest_group)
			# view.unc = max([fabs(op - view.opinion) for op in largest_group])

		else:
			# Agent recognizes that there is a difference in it's own attitude and opinion
			# Find the group that is closest to the opinion of this agent.
			self.template_pubop_nsi_journal(person)
			closest_group, mean_of_group = self.closest_group_to_view(view)
			if not self.contemplation:
				print("The closest group was the one with %s" % (self.template_name_group_members(self.participant_grouping[mean_of_group], excludePerson=person)))
			view = deepcopy(self.check_normative_social_influence(view=view, opinion_group=closest_group, agent_name=person))

		self.did_view_change(temp_view, view, person, show=False)

		return view

	def did_view_change(self, old_view, new_view, person, show=False):
		if self.contemplation: 
			return

		change = old_view.display_change_from(new_view)

		if "Unchanged" not in change: 
			if not show: 
				print("\t%s updated their view rating" % (person.first_name))
			else: 
				att_change = True if "attitude: **" in change else False
				op_change = True if "opinion: **" in change else False
				unc_change = True if "uncertainty: **" in change else False

				print("--> %s updated their view rating to %s" % (person.first_name, change))

		else:
			if not show: 
				print("\t%s did not change their mind." % (person.first_name))
			else:
				print("--> %s retained their views of %s" % (person.first_name, old_view.display_verbose()))


	def no_public_opinion(self, agent_name, view):
		"""If there are many groups, then public opinion has not formed."""

		# if not isinstance(agent_name, Person):
		# 	return view

		temp_view = deepcopy(view)
		view = deepcopy(view)

		closest_group, mean_closest_group = self.closest_group_to_view(view)
		_mean_closest = sum([op for op in closest_group]) / len(closest_group)

		view.opinion = (_mean_closest + view.attitude) / 2
		# max_group, min_group = max(closest_group), min(closest_group)
		# view.unc = max([fabs(op - view.opinion) for op in closest_group])

		change = temp_view.display_change_from(view)

		if "Unchanged" in change: 
			self.template_nopubop_closer_journal(agent_name, mean_closest_group, False)
		else:
			self.template_nopubop_closer_journal(agent_name, mean_closest_group, True)
		self.did_view_change(temp_view, view, agent_name, show=False)

		return view


	def internal_debate(self, view, opinion_group, op_str, agent_name):
		"""Internal Debate
			Decides whether the public opinion strength of this group is strong enough for the agent
			to change either it's attitude or its opinion
		""" 
		# Default public threshold
		view = deepcopy(view)
		def_val_pub_thr = 0.6

		# Using a public opinion spectrum we divide the public opinion spectrum into 3 categories: 
		# using 2 thresholds: th1, th2
		th1 = fabs(0.7 - view.unc)
		th2 = def_val_pub_thr if th1 < def_val_pub_thr else th1	  		# 0.6
		public_opinion_expressed = round(mean(opinion_group), 2)

		if op_str < th1: 
			# op_str is too weak for this agent to follow in terms of either attitude or opinion
			# No change in agent attitude or opinion
			self.template_pubop_nsi_nochange_journal(agent_name)
			pass

		elif op_str >= th1 and op_str < th2: 
			"""Private acceptance
				1. Agents with small uncertainty value find the op_str is strong enough to follow
					and change their expressed opinions to match. 
					Since there is now an inconsistency in the expressed opinions and the internal attitudes, 
					the agents will change their internal attitudes to match the external opinions they now express
				2. Agents with large uncertainty values find the op_str is strong enough for them to follow the
					mean opinion. However, the op_str is not strong enough for them to realize they're bending to public pressure
					Thus, they think they follow the pub_op based on their internal attitudes, and change the same to match
				3. ie. any agent in this category will change their internal attitudes and expressed op. to match the 
					mean opinion of the group
			""" 

			# if not self.contemplation: 
			# 	print(agent_name.name, "CSI: ", op_str, th1, th2, view.unc)

			if th1 < th2: 
				self.template_pubop_nsi_change_highunc_journal(agent_name)
			else:
				self.template_pubop_nsi_change_lowunc_journal(agent_name)

			if not self.contemplation and len(opinion_group) > 2: 
				# max_group, min_group = max(opinion_group), min(opinion_group)
				# view.unc = max([fabs(op - view.opinion) for op in opinion_group])				# max(max_group - view.opinion, view.opinion - min_group)
				print("CSI: ", op_str, th1, th2, view.unc)

			view.opinion = public_opinion_expressed
			view.attitude = public_opinion_expressed

		elif op_str >= th2: 
			"""Public conformity
				Public opinion strength is too large. 
				Agents conform to the public opinion with their expressed opinions for group inclusion
				However, they are aware that this doesn't change their inner attitudes
				ie. opinion of the agent changes, but attitude does not
			""" 
			self.template_pubop_nsi_conform_forced_journal(agent_name)
			view.opinion = public_opinion_expressed
			# max_group, min_group = max(opinion_group), min(opinion_group)
			# view.unc = max([fabs(op - view.opinion) for op in opinion_group])

		view.opinion = round(view.opinion, 2)
		view.attitude = round(view.attitude, 2)

		return deepcopy(view)

	def check_normative_social_influence(self, view: View=None, opinion_group=[], agent_name=None):
		f_a = self.calculate_fa(opinion_group)
		f_b = self.calculate_fb(opinion_group)
		f_c = self.calculate_fc(opinion_group, view)

		if not self.contemplation:
			print("%s thought about whether the group opinion was strong enough." % (agent_name))

		# Public Opinion Strength (op_str)
		# Pressure to conform to a group's opinion increases as op_str approaches 1
		# After calculating the op_str agents decide whether or not to conform to the public opinion of the group
		op_str = (f_a + f_b + f_c) / 3

		# if not self.contemplation:
		# 	print("CSI: ", agent_name.name, f_a, op_str)
		# print(op_str, f_a, f_b, f_c)

		final_view = deepcopy(self.internal_debate(view, opinion_group, op_str, agent_name))
		return final_view

	def calculate_fa(self, opinion_group):
			"""Opinion Strength based on: Number of individuals in the opinion group"""
			x = len(opinion_group)
			if(x <= 1):
				return 0
			elif(x >= 10):
				return 1
			else: 
				size_proportion = (x / (len(self.participants) - 1))
				return size_proportion

			# else:
			# 	return (x / 10)


	def calculate_fb(self, opinion_group):
		"""Opinion Strength based on: Group Opinion Homogenity"""
		x = 1 - np.var(opinion_group)
		# Homogenity of opinions / More variance -> less homogenity
		f_b = 1 / (1 + exp(24 * x - 6))
		return f_b


	def calculate_fc(self, opinion_group, view):
		"""Opinion Strength based on: Discrepancy between the agent's 
		internal attitude and the mean public opinion in the group
		"""
		x = round(fabs(view.attitude - mean(opinion_group)), 2)
		return (1 / (1 + exp(-12 * x + 6)))


	#################
	# Jenkspy Implementation 2
	################


	def find_best_grouping_of_opinions(self):
		def small_grouping_opinions():
			# if(len(opinions) < 2):
			# 	return 0    
			opinions.sort()
			maximumGap = 0
			split = 0

			for i in range(len(opinions) - 1):
				if(maximumGap < (opinions[i + 1] - opinions[i])):
					maximumGap = opinions[i + 1] - opinions[i]
					split = opinions[i]
			groups = [[num for num in opinions if num <= split], [num for num in opinions if num > split]]
			opinion_grouping = defaultdict(list)
			participant_grouping = defaultdict(list)
			for group in groups:
				if len(group) > 0: 
					mean_group = round(mean(group), 2) 
					opinion_grouping[mean_group] = group
					for index, op in enumerate(opinions): 
						if op in group: 
							person = self.participants[index]
							participant_grouping[mean_group].append(self.participants[index])

			# print(opinion_grouping, participant_grouping)
			return opinion_grouping, participant_grouping


		def get_classified_ops(zone_indices, participants=False):
			if not participants: 
				array_sort = [np.array([opinions[index] for index in zone]) for zone in zone_indices if zone]
				return array_sort

			else:
				# sorted polygon stats --- sorted array
				array_sort = [[opinions[index] for index in zone] for zone in zone_indices if zone]
				participants_sort = [[self.participants[index] for index in zone] for zone in zone_indices if zone]
				# sorted polygon stats --- sorted array
				opinion_grouping = defaultdict(list)
				participant_grouping = defaultdict(list)
				for index, zone in enumerate([zone for zone in array_sort]): 
					mean_op = round(mean(zone), 2)
					opinion_grouping[mean_op] = [op for op in zone]
					participant_grouping[mean_op] = participants_sort[index]

				return opinion_grouping, participant_grouping


		def goodness_of_variance_fit(nclasses):

			# Breaks will include the min/max of the data 
			# 3 is the min num_classes that is taken into the breaks --> i.e. produces 2 classes 
			classes = jenkspy.jenks_breaks(opinions, nb_class=nclasses)

			# Do actual classification
			classified = np.array([classify(i, classes) for i in opinions])

			# max values of zones
			maxz = max(classified)

			# nested list of zone indices
			zone_indices = [[idx for idx, val in enumerate(classified) if zone + 1 == val] for zone in range(maxz)]

			array_sort = get_classified_ops(zone_indices)

			# sum of squared deviations from array mean
			sdam = np.sum((opinions - np.mean(opinions)) ** 2)

			# sum of squared deviations of class means
			sdcm = sum([np.sum((classified - classified.mean()) ** 2) for classified in array_sort])

			# goodness of variance fit
			gvf = (sdam - sdcm) / sdam

			return gvf, zone_indices

		def classify(value, breaks):
			for i in range(1, len(breaks)):
				if value <= breaks[i]:
					return i
			return len(breaks) - 1


		gvf = 0.0
		nclasses = 2
		opinions = [view.opinion for view in self.views]

		if len(opinions) <= 3:
			return small_grouping_opinions()
			# participant_grouping = {round(mean(opinions), 2): self.participants}
			# opinion_grouping = {round(mean(opinions), 2): opinions}
			# self.template_no_groups_journal(participant_grouping)
			# return opinion_grouping, participant_grouping


		# Goodness of fit set to 0.9
		best_gvf = 0.0
		best_zone_indices = None
		while nclasses < len(opinions) and gvf < 0.9:
			gvf, zone_indices = goodness_of_variance_fit(nclasses)
			if gvf > best_gvf: 
				best_gvf = gvf
				best_zone_indices = zone_indices

			nclasses += 1

		# print("GVF for clustering: ", best_gvf)
		return get_classified_ops(best_zone_indices, participants=True)

		######################################

	def show_final_change_in_views(self):
		views = deepcopy(self.new_views)
		self.original_views.append(views)
		self.views = self.adjust_unc(views)
		self.plot_chart_ops()
		# print("\nOverall Change: Old View \t--> New_Views")
		# for index, each in enumerate(zip(self.original_views[0], self.original_views[-1])): 
		# 	print("%s \n\t\tOld View:%s \n\t\tNew View:%s" % (self.participants[index], each[0].display_verbose(), each[0].display_change_from(each[1])))
		# print("\n----------------------")

	def discussion_chart_vals(self):
		from NPC.Person import Person

		rounds = range(len(self.original_views) - 1)
		person_change_ops = defaultdict(list)
		person_change_unc = defaultdict(list)

		for index, viewset in enumerate(self.original_views[1:]): 
			for index, view in enumerate(viewset[:]):
				person = self.participants[index]
				if not isinstance(person, Person):
					continue
				person_change_ops[person.first_name].append(view.opinion)
				person_change_unc[person.first_name].append(view.unc)

		df_ops = pd.DataFrame.from_dict(person_change_ops)
		df_unc = pd.DataFrame.from_dict(person_change_unc)

		# print(rounds)
		# print(df_ops)

		# print(person_change_unc)
		# print(df_unc)

		return rounds, df_ops, df_unc


	def plot_chart_ops(self):
		rounds, df_ops, df_unc = self.discussion_chart_vals()

		plt.figure(figsize=(10, 10))

		ax1 = plt.subplot(211)
		plt.xticks(np.arange(0, max(rounds) + 1, 1))
		plt.yticks(np.arange(-1.0, 1.25, 0.25), ('Left', 'Moderately Left', 'Lean Left', 'Slightly Lean Left', 'Centrist', 'Slightly Lean Right', 'Lean Right', 'Moderately Right', 'Right', 'Hidden'))
		for person in self.participants[:-1]:
			plt.plot(rounds, person.first_name, data=df_ops, marker='o')
		plt.xlabel('Rounds')
		plt.ylabel('Opinion')

		ax2 = plt.subplot(212, sharex=ax1)
		# plt.xticks(np.arange(0, max(rounds) + 1, 1.0))
		plt.yticks(np.arange(0, 1, 0.10), ('0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'))
		for person in self.participants[:-1]:
			plt.plot(rounds, person.first_name, data=df_unc, marker='o')
		plt.legend([person.first_name for person in self.participants[:-1]], loc='lower right')
		plt.xlabel('Rounds')
		plt.ylabel('Uncertainty')

		plt.show()

		print(df_ops)
		print(df_unc)




	def get_opinion_holders(self, opinion):
		people = [person for index, person in enumerate(self.participants) if self.views[index].opinion == opinion]
		return people

	def template_name_group_members_with_optext(self, group, ops):
		if self.contemplation: 
			return
		group = [member for member in group if member != self.participants[-1]]
		if len(group) > 1:
			return "%s and %s (%s:%s)" % (', '.join(["%s (%s:%s)" % (human.name, Bias.get_bias_text(Bias.get_bias(ops[index]).value), ops[index]) for index, human in enumerate(group[:-1])]), group[-1].name, Bias.get_bias_text(Bias.get_bias(ops[-1]).value), ops[-1])
		elif len(group) == 1 and group[0].name != "the Article":
			return "%s (%s:%s)" % (group[0].name, Bias.get_bias_text(Bias.get_bias(ops[0]).value), ops[0])
		else:
			return "the other view(s)"


	def template_name_group_members(self, group, excludePerson=None):
		if self.contemplation: 
			return
		_group = [person for person in list(set(group)) if person != excludePerson]
		if len(_group) > 1:
			return "%s and %s" % (', '.join(["%s" % (human.name) for human in _group[:-1]]), _group[-1].name)
		elif len(_group) == 1:
			return _group[0].name
		else:
			return "the other view(s)"



######################################################
######### TEMPLATES FOR GROUP OPINIONS ###############
######################################################

	def template_participant_grouping_journal(self):
		if self.contemplation: 
			return

		for opinion, group in self.participant_grouping.items():
			group = list(group)
			ops = self.opinion_grouping[opinion]
			flag_article_in_group = False

			if self.participants[-1] in group: 
				index_article = group.index(self.participants[-1])
				flag_article_in_group = True

			if len(group) > 1:
				if flag_article_in_group: 
					print(random.choice(Discussion.template_grouping_choices_article_agree) % (self.template_name_group_members_with_optext(group, ops)))
				else:
					print(random.choice(Discussion.template_grouping_choices) % (self.template_name_group_members_with_optext(group, ops)))
			elif len(group) == 1 and not flag_article_in_group:
				print(random.choice(Discussion.template_alone_group) % (group[0].name, Bias.get_bias_text(Bias.get_bias(ops[0]).value), ops[0]))
			elif len(group) == 1 and flag_article_in_group:
				print("--> No one agreed with the Article's (%s:%s) view." % (Bias.get_bias_text(Bias.get_bias(ops[0]).value), ops[0]))


	def template_no_groups_journal(self, participant_grouping):
		if self.contemplation: 
			return
		# print(participant_grouping)
		# from NPC.Event import Event
		for op, group in participant_grouping.items():
			group = list(set(group))
			# event = Event(group[0].world.current_date, group)
			# for person in group: 
			# 	journal_msg = random.choice(Discussion.template_no_group_small)
			# 	event.add_to_journal(person, journal_msg)
			print(random.choice(Discussion.template_no_group_small))


	def template_consensus_journal(self, participant_grouping):
		if self.contemplation: 
			return
		# print(participant_grouping)
		# from NPC.Event import Event
		for op, group in participant_grouping.items():
			group = list(set(group))
			# event = Event(group[0].world.current_date, group)
			# for person in group: 
			# 	journal_msg = random.choice(Discussion.template_consensus)
			# 	event.add_to_journal(person, journal_msg)
			print(random.choice(Discussion.template_consensus))

	def template_highunc_journal(self, agent_name):
		if self.contemplation: 
			return
		print(random.choice(Discussion.template_pubop_highUnc) % agent_name)

	def template_pubop_nsi_journal(self, agent_name):
		if self.contemplation: 
			return
		print(random.choice(Discussion.template_pubop_nsi) % (agent_name))


	def template_pubop_nsi_nochange_journal(self, agent_name):
		if self.contemplation: 
			return
		print(random.choice(Discussion.template_pubop_nsi_nochange) % (agent_name))

	def template_pubop_nsi_change_highunc_journal(self, agent_name):
		if self.contemplation: 
			return
		print("%s accepted that their views were outdated. Retaining their views meant risking rejection." % (agent_name))
		print(random.choice(Discussion.template_pubop_nsi_change_highunc) % (agent_name))

	def template_pubop_nsi_change_lowunc_journal(self, agent_name):
		if self.contemplation: 
			return
		print("%s accepted that their views were outdated. Retaining their views meant risking rejection." % (agent_name))
		print(random.choice(Discussion.template_pubop_nsi_change_lowunc) % (agent_name))


	def template_pubop_nsi_conform_forced_journal(self, agent_name):
		if self.contemplation: 
			return
		print(random.choice(Discussion.template_pubop_nsi_conform_forced) % (agent_name))


	def template_nopubop_closer_journal(self, agent_name, mean_closest_group, change=True):
		if self.contemplation: 
			return
		if change == True: 
			people = self.participant_grouping[mean_closest_group]
			if len(people) == 1:
				# then the agent tries to reconcile the difference between their internal attitudes and opinions
				print(random.choice(Discussion.template_nopubop_closer_group_alone) % (agent_name))
			else:
				print(random.choice(Discussion.template_nopubop_closer_group) % (agent_name, self.template_name_group_members(people, agent_name)))
		else:
			print(random.choice(Discussion.template_nopubop_closer_noChange) % (agent_name))

	template_grouping_choices_article_agree = [
		"--> %s agreed with the article's position "
	]

	template_grouping_choices = [
		# Template string + name of other group participants
		"--> %s agreed with each other's views ", 
		"--> %s were in accordance", 
		"--> %s found their views aligned with one another", 
		"--> %s agreed the most with each other", 
		"--> %s sided with one another"
	]

	template_no_group_small = [
		# "No one took sides.", 
		# "There were too few participants to form coalitions.",
		"There weren't enough conversationalists for distinct coalitions to emerge."
	]

	template_consensus = [
		"The participants found they reached a consensus.",
		# "The group realized they were preaching to the choir.",
		# "Everyone realized they were all saying the same thing.",
		# "Everyone agreed upon the basics"
	]

	template_alone_group = [
		"--> %s (%s:%s) disagreed with the rest.",
		# "%s could see groups forming with like minded individuals. But they stood their ground.",
		# "%s refused to budge from their views.",
		# "%s disagreed with the other's views on the article."
	]

	template_pubop_formed = [
		"Public opinion seemed to have formed.",
		# "Public opinion has emerged."
	]

	template_pubop_highUnc = [
		"%s was very uncertain about their own views. \n\tThey decided their personal attitudes aligned with the majority opinion and changed their mind accordingly.",
		# "Uncertain as %s was, agreeing with the majority opinion seemed like the safest option. ",
		# "Uncertain and unable to make up their mind, %s decided the majority was right."
	]

	template_pubop_nsi = [
		# "%s realized they were experiencing cognitive dissonance between the opinions they were expressing and the point of view that they held.",
		# "%s realized that their opinions didn't really match what they believed",
		"""%s realized the opinion they expressed was inconsistent with their internal attitude on the article.\n\tThey looked for the group with views closest to their own expressed opinions."""
	]


	template_pubop_nsi_nochange = [
		"""After an internal debate %s realized that the strength of the group's convictions was too weak.\n\tThey maintained their opinions.""",
		# "However, the public opinion did not sway %s. They maintained their views."
	]

	# High uncertainty
	template_pubop_nsi_change_highunc = [
		# "%s felt this group's opinion best captured their own and changed their mind.",
		# "%s felt the majority opinion was a better representation of their own attitudes, and changed their mind.",
		"""%s felt that the group's views represented a natural evolution of their own attitudes.\n\t They modified their opinions and attitudes to match.""", 
		# "%s felt they agreed with the majority"
	]

	# Low uncertainty
	template_pubop_nsi_change_lowunc = [
		"""The group opinion was strong enough to sway %s.\n\tThey accepted the group's views and changed their opinions and attitudes to match.""",
		# "Convinced by the majority opinion, $s changed their views on the article.",
		# "%s was swayed by the public opinion. They changed their views to match.", 
		# "Convinced by the public opinion, %s changed their mind on the matter."
	]

	template_pubop_nsi_conform_forced = [
		"""%s grew aware of the peer pressure to conform to the group's views. \n\tHowever, they were aware the group's opinions did not agree with their internal attitudes on the matter.\n\tThey pretended to agree with the group to avoid exclusion from their midst."""
		# "Unable to convince the others, %s stayed silent.",
		# "%s decided it was best to pretend to agree with the others.",
		# "Not wanting to be ridiculed, %s decided to pretend they agreed with the public opinion.",
		# "%s remained unconvinced by the public opinion and stayed silent."
	]

	template_nopubop_closer_group_alone = [
		"%s did not agree with the other opinions. \n\tThey realized their expressed opinions did not truly match their internal attitudes.\n\tThey tried to reconcile the difference."
	]

	template_nopubop_closer_group = [
		# Agent tries to reconcile the difference between their attitude and the opinions of the others in the closest group
		"%s was swayed by %s's argument.\n\tThey decided to change their rating to indicate the same."
	]

	template_nopubop_closer_noChange = [
		"%s decided the group's views were insufficient to change their opinions."
	]
