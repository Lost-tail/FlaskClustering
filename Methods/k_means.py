import pandas as pd
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import matplotlib.pyplot as plt

class Analyzation():
    def __init__(self,direct='data/'):
        self.X = []
        scaler = MinMaxScaler()
        self.data = [pd.read_csv(direct+'20{}.csv'.format(i), sep=';',encoding='ANSI',lineterminator='\n').dropna(thresh=4).fillna(0) for i in range(10,19)]
        for i in range(len(self.data)):
            #self.data[i] = self.data[i].where(self.data[i].applymap(lambda x: str(x).isdigit()),0)
            self.X.append(scaler.fit_transform(self.data[i].drop('Регион',1).where(self.data[i].applymap(lambda x: str(x).isdigit()),0)))
            #for x in self.data[i].columns:
                #self.data[i][x] = self.data[i][x].str.extract('(\w+)',expand = False)
    def k_means(self):
        #scaler = MinMaxScaler()
        #X = scaler.fit_transform(self.data[-1].drop('Регион',1))
        km = KMeans(n_clusters = 6,random_state  = 1)
        algo = km.fit(self.X[-1])
        for i in range(len(self.data)):
            self.data[i]['k-means'] = algo.predict(self.X[i])

Test = Analyzation()
Test.k_means()
print(Test.data[-1])

data = pd.read_csv('data/2018.csv', sep=';',encoding='ANSI',lineterminator='\n').dropna(thresh=3).fillna(0)
scaler = MinMaxScaler()
X = scaler.fit_transform(data.drop('Регион',1))
km = KMeans(n_clusters = 6,random_state  = 1)
algo = km.fit(X)
data['cluster'] = algo.labels_
print(data)
index = metrics.silhouette_score(X, algo.labels_)
#plt.xticks(rotation=90)
#plt.scatter(data['Регион'],X.mean(axis=1), c = algo.labels_)
#plt.savefig('test.png')
