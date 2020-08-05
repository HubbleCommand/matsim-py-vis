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
import matsim
import pandas as pd
from collections import defaultdict
import bokeh

#https://gis.stackexchange.com/questions/223653/cannot-get-plot-in-geopandas-to-produce-a-map-of-the-geodataframe
#Not in a notebook environment, so need to explicitly use MatPlotLib
import matplotlib.pyplot as plt

def showWorld():
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

    cities = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))
    world.head()
    world.plot();
    import matplotlib.pyplot as plt
    plt.show()

def readNetworkFile(file):
    print("Reading network...")
    net = matsim.read_network(file)
    print("Read network!")
    print("Network to geo...")
    geo = net.as_geo()
    print("Network ready!")
    return geo

def readEventsFile(file):
    return matsim.event_reader(file, types='entered link,left link')

def getEvent(event):
    link_counts = defaultdict(int) # defaultdict creates a blank dict entry on first reference
    events = readEventsFile(events)

    eventsCounter = 0
    for event in events:
        if event['type'] == 'entered link':
            link_counts[event['link']] += 1

            eventsCounter += 1
            if eventsCounter % 1000 == 0:
                print("Got to event : " + str(eventsCounter))

    return link_counts

def compareEvents(events1Src, events2Src):
    print("Comparing events...")
    link_counts = defaultdict(int) # defaultdict creates a blank dict entry on first reference

    print("Loading events 1...")
    events1 = readEventsFile(events1Src)
    print("Loaded events 1!")
    print("Loading events 2...")
    events2 = readEventsFile(events2Src)
    print("Loaded events 2!")
    
    eventsCounter = 0

    print("Analysis events 1...")
    for event in events1:
        if event['type'] == 'entered link':
            link_counts[event['link']] += 1
            eventsCounter += 1
            if eventsCounter % 1000 == 0:
                print("Sim 1 : Got to event : " + str(eventsCounter))
    
    eventsCounter = 0;
    print("Analysing events 2...")
    for event in events2:
        if event['type'] == 'entered link':
            link_counts[event['link']] -= 1
            eventsCounter += 1
            if eventsCounter % 1000 == 0:
                print("Sime 2 : Got to event : " + str(eventsCounter))

    return link_counts

# -------------------------------------------------------------------
# 1. NETWORK: Read a MATSim network:
print("")

#networkSrc = 'D:/MATSim outputs to keep/equil output 2/output_network.xml.gz'
#net = matsim.read_network(networkSrc)

#geo = net.as_geo()  # combines links+nodes into a Geopandas dataframe with LINESTRINGs
#geo = readNetworkFile('D:/MATSim outputs to keep/equil output 2/output_network.xml.gz')
geo = readNetworkFile('D:/MATSim outputs to keep/ge 10pct tweaking/ge 1 tweaking/output_network.xml.gz')
#geo.plot()    # try this in a notebook to see your network!
#plt.show()

# -------------------------------------------------------------------
# 2. EVENTS: Stream through a MATSim event file.

#link_counts = compareEvents('D:/MATSim outputs to keep/equil output 1/output_events.xml.gz', 'D:/MATSim outputs to keep/equil output 2/output_events.xml.gz')
link_counts = compareEvents('D:/MATSim outputs to keep/ge 10pct tweaking/ge 1 tweaking/output_events.xml.gz', 'D:/MATSim outputs to keep/ge 10pct tweaking/ge 2 tweaking/output_events.xml.gz')

# convert our link_counts dict to a pandas dataframe,
# with 'link_id' column as the index and 'count' column with value:
link_counts = pd.DataFrame.from_dict(link_counts, orient='index', columns=['count']).rename_axis('link_id')

# attach counts to our Geopandas network from above
volumes = geo.merge(link_counts, on='link_id')
volumes.plot(column='count', figsize=(10,10), cmap='Wistia') #cmap is colormap

plt.show()
print("Should be showing...")