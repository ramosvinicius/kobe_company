#Bibliotecas
import pandas as pd
import numpy as np
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


#-------------------------------
# Selecionando tipo de página
#-------------------------------

st.set_page_config(page_title= 'Home', layout="wide")

#-------------------------------
# Funções
#-------------------------------

def avg_std_time_on_traffic(df1):
    df_aux = df1.loc [:, ['City','Time_taken(min)','Road_traffic_density']].groupby (['City', 'Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst (df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                       color='std_time', color_continuous_scale = 'RdBu',
                       color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph (df1):
    df_aux = df1.loc[:,['City', 'Time_taken(min)']].groupby ('City').agg ({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar (name='Control',x=df_aux ['City'],y=df_aux ['avg_time'],                       error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout (barmode='group')
    
    return fig


def avg_std_time_delivery (df1, festival, op ):
    """ Está função calcula o tempo médio e o desvio padrão do tempo de entrega. 
    Parâmetros:
        Input: 
            - df: Dataframe com os dados necessários para o cálculo
            - op: Tipo de operação que precisa ser calculado
            'avg_time': Calcula o tempo médio
            'std_time': Calcula o desvio padrão do tempo.
        Output:
            - df: Dataframe com 2 colunas e 1 linha.
    """
    df_aux = df1.loc [:, ['Time_taken(min)','Festival']].groupby ('Festival').agg ({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time', 'std_time'] 
    df_aux = df_aux.reset_index()
    df_aux = np.round (df_aux.loc [df_aux['Festival'] == festival, 'avg_time'],2)
    
    return df_aux




def distance(df1, fig):
    cols = ['Delivery_location_latitude','Delivery_location_longitude',
            'Restaurant_latitude','Restaurant_longitude']

    df1['distance'] = df1.loc[:, cols].apply(
        lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
        ),
        axis=1
    )

    if not fig:
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    else:
        df_aux = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(
            data=[go.Pie(labels=df_aux['City'], values=df_aux['distance'], pull=[0, 0.1, 0])]
        )
        return fig




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


#-------------------------------
# Importando o data set
#-------------------------------

df = pd.read_csv('../train.csv')

# ----------- ---
# Cleaning Data
# --------------
df1 = clean_code (df)

# =====================================================================================
# BARRA LATERAL
# =====================================================================================

st.header ('Marketplace - Visão Restaurante')

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

weather_options = st.sidebar.multiselect(
    'Quais os tipos de cidade?',
    ['Metropolitian','Semi-Urban', 'Urban'],
    
    default= ['Metropolitian','Semi-Urban', 'Urban'])

st.sidebar.markdown ("""---""")

# Filtro de Datas
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc [linhas_selecionadas,:]

# Mostrar dataframe, para validações
# st.dataframe (df1)

# Filtro de Tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc [linhas_selecionadas,:]

# Filtro de Clima
linhas_selecionadas = df1['City'].isin( weather_options )
df1 = df1.loc [linhas_selecionadas,:]

# Mostrar dataframe, para validações
# st.dataframe (df1)

# =====================================================================================
# LAYOUT NO STREAMLIT
# =====================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Métricas Gerais')
        
    col1, col2, col3, col4, col5, col6 = st.columns (6)

    with col1:
        delivery_unique = len(df1.loc [:, 'Delivery_person_ID'].unique())
        col1.metric ('Entregadores Únicos', delivery_unique)

    with col2: 
        avg_distance = distance (df1, fig=False)
        col2.metric('Distancia Média', avg_distance)
    
    with col3:  
        df_aux = avg_std_time_delivery (df1, 'Yes', 'avg_time')
        col3.metric ('Tempo Médio com Festival', df_aux)

    with col4:
        df_aux = avg_std_time_delivery (df1, 'Yes', 'std_time')
        col4.metric('STD de Entrega com Festival', df_aux)
        
    with col5:
        df_aux = avg_std_time_delivery (df1, 'No', 'avg_time')
        col5.metric ('Tempo Médio sem Festival', df_aux)
        
    with col6: 
        df_aux = avg_std_time_delivery (df1, 'No', 'std_time')
        col6.metric('STD Entrega sem Festival', df_aux)        


    with st.container():
        st.markdown("""---""")

        col1, col2 = st.columns (2)

    with col1:
        
        st.markdown('### Tempo Médio de Entrega por Cidade')
        fig = avg_std_time_graph (df1)
        st.plotly_chart (fig)


    with col2:
        st.markdown('### Distribuição de Tempo')

        df_aux = (df1.loc[:, ['City','Time_taken(min)','Type_of_order']]
                     .groupby(['City','Type_of_order'])
                     .agg({'Time_taken(min)': ['mean','std']}))
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()

        st.dataframe (df_aux)


    with st.container():
        st.markdown("""---""")
        st.markdown ('### Distribuição de Tempo')

        col1, col2 = st.columns (2)
        
        with col1:
            fig = distance (df1, fig=True)
            st.plotly_chart(fig)
        
        with col2:                
            fig = avg_std_time_on_traffic (df1)
            st.plotly_chart (fig)
    

            
