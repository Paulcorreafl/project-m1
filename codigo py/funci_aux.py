#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import matplotlib.pyplot as plt
#import seaborn as sns
import requests 
import json
from shapely.geometry import Point
import geopandas as gpd
import ast
import argparse

def acquire():
    df_bicimad = pd.read_csv("../data/bicimad_stations.csv", sep="\t")

    headers = {
        'Accept': 'application/json',
    }
    
    response     = requests.get('https://datos.madrid.es/egob/catalogo/200215-0-instalaciones-deportivas.json', headers=headers)
    json_data    = response.json()
    text         = json_data['@graph']
    df_deportivo = pd.DataFrame(text)
    return df_bicimad,df_deportivo 
    
#df_bicimad,df_deportivo=acquire()
#df_bicimad,df_deportivo

def merge_clean(df_bicim,df_centrosd):
    df_bicim=pd.DataFrame(columns=["name","address","long_start","lat_start"]) 
    for i in range(len(df_bicimad["address"])):
        lugar=df_bicimad["address"][i]
        name=df_bicimad["name"][i]
        direccion=ast.literal_eval(df_bicimad["geometry.coordinates"][i])   
        latitude=direccion[1]
        longitude=direccion[0]
        df_bicim.loc[i,"address"]=lugar
        df_bicim.loc[i,"long_start"]=longitude
        df_bicim.loc[i,"lat_start"]=latitude
        df_bicim.loc[i,"name"]=name
    df_bicim["id"]=1
    
    df_centrosd=pd.DataFrame(columns=['distrito',"centro deportivo","lat_finish","long_finish"])  
    for i in range(len(df_deportivo["title"])):
        centro=df_deportivo["title"][i]
        direccion=df_deportivo["location"][i]
        sitio_interes=df_deportivo["address"][i]
        latitude=direccion["latitude"]
        longitude=direccion["longitude"]
        sitio_inter=sitio_interes['street-address']
        df_centrosd.loc[i,"centro deportivo"]=centro
        df_centrosd.loc[i,"lat_finish"]=latitude
        df_centrosd.loc[i,"long_finish"]=longitude
        df_centrosd.loc[i,'distrito']=sitio_inter
    df_centrosd['id']= 1    
    df_union =df_union = pd.merge(df_bicim, df_centrosd, on='id')
    df_limpio=df_union.drop('id', axis=1)
    return df_bicim,df_centrosd,df_limpio
#df_bicim,df_centrosd,df_limpio=merge_clean(df_bicimad,df_deportivo)
#print(df_bicim,df_centrosd,df_limpio)
  


# In[12]:


def distancia_min(df_limpio):
    def to_mercator(lat, long):
        # transform latitude/longitude data in degrees to pseudo-mercator coordinates in metres
        c = gpd.GeoSeries([Point(lat, long)], crs=4326)
        c = c.to_crs(3857)
        return c
    
    def distance_meters(lat_start, long_start, lat_finish, long_finish):
        # return the distance in metres between to latitude/longitude pair points in degrees 
        # (e.g.: Start Point -> 40.4400607 / -3.6425358 End Point -> 40.4234825 / -3.6292625)
        start = to_mercator(lat_start, long_start)
        finish = to_mercator(lat_finish, long_finish)
        return start.distance(finish)
        
    df_limpio["distancia_m"]=df_limpio.apply(lambda row: distance_meters(row["lat_start"],row["long_start"],row["lat_finish"],row["long_finish"]),axis=1)
    return df_limpio
#df_limpio=distancia_min(df_limpio)
#df_limpio


# In[24]:


def analyze(df_limpio):
    df_final=df_limpio.groupby(["centro deportivo"]).agg({"distancia_m":["min"]}).reset_index()
    df_final.columns=["centro deportivo","min"]
    df_min=df_final[("min")].dropna().astype(int)
    final=df_limpio.loc[df_min]
    df_fin=pd.merge(df_final,final[["centro deportivo","address","distrito"]],on="centro deportivo")
    return df_fin
#df_fin=analyze(df_limpio)
#df_fin


# In[11]:


def save_csv(df_fin):
    df_fin.to_csv("../csv/direcciones.csv",sep=';', index=False)


# In[26]:


def argument_parser():
    parser       = argparse.ArgumentParser(description= 'Closest bicimad to sports centers')
    help_message ='You have to introduce two input. Update?: "total" for yes: "csv" for no: and "centro" for other. Sport Center (please select "centro" as first input)'
    parser.add_argument('-u', '--update', help=help_message, type=str)
    #parser.add_argument('-c', '--centro', help=help_message,type=str,)
    args = parser.parse_args()
    return args


# In[23]:
if __name__ == '__main__':
    if argument_parser().update == 'total': #Actualiza el csv
        df_bicimad,df_deportivo        = acquire()
        df_bicim,df_centrosd,df_limpio = merge_clean(df_bicimad,df_deportivo)
        df_limpio                      = distancia_min(df_limpio)
        df_fin                         = analyze(df_limpio)
        save_csv(df_fin)
        result                         = df_fin
        
    elif argument_parser().update == 'csv': #No actualiza, carga el csv anterior
        result=pd.read_csv("../csv/direcciones.csv",sep=';') # consultar como cargar un doc cvs
      
    elif argument_parser().update == 'centro': #BiciMad cercano al centro deportivo especificado
        df_fin= pd.read_csv("../csv/direcciones.csv",sep=';')
        #df_fin = df_fin.set_index('centro deportivo')
        centro_deportivo=input(str("lugar: "))
        indice = df_fin[df_fin['centro deportivo'] == centro_deportivo].index
        #f_fin.columns=["address","distrito","centro deportivo","min"]
        #centro_deportivo=input(str("lugar: "))
        #df_dato=df_fin.loc['centro ', axis=0]
        result = df_fin.iloc[indice]
        
    else:
        result = 'FATAL ERROR...you need to select the correct method'
    print(f'The result is => {result}')
        

