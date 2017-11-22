import os
import sys
from optparse import OptionParser
import ebaysdk
import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection as Finding
import pandas as pd
import matplotlib.pyplot as plt

#CODE PAR LOIC BONTEMPS 
####################################


# Initialisation d'indicateurs et de Series pour le stockage des parametres
index = 0
moyenne = 0
prix = pd.Series()
start_time = pd.Series()
title = pd.Series()
graph = []


#Initialisation de la DataFrame
df = pd.DataFrame()
#Initialisation du decoupage en temps de notre calcul de moyenne
rng = pd.to_datetime(pd.date_range('8/9/2016', periods=30, freq='3D'))

#Definition de l'ecosysteme de recherche -- On effectue une recherche en FRANCE, avec donc un prix en EUROS
api = Finding(domain='svcs.ebay.com', appid="loicBont-Loicapp-PRD-1bff3fe44-471007be", config_file=None, siteid='EBAY-FR')


#Boucle adaptee a notre recherche ==> ici 4 pages de 100 items
for m in range(1,5):

	#Requete avec filtre par keywords, et des conditions sur les pages en entrees (un maximum de pages SVP!!)
	response = api.execute('findItemsByKeywords', {'keywords': [u'Iphone' + u'6S' + u'64gb'], 'paginationInput': [ {'entriesPerPage': '100'}, {'pageNumber': '%d' % m} ] })

	for i in response.reply.searchResult.item:

		#Filtre a Prix
		if (float(i.sellingStatus.currentPrice.value) > 120) & (float(i.sellingStatus.currentPrice.value) < 950):
			
			###Possibilite d'afficher le prix et titre des elements filtres si necessaire
			#print("Matched: %s" % i.title)
			#print i.sellingStatus.currentPrice.value

			#Stockage des attributs necessaires dans des series pandas // Nous considererons ici que sellingStatus.sellingState = 'Active' correspond au critere vendu -- sinon manque d'items dans la recherche
			if i.sellingStatus.sellingState == 'Active':
				title = title.append(pd.Series([i.title]))
				prix = prix.append(pd.Series([float(i.sellingStatus.currentPrice.value)]))
				start_time = start_time.append(pd.Series([i.listingInfo.startTime]))


#Initialisation d'un start_time : "il y a 3mois"
start_time = pd.to_datetime(start_time)

#Concatenation des Series en une Unique DataFrame
d = {'prix': prix, 'start time': start_time}
df = pd.DataFrame(d)

#Tri des items par ordre de prix croissant puis representation graphique -- il est aussi possible de trier en fonction d'autres parametre comme le temps
df = df.sort(columns='prix', axis=0, ascending=True)
plt.plot(df["prix"])
plt.show()

#Segmentation du temps et calcul de moyenne
prec = pd.to_datetime('8/6/2016')
for date in rng:
	sortdf = df[(df['start time'] <= date) & (df['start time'] >= prec)].sort_index(axis=0)
	prec = date

	#Calcul de la moyenne de prix sur un intervalle de temps si il existe bien des items vendus sur cette periode
	if sortdf.size > 0:
		moyenne = sortdf['prix'].mean()
	graph[index:(index+1)] = [moyenne]

	index += 1


#Representaion graphique et stockage dans fichier .csv des valeurs de sortie
plt.plot(rng, graph)
plt.show()

df.to_csv('ebay.csv',index=False,header=True)
