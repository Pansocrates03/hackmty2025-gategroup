import streamlit as st

st.title("Predicción de Consumo")
st.write("Aquí puedes ver las predicciones de consumo basadas en el modelo entrenado.")

st.date_input("Selecciona una fecha")
st.selectbox("Selecciona un producto", ["Producto A", "Producto B", "Producto C"])
st.selectbox("Selecciona un lugar de origen", ["Ubicación 1", "Ubicación 2", "Ubicación 3"])

st.chat_input("¿Tienes alguna pregunta sobre las predicciones?")