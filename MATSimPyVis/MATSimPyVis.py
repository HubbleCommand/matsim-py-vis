# IMPORTANT NOTE - NEED TO USE env ENVIRONMENT (geopandas was installed with conda for simplicity)
import geopandas
import matsim
import math
import pandas as pd
from collections import defaultdict
import bokeh
from bokeh.models import ColumnDataSource

#https://gis.stackexchange.com/questions/223653/cannot-get-plot-in-geopandas-to-produce-a-map-of-the-geodataframe
#Not in a notebook environment, so need to explicitly use MatPlotLib
import matplotlib.pyplot as plt

def readNetworkFile(file):
    print("Reading network...")
    net = matsim.read_network(file)
    print("Read network!")
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
    """Compare the events of two simulations

    Parameters:
        events1Src (string): the path to the first simulation output events file
        events2Src (string): the path to the second simulation output events file

    Returns
        link_counts (defaultdic(int)):
    """

    print("Comparing events...")
    link_counts = defaultdict(int)

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

def calculateNetworkCapacity(netSrc):
    """Calculate the total capacity of a MATSim network

    Parameters:
    netSrc -- 
    """
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

def getEventsMaximumTime(eventsSrc):
    events = readEventsFile(eventsSrc)
    event = None
    counter = 0
    for event in events:
        counter+=1
        if counter % 100000 == 0:
            print('Got to event : ' + str(counter))
        #pass
    print("End time: " + str(event['time'] / 3600))
    return event['time'] / 3600

def getHourlyCongestionRatio(netSrc, eventsSrc, totalNetworkCapacity, endHour):
    endHour = math.ceil(endHour)
    dictlista = [defaultdict(int) for x in range(endHour)]

    eventsCounter = 0;

    events = readEventsFile(eventsSrc)
    print("Type: " + str(type(events)))
    for event in events:
        if event['type'] == 'entered link':
            slot = int(event['time'] / 3600)
            q = dictlista[slot]
            q[event['link']] += 1
            dictlista[slot] = q

            eventsCounter += 1
            if eventsCounter % 10000 == 0:
               print("Got to event : " + str(eventsCounter) + " in slot : " + str(slot))
                
    timeSlotNumber = 0;
    dictlistRations = [defaultdict(int) for x in range(endHour)]
    dictlistVolumes = [defaultdict(int) for x in range(endHour)]
    for time in dictlista:
        sumVolume = sum(time.values())
        print("Time Slot: " + str(timeSlotNumber) + " Total volume: " + str(sumVolume) + "  Congestion Ratio : " + str(sumVolume/totalNetworkCapacity))
        dictlistRations[timeSlotNumber] = sumVolume/totalNetworkCapacity
        dictlistVolumes[timeSlotNumber] = sumVolume
        timeSlotNumber += 1;

    return dictlistRations, dictlistVolumes

def doCompareTest(netSrc, events1Src, events2Src, cmap):
    geo = readNetworkFile(netSrc)
    link_counts = compareEvents(events1Src, events2Src)

    # convert our link_counts dict to a pandas dataframe, with "link_id" column as the index and "count" column with value:
    link_counts = pd.DataFrame.from_dict(link_counts, orient="index", columns=["count"]).rename_axis("link_id")

    # attach counts to our Geopandas network from above
    volumes = geo.merge(link_counts, on="link_id")
    #volumes.crs={"init" :"epsg:4326"}
    volumes.plot(column="count", figsize=(10,10), cmap=cmap)

    plt.show()
    print("Should be showing...")

# 0% - 100%
#doCompareTest('D:/tmp/0%/output_network.xml.gz', 'D:/tmp/0%/output_events.xml.gz', 'D:/tmp/100%/output_events.xml.gz', 'RdYlGn')
endTime = getEventsMaximumTime('D:/tmp/0%/output_events.xml.gz')
getHourlyCongestionRatio('D:/tmp/0%/output_network.xml.gz', 'D:/tmp/0%/output_events.xml.gz', 113844500.0, endTime)
