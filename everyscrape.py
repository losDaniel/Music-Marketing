import pip._internal

try:
    from bs4 import BeautifulSoup
except:
    pip._internal.main(['install', 'bs4'])
    from bs4 import BeautifulSoup

try: 
    import fuzzymatcher
except: 
    import pip 
    pip._internal.main(['install', 'fuzzymatcher'])
    import fuzzymatcher

import re, os, string, time
import pandas as pd
import urllib.request as urllib
from urllib.parse import quote
from IPython.display import clear_output



#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#
#~#~#~#~ EVERYSOUND SCRAPER #~#~#~#~#~#
#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#



def fresh_soup(url):    
    '''
    Collects and parses the page source from a given url, returns the parsed page source 
    - url : the url you wish to scrape
    '''
    hdr = {'User-Agent': 'Mozilla/5.0'}                                       # we will browse as if using the Mozilla Browser
    
    try: 
        req = urllib.Request(url,headers=hdr)                                 # make a url request using the specified browser
        source = urllib.urlopen(req,timeout=10).read()                        # retrieve the page source
        
    except:                                                                   # if the url is reject due to non formatted characters 
        url = clean_url(url)
        
        req = urllib.Request(url,headers=hdr)                                 # the url should be readable now 
        source = urllib.urlopen(req,timeout=10).read()                        
            
    soup = BeautifulSoup(source,"lxml")                                       # process it using beautiful soup 
    
    return soup


def clean_url(url):
    non_conformists = [s for s in url if s not in string.printable]       # we get a list of the troublemaker characters 
    for s in non_conformists:
        url = url.replace(s,quote(s))       # and use the quote function from urllib.parse to translate them 
    return url


def get_cities():
    origin = 'http://everynoise.com/everyplace.cgi?root=all'                           # url for a list of every city listed in everynoise
    root = 'http://everynoise.com/everyplace.cgi?root='                                # define the root url for generating new links 
    search_params = '&scope=all'                                                       # and the suffix search parameter for new links 

    soup = fresh_soup(origin)                                                          # get the formatted page source 

    table = soup.find_all('table')[1]                                                  # retrieve the table with the information we want to scrape 

    links = []
    for row in table.find_all('tr'):                                                   # loop through every row in the table 
        elements = [a.text for a in row.find_all('a')]                                 # extract the ['headphone symbol','city name','country code']

        link = root+'%20'.join(elements[1].split())+'%20'+elements[2]+search_params    # create the link the way its supposed to be
        links.append((elements[1], elements[2], link))                                 # save each link in a (city,country,link) tuple 
        
    return links 


def listeners_by_city():
    '''Get the cities ranked by number of spotify listeners'''

    origin = 'http://everynoise.com/everyplace.cgi?scope=all'                          # for a list of every city in order of listener 
    soup = fresh_soup(origin)                                                          # get the formatted page source 
    table = soup.find_all('table')[1]                                                  # retrieve the table with the information we want to scrape 

    cities = []
    countries = []
    for row in table.find_all('tr'):
        elements = [a.text for a in row.find_all('a')]
        cities.append(elements[1])
        countries.append(elements[2])

    listening_cities = pd.DataFrame({'city':cities,
                                     'country code':countries})
    listening_cities = listening_cities.reset_index().rename(columns={'index':'rank'})
    
    return listening_cities
    
    
