# These imports happen before log is setup because they should always work. 
# If they dont, leave it up to the user to figure out.
import traceback
import inspect
import sys
from random import choice, randint
from time import time, sleep

from os import getcwd, getlogin
from os.path import isfile, isdir
from datetime import datetime


###### CONFIGS ######
MAX_WEBDRIVER_WAIT = 100

EDGE_EXE_PATH = rf"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
EDGE_PROFILE_DIR = rf"C:\Users\{getlogin()}\AppData\Local\Microsoft\Edge\User Data"
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

class Logger:
	"""Custom logging solution"""
	
	fileset = False
	LOG_OUT_FILE = "./last_run.log"
	err_count = 0
	def __new__(cls, *args):
		"""
		Instead of creating a new instance, it returns the object/type itself because we want to mimic fully static class.
		"""
		if not Logger.fileset:
			Logger.resetLogFile()
		return Logger
	
	@staticmethod
	def resetLogFile(log_file_path:str=None):
		"""Resets the log file contents.

		Args:
			log_file_name (str, optional): If given, will attempt to set the log file path to the given log file name value. Defaults to None.
		"""
		if not log_file_path:
			f = open(Logger.LOG_OUT_FILE, 'w')
			f.close()
		else:
			try:
				f = open(log_file_path, 'w')
				f.close()
				Logger.LOG_OUT_FILE = log_file_path
			except:
				raise ValueError('invalid file path given')
		Logger.fileset = True
	
	@staticmethod
	def log(*args, **kwargs):
		"""Logs the given value into the logfile in a standardized format.
		Args:
			If any args are given, it will log the values with no special key.
			If any kwargs are given, it will log the values with the key.
		"""
		ts = f"{datetime.now()}"
		s = traceback.extract_stack()[:-1]
		s = [x.name for x in s]
		s = ".".join(s[max([i for i,x in enumerate(s) if x == "<module>" or i == 0]):])
		for arg in args:
			try:
				v = Logger._format_val_for_write(arg)
			except:
				v = f"!!!!Error converting value {arg}!!!"
			Logger._write_to_logs(ts=ts, k=None, v=v)
		for kw in kwargs:
			try:
				v = Logger._format_val_for_write(kwargs[kw])
			except:
				v = f"!!!!Error converting value for key {kw}!!!"
			Logger._write_to_logs(ts=ts, k=kw, v=v)

	@staticmethod
	def _format_val_for_write(val:object):
		"""Converts the given object into a human readable string
		Args:
			val (object): the value to be converted.
		Returns:
			list: list of human readable strings for the given value
			or
			str: human readable strings for the given value
		"""
		t = type(val)
		if t == str:
			return val.split("\n") if val.count("\n") > 1 else val
		if t in {int, float}:
			return repr(val)
		elif t == type(None):
			return 'null'
		elif t in {list, tuple, set, range, frozenset}:
			f = {list:("[","]"), tuple:("(",")"), set:("{","}"), range: ("(",")"), frozenset:("frozenset({","})")}
			ret = f[t][0]
			for v in val:
				ret += Logger._format_val_for_write(Logger._format_val_for_write(v))
				ret += ","
			ret += f[t][1]
			return ret
		elif t == dict:
			new_dict = {}
			for k,v in dict.items():
				new_dict[Logger._format_val_for_write(k)] = Logger._format_val_for_write(v)
			return repr(new_dict)
		elif isinstance(val, Exception):
			Logger.err_count = Logger.err_count + 1
			return ''.join(traceback.format_exception(t, val, val.__traceback__))
		elif t in {complex, bytes, memoryview}:
			return t.__name__ + f"(bytes({val.obj}))" if t == memoryview else f"{val}"
		elif t == bytearray:
			return repr(bytearray)
		elif t.__name__ == 'type':
			# TODO: what to do here?
			return repr(val)

	@staticmethod
	def _write_to_logs(ts:datetime, k:str, v:object):
		"""Actually writes the given values to the file

		Args:
			ts (datetime): timestamp to use
			k (str): key to use
			v (list | str): value to use.
		"""
		f = None
		try:
			f = open(Logger.LOG_OUT_FILE, 'a')
		except:
			pass
		if type(v) == list:
			for o in v:
				print(f"{ts}\t{k if k else ''}\t{o}")
				if f:
					f.write(f"{ts}\t{k if k else ''}\t{o}\n")
		else:
			print(f"{ts}\t{k if k else ''}\t{v}")
			if f:
				f.write(f"{ts}\t{k if k else ''}\t{v}\n")
		if f:
			f.close()

