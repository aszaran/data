import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.markers as mk
import matplotlib.ticker as mtick
from scipy.optimize import fmin
import matplotlib.pyplot as plt
import openpyxl
import streamlit as st

# Crear diccionarios vacío para guardar los dfs
dfs_int_USD = {}
dfs_local_PYG = {}

# Cargar los excels
xls_int_USD = pd.ExcelFile('Rendimientos_bonos_internacionales_USD.xlsx')
xls_local_PYG = pd.ExcelFile('PYG_local_bonds.xlsx')

# Iterar sobre cada hoja para agregar al diccionario
for hoja in xls_int_USD.sheet_names:
    dfs_int_USD[hoja] = pd.read_excel(xls_int_USD, hoja, header=0)

# Iterar sobre cada hoja para agregar al diccionario
for hoja in xls_local_PYG.sheet_names:
    dfs_local_PYG[hoja] = pd.read_excel(xls_local_PYG, hoja, header=0)

# %%
# Convertir las fechas de vencimiento objeto de tipo 'datetime'
for nombre, df in dfs_int_USD.items():
    # Excluir la hoja 'Vencimientos' porque tiene distintos datos
    if nombre == 'Vencimientos':
        continue
    else:
        try:
            # Convertir la columna 'Fecha' a datetime previendo distintos formatos y que inicia con el dia
            df['Fecha'] = pd.to_datetime(df['Fecha'], format= 'mixed', dayfirst=True)
        except Exception as e:
            # Imprimir el nombre_usd de la hoja y el error para manejar excepciones
            print(f"Error al procesar la hoja '{nombre}': {e}")

# %%
# Configurar las fechas de vencimiento
for nombre, df in dfs_local_PYG.items():
    # Excluir la hoja 'Vencimientos' porque tiene datos distintos
    if nombre == 'Vencimientos':
        continue
    else:
        try:
            # Convertir la columna 'Fecha' a datetime previendo distintos formatos y que inicia con el dia
            df['Date'] = pd.to_datetime(df['Date'], format= 'mixed', dayfirst=True)
        except Exception as e:
            # Imprimir el nombre_usd de la hoja y el error para manejar excepciones
            print(f"Error al procesar la hoja '{nombre}': {e}")

# %%
# Crear df para guardar las fechas de vencimiento de los bonos
df_int_USD_maturity = dfs_int_USD['Vencimientos']
dfs_int_USD.pop('Vencimientos')

########### falta configurar las fechas###################

# %%
# Crear df para guardar las fechas de vencimiento de los bonos
df_local_PYG_maturity = dfs_local_PYG['Vencimientos']
dfs_local_PYG.pop('Vencimientos')

########### falta configurar las fechas###################

# %%
# Crear df para guardar los rendimientos de los bonos
df_int_USD_yield = None

# Iterar sobre cada df para unirlos
for nombre, df in dfs_int_USD.items():
    if df_int_USD_yield is None:
        df_int_USD_yield = df
    else:
        # Unir utilizando la columna 'Fecha' como referencia con una unión 'outer'
        df_int_USD_yield = pd.merge(df_int_USD_yield, df, on='Fecha', how='outer', suffixes=('', f'_{nombre}'))

# Configurar índice como fechas
df_int_USD_yield.set_index('Fecha', inplace=True)
# Ordenar índice del más viejo al más nuevo
df_int_USD_yield.sort_index(inplace=True)
df_int_USD_yield.head()

############### Eliminar fila rara
df_int_USD_yield.drop(columns=['Unnamed: 2'], inplace=True)

# %%
# Crear df para guardar los rendimientos de los bonos
df_local_PYG_yield = None

# Iterar sobre cada df para unirlos
for nombre, df in dfs_local_PYG.items():
    if df_local_PYG_yield is None:
        # Guarda la primera hoja como df para unir con las demas
        df_local_PYG_yield = df
    else:
        # Unir utilizando la columna 'Fecha' como referencia con una unión 'outer'
        df_local_PYG_yield = pd.merge(df_local_PYG_yield, df, on='Date', how='outer', suffixes=('', f'_{nombre}'))