def genre_popularity(links, filename, resume=0):
    '''
    Scrape the most popular ranked genres for each city in the world
    __________
    parameters
    
    links : list of str. Urls to scrape
    
    filename : filepath & filename to save data as its scraped
    
    resume : int, default 0. index to resume the dataset from 
    '''
    everynoise_popularity = pd.DataFrame()                                              # create a dataset where you will store everything

    itermitent_save = 1                                                                 # save the data itermittently just in case you lose internet or something 
    last_save = 0 
    
    for link in links[resume:]:                                                                  # loop through each link

        clear_output()
        print("Retrieving data for link: ", str(links.index(link)))
        print("Last save was.. ",str(last_save))

        soup = fresh_soup(link[2])           
        genres = soup.find_all('div', {'class':'note'})                                 # find the table with the most popular genres

        if len(genres)>0:                                                               # if we find a table we proceed 

            genres = soup.find_all('div', {'class':'note'})[0]                          # get the table 
            genres = genres.find_all('div')[1:]                                         # and every row in the table

            popularity = []
            genre = [] 
            for element in genres: 
                popularity.append(re.findall('font-size: ([0-9]+)%;', str(element))[0]) # use the font-size as a proxy for popularity 
                genre.append(element.text)                                              # get the name of the genre

            df = pd.DataFrame({"Popularity":popularity,"Genre":genre})                  # place all the data collected in a dataframe 
            df['City'] = link[0]                                                        # attach the city and country code
            df['Country Code'] = link[1]

            everynoise_popularity = everynoise_popularity.append(df,                    # append the data to the master dataset
                                                                 ignore_index=True, 
                                                                 sort=False)  

            itermitent_save+=1 
            if itermitent_save%100==0:                                                  # save the file every hundren links 
                everynoise_popularity.to_csv(os.getcwd()+'/data/everynoise_popularity.csv')  
                last_save = links.index(link)

    everynoise_popularity.to_csv(filename)                                              # save the file
    
    return everynoise_popularity


def country_city_count(ds):
    df = ds.copy(deep=True)
    df['check'] = df['City'] + df['Country Code']
    print(str(len(list(df['check'].unique()))), ' unique cities')

    
    
def meatloaf(left, right, left_on, right_on, leftovers='left_only'):
    '''Merge two datasets and return the merged and residuals'''
    mrg = pd.merge(left, right, left_on=left_on, right_on=right_on, how='outer', indicator=True) # merge the two datasets 
    # print(mrg['_merge'].value_counts())                                          
    residuals = mrg[mrg['_merge']==leftovers][left.columns]                      # get the data that didn't merge 
    mrg = mrg[mrg['_merge']=='both']                                             # keep the data that did merge 
    return mrg, residuals 


