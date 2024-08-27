"""
Description
-----------
    I made the dataset for EDA with this .py file. 
    The disease data are combined with the meteostat weather data from 2012 to 2022.(2011 ~ 2021 for analysis with tsun data).
    Note: To save time and energy, please Don't run it again because the data are already saved in the file 'informations_2.csv'
          If you were to run it, it takes hours!
          Also, because of the slightly difference in dataset for each year,
          this file does not gaurantee the use for year outside the range of [2012, 2022].

Parameters
----------
Adjust these 2 variables at the start of this file (line 26 & 27):

start_year: int
    the year from which I started to fetch data from meteostat and combine the mental disease data to dataframe.
    In the range of [2012, 2022] because I only requested the data from 2012 to 2022.
end_year: int
    the last year for fetching data from meteostat and combine the mental disease data to dataframe.
    In the range of [start_year, 2022] because I only requested the data from 2012 to 2022.

Returns
-------
The weather and disease data for each year will be saved in the folder 'informations'(will be created if it doesn't exisits)
"""
start_year = 2012
end_year = 2022

from pycountry import countries
from datetime import datetime
import pandas as pd
import numpy as np
import math
import os
import meteostat
from meteostat import Stations, Daily
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import time
perf_time0 = time.time()

def annual_average(avg_station, stations_amount, data, feature):
    if not math.isnan(data_start[feature].iat[0]):
        avg_this_station = 0
        avail_days = 0
        goodData = True

        for val in data[feature]:
            if math.isnan(val):
                goodData = False
                break
            avg_this_station += val
            avail_days += 1
            
        if goodData:
            avg_this_station = avg_this_station / avail_days
            avg_station = (avg_station * stations_amount + avg_this_station)/(stations_amount + 1)
            stations_amount += 1
       
    return avg_station, stations_amount
    

def annual_total(total_station, stations_amount, data, feature):
    if not math.isnan(data_start[feature].iat[0]):
        total_this_station = 0
        avail_days = 0
        goodData = True

        for val in data[feature]:
            if math.isnan(val):
                goodData = False
                break
            total_this_station += val
            avail_days += 1
            
        if goodData:
            total_station = (total_station * stations_amount + total_this_station)/(stations_amount + 1)
            stations_amount += 1
       
    return total_station, stations_amount
    


for k in range(start_year, end_year):
    print(k)
    # read the disease data
    prevalence=pd.read_csv("prevalence/global_prevalence_"+str(k)+".csv")
    incidence=pd.read_csv("incidence/global_incidence_"+str(k)+".csv")
    
    for j in range(len(incidence)):
        if 'Taiwan' in incidence.loc[j, 'location_name']:
            incidence.loc[j, 'location_name'] = 'Taiwan'
            break
    for i in range(len(prevalence)):
        if 'Taiwan' in prevalence.loc[i, 'location_name']:
            prevalence.loc[i, 'location_name'] = 'Taiwan'
            break

    informations = {'Country':[], 'Year':[], 'tavg':[], 'delta_t':[], 'snow':[], 'wspd':[], 
                    'wpgt':[], 'pres':[], 'prcp':[], 'Prevalence':[], 'Incidence':[]}
    country_code_not_in_pycountry = {"Micronesia (Federated States of)":'FM',
                                     "Taiwan":'TW',
                                     "Democratic People's Republic of Korea":'KP',
                                     "Republic of Korea":'KR', "Republic of Moldova":'MD',
                                     "United States of America":'US', "Bolivia (Plurinational State of)":'BO', "Venezuela (Bolivarian Republic of)":'VE', "Iran (Islamic Republic of)":'IR', "Turkey":'TR', "Palestine":'PS', "Democratic Republic of the Congo":'CD', "United Republic of Tanzania":'TZ', "United States Virgin Islands":'VI'}
    
    for i in range(len(prevalence)):
        print(i)
        country = prevalence.loc[i,'location_name']
        year = int(prevalence.loc[i,'year'])
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        if countries.get(name=country):
            stations = Stations().region(countries.get(name=country).alpha_2)
        else:
            stations = Stations().region(country_code_not_in_pycountry[country])
        stations = stations.inventory('daily', (start, end))
        stations = stations.fetch().index.tolist()

        temp_avg, temp_stations_amount, temp_avg1, temp_stations_amount1 = 0, 0, 0, 0
        annual_tavg, annual_tmin, annual_tmax, annual_delta_t, total_snow, total_prcp = 0, 0, 0, 0, 0, 0
        annual_wspd, annual_wpgt, annual_pres = 0, 0, 0
        tavg_stations_amount, tmin_stations_amount, tmax_stations_amount, delta_t_stations_amount = 0, 0, 0, 0
        snow_stations_amount, wspd_stations_amount, wpgt_stations_amount, pres_stations_amount, prcp_stations_amount = 0, 0, 0, 0, 0

        for j, station in enumerate(stations):
            data_start = Daily(station, start, start).fetch()
            # continue if data unavailable
            if data_start.empty:
                continue

            data = Daily(station, start, end).fetch()

            # since the disease data are provide per country per year,
            # we use the average of following weather data for each year

            # calculate tavg of the country
            annual_tavg, tavg_stations_amount = annual_average(annual_tavg, tavg_stations_amount, data, 'tavg')
            # annual_tavg = temp_avg
            # tavg_stations_amount = temp_stations_amount

            # calculate delta_temperature from tmax and tmin of the country
            temp_avg, temp_stations_amount = annual_average(annual_tmax, tmax_stations_amount, data, 'tmax')
            temp_avg1, temp_stations_amount1 = annual_average(annual_tmin, tmin_stations_amount, data, 'tmin')
            if (temp_stations_amount > tmax_stations_amount) and (temp_stations_amount1 > tmin_stations_amount):
                delta_t_stations_amount += 1
                
                annual_delta_t = (annual_delta_t*(delta_t_stations_amount-1) + (temp_avg - temp_avg1)) / delta_t_stations_amount
            
            annual_tmax = temp_avg
            tmax_stations_amount = temp_stations_amount
            annual_tmin = temp_avg1
            tmin_stations_amount = temp_stations_amount1

            # calculate total snow of the country
            temp_avg, temp_stations_amount = annual_average(total_snow, snow_stations_amount, data, 'snow')
            total_snow = temp_avg
            snow_stations_amount = temp_stations_amount

            # calculate wspd(average wind speed) of the country
            temp_avg, temp_stations_amount = annual_average(annual_wspd, wspd_stations_amount, data, 'wspd')
            annual_wspd = temp_avg
            wspd_stations_amount = temp_stations_amount

            # calculate wpgt(peak wind gust) of the country
            temp_avg, temp_stations_amount = annual_average(annual_wpgt, wpgt_stations_amount, data, 'wpgt')
            annual_wpgt = temp_avg
            wpgt_stations_amount = temp_stations_amount

            # calculate pres(average sea-level air pressure in hPa) of the country
            temp_avg, temp_stations_amount = annual_average(annual_pres, pres_stations_amount, data, 'pres')
            annual_pres = temp_avg
            pres_stations_amount = temp_stations_amount

            # calculate total prcp of the country
            temp_avg, temp_stations_amount = annual_total(total_prcp, prcp_stations_amount, data, 'prcp')
            total_prcp = temp_avg
            prcp_stations_amount = temp_stations_amount        
        

        informations['Country'].append(country)
        informations['Year'].append(year)
        if tavg_stations_amount:
            informations['tavg'].append(annual_tavg)
        else:
            informations['tavg'].append(np.nan)

        if delta_t_stations_amount:
            informations['delta_t'].append(annual_delta_t)
        else:
            informations['delta_t'].append(np.nan)

        if snow_stations_amount:
            informations['snow'].append(total_snow)
        else:
            informations['snow'].append(np.nan)
            
        if wspd_stations_amount:
            informations['wspd'].append(annual_wspd)
        else:
            informations['wspd'].append(np.nan)

        if wpgt_stations_amount:
            informations['wpgt'].append(annual_wpgt)
        else:
            informations['wpgt'].append(np.nan)

        if pres_stations_amount:
            informations['pres'].append(annual_pres)
        else:
            informations['pres'].append(np.nan)

        if prcp_stations_amount:
            informations['prcp'].append(total_prcp)
        else:
            informations['prcp'].append(np.nan)

        informations['Prevalence'].append(prevalence.loc[i,'val'])
        informations['Incidence'].append(np.nan)

    df = pd.DataFrame(informations)
    for i in range(len(incidence)):
        df.loc[(df['Country'] == incidence.loc[i,'location_name']) & (df['Year'] == int(incidence.loc[i,'year'])),'Incidence'] = incidence.loc[i,'val']
    outdir = 'informations'
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    df.to_csv("informations/information_"+str(k)+".csv", sep=',', index=False, encoding='utf-8')