# Configurar índice como fechas
df_local_PYG_yield.set_index('Date', inplace=True)
# Ordenar índice del más viejo al más nuevo
df_local_PYG_yield.sort_index(inplace=True)
df_local_PYG_yield.head()

# %%
# Seleccionar ultima fecha disponible para analizar datos
date_int_USD = st.sidebar.date_input('Selecciona una fecha para bonos USD', df_int_USD_yield.index[-1])
date_int_USD = pd.Timestamp(date_int_USD)
# Extraer la fila correspondiente 
data_int_USD = df_int_USD_yield.loc[date_int_USD]
# Transponer la fila para convertir en columna
df_int_USD_analysis = data_int_USD.transpose().to_frame()
# Renombrar la columna
df_int_USD_analysis.columns = ['Yield']
# Convertir el yield a porcentaje
df_int_USD_analysis['Yield'] = df_int_USD_analysis['Yield'] / 100
# df_int_USD_analysis

# %%
# Seleccionar ultima fecha disponible para analizar datos
date_local_PYG = st.sidebar.date_input('Selecciona una fecha para bonos PYG', df_local_PYG_yield.index[-1])
date_local_PYG = pd.Timestamp(date_local_PYG)
# Extraer la fila correspondiente
data_local_PYG = df_local_PYG_yield.loc[date_local_PYG]
# Transponer la fila para convertir en columna
df_local_PYG_analysis = data_local_PYG.transpose().to_frame()
# Renombrar la columna
df_local_PYG_analysis.columns = ['Yield']
# Convertir el Yield a porcentaje
df_local_PYG_analysis['Yield'] = df_local_PYG_analysis['Yield'] / 100
# df_local_PYG_analysis

# %%
# Agregar al df la madurez de los bonos
df_int_USD_analysis['Maturity'] = (pd.to_datetime(df_int_USD_maturity['Fecha de vencimiento'], dayfirst= True) - 
                                   pd.to_datetime(date_int_USD, dayfirst= True)
).values
df_int_USD_analysis['Maturity'] = (df_int_USD_analysis['Maturity'].dt.days / 360)
# df_int_USD_analysis

# %%
# Agregar al df la madurez de los bonos
df_local_PYG_analysis['Maturity'] = (pd.to_datetime(df_local_PYG_maturity['Fecha de vencimiento'], dayfirst= True) - 
                                     pd.to_datetime(date_local_PYG, dayfirst= True)
).values
df_local_PYG_analysis['Maturity'] = (df_local_PYG_analysis['Maturity'].dt.days / 360)
# df_local_PYG_analysis

# %%
# Copiar base de datos para el modelo de regresion
dd_USD = df_int_USD_analysis.copy()
dd_USD.sort_values('Maturity', inplace=True)
df_USD = dd_USD.copy()
# df_USD.style.format({'Maturity': '{:,.2f}'.format,'Yield': '{:,.2%}'})

# %%
# Ordenar de mayor a menor madurez
dd_PYG = df_local_PYG_analysis.copy()
dd_PYG.sort_values('Maturity', inplace=True)
df_PYG = dd_PYG.copy()
# df_PYG.style.format({'Maturity': '{:,.2f}'.format,'Yield': '{:,.2%}'})

# %%
# Inicializar coeficientes del modelo de regresion
β0_USD = 0.01
β1_USD = 0.01
β2_USD = 0.01
λ_USD = 1.00

# Calcular los retornos teoricos con el modelo Nelson-Siegel
df_USD['NS'] = (
    (β0_USD)+
    (β1_USD*((1-np.exp(-df_USD['Maturity']/λ_USD))/(df_USD['Maturity']/λ_USD)))+
    (β2_USD*((((1-np.exp(-df_USD['Maturity']/λ_USD))/(df_USD['Maturity']/λ_USD)))-(np.exp(-df_USD['Maturity']/λ_USD))))
)
# df_USD.style.format({'Maturity': '{:,.0f}'.format,'Yield': '{:,.2%}','NS': '{:,.2%}'})

