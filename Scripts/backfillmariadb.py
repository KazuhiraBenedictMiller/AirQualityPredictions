'''
Importing Necessary Libraries.
'''

import json
import time

import numpy as np
import pandas as pd

from datetime import datetime

import mariadb as mdb

import sys

import os
from dotenv import load_dotenv

load_dotenv("../.env")

import sys

sys.path.append("../Scripts/")
sys.path.append("../")

import paths
import config
import sourcing
import featureengineering

def ConnectMariaDB() -> (mdb.Cursor, mdb.Connection):
    '''
    Dummy function used to Connect to the (Either Containerized or not) that returns the Connection and Cursor Variables.
    '''
    
    # Connect to MariaDB Platform
    try:
        connection = mdb.connect(
            user = config.MariaDBUser,
            password = config.MariaDBUserPassword,
            host = config.MariaDBHost,    #<-MariaDB Container IP Address (Running Locally, otherwise, you'd need to put the IP Address of the Machine hosting the Container)
            port = config.MariaDBPort,
            database = config.MariaDBDatabase
        )
        
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cursor = connection.cursor()
    
    return cursor, connection

def FetchFromWeb(DiskDump:bool, CheckOnDisk:bool) -> pd.DataFrame:
    '''
    Dummy function used to run the FetchHistoricalData on sourcing.py file.
    '''
    
    return sourcing.FetchHistoricalData(DiskDump, CheckOnDisk) 

def EngineerFeatures(Data:pd.DataFrame) -> pd.DataFrame:
    '''
    Dummy function used to run the EngineerWholeDF on featureengineering.py file.
    '''
    
    return featureengineering.EngineerWholeDF(Data) 

def DefineRawSchema(GigaDF:pd.DataFrame) -> (dict, str):
    '''
    Function used to define the Table Schema for storing our RawData.
    Takes as input the GigaDF, grabs the Columns and returns a string, used later in our SQL syntax to generate the table.
    '''
    
    
    #First 2 are Strings, and so, defined Manually
    DataFormat = {"CityID": "VARCHAR(2)", "Date_GMT1": "VARCHAR(16)"}

    DataFormat.update({column.replace("-", "_"):  "INTEGER" if GigaDF[column].dtype == "int64"
                                                            else "DOUBLE" if GigaDF[column].dtype == "float64"
                                                            else "VARCHAR(50)"
                                                            for column in GigaDF.columns if GigaDF[column].dtype != "object"})

    #Quick Check
    if len(DataFormat) != len(GigaDF.columns):
        raise DataIntegrityError("There's been an Error in Setting Columns and DataTypes for MariaDB!!")

    else:
        print("Check Passed, Data correctly Transformed in MariaDB Table!")
        
    #Formatting as Single String
    NameFormats = ["".join(f'{ColName} {ColFormat}, ' for ColName, ColFormat in DataFormat.items())]

    #Taking out last ", " characters
    NameFormats = NameFormats[-1][:-2]
    
    return DataFormat, NameFormats
    
def DefineFeaturesSchema(GigaDF:pd.DataFrame) -> (dict, str):
    '''
    Function used to define the Table Schema for storing our RawData.
    Takes as input the GigaDF, grabs the Columns and returns a string, used later in our SQL syntax to generate the table.
    '''

    DataFormat = {column.replace("-", "_"):  "INTEGER" if GigaDF[column].dtype == "int64"
                                                            else "DOUBLE" if GigaDF[column].dtype == "float64"
                                                            else "VARCHAR(50)"
                                                            for column in GigaDF.columns if GigaDF[column].dtype != "object"}
    
    #Quick Check
    if len(DataFormat) != len(GigaDF.columns):
        raise DataIntegrityError("There's been an Error in Setting Columns and DataTypes for MariaDB!!")

    else:
        print("Check Passed, Data correctly Transformed in MariaDB Table!")
        
    #Formatting as Single String
    NameFormats = ["".join(f'{ColName} {ColFormat}, ' for ColName, ColFormat in DataFormat.items())]

    #Taking out last ", " characters
    NameFormats = NameFormats[-1][:-2]
    
    return DataFormat, NameFormats

def CreateBackfillMariaDBTable(cursor:mdb.Cursor, connection:mdb.Connection, TableName:str, Data:pd.DataFrame, Schema:dict, StringSchema:str):
    '''
    Function that Takes several different Inputs:
    cursor and connection to connect to the Mariadb DB
    TableName, Schema and StringSchema for Declaring and Creating the Table
    Schema is also used for building up the query to insert our data.
    '''
    
    #Create Table
    
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {TableName} ({StringSchema})')
    connection.commit()

    cursor.execute('SHOW TABLES')

    Tables = []

    for x in cursor:
        Tables.append(x[0])

    if TableName not in Tables:
        raise TableCreationError(f'There has been an Error in Creating the {TableName} Table for MariaDB!!')

    else:
        print("Check Passed, MariaDB Data Table Correcly Created!")
    
    #Backfill
    
    #Generating the Query
    query = f'INSERT INTO {TableName} VALUES ({", ".join(["%s"]*len(list(Schema.keys())))})'
    
    DataToInsert = []

    for x in Data.iterrows():
        DataToInsert.append(tuple(x[1]))
    
    #Actually Inserting - Inefficient but Safe and Stable.
    for x in DataToInsert:
        cursor.execute(query, x)
        
    connection.commit()
    
    assert CheckDataInsertedIntegrity(cursor, connection, TableName, len(Data)) == True, "Data Inserted Integrity Check Failed!!"
    
    print(f'Data Correctly Inserted into {TableName} Table!!')
    
def CheckDataInsertedIntegrity(cursor, connection, TableName:str, DataSize:int) -> bool:    
    '''
    Simple Function to Check that the Data has been correctly inserted into the DB Table.
    Returns True if successful, otherwise False.
    '''
    #Checking the Data
    cursor.execute(f'SELECT COUNT(*) FROM {TableName}')
    Count = cursor.fetchall()[0][0]
    
    if Count == DataSize:
        return True
    
    else:
        return False
    
if __name__ == "__main__":
    Data = FetchFromWeb(False, True)
    
    FEData = EngineerFeatures(Data)
    
    cursor, connection = ConnectMariaDB()
    
    RawSchema, RawSchemaString = DefineRawSchema(Data)
    FESchema, FESchemaString = DefineFeaturesSchema(FEData)
    
    CreateBackfillMariaDBTable(cursor, connection, config.MariaDBRawTableName, Data, RawSchema, RawSchemaString)
    CreateBackfillMariaDBTable(cursor, connection, config.MariaDBTransformedTableName, FEData, FESchema, FESchemaString)