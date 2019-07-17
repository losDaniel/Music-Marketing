import os, requests, re
import numpy as np
import pandas as pd 

from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool     

try:
    from bs4 import BeautifulSoup
except:
    import pip
    pip.main(['install', 'bs4'])    
    from bs4 import BeautifulSoup
try:
    from selenium import webdriver
except:
    import pip
    pip.main(['install', 'selenium'])  
    from selenium import webdriver    



class instagram_scraper: 

	def __init__(self, launch_pad='https://www.instagram.com/dankundertone'):
		'''
		Scraper to get all sorts of useful instagram data
		
		- launch_pad : str. url to browse from when using the search bar. 

		'''

		self.launch_pad = launch_pad

		try:
		    self.cdir = 'C:/chromewebdriver'
		    assert os.path.exists(self.cdir + '/chromedriver.exe')
		except: 
		    check = False
		    print('Download chrome webdriver from https://sites.google.com/a/chromium.org/chromedriver/downloads')
		    while check == False:
		        self.cdir = input('folder containing chromedriver.exe (E to exit):')
		        try:    
		            assert os.path.exists(self.cdir + 'chromedriver.exe')
		            check = True
		        except:
		            print('could not find chromedriver.exe')
		        if self.cdir == 'E':
		            raise ValueError('Exit!') 


	def launch_driver(self, wait=10):
		chromeDriver = self.cdir + "/chromedriver.exe"                # set the driver path 
		driver = webdriver.Chrome(executable_path=chromeDriver)       # launch the driver 
		driver.implicitly_wait(wait)                                  # tell the driver to wait at least `wait` seconds before throwing up an error

		return driver 



	def get_related_hashtag_volume(self, hashtag): 
		'''
		Find the hastags related to the given hashtag and the number of posts for all of them. 	
		__________
		parameters	
		- hashtag : str or list of str. Hashtags for which you want to retrieve related hashtag data
		'''

		driver = self.launch_driver()        # launch a selenium webdriver 
		
		# ensure we use a list of hashtags 
		if type(hashtag)==str:               
			hashtags = [hashtag]
		else: 
			assert type(hashtag)==list
			hashtags = hashtag

		tag_data = pd.DataFrame()
		for tag in hashtags:                 # for each hashtag submitted 
			if "#" not in tag: 				 # if no # is attached to the submission we attach it for better search results 
				tag = "#" + tag              

			driver.get(self.launch_pad)      # go to the launch_pad to begin the search 
	        
	        # find the search bar 	
			search = driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input')

			search.send_keys(tag)            # key the search term into the search bar 

			# get the dropdown meny that appears upon entering a text in the search bar 
			dropdown = driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/div[2]/div[2]')

			# get each one of the suggestions 
			suggestion_list = dropdown.find_elements_by_tag_name('a')     

			hashbrowns = {} 
			for suggestion in suggestion_list: 
				text = suggestion.text
				ht = text.split('\n')[0].replace('#','')
				posts = int(text.split('\n')[1].replace('posts','').replace(',',''))
				hashbrowns[ht] = posts

			tag_data = tag_data.append(pd.DataFrame({'hashtags':list(hashbrowns.keys()), 
									   'posts':list(hashbrowns.values())}),
							           ignore_index=True,
							           sort=False)

			search.clear()                   # clear the search bar 

		driver.quit()

		return tag_data