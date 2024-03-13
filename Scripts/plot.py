'''
Importing Necessary Libraries.
'''

import json
import time
from math import sqrt, radians
import numpy as np

import pandas as pd
import geopandas as gpd

import folium
import folium.plugins

from typing import List

import os
from dotenv import load_dotenv

load_dotenv("../.env")

import sys

sys.path.append("../Scripts/")
sys.path.append("../")

import paths
import config

def GenerateGeoDF(DF:pd.DataFrame) -> gpd.GeoDataFrame:
    '''
    Function that takes in input a DataFrame that has the following Columns:
    - CityID      <- ID of the City
    - Latitude    <- Latitude of the City
    - Longitude   <- Longitude of the City
    - EuropeanAQI <- EuropeanAQI of the City
    And Returns a GeoDataFrame with relative Coordinates
    P.S.: Coordinates are given already in columns Latitude and Longitude though.
    Even if it's repetitive, might decide to tweak this function in a future code refactoring, probably not going to be used.
    '''
    
    Geometry = gpd.points_from_xy(DF["Latitude"], DF["Longitude"])
    GeoDF = gpd.GeoDataFrame(
        LastRecordDF, geometry = Geometry
    )

    return GeoDF

def EuclideanDistance(Point1_Coords:List, Point2_Coords:List) -> float:
    '''
    Dummy Function that Calculates Euclidean distance between 2 Points Coordinates and return a float from the following inputs:
    
    Point1_Coords <- Point A Coordinates as [Latitude, Longitude]
    Point2_Coords <- Point B Coordinates as [Latitude, Longitude]
    '''
    
    #Convert latitude and longitude from degrees to radians
    Lat1, Lon1, Lat2, Lon2 = map(radians, [Point1_Coords[0], Point1_Coords[1], Point2_Coords[0], Point2_Coords[1]])

    #Calculate differences in latitude and longitude
    LatDiff = abs(Lat2 - Lat1)
    LonDiff = abs(Lon2 - Lon1)
    
    #Calculate Euclidean distance
    Distance = sqrt(LatDiff**2 + LonDiff**2)
    
    return round(Distance, 6)

def CalculateSyntheticEAQI(EAQI_A:int, EAQI_B:int, PointA_Coords:List, PointB_Coords:List, PointX_Coords:List):
    '''
    Dummy Function used to Generate a Synthetic AQI given the following Inputs:
    
    EAQI_A        <- EuropeanAQI of Point A
    EAQI_B        <- EuropeanAQI of Point B
    PointA_Coords <- Point A Coordinates as [Latitude, Longitude]
    PointB_Coords <- Point B Coordinates as [Latitude, Longitude]
    PointX_Coords <- Intermediate Point Coordinates as [Latitude, Longitude]
    '''
    
    
    EAQI_Diff = EAQI_B - EAQI_A
    DistancePercentage = EuclideanDistance(PointA_Coords, PointX_Coords) / EuclideanDistance(PointA_Coords, PointB_Coords)
    EAQI_X = EAQI_A + EAQI_Diff * DistancePercentage
    
    return int(EAQI_X)

