from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

try:
	import tqdm
except ImportError:
	print("TQDM not installed, simple timer will be used")

import logging
from traceback import print_exc
from random import choice, randint
from time import time, sleep

from os import getcwd, getlogin
from os.path import isfile, isdir
from datetime import datetime

###### CONFIGS ######
MAX_WEBDRIVER_WAIT = 100

EDGE_EXE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
EDGE_PROFILE_DIR = f"C:\\Users\\{getlogin()}\\AppData\\Local\\Microsoft\\Edge\\User Data"
EDGE_PROFILE_NAME = "Default"

MAX_SEARCH_POINTS = {
	'mobile':100,
	'desktop':150,
}
POINTS_PER_SEARCH = 5
###### CONFIGS ######

class wait_for_page_load(object):
	def __init__(self, browser, timeout = None):
		self.start = time()
		try:
			self.timeout = int(timeout)
		except:
			self.timeout = MAX_WEBDRIVER_WAIT
		self.browser = browser
	
	def __enter__(self):
		try:
			self.old_page = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
		except:
			self.old_page = None
		self.timeout = max(5, self.timeout - (time() - self.start))
	
	def page_has_loaded(self):
		new_page = self.browser.find_element(By.TAG_NAME, 'html')
		return new_page.id != self.old_page.id
	
	def __exit__(self, *_):
		timeout_at = time() + self.timeout
		while not self.page_has_loaded:
			if time() > timeout_at:
				refresh_btn = self.browser.find_element(By.ID, 'reload-button')
				if refresh_btn:
					refresh_btn.click()
					self.browser.implicitly_wait(5)
					timeout_at = time() + (self.timeout / 2)
				else:
					timeout_at = time() + (self.timeout / 2)
			pass
		tqdm_sleep(randint(1,10)/2) #randomizer, anti-ban

def tqdm_sleep(t: float):
	"""Sleeps with printing the remaining time to console
	# if tqdm not installed, no worries, it will use simple sleep display
	Args:
		t (float): time to sleep
	"""
	end_at = time() + t
	try:
		pbar = tqdm.tqdm(total=t, bar_format="Anti-ban sleep: {n:.5f}")
		while end_at > time():
			pbar.n = end_at - time()
			pbar.refresh()
		pbar.close()
	except:
		print(f"anti ban, sleep for: {t}")
		while time() < end_at:
			pass

def do_quest(driver:webdriver):
	"""Prerequisite: page is on a quest.
	Clicks on the next available task for the quest

	Args:
		driver (webdriver): webdriver
	"""
	with wait_for_page_load(driver):
		driver.execute_script("document.querySelector('.punchcard-row').querySelector('a').click()")

def poll(driver:webdriver) -> bool:
	"""
	If the loaded page has a poll, do the poll.
	Args:
		driver (webdriver): webdriver

	Returns:
		bool: True if a poll was completed, otherwise False
	"""
	try:
		overlay = driver.find_element(By.CSS_SELECTOR, 'div.bt_poll')
		selection = choice(overlay.find_elements(By.CSS_SELECTOR, ".btOption.b_cards"))
		with wait_for_page_load(driver):
			WebDriverWait(driver, 60).until(EC.element_to_be_clickable(selection)).click()
			tqdm_sleep(randint(1,4))
	except:
		# page does not have poll, or some other arbitrary error
		return False
	return False

def select_x_of_y_overlay(driver:webdriver) -> bool:
	"""
	If the loaded page has a multiple choice or multi-select overlay option, do it until completed.
	Args:
		driver (webdriver): webdriver

	Returns:
		bool: True if a select x of y overlay was completed, otherwise False
	"""
	try:
		driver.find_element(By.CSS_SELECTOR, "div.TriviaOverlayData")
	except:
		# page does not have a select x of y overlay.
		return False
	# start button
	try:
		btn = driver.find_element(By.CSS_SELECTOR, 'input[value="Start playing"]')
		WebDriverWait(driver, 60).until(EC.element_to_be_clickable(btn)).click()
		#btn.click()
	except:
		return False
	is_done = False
	while not is_done:
		with wait_for_page_load(driver):
			driver.execute_script("Array.from(document.querySelectorAll('input.rqOption')).filter(e=>!e.classList.contains('optionDisable'))[0].click()")
			sleep(2)
			try:
				is_done = driver.find_element(By.CSS_SELECTOR, 'div.cico.rqSumryLogo').find_element(By.CSS_SELECTOR, 'img[alt="Checkmark Image"]')
			except:
				pass
	return True

