"""
Selenium-driven web crawler to extract problem data from Leetcode
Author: Brighton Balfrey

For scraping name, difficulty, and description for problems
on Leetcode. Requires dependencies outlined in `requirements.txt` along
with a chromedriver executable in the dir that the script is called.
Furthermore, a `html/leetcode` html file is also required in the same
dir. This HTML is a full list of every leetcode question on leetcode.com.
Because that is a central source of truth that we want to remain static
and version, we keep the version of that page checked into the same
repository as the script.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", default="./chromedriver")
os.chmod(CHROME_DRIVER_PATH, 755)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-setuid-sandbox")
problem_list_html = open("html/leetcode_01").read()
LEETCODE_BASE_PROBLEM_URL = "https://leetcode.com/problems/"
LEETCODE_PROBLEM_TAG_BASE_URL = "https://leetcode.com/tag/"
bs_problem_list = BeautifulSoup(problem_list_html, 'html5lib')
driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)

def get_all_leetcode_problem_links(problem_list, base_url) :
	"""
	Given a beautiful soup object with html containing list page of all
	problems on leetcode, parse out all of the unique problem url's
	:param problem_list - beautiful soup object containing the page
	:param base_url - the base url of all problems on leetcode
	:return list of valid question uris
	"""
	return list(dict.fromkeys([
		a['href'] for a in problem_list.select('a')
		if base_url in a['href']]
	))

class Page_Result :
	"""
	Helper class to store data extracted from the page
	"""
	class Topic :
		def __init__(self, name, uri) :
			self.name = name
			self.uri = uri
		def toDict(self) :
			return {
				"uri": self.uri,
				"name": self.name
			}
		def __hash__(self) :
			return hash((self.uri, self.name))
	def __init__(self, uri, id, name, difficulty, description, topics) :
		self.name = name
		self.id = id
		self.difficulty = difficulty
		self.description = description
		self.uri = uri
		self.topics = topics
	def toDict(self) :
		return {
			"id": self.id,
			"title": self.name,
			"uri": self.uri,
			"difficulty": self.difficulty,
			"description": self.description,
			"topics": [t.toDict() for t in self.topics]
		}

def is_question_loaded(driver) :
	"""
	Given a valid Leetcode page Selenium driver, return true when
	the page is loaded
	:param driver - Selenium driver rendering Leetcode page
	:return true if page is fully rendered, false otherwise
	"""
	return not (
		driver.title.lower() == "loading..."
		or driver.title.lower() == "loading question... leetcode"
		or driver.title.lower() == "loading question...")

def get_question_title(driver):
	"""
	Given a valid Leetcode page's Selenium driver, return the
	question's title
	:param driver - Selenium driver with rendered Leetcode question page
	:return question title
	"""
	return driver.title.replace(" - LeetCode", "")

def get_question_id(driver) :
	"""
	Given a valid Leetcode page's Selenium driver, return the
	question's id
	:param driver - Selenium driver with rendered Leetcode question page
	:return question id
	"""
	return driver.find_element_by_css_selector('.css-v3d350').text.split('.')[0].strip()

def get_question_difficulty(driver) :
	"""
	Given a valid Leetcode page's Selenium driver, return the
	question's difficulty
	:param driver - Selenium driver with rendered Leetcode question page
	:return question difficulty
	"""
	difficulty_unparsed = driver.find_element_by_css_selector(".css-10o4wqw").text
	return ''.join(
		[c for c in difficulty_unparsed if not c.isdigit()]
	).replace("Add to List", "").replace("Share", "").strip()

def get_question_content(driver) :
	"""
	Given a valid Leetcode page's Selenium driver, return the
	question's content/description
	:param driver - Selenium driver with rendered Leetcode question page
	:return question content
	"""
	return driver.find_element_by_xpath("//div[contains(@class, 'content__u3I1') and contains(@class, 'question-content__JfgR')]").text

def get_question_topics(driver) :
	"""
	Given a valid Leetcode page's Selenium driver, return the
	question's related tags/topics
	:param driver - Selenium driver with rendered Leetcode question page
	:return topics extracted from the topic
	"""
	return [
		Page_Result.Topic(
			t.get_attribute("href").replace(LEETCODE_PROBLEM_TAG_BASE_URL, "").replace("/", "").replace("-", " "),
			t.get_attribute("href")
		)
		for t in driver.find_elements_by_css_selector('.topic-tag__1jni')
	]

def parse_pages(problem_list) :
	"""
	Given a list of URLs pointing to leetcode questions, extract necessary
	information using selenium driven web crawling.
	:param problem_list - array of problem uris
	:return tuple (results list, question topics list)
	"""
	results = []
	question_topics = set()
	def parse_page(problem_uri) :
		driver.get(problem_uri)
		time.sleep(3)
		while not is_question_loaded(driver) : 
			time.sleep(1)
		try :
			question_title = get_question_title(driver)
			question_id = get_question_id(driver)
			difficulty = get_question_difficulty(driver)
			content = get_question_content(driver)
			topics = get_question_topics(driver)
			results.append(
				Page_Result(problem_uri,
					question_id,
					question_title,
					difficulty,
					content,
					topics
				)
			)
			for t in topics : question_topics.add(t)
			print(results)
			print(topics)
		# We want our script to continue and not error out
		except Exception as e :
			print("Error {}".format(e))
	for uri in problem_list : parse_page(uri)
	return results, question_topics

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
		json.dump(obj=res, fp=f, indent=4)

if __name__ == "__main__":
	run()
