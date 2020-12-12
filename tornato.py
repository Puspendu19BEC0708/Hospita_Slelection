#!/usr/bin/env python
# coding: utf-8

# # objective
# analyse the tornato neighbour

# ### import panda libary to manupulate data 

# In[1]:


import pandas as pd
import numpy as np


# ### use pd.read_html to read table from wikepedia

# In[2]:


dfs=pd.read_html('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M')


# In[3]:


tornato_df=dfs[0]


# In[4]:


tornato_df


# assign nan value to Not assigned coloumn 

# In[5]:


tornato_df.replace("Not assigned", np.nan, inplace = True)


# drop those row which have a nan value 

# In[6]:


tornato_df.dropna(subset=["Borough"], axis=0, inplace=True)


# resting the indexes as you drop two row 

# In[7]:


tornato_df.reset_index(drop=True, inplace=True)


# In[8]:


tornato_df


# In[9]:


tornato_df.shape


# read the longitude and latitude file 

# In[10]:


df_lon_lat=pd.read_csv('http://cocl.us/Geospatial_data')


# In[11]:


df_lon_lat.head()


# merge two table based on postal code 

# In[12]:


df=pd.merge(df_lon_lat,tornato_df,on="Postal Code")


# In[13]:


df.head()


# In[14]:


pip install geopy


# In[15]:



pip install folium


# In[16]:


import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files


from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans


import folium # map rendering library

print('Libraries imported.')


# In[17]:


Tornto_data = df[df['Borough'] == 'Downtown Toronto'].reset_index(drop=True)
Tornto_data


# In[18]:


CLIENT_ID = 'ZUWOAQTQEIPGE0YB0RCGUZFEFT5QR13XGJWR0IA3RDWLEU14' # your Foursquare ID
CLIENT_SECRET = 'EB44FEKX5WFX05JEIWJKHG2ZFSMUKLOOECTPNRVYJDTXUCMS' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version
LIMIT = 100 # A default Foursquare API limit value
neighborhood_latitude='43.654260'
neighborhood_longitude='-79.360636'



radius=500
url='https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}'.format(
    CLIENT_ID,CLIENT_SECRET,VERSION, 
    neighborhood_latitude, 
    neighborhood_longitude, 
    radius)


# In[ ]:





# In[ ]:





# In[19]:


results = requests.get(url).json()
results


# In[20]:


def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[ ]:





# In[21]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[22]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            )
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[23]:


Toronto_venues = getNearbyVenues(names=df['Neighbourhood'],
                                   latitudes=df['Latitude'],
                                   longitudes=df['Longitude']
                                  )


# In[61]:


Toronto_venues.head(1000)


# In[25]:


Toronto_venues.groupby('Neighborhood').count()


# In[ ]:





# In[26]:



# one hot encoding
Toronto_onehot = pd.get_dummies(Toronto_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
Toronto_onehot['Neighborhood'] = Toronto_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [Toronto_onehot.columns[-1]] + list(Toronto_onehot.columns[:-1])
Toronto_onehot = Toronto_onehot[fixed_columns]

Toronto_onehot.head()


# In[27]:


Toronto_onehot.shape


# In[28]:


Toronto_grouped = Toronto_onehot.groupby('Neighborhood').mean().reset_index()
Toronto_grouped


# In[29]:


Toronto_grouped.shape


# In[30]:


num_top_venues = 5

for hood in Toronto_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = Toronto_grouped[Toronto_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')


# In[31]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[41]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhood_venue_sorted = pd.DataFrame(columns=columns)
neighborhood_venue_sorted['Neighborhood'] = Toronto_grouped['Neighborhood']

for ind in np.arange(Toronto_grouped.shape[0]):
    neighborhood_venue_sorted.iloc[ind, 1:] = return_most_common_venues(Toronto_grouped.iloc[ind, :], num_top_venues)

neighborhood_venue_sorted.head()


# In[42]:


kclusters = 5

Toronto_grouped_clustering = Toronto_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(Toronto_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 


# In[56]:



Toronto_grouped = Toronto_onehot.groupby('Neighborhood').mean().reset_index()
Toronto_grouped.head()


# In[66]:


Toronto_merge=pd.merge(Toronto_grouped,Toronto_venues,on="Neighborhood")
Toronto_merge.head()


# In[48]:


kclusters = 5

Toronto_grouped_clustering = Toronto_grouped.drop('Neighborhood',axis=1)
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(Toronto_grouped_clustering)

labels=pd.Series(kmeans.labels_,name='cluster_number') 
print(labels.value_counts(sort=False))


# In[ ]:





# In[ ]:




