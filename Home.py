import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="")

image_path = 'C:\\Users\\ramos\\Documents\\repos\\ftc_analisando_python\\dataset\\.ipynb_checkpoints\\logo.png'

st.sidebar.markdown ('# Kobe Foods')
st.sidebar.markdown ('## The Most Delicious and Faster Delivery')
st.sidebar.markdown ("""---""")

st.write ('# Kobe Foods - Growth Dashboard')

st.markdown ("""
   O Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard? 
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento. 
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador: 
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes    
""")