def multiple_choice_inpage(driver:webdriver) -> bool:
	"""
	If the loaded page has an in-page (not overlay) multiple choice question, do it until completed.
	Args:
		driver (webdriver): webdriver

	Returns:
		bool: True if a multiple choice question series was completed, otherwise False
	"""
	try:
		opts = driver.find_elements(By.CSS_SELECTOR, "div.wk_OptionClickClass")
		if not opts:
			# not a multiple choice page option
			return False 
	except:
		# not a multiple choice page option
		return False
	while opts:
		# chose random button and click
		with wait_for_page_load(driver):
			# select a random options
			chosen = choice(opts)
			WebDriverWait(driver, 60).until(EC.element_to_be_clickable(chosen)).click()
		with wait_for_page_load(driver):
			# click next question / get your score button
			nxt_btn = driver.find_element(By.CSS_SELECTOR, "div.wk_button")
			WebDriverWait(driver, 60).until(EC.element_to_be_clickable(nxt_btn)).click()
			
		# do we have more options?
		opts = driver.find_elements(By.CSS_SELECTOR, "div.wk_OptionClickClass")
	return True

def complete_task(driver:webdriver) -> bool:
	"""Attempts to complete the task that was opened in a new tab.

	Args:
		driver (webdriver): webdriver

	Returns:
		bool: True on completion
	"""
	if not driver.current_url.lower().strip().startswith("https://www.bing.com/search?"):
		# if the webpage isnt a search type, its probably nothing left to do
		return True
	# attempt to run each type of task completion on it. 
	# sometimes the overlay is slow to load so give it an extra 2.5 seconds
	tqdm_sleep(2.5)
	task_completion_types = [multiple_choice_inpage, select_x_of_y_overlay, poll]
	for task_completion_func in task_completion_types:
		if task_completion_func(driver):
			# on successful completion, dont need to try to do the other types, return for next task.
			return True
	# if you get here its probably just a search with nothing else to do
	tqdm_sleep(randint(1,5))
	return True

def do_searches(driver:webdriver, max_points:int):
	"""Attempts to do the searches that meets the given amount of points to get.
	This is not bullet proof and might actually get run more than once if the points dont register quickly.

	Args:
		driver (webdriver): webdriver
		max_points (int): the maximum points you want to get searches for.
	"""
	for search in range(0, max_points, POINTS_PER_SEARCH):
		with wait_for_page_load(driver):
			# go to and wait for page to finish loading
			# to ensure a unique search is done, we just search the current timestamp
			driver.get(f"https://bing.com/search?q={time()}")

def searches()->webdriver:
	"""
	If you havent met the max search points for the day, will do the searches.
	Gets the proper browser with specific user agent (desktop or mobile) and does the searches.

	Returns:
		webdriver: the leftover webdriver (its in desktop mode)
	"""
	driver = get_driver('desktop')
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/pointsbreakdown')
	try:
		needs_search = any([len(set([int(x) for x in p.text.split(' / ')]))>1 for p in driver.find_elements(By.CSS_SELECTOR, 'p.pointsDetail.c-subheading-3.ng-binding')])
	except:
		needs_search = True
	if not needs_search:
		return driver
	for mode in MAX_SEARCH_POINTS:
		if driver:
			print("need to restart browser")
			driver.quit()
			tqdm_sleep(1)
		driver = get_driver(mode)
		do_searches(driver, MAX_SEARCH_POINTS[mode])
	return driver

