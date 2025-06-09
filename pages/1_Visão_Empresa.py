#Bibliotecas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import folium 
import re
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

# ---------- -------------------
# Definindo layout do streamlit
# ------------------------------
st.set_page_config(page_title= 'Visão Empresa', layout="wide")


# ----------------------------
# Importando o data set
# ----------------------------
df = pd.read_csv('../train.csv')

df1 = df.copy()

# -----------------------------------------
# Funções
# -----------------------------------------

def order_metric(df1):
    cols = ['ID', 'Order_Date']
    # Seleção de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    # Desenhar o gráfico de linha
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig




def traffic_order_city (df1):
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                 .groupby(['City', 'Road_traffic_density'])
                 .count()
                 .reset_index())
    
    fig = px.scatter (df_aux, x ='City', size ='ID', color='City')
    return fig



def traffic_order_share (df1):                
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby ('Road_traffic_density').count().reset_index()
        
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN",:]
    df_aux ['entregas_perc'] = df_aux['ID']/ df_aux['ID'].sum()
        
    fig = px.pie (df_aux, values ='entregas_perc', names ='Road_traffic_density')
    return fig



def order_by_week (df1):      
    # Criar a coluna de semana 
    df1 ['week_of_year'] = df1 ['Order_Date'].dt.strftime ('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby ('week_of_year').count().reset_index()
    fig = px.line (df_aux, x='week_of_year', y='ID')
    return fig



def order_share_by_week (df1):
    # Quantidade de pedidos por semana / Número único de entregadores por semana
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    
    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux ['order_by_deliver'] = df_aux ['ID']/df_aux ['Delivery_person_ID']
    
    fig = px.line (df_aux, x='week_of_year', y='order_by_deliver')
    return fig


def country_maps (df1):        
    # Agrupamento e mediana
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = (df1.loc[:, cols] \
                 .groupby(['City', 'Road_traffic_density']).median() \
                 .reset_index())
    
def country_maps(df1):        
    # Agrupamento e mediana
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = (df1.loc[:, cols]
                 .groupby(['City', 'Road_traffic_density']).median()
                 .reset_index())
    
    # Criar o mapa
    map = folium.Map()
    
    # Adicionar marcadores
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                       location_info['Delivery_location_longitude']],
                       popup=f"{location_info['City']} - {location_info['Road_traffic_density']}").add_to(map)
    
    folium_static(map, width=1024, height=600)
    return None


def clean_code (df1):

    """ Esta função tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança no tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (Remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    
    """
    

    # 1. Convertendo a coluna age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1 ['Delivery_person_Age'].astype(int)
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # Forçar NaNs para a string 'NaN' (para usar seu modelo de filtro)
    df1 ['City'] = df1['City'].fillna('NaN')
    df1 ['Road_traffic_density'] = df1['Road_traffic_density'].fillna('NaN')
    
    # Filtrar conforme seu padrão
    df1 = df1[df1['City'] != 'NaN']
    df1 = df1[df1['Road_traffic_density'] != 'NaN']
    
    
    # 2. Convertendo a coluna Ratings de texto para o numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # 3. Convertendo a coluna Ratings de texto para o numero decimal (float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y' )
    
    # 4. Convertendo a coluna multiple_deliveries de texto para numero inteiro
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1 ['multiple_deliveries'].astype(int)
    
    # 5. Removendo os espaços dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:,'Festival'].str.strip()
    
    # 7. limpando a coluna de time taken
    
    # 1. Extrair apenas o número (depois de "(min) ")
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    
    # 2. Remover espaços em branco
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.strip()
    
    # 3. Converter para inteiro
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

# =====================================================================================
# BARRA LATERAL
# =====================================================================================

df1 = clean_code(df1)

st.header ('Marketplace - Visão Empresa')

# image_path = 'C:\\Users\\ramos\\Documents\\repos\\ftc_analisando_python\\dataset\\.ipynb_checkpoints\\logo.png'
image=Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown ('# Kobe Foods')
st.sidebar.markdown ('## The Most Delicious and Faster Delivery')
st.sidebar.markdown ("""---""")

st.sidebar.markdown ('## Selecione a data limite')

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value= datetime(2022, 4, 13),
    min_value= datetime(2022, 2, 11),
    max_value= datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.sidebar.markdown ("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânisto?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown ("""---""")

# Garantir que 'Order_Date' está como datetime
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# Filtro de Datas
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]


# Mostrar dataframe, para validações
# st.dataframe (df1)

# Filtro de Tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc [linhas_selecionadas,:]

# Mostrar dataframe, para validações
# st.dataframe (df1)

# =====================================================================================
# LAYOUT NO STREAMLIT
# =====================================================================================


tab1, tab2, tab3 = st.tabs (['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Metrics   
        fig = order_metric (df1)
        st.markdown("# Pedidos por Dia")
        st.plotly_chart(fig, use_container_width=True)
            
        
    
        with st.container():
            col1, col2 = st.columns(2)

        with col1:
            fig = traffic_order_share (df1)
            st.header ('Divisão de Pedidos por Tipo de Tráfego')
            st.plotly_chart (fig, use_container_width=True)


        with col2:
            
            st.header ('Pedidos por Tipo de Cidade e Tráfego')
            fig = traffic_order_city (df1)
            st.plotly_chart (fig, use_container_width=True)
           

    st.markdown("") 

with tab2:
    with st.container():
        st.markdown("### Pedidos por Semana")
        fig = order_by_week (df1)
        st.plotly_chart (fig, use_container_width=True)
        

    with st.container():
        st.markdown("### Pedidos por Semana x Quantidade de Entregadores ")
        fig = order_share_by_week (df1)
        st.plotly_chart (fig, use_container_width=True)
   

with tab3:
    st.markdown("### Mapa")
    country_maps (df1)

    



































