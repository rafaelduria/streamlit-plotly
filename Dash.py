import warnings
import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import pyodbc
import sqlalchemy
from sqlalchemy import create_engine

# pip install plotly-express
servidor_dns = 'cismssql03.ciser.com.br'
servidor_database = 'inteligcom'
url = f'mssql+pyodbc://@{servidor_dns}/{servidor_database}?trusted_connection=yes&driver=SQL+Server'
engine = sqlalchemy.create_engine (url)

#def para gerar grafico de barras
def Gerar_grafico_de_barra_px_bar(dados,color_continuous_scale):
    grafico = px.bar(
                    dados,        
                    x=dados['Data_Criação'],         
                    y=dados['Quantidade'],
                    #ativando rotulo        
                    text_auto=True,
                    color= dados['Quantidade'],
                    color_continuous_scale=color_continuous_scale
                    )
    grafico = grafico.update_layout(yaxis_title=None, 
                                    xaxis_title=None,
                                    #quando passa mouse em cima do grafico 
                                    hoverlabel_font_size=16,
                                    #font rotulo de dados 
                                    font=dict(
                                    size=22)
                                    )
    grafico = grafico.update_yaxes(showticklabels=False)
    #respeitar tamanho
    st.plotly_chart(grafico, use_container_width=True)
    return grafico

# .\venv\Scripts/activate
# streamlit run Dash.py
# streamlit run Dashboard.py

data_day =  datetime.date.today()
day = data_day.day
month = data_day.month
year = data_day.year

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
#deixar página tamanho grande
st.set_page_config(layout='wide')
#st.header('Itens Cadastros')
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
##Visualização Streamlit
#Criando Abas para página principal
pagina1, pagina2 = st.tabs(['Gráficos', 'Tabelas'])
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
#base de dados SQL para gerar graficos
base = pd.read_sql("""
                        SELECT  
                        MARA.ERSDA AS Data_Criação,
                        MARA.MTART AS Tipo_Material,
                        COUNT( MARA.ERSDA ) AS Quantidade                               
                        FROM MARA
                        GROUP BY MARA.ERSDA,MARA.MTART
                        ORDER BY Data_Criação                    
                    """,engine)

#deixando dia como primeira data
base["Data_Criação"] = pd.to_datetime(base["Data_Criação"], dayfirst=True)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------      
#Barra lateral esquerda
#titulo
st.sidebar.title('Filtro') 
#lista teipo de materiais
Lista_tipo_de_materiais = list(base['Tipo_Material'].unique())
#ordenando lista tipo de materiais
Lista_tipo_de_materiais = sorted(Lista_tipo_de_materiais)
#botão radio, na lateral estquerda "sidebar"
tipo_de_materiais_escolhido = st.sidebar.radio(label = 'Tipo Material', options = Lista_tipo_de_materiais, index=3)
#filtrando base de dados conforme filtro tipo de material - tipo_de_materiais_escolhido
base = base.loc[(base['Tipo_Material'] == tipo_de_materiais_escolhido)]
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
#filtro primeiro grafico direita
Filtro_Mes = f'{year}-{month}-01'
#filtro pelo (Mês atual)
dados_dias = base.loc[(base['Data_Criação'] > Filtro_Mes)]
#ajustando formato para dia/mês
dados_dias['Data_Criação'] = dados_dias['Data_Criação'].dt.strftime('%d/%m')
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
#Segundo grafico
#filtro pelo (Ano atual)
dados_meses = base.loc[(base['Data_Criação'] > f'{year}-01-01') & (base['Data_Criação'] < f'{year}-12-31') ]
#agrupando dados por meses e ajustando formato mostrando nome do mês 
dados_meses = dados_meses.groupby(dados_meses['Data_Criação'].dt.strftime('%B'), sort=False)['Quantidade'].sum().reset_index()
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# dados pagina1 #grafico abaixo
#agrupando dados por anos e ajustando formato mostrando numero ano exemplo (1999,2000,2001)
dados_anos = base.groupby(base['Data_Criação'].dt.strftime('%Y'), sort=False)['Quantidade'].sum().reset_index()
#-----------------------------------------------------------------------------------------------------------------------------------------------------------

#Base de dados para gerar tabela de dados -dataframe lado esquerdo
dados_dataframe = pd.read_sql("""
                                    SELECT
                                    SUBSTRING(MARA.MATNR, PATINDEX('%[^0]%', MARA.MATNR), LEN(MARA.MATNR)) AS Material,
                                    MARA.MTART AS Tipo_Material,
                                    MARA.ERSDA AS Data_Criação,
                                    MARA.ERNAM AS Criado_Por                    
                                    FROM MARA
                                    WHERE MARA.ERSDA BETWEEN REPLACE(CONVERT(varchar,FORMAT(getdate(), 'yyyy-MM-01')),'-','') AND REPLACE(CONVERT(varchar,FORMAT(getdate(), 'yyyy-MM-31')),'-','')
                                    ORDER BY Data_Criação DESC
                                """,engine )
#deixando dia como primeira data                              
dados_dataframe["Data_Criação"] = pd.to_datetime(dados_dataframe["Data_Criação"], dayfirst=True)
#ajustando dia mes ano
dados_dataframe['Data_Criação'] = dados_dataframe['Data_Criação'].dt.strftime('%d/%m/%Y')
#filtrando base de dados conforme filtro tipo de material - tipo_de_materiais_escolhido
dados_dataframe = dados_dataframe.loc[(dados_dataframe['Tipo_Material'] == tipo_de_materiais_escolhido)]
#filtrando apenas colunas de Material e Data_Criação não trazendo Tipo_Material
dados_dataframe = dados_dataframe[['Material','Data_Criação','Criado_Por']]


#criando paginas
with pagina1:
    #Separando abas em colunas, na página
    pagina1_coluna1, pagina1_coluna2 = st.columns(2)

    #primeiro grafico lado direto
    with pagina1_coluna2:
        #Titulo
        st.subheader(f'Mês Atual')
        #condição if não dar erro não houver cadastro neste periodo
        if len(dados_dias) >0 :
            #gerando grafico atraves da def
            Gerar_grafico_de_barra_px_bar(dados=dados_dias,color_continuous_scale=px.colors.sequential.BuPu )
    
    with pagina1_coluna1:
        #Titulo
        st.subheader(f'Itens')
        #condição if não dar erro não houver cadastro neste periodo
        if len(dados_meses) >0:
            st.dataframe(dados_dataframe,hide_index=True,use_container_width=False)


    #segundo grafico
    #Titulo
    st.subheader(f'Ano Atual')
    #condição if não dar erro não houver cadastro neste periodo     
    if len(dados_meses) >0:
        Gerar_grafico_de_barra_px_bar(dados=dados_meses,color_continuous_scale=px.colors.sequential.GnBu)



    #terceiro grafico
    #Titulo
    st.subheader(f'Todos Anos')
    #multi select para ultimo grafico trazendo lista de todos anos, iniciando apenas com ulitmos cinco anos [-5]:
    options = st.multiselect(label='', options = list(dados_anos.Data_Criação), default = list(dados_anos.Data_Criação)[-5:])
    if options:
        #filtro, filtrando dados_anos conforme options do multi select
        dados_anos = dados_anos[dados_anos['Data_Criação'].isin(options)]
        Gerar_grafico_de_barra_px_bar(dados=dados_anos,color_continuous_scale=px.colors.sequential.Greens)

#ainda não está sendo utilizada
with pagina2:
    print('f')


