# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np
import json 
import random
import re 
import math
import networkx as nx
#import News
#from News import News
#F1uncion que convierte articulo en numero
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
Estacion = "ESTACION E-03 SANTA FE" 
print("ID de alguien para la Estación " + Estacion + ' ?y/n')
respuesta =input()
if respuesta == 'y':
    print("Introduzca el ID")
    ID = input()
print("Procesando...")
TamaNodos=50
#ID = '99263 - CORREDOR ZAMORA YANIG ADRIAN'  
def AsignarModa(df,col,col1,identificacion):
    A = list(df[col].loc[df[col1]==identificacion])
    try:
        a = statistics.mode(A)
    except:
        a = A[0]
    df[col].loc[df[col1]== identificacion]=a
##leer archivo de Fiscalia y policia
#Fiscalia = pd.read_csv("CAPTRUAS - Fiscalia.csv",";", encoding = "latin-1")
Policia = pd.read_csv("Data/CAPTURAS - Policia.csv","\t")
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
Policia2['IDENTIFICACION']=Policia2['IDENTIFICACION'].str.replace(".0","")
#Policia2['Alias']=Policia2['IDENTIFICACION']+' - '+Policia2['NOMBRES']+' '+Policia2['APELLIDOS']
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
listaID = Policia2["IDENTIFICACION"]


#logicoEstacion=Policia2.apply(lambda x: x.loc['JURISESTACIÓNÁREA']== Estacion, axis = 1) 
#Policia2=Policia2.loc[logicoEstacion]
# creamos grafos con la estacion solicitada 
grafoPolicia = nx.from_pandas_dataframe(Policia2,'Alias', 'NUMEROUNICODENUNCIAS', edge_attr=None, create_using = nx.DiGraph())
grafoPolicia2 = nx.from_pandas_dataframe(Policia2,'Alias', 'NUMEROUNICODENUNCIAS', edge_attr=None, create_using = None)
ClasesConexas = sorted(nx.connected_components(grafoPolicia2), key = len, reverse=True)

#Creamos el subgrafo correspondiente al ID_PERSONA o NOTICIA
i=0
t=len(ClasesConexas[i])
if respuesta=='y':
    for c in ClasesConexas:
        if ID in c:
            H_ID=grafoPolicia.subgraph(list(c))
else:
    if len(ClasesConexas[0])<TamaNodos:
        c=ClasesConexas[0]
    else:
        while t>TamaNodos:
            c=ClasesConexas[i]
            t=len(c)
            i+=1
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
with open(Estacion + str(TamaNodos) + '.json', 'w') as outfile:
    json.dump(grafoJson, outfile)
    
#Fiscalia2.to_pickle('Fiscalia2')

#Codigo para buscar noticias
MonthtoNum={'jan':'01','feb':'02','mar':'03','apr':'04','may':'05','jun':'06','jul':'07','aug':'08','sep':'09','oct':'10','nov':'11','dec':'12'}
NombreNoticiaFecha=[(li['source'].split('- ')[1],li['target']) for li in Li]
Fechas=list()
for i in range(len(NombreNoticiaFecha)):
    Fech=Policia.loc[Policia['NUMEROUNICODENUNCIAS']==NombreNoticiaFecha[i][1]]['FECHA_HECHO'].iloc[0]
    Rango=Fech[5:9]+MonthtoNum[Fech[2:5]]+Fech[0:2]
    Fechas.append(Rango)
NombreNoticiaFecha=[(li['source'].split('- ')[1],li['target'],Rango) for li,Rango in zip(Li,Fechas)]

BusquedaNombres = [NombreNoticiaFecha[0]]
for tup in NombreNoticiaFecha[1:]:
    if tup not in [t[0] for t in BusquedaNombres]:
        BusquedaNombres.append(tup)

DF=Policia.loc[Policia['NUMEROUNICODENUNCIAS']==NombreNoticiaFecha[0][1]]
#
#Textos=[]
#print("Desea Buscar las noticias en Google de los " + str(len(Nombres)) + "mimbros de la Banda" + " ?y/n")
#respuesta2 =input()
#if respuesta2=='y':
#    j=0
#    for q in Busquedas:
#        Textos.append(Nombres[j])
#        j+=1
#        try:
#            Resultados=News(q)
#        except:
#            pass
#        for r in Resultados:
#            try:
#                Textos.append(r['title'])
#            except:
#                pass
#            try:
#                Textos.append(r['snippet'])
#            except:
#                pass
#        a=0
