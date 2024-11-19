#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import argparse
import ipynb

from ipynb.fs.full.funci_aux import acquire,merge_clean,distancia_min,analyze
def argument_parser():
    parser       = argparse.ArgumentParser(description= 'Closest bicimad to sports centers')
    help_message ='You have to introduce two input. Update?: "Y" for yes: "N" for no: and "O" for other. Sport Center (please select "O" as first input)'
    parser.add_argument('-u', '--update', help='Y/N/O')
    parser.add_argument('-c', '--centro', type=int, help='Sports Center')
    args = parser.parse_args()
    return args
if __name__ == '__main__':
    if argument_parser().update == 'Y': #Actualiza el csv
        df_bicimad,df_deportivo        = acquire()
        df_bicim,df_centrosd,df_limpio = merge_clean(df_bicim,df_centrosd)
        df_limpio                      = distancia_min(df_limpio)
        df_fin                         = analyze(df_final)
        save_csv(df_fin)
        result                         = df_fin
        
    elif argument_parser().update == 'N': #No actualiza, carga el csv anterior
        result   =  pd.read_csv("../csv/direcciones.csv",sep=';', index=False)
      
    elif argument_parser().update == 'O': #BiciMad cercano al centro deportivo especificado
        df_fin   =  pd.read_csv("../csv/direcciones.csv",sep=';', index=False)
        centro   = argument_parser().centro
        result   = df_fin.loc[df_fin['centro deportivo'] == centro]
    else:
        result = 'FATAL ERROR...you need to select the correct method'
    print(f'The result is => {result}')
    