inform=pd.read_csv("informations/information_2012.csv")
informations = {'Country':[], 'Year':[], 'tavg':[], 'delta_t':[], 'snow':[], 'wspd':[], 
                    'wpgt':[], 'pres':[], 'prcp':[], 'Prevalence':[], 'Incidence':[]}

for i in range(len(inform)):
    informations['Country'].append(inform.loc[i,'Country'])
    informations['Year'].append(inform.loc[i,'Year'])
    informations['tavg'].append(inform.loc[i,'tavg'])
    informations['delta_t'].append(inform.loc[i,'delta_t'])
    informations['snow'].append(inform.loc[i,'snow'])
    informations['wspd'].append(inform.loc[i,'wspd'])
    informations['wpgt'].append(inform.loc[i,'wpgt'])
    informations['pres'].append(inform.loc[i,'pres'])
    informations['prcp'].append(inform.loc[i,'prcp'])
    informations['Prevalence'].append(inform.loc[i,'Prevalence'])
    informations['Incidence'].append(inform.loc[i,'Incidence'])

for k in range(2013,2022):
    inform=pd.read_csv("informations/information_"+str(k)+".csv")
    for i in range(len(inform)):
        j = 0
        while j < len(informations['Country']) and informations['Country'][j] != inform.loc[i,'Country']:
            j += 1
        while j < len(informations['Country']) and informations['Country'][j] == inform.loc[i,'Country']:
            j += 1

        informations['Country'].insert(j,inform.loc[i,'Country'])
        informations['Year'].insert(j,inform.loc[i,'Year'])
        informations['tavg'].insert(j,inform.loc[i,'tavg'])
        informations['delta_t'].insert(j,inform.loc[i,'delta_t'])
        informations['snow'].insert(j,inform.loc[i,'snow'])
        informations['wspd'].insert(j,inform.loc[i,'wspd'])
        informations['wpgt'].insert(j,inform.loc[i,'wpgt'])
        informations['pres'].insert(j,inform.loc[i,'pres'])
        informations['prcp'].insert(j,inform.loc[i,'prcp'])
        informations['Prevalence'].insert(j,inform.loc[i,'Prevalence'])
        informations['Incidence'].insert(j,inform.loc[i,'Incidence'])
    
    df = pd.DataFrame(informations)
    df.to_csv("informations/informations_2.csv", sep=',', index=False, encoding='utf-8')

perf_time1 = time.time()
took_time = perf_time1 - perf_time0
print(f'It took: {took_time}s')