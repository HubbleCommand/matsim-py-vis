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
    """Reads a MATSim network file and converts it to a geo
    Parameters:
        file (string): the path of the network file

    Returns:
        geo : the MATSim network
    """
    print("Reading network...")
    net = matsim.read_network(file)
    print("Read network!")
    geo = net.as_geo()
    print("Network ready!")
    return geo

def readEventsFile(file):
    """Reads a MATSim events file
    Parameters:
        file (string): the path of the events file
    """
    return matsim.event_reader(file, types='entered link,left link,vehicle enters traffic,vehicle leaves traffic')

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
    """Compare the events of two simulations by link

    Parameters:
        events1Src (string): the path to the first simulation output events file
        events2Src (string): the path to the second simulation output events file

    Returns:
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
            eventsCounter += 1
            if eventsCounter % 10000 == 0:
                print("Sim 1 : Got to event : " + str(eventsCounter))
    
    eventsCounter = 0;
    print("Analysing events 2...")
    for event in events2:
        if event['type'] == 'entered link':
            link_counts[event['link']] -= 1
            eventsCounter += 1
            if eventsCounter % 10000 == 0:
                print("Sim 2 : Got to event : " + str(eventsCounter))

    return link_counts

def calculateNetworkCapacity(netSrc):
    """Calculate the total capacity of a MATSim network

    Parameters:
        netSrc (string): the path of the network

    Returns:
        totalCapacity (int): the total capacity of the network
    """
    net = readNetworkFile(netSrc)

    netCounter = 0;
    totalCapacity = 0;
    print("Calculating capacity...")
    for index, row in net.iterrows():
        totalCapacity += row['capacity']
        
        if netCounter % 100000 == 0:
             print("Got to link : " + str(index) + " with capacity : " + str(row['capacity']))
        netCounter += 1

    print("Total capacity : " + str(totalCapacity))
    return totalCapacity

def getEventsLastMillis(eventsSrc):
    """Gets the last hour of a MATSim simulation events file
    Parameters:
        eventsSrc (string): the path of the events file
    """
    events = readEventsFile(eventsSrc)
    event = None
    counter = 0
    for event in events:
        counter+=1
        if counter % 100000 == 0:
            print('Got to event : ' + str(counter))
    print("End time: " + str(event['time']))
    print("End time: " + str(event['time'] / 3600))
    return event['time']

def getMillisecondCongestionRatio(netSrc, eventsSrc, totalNetworkCapacity):
    """Calculates the congestion ratio per millisecond, and prints to a Pandas line chart
    Parameters:
        netSrc (string):                the path to the network file
        eventsSrc (string):             the path to the events file
        totalNetworkCapacity (int):     the total capacity of the network (in vehicles / millisecond), can be calculated with calculateNetworkCapacity()

    Returns:
        dictlistVolumes ([int]): an array (index is the millisecond of the day) containing the count of vehicles on the network per hour 
    """
    #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.line.html
    dictlistMillisVols = defaultdict(int)
    dictlistMillisRats = defaultdict(int)

    events = readEventsFile(eventsSrc)
    totalPresentVehiclesCounter = 0
    eventsCounter = 0;
    for event in events:
        if event['type'] == 'vehicle enters traffic':
            totalPresentVehiclesCounter += 1

        if event['type'] == 'vehicle leaves traffic':
            totalPresentVehiclesCounter -= 1;

        dictlistMillisVols[int(event['time'])] = totalPresentVehiclesCounter
        dictlistMillisRats[int(event['time'])] = totalPresentVehiclesCounter / totalNetworkCapacity
        eventsCounter += 1
        if eventsCounter % 100000 == 0:
            print("Got to event : " + str(eventsCounter))
    
    return dictlistMillisVols, dictlistMillisRats


"""
THIS FUNCTION IS REPRESENTATIVE OF THE CONGESTION RATIO, IT DOES NOT CALCULATE THE ACTUAL CONGESTION RATIO
IN TERMS OF ANALYSING THE RESULTS OF A SINGLE SIMULATION OR MULTIPLE SIMULATIONS, IT IS FINE
BUT FOR COMPARING TO THE RESULTS OF OTHER REPORTS IT WILL BE WRONG