def tasks(driver:webdriver) -> webdriver:
	"""
	Attempts to do all of the available tasks, including daily.
	
	Args:
		driver (webdriver): the webdriver
	
	Returns:
		webdriver: the leftover webdriver (its in desktop mode)
	"""
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/')
	og = driver.current_window_handle
	# one task at a time so it dosent combine
	try:
		tasks = driver.find_elements(By.CSS_SELECTOR, ".mee-icon-AddMedium")
	except:
		print("uh oh, spaghetti-o, couldn't find taks to do, do this by hand or re-run?")
		tasks = []
	for taskidx, task in enumerate(tasks, start=1):
		prev_tabs = driver.window_handles
		WebDriverWait(driver, MAX_WEBDRIVER_WAIT).until(EC.element_to_be_clickable(task)).click()
		try:
			WebDriverWait(driver, MAX_WEBDRIVER_WAIT/5).until(EC.number_of_windows_to_be(len(prev_tabs)+1))
			new_tab = [x for x in driver.window_handles if x not in prev_tabs]
			print(f"task #{taskidx} opened {len(new_tab)} new tabs")
			for t in new_tab: 
				driver.switch_to.window(t)
				complete_task(driver)
				driver.close()
		except TimeoutException:
			try:
				# MAYBE ITS NOT A NEW TAB KIND OF TASK BUT RATHER A POPUP THINGY, IF SO JUST CLICK X AND CONTINUE
				WebDriverWait(driver, MAX_WEBDRIVER_WAIT/5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.c-glyph.glyph-cancel"))).click()
			except:
				pass
		for t in [x for x in driver.window_handles if x not in prev_tabs]:
			tqdm_sleep(1)
			driver.switch_to_window(t)
			driver.close()
		WebDriverWait(driver, 60).until(EC.number_of_windows_to_be(len(prev_tabs)))
		driver.switch_to.window(og)
	return driver

def quests(driver:webdriver) -> webdriver:
	"""_summary_

	Args:
		driver (webdriver): the webdriver

	Returns:
		webdriver: the leftover webdriver (its in desktop mode)
	"""
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/')
	og = driver.current_window_handle
	new_tabs = driver.window_handles
	# you can do all quests at once because they dont interfere with eachother
	driver.execute_script("Array.from(document.querySelectorAll('li.ng-scope')).forEach(e=>{var items = Array.from(e.querySelectorAll('span.icon-wrapper.ng-scope')).filter(x=>{return x.querySelector('i.mee-icon.mee-icon-StatusCircleCheckmark') == null}); if (items.length > 0){e.querySelector('a').click();}})")
	new_tabs = [x for x in driver.window_handles if x not in new_tabs]
	for tab in new_tabs:
		driver.switch_to.window(tab)
		do_quest(driver)
	for tab in [x for x in driver.window_handles if x != og]:
		driver.switch_to.window(tab)
		driver.close()
	return driver

def get_driver(ua:str) -> webdriver:
	"""Returns the webdriver specific for the given user agent string type

	Args:
		ua (str): The user agent string type. Valid values are "mobile", or "desktop"

	Raises:
		ValueError: if the EDGE_EXE_PATH is invalid, or the ua argument value is invalid

	Returns:
		webdriver: a webdriver
	"""
	USER_AGENTS = {
		'mobile':"Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
		'desktop':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54"
	}
	edge_options = Options()
	if not isfile(EDGE_EXE_PATH):
		raise ValueError("README: You need to edit the `EDGE_EXE_PATH` variable to be the full file path for your executable edge program. Open this file in a text editor and change the value!")
	edge_options.binary_location = EDGE_EXE_PATH
	if not isdir(EDGE_PROFILE_DIR):
		raise ValueError("README: You need to edit the `EDGE_PROFILE_PATH` variable to be the full file path for your executable edge program. Open this file in a text editor and change the value!")
	edge_options.add_argument(f"user-data-dir={EDGE_PROFILE_DIR}")
	# TODO: error check for profile name? idk if thats a directory or what
	edge_options.add_argument(f"profile-directory={EDGE_PROFILE_NAME}")
	if str(ua).strip().lower() not in USER_AGENTS:
		raise ValueError("Invalid 'ua' value.")
	
	edge_options.add_argument("disable-infobars")
	edge_options.add_argument("--disable-extensions")
	edge_options.add_argument(f"user-agent={USER_AGENTS.get(ua,'')}")
	edge_options.add_experimental_option("detach", True)
	try:
		driver = webdriver.Edge(options=edge_options)
	except Exception as e:
		print(e)
		print("issue occurred while attempting to open the driver! rerun the program?")
	return driver

def log_current_points(driver:webdriver):
	"""Logs todays date and the current points into a file so you can keep track. 
	also remnants of self-checking so it would only run once a day. can be disabled with no consequences.

	Args:
		driver (webdriver): webdriver
	"""
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/')
	try:
		val = driver.find_element(By.CSS_SELECTOR, '.pointsValue').text
		ts = f"{datetime.now}"
		outf = getcwd()+"\\"+"point_logs.txt"
		print(f"as of {ts} you have {val} points!")
		with open(outf, 'a') as f:
			f.write(f"{ts}\t{val}")
			print(f"See {outf} for historical point values")
	except:
		pass
	
def main():
	"""
	Does searches.
	Does tasks.
	Does quests.
	Logs points.
	Exits (and leaves edge open to the pointsbreakdown so you can visually verify everything worked fine).
	you may close or use the webbrowser at the end with no problems.
	"""
	driver = searches()
	driver = tasks(driver)
	driver = quests(driver)
	#while len(driver.window_handles) > 1:
	#	pass
	tqdm_sleep(3)
	driver.switch_to.window(driver.window_handles[0])
	log_current_points(driver)
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/pointsbreakdown')
	print("COMPLETED!\nThe script has completed, please do a quick visual check on the rewards page to make sure it worked.\nYou may now close this window and the browser!")

if __name__ == "__main__":
	"""when run, do the thing."""
	import logging
	logger = logging.getLogger('scope.name')
	file_log_handler = logging.FileHandler('logfile.log')
	logger.addHandler(file_log_handler)
	stderr_log_handler = logging.StreamHandler()
	logger.addHandler(stderr_log_handler)

	# nice output format
	formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t""%(message)s""')
	file_log_handler.setFormatter(formatter)
	stderr_log_handler.setFormatter(formatter)

	try:
		main()
	except Exception as e:
		traceback.print_exc()
		
	quit()
