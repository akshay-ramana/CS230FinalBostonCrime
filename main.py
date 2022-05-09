'''
Name:       Akshay Ramana
CS230:      Section 5
Data:       Which data set you used
URL:        Link to your web application online

Description:

This program provides different data visualization tools for the Boston crime data for 2022.
The user can choose to view offenses by day, week, and district through a bar chart, histogram, and map/pie chart respectively.
The user navigates the data through select boxes on the sidebar.

If offenses are viewed by day or week, the user can select the offenses of choice to view distributions over days and hours of the day.
If offenses are viewed by district, a map with dots representing each offenses appears.
The user can hover over individual dots to view the offense description and district.
Below is a pie chart with each district's respective proportion of offenses committed in Boston.
If the user selects a district, only the offenses in that district will appear in the map, and below will be a pie chart representing the respective proportions of the 5 most frequently committed offenses in the district.
If the user selects offenses, only those offenses in the selected district will appear.
'''

import csv
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd
import pydeck as pdk

data = pd.read_csv("BostonCrime2022_8000_sample.csv")

offenseBank = data.sort_values(["OFFENSE_DESCRIPTION"], ascending = True)

bank = []
for crime in offenseBank["OFFENSE_DESCRIPTION"]:
    if crime not in bank:
        bank.append(crime)
bank.sort()


def findFrequencies(dataFrame):
    offenses = {}
    for crime in dataFrame.itertuples():
        if crime[4] not in offenses:
            offenses[crime[4]] = 1
        else:
            offenses[crime[4]] += 1
    return offenses

st.title("Analysis of Boston Crime Data: 2022")
st.sidebar.header("Inputs")

chartChoice = ["", "Crime over the week", "Crime over the day", "Crime by district", "Crime by frequency"]
chart = st.sidebar.selectbox("Please select the type of data you would like to visualize:", chartChoice)

if not chart:
    st.write("Akshay Ramana")
    st.info("Please select type of data")

#choose which data you want to see

if chart == "Crime over the week":
    st.header("Crime over the week")
    # create bar chart based off type of crime you want + frequencies for each day of the week
    offense = st.sidebar.selectbox("Please select the criminal offense you would like to track:", bank)

    def frequencyWeek(labels, data):
        frequency = []
        for label in labels:
            weekData = data[data["DAY_OF_WEEK"] == label]
            if len(weekData) == 0:
                frequency.append(0)
            else:
                frequency.append(findFrequencies(weekData)[offense])
        return frequency

    offenseData = data[data["OFFENSE_DESCRIPTION"] == offense]
    DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    fig, ax = plt.subplots()

    ax.bar(DAYS, frequencyWeek(DAYS, offenseData))
    ax.set_xlabel("Days of the week")
    ax.set_ylabel(f"Frequency of {offense}")
    ax.set_title(f"Frequency of {offense} by Day of the Week")
    st.pyplot(fig)

if chart == "Crime over the day":
    # list of frequencies for each hour in the day
    # list of times of the day
    st.header("Crime over the day")
    offense = st.sidebar.selectbox("Please select the criminal offense you would like to track:", bank)
    offenseData = data[data["OFFENSE_DESCRIPTION"] == offense]
    TIMES = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    timeFrequency = []
    for time in TIMES:
        offenseTime = offenseData[offenseData["HOUR"] == time]
        if len(offenseTime) != 0:
            for x in range(len(offenseTime)):
                timeFrequency.append(time)

    fig, ax = plt.subplots()

    ax.hist(timeFrequency, bins = TIMES, edgecolor = "black")
    ax.set_xticks(TIMES)
    ax.set_title(f"Frequency of {offense} by Time of Day")
    ax.set_xlabel("Time of day (hour)")
    ax.set_ylabel(f"Frequency of {offense}")
    st.pyplot(fig)

