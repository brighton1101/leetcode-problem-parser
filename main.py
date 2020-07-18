"""
Selenium-driven web crawler to extract problem data from Leetcode
Author: Brighton Balfrey

For scraping name, difficulty, and description for problems
on Leetcode. Requires dependencies outlined in `requirements.txt` along
with a chromedriver executable in the dir that the script is called.
Furthermore, a `leetcode.html` html file is also required in the same
dir. This HTML is a full list of every leetcode question on leetcode.com.
Because that is a central source of truth that we want to remain static
and version, we keep the version of that page checked into the same
repository as the script.
"""
from selenium import webdriver
from bs4 import BeautifulSoup
from threading import Thread
import time
import json
import os

"""
Some initial setup that can be played with. Location of the chromedriver
executable, giving that executable permissions, opening up the 'source of
truth' html file, initializing Beautiful Soup, initializing Selenium Webdriver
"""
CHROME_DRIVER_PATH = "./chromedriver"
os.chmod(CHROME_DRIVER_PATH, 755)
problem_list_html = open("leetcode.html").read()
LEETCODE_BASE_PROBLEM_URL = "https://leetcode.com/problems/"
bs_problem_list = BeautifulSoup(problem_list_html, 'html5lib')
driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)

def get_all_leetcode_problem_links(problem_list, base_url) :
	"""
	Given a beautiful soup object with html containing list page of all
	problems on leetcode, parse out all of the unique problem url's
	:param problem_list - beautiful soup object containing the page
	:param base_url - the base url of all problems on leetcode
	"""
	return list(dict.fromkeys([
		a['href'] for a in problem_list.select('a')
		if base_url in a['href']]
	))

class Page_Result :
	"""
	Helper class to store results from individual problems' pages.
	"""
	def __init__(self, uri, name, difficulty, description) :
		self.name = name
		self.difficulty = difficulty
		self.description = description
		self.uri = uri
	def toDict() :
		return {
			"title": self.name,
			"uri": self.uri,
			"difficulty": self.difficulty,
			"description": self.description
		}

def parse_pages(problem_list) :
	"""
	Given a list of URLs pointing to leetcode questions, extract necessary
	information using selenium driven web crawling.
	:param problem_list - array of problem uris
	"""
	results = []
	def parse_page(problem_uri) :
		driver.get(problem_uri)
		time.sleep(3)
		while driver.title.lower() == "loading..." or driver.title.lower() == "loading question... leetcode" or driver.title.lower() == "Loading Question...": 
			time.sleep(1)
		try :
			question_title = driver.title.replace(" - LeetCode", "")	
			difficulty_unparsed = driver.find_element_by_css_selector(".css-10o4wqw").text
			difficulty = ''.join(
				[c for c in difficulty_unparsed if not c.isdigit()]
			).replace("Add to List", "").replace("Share", "").strip()
			content = driver.find_element_by_xpath("//div[contains(@class, 'content__u3I1') and contains(@class, 'question-content__JfgR')]").text
			results.append(
				Page_Result(problem_uri,
					question_title,
					difficulty,
					content
				)
			)
		# We want our script to continue and not error out
		except :
			pass
	for uri in problem_list : parse_page(uri)
	return results

def run() :
	"""
	A runner script. Right now, very rough, to say the least. Just for demonstration purposes,
	when we figure out what more we need to add, more will be added.
	"""
	problem_uris = get_all_leetcode_problem_links(bs_problem_list, LEETCODE_BASE_PROBLEM_URL)
	problems = parse_pages(problem_uris)
	res = {}
	res['status'] = "success"
	res['results'] = [p.toDict() for p in problems]
	print(res)
	with open("result.json", 'w') as f :
		json.dump(res, f)

if __name__ == "__main__":
	run()