def fuzzy_city_merge(enpop, worldcities):
    '''Merge the every noise data with the worldcities data exact and then fuzzy matching, returns merged and leftover cities'''
    
    # create a dataset with precise data for specific cities 
    enpop_cities = pd.DataFrame()               
    
    # beginning exact matching attempts 
    # merge using the city variable in world cities 
    mrg, leftovers = meatloaf(enpop[['popularity','genre','city','country','country code','country code 3']],
                              worldcities[['city','lat','lng','country code 3','population']],
                              left_on=['city','country code 3'],
                              right_on=['city','country code 3'])
    enpop_cities = enpop_cities.append(mrg, ignore_index=True, sort=False)

    # merge using the city_ascii variable in world cities 
    mrg, leftovers = meatloaf(leftovers,
                              worldcities[['city_ascii','lat','lng','country code 3','population']],
                              left_on=['city','country code 3'],
                              right_on=['city_ascii','country code 3'])
    enpop_cities = enpop_cities.append(mrg, ignore_index=True, sort=False)

    # merge using the admin_name variable in world cities 
    mrg, leftovers = meatloaf(leftovers,
                              worldcities[['admin_name','lat','lng','country code 3','population']],
                              left_on=['city','country code 3'],
                              right_on=['admin_name','country code 3'])
    enpop_cities = enpop_cities.append(mrg, ignore_index=True, sort=False)

    # for the leftovers of the exact matching, 
    # retrieve a fuzzy match between unique city-countries in the leftovers and each worldcities variables 
    merge_1 = fuzzymatcher.fuzzy_left_join(leftovers.groupby(['city','country code 3'],as_index=False)['country'].first(), 
                                           worldcities[['city','lat','lng','country code 3','population']], 
                                           ['city','country code 3'], 
                                           ['city','country code 3'])
    merge_2 = fuzzymatcher.fuzzy_left_join(leftovers.groupby(['city','country code 3'],as_index=False)['country'].first(), 
                                           worldcities[['city_ascii','lat','lng','country code 3','population']], 
                                           ['city','country code 3'], 
                                           ['city_ascii','country code 3'])
    merge_3 = fuzzymatcher.fuzzy_left_join(leftovers.groupby(['city','country code 3'],as_index=False)['country'].first(), 
                                           worldcities[['admin_name','lat','lng','country code 3','population']], 
                                           ['city','country code 3'], 
                                           ['admin_name','country code 3'])

    # concatenate the similarity scores for each merge so they can be compared
    fuzzy_eval = pd.concat([merge_1.reset_index().rename(columns={'best_match_score':'bms1','index':'idx1'})[['bms1','idx1']],     
                            merge_2.reset_index().rename(columns={'best_match_score':'bms2','index':'idx2'})[['bms2','idx2']],
                            merge_3.reset_index().rename(columns={'best_match_score':'bms3','index':'idx3'})[['bms3','idx3']]], 1)

    # find the columns (merge) with the maximum similarity for each city-country combo
    fuzzy_eval['max'] = fuzzy_eval[[c for c in fuzzy_eval if 'bms' in c]].idxmax(axis=1)    
    
    # for each merge, retrieve the indices where they had the maximum similarity out of the three merges 
    # merge that to the enpop_cities dataset, retrieve the leftovers and proceed 
    mrg1 = merge_1.loc[fuzzy_eval.loc[fuzzy_eval['max']=='bms1']['idx1']][['city_left',
                                                                           'city_right',
                                                                           'lat',
                                                                           'lng',
                                                                           'population',
                                                                           'country code 3_left']].rename(columns={'city_left':'city',
                                                                                                                   'city_right':'fuzzy_city',
                                                                                                                   'country code 3_left':'country code 3'})
    mrg, leftovers = meatloaf(leftovers,
                              mrg1,
                              left_on=['city','country code 3'],
                              right_on=['city','country code 3'])
    enpop_cities = enpop_cities.append(mrg, ignore_index=True, sort=False)
    # second merge
    mrg2 = merge_2.loc[fuzzy_eval.loc[fuzzy_eval['max']=='bms2']['idx2']][['city',
                                                                           'city_ascii',
                                                                           'lat',
                                                                           'lng',
                                                                           'population',
                                                                           'country code 3_left']].rename(columns={'city_ascii':'fuzzy_city',
                                                                                                                   'country code 3_left':'country code 3'})
    mrg, leftovers = meatloaf(leftovers,
                              mrg2,
                              left_on=['city','country code 3'],
                              right_on=['city','country code 3'])
    enpop_cities = enpop_cities.append(mrg, ignore_index=True, sort=False)
    # third merge
    mrg3 = merge_3.loc[fuzzy_eval.loc[fuzzy_eval['max']=='bms3']['idx3']][['city',
                                                                           'admin_name',
                                                                           'lat',
                                                                           'lng',
                                                                           'population',
                                                                           'country code 3_left']].rename(columns={'admin_name':'fuzzy_city',
                                                                                                                   'country code 3_left':'country code 3'})
    mrg, leftovers = meatloaf(leftovers,
                              mrg3,
                              left_on=['city','country code 3'],
                              right_on=['city','country code 3'])
    enpop_cities = enpop_cities.append(mrg, ignore_index=True, sort=False)
    
    # return the maximized match and any leftovers
    return enpop_cities, leftovers 



def get_descriptor_freqs(everygenre):

    # get a genre list
    genres = [g for g in list(everygenre['genre'].unique())]

    # tokenize the genre list 
    tokenized_genres = [doc.split(' ') for doc in genres]       

    # get a list of the unique words used to describe genres 
    unique_descriptors = [] 
    for doc in tokenized_genres: 
        for token in doc:
            if token not in unique_descriptors:
                unique_descriptors.append(token)

    descriptor_frequencies = {} 
    for descriptor in unique_descriptors:
        for idx, doc in enumerate(tokenized_genres): 
            if descriptor in doc: 
                if descriptor in descriptor_frequencies:
                    descriptor_frequencies[descriptor]+=1

                else:
                    descriptor_frequencies[descriptor]=1

    descriptor_frequencies = pd.DataFrame({'Descr':list(descriptor_frequencies.keys()),
                                           'Freq':list(descriptor_frequencies.values())})

    descriptor_frequencies = descriptor_frequencies.sort_values('Freq', ascending=False)
    
    return descriptor_frequencies






