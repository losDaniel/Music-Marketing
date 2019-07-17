# Music Markets 

In this repo we scrape Everynoise.com to put together a map of music genre markets based on spotify listener data. Using this information along with some short instagram data collectors we can build music marketing campaigns that target cities where the specific genres we're interested in are most popular. 

## Everynoise 

*Every Noise at Once* is a great website that hosts information on all the genres and sub-genres listened to around the world. Fortunately they also display information in lists, showing 1) the most popular genres in almost 3,000 cities and 2) ordering the cities from most to fewest spotify listeners. 

## Mapping Music Markets 

We create our map using the *Mapbox* functionality in `plotly`. In order to do this we needed additional geographic information including latitude and longitude information for cities which came from [Simplemaps.com](https://simplemaps.com/data/world-cities) and the latitude and longitude of country centroids which came from [Periscopedata.com](https://community.periscopedata.com/t/63fy7m/country-centroids).

![Rap_HipHop_Markets](Rap_HipHop_World.html)

## Notebooks

The notebooks in this repo will help you get the information you need to target specific cities when marketing music markets. The order of the notebooks is: 

1) `scrape_everynoise.ipynb` : implements the `everyscrape.py` module to collect spotify data. Might take several minutes or longer to run depending on your internet speed. 

2) `targeting.ipynb` : provides lists of the most relevant markets for selected genres. The notebook displays available genres and sub-genre frequencies which can be used to select the most appropriate key words (genre names), a calculation of market importance based on genre popularity and spotify listeners, and finally lists and the map of the data which can be used to target marketing campaigns. 

3) `instagram_pulls.ipynb` : if you are planning to market or promote instagram posts, this short script will pull the most popular hashtags associated with any key words. Useful for making sure posts get noticed. 

## Dependencies 

`pip install fuzzymatcher`

`pip install bs4` # BeautifulSoup

`pip install selenium`

`pip install plotly` 

The current mapping functions work offline, but you may host your maps on [Mapbox](https://www.mapbox.com/studio) by creating an accounting and using your access token. 