# %%
# Calcular el error cuadratico como la diferencia entre los retornos observados y los retornos teoricos
df_USD['SE'] =  (df_USD['Yield'] - df_USD['NS'])**2
df22_USD = df_USD[['Maturity','Yield','NS','SE']]  
# df22_USD.style.format({'Maturity': '{:,.0f}'.format,'Yield': '{:,.2%}','NS': '{:,.2%}','SE': '{:,.9f}'})

# %%
# Definición de una función para calcular la suma de residuos cuadrados
def myval_USD(c):
    # Se crea una copia del DataFrame original para manipulación
    df_USD = dd_USD.copy()
    # Cálculo de los rendimientos teóricos utilizando los coeficientes del modelo de Nelson-Siegel
    df_USD['NS'] = (
        (c[0]) +
        (c[1] * ((1 - np.exp(-df_USD['Maturity'] / c[3])) / (df_USD['Maturity'] / c[3]))) +
        (c[2] * ((((1 - np.exp(-df_USD['Maturity'] / c[3])) / (df_USD['Maturity'] / c[3]))) - (np.exp(-df_USD['Maturity'] / c[3]))))
    )
    # Cálculo de los residuos cuadrados entre los rendimientos observados y los teóricos
    df_USD['MS'] = (df_USD['Yield'] - df_USD['NS']) ** 2
    # Suma de los residuos cuadrados para obtener una medida de la calidad del ajuste
    error_USD = np.sum(df_USD['MS'])
    print("[β0, β1, β2, λ]=", c, ", SUM:", error_USD)
    return error_USD
# Optimización de los coeficientes del modelo de Nelson-Siegel utilizando la regresion de mínimos cuadrados
c_USD = fmin(myval_USD, [0.01, 0.00, -0.01, 1.0])

# Extracción de los coeficientes ajustados
β0_USD = c_USD[0]
β1_USD = c_USD[1]
β2_USD = c_USD[2]
λ_USD = c_USD[3]
print("[β0, β1, β2, λ]=", [c_USD[0].round(2), c_USD[1].round(2), c_USD[2].round(2), c_USD[3].round(2)])

# %%
# Actualización de los rendimientos teóricos utilizando los coeficientes ajustados
df_USD = df_USD.copy()
df_USD['NS'] = (
    (β0_USD) +
    (β1_USD * ((1 - np.exp(-df_USD['Maturity'] / λ_USD)) / (df_USD['Maturity'] / λ_USD))) +
    (β2_USD * ((((1 - np.exp(-df_USD['Maturity'] / λ_USD)) / (df_USD['Maturity'] / λ_USD))) - (np.exp(-df_USD['Maturity'] / λ_USD))))
)

# Creación de DataFrames para visualización y procesamiento adicional de los datos
sf4_USD = df_USD.copy()
sf5_USD = sf4_USD.copy()
sf5_USD['Y'] = round(sf4_USD['Yield'] * 100, 4)
sf5_USD['N'] = round(sf4_USD['NS'] * 100, 4)
sf4_USD = sf4_USD.style.format({'Maturity': '{:,.2f}'.format, 'Yield': '{:,.2%}', 'NS': '{:,.2%}'})
# sf4_USD

# %%
# Definición de algunas variables adicionales
M0 = 0.00
M1 = 3.50

# %%
# Graficar retornos y retornos teoricos
X_USD = sf5_USD["Maturity"]
Y_USD = sf5_USD["Y"]
X_USD = sf5_USD["Maturity"]
Y_USD = sf5_USD["N"]
fontsize=15
fig_int_USD = plt.figure(figsize=(13,7))
plt.title("Bonos USD, mercado internacional",fontsize=fontsize)
fig_int_USD.patch.set_facecolor('white')
plt.plot(X_USD, Y_USD, color="orange", label="Modelo NS")
plt.scatter(X_USD, Y_USD, marker="o", c="orange")
plt.scatter(X_USD, Y_USD, marker="o", c="blue")
plt.xlabel('Maturity (in years)',fontsize=fontsize)
plt.ylabel('Yield (%)',fontsize=fontsize)
plt.legend(loc="lower right")
plt.grid()
plt.show()

