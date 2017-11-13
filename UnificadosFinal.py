# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
from igraph import *
import cairo
import json 
import random
import re 
import math
 

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
def AreaNum(str):
    if str != '25':
        try:
            if np.isnan(str):
                return '30'
        except: 
           x = re.findall(r"\d+",str )
           if not x:
               x.append('30')
           return x[0]
    return str       
# leer los dos archivos de Fiscalia y Policia

Fiscalia = pd.read_csv("CAPTRUAS - Fiscalia.csv",";", encoding = "latin-1")
Policia = pd.read_csv("CAPTURAS - Policia.csv", "\t")

#Vamos a eliminar los duplicados 

Policia = Policia.drop_duplicates(subset=['NUMEROUNICODENUNCIAS','IDENTIFICACION','FECHA_HECHO'])

#Vamos a cambiar el nombre de la columna de las estaciones por AREA

Policia = Policia.rename(columns = {Policia.columns.values[2] : 'AREA',Policia.columns.values[9] : 'NOTICIA',
                                    Policia.columns.values[6] : 'ARTICULO',Policia.columns.values[14] : 'DOCUMENTO', 
                                    Policia.columns.values[0] : 'FECHA_HECHO'})




# Quitamos las comillas de fiscalia

Fiscalia['NOTICIA'] =  Fiscalia['NOTICIA'].str.replace("'","")

# Vamos a asignarle el ID_PERSONA las filas que no tienen documento

Fiscalia.loc[Fiscalia['DOCUMENTO'].isnull(),'DOCUMENTO']= Fiscalia.loc[Fiscalia['DOCUMENTO'].isnull(),'ID_PERSONA']

Fiscalia2 = Fiscalia.drop_duplicates(subset=['NOTICIA','DOCUMENTO','FECHA_HECHO'])

# Asignaremos un color a los delitos para colorear los nodos

Lista_Titulos = list(Fiscalia2['TITULO'].drop_duplicates())
ColorDelito = dict()
ColorDelito = {Lista_Titulos[i]:i for i in range(len(Lista_Titulos))}
COLOR = Fiscalia2.apply(lambda x: ColorDelito[x['TITULO']], axis=1)
Fiscalia2.insert(len(Fiscalia.columns),'COLOR',COLOR)


# Crear Policia Reducida y Fiscalia Reducida para manipularlas mas facil

FiscaliaReducida = Fiscalia2[['NOTICIA','DOCUMENTO','ARTICULO','FECHA_HECHO','COLOR']]
PoliciaReducida = Policia[['NOTICIA','DOCUMENTO','ARTICULO','FECHA_HECHO','AREA']]

FiscaliaReducida.insert(len(FiscaliaReducida.columns)-1,'AREA', 25)
PoliciaReducida.insert(len(PoliciaReducida.columns),'COLOR', 69)


# Creamos un dataframe unificado de la policia y la fiscalia
Unificado = FiscaliaReducida.append(PoliciaReducida, ignore_index = True)
Unificado = Unificado.drop_duplicates(subset=['NOTICIA','DOCUMENTO','FECHA_HECHO'])
#LLenamos los huecos donde no existen noticias
vaciosNoticia = np.where(pd.isnull(Unificado['NOTICIA']))
vaciosNoticia = vaciosNoticia[0]
Unificado.iloc[vaciosNoticia,0]="0000000000000000000"
#llenamos el campo donde no hay documentos registrados 
vaciosDocumento = np.where(pd.isnull(Unificado['DOCUMENTO']))
vaciosDocumento = vaciosDocumento[0]
Unificado.iloc[vaciosDocumento,1]="0"
#Eliminar los campos que aparecen vacio
vaciosArea = np.where(pd.isnull(Unificado['AREA']))
vaciosArea = vaciosArea[0]
Unificado.iloc[vaciosArea,4]="30"
# Mapeamos las letras a valores numericos
Unificado['AREA'] = Unificado.apply(lambda x: AreaNum(x['AREA']), axis = 1)
Unificado['ARTICULO'] = Unificado.apply(lambda x: ArticuloNum(x['ARTICULO']), axis = 1)
# Vamos a crear todos para poder hacer los links y los graphs

Nodos1 = Unificado[['NOTICIA','AREA']]
Nodos2 = Unificado[['DOCUMENTO','AREA']]
Nodos2 = Nodos2.rename(columns = {Nodos2.columns.values[0] : 'NODOS'})
Nodos1 = Nodos1.rename(columns = {Nodos1.columns.values[0] : 'NODOS'})

Nodos = Nodos1.append(Nodos2)

Nodos['NODOS'] = Nodos['NODOS'].replace(".","")
Nodos['AREA'] = Nodos['AREA'].replace(".","")
Nodos = Nodos.drop_duplicates()
# Vamos a crear los links 

Links = Unificado[['DOCUMENTO','NOTICIA','COLOR']]
Links['DOCUMENTO'] = Links['DOCUMENTO'].replace(".","")
Links['NOTICIA'] = Links['NOTICIA'].replace(".","")

Li=[tuple(x) for x in Links[['DOCUMENTO','NOTICIA']].to_records(index=False)]
No=list(Nodos['NODOS'])
gLinks=Graph.TupleList(Li[0:1000], No[0:1000])
gLinks.to_undirected()

clusters = gLinks.community_multilevel( weights=None, return_levels=False)
member = clusters.membership
new_cmap = ['#'+''.join([random.choice('0123456789abcdef') for x in range(6)]) for z in range(len(clusters))]
vcolors = {v: new_cmap[i] for i, c in enumerate(clusters) for v in c}
gLinks.vs["color"] = [vcolors[v] for v in gLinks.vs.indices]
ecolors = {e.index: new_cmap[member[e.tuple[0]]] if member[e.tuple[0]]==member[e.tuple[1]] else "#e0e0e0" for e in gLinks.es}
eweights = {e.index: (3*g.vcount()) if member[e.tuple[0]]==member[e.tuple[1]] else 0.1 for e in gLinks.es}
gLinks.es["weight"] = [eweights[e.index] for e in gLinks.es]
gLinks.es["color"] = [ecolors[e] for e in gLinks.es.indices]

visual_style=dict()
visual_style["layout"] = gLinks.layout_fruchterman_reingold(weights=gLinks.es["weight"], maxiter=500, area=2 ** 3, repulserad=2 ** 3)
#visual_style["layout"] = gLinks.layout_fruchterman_reingold(weights=gLinks.es["weight"], maxiter=500)
igraph.plot(gLinks, **visual_style)





# Vamos a tomar la parte entera de los numeros por que velez no pudo



#Vamos a crear los grafos

#Nodos.to_csv('NODOS', sep='\t')
#Links.to_csv('LINKS', sep='\t')
#Unificado.to_csv('UNIFICADOS', sep='\t')


    

