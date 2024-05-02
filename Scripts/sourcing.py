'''
Importing Necessary Libraries.
'''

import requests
import wget
import gzip
import json

import time
from datetime import datetime, timedelta

import pandas as pd

from typing import Dict

import os
from dotenv import load_dotenv

load_dotenv("../.env")

import sys

sys.path.append("../Scripts/")
sys.path.append("../")

import paths
import config

def FetchWeatherData(city:Dict, parameters:Dict) -> pd.DataFrame:
    '''
    Simple Function that takes as input the Parameter for the Data to be Fetched from OpenMeteo API.
    It then Computes a very basic Integrity check, and if passed returns the desired WeatherData DataFrame.
    If you want to see the Data Integrity Check logic, simply head over the Notebook 01 - DataSourcing.
    '''
    
    response = requests.get(config.HistoricalWeatherURL, params=parameters)

    Weatherdict = dict(json.loads(response.text))
    
    Weathercolumns = ["Date_GMT+1_Europe/Berlin",
                      "Temperature_2m", "Relative_Humidity_2m", "Dew_Point_2m", 
                      "Precipitation", "Pressure_msl", "Surface_Pressure", "Cloud_Cover", 
                      "Wind_Speed_10m", "Wind_Speed_100m", "Wind_Wirection_10m", "Wind_Direction_100m", 
                      "Soil_Temperature_0-7cm", "Soil_Temperature_7-28cm", "Soil_Temperature_28-100cm", "Soil_Temperature_100-255cm", 
                      "Soil_Moisture_0-7cm", "Soil_Moisture_7-28cm", "Soil_Moisture_28-100cm"]
    
    Weather_df = pd.DataFrame(data = zip(*Weatherdict["hourly"].values()), columns = Weathercolumns)
    
    #Integrity Check
    dict_keys = list(Weatherdict["hourly"].keys())
    for dictkey, dfcol in zip(dict_keys, Weather_df.columns):
        print(f'Checking Weather Data Integrity of {city["CityName"]} for: {dictkey, dfcol}')
        
        totTrues = sum(Weather_df[dfcol].values == Weatherdict["hourly"][dictkey]) == len(Weather_df)
        
        if not totTrues:
            raise DataIntegrityError(f'An error has occurred, the length of {dictkey} Raw Data Dict Key and {dfcol} DataFrame Column are different or the values are not the exact same in the exact same place, check failed!!')
            break
        
        else:
            print("-----------------------------------------------------")        
            print(f'Weather Data Integrity Check for {city["CityName"]} Passed!!')
            print("-----------------------------------------------------")
    
            return Weather_df
    
def FetchAirQualityData(city:Dict, parameters:Dict) -> pd.DataFrame:
    '''
    Simple Function that takes as input the Parameter for the Data to be Fetched from OpenMeteo API.
    It then Computes a very basic Integrity check, and if passed returns the desired AQIData DataFrame.
    If you want to see the Data Integrity Check logic, simply head over the Notebook 01 - DataSourcing.
    '''
    
    response = requests.get(config.HistoricalAirQualityURL, params=parameters)

    AQIdict = dict(json.loads(response.text))
    
    AQI_df = pd.DataFrame(data = zip(*AQIdict["hourly"].values()), columns = ["Date_GMT+1_Europe/Berlin", "EuropeanAQI"])         
    
    dict_keys = list(AQIdict["hourly"].keys())
    for dictkey, dfcol in zip(dict_keys, AQI_df.columns):
        print(f'Checking Air Quality Data Integrity of {city["CityName"]} for: {dictkey, dfcol}')
        
        totTrues = sum(AQI_df[dfcol].values == AQIdict["hourly"][dictkey]) == len(AQI_df)
        
        if not totTrues:
            raise DataIntegrityError(f'An error has occurred, the length of {dictkey} Raw Data Dict Key and {dfcol} DataFrame Column are different or the values are not the exact same in the exact same place, check failed!!')
            break
        
        else:
            print("-----------------------------------------------------")
            print(f'Air Quality Data Integrity Check for {city["CityName"]} Passed!!')
            print("-----------------------------------------------------")
            
            return AQI_df
        
def MergeDF(Weather_df:pd.DataFrame, AQI_df:pd.DataFrame) -> pd.DataFrame:
    '''
    Simple Function that Merges two DataFrames, used to Wrap everything up in the Main Function.
    Before Returning the Merged DF, a Simple Integrity Check is computed.
    '''
    
    print("Merging all Data Together...")
    print("-----------------------------------------------------")
    
    Merged_df = pd.merge(Weather_df, AQI_df, on = ["Date_GMT+1_Europe/Berlin"])

    #A Quick check that the length of the df is untouched as we want an inner join on Date Columns.
    
    if len(Weather_df) == len(AQI_df) == len(Merged_df):
        #print("-----------------------------------------------------")        
        print("Data Correctly Merged!!")
        print("-----------------------------------------------------")
        
        return Merged_df
    
    else:
        raise DataMergingError("There was an error in Merging the Historical Weather and AQI Data, the Length of the DataFrames are not the same!!")
        