def tqdm_sleep(t: float):
	"""Sleeps with printing the remaining time to console
	# if tqdm not installed, no worries, it will use simple sleep display
	Args:
		t (float): time to sleep
	"""
	end_at = time() + t
	Logger.log(f"Wait: {t}s")
	try:
		pbar = tqdm.tqdm(total=t, bar_format="Wait: {n:>.5f}")
		while end_at > time():
			pbar.n = end_at - time()
			pbar.refresh()
		pbar.close()
	except:
		while time() < end_at:
			pass

def do_quest(driver:'webdriver'):
	"""Prerequisite: page is on a quest.
	Clicks on the next available task for the quest

	Args:
		driver (webdriver): webdriver
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	Logger.log(f"In quest: {driver.current_url}")
	with wait_for_page_load(driver):
		driver.execute_script("document.querySelector('.punchcard-row').querySelector('a').click()")

def poll(driver:'webdriver') -> bool:
	"""
	If the loaded page has a poll, do the poll.
	Args:
		driver (webdriver): webdriver

	Returns:
		bool: True if a poll was completed, otherwise False
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	try:
		overlay = driver.find_element(By.CSS_SELECTOR, 'div.bt_poll')
		selection = choice(overlay.find_elements(By.CSS_SELECTOR, ".btOption.b_cards"))
		with wait_for_page_load(driver):
			WebDriverWait(driver, 60).until(EC.element_to_be_clickable(selection)).click()
			tqdm_sleep(randint(1,4))
		return True
	except:
		# page does not have poll, or some other arbitrary error
		return False
	return False

def select_x_of_y_overlay(driver:'webdriver') -> bool:
	"""
	If the loaded page has a multiple choice or multi-select overlay option, do it until completed.
	Args:
		driver (webdriver): webdriver

	Returns:
		bool: True if a select x of y overlay was completed, otherwise False
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
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
			try:
				WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.rqOption')))
				driver.execute_script("Array.from(document.querySelectorAll('input.rqOption')).filter(e=>!e.classList.contains('optionDisable'))[0].click()")
			except:
				try:
					# maybe its this or that?
					WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btOptionCard')))
					selection = choice(driver.find_elements(By.CSS_SELECTOR, '.btOptionCard'))
					Logger.log("This or that! Sorry, too lazy to figure out how to get the correct answer, so do this by hand or let it run and guess!")
					selection.click()
				except:
					# nope
					pass
			sleep(2)
			try:
				is_done = driver.find_element(By.CSS_SELECTOR, 'div.cico.rqSumryLogo').find_element(By.CSS_SELECTOR, 'img[alt="Checkmark Image"]')
			except:
				pass
	return True

def multiple_choice_inpage(driver:'webdriver') -> bool:
	"""
	If the loaded page has an in-page (not overlay) multiple choice question, do it until completed.
	Args:
		driver (webdriver): webdriver

	Returns:
		bool: True if a multiple choice question series was completed, otherwise False
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
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

def complete_task(driver:'webdriver') -> bool:
	"""Attempts to complete the task that was opened in a new tab.

	Args:
		driver (webdriver): webdriver

	Returns:
		bool: True on completion
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	if not driver.current_url.lower().strip().startswith("https://www.bing.com/search?"):
		# if the webpage isnt a search type, its probably nothing left to do
		Logger.log(f"Task success: redirected to: {driver.current_url}")
		return True
	# attempt to run each type of task completion on it. 
	# sometimes the overlay is slow to load so give it an extra 2.5 seconds
	tqdm_sleep(2.5)
	task_completion_types = [multiple_choice_inpage, select_x_of_y_overlay, poll]
	for task_completion_func in task_completion_types:
		if task_completion_func(driver):
			# on successful completion, dont need to try to do the other types, return for next task.
			Logger.log(f"Task success: {task_completion_func.__name__}: {driver.current_url}")
			return True
	# if you get here its probably just a search with nothing else to do
	tqdm_sleep(randint(1,5))
	Logger.log(f"Task success? just a search: {driver.current_url}")
	return True

def do_searches(driver:'webdriver', max_points:int):
	"""Attempts to do the searches that meets the given amount of points to get.
	This is not bullet proof and might actually get run more than once if the points dont register quickly.

	Args:
		driver (webdriver): webdriver
		max_points (int): the maximum points you want to get searches for.
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	for search in range(0, max_points, POINTS_PER_SEARCH):
		with wait_for_page_load(driver):
			# go to and wait for page to finish loading
			# to ensure a unique search is done, we just search the current timestamp
			driver.get(f"https://bing.com/search?q={time()}")
		Logger.log(f"{search}/{max_points}: {driver.current_url}")