def FillDFwIntermediates(DF:pd.DataFrame) -> pd.DataFrame:
    '''
    Function that takes in input a DataFrame that has the following Columns:
    - CityID      <- ID of the City
    - Latitude    <- Latitude of the City
    - Longitude   <- Longitude of the City
    - EuropeanAQI <- EuropeanAQI of the City
    
    It then uses 2 External functions to calculate Euclidean Distance and a Synthetic EQI to generate Intermediate Data Points between two destinations.
    Lastly, it fills and Return the Filled DataFrame.
    
    NOTE:
    
    I decided to calculate the Euclidean Distance as if Earth was Flat.
    I DO NOT BELIEVE EARTH IS FLAT, but in shorter distances and far from the poles, earth curvature is negotiable.
    A more precise method would be calculating Haversine Distance.
    '''
    
    #Mind that PairsIDsToDo is a manually written list of PointA-PointB distances that I want to be covered with intermediate points.
    for pair in config.PairsIDsToDo:

        #Getting PointA and PointB rows given 2 City IDs, then getting the coordinates, generating the intermediate point and lastly, inserting a "fake" City ID as First Element
        #and a Synthetic European AQI as Last Element.
        PointA = DF[DF["CityID"] == pair[0]]
        PointB = DF[DF["CityID"] == pair[1]]
    
        PointA_Coords = [PointA["Latitude"].values[0], PointA["Longitude"].values[0]]
        PointB_Coords = [PointB["Latitude"].values[0], PointB["Longitude"].values[0]]
        
        #Calculating the number of intermediate points I want between Point A and B as 1 point every 0.1 Difference in Latitude + 1 point every 0.1 Difference in Longitude
        NumIntermediates = int(abs(PointA_Coords[0] - PointB_Coords[0]) * 10) + int(abs(PointA_Coords[1] - PointB_Coords[1]) * 10)
    
        #Getting all the latitudes and longitudes given point Aand B coordinates and the number of intermediates I want.
        Lats = np.linspace(PointA_Coords[0], PointB_Coords[0], NumIntermediates + 2)
        Longs = np.linspace(PointA_Coords[1], PointB_Coords[1], NumIntermediates + 2)
        
        IntermediatePoints = [[round(lat, 6), round(lon, 6)] for lat, lon in zip(Lats, Longs)]
        #Cutting off First and Last Elements as they are PointA and PointB
        IntermediatePoints = IntermediatePoints[1:-1]
    
        #Now for every IntermediatePoint Coordinates, we want to generate a DF row, inserting the Fake CityID as first element of the list
        #and the Synthetic EuropeanAQI as last element.
        #Then, we concatenate it to the DF
        for intermediate in IntermediatePoints:
            IntermediateCoords = intermediate.copy()

            intermediate.insert(0, "IntermediatePoint")
            #Let's add those points to the DataFrame with a "IntermediatePoint" ID and a EuropeanAQI Value
            intermediate.append(CalculateSyntheticEAQI(PointA["EuropeanAQI"].values[0], PointB["EuropeanAQI"].values[0], PointA_Coords, PointB_Coords, IntermediateCoords))

            DF = pd.concat([DF, pd.DataFrame([[x for x in intermediate]], columns = DF.columns)], ignore_index=True)
    
    return DF

def GenerateMap(DF:pd.DataFrame) -> folium.Map:
    '''
    Function that takes in input a DataFrame that has the following Columns:
    - CityID
    - Latitude
    - Longitude
    - EuropeanAQI
    And Returns a Folium Map with Markers and Heatmap Data on it.
    '''
    HeatData = []
    
    #Creating the Map
    Map = folium.Map(location=[41.50, 16.50], tiles = "Esri.WorldPhysical", zoom_start = 6,
               zoom_control = False,
               scrollWheelZoom = False,
               dragging = False)
    
    #Filling our DataFrame with Intermediate Points.
    FilledDF = FillDFwIntermediates(DF)
    
    for row in FilledDF.iterrows():
        
        #Generating the Markers, but only for the Real Markers and not Intermediate ones.
        #Adding Markers, Only Colored for Real Data Ones.
        CityID = row[1]["CityID"]
        Latitude = row[1]["Latitude"]
        Longitude = row[1]["Longitude"]
        EuropeanAQI = row[1]["EuropeanAQI"]
    
        if CityID != "IntermediatePoint":
        
            if EuropeanAQI < 20:
                Color = "green"

            elif EuropeanAQI < 40 and EuropeanAQI >= 20:
                Color = "beige"

            elif EuropeanAQI < 60 and EuropeanAQI >= 40:
                Color = "orange"

            elif EuropeanAQI < 80 and EuropeanAQI >= 60:
                Color = "red"

            elif EuropeanAQI < 100 and EuropeanAQI >= 80:
                Color = "darkred"

            elif EuropeanAQI >= 100:
                Color = "black"

            #Place the markers with the popup labels and data
            Map.add_child(folium.Marker(
                                        location = (Latitude, Longitude),
                                        popup =
                                        "CityID: " + str(CityID) + "<br>" + "PredictedAQI: " + str(EuropeanAQI) + "<br>",
                                        icon = folium.Icon(color="%s" % Color),
                                    )
                                )
        
        #Generating the Heatmap.
        Data = [row[1]["Latitude"], row[1]["Longitude"], EuropeanAQI]

        #The Heatmap wants Data in format [Latitude, Longitude] or [Latitude, Longitude, Value]
        HeatData.append(Data)

    folium.plugins.HeatMap(HeatData, radius = 40, blur = 55, min_opacity = 0.55, gradient = {0.4: "lime", 0.77: "yellow", 1: "red"}).add_to(Map)
    
    return Map