# %%
# Inicializar coeficientes del modelo de regresion
β0_PYG = 0.01
β1_PYG = 0.01
β2_PYG = 0.01
λ_PYG = 1.00

# Calcular los retornos teoricos con el modelo Nelson-Siegel
df_PYG['NS'] = ((β0_PYG)+
                (β1_PYG*((1-np.exp(-df_PYG['Maturity']/λ_PYG))/(df_PYG['Maturity']/λ_PYG)))+
                (β2_PYG*((((1-np.exp(-df_PYG['Maturity']/λ_PYG))/(df_PYG['Maturity']/λ_PYG)))-(np.exp(-df_PYG['Maturity']/λ_PYG))))
)
# df_PYG.style.format({'Maturity': '{:,.0f}'.format,'Yield': '{:,.2%}','NS': '{:,.2%}'})

# %%
# Calcular el error como la diferencia entre los retornos observados y los retornos teoricos elevada al cuadrado
df_PYG['MS'] =  (df_PYG['Yield'] - df_PYG['NS'])**2
df22_PYG = df_PYG[['Maturity','Yield','NS','MS']]
df22_PYG.style.format({'Maturity': '{:,.0f}'.format,'Yield': '{:,.2%}','NS': '{:,.2%}','MS': '{:,.9f}'})

# Definición de una función para calcular la suma de residuos cuadrados
def myval_PYG(c):
    df_PYG = dd_PYG.copy()
    df_PYG['NS'] =(c[0])+(c[1]*((1-np.exp(-df_PYG['Maturity']/c[3]))/(df_PYG['Maturity']/c[3])))+(c[2]*((((1-np.exp(-df_PYG['Maturity']/c[3]))/(df_PYG['Maturity']/c[3])))-(np.exp(-df_PYG['Maturity']/c[3]))))
    df_PYG['MS'] =  (df_PYG['Yield'] - df_PYG['NS'])**2
    val_pyg = np.sum(df_PYG['MS'])
    print("[β0, β1, β2, λ]=",c,", SUM:", val_pyg)
    return(val_pyg)
c_PYG = fmin(myval_PYG, [0.01, 0.00, -0.01, 1.0])

# Extracción de los coeficientes ajustados
β0_PYG = c_PYG[0]
β1_PYG = c_PYG[1]
β2_PYG = c_PYG[2]
λ_PYG = c_PYG[3]
print("[β0, β1, β2, λ]=", [c_PYG[0].round(2), c_PYG[1].round(2), c_PYG[2].round(2), c_PYG[3].round(2)])

# %%
# Actualización de los rendimientos teóricos utilizando los coeficientes ajustados
df_PYG = df_PYG.copy()
df_PYG['NS'] = ((β0_PYG)+
                (β1_PYG*((1-np.exp(-df_PYG['Maturity']/λ_PYG))/(df_PYG['Maturity']/λ_PYG)))+
                (β2_PYG*((((1-np.exp(-df_PYG['Maturity']/λ_PYG))/(df_PYG['Maturity']/λ_PYG)))-(np.exp(-df_PYG['Maturity']/λ_PYG))))
)

# %%
# Creación de DataFrames para visualización y procesamiento adicional de los datos
sf4_PYG = df_PYG.copy()
sf5_PYG = sf4_PYG.copy()
sf5_PYG['Y'] = round(sf4_PYG['Yield']*100,4)
sf5_PYG['N'] = round(sf4_PYG['NS']*100,4)
sf4_pyg = sf4_PYG.style.format({'Maturity': '{:,.2f}'.format,'Yield': '{:,.2%}', 'NS': '{:,.2%}'})

# %%
# Definición de algunas variables adicionales
M0 = 0.00
M1 = 3.50

