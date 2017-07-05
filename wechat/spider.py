from bs4 import BeautifulSoup
from pymongo import MongoClient

import datetime
import json
import re

from xml.sax.saxutils import unescape

mongodbauth=False
username="jiangdunchuan"
password="jiangdunchuan"
dbname="wechat"
collection_official_accounts="official_accounts"
collection_articles="articles"
dbaddress="localhost:27017"

account_save_max_articles=15 #若该值为0，则代表保存截获到的所有文章列表


html_unescape_table = {
	"&quot;":"\"",
	"&apos;":"\'",
	"&nbsp;":" ",
	"&amp;":"&",
	}

def html_unescape(text):
	return unescape(text, html_unescape_table)


def get_article(app_msg_ext_info, date):
	pattern_biz = re.compile(r"__biz=(.*?)&")
	pattern_mid = re.compile(r"mid=(.*?)&")
	pattern_idx = re.compile(r"idx=(.*?)&")
	pattern_slash = re.compile(r"\\/")
	title = app_msg_ext_info["title"]
	content_url = app_msg_ext_info["content_url"]
	content_url = re.sub(pattern_slash, r"/", content_url)
	__biz = pattern_biz.search(content_url).group(1)
	mid = pattern_mid.search(content_url).group(1)
	idx = pattern_idx.search(content_url).group(1)
	article = {
		"title":title,
		"content_url":content_url,
		"datetime":date,
		"__biz":__biz, 
		"mid":mid,
		"idx":idx
	}
	return article