def searches()->'webdriver':
	"""
	If you havent met the max search points for the day, will do the searches.
	Gets the proper browser with specific user agent (desktop or mobile) and does the searches.

	Returns:
		webdriver: the leftover webdriver (its in desktop mode)
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	driver = get_driver('desktop')
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/pointsbreakdown')
	try:
		# needs to sleep 1s for the point animation to load lol, idk where else i find the point values
		tqdm_sleep(1)
		needs_search = any([len(set([int(x) for x in p.text.split(' / ')]))>1 for p in driver.find_elements(By.CSS_SELECTOR, 'p.pointsDetail.c-subheading-3.ng-binding')])
	except Exception as e:
		Logger.log(e)
		Logger.log(f"Issue calculating if searches are needed, so we are gonna do it anyways.")
		needs_search = True
	if not needs_search:
		return driver
	for mode in MAX_SEARCH_POINTS:
		if driver:
			Logger.log("need to restart browser")
			driver.quit()
			tqdm_sleep(1)
		driver = get_driver(mode)
		Logger.log(f'Starting searches for {mode} mode')
		do_searches(driver, MAX_SEARCH_POINTS[mode])
	return driver

def tasks(driver:'webdriver') -> 'webdriver':
	"""
	Attempts to do all of the available tasks, including daily.
	
	Args:
		driver (webdriver): the webdriver
	
	Returns:
		webdriver: the leftover webdriver (its in desktop mode)
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/')
	og = driver.current_window_handle
	# one task at a time so it dosent combine
	try:
		tasks = driver.find_elements(By.CSS_SELECTOR, ".mee-icon-AddMedium")
	except:
		Logger.log("uh oh, spaghetti-o, couldn't find taks to do, do this by hand or re-run?")
		tasks = []
	for taskidx, task in enumerate(tasks, start=1):
		prev_tabs = driver.window_handles
		WebDriverWait(driver, MAX_WEBDRIVER_WAIT).until(EC.element_to_be_clickable(task)).click()
		try:
			WebDriverWait(driver, MAX_WEBDRIVER_WAIT/5).until(EC.number_of_windows_to_be(len(prev_tabs)+1))
			new_tab = [x for x in driver.window_handles if x not in prev_tabs]
			Logger.log(f"task #{taskidx} opened {len(new_tab)} new tabs")
			for t in new_tab: 
				driver.switch_to.window(t)
				complete_task(driver)
				driver.close()
		except TimeoutException:
			try:
				# MAYBE ITS NOT A NEW TAB KIND OF TASK BUT RATHER A POPUP THINGY, IF SO JUST CLICK X AND CONTINUE
				WebDriverWait(driver, MAX_WEBDRIVER_WAIT/5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.c-glyph.glyph-cancel"))).click()
				Logger.log(f"task #{taskidx} was a popup redirect thingy. closed it.")
			except:
				pass
		for t in [x for x in driver.window_handles if x not in prev_tabs]:
			tqdm_sleep(1)
			driver.switch_to_window(t)
			driver.close()
		WebDriverWait(driver, 60).until(EC.number_of_windows_to_be(len(prev_tabs)))
		driver.switch_to.window(og)
	return driver

def quests(driver:'webdriver') -> 'webdriver':
	"""Does the quests for the day. Only one per day though as they usually are 24hr timelocked.

	Args:
		driver (webdriver): the webdriver

	Returns:
		webdriver: the leftover webdriver (its in desktop mode)
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/')
	og = driver.current_window_handle
	new_tabs = driver.window_handles
	# you can do all quests at once because they dont interfere with eachother
	driver.execute_script("Array.from(document.querySelectorAll('li.ng-scope')).forEach(e=>{var items = Array.from(e.querySelectorAll('span.icon-wrapper.ng-scope')).filter(x=>{return x.querySelector('i.mee-icon.mee-icon-StatusCircleCheckmark') == null}); if (items.length > 0){e.querySelector('a').click();}})")
	new_tabs = [x for x in driver.window_handles if x not in new_tabs]
	Logger.log(f"{len(new_tabs)} quests opened.")
	for tab in new_tabs:
		driver.switch_to.window(tab)
		do_quest(driver)
	for tab in [x for x in driver.window_handles if x != og]:
		driver.switch_to.window(tab)
		driver.close()
	return driver

def get_driver(ua:str) -> 'webdriver':
	"""Returns the webdriver specific for the given user agent string type

	Args:
		ua (str): The user agent string type. Valid values are "mobile", or "desktop"

	Raises:
		ValueError: if the EDGE_EXE_PATH is invalid, or the ua argument value is invalid

	Returns:
		webdriver: a webdriver
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
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
		Logger.log(e)
		Logger.log("issue occurred while attempting to open the driver! rerun the program?")
	return driver

def log_current_points(driver:'webdriver'):
	"""Logs todays date and the current points into a file so you can keep track. 
	also remnants of self-checking so it would only run once a day. can be disabled with no consequences.

	Args:
		driver (webdriver): webdriver
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/')
	try:
		val = driver.find_element(By.CSS_SELECTOR, '.pointsValue').text
		ts = f"{datetime.now()}"
		outf = getcwd()+"\\"+"point_logs.txt"
		Logger.log(f"as of {ts} you have {val} points!")
		with open(outf, 'a') as f:
			f.write(f"{ts}\t{val}")
			Logger.log(f"See {outf} for historical point values")
	except:
		Logger.log(f"Failed to log points into the point_logs file.")
	
def main():
	"""
	Does searches.
	Does tasks.
	Does quests.
	Logs points.
	Exits (and leaves edge open to the pointsbreakdown so you can visually verify everything worked fine).
	you may close or use the webbrowser at the end with no problems.
	"""
	Logger.log(inspect.currentframe().f_code.co_name)
	driver = searches()
	driver = tasks(driver)
	driver = quests(driver)
	tqdm_sleep(3)
	driver.switch_to.window(driver.window_handles[0])
	log_current_points(driver)
	with wait_for_page_load(driver):
		driver.get('https://rewards.bing.com/pointsbreakdown')
	Logger.log("COMPLETED!\nThe script has completed, please do a quick visual check on the rewards page to make sure it worked.\nYou may now close this window and the browser!")
	Logger.log(f"{Logger.err_count} logged err count")
	if Logger.err_count > 0:
		Logger.log(f"If the program did not work properly, feel free to share the {Logger.LOG_OUT_FILE} file with the script's author so that they can attempt to diagnose the issue.")

def check_for_updates():
	"""Checks for updates against the src code via software solution.
	You can delete/disable this function if you know how to git.
	DOES NOT IMPLEMENT UPDATES, REQUIRES USER TO UPDATE THEMSELEVES FOR SECURITY PURPOSES!
	"""
	import requests
	SRC_URL = 'https://raw.githubusercontent.com/Noah-Jaffe/MsftRewards-full-auto/main/auto.py'
	try:
		latest_src_code = requests.get(SRC_URL).content
		with open(__file__,'r') as f:
			if latest_src_code != f.read():
				Logger.log("ATTENTION! The script might have been updated! Please verify with the script's author if you should be using the new version.")
	except:
		Logger.log('Unable to check for script updates, try again later.')

if __name__ == "__main__":
	"""when run, do the thing."""
	# Start logging
	Logger.resetLogFile()
	# Add exception tracker
	sys.excepthook = lambda exctype, value, tb: Logger.log(value)#; Logger.log(''.join(traceback.format_exception(exctype, value, tb.__traceback__)))
	
	# Import the 3rd party packages
	from selenium import webdriver
	from selenium.webdriver.edge.options import Options
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.common.exceptions import TimeoutException

	try:
		import tqdm
	except ImportError:
		Logger.log(warning="TQDM not installed, simple timer will be used")

	main()
	# check for updates after otherwise user likely to not see the notification text
	check_for_updates()
	quit()