# %%
# Graficar retornos y retornos teoricos
X_PYG = sf5_PYG["Maturity"]
Y_PYG = sf5_PYG["Y"]
x_PYG = sf5_PYG["Maturity"]
y_PYG = sf5_PYG["N"]
fontsize=15
fig_local_PYG = plt.figure(figsize=(13,7))
plt.title("Bonos PYG, mercado local",fontsize=fontsize)
fig_local_PYG.patch.set_facecolor('white')
plt.plot(x_PYG, y_PYG, color="purple", label="Modelo NS")
plt.scatter(x_PYG, y_PYG, marker="o", c="purple")
plt.scatter(X_PYG, Y_PYG, marker="o", c="orange")
plt.xlabel('Maturity (in years)',fontsize=fontsize)
plt.ylabel('Yield (%)',fontsize=fontsize)
plt.legend(loc="lower right")
plt.grid()
plt.show()

# Graficar en streamlit
st.title('Curva de rendimientos')
st.pyplot(fig_int_USD)

# Input de streamlit para calcular el retorno teorico de una madurez
st.sidebar.title('Bonos internacionales en USD')
maturity_USD_input = st.sidebar.number_input('Madurez (en años)', min_value=0.0, max_value=30.0, value=5.0)

# Validar la entrada del usuario y calcular el rendimiento teórico
try:
    # Cálculo del rendimiento teórico utilizando la función definida previamente
    yield_USD = ((β0_USD) +
                (β1_USD * ((1 - np.exp(-maturity_USD_input / λ_USD)) / (maturity_USD_input / λ_USD))) +
                (β2_USD * ((((1 - np.exp(-maturity_USD_input / λ_USD)) / (maturity_USD_input / λ_USD))) - (np.exp(-maturity_USD_input / λ_USD))))
    )
    # Renderiza el resultado en Streamlit
    st.write(f'Rendimiento teórico para madurez de {maturity_USD_input} años en bonos USD: {yield_USD:.2%}')
except ValueError:
    st.error('Por favor ingresa un valor numérico válido para la madurez.')

# Graficar en streamlit
st.pyplot(fig_local_PYG)

# Input de streamlit para calcular el retorno teorico de una madurez
st.sidebar.title('Bonos locales en PYG')
maturity_PYG_input = st.sidebar.number_input('Madurez (en años)', min_value=0.0, max_value=20.0, value=5.0)

# Validar la entrada del usuario y calcular el rendimiento teórico
try:
    # Cálculo del rendimiento teórico utilizando la función definida previamente
    yield_PYG = ((β0_PYG) +
                (β1_PYG * ((1 - np.exp(-maturity_PYG_input / λ_PYG)) / (maturity_PYG_input / λ_PYG))) +
                (β2_PYG * ((((1 - np.exp(-maturity_PYG_input / λ_PYG)) / (maturity_PYG_input / λ_PYG))) - (np.exp(-maturity_PYG_input / λ_PYG))))
    )
    # Renderiza el resultado en Streamlit
    st.write(f'Rendimiento teórico para madurez de {maturity_PYG_input} años en bonos USD: {yield_PYG:.2%}')
except ValueError:
    st.error('Por favor ingresa un valor numérico entre 0 y 20.')

# Graficar rendimientos
fig_USD_yield = plt.figure(figsize=(12, 8))
for column in df_int_USD_yield.columns:
    if column == 'Unnamed: 2':
        continue
    plt.plot(df_int_USD_yield.index, df_int_USD_yield[column], label=column)
plt.title("Bonos USD, mercado internacional")
plt.ylabel("Rendimiento (%)")
plt.legend(loc="best")
plt.grid(True)
plt.show()
# Graficar en streamlit
st.pyplot(fig_USD_yield)


# Graficar rendimientos
fig_PYG_yield = plt.figure(figsize=(12, 8))
for column in df_local_PYG_yield.columns:
    plt.plot(df_local_PYG_yield.index, df_local_PYG_yield[column], label=column)
plt.title("Bonos PYG, mercado local")
plt.ylabel("Rendimiento (%)")
plt.legend(loc="best")
plt.grid(True)
plt.show()
# Graficar en streamlit
st.pyplot(fig_PYG_yield)



