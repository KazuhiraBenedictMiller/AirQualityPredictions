import os
from dotenv import load_dotenv

load_dotenv("../.env")

Cities = [
            {
                "CityID": "AO",
                "CityName": "Aosta",
                "Latitude": 45.735062, 
                "Longitude": 7.313080
            },
    
            {
                "CityID": "TO",
                "CityName": "Torino",
                "Latitude": 45.070339,
                "Longitude": 7.686864
            },
    
            {
                "CityID": "TN",
                "CityName": "Trento",
                "Latitude": 46.066669,
                "Longitude": 11.129070
            },
    
            {
                "CityID": "MI",
                "CityName": "Milano",
                "Latitude": 45.464203, 
                "Longitude": 9.189982
            },

            {
                "CityID": "VE",
                "CityName": "Venezia",
                "Latitude": 45.440845, 
                "Longitude": 12.315515
            },
            
            {
                "CityID": "TS",
                "CityName": "Trieste",
                "Latitude": 45.653599, 
                "Longitude": 13.778520
            },
    
            {
                "CityID": "GE",
                "CityName": "Genova",
                "Latitude": 44.405651, 
                "Longitude": 8.946256
            },

            {
                "CityID": "FI",
                "CityName": "Firenze",
                "Latitude": 43.769562, 
                "Longitude": 11.255814
            },
    
            {
                "CityID": "BO",
                "CityName": "Bologna",
                "Latitude": 44.494888, 
                "Longitude": 11.342616
            },
            
            {
                "CityID": "AN",
                "CityName": "Ancona",
                "Latitude": 43.615849, 
                "Longitude": 13.518740
            },
    
            {
                "CityID": "PG",
                "CityName": "Perugia",
                "Latitude": 43.110718, 
                "Longitude": 12.390828
            },
    
            {
                "CityID": "RM",
                "CityName": "Roma",
                "Latitude": 41.902782, 
                "Longitude": 12.496365
            },
    
            {
                "CityID": "NA",
                "CityName": "Napoli",
                "Latitude": 40.851799, 
                "Longitude": 14.268120
            },
    
            {
                "CityID": "AQ",
                "CityName": "L'Aquila",
                "Latitude": 42.350700, 
                "Longitude": 13.399930
            },
    
            {
                "CityID": "CB",
                "CityName": "Campobasso",
                "Latitude": 41.560090, 
                "Longitude": 14.664800
            },
    
            {
                "CityID": "BA",
                "CityName": "Bari",
                "Latitude": 41.125912, 
                "Longitude": 16.872110
            },
    
            {
                "CityID": "PZ",
                "CityName": "Potenza",
                "Latitude": 40.637241, 
                "Longitude": 15.802220
            },
    
            {
                "CityID": "CZ",
                "CityName": "Catanzaro",
                "Latitude": 38.910542, 
                "Longitude": 16.587761
            },
    
            {
                "CityID": "PA",
                "CityName": "Palermo",
                "Latitude": 38.115662, 
                "Longitude": 13.361470
            },
    
            {
                "CityID": "CA",
                "CityName": "Cagliari",
                "Latitude": 39.215408, 
                "Longitude": 9.109320
            },
]

PairsIDsToDo = [["AO", "TO"],
                ["AO", "TN"],
                ["AO", "MI"],
                ["TO", "MI"],
                ["TO", "GE"],
                ["MI", "GE"],
                ["MI", "TN"],
                ["MI", "BO"],
                ["MI", "VE"],
                ["GE", "BO"],
                ["GE", "FI"],
                ["TN", "VE"],
                ["TN", "TS"],
                ["VE", "TS"],
                ["VE", "BO"],
                ["BO", "AN"],
                ["BO", "FI"],
                ["FI", "RM"],
                ["FI", "PG"],
                ["FI", "AN"],
                ["PG", "AN"],
                ["PG", "AQ"],
                ["PG", "RM"],
                ["AN", "AQ"],
                ["RM", "AQ"],
                ["RM", "NA"],
                ["RM", "CB"],
                ["AQ", "CB"],
                ["NA", "CB"],
                ["NA", "PZ"],
                ["CB", "BA"],
                ["CB", "PZ"],
                ["PZ", "BA"],
                ["PZ", "CZ"],
                ["CZ", "PA"],
                #["PA", "CA"]
               ]
#It took less than 5 Minutes.

CitiesSubRegion = [["AO", "North"],
                   ["TN", "North"],
                   ["TO", "North"],
                   ["MI", "North"],
                   ["TS", "North"],
                   ["VE", "North"],
                   ["GE", "North"],
                   ["FI", "Center"],
                   ["AN", "Center"],
                   ["BO", "Center"],
                   ["PG", "Center"],
                   ["RM", "Center"],
                   ["CA", "Center"],
                   ["NA", "South"],
                   ["AQ", "South"],
                   ["CB", "South"],
                   ["BA", "South"],
                   ["PZ", "South"],
                   ["CZ", "South"],
                   ["PA", "South"]
                  ]

HistoricalWeatherURL = "https://archive-api.open-meteo.com/v1/archive"
HistoricalAirQualityURL = "https://air-quality-api.open-meteo.com/v1/air-quality"

MariaDBUser = str(os.environ["MARIADB_USER"])
MariaDBUserPassword = str(os.environ["MARIADB_PASSWORD"])
MariaDBDatabase = str(os.environ["MARIADB_DBNAME"])
MariaDBRawTableName = str(os.environ["MARIADB_RAWTABLE"])
MariaDBTransformedTableName = str(os.environ["MARIADB_FETABLE"])
MariaDBHost = str(os.environ["MARIADB_CONTAINERIP"])
MariaDBPort = int(os.environ["MARIADB_CONTAINERPORT"])