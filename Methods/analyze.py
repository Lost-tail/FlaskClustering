import pandas as pd
from sklearn import metrics
from sklearn.cluster import KMeans, DBSCAN, Birch
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import numpy as np
import matplotlib
matplotlib.use('Agg')

class Analyzation():
    def __init__(self,direct='data/'):
        self.X = []
        self.index=dict()
        self.pure_data = []
        self.scaler = MinMaxScaler()
        self.km = []
        self.cl1=None
        self.cl2=None
        self.dbscn=None
        self.br=None
        self.data = [pd.read_csv(direct+'20{}.csv'.format(i), sep=';',encoding='ANSI',lineterminator='\n').dropna(thresh=1).fillna(0) for i in range(10,19)]
        for i in range(len(self.data)):
            def is_float(x):
                try:
                    float(x)
                    return True
                except:
                    return False
            self.pure_data.append(self.data[i].drop('Регион',1).where(self.data[i].applymap(lambda x: is_float(x)),0))
            self.X.append(self.scaler.fit_transform(self.data[i].drop('Регион',1).where(self.data[i].applymap(lambda x: is_float(x)),0)))
        self.aver_param = self.pure_data[-1].applymap(lambda x: float(x))
        for i in self.pure_data[:-1]:
            self.aver_param+=i.applymap(lambda x: float(x))
        self.aver_param=self.aver_param/9
        self.aver_param['Регион']=self.data[-1]['Регион']
    def birch(self):
        br = Birch(n_clusters = 6)
        self.br =br.fit(self.X[-1])
        #for i in range(len(self.X)-1):
            #self.km = self.km.fit(self.X[i])
        for i in range(len(self.data)):
            self.data[i]['birch'] = self.br.predict(self.X[i])
        self.index['birch'] = [metrics.silhouette_score(self.X[i], self.br.labels_) for i in range(len(self.X))]
        #print(self.br.subcluster_labels_)
    def k_means(self):
        #km = KMeans(n_clusters = 6,random_state  = 1)
        #self.km =km.fit(self.X[-1])
        for i in range(len(self.X)):
            kmeans = KMeans(n_clusters = 6,random_state  = 1)
            self.km.append(kmeans.fit(self.X[i]))
        for i in range(len(self.data)):
            self.data[i]['k-means'] = self.km[i].predict(self.X[i])
        self.index['k-means'] = [metrics.silhouette_score(self.X[i], self.km[i].labels_) for i in range(len(self.X))]
        clusters_center1=[None]*len(self.km)
        clusters_center2=[]
        def interpretation(x):
            if x < 0.2:
                return 'низкий'
            elif x < 0.4:
                return 'ниже среднего'
            elif x < 0.6:
                return 'средний'
            elif x < 0.8:
                return 'выше среднего'
            else:
                return 'высокий'
        for i in range(len(self.km)):
            arr=[]
            for y in self.km[i].cluster_centers_:
                arr.append([interpretation(x) for x in y])
            clusters_center1[i]=arr
            clusters_center2.append(self.scaler.inverse_transform(self.km[i].cluster_centers_).round())
        self.cl1 = clusters_center1
        self.cl2 = clusters_center2
      
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
        for param in range(len(self.aver_param.columns[:-1])):
            data = []
            cl_data=[]
            for year in range(len(self.pure_data)):
                data.append(float(self.pure_data[year].at[ind,self.aver_param.columns[param]]))
                cl_data.append(self.cl2[year][int(self.data[year].at[ind,'k-means'])][param])
            fig,ax= plt.subplots(figsize=(15,6))
            plt.plot([i for i in range(2010,2019)], data, color='firebrick')
            plt.title(self.aver_param.columns[param])
            plt.scatter([i for i in range(2010,2019)],cl_data,marker='*',s=200,label='Центр кластера субъекта')
            plt.xticks(rotation=60, horizontalalignment='right',fontsize=8)
            fig.legend()
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
        plt.ylabel('Мощность кластера')
        fig.savefig('static/figures/clusters/clust_power{}.png'.format(clust_numb))
        plt.close()
    def clust_diff(self,clust_numb):
        for param in range(len(self.aver_param.columns[:-1])):
            cl_data = []
            max_ = []
            min_ = []
            for y in range(9):
                cl_data.append(self.cl2[y][clust_numb][param])
                try:
                    a_max=float(self.data[y].groupby('k-means')[self.aver_param.columns[param]].max()[clust_numb])
                except:
                    a_max = 0
                try:
                    a_min=float(data_cl[y].groupby('k-means')[self.aver_param.columns[param]].min()[clust_numb])
                except:
                    a_min=0
                max_.append(a_max)
                min_.append(a_min)
            fig,ax= plt.subplots(figsize=(15,6))
            plt.plot([i for i in range(2010,2019)], cl_data, color='firebrick')
            plt.scatter([i for i in range(2010,2019)],max_,marker='*',s=200,label='Максимальное значение')
            plt.scatter([i for i in range(2010,2019)],min_,marker='*',s=200,label='Минимальное значение')
            plt.title(self.aver_param.columns[param]) 
            fig.legend()
            fig.savefig('static/figures/clusters/cl{}{}.png'.format(clust_numb,param))
            plt.close()
    def vis_k_means(self):
        i=0
        for year in self.X:
            tsne = TSNE(random_state=13)
            data= np.vstack((year,self.km[i].cluster_centers_))
            tsne_repr = tsne.fit_transform(data)
            fig,ax= plt.subplots(figsize=(15,6))
            plt.scatter(tsne_repr[:-6,0],tsne_repr[:-6,1],c=self.data[i]['k-means'].map({0:'b',1:'g',2:'y',3:'k',4:'r',5:'m',6:'c'}))
            plt.scatter(tsne_repr[-6:,0],tsne_repr[-6:,1],c=['b','g','y','k','r','m'],marker='*',s=200)
            plt.title("Распределение кластеров в 201{} году".format(i))
            fig.savefig('static/figures/visualization/k-means201{}.png'.format(i))
            plt.close()
            i+=1
    def vis_birch(self):
        i=0
        for year in self.X:
            tsne = TSNE(random_state=13)
            data= np.vstack((year,self.br.subcluster_centers_))
            tsne_repr = tsne.fit_transform(data)
            fig,ax= plt.subplots(figsize=(15,6))
            plt.scatter(tsne_repr[:-12,0],tsne_repr[:-12,1],c=self.data[i]['birch'].map({0:'b',1:'g',2:'y',3:'k',4:'r',5:'m'}))
            plt.scatter(tsne_repr[-12:,0],tsne_repr[-12:,1],c=pd.Series(self.br.subcluster_labels_).map({0:'b',1:'g',2:'y',3:'k',4:'r',5:'m'}),marker='*',s=200)
            plt.title("Распределение кластеров в 201{} году".format(i))
            fig.savefig('static/figures/visualization/birch201{}.png'.format(i))
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



