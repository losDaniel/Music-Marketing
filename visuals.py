import pip._internal

try:
    import plotly 
except:
    pip._internal.main(['install', 'plotly'])
    import plotly 

import os
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
from IPython.display import display_html
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#
#~#~#~# Data Visualizations #~#~#~#
#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#


def set_credentials(local_file="plotly config.txt"):
    '''Set the credentials for plotly'''
    with open(local_file,'r') as f: u,p=f.read().split() # get the username and password 

    creds={'user':u,'api_key':p}

    auth = False
    if creds['user'] is not None and creds['api_key'] is not None: 
        plotly.tools.set_credentials_file(username='dankUndertone', api_key='cEsZpcyWsO8xC0bSFxlm')
        auth = True
    assert auth==True
        
def plot_map_data(ds, data_name, opacity_value):
    element = go.Scattermapbox(                    # plot the points in the dataset 
        lat=ds['lat'],                             # latitude  
        lon=ds['lng'],                             # longitud 
        mode='markers',                            # point types 
        opacity=opacity_value, 
        marker=go.scattermapbox.Marker(
            size=ds['market_importance'],          # marker size based on market importance
        ),
        name = data_name,
        # display the city name and top genres when hovering over a point
        text=ds['city'].str.title()+'<br><br>'+ds['genre'].str.title().str.replace(',','<br>'), 
    )
    return element

def draw_genre_markets(graph_data, mat=None, opacity_reduction=0.5, names = []):
    '''
    Creates an interactive graph using Plotly and Mapboxplot to plot long-lat coordinates over a map.
    __________
    parameters
    - graph_data : pandas DataFrame or list of pandas DataFrames. Each dataframe is a dataset to plot
    - mat : str. Filepath, .txt file containing mapbox access token.
    - opacity_reduction : float, default 0.5. Each additional scatter plot with be the percentage more
         transparent than the previous scatter (useful when len(graph_data)>1).   
    '''
    try: 
        # import the country lat-long data 
        country_data = pd.read_csv(os.getcwd()+'/data/country_centroids.csv', encoding='iso-8859-1')
    except: 
        raise ValueError("Was unable to locate country_centroids.csv")

    try: 
        # load your mapbox access token 
        if mat is not None: 
            mapbox_access_token = open(mat,'r').read()
        else: 
            mapbox_access_token = open(os.getcwd()+'/data/mapbox.txt','r').read()
    except: 
        raise ValueError("Was unable to locate a text file with your mapbox access token")
    assert type(opacity_reduction) == float 
    assert opacity_reduction <=1 

    if type(graph_data)!=list: 
        graph_data = [graph_data]
    if len(names)>0: 
        try: 
            assert len(names)==len(graph_data)
        except: 
            raise ValueError("Make sure names list is same length as graph data")
    else: 
        i = 1
        for ds in graph_data: 
            names.append("DS"+str(i))
            i+=1 
    
    # create the first element of the scroll down list which will be shown by default 
    countries=list([
        dict(
            args=[ { 
                'mapbox.center.lat':0,              # set the default view to the cetner of the world 
                'mapbox.center.lon':0,
                'mapbox.zoom':1.2,                  # with a really high zoom
                'annotations[0].text':'World View'  # titled "World View" 
            } ],
            label='World',                          # give it the layout world in the menu 
            method='relayout'
        )
    ])

    country_list = []
    for ds in graph_data:                                           # for each dataset in the graph data
        country_list+=list(ds['country code'].unique())     # get the unique countries in that dataset and append them 
    country_list = list(set(country_list))                          # remove any duplicates from the list
        
    # create a menu that allows you to select and zoom into any country in the data 
    for idx, row in country_data[country_data['country'].isin(country_list)].iterrows():
        countries.append(
            dict( 
                args=[ { 
                    'mapbox.center.lat': row['latitude'],                # element centers on the latitude and longitude
                    'mapbox.center.lon': row['longitude'],
                    'mapbox.zoom':3,                                     # zoom to only see the country 
                    'annotations[0].text':'<br>'.join([row['country'],   # display the country code, name and prefered, relevant sub-genre
                                                       row['name'],
                                                       ])}],
                label=row['name'],
                method='relayout',
            )
        )

    opacity_value = 1 # reduce the opacity with each additional set of points so we can see the ones below 
    data = []
    n = 0
    for ds in graph_data:                                  # for each dataset in the graph data
        data.append(
            plot_map_data(ds, names[n], opacity_value)
        )
        opacity_value = opacity_value*opacity_reduction
        n+=1

    layout = dict(
        height = 500,                                            
        margin = dict( t=0, b=0, l=0, r=0 ),            # margins  
        font = dict( color='#FFFFFF', size=11 ),        # set font properties 
        paper_bgcolor = '#000000',                      # set the paper's background color 
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=0,                                  # set the mapbox center
                lon=0
            ),
            pitch=0,
            zoom=1.2,
            style='dark'                                # set the graph style 
        ),
    )

    updatemenus=list([                                  # create menus that update the graph 
        dict(                                           # FIRST MENU
            buttons = countries,                        # buttons are the countries
            pad = {'r': 0, 't': 10},
            x = 0.03,                                   # space from x anchor 
            xanchor = 'left',                           # anchor it to the left
            y = 1,                                      # space from y anchor 
            yanchor = 'top',                            # anchor to the top 
            bgcolor = '#AAAAAA',                        # menu background color 
            active = 99,
            bordercolor = '#FFFFFF',
            font = dict(size=11, color='#000000')
        ),
        dict(                                                     # SECOND MENU 
            buttons=list([                                        # buttons are listed manually 
                dict(                    
                    args=['mapbox.style', 'dark'],                # set style to dark 
                    label='Dark',
                    method='relayout'
                ),                    
                dict(                                             # set style to light 
                    args=['mapbox.style', 'light'],
                    label='Light',
                    method='relayout'
                ),
                dict(                                             # set style to satelite  
                    args=['mapbox.style', 'satellite'],
                    label='Satellite',
                    method='relayout'
                ),
                dict(                                             # set style to satelite with streets 
                    args=['mapbox.style', 'satellite-streets'],
                    label='Satellite with Streets',
                    method='relayout'
                )                    
            ]),
            direction = 'up',                                     # the menu opens upware 
            x = 0.75,                                             # anchors 
            xanchor = 'left',
            y = 0.05,
            yanchor = 'bottom',
            bgcolor = '#000000',
            bordercolor = '#FFFFFF',
            font = dict(size=11)
        ),                                                        # end of second menu 
    ])


    layout['updatemenus'] = updatemenus

    fig = go.Figure(data=data, layout=layout)
    
    return fig 




