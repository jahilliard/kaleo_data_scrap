# Probably should break this controller up, but time constrainsts...

from lxml import html
import csv
import os.path
import asyncio
import aiohttp
import urllib
from classes import Category as cat
from classes import Subcategory
from classes import Document

all_subcategorries = []
all_docs = []

def read_categories_to_load(file_name = 'category_list/category_list.csv'):
	categories = []
	# Read in Category List if csv exists... if not load default categories
	if os.path.isfile(file_name):
		with open(file_name, 'r') as csvfile:
			category_list = csv.reader(csvfile, delimiter=',', quotechar='|')
			for category in category_list:
				try: 
					if category[0][:3] != "###":
						categories.append(cat.Category(name = category[0].strip().replace("_", " "), 
							url = "https://en.wikipedia.org/wiki/Category:" + category[0].strip()))
				except IndexError:
					# IndexError is okay here, because user may 
					# include extra lines in category list by mistake
					continue
	else:
		print("Custom category load file not found! Loading Default categories!")
		categories = [cat.Category(name= 'Machine_learning'.replace ("_", " ") , 
						url = "https://en.wikipedia.org/wiki/Category:Machine_learning"), 
						cat.Category(name= 'Business_software'.replace ("_", " ") , 
						url = "https://en.wikipedia.org/wiki/Category:Business_software")]
	return categories


@asyncio.coroutine
def load_page_async(url, category = None, is_subpage = False):
	exists = True
	connector = aiohttp.TCPConnector(verify_ssl=False)
	with aiohttp.ClientSession(connector=connector) as session:
		with aiohttp.Timeout(20):
			response = yield from session.get(urllib.parse.unquote(url))
			if response.status == 200:
				content = yield from response.read()
			else:
				print(url + " does not exist")
				exists = False
	if is_subpage == False and exists == True:
		manipulate_content(content, category,  is_subpage = False)
	elif is_subpage == True and exists == True:
		manipulate_content(content, category,  is_subpage = True)
	else:
		pass

def manipulate_content(content, category = None, is_subpage = False):
	doc = html.fromstring(content)
	if is_subpage == False:
		for page in doc.get_element_by_id("mw-pages").find_class("mw-category-group"):
			all_subcategorries.append([Subcategory.Subcategory(url = "https://en.wikipedia.org" + link_data[2],
 														name =  link_data[2][6:].replace("_", " "),
 														category = category)
										for link_data in page.iterlinks()])
	else:
		all_docs.append(Document.Document(subcategory = category, full_text = remove_tags(doc)))

def remove_tags(doc):
	return ' '.join(doc.get_element_by_id("bodyContent").itertext())

# ['Machine_learning', 'Business_software', 'Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software', 'Machine_learning', 'Business_software', 'Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software','Machine_learning', 'Business_software']
def load_categories_from_wikipedia(categories, is_subpage = False):
	# async lib runs O(log(n))... requests is O(n)
	# TODO: figure out how to load to async queue
	async_tasks = []
	loop = asyncio.get_event_loop()
	if len(categories) == 0 and is_subpage == True:
		loop.close()
		return []
	for item in categories:
		if is_subpage == False:
			if not item.was_subcategory_queried():
				action_item = asyncio.ensure_future(load_page_async(url = item.url, 
					category = item, is_subpage = is_subpage))
				async_tasks.append(action_item)
		else:
			action_item = asyncio.ensure_future(load_page_async(url = item.url, 
				category = item, is_subpage = is_subpage))
			async_tasks.append(action_item)
	if len(async_tasks) > 0:
		loop.run_until_complete(asyncio.wait(async_tasks))
	if is_subpage == True:
		loop.close()
		return all_docs
	return all_subcategorries