This was a design choice to represent the AMOUNT OF THE NETWORK USED WITHIN THE HOUR.
Just getting the number of unique vehicles that traversed the network doesn't tell the whole story! We don't know how MUCH of the network they used! SO the way it is is actually perfectly fine!
Adding to the volume for each entered link is wrong, as a single vehicle can enter multiple links!!! (ACTUALLY WE WANT HOW IT IS RIGHT NOW WHEN CALCULATING FOR PERIODS OF TIME!!!!!)

THE DATA GENERATED AND PRESENTED IN THE REPORT WAS USELESS, but still was good to compare to each other
It was good to compare the different results, as the calculation error is the same in all of them.
However, just look at the millisecond calculator, which looks at vehicle exit times as well.
Additionally, the graph outputted by the Millisecond analysis is very similar to the ones generated for the report
"""
def getHourlyCongestionRatio(netSrc, eventsSrc, totalNetworkCapacity, endHour):
    """Calculates the congestion ratio, per hour, of a MATSim simulation
    Parameters:
        netSrc (string):                the path to the network file
        eventsSrc (string):             the path to the events file
        totalNetworkCapacity (int):     the total capacity of the network (in vehicles / hour), can be calculated with calculateNetworkCapacity()
        endHour (int):                  the last hour of the simulation, can be calculated with getEventsLastMillis() and dividing by 3600

    Returns:
        dictlistRations ([float]): an array (index is the hour of the day) containing the congestion ratio of the network per hour 
        dictlistVolumes ([int]): an array (index is the hour of the day) containing the count of vehicles on the network per hour 
    """
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
            if eventsCounter % 100000 == 0:
               print("Got to event : " + str(eventsCounter) + " in slot : " + str(slot))
                
    timeSlotNumber = 0;
    dictlistRations = [float for x in range(endHour)]
    dictlistVolumes = [int for x in range(endHour)]
    for time in dictlista:
        sumVolume = sum(time.values())
        print("Time Slot: " + str(timeSlotNumber) + " Total volume: " + str(sumVolume) + "  Congestion Ratio : " + str(sumVolume/totalNetworkCapacity))
        dictlistRations[timeSlotNumber] = sumVolume/totalNetworkCapacity
        dictlistVolumes[timeSlotNumber] = sumVolume
        timeSlotNumber += 1;

    return dictlistRations, dictlistVolumes

def doCompareTest(netSrc, events1Src, events2Src, cmap):
    """Example / test of how to comapre 2 simulation event results
    Parameters:
        netSrc (string): path to the network file
        events1Src (string): path to the first events file
        events2Src (string): path to the second events file
        cmap (string): the color map to use
    """
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

def doRatioTest(netSrc, eventsSrc):
    """Example / test of how to calculate congestion ratios
    Parameters:
        netSrc (string): path to the network file
        eventsSrc (string): path to the events file
    """
    endTime = getEventsLastMillis(eventsSrc) / 3600 #calculates the last hour of the simulation, best to calculate this once and hard-code the value when doing for the same simulation
    netCap = calculateNetworkCapacity(netSrc) #calculates the total capacîty of the network, best to calculate this once and hard-code the value when doing for simulations on the same network
    res = getHourlyCongestionRatio(netSrc, eventsSrc, 113844500.0, endTime)
    print(res[0])
    print(res[1])

def doMillisRatioTest(netSrc, eventsSrc):
    """Example / test of how to calculate congestion ratios
    Parameters:
        netSrc (string): path to the network file
        eventsSrc (string): path to the events file
    """
    netCap = calculateNetworkCapacity(netSrc) #calculates the total capacîty of the network, best to calculate this once and hard-code the value when doing for simulations on the same network
    res = getMillisecondCongestionRatio(netSrc, eventsSrc, (netCap / 3600))

    s = pd.Series(res[0])
    s.plot.line()
    b = pd.Series(res[1])
    b.plot.line(subplots=True)
    plt.show()

#doCompareTest('D:/tmp/0%/output_network.xml.gz', 'D:/tmp/0%/output_events.xml.gz', 'D:/tmp/100%/output_events.xml.gz', 'RdYlGn')   # 0% - 100%
doMillisRatioTest('D:/tmp/0%/output_network.xml.gz', 'D:/tmp/0%/output_events.xml.gz')
