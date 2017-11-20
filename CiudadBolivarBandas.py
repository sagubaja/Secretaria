# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json 
import random
import re 
import math
import networkx as nx
#import News
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
Estacion = "ESTACION E-19 CIUDAD BOLIVAR" 
ID = '99263 - CORREDOR ZAMORA YANIG ADRIAN'  

##leer archivo de Fiscalia y policia
#Fiscalia = pd.read_csv("CAPTRUAS - Fiscalia.csv",";", encoding = "latin-1")
Policia = pd.read_csv("CAPTURAS - Policia.csv","\t")
Policia = Policia.applymap(str)
##Quitamos las comillas de fiscalia
#Fiscalia2=Fiscalia[['NOTICIA','ID_PERSONA','TITULO','ARTICULO','FECHA_HECHO','PRIMER_APELLIDO']]
#Fiscalia2= Fiscalia2.applymap(str)
#Fiscalia2['NOTICIA'] =  Fiscalia2['NOTICIA'].str.replace("'","")
#Fiscalia2 = Fiscalia2.drop_duplicates(subset=['NOTICIA','ID_PERSONA'])
#3 Asignaremos un color a los delitos para colorear los nodos
#Lista_Titulos = list(Fiscalia2['TITULO'].drop_duplicates())
#ColorDelito = dict()
#ColorDelito = {Lista_Titulos[i]:i for i in range(len(Lista_Titulos))}
#COLOR = Fiscalia2.apply(lambda x: ColorDelito[x['TITULO']], axis=1)
#Fiscalia2.insert(len(Fiscalia2.columns),'COLOR',COLOR)
## Mapeamos las letras a valores numericos en ARTICULO
Policia2 = Policia[["JURISESTACIÓNÁREA","NUMEROUNICODENUNCIAS","NOMBRES","APELLIDOS","IDENTIFICACION"]]
Policia2=Policia2.applymap(str)
Policia2['IDENTIFICACION']=Policia2['IDENTIFICACION'].str.replace(".0","")
Policia2['Alias']=Policia2['IDENTIFICACION']+' - '+Policia2['APELLIDOS']+' '+Policia2['NOMBRES']
logico=Policia2.apply(lambda x: (x.loc['NUMEROUNICODENUNCIAS']=='nan') and (x.loc['IDENTIFICACION']=='nan'), axis = 1 )
Policia2=Policia2.loc[~logico]
logico1= Policia2.apply(lambda x: x.loc['NUMEROUNICODENUNCIAS']=='nan',axis = 1)
B = list(logico1.loc[logico1 == True].index)
BB=list(map(str,B))
B=['Sin_Noticia_' + b for b in BB]
Policia2.loc[logico1,'NUMEROUNICODENUNCIAS']=B
logico2= Policia2.apply(lambda x: x.loc['IDENTIFICACION']=='nan',axis = 1)
A = list(logico2.loc[logico2 == True].index)
AA=list(map(str,A))
A=['Sin_Identificacion_' + b for b in AA]
Policia2.loc[logico2,'IDENTIFICACION']=A
#logicoEstacion=Policia2.apply(lambda x: x.loc['JURISESTACIÓNÁREA']== Estacion, axis = 1) 
#Policia2=Policia2.loc[logicoEstacion]
# creamos grafos con la estacion solicitada 
grafoPolicia = nx.from_pandas_dataframe(Policia2,'Alias', 'NUMEROUNICODENUNCIAS', edge_attr=None, create_using = nx.DiGraph())
grafoPolicia2 = nx.from_pandas_dataframe(Policia2,'Alias', 'NUMEROUNICODENUNCIAS', edge_attr=None, create_using = None)
ClasesConexas = sorted(nx.connected_components(grafoPolicia2), key = len, reverse=True)

#Creamos el subgrafo correspondiente al ID_PERSONA o NOTICIA
for c in ClasesConexas:
    if ID in c:
        H_ID=grafoPolicia.subgraph(list(c))
                  

nx.draw(H_ID, with_labels=True, font_weight='bold')

NodesID=list(H_ID.nodes())
Color1={l:0 for l in NodesID if l in list(Policia2['Alias'])}
Color2={l:5 for l in NodesID if l in list(Policia2['NUMEROUNICODENUNCIAS'])}
Color1.update(Color2)
EdgesID=list(H_ID.edges())        

# Vamos a crear un json con los datos 
No=[{'id':n,'group':Color1[n]} for n in NodesID]
Li=[{'source': e[0], 'target': e[1], 'value': random.randrange(0,8)} for e in EdgesID]
grafoJson={'nodes':No,'links':Li}
with open('grafoJsonCiudadBolivarPrueba.json', 'w') as outfile:
    json.dump(grafoJson, outfile)
    
#Fiscalia2.to_pickle('Fiscalia2')

#Codigo para buscar noticias
Nombres=list()
for n in NodesID:
    try:
        if '-' in NodesID[0]:
            Nombres.append(n.split('- ')[1])  
    except: 
        pass      