def FetchHistoricalData(DumpToDisk:bool, CheckDiskAvailability:bool) -> pd.DataFrame:
    '''
    Main Function that's gonna Fetch Historical Data for both Weather and Air Quality.
    Our Start Date is set at the 1st September 2022.
    Our End Date is set at the 29th February 2024.
    For Every City in our List of Cities, we Pass the Parameters to the Above Functions and return DataFrames, later on Merged and Dumped to Disk.
    NOTE: In case the DumpToDisk parameter is set to true, it's going to Dump to Disk the files, otherwise, it will simply return a Merged MaxiDF with all the Raw Data for all our requested Cities.
    Also, in case CheckDiskAvailability is set to False, the Function is going to Fetch the Data Regardless its presence on local disk.
    '''
    
    GiganticDF = pd.DataFrame()
    
    Cities = config.Cities
    #Only Used for File Names
    StartDate = "01092022"
    #End Date 2 Days ago, cause Yesterday not available, one day lag in historical Data loading.
    EndDate = datetime.strftime(datetime.now() - timedelta(days=2), "%d%m%Y")
    
    for city in Cities:
        OnDiskFlag = False
        
        if CheckDiskAvailability == True:
            #Checking if our Desired File has already been Dumped to Disk.
            #For this Particular Example, the logic is simple, but we can actually check more and implement further logic. (especially when Data Versioning is required)
            if os.path.exists(paths.RAW_DATA_DIR / f'{city["CityName"]}_HistoricalData_{StartDate}_{EndDate}.parquet'):
                print("-----------------------------------------------------")   
                print(f'Skipping for {city["CityID"]} - {city["CityName"]} as already into Disk')
                print("-----------------------------------------------------")   

                #If present on Disk, we simply load into the df and move on.
                OnDiskFlag = True
                
                DiskDF = pd.read_parquet(paths.RAW_DATA_DIR / f'{city["CityName"]}_HistoricalData_{StartDate}_{EndDate}.parquet')
                
                GiganticDF = pd.concat([GiganticDF, DiskDF])
                continue
        
        if OnDiskFlag == False:
            print("-----------------------------------------------------")   
            print(f'Fetching Data for {city["CityID"]} - {city["CityName"]}')
            print("-----------------------------------------------------")  
            
            latitude = city["Latitude"] 
            longitude = city["Longitude"]
            
            #Fetching Historical Weather Data
            Weather_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", 
                               "precipitation", "pressure_msl", "surface_pressure", "cloud_cover", 
                               "wind_speed_10m", "wind_speed_100m", "wind_direction_10m", "wind_direction_100m", 
                               "soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm", "soil_temperature_28_to_100cm", 
                               "soil_temperature_100_to_255cm", "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm"],        
                    "timezone": "Europe/Berlin",
                    "start_date": "2022-09-01",
                    "end_date": datetime.strftime(datetime.now() - timedelta(days=2), "%Y-%m-%d")
                }
            
            #Weather_df = FetchWeatherData(Weather_params)
            
            #Fetching Historical AQI Data
            AQI_params = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "hourly": "european_aqi",
                        "timezone": "Europe/Berlin",
                        "start_date": "2022-09-01",
                        "end_date": datetime.strftime(datetime.now() - timedelta(days=2), "%Y-%m-%d")
                         }
            
            #AQI_df = FetchAirQualityData(AQI_params)
            
            Merged_df = MergeDF(FetchWeatherData(city, Weather_params), FetchAirQualityData(city, AQI_params))
            
            #Adding Column CityID
            
            #Get the City ID for given City from Cities List
            CityID = city["CityID"]
            print(f'Adding Column CityID {CityID} to {city["CityName"]}')
                
            #Moving the CityID Column as First
            Merged_df["CityID"] = CityID
            CityIDColumn = Merged_df.pop("CityID")
            Merged_df.insert(0, "CityID", CityIDColumn)
        
            #A Shorter Single-Liner
            #Merged_df.insert(0, "CityID", [CityID for x in range(len(Merged_df))])

            if DumpToDisk:
                
                print("-----------------------------------------------------")        
                print("Dumping Data to Disk!!")
                #print("-----------------------------------------------------")

                Merged_df.to_parquet(paths.RAW_DATA_DIR / f'{city["CityName"]}_HistoricalData_{StartDate}_{EndDate}.parquet')

            GiganticDF = pd.concat([GiganticDF, Merged_df])
            
            #Required so we won't ping the OpenMeteo API too much!!
            time.sleep(10)
    
    return GiganticDF
            
def FetchFromDisk() -> pd.DataFrame:
    '''
    Dummy Function used to gather all Data on Disk, concat them in a GiganticDF and then returning it.
    '''
        
    GiganticDF = pd.DataFrame()
    Cities = config.Cities
    
    for file in os.listdir(paths.RAW_DATA_DIR):
        if file.endswith(".parquet"):
            #Splitting the FileName for '_' character and then getting the first item in the list as it's going to be the correspective name of the city.
            CityName = file.split("_")[0]
            print(f'Fetching Raw Data from Disk in Raw Data Dir for {CityName}')

            TempCityDF = pd.read_parquet(paths.RAW_DATA_DIR / file)

            GiganticDF = pd.concat([GiganticDF, TempCityDF])
    
    return GiganticDF
