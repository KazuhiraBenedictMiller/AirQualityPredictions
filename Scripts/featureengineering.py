'''
Importing Necessary Libraries.
'''

import json
import time

import numpy as np
import pandas as pd

from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv("../.env")

import sys

sys.path.append("../Scripts/")
sys.path.append("../")

import paths
import config

def GenerateRawDF(DF:pd.DataFrame) -> pd.DataFrame:
    '''
    Dummy Function that takes in input a DataFrame, reformats the Date Column and returns the formatted df.
    '''
    
    DF["Date"] = RawDF["Date_GMT+1_Europe/Berlin"].apply(lambda x: datetime.strptime(x.replace("T", " "), "%Y-%m-%d %H:%M"))
    DF.drop("Date_GMT+1_Europe/Berlin", axis = 1, inplace = True)
    
    return DF

def EngineerWholeDF(GiganticDF:pd.DataFrame) -> pd.DataFrame:
    '''
    Main Function use to Engineer our Data.
    It takes as input a DataFrame (previously generated by our function FetchHistoricalData in sourcing.py)
    Lastly it returns our WrangledDF.
    NOTE: the DF must be the Gigantic one with Data from all the Cities or a big one with all the Historical Data for a given City.
    '''
    
    #Let's make a copy of the DF just in case
    DF = GiganticDF.copy()
    
    CitiesSubRegion = config.CitiesSubRegion
    
    #Date Feature Engineering - Then Dropping the Column
    DF["Date"] = DF["Date_GMT+1_Europe/Berlin"].apply(lambda x: datetime.strptime(x.replace("T", " "), "%Y-%m-%d %H:%M"))
    DF.drop("Date_GMT+1_Europe/Berlin", axis = 1, inplace = True)

    #Sub-Region Feature Engineering - Then Dropping the Column
    DF["SubRegion"] = DF["CityID"].apply(lambda x: next((z[1] for z in CitiesSubRegion if x == z[0]), None))
    DF.drop("CityID", axis = 1, inplace = True)

    #Season Feature Engineering 
    DF["Season"] = DF["Date"].apply(lambda x: "Winter" if ((x.month >= 12 and x.day >= 21) or (x.month < 3) or (x.month == 3 and x.day <= 20)) 
                                                       else "Spring" if ((x.month >= 3 and x.day >= 21) or (x.month < 6) or (x.month == 6 and x.day <= 20))  
                                                       else "Summer" if ((x.month >= 6 and x.day >= 21) or (x.month < 9) or (x.month == 9 and x.day <= 22)) 
                                                       else "Autumn" if ((x.month >= 9 and x.day >= 23) or (x.month < 12) or (x.month == 12 and x.day <= 20)) 
                                                       else "NoSeasonFound")

    #Quick Check
    if "NoSeasonFound" in list(DF):
        raise DataIntegrityError("There's been an Error in Categorizing Data in Seasons!!")
    
    #Hour Feature Engineering - Then Dropping the Column Date
    DF["Hour"] = DF["Date"].apply(lambda x: x.hour)
    DF.drop("Date", axis = 1, inplace = True)

    #Generating Dummies for SubRegion, Season and Hour columns, concat-ing them to the DF and then Dropping them
    SubRegionDummies = pd.get_dummies(DF["SubRegion"], prefix = "IsSubRegion", dtype = int)
    SeasonDummies = pd.get_dummies(DF["Season"], prefix = "IsSeason", dtype = int)
    HourDummies = pd.get_dummies(DF["Hour"], prefix = "IsHour",dtype = int)

    #Let's Concat to the DataFrame and get rid of the original columns.
    #Note that can also be done by inserting the df as parameter in pd.get_dummies, check the docs.

    DF = pd.concat([DF, SubRegionDummies], axis = 1)
    DF = pd.concat([DF, SeasonDummies], axis = 1)
    DF = pd.concat([DF, HourDummies], axis = 1)

    DF.drop(["SubRegion", "Season", "Hour"], axis = 1, inplace = True)
    
    return DF

