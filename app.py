from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField
from Methods.analyze import Analyzation
from multiprocessing import Process        

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'

bootstrap=Bootstrap(app)
Analyze = Analyzation()
Analyze.k_means()
Analyze.dbscan()
Analyze.create_pictures()

class K_MeansForm(FlaskForm):
    submit1 = SubmitField('K_Means')
class DbscanForm(FlaskForm):
    submit2 = SubmitField('DBSCAN')
class StingForm(FlaskForm):
    submit3 = SubmitField('Sting')
class Choose_MethodForm(FlaskForm):
    submit = SubmitField('Выбрать данный метод основным')

@app.route('/',methods=['GET', 'POST'])
def start_page():
    button1 = K_MeansForm()
    button2 = DbscanForm()
    button3 = StingForm()
    if button1.submit1.data:
        return redirect(url_for('k_means_method'))
    if button2.submit2.data:
        return redirect(url_for('dbscan_method'))
    if button3.submit3.data:
        return redirect(url_for('sting_method'))
    return render_template('start_page.html',form1=button1,form2=button2,form3=button3)
    

@app.route('/sting',methods=['GET'])   
def sting_method():
    return render_template('base_overall.html', method='Sting')

@app.route('/dbscan',methods=['GET'])     
def dbscan_method():
    headers = Analyze.data[-1].columns[1:16]
    index = Analyze.index['dbscan'][-1]
    years = [ i for i in range(2010,2019)]
    subj_numb =[[x-1]+[0]*(len(years)) for x in range(len(Analyze.data[-1].groupby('dbscan')))]
    for j in range(len(years)):
        i=0
        for x in Analyze.data[j].groupby('dbscan'):
            subj_numb[i][j+1] = len(x[1])
            i+=1
    return render_template('dbscan.html', method='DBSCAN',subj_numb=subj_numb,index=index,years=years)

@app.route('/k_means',methods=['GET'])     
def k_means_method():
    headers = Analyze.data[-1].columns[1:16]
    #clusters_centers=[]
    clusters_center1=[]
    i=0
    for y in Analyze.km.cluster_centers_:
        clusters_center1.append([i]+[interpretation(x) for x in y])
        #clusters_centers.append([i]+[x for x in y])
        i+=1
    cl1 = clusters_center1
    #clusters = sorted(clusters_centers, key = lambda x: sum(x[1:])/(len(x)-1),reverse = True)
    #for i in range(len(clusters)):
        #for j in range(1,len(clusters[i])):
            #clusters[i][j] = interpretation(clusters[i][j])
    index = Analyze.index['k-means'][-1]
    years = [ i for i in range(2010,2019)]
    subj_numb =[[x]+[0]*(len(years)) for x in range(6)]

    for j in range(len(years)):
        i=0
        for x in Analyze.data[j].groupby('k-means'):
            subj_numb[i][j+1] = len(x[1])
            i+=1
    return render_template('base_overall.html', method='K_Means',headers=headers,clusters=cl1,index=index,years=years,subj_numb=subj_numb)

@app.route('/compare',methods=['GET'])  
def compare():
    index1 = Analyze.index['k-means'][-1]
    index2 = Analyze.index['dbscan'][-1]
    number1 = len(Analyze.data[-1].groupby('k-means'))
    number2 = len(Analyze.data[-1].groupby('dbscan'))
    return render_template('compare.html',index1=index1,index2=index2,number1=number1,number2=number2)

@app.route('/analyze',methods=['GET']) 
def analyze():
    regions = Analyze.data[-1]['Регион']
    return render_template('analyze.html',regions=regions)

@app.route('/average_params',methods=['GET','POST']) 
def average_params():
    params = Analyze.aver_param.columns[:-1]
    imgs1 = ["figures/aver{}.png".format(i) for i in range(15)]
    imgs2 = ["figures/aver_2{}.png".format(i) for i in range(15)]
    return render_template('average_params.html',params = params,imgs1=imgs1,imgs2=imgs2)
    
@app.route('/subject_params',methods=['GET','POST']) 
def subject_params():
    params = Analyze.data[-1]['Регион']
    active_param = request.args.get('active_param')
    if active_param:
        Analyze.subj_param(active_param)
        Analyze.clust_numb(active_param)
    img2 = 'figures/subjects/clust_numb{}.png'.format(active_param)
    imgs = ['figures/subjects/{}{}.png'.format(active_param,i) for i in range(len(Analyze.aver_param.columns[:-1]))]
    return render_template('subject_params.html',params=params,active_param=active_param,imgs=imgs,img2=img2)
    
@app.route('/cluster_params',methods=['GET','POST']) 
def cluster_params():
    return render_template('cluster_params.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

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
if __name__=='__main__':
	app.run(debug=True)
