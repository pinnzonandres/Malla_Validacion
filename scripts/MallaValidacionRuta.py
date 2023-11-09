"""Malla Validacion Ruta
Este Script es un módulo donde define la clase encargada de utilizar las funciones definidas y validar la información
"""
# Autor: Wilson Andrés Pinzón Cortés
# Correo electrónico: wilson.pinzon@prosperidadsocial.gov.co - pinnzonandres@gmail.com
# Fecha de creación: 2023-11-07
# Última modificación: 2023-11-07
# Versión: 1.0
# Este código está bajo la licencia MIT.
# Copyright (c) 2023 Wilson Andrés Pinzón Cortés


# Se importan las librerias necesarias
import pandas as pd
import numpy as np
import json
import requests

# Se importa el script MallaFunctions como un módulo para poder acceder a sus funciones
import malla_functions as mf
from schema import Schema, And, Use, Optional, SchemaError, Or


# Definición de la clase validacion
class validacion:
    """Esta clase tiene como objetivo descargar y validar los datos a partir de la malla de validación entregada
    
    Atributos: 
            - token (dict) : Nombre del archivo json config donde se encuentra la puerta de acceso a los datos por medio del API de RIT
            - json_malla (bool) : Booleano que le indica a la clase si la malla de validación ya se encuentra en formato JSON o se debe crear a partir del archivo Excel
            - nombre_malla (str) : Nombre que identifica a la malla de validación, ya sea de tipo JSON o de tipo Excel (Ambos archivos deben tener el mismo nombre)
            - ruta (str) : Cadena de texto que ubica la ruta a la carpeta del proyecto o al repositorio
    """
    def __init__(self, token:dict, json_malla: bool, nombre_malla : str, ruta:str):
        """
        Inicialización de la instancia validación
        
        Args:
            token (dict) : Nombre del archivo json config donde se encuentra la puerta de acceso a los datos por medio del API de RIT
            json_malla (bool) : Booleano que le indica a la clase si la malla de validación ya se encuentra en formato JSON o se debe crear a partir del archivo Excel
            nombre_malla (str) : Nombre que identifica a la malla de validación, ya sea de tipo JSON o de tipo Excel (Ambos archivos deben tener el mismo nombre)
            ruta (str) : Cadena de texto que ubica la ruta a la carpeta del proyecto o al repositorio
        """
        self.config = token
        self.bool_malla = json_malla
        self.ruta = ruta
        self.nombre_malla = nombre_malla
        self.malla = dict()
        self.dataframe = pd.DataFrame
        self.validacion = pd.DataFrame
        
    # Método que lee el archivo JSON con la configuracion
    def get_token(self):
        """Método que revisa si la estructura del token está correcta
        """
        conf_schema = Schema({"url": And(Use(str)),"method": And(str, lambda s: s == "GET"),"headers": {"Authorization":And(Use(str))}})
        
        try: 
            mf.check(conf_schema = conf_schema, token=self.config)
        except Exception as e:
            print(e)  
            
    # Método que accede al API para poder leer el dataframe
    def get_dataframe(self):
        """Método de la clase validación que accede al conjunto de datos del API a través del token de acceso
        
        Args:
            None
        """
        # Accede al archivo Config
        try:
            self.get_token() 
        except:
            print("Problema con el Token")
        
        # Se realiza la conexión con el API
        try: 
            response = requests.get(self.config["url"],
                                    headers = self.config["headers"])
        except Exception as e:
            print("Conexión Fallida")
            print(e)
        
        # Almacena en un dataframe de Pandas el resultado del acceso
        try:
            self.dataframe = pd.json_normalize(response.json())
            print("Dataframe Cargado desde el API")
        except Exception as e:
            print('No se cargo correctamente como dataframe la información del API')
            print(e)
            
    # Método para normalizar el dataframe y expandir las respuestas de Integrantes
    def normalize_data(self):
        try:
            # Expande las respuestas de cada encuesta
            self.dataframe =  self.dataframe.explode('respuestas.integrante').reset_index(drop=True)
            
            # Expande las respuestas de los integrantes
            df_resp_integrante = pd.json_normalize(self.dataframe['respuestas.integrante'])
            df_resp_integrante = df_resp_integrante.rename(columns={'identificacion':'identificacion_integrante'})
            
            # Concatena las respuestas de los integrantes
            self.dataframe = pd.concat([self.dataframe, df_resp_integrante], axis=1)
            
            # Elimina de los nombres de la expansión el prefijo "respuestas."
            self.dataframe = self.dataframe.rename(columns = lambda x: x.replace('respuestas.', ''))
            
        except Exception as e:
            print("Normalización del Dataframe Cancelado")
            print(e)
    
    # Método para extraer la malla de validación
    def get_malla(self):
        
        # Si la malla ya está en formato JSON lee este archivo
        if self.bool_malla:
             ruta = '{}/data/validation_json/{}.json'.format(self.ruta, self.nombre_malla)
             with open(ruta, encoding='utf-8') as file:
                 self.malla = json.load(file)
        # Si la malla no está en formato json, lee el archivo excel y exporta su resultado como un JSON
        else:
            ruta =  '{}/data/validation_excel/{}.xlsx'.format(self.ruta, self.nombre_malla)
            ruta_export = '{}/data/validation_json/{}.json'.format(self.ruta, self.nombre_malla)
            try:
                cond = pd.read_excel(ruta, sheet_name='Validaciones')
                val = pd.read_excel(ruta, sheet_name='Valores')
                val = val.dropna(subset=['valores'])
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
                
                
    # Método que valida los datos
    def validar_datos(self):
        """Método de la clase validación que se encarga de validar la información del conjunto de datos a través de la malla de validación obtenida

        Returns:
            (pd.DataFrame, pd.Dataframe, pd.Dataframe):  Devuelve tres dataframes de Pandas con los resultados de la validación, la validación general, 
            los registros validos y los registros no validos
        """
        # Obtiene el dataframe del API
        self.get_dataframe()
        
        # Normaliza la información del dataframe
        self.normalize_data()
        
        # Obtiene la malla de validación
        self.get_malla()
        
        try:
            # Expande las posibles columnas adicionales que se deben expandir
            self.dataframe = mf.expand_cols(self.dataframe, self.malla)
            print("Dataframe Expandido")
        except Exception as e:
            print("No se logró expandir el dataframe")
            print(e)
        
        
        # Se inicia el proceso de validación
        print("INICIO PROCESO DE VALIDACIÓN DE DATOS")
        try:
            validacion, validas, novalidas = mf.malla_validacion(data = self.dataframe, guia_validacion = self.malla)
            print("FINZALIZACIÓN PROCESO DE VALIDACIÓN DE DATOS")
            return validacion, validas, novalidas
        except Exception as e:
            print("Problemas al intentar validar la información")
            print(e)
        