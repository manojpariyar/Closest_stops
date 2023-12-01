#!/usr/bin/env python
# coding: utf-8

# In[2]:


import geopandas as gpd
from pyproj import CRS


# In[3]:


# Read geodata files (shapefiles)
stops = gpd.read_file('D:\WEB-MAP\\Network\Stops.shp')
buildings = gpd.read_file('D:\WEB-MAP\\Network\Buildings.shp')


# In[4]:


# Check the coordinate system of the shapefiles
# The BallTree method requires the shapefiles to be in geographic coordinate system to calculate the haversine distance.
# The haversine distance is the great circular distance between two points on a sphere.

print(buildings.crs, '\n')
print(stops.crs)


# In[5]:


# Check the data to avoid unnecessary columns and clean the data as needed.
# In this case, the data is already cleaned and the steps are skipped here.
# The most important thing is to check the geometry columns if they resemble the coordinate system
# Most common mistake - when we overwrite the geodataframe while changing the CRS, the geometry ....
# (points' coordinate remains the same). Hence, the distance between the source and destination points is calculated incorrect.

print(buildings.head(), '\n-----------------')
print(stops.head())


# In[6]:


# Plot the data to visualize the points

get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt

fig, axes=plt.subplots(nrows=1, ncols=2, figsize=(20,10))

# Plot buildings
buildings.plot(ax=axes[0],markersize=0.2, alpha=0.5)
axes[0].set_title('Buildings')

# Plot stops
stops.plot(ax=axes[1], markersize=0.2, alpha=0.5, color='red')
axes[1].set_title('Stops');


# In[7]:


# BallTree Method

from sklearn.neighbors import BallTree
import numpy as np
def get_nearest(src_points, candidates, k_neighbors=1):
    """
    Find nearest neighbors for all source points from a set of candidate points
    """
    # Create tree from the candidate points
    tree = BallTree(candidates, leaf_size=15, metric='haversine')
    
    # Find closest points and distances
    distances, indices = tree.query(src_points, k=k_neighbors)
    
    # Transpose to get distances and indices into arrays
    distances = distances.transpose()
    indices = indices.transpose()
    
    # Get closest indices and distances (i.e. array at index 0)
    # note: for the second closest points, you would take index 1, etc.
    closest = indices[0]
    closest_dist = distances[0]
    
    # Return indices and distances
    return (closest, closest_dist)

def nearest_neighbor(left_gdf, right_gdf, return_dist=False):
  
    left_geom_col = left_gdf.geometry.name
    right_geom_col = right_gdf.geometry.name
    
    # Ensure that index in right gdf is formed of sequential numbers
    right = right_gdf.copy().reset_index(drop=True)
    
    # Parse coordinates from points and insert them into a numpy array as RADIANS
    # Notice: should be in Lat/Lon format
    left_radians = np.array(left_gdf[left_geom_col].apply(lambda geom: (geom.y * np.pi / 180, geom.x * np.pi / 180)).to_list())
    right_radians = np.array(right[right_geom_col].apply(lambda geom: (geom.y * np.pi / 180, geom.x * np.pi / 180)).to_list())
    
    # Find the nearest points
    # -----------------------
    # closest ==> index in right_gdf that corresponds to the closest point
    # dist ==> distance between the nearest neighbors (in meters)
    closest, dist = get_nearest(src_points=left_radians, candidates=right_radians)
                                                                       
    # Return points from right GeoDataFrame that are closest to points in left GeoData
    closest_points = right.loc[closest]
                                                                       
    # Ensure that the index corresponds the one in left_gdf
    closest_points = closest_points.reset_index(drop=True)
                                                                       
    # Add distance if requested
    if return_dist:
        # Convert to meters from radians
        earth_radius = 6371000 # meters
        closest_points['distance'] = dist * earth_radius
    return closest_points


# In[8]:


# Find closest stop for each building and also the distance (haversine)
closest_stops = nearest_neighbor(buildings, stops, return_dist=True)

# Result
closest_stops.head(3)


# In[9]:


# Just check the changes in the result file (closest_stops) as compared to the orginal fie (stops)
stops.head(3)


# In[10]:


# Once again check the buildings file. Now we need to add the closest_stops file to the buildings file
buildings.head(3)


# In[11]:


# check if any buildings is missing in the analysis
# Now we should have exactly the same number of closest_stops as we have buildings
print(len(closest_stops), '==', len(buildings))


# In[12]:


# Rename the geometry of closest stops gdf so that we can easily identify it
closest_stops = closest_stops.rename(columns={'geometry': 'closest_stop_geom'})

# Merge the datasets by index (for this, it is good to use '.join()' -function)
buildings = buildings.join(closest_stops)

# Let's see what we have
buildings.head()


# In[13]:


# Descriptive statistics of the distance data calculated
buildings['distance'].describe()


# In[14]:


# Plot the final result based on calculated distance
buildings.plot(column='distance', markersize=0.2, alpha=0.5, figsize=(10,10), scheme='quantiles', legend=True)


# In[15]:


# Now save the geodataframe to shapefile in a folder
# But the long column names get truncated so it is good to make them short and understandable.
buildings = buildings.rename(columns={'stops_geom': 'closest_stop_geom'})
buildings.columns


# In[16]:


# Check the changes
buildings.head()


# In[17]:


# Select only important columns for the geodataframe
selection = buildings[['OBJECTID', 'objtype', 'bygningsnu','bygningsst','kommunenum','kommunenav', 'geometry',
                       'osm_id', 'distance' ]]
selection.head()


# In[18]:


# Save it to a folder
selection.to_file('D:\WEB-MAP\\Network\Final_map.shp')


# In[19]:


selection.plot(column='distance', markersize=0.2, alpha=0.5, figsize=(10,10), scheme='quantiles', legend=True)


# In[20]:


from shapely.geometry import LineString

# Create a link (LineString) between building and stop points
buildings['link'] = buildings.apply(lambda row: LineString([row['geometry'], row['closest_stop_geom']]), axis=1)
                                                                                 
# Set link as the active geometry
building_links = buildings.copy()
building_links = building_links.set_geometry('link')


# In[47]:


# Plot the connecting links between buildings and stops and color them based on distan
ax = building_links.plot(column='distance', cmap='Greens', scheme='quantiles', k=4, alpha=0.8, lw=0.7, figsize=(13, 10))
ax = buildings.plot(ax=ax, color='yellow', markersize=1, alpha=0.7)
ax = stops.plot(ax=ax, markersize=4, marker='o', color='red', alpha=0.9, zorder=3)
                         
# Zoom closer
ax.set_xlim([7.15, 7.2])
ax.set_ylim([62.73, 62.75])
                         
# Set map background color to black, which helps with contrast
ax.set_facecolor('black')

plt.savefig('D:\WEB-MAP\\Network\BuildingLinksToStop.png')


# In[48]:


# Plot the connecting links between buildings and stops and color them based on distan
ax = building_links.plot(column='distance', cmap='Greens', scheme='quantiles', k=4, alpha=0.8, lw=0.7, figsize=(13, 10))
ax = buildings.plot(ax=ax, color='yellow', markersize=1, alpha=0.7)
ax = stops.plot(ax=ax, markersize=4, marker='o', color='red', alpha=0.9, zorder=3)
                         
# Set map background color to black, which helps with contrast
ax.set_facecolor('black')

plt.savefig('D:\WEB-MAP\\Network\BuildingLinksToStopFull.png')

