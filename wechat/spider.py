from bs4 import BeautifulSoup
from pymongo import MongoClient

import datetime
import json
import re

username="jiangdunchuan"
password="jiangdunchuan"
dbname="wechat"
collectionname="articles"
dbaddress="localhost"


def check_url_query(query):
	if ("__biz" in query) and ("mid" in query) and ("idx" in query):
		return True
	else:
		return False



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

			html = BeautifulSoup(content, "html.parser")
			rich_media_content = html.find("div", class_="rich_media_content", id="js_content")
			user = html.find("a", id="post-user")
			date = html.find("em", id="post-date")
			title = html.find(id="activity-name")
			tag = html.find("span", id="copyright_logo")
			url = flow.request.pretty_url

			print("user:%s date:%s title:%s" % (user.get_text(), date.get_text(), title.get_text().strip()))
			print("tag is %s" % ("None" if tag == None else tag.get_text()))

			client = MongoClient('mongodb://%s:%s@%s' % (username, password, dbaddress))
			db=client[dbname]
			collection=db[collectionname]

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

				client = MongoClient('mongodb://%s:%s@%s' % (username, password, dbaddress))
				db=client[dbname]
				collection=db[collectionname]

				collection.update({"__biz":__biz,"mid":mid,"idx":idx}, {"$set":{"like_num":like_num, "read_num":read_num, "last_modify_time":datetime.datetime.utcnow()}})
				client.close()

				print("like_num:%s read_num:%s" % (like_num, read_num))

		elif (flow.request.method == "GET" and len(path_components) == 2 and path_components[0] == "mp" and path_components[1] == "profile_ext"):

			if not (("__biz" in query) and ("action" in query)):
				print("Error:url query format is wrong! Location 3.")
				return

			if (query["action"] == "home"):
				__biz = query["__biz"]


				content = response.content
				content = content.replace("&quot;", '\"')

				html = BeautifulSoup(content, "html.parser")
				print("-----------------------------------")
				print(html)
				print("-----------------------------------")

				pattern = re.compile(r'hello')
				match1 = pattern.match('hello world!')
