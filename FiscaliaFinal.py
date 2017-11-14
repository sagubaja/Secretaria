# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json 
import random
import re 
import math
import networkx as nx 
#Variable de entrada: ID_PERSONA o NOTICIA

ID = input('Escriba el numero de ID_PERSONA o NOTICIA    \n') 
#Funcion que convierte articulo en numero
def ArticuloNum(frase):
    try:
        if np.isnan(frase):
            return '000'
    except: 
        x = re.findall(r"\d+",frase )
        l = [s for s in x if len(s) == 3]
        if not l:
            l.append('093')
        return l[0]
# Creamos una funcion que captura los numeros del area 

       
# leer archivo de Fiscalia
Fiscalia = pd.read_csv("CAPTRUAS - Fiscalia.csv",";", encoding = "latin-1")

# Quitamos las comillas de fiscalia
Fiscalia2=Fiscalia[['NOTICIA','ID_PERSONA','TITULO','ARTICULO','FECHA_HECHO','PRIMER_APELLIDO']]
Fiscalia2= Fiscalia2.applymap(str)
Fiscalia2['NOTICIA'] =  Fiscalia2['NOTICIA'].str.replace("'","")
Fiscalia2 = Fiscalia2.drop_duplicates(subset=['NOTICIA','ID_PERSONA'])

# Asignaremos un color a los delitos para colorear los nodos
Lista_Titulos = list(Fiscalia2['TITULO'].drop_duplicates())
ColorDelito = dict()
ColorDelito = {Lista_Titulos[i]:i for i in range(len(Lista_Titulos))}
COLOR = Fiscalia2.apply(lambda x: ColorDelito[x['TITULO']], axis=1)
Fiscalia2.insert(len(Fiscalia2.columns),'COLOR',COLOR)

# Mapeamos las letras a valores numericos en ARTICULO
Fiscalia2['ARTICULO'] = Fiscalia2.apply(lambda x: ArticuloNum(x['ARTICULO']), axis = 1)

# vamos a crear nuestro grafo usando Networkx 

grafoFiscalia = nx.from_pandas_dataframe(Fiscalia2,'ID_PERSONA', 'NOTICIA', edge_attr=None, create_using = nx.DiGraph())
grafoFiscalia2 = nx.from_pandas_dataframe(Fiscalia2,'ID_PERSONA', 'NOTICIA', edge_attr=None, create_using = None)
ClasesConexas = sorted(nx.connected_components(grafoFiscalia2), key = len, reverse=True)

#Creamos el subgrafo correspondiente al ID_PERSONA o NOTICIA
for c in ClasesConexas:
    if ID in c:
        H_ID=grafoFiscalia.subgraph(list(c))
             
options = {
    'node_color': 'blue',
    'node_size': 100,
    'width': 3,
}        

nx.draw(H_ID, with_labels=True, font_weight='bold', **options)

NodesID=list(H_ID.nodes())
EdgesID=list(H_ID.edges())        

# Vamos a crear un json con los datos 
No=[{'id':n,'group':25} for n in NodesID]
Li=[{'source': e[0], 'target': e[1], 'value': random.randrange(0,8)} for e in EdgesID]
grafoJson={'nodes':No,'links':Li}
with open('grafoJson.json', 'w') as outfile:
    json.dump(grafoJson, outfile)
    
Fiscalia2.to_pickle('Fiscalia2')

#Fiscalia3=pd.read_pickle('Fiscalia2')

#Mostrar los peores casos Quantil 10 superior
#Mayoresa2 = [ X for X in ClasesConexas if len(X) > 2] 








