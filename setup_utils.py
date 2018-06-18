import json
from Knowledge.Source import Source
from Knowledge.Topic import Topic
from Knowledge.Article import Article



def add_initial_media_sources(knowledge):
	with open("AllSides/sources.json") as sources_file: 
		data = json.load(sources_file)
		for source in data.values(): 
			new_source = Source(source['title'], source['rating'], source['url'])
			knowledge.add_source(new_source)


def add_initial_topics(knowledge):
	with open("AllSides/topics.json") as topics_file: 
		data = json.load(topics_file)
		for topic in data:
			new_topic = Topic(topic['title'], topic['description'], topic['url'])
			knowledge.add_topic(new_topic)


def add_initial_articles(knowledge):
	with open("AllSides/articles.json") as articles_file: 
		data = json.load(articles_file)
		for topic_title, articles in data.items():

			topic = Topic.get_topic_by_title(topic_title)
			if not topic: 
				topic = Topic(topic_title)
				knowledge.add_topic(topic)

			for article in articles: 
				source_title = article['source']
				source = Source.get_source_by_title(source_title)

				if not source: 
					source = Source(source_title, article['rating'])
					knowledge.add_source(source)

				title = article['title']
				rating = article['rating']
				description = article['description']
				url = article['url']
				opinion = article['opinion']

				new_article = Article(title, source, description, url, rating, opinion)
				new_article.add_topic(topic)
				knowledge.add_article(new_article)