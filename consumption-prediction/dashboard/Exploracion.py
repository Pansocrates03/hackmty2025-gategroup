import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Funciones de gráficos
def plot_consumption_vs_returned(df):
    df_category = df.groupby(['Service_Type']).sum().reset_index()

    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    index = np.arange(len(df_category['Service_Type']))

    plt.bar(index - bar_width/2, df_category['Quantity_Consumed'], bar_width, label='Consumido')
    plt.bar(index + bar_width/2, df_category['Quantity_Returned'], bar_width, label='Retornado')

    plt.xlabel('Tipo de Servicio')
    plt.ylabel('Cantidad')
    plt.title('Comparación de Cantidades Consumidas y Retornadas por Tipo de Servicio')
    plt.xticks(index, df_category['Service_Type'])
    plt.legend()
    st.pyplot(plt)
    plt.clf()

def plot_porcentaje_retornado_por_producto(df):
    df_product = df.groupby('Product_Name').sum().reset_index()
    df_product['Porcentaje_Retornado'] = (df_product['Quantity_Returned'] / df_product['Quantity_Consumed']) * 100

    plt.figure(figsize=(12, 6))
    plt.bar(df_product['Product_Name'], df_product['Porcentaje_Retornado'], color='orange')
    plt.xlabel('Producto')
    plt.ylabel('Porcentaje Retornado (%)')
    plt.title('Porcentaje de Cantidad Retornada por Producto')
    plt.xticks(rotation=45)
    st.pyplot(plt)
    plt.clf()

def plot_porcentaje_retornado_por_FlightId(df):
    df_flight = df.groupby('Flight_ID').sum().reset_index()
    df_flight['Porcentaje_Retornado'] = (df_flight['Quantity_Returned'] / df_flight['Quantity_Consumed']) * 100
    
    # Ordenar por porcentaje retornado y obtener los top 10
    df_flight_top10 = df_flight.nlargest(10, 'Porcentaje_Retornado')

    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(df_flight_top10)), df_flight_top10['Porcentaje_Retornado'], color='green')
    plt.xlabel('ID de Vuelo')
    plt.ylabel('Porcentaje Retornado (%)')
    plt.title('Top 10 Vuelos con Mayor Porcentaje de Devolución')
    
    # Configurar las etiquetas del eje x con los Flight_ID
    plt.xticks(range(len(df_flight_top10)), df_flight_top10['Flight_ID'], rotation=45)
    
    # Añadir etiquetas con los porcentajes exactos sobre cada barra
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')
    
    plt.tight_layout()  # Ajustar el layout para que no se corten las etiquetas
    st.pyplot(plt)
    plt.clf()

st.title("Exploración de los Datos")
st.write("Aquí puedes explorar los datos de consumo y las características derivadas.")
df = pd.read_excel('D:\GIT\hackmty2025-gategroup\consumption-prediction\data\ConsumptionPrediction_Dataset_v1.xlsx')


st.subheader("Datos de Consumo")
# Aquí irían gráficos y tablas para explorar los datos de consumo
plot_consumption_vs_returned(df)
plot_porcentaje_retornado_por_producto(df)
plot_porcentaje_retornado_por_FlightId(df)


st.subheader("Características Derivadas")
st.write("Análisis de las características derivadas del conjunto de datos.")
# Aquí irían gráficos y tablas para explorar las características derivadas

st.subheader("Análisis Temporal")
st.write("Exploración de patrones temporales en los datos.")
# Aquí irían gráficos y tablas para explorar patrones temporales