import pandas as pd
import numpy as np
import json
import requests
import malla_functions as mf


class validacion:
    def __init__(self, nombre_api:str, json_malla: bool, nombre_malla : str, ruta:str):
        self.config = "{}\\config\\{}.json".format(ruta, nombre_api) 
        self.bool_malla = json_malla
        self.ruta = ruta
        self.nombre_malla = nombre_malla
        self.malla = dict()
        self.token = dict()
        self.dataframe = pd.DataFrame
        self.validacion = pd.DataFrame
        
    def get_token(self):
        try: 
            with open(self.config) as file:
                self.token = json.load(file) 
        except Exception as e:
            print(e)  
    
    def get_dataframe(self):
        self.get_token() 
        
        try: 
            response = requests.get(self.token["url"],
                                    headers = self.token["headers"])
        except Exception as e:
            print("Conexión Fallida")
            print(e)
        
        try:
            self.dataframe = pd.json_normalize(response.json())
            print("Dataframe Cargado desde el API")
        except Exception as e:
            print('No se cargo correctamente como dataframe la información del API')
            print(e)
            
    def normalize_data(self):
        try:
            self.dataframe =  self.dataframe.explode('respuestas.integrante').reset_index(drop=True)
            df_resp_integrante = pd.json_normalize(self.dataframe['respuestas.integrante'])
            df_resp_integrante = df_resp_integrante.rename(columns={'identificacion':'identificacion_integrante'})
            self.dataframe = pd.concat([self.dataframe, df_resp_integrante], axis=1)
            self.dataframe = self.dataframe.rename(columns=lambda x: x.replace('respuestas.', ''))
            
        except Exception as e:
            print("Normalización del Dataframe Cancelado")
            print(e)
    
    def get_malla(self):
        if self.bool_malla:
             ruta = '{}\\data\\validation_json\\{}.json'.format(self.ruta, self.nombre_malla)
             with open(ruta, encoding='utf-8') as file:
                 self.malla = json.load(file)
        else:
            ruta =  '{}\\data\\validation_excel\\{}.xlsx'.format(self.ruta, self.nombre_malla)
            ruta_export = '{}\\data\\validation_json\\{}.json'.format(self.ruta, self.nombre_malla)
            try:
                cond = pd.read_excel(ruta, sheet_name='Validaciones')
                val = pd.read_excel(ruta, sheet_name='Valores')
                val = val.dropna(subset=['Valores'])
            except Exception as e:
                print('Nombre o archivo excel erroneo')
                print(e)
            
            try:
                self.malla = mf.create_malla_dict(condiciones = cond, valores = val)
            except Exception as e:
                print('Estructura del Archivo excel erroneo')
                print(e)
            
            try:
                with open(ruta_export, 'w', encoding='utf8') as file:
                    json.dump(self.malla, file, ensure_ascii=False, indent = 1)
            except Exception as e:
                print('Error al intentar exportar el archivo json')
                print(e)
                
                
    def validar_datos(self):
        
        self.get_token()
        self.get_dataframe()
        self.normalize_data()
        self.get_malla()
        self.dataframe = mf.expand_cols(self.dataframe, self.malla)
        
        print("INICIO PROCESO DE VALIDACIÓN DE DATOS")
        validacion = mf.malla_validacion(data = self.dataframe, guia_validacion = self.malla)
        return validacion
        