def response(flow):
	path_components = None
	content = None
	request = flow.request
	response = flow.response
	if (request.host == "mp.weixin.qq.com"):
		path_components = request.path_components
		query = request.query
		if (len(path_components) == 1 and path_components[0] == "s"):

			if not (("__biz" in query) and ("mid" in query) and ("idx" in query)):
				print("Error:url query format is wrong! Location 1.")
				return

			print("pretty_url:%s" % (flow.request.pretty_url))

			__biz = query["__biz"]
			mid = query["mid"]
			idx = query["idx"]

			print("__biz:%s mid:%s idx:%s" % (__biz, mid, idx))

			content = response.content

			document = BeautifulSoup(content, "html.parser")
			rich_media_content = document.find("div", class_="rich_media_content", id="js_content")
			user = document.find("a", id="post-user")
			date = document.find("em", id="post-date")
			title = document.find(id="activity-name")
			tag = document.find("span", id="copyright_logo")
			url = flow.request.pretty_url

			print("user:%s date:%s title:%s" % (user.get_text(), date.get_text(), title.get_text().strip()))
			print("tag is %s" % ("None" if tag == None else tag.get_text()))

			if mongodbauth:
				client = MongoClient('mongodb://%s:%s@%s' % (username, password, dbaddress))
			else:
				client = MongoClient('mongodb://%s' % dbaddress)
			db=client[dbname]
			collection=db[collection_articles]

			if collection.find({"__biz":__biz,"mid":mid,"idx":idx}).count() != 0:
				print("Warning:Find Duplicate articles(%s)" % flow.request.pretty_url)
				return 

			post = {"__biz":__biz,
					"mid":mid,
					"idx":idx,
					"title":title.get_text().strip(),
					"user":user.get_text(),
					"date":date.get_text(),
					"tag":"None" if tag == None else tag.get_text(),
					"url":flow.request.pretty_url,
#					"like_num":0,
#					"read_num":0,
					"create_time":datetime.datetime.utcnow(),
					"last_modify_time":datetime.datetime.utcnow(),
					"rich_media_content":rich_media_content.get_text()}
			collection.insert(post)

			client.close()

		elif (flow.request.method == "POST" and len(path_components) == 2 and path_components[0] == "mp" and path_components[1] == "getappmsgext"):

			if not (("__biz" in query) and ("mid" in query) and ("idx" in query)):
				print("Error:url query format is wrong! Location 2.")
				return

			__biz = query["__biz"]
			mid = query["mid"]
			idx = query["idx"]				

			data = json.loads(response.content)

			if "appmsgstat" in data.keys():
				appmsgstat = data["appmsgstat"]
				like_num = appmsgstat.get("like_num", "")
				read_num = appmsgstat.get("read_num", "")

				if like_num == "" or read_num == "":
					print("Error:like_num or read_num is invalid!")
					return

				if mongodbauth:
					client = MongoClient('mongodb://%s:%s@%s' % (username, password, dbaddress))
				else:
					client = MongoClient('mongodb://%s' % dbaddress)
				db = client[dbname]
				collection = db[collection_articles]

				collection.update({"__biz":__biz,"mid":mid,"idx":idx}, {"$set":{"like_num":like_num, "read_num":read_num, "last_modify_time":datetime.datetime.utcnow()}})
				client.close()

				print("like_num:%s read_num:%s" % (like_num, read_num))

		elif (flow.request.method == "GET" and len(path_components) == 2 and path_components[0] == "mp" and path_components[1] == "appmsg_comment"):
			if not (("__biz" in query) and ("appmsgid" in query) and ("idx" in query) and ("action" in query)):
				print("Error:url query format is wrong! Location 3.")
				return

			if (query["action"] == "getcomment"):
				__biz = query["__biz"]
				mid = query["appmsgid"]
				idx = query["idx"]			

				data = json.loads(response.content)
				if "elected_comment" in data.keys():
					comments = data["elected_comment"]

					if mongodbauth:
						client = MongoClient('mongodb://%s:%s@%s' % (username, password, dbaddress))
					else:
						client = MongoClient('mongodb://%s' % dbaddress)
					db = client[dbname]
					collection = db[collection_articles]
					collection.update({"__biz":__biz,"mid":mid,"idx":idx}, {"$set":{"elected_comment":comments, "last_modify_time":datetime.datetime.utcnow()}})
					client.close()
				

		elif (flow.request.method == "GET" and len(path_components) == 2 and path_components[0] == "mp" and path_components[1] == "profile_ext"):

			if not (("__biz" in query) and ("action" in query)):
				print("Error:url query format is wrong! Location 4.")
				return

			if (query["action"] == "home"):
				__biz = query["__biz"]

				content = response.text
				
				document = BeautifulSoup(content, "html.parser")
				user = document.find("strong", class_="profile_nickname", id="nickname")
				nickname = user.get_text().strip()
				print("user:%s" % nickname)

				content = html_unescape(content)
				#print("-----------------------------------")
				#print(content)
				#print("-----------------------------------")
				pattern = re.compile(r"var msgList = '(.*?)';")
				match = pattern.search(content)
				if match == None:
					print("Error:Not found magList.")
					return
				msg_list_str = match.group(1)
				#print("-----------------------------------")
				#print("msgList is %s." % msg_list_str)
				#print("-----------------------------------")
				msg_list_json = json.loads(msg_list_str)
				msg_list = msg_list_json["list"]

				articles = []
				for msg_item in msg_list:
					if (account_save_max_articles != 0) and (len(articles) == account_save_max_articles):
						print(len(articles))
						break
					#print("-----------------------------------")	
					#print(msg_item)
					#print("-----------------------------------")
					comm_msg_info = msg_item["comm_msg_info"]
					msg_type = comm_msg_info["type"]
					date = comm_msg_info["datetime"]
					if msg_type != 49:
						print("Notice:Recv a message type is %d nickname:%s." % (msg_type, nickname))
						continue
					app_msg_ext_info = msg_item["app_msg_ext_info"]
					article = get_article(app_msg_ext_info, date)
					articles.append(article)

					if app_msg_ext_info["is_multi"] == 1:
						msg_list_sub = app_msg_ext_info["multi_app_msg_item_list"]
						for msg_item_sub in msg_list_sub:
							if (account_save_max_articles != 0) and (len(articles) == account_save_max_articles):
								print(len(articles))
								break
							article = get_article(msg_item_sub, date)
							articles.append(article)

				#print("-----------------------------------")
				#print(articles)
				#print("-----------------------------------")

				if mongodbauth:
					client = MongoClient('mongodb://%s:%s@%s' % (username, password, dbaddress))
				else:
					client = MongoClient('mongodb://%s' % dbaddress)
				db = client[dbname]
				collection = db[collection_official_accounts]

				collection.update({"__biz":__biz,"nickname":nickname}, {"$set":{"articles":articles}}, True, False)
				client.close()							

			elif (query["action"] == "getmsg"):
				#must todo something.
				pass
