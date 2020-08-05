# IMPORTANT NOTE - NEED TO USE env ENVIRONMENT (geopandas was installed with conda for simplicity)

# From old project, not much done
#from math import radians
#import numpy as np
#import matplotlib.pyplot as plt
#
#def main():
#	x=np.arange(0, radians(1800), radians(12))
#	plt.plot(x,np.cos(x), 'b')
#	plt.show()
#
#main()

import geopandas

def showWorld():
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

    cities = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))
    world.head()
    world.plot();
    import matplotlib.pyplot as plt
    plt.show()

import matsim
import pandas as pd
from collections import defaultdict

# -------------------------------------------------------------------
# 1. NETWORK: Read a MATSim network:
networkSrc = 'D:/MATSim outputs to keep/equil output 2/output_network.xml.gz'
net = matsim.read_network(networkSrc)
#net.nodes
#net.links
geo = net.as_geo()  # combines links+nodes into a Geopandas dataframe with LINESTRINGs
#geo.plot()    # try this in a notebook to see your network!

#https://gis.stackexchange.com/questions/223653/cannot-get-plot-in-geopandas-to-produce-a-map-of-the-geodataframe
#Not in a notebook environment, so need to explicitly use MatPlotLib
#import matplotlib.pyplot as plt
#plt.show()

# -------------------------------------------------------------------
# 2. EVENTS: Stream through a MATSim event file.

# The event_reader returns a python generator function, which you can then
# loop over without loading the entire events file in memory.
# In this example let's sum up all 'entered link' events to get link volumes.


eventsSrc = 'D:/MATSim outputs to keep/equil output 1/output_events.xml.gz'
events = matsim.event_reader(eventsSrc, types='entered link,left link')

link_counts = defaultdict(int) # defaultdict creates a blank dict entry on first reference

for event in events:
    if event['type'] == 'entered link':
        link_counts[event['link']] += 1

# My addition to compare different simulations
events2Src = 'D:/MATSim outputs to keep/equil output 2/output_events.xml.gz'
events2 = matsim.event_reader(events2Src, types='entered link,left link')

for event in events2:
    if event['type'] == 'entered link':
        link_counts[event['link']] -= 1




# convert our link_counts dict to a pandas dataframe,
# with 'link_id' column as the index and 'count' column with value:
link_counts = pd.DataFrame.from_dict(link_counts, orient='index', columns=['count']).rename_axis('link_id')

# attach counts to our Geopandas network from above
volumes = geo.merge(link_counts, on='link_id')
volumes.plot(column='count', figsize=(10,10), cmap='Wistia') #cmap is colormap

import matplotlib.pyplot as plt
plt.show()