# Normal map with small dots for each instance of crime
# Each district has a different color
if chart == "Crime by district":
    data = pd.read_csv("BostonCrime2022_8000_sample.csv")

    data.rename(columns={"Lat":"lat", "Long":"lon"}, inplace=True)

    districtData = data.loc[:,["DISTRICT", "STREET", "lat", "OFFENSE_DESCRIPTION", "lon", "OCCURRED_ON_DATE"]]
    districtData = districtData[(districtData["lat"] != 0) & (districtData["lon"] != 0)]
    districtData = districtData.dropna()

    districts = ["", "A15", "A7", "A1", "C6", "D4", "D14", "E13", "E5", "B3", "C11", "E18", "B2"]
    districtChoice = st.sidebar.selectbox("Please select a district:", districts)

    bank.insert(0, "")
    multiOffenses = st.sidebar.multiselect("Please select offenses:", bank)

    st.header("Offenses by Boston district")

    view_state = pdk.ViewState(
        latitude=districtData["lat"].mean(), # The latitude of the view center
        longitude=districtData["lon"].mean(), # The longitude of the view center
        zoom=11, # View zoom level
        pitch=0) # Tilt level

    def specificData(district, offenses):
        specificDistrict = districtData[districtData["DISTRICT"] == district]

        if len(offenses) == 0:
            return specificDistrict
        else:
            listMultiOffense = []

            for offense in offenses:
                selectedOffenseData = specificDistrict[specificDistrict["OFFENSE_DESCRIPTION"] == offense]
                listMultiOffense.append(selectedOffenseData)

            return pd.concat(listMultiOffense, ignore_index = True)

    #Custom layer for each district
    A15 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("A15", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[10, 123, 131],   # scatter color
                      pickable=True # work with tooltip
                      )

    A7 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("A7", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[42, 168, 118],   # scatter color
                      pickable=True # work with tooltip
                      )

    A1 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("A1", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[255, 210, 101],   # scatter color
                      pickable=True # work with tooltip
                      )

    C6 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("C6", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[241, 156, 101],   # scatter color
                      pickable=True # work with tooltip
                      )

    D4 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("D4", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[206, 77, 69],   # scatter color
                      pickable=True # work with tooltip
                      )

    D14 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("D14", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[38, 50, 72],   # scatter color
                      pickable=True # work with tooltip
                      )

    E13 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("E13", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[168, 230, 207],   # scatter color
                      pickable=True # work with tooltip
                      )

    E5 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("E5", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[177, 215, 116],   # scatter color
                      pickable=True # work with tooltip
                      )

    B3 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("B3", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[255, 211, 182],   # scatter color
                      pickable=True # work with tooltip
                    )

    C11 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("C11", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[255, 170, 165],   # scatter color
                      pickable=True # work with tooltip
                      )

    E18 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("E18", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[255, 139, 148],   # scatter color
                      pickable=True # work with tooltip
                  )

    B2 = pdk.Layer(type = 'ScatterplotLayer', # layer type
                      data=specificData("B2", multiOffenses), # data source
                      get_position='[lon, lat]', # coordinates
                      get_radius=50, # scatter radius
                      get_color=[126, 138, 162],   # scatter color
                      pickable=True # work with tooltip
              )

    tool_tip = {"html": "Offense description:<br/> <b>{OFFENSE_DESCRIPTION}</b> <br/> District: <b>{DISTRICT}</b> <br/> Time: <b>{OCCURRED_ON_DATE}</b>",
                "style": { "backgroundColor": "black",
                            "color": "white"}
                }

    def districtLayer(districtChoice):
        if districtChoice == "":
            selectedLayers = [A15, A7, A1, C6, D4, D14, E13, E5, B3, C11, E18, B2]
        else:
            selectedLayers = [globals()[districtChoice]]
        return selectedLayers

    layerChoice = districtLayer(districtChoice)

    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=view_state,
        layers=layerChoice,
        tooltip= tool_tip
    )

    st.pydeck_chart(map)

    pieDistricts = [str(district) for district in districts][1:]

    if districtChoice == "":
        st.subheader(f"Breakdown of crime by district")
        districtFrequency = []
        for district in pieDistricts:
            districtOffenses = districtData[districtData["DISTRICT"] == district]
            districtFrequency.append(len(districtOffenses))

        fig, ax = plt.subplots()
        ax.pie(districtFrequency, labels = pieDistricts, autopct = "%.2f%%")
        st.pyplot(fig)

    else:
        st.subheader(f"Breakdown of 5 most common crimes in district {districtChoice}")
        districtOffenses = districtData[districtData["DISTRICT"] == districtChoice]
        offenseByDistrict = findFrequencies(districtOffenses)

        sorted = dict(sorted(offenseByDistrict.items(), key=lambda x: x[1], reverse=True))

        districtOffense = [offense for offense in sorted]
        districtOffenseFrequency = [sorted[offense] for offense in sorted]

        fig, ax = plt.subplots()
        ax.pie(districtOffenseFrequency[0:5], labels = districtOffense[0:5], autopct = "%.2f%%")
        st.pyplot(fig)

if chart == "Crime by frequency":
    minFrequency = st.sidebar.number_input("Choose minimum frequency:")
    st.success(f"The minimum offense frequency is {minFrequency}")

    frequencyData = findFrequencies(data)

    sortedFrequencyData = dict(sorted(frequencyData.items(), key=lambda x: x[1], reverse=True))

    for offense in sortedFrequencyData:
        if sortedFrequencyData[offense] >= minFrequency:
            st.write(f"{offense.lower().capitalize()} : {sortedFrequencyData[offense]} offenses")
