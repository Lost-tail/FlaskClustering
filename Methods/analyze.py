import pandas as pd
from sklearn import metrics
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import numpy as np
from multiprocessing import Process
import matplotlib
matplotlib.use('Agg')

class Analyzation():
    def __init__(self,direct='data/'):
        self.X = []
        self.index=dict()
        self.pure_data = []
        scaler = MinMaxScaler()
        self.km = None
        self.dbscn=None
        self.data = [pd.read_csv(direct+'20{}.csv'.format(i), sep=';',encoding='ANSI',lineterminator='\n').dropna(thresh=1).fillna(0) for i in range(10,19)]
        for i in range(len(self.data)):
            def is_float(x):
                try:
                    float(x)
                    return True
                except:
                    return False
            self.pure_data.append(self.data[i].drop('Регион',1).where(self.data[i].applymap(lambda x: is_float(x)),0))
            self.X.append(scaler.fit_transform(self.data[i].drop('Регион',1).where(self.data[i].applymap(lambda x: is_float(x)),0)))
        self.aver_param = self.pure_data[-1].applymap(lambda x: float(x))
        for i in self.pure_data[:-1]:
            self.aver_param+=i.applymap(lambda x: float(x))
        self.aver_param=self.aver_param/9
        self.aver_param['Регион']=self.data[-1]['Регион']
    def k_means(self):
        km = KMeans(n_clusters = 6,random_state  = 1)
        self.km =km.fit(self.X[-1])
        #for i in range(len(self.X)-1):
            #self.km = self.km.fit(self.X[i])
        for i in range(len(self.data)):
            self.data[i]['k-means'] = self.km.predict(self.X[i])
        self.index['k-means'] = [metrics.silhouette_score(self.X[i], self.km.labels_) for i in range(len(self.X))]

    def dbscan(self):
        """model = NearestNeighbors(n_neighbors=5)
        for i in range(len(self.X)):
            model.fit(self.X[i])
        for i in range(len(self.X)):
            dist, _ = model.kneighbors(self.X[i],n_neighbors=5,return_distance=True)
            dist = dist[:,-1]
            dist = np.sort(dist)
            plt.plot(dist)
            plt.savefig('test{}.png'.format(i))"""
        eps = 0.7
        self.dbscn = DBSCAN(eps=eps, min_samples = 5)
        for i in range(len(self.X)):
            self.data[i]['dbscan']=self.dbscn.fit_predict(self.X[i])
        self.index['dbscan'] = [metrics.silhouette_score(self.X[i], self.dbscn.labels_) for i in range(len(self.X))]
    def create_pictures(self):
        self.aver_pict()
        self.aver_pict2()
    def aver_pict(self):
        i=0
        for x in self.aver_param.columns[:-1]:
            data = self.aver_param.sort_values(by=x,ascending=False)
            fig, ax = plt.subplots(figsize=(14,7))
            plt.vlines(x=data['Регион'], ymin=0, ymax=data[x], color='firebrick', alpha=0.7, linewidth=7)
            plt.title(x)
            plt.xticks(rotation=60, horizontalalignment='right',fontsize=8)
            ax.set_box_aspect(0.3)
            ax.set_anchor('N')
            fig.savefig('static/figures/'+'aver{}.png'.format(i))
            plt.close()
            i+=1
    def aver_pict2(self):
        i=0
        for x in self.aver_param.columns[:-1]:
            data2 = self.pure_data[-1]
            data2['Регион']=self.data[-1]['Регион']
            data2 = data2.sort_values(by=x,ascending=False)
            fig,ax= plt.subplots(figsize=(14,7))
            plt.vlines(x=data2['Регион'], ymin=0, ymax=data2[x], color='firebrick', alpha=0.7, linewidth=7)
            plt.title(x)
            plt.xticks(rotation=60, horizontalalignment='right',fontsize=8)
            ax.set_box_aspect(0.3)
            ax.set_anchor('N')
            fig.savefig('static/figures/'+'aver_2{}.png'.format(i))
            plt.close()
            i+=1
    def subj_param(self,active_param):
        ind = list(self.data[-1]['Регион']).index(active_param)
        i=0
        for param in self.aver_param.columns[:-1]:
            data = []
            for year in self.pure_data:
                data.append(float(year.at[ind,param]))
            fig,ax= plt.subplots(figsize=(15,6))
            plt.plot([i for i in range(2010,2019)], data, color='firebrick')
            plt.title(param)
            plt.xticks(rotation=60, horizontalalignment='right',fontsize=8)
            fig.savefig('static/figures/subjects/{}{}.png'.format(active_param,i))
            plt.close()
            i+=1
    def clust_numb(self,active_param):
        ind = list(self.data[-1]['Регион']).index(active_param)
        data=[]
        for year in self.data:
                data.append(float(year.at[ind,'k-means']))
        fig,ax= plt.subplots(figsize=(15,6))
        plt.plot([i for i in range(2010,2019)], data, color='firebrick')
        plt.xticks(rotation=60, horizontalalignment='right',fontsize=8)
        fig.savefig('static/figures/subjects/clust_numb{}.png'.format(active_param))
        plt.close()
    def clust_power(self,clust_numb):
        data=[]
        for year in self.data:
            data.append(year.groupby('k-means').size()[clust_numb])
        fig,ax= plt.subplots(figsize=(15,6))
        plt.plot([i for i in range(2010,2019)], data, color='firebrick')
        plt.xticks(rotation=60, horizontalalignment='right',fontsize=8)
        plt.title("Кластер №{}".format(clust_numb))
        fig.savefig('static/figures/clusters/clust_power{}.png'.format(clust_numb))
        plt.close()
    def vis_k_means(self):
        i=0
        for year in self.X:
            tsne = TSNE(random_state=13)
            tsne_repr = tsne.fit_transform(year)
            fig,ax= plt.subplots(figsize=(15,6))
            plt.scatter(tsne_repr[:,0],tsne_repr[:,1],c=self.data[i]['k-means'].map({0:'b',1:'g',2:'y',3:'k',4:'r',5:'m'}))
            plt.title("Распределение кластеров в 201{} году".format(i))
            fig.savefig('static/figures/visualization/k-means201{}.png'.format(i))
            plt.close()
            i+=1
    def vis_dbscan(self):
        i=0
        for year in self.X:
            tsne = TSNE(random_state=13)
            tsne_repr = tsne.fit_transform(year)
            fig,ax= plt.subplots(figsize=(15,6))
            plt.scatter(tsne_repr[:,0],tsne_repr[:,1],c=self.data[i]['dbscan'].map({0:'b',1:'g',2:'y',3:'k',4:'r',-1:'m'}))
            plt.title("Распределение кластеров в 201{} году".format(i))
            fig.savefig('static/figures/visualization/dbscan201{}.png'.format(i))
            plt.close()
            i+=1
            

