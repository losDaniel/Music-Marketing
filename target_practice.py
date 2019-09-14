import os
import everyscrape
import pandas as pd
import numpy as np


def word_genre_freq(everygenre, verbose=0):
	'''
    How often do words pop up in genre names, and how popular are the genres cumulatively.
    __________
    parameters
	- everygenre : pandas DataFrame. dataset with the genres and popularities 
	- verbose : 0, print nothing. 1, print unique genres. 2, also print # genres for given popularity levels 
	'''
	if verbose>0:
		print('There are',str(len(everygenre['genre'].unique())), 'unique genres in the data')

	# get the frequency of words in the genre descriptions, the most frequent words may be general categories ("pop", "rock",...)
	descriptor_frequencies = everyscrape.get_descriptor_freqs(everygenre)
	descriptor_frequencies = descriptor_frequencies.sort_values('Freq', ascending=False)

	full_freq = {}                                                                            # get the distribution in the data
	for d in descriptor_frequencies['Descr']:                                                 # for every general category 
	    full_freq[d] = everygenre['genre'].apply(lambda s: d in s.split()).astype(int).sum()  # use the apply function instead of contains because short strings like "a" could be part of words and not words that make up the genre 
	    
	descriptor_frequencies['PopFreq'] = descriptor_frequencies['Descr'].replace(full_freq)    # attach it to the frequency dataset 
	descriptor_frequencies = descriptor_frequencies.sort_values('PopFreq', ascending=False)

	if verbose==2:
		for i in range(0,10): 
		    print("Genres that appear more than",str(i),':',str(len(descriptor_frequencies[descriptor_frequencies['PopFreq']>i])))
	    
	# generate a list of suggested genres based on descriptor use and frequency 
	suggested_genres = descriptor_frequencies[(descriptor_frequencies['PopFreq']>200)&(descriptor_frequencies['Freq']>10)].reset_index(drop=True)
	
	return descriptor_frequencies, suggested_genres


def subgenre_freq(everygenre, genres):
    '''
    Find the frequencies of sub-genres with given key words 
    __________
    parameters
    - everygenre : pandas DataFrame. dataset with the genres and popularities 
    - genres: str or list of str. Key words to search sub-genres with. 
    '''
    if type(genres)==str: 
        genres=[genres]
    
    # get the frequencies of all the sub-genres 
    sub_freqs = pd.DataFrame(everygenre['genre'].value_counts()).sort_values('genre', ascending=False)
    sub_freqs = sub_freqs.reset_index()
    sub_freqs.columns = ['genre','freq']

    # identify all of the genre's sub-genres 
    sub_freqs = sub_freqs[sub_freqs['genre'].apply(lambda s: len(np.intersect1d(genres,s.split()))>0)]    
    
    return sub_freqs 


def find_genre(df, top_n, genre, subgenre=True, country=None, country_var='country code 3'):
    
    subset = df[df['top_genres']<=top_n]                                      # keep the top n genres for each city 
    
    if len(genre.strip().split())>1: 
        subset = subset[subset['genre'].apply(lambda s: genre in s)]          # if a phrase sub-genre is specified search it directly in the string  
    else: 
        subset = subset[subset['genre'].apply(lambda s: genre in s.split())]  # if a single word genre is specified search the tokens 
    
    if country is not None:                                                   # if a country was specified
        subset = subset[subset[country_var]==country]                         # keep the rows in a given country 
    
    subset['top_genres'] = top_n - subset['top_genres'] + 1                   # invert the scores to create a point system
    subset = subset.sort_values('rank')                                       # sort by spotify listener volume ranking 
    
    return subset 


def cities_by_genres(everygenre, rank_exponent=1.2, genre=None, rank=None, genre_rank=None):
    '''
    Retrieve a dataset listing the cities where the selected genre(s) are ranked in the top N listened to genres
    for that city. Create a `market_importance` score dependent on # of spotify listeners in the city and genre
    rank. If the same genre (or a sub-genre of a high level genre) appear multiple times in a single city that 
    city's market importance score increases. 
    __________
    parameters
    - everygenre : pandas DataFrame. a dataset with the everyscrape data include lat, lng, rank, country code, genre, top_genres 
          city, and country.
    - rank_exponent : float, default 1.2. City ranks are converted to 0-1 and this exponent is applied to generate a non-linear 
         depreciation over ranks. the higher the `rank_exponent`, the more importance is given to larger markets.
    - genre : str. genre you want to find
    - rank : int. only consider top-n = top-`rank` for cities 
    - genre_rank : dictionary of type {str : int} = {genre : rank}. Substitutes genre and rank, use genre_rank to submit
         more than one genre and rank combination. 
    '''

    if type(genre_rank)==dict:
        graph_data = pd.DataFrame() 
        for k in genre_rank: 
            graph_data = graph_data.append(find_genre(everygenre,genre_rank[k],k))
    else: 
        assert type(genre)==str
        assert type(rank)==int
        graph_data = find_genre(everygenre,rank, genre)
    # rank exponent is not rank 
    assert type(rank_exponent)==float
    rank_exp = rank_exponent

    graph_data = graph_data.groupby(['city','country'],as_index=False).agg({'lat':'first',
                                                                            'lng':'first',
                                                                            'rank':'first',
                                                                            'country code':'first',
                                                                            'genre':'unique',
                                                                            'top_genres':'sum'})
    # apply a non-linear weight to rank 
    graph_data['scale_rank'] = np.power((graph_data['rank'].max()-graph_data['rank'])/graph_data['rank'].max(),rank_exp)

    graph_data['market_importance'] = graph_data['top_genres']*graph_data['scale_rank']
    graph_data['genre'] = graph_data['genre'].apply(lambda s: ', '.join(s))
    graph_data = graph_data.dropna()

    return graph_data.sort_values('market_importance', ascending=False)