def EngineerSingleFeature(SingleRecordDF:pd.DataFrame) -> pd.DataFrame:
    '''
    Function use to Engineer a Sinlge Data Point.
    It takes as input a Single Data Input.
    Lastly it returns our WrangledDF.
    '''
    
    #Let's make a copy of the DF just in case
    SingleRecord = SingleRecordDF.copy()
    
    CitiesSubRegion = config.CitiesSubRegion
    
    #Date Feature Engineering - Then Dropping the Column
    SingleRecord["Date"] = [datetime.strptime(SingleRecord["Date_GMT+1_Europe/Berlin"].iloc[0].replace("T", " "), "%Y-%m-%d %H:%M")]
    #As it's going to be a pd.Series, we don't need to specify the axis
    SingleRecord.drop("Date_GMT+1_Europe/Berlin", axis = 1, inplace = True)

    #We Need [1] or [0] as Dict values cause otherwise it's going to mess with shape, we can't treat them as scalars
    SubRegion = {"IsSubRegion_" + x: [1] if x == next((z[1] for z in config.CitiesSubRegion if SingleRecord["CityID"].iloc[0] == z[0]), None) else [0] for x in ["Center", "North", "South"]}

    #Quick Check
    if sum([x[0] for x in SubRegion.values()]) == 0 or sum([x[0] for x in SubRegion.values()]) > 1:
        raise DataIntegrityError("There's been an Error in Categorizing Data in SubRegions!!")

    else:
        print("Check Passed, CityID correctly Transformed in SubRegions!")

    SingleRecord = pd.concat([SingleRecord, pd.DataFrame(SubRegion)], axis = 1)
    
    #Season Feature Engineering 
    Date = SingleRecord["Date"][0]
    Season = {"IsSeason_Winter": [1] if ((Date.month >= 12 and Date.day >= 21) or (Date.month >= 1 and Date.month < 3) or (Date.month == 3 and x.day <= 20)) else [0],
              "IsSeason_Spring": [1] if ((Date.month >= 3 and Date.day >= 21) or (Date.month >= 4 and Date.month < 6) or (Date.month == 6 and Date.day <= 20)) else [0],
              "IsSeason_Summer": [1] if ((Date.month >= 6 and Date.day >= 21) or (Date.month >= 7 and Date.month < 9) or (Date.month == 9 and Date.day <= 22))  else [0],
              "IsSeason_Autumn": [1] if ((Date.month >= 9 and Date.day >= 23) or (Date.month >= 10 and Date.month < 12) or (Date.month == 12 and Date.day <= 20)) else [0]         
             }

    #Quick Check
    if sum([x[0] for x in Season.values()]) == 0 or sum([x[0] for x in Season.values()]) > 1:
        raise DataIntegrityError("There's been an Error in Categorizing Data in Seasons!!")

    else:
        print("Check Passed, Datetimes correctly Transformed in Seasons!")

    SingleRecord = pd.concat([SingleRecord, pd.DataFrame(Season)], axis = 1)

    #Hour Feature Engineering
    Date = SingleRecord["Date"][0]
    Hour = {"IsHour_" + str(x): [1] if x == Date.hour else [0] for x in range(24)}

    #Quick Check
    if sum([x[0] for x in Hour.values()]) == 0 or sum([x[0] for x in Hour.values()]) > 1:
        raise DataIntegrityError("There's been an Error in Categorizing Data in Hours!!")

    else:
        print("Check Passed, Datetimes correctly Transformed in Hours!")

    SingleRecord = pd.concat([SingleRecord, pd.DataFrame(Hour)], axis = 1)
    
    SingleRecord.drop("Date", axis = 1, inplace = True)
    SingleRecord.drop("CityID", axis = 1, inplace = True)

    return SingleRecord