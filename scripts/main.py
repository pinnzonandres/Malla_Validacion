import pandas as pd
from Malla_Validacion import validacion
import argparse

import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)


# Argumentos para correr la función
parser = argparse.ArgumentParser(description='Descripción de tu programa')
parser.add_argument('--nombre_api', type=str, help='Nombre del API')
parser.add_argument('--json_malla', action='store_true', help='Indicar si se usará JSON para la malla')
parser.add_argument('--nombre_malla', type=str, help='Nombre de la malla')


if __name__ == "__main__":

    try:
        args = parser.parse_args()
        datos = validacion(nombre_api= args.nombre_api, json_malla = args.json_malla, nombre_malla=args.json_malla)
    except Exception as e:
        print('Añade los argumentos necesarios para correr la función')
        print(e)
        
    test, validas, novalidas = datos.validar_datos()
    
    test.to_excel('..\\results\\test.xlsx', index = False)
    validas.to_excel('..\\results\\validas.xlsx', index = False)
    novalidas.to_excel('..\\results\\novalidas.xlsx', index = False)