import pandas as pd
import numpy as np


# Función para dejar las condiciones como lista o solo con valores
def get_list_condiciones(row):
    A = str(row['Condicion'])
    B = row['Tipo Validacion']
    if A =='nan':
        val = None
    else:
        if B == 'int':
            val = [int(i) for i in A.split("|")]
        else:
            val = [str(i) for i in A.split("|")]
    return val

# Función para definir los valores que puede tomar la variable
def get_list_valores(row):
    A = str(row['Valores'])
    B = row['Tipo Validacion']
    if A =='nan':
        val = None
    else:
        if B == 'int':
            val = [int(i) for i in A.split("|")]
        elif B == 'str':
            val = [str(i) for i in A.split("|")]
        else:
            val = A
    return val



## Creación de la malla de validación
def create_malla_dict(condiciones, valores):
    malla = dict()
    condiciones['Condicion'] = condiciones.apply(get_list_condiciones, axis = 1)
    valores['Valores'] = valores.apply(get_list_valores, axis = 1)
    try:
        result = condiciones.merge(valores, on = 'Variable', how = 'left')
    except Exception as e:
        print('Problemas con el archivo Excel de Malla de Validación')
        print(e)
        
    for index, row in result.iterrows():
        variable = row['Variable']
        dependiente = row['Dependiente']
        condicion = row['Condicion']
        excluye = row['Excluye Participar']
        obligatoria = row['Obligatorio']
        iand = row['iand']
        valor = row['Valores']
        condicion_valor = row['Tipo Validacion_y']
        
        if variable in malla.keys():
            malla[variable]['condicion'].update({dependiente : condicion})
        else:
            malla[variable] = {
                'condicion': None if pd.isna(dependiente) else {dependiente : condicion},
                'valores': None if pd.isna(condicion_valor) else {'valor':valor, 'Tipo': condicion_valor},
                'iand': False if pd.isna(iand) else True,
                'obligatoria': False if pd.isna(obligatoria) else True,
                'excluida_PTA': False if pd.isna(excluye) else True
                }
    return malla


## Crear las condiciones para cada variable o pregunta
def crear_condicion(diccionario, data, iand = False, general = False):
    condicion_total = None
    columnas_a_verificar = ['DESEAPARTICIPAR', 'HOGAR_DISPONE_TIERRA', 'HOGAR_DISPONE_AGUA']
    filtros = []
    for columna in columnas_a_verificar:
        if columna in data.columns:
            filtro = data[columna] == ('SI' if columna == 'DESEAPARTICIPAR' else True)
            filtros.append(filtro)
    
    if filtros:
        condicion_general = all(filtros)
    else:
        condicion_general = None
    
    if diccionario is None:
        if general:
            return condicion_general
        else:
            return None
    else:
        for col, valores in diccionario.items():
            if 'Edad' in col:
                condicion_col = data[col] > valores[0]
            else: 
                condicion_col = data[col].isin(valores)
            if condicion_total is None:
                condicion_total = condicion_col
            else:
                if iand:
                    condicion_total = condicion_total & condicion_col
                else:
                    condicion_total = condicion_total | condicion_col
            if general == False:
                return condicion_total & condicion_general
            else:
                return condicion_total
            
            
# Función para retornar verdadero o falso si la validación es de lista
def todos_en_valores_permitidos(row, lista, col):
    try:
        return all(valor in lista for valor in row[col])
    except:
        return False

def validar_listlist(row, lista, col):
    try:
        return all(all(valor in lista for valor in list) for list in row[col]) 
    except:
        return False

## Función para crear las condiciones en el caso que se deban validar los valores
def verificar_valores(diccionario, data, col):
    if diccionario is None:
        return None
    else:
        valores = diccionario['valor']
        tipo = diccionario['Tipo']
        if tipo == 'regex':
            condicion = data[col].astype(str).str.match(valores)
        elif tipo == 'list':
            condicion = data.apply(todos_en_valores_permitidos, args = (valores, col), axis = 1)
        elif tipo == 'listlist':
            condicion = data.apply(validar_listlist, args = (valores, col), axis = 1)
        else:
            condicion = data[col].isin(valores)
    return condicion

# Función que entrar a revisar las condiciones y valores a tomar
def validar_valor(condicion, values, col, data, file):
    file[col] = 0
    if condicion is None:
        val_data = data
    else:
        val_data = data[condicion]
    
    if values is None:
        val_series = val_data[col].isnull().astype(int)
    else:
        val_series = val_data.where(values)[col].isnull().astype(int)
        
    file[col].update(val_series)
    
    return file[col]


# Función para convertir las variables numéricas de tipo entero
def restore_type(data: pd.DataFrame, numeric: list or tuple):
    num_cols = list(set(list(data.select_dtypes(include=np.number).columns))|set(numeric))
    for col in num_cols:
        if col not in ['latitud', 'longitud']:
            try:
                data[col]= data[col].astype('float').astype('Int64')
            except:
                data[col] = np.floor(pd.to_numeric(data[col], errors='coerce')).astype('Int64')
    return data

def concatenate_Errores(row, cols_obligatorias):
    errores = []
    for col in cols_obligatorias:
        if row[col] == 1:
            errores.append(col)
    return ', '.join(errores) if row['Validacion'] > 0 else ''


#%%%%%%%%%%%%%%%%%%%%%%%
# Malla de Validación
#%%%%%%%%%%%%%%%%%%%%%%

