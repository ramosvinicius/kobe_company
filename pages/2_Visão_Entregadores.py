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

#-------------------------------
# Selecionando tipo de página
#-------------------------------
st.set_page_config(page_title= 'Visão Entregadores', layout="wide")


#-------------------------------
# Funções
#-------------------------------

def top_delivers(df1, top_asc):
    # Agrupar e ordenar
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
              .groupby(['City', 'Delivery_person_ID'])
              .min()
              .sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())
    df_aux01 = df2.loc [df2['City'] == 'Metropolititian', :].head(10)
    df_aux02 = df2.loc [df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc [df2['City'] == 'Semi-Urban', :].head(10)   
    df3 = pd.concat ([df_aux01, df_aux02, df_aux03]).reset_index ( drop=True)
    return df3



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


# Importando o data set
try:
    df = pd.read_csv('dataset/train.csv')
except Exception as e:
    import streamlit as st
    st.error(f"Erro ao carregar CSV: {e}")
    df = None


# Limpando o dataset
df1 = clean_code (df)

# =====================================================================================
# BARRA LATERAL
# =====================================================================================

st.header ('Marketplace - Visão Entregadores')

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
    'Quais as condições climáticas?',
    ['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Sandstorms', 'conditions Sunny', 'conditions Windy'],
    
    default=['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Sandstorms', 'conditions Sunny', 'conditions Windy'])

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
linhas_selecionadas = df1['Weatherconditions'].isin( weather_options )
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

        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)

        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)

        with col3:
            melhor_condicao = df1['Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_condicao)

        with col4:
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_condicao)

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
    
        col1, col2 = st.columns(2)
    
        with col1:
            st.markdown('##### Avaliações Médias por Entregador')
    
            df_media_avaliacoes_entregador = (
                df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                   .groupby('Delivery_person_ID')
                   .mean()
                   .reset_index()
            )
    
            st.dataframe(df_media_avaliacoes_entregador)
    
        with col2:
            st.markdown('##### Avaliação Média por Trânsito')
        
            df_avg_std_traffic_ratings = (
                df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                   .groupby('Road_traffic_density')
                   .agg({'Delivery_person_Ratings': ['mean', 'std']})
            )
            df_avg_std_traffic_ratings.columns = ['delivery_mean', 'delivery_std']
        
            st.dataframe(df_avg_std_traffic_ratings)
        
            st.markdown('##### Avaliação Média por Clima')
        
            df_avg_std_weather_ratings = (
                df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                   .groupby('Weatherconditions')
                   .agg({'Delivery_person_Ratings': ['mean', 'std']})
            )
            df_avg_std_weather_ratings.columns = ['delivery_mean', 'delivery_std']
        
            st.dataframe(df_avg_std_weather_ratings)



    with st.container():
        st.markdown("""---""")
        st.title('Velocidade das Entregas')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(' ##### Top Entregadores mais Rápidos')
            df3 = top_delivers (df1, top_asc=True)
            st.dataframe (df3)


        with col2:
            st.markdown('##### Top Entregadores mais Lentos')
            df3 = top_delivers (df1, top_asc=False)
            st.dataframe (df3)

            