def draw_scatter_plot(X,
                      Y,
                      graph_name='marks_in_session', 
                      color='Green',
                      labels=[],
                      msize=10,
                      mode='markers'):
    '''Add a polar scatter plot to the data going into a figure
    __________
    parameters
    
    cscale : colorscale, select from : Greys,YlGnBu,Greens,YlOrRd,Bluered,RdBu,Reds,Blues,Picnic,Rainbow,Portland,Jet,Hot,Blackbody,Earth,Electric,Viridis,Cividis.
    labels : 
    '''
    if len(labels)==0:
        labels=list(X.index)
    
    scatter=go.Scatter(
        name=graph_name,
        x = X,
        y = Y,
        mode='markers',
        marker=dict(
            color=color,
            size=msize),
        text=labels
        )
    
    return scatter 


def draw_data(data,title='Title',xlabel='X',ylabel='Y'): 
    '''Draw out the data for a plotly graph with a minimal layout'''
    layout = go.Layout(
        title=title,
        angularaxis=dict(
            tickcolor='#CCC',
            showline=False,
        ),
        xaxis = dict(title = xlabel),
        yaxis = dict(title = ylabel),
    )
    fig = go.Figure(data=data, layout=layout)
    return fig  


def display_side_by_side(*args):
    '''Display the given tables side by side'''
    html_str=''
    for df in args:
        if type(df) == list:
            for t in df: 
                html_str+=t.to_html()
        else:
            html_str+=df.to_html()
    display_html(html_str.replace('table','table style="display:inline"'),raw=True)
