# IMPORTANT NOTE - NEED TO USE env ENVIRONMENT (geopandas was installed with conda for simplicity)
import geopandas
import matsim
import pandas as pd
from collections import defaultdict
import bokeh
from bokeh.models import ColumnDataSource

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

    '''
    Analysing moring rush hour
    12h = 43200

    so if event['time'] > 43200 ignore, and can break
    '''

    print("Analysis events 1...")
    for event in events1:
        if event['type'] == 'entered link':
            link_counts[event['link']] += 1
            #link_counts[event['link']] = 0
            eventsCounter += 1
            if eventsCounter % 10000 == 0:
                print("Sim 1 : Got to event : " + str(eventsCounter))
    
    eventsCounter = 0;
    print("Analysing events 2...")
    for event in events2:
        if event['type'] == 'entered link':
            link_counts[event['link']] -= 1
            #link_counts[event['link']] = 0
            eventsCounter += 1
            if eventsCounter % 10000 == 0:
                print("Sim 2 : Got to event : " + str(eventsCounter))

    return link_counts

def calculateNetworkCapacity():
    net = readNetworkFile(netSrc)
    print(net)
    print(type(net))

    netCounter = 0;
    totalCapacity = 0;
    print("Calculating capacity...")
    for index, row in net.iterrows():
        totalCapacity += row['capacity']
        if netCounter % 10000 == 0:
                print("Got to link : " + str(index) + " with capacity : " + str(row['capacity']))

    print("Total capacity : " + str(totalCapacity))
    return totalCapacity

def getHourlyCongestionRatio(netSrc, eventsSrc):
    totalCapacity = 113844500.0 #Don't need to calculate this again

    dictlista = [defaultdict(int) for x in range(24)]

    eventsCounter = 0;

    events = readEventsFile(eventsSrc)
    for event in events:
        if event['type'] == 'entered link':
            #if event['link'] == 83006:
            slot = int(event['time'] / 3600)
            q = dictlista[slot]
            q[event['link']] += 1
            dictlista[slot] = q

            eventsCounter += 1
            #if eventsCounter % 10000 == 0:
                #print("Got to event : " + str(eventsCounter) + " in slot : " + str(slot))
                
    timeSlotNumber = 0;
    for time in dictlista:
        sumVolume = sum(time.values())
        print("Time Slot: " + str(timeSlotNumber) + " Total volume: " + str(sumVolume))
        print("Time Slot: " + str(timeSlotNumber) + " Congestion ratio : " + str(sumVolume/totalCapacity)) 
        timeSlotNumber += 1;

def getAllCongestionRatios():
    print("Getting congestion ratio for no reservations")
    getHourlyCongestionRatio('D:/MATSim outputs to keep/zzz 2nd to last run/output_network.xml.gz', 
        "D:/MATSim outputs to keep/zzz last run 1.0 factor reserve 0.0/output_events.xml.gz")

    print("Getting congestion ratio for 30% reservations")
    getHourlyCongestionRatio('D:/MATSim outputs to keep/zzz 2nd to last run/output_network.xml.gz', 
        "D:/MATSim outputs to keep/ge 25pct 1.0 factor reserve 0.3/output_events.xml.gz")

    print("Getting congestion ratio for 50% reservations")
    getHourlyCongestionRatio('D:/MATSim outputs to keep/zzz 2nd to last run/output_network.xml.gz', 
        "D:/MATSim outputs to keep/ge 25pct 1.0 factor reserve 0.5/output_events.xml.gz")

    print("Getting congestion ratio for 60% reservations")
    getHourlyCongestionRatio('D:/MATSim outputs to keep/zzz 2nd to last run/output_network.xml.gz', 
        "D:/MATSim outputs to keep/ge 25pct 1.0 factor reserve 0.6/output_events.xml.gz")

    print("Getting congestion ratio for 70% reservations")
    getHourlyCongestionRatio('D:/MATSim outputs to keep/zzz 2nd to last run/output_network.xml.gz', 
        "D:/MATSim outputs to keep/ge 25pct 1.0 factor reserve 0.7/output_events.xml.gz")

    print("Getting congestion ratio for 70% reservations real factor")
    getHourlyCongestionRatio('D:/MATSim outputs to keep/zzz 2nd to last run/output_network.xml.gz', 
        "D:/MATSim outputs to keep/ge 25pct 1.0 factor reserve 0.7 real factor/output_events.xml.gz")

    print("Getting congestion ratio for 100% reservations")
    getHourlyCongestionRatio('D:/MATSim outputs to keep/zzz 2nd to last run/output_network.xml.gz', 
        "D:/MATSim outputs to keep/zzz 2nd to last run/output_events.xml.gz")

'''
# -------------------------------------------------------------------
# 1. NETWORK: Read a MATSim network:
#geo = readNetworkFile('D:/MATSim outputs to keep/equil output 2/output_network.xml.gz')
#geo = readNetworkFile('D:/MATSim outputs to keep/ge 10pct tweaking/ge 1 tweaking/output_network.xml.gz')
#geo = readNetworkFile('D:/MATSim outputs to keep/ge 25pct .5 factor/output_network.xml.gz')
#geo = readNetworkFile('D:/MATSim outputs to keep/ge 25pct reserve/output_network.xml.gz')
geo = readNetworkFile('D:/MATSim outputs to keep/zzz 2nd to last run/output_network.xml.gz')

# 2. EVENTS: Stream through a MATSim event file.

#link_counts = compareEvents('D:/MATSim outputs to keep/equil output 1/output_events.xml.gz', 'D:/MATSim outputs to keep/equil output 2/output_events.xml.gz')
#link_counts = compareEvents('D:/MATSim outputs to keep/ge 10pct tweaking/ge 1 tweaking/output_events.xml.gz', 'D:/MATSim outputs to keep/ge 10pct tweaking/ge 2 tweaking/output_events.xml.gz')
#link_counts = compareEvents('D:/MATSim outputs to keep/ge 25pct .4 factor/output_events.xml.gz', 'D:/MATSim outputs to keep/ge 25pct .5 factor/output_events.xml.gz')
#link_counts = compareEvents('D:/MATSim outputs to keep/ge 25pct reserve/output_events.xml.gz', 'D:/MATSim outputs to keep/ge 25pct no reserve/output_events.xml.gz')
#link_counts = compareEvents('D:/MATSim outputs to keep/ge 25pct reserve/output_events.xml.gz', 'D:/MATSim outputs to keep/ge 25pct no reserve/output_events.xml.gz')

# 0% - 100%
link_counts = compareEvents("D:/MATSim outputs to keep/zzz last run 1.0 factor reserve 0.0/output_events.xml.gz", "D:/MATSim outputs to keep/zzz 2nd to last run/output_events.xml.gz")

 convert our link_counts dict to a pandas dataframe, with "link_id" column as the index and "count" column with value:
link_counts = pd.DataFrame.from_dict(link_counts, orient="index", columns=["count"]).rename_axis("link_id")

 attach counts to our Geopandas network from above
volumes = geo.merge(link_counts, on="link_id")
volumes.crs={"init" :"epsg:4326"}
volumes.to_file("countries.geojson", driver="GeoJSON")

 volumes.plot(column="count", figsize=(10,10), cmap="Wistia") #cmap is colormap
 https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
volumes.plot(column="count", figsize=(10,10), cmap="RdYlGn")

plt.show()
print("Should be showing...")
'''

getAllCongestionRatios()