def malla_validacion(data: pd.DataFrame, guia_validacion : dict) -> pd.DataFrame:
    columnas = [i for i in data.columns if i in guia_validacion.keys()]
    data = data[columnas]
    
    try:
        numeric = [n for n in [m for m in [i for i in guia_validacion.keys() if guia_validacion[i]['valores'] is not None] if guia_validacion[m]['valores']['Tipo'] == 'int'] if n in columnas]
    except Exception as e:
        print('Problemas con la malla de validación entregada')
        print(e)
    data = restore_type(data, numeric)
    
    store_file = data.copy()
    
    for col in columnas:
        try:
            condicion = crear_condicion(guia_validacion[col]['condicion'], data, guia_validacion[col]['iand'], guia_validacion[col]['excluida_PTA'])
            values = verificar_valores(guia_validacion[col]['valores'], data, col)
            store_file[col] = validar_valor(condicion = condicion, values = values, col = col, data = data, file = store_file)
        except Exception as e:
            print("Problema para validar la columna {}".format(col))
            print(e)
        
    obligatorias = [i for i in guia_validacion.keys() if guia_validacion[i]['obligatoria']== False]
    obligatorias = [i for i in obligatorias if i in store_file.columns]
    
    store_file['Documento_Duplicado'] = data['num_documento'].duplicated().astype(int)
    id_hogar = data['id']
    num_doc_representante = data['NUMERODOCUMENTOTITULAR']
    num_doc_integrante = data['num_documento']
    store_file.insert(0, 'ID_HOGAR', id_hogar)
    store_file.insert(1,'NUM_TITULAR', num_doc_representante)
    store_file.insert(2,'NUM_DOC_INTEGRANTE', num_doc_integrante)
    
    obligatorias.append('Documento_Duplicado')
    
    store_file['Validacion'] = store_file[obligatorias].sum(axis = 1)
    
    store_file['Errores'] = store_file.apply(concatenate_Errores, args=(obligatorias,), axis=1)
    
    resultados = store_file.groupby(by=['ID_HOGAR','NUM_TITULAR','NUM_DOC_INTEGRANTE'], as_index=False).agg({'Validacion':'sum'})
    data_con_errores = resultados[resultados['Validacion'] > 0].drop(columns = ['Validacion'])
    data_sin_errores = resultados[resultados['Validacion'] == 0].drop(columns = ['Validacion'])
    
    novalid = data_con_errores.merge(store_file, on=['ID_HOGAR','NUM_TITULAR','NUM_DOC_INTEGRANTE'], how='left')[['ID_HOGAR','NUM_TITULAR','NUM_DOC_INTEGRANTE','Validacion','Errores']]
    valid = data_sin_errores.merge(store_file, on=['ID_HOGAR','NUM_TITULAR','NUM_DOC_INTEGRANTE'], how='left')[['ID_HOGAR','NUM_TITULAR','NUM_DOC_INTEGRANTE','Validacion','Errores']]
    
    print("RESULTADOS MALLA DE VALIDACIÓN")
    print("El número total de elementos validados fueron {} participantes que equivale a {} Hogares".format(len(store_file), store_file['ID_HOGAR'].nunique()))
    print("="*70)
    print("El número total de participantes con valores correctos es {} que equivale a {} hogares".format(len(valid),valid['ID_HOGAR'].nunique()))
    print("="*70)
    print("El número total de participantes con valores erroneos es {} que equivale a {} hogares".format(len(novalid),novalid['ID_HOGAR'].nunique()))
    
    return store_file, valid, novalid



# EXPANDIR COLUMNAS
def remove_nans(row, col):
    A = row[col]
    valor = pd.isna(A).squeeze()
    forma = len(valor.shape)
    if forma == 0:
        if valor == True:
            return np.nan
        else:
            return A
    elif forma == 1:
        if all(i for i in valor):
            return np.nan
        else:
            return A
    else:
        if all(all(m for m in i) for i in valor):
            return np.nan
        else:
            return A
        
def expand_data_frame(col, data):
    expansion = pd.json_normalize(data[col].explode())
    relacion_filas = data[col].explode().index
    
    if len(list(expansion.columns)) == 1:
        expansion = expansion.rename(columns={list(expansion.columns)[0]:col})
        
    expansion['id'] = relacion_filas
    
    
    is_dict = expansion.transform(lambda x: x.apply(type).eq(list)).any()
    a_expandir = list(is_dict[is_dict==True].index)
    
    columnas = list(expansion.columns)
    columnas.remove("id")
    
    aggregation_dict = {
    columna: (lambda x: [i for i in x]) if columna in a_expandir else (lambda x: [i for i in x] if not all(pd.isna(i) for i in x) else np.nan)
    for columna in columnas
    }
    
    result = expansion.groupby('id', as_index=False).agg(aggregation_dict)
    
    for columna in a_expandir:
        result[columna] = result.apply(remove_nans, args=(columna,), axis = 1)
    
    result = result.drop(columns='id')
    return result

def expand_cols(data:pd.DataFrame, diccionario: dict):
    is_dict = data.transform(lambda x: x.apply(type).eq(list)).any()
    posible_expandir = list(is_dict[is_dict==True].index)
    try:
        Expandir = [i for i in posible_expandir if diccionario[i]['valores'] is None]
    except Exception as e:
        print("Error en la malla de validación")
        print(e)
    
    for columna in Expandir:
        try:
            result = expand_data_frame(columna, data)
            if len(result.columns) == 1:
                data = data.drop(columns = columna)
            data = pd.concat([data, result], axis = 1)
        except Exception as e:
            print("Problemas con la expansión de la columna {}".format(columna))
            print(e)
    
    return data
    

