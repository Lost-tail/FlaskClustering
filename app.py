from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField
from Methods.analyze import Analyzation     

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'

bootstrap=Bootstrap(app)
Analyze = Analyzation()
Analyze.k_means()
Analyze.dbscan()
Analyze.birch()
Analyze.create_pictures()

class K_MeansForm(FlaskForm):
    submit1 = SubmitField('K_Means')
class DbscanForm(FlaskForm):
    submit2 = SubmitField('DBSCAN')
class StingForm(FlaskForm):
    submit3 = SubmitField('Birch')
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
        return redirect(url_for('birch_method'))
    return render_template('start_page.html',form1=button1,form2=button2,form3=button3)
    

@app.route('/birch',methods=['GET'])   
def birch_method():
    headers = Analyze.data[-1].columns[1:16]
    Analyze.vis_birch()
    imgs = ['figures/visualization/birch201{}.png'.format(i) for i in range(9)]
    index = sum(Analyze.index['birch'])/len(Analyze.index['birch'])
    years = [ i for i in range(2010,2019)]
    subj_numb =[[x]+[0]*(len(years)) for x in range(len(Analyze.data[-1].groupby('birch')))]
    for j in range(len(years)):
        i=0
        for x in Analyze.data[j].groupby('birch'):
            subj_numb[i][j+1] = len(x[1])
            i+=1
    return render_template('dbscan.html', method='Birch',subj_numb=subj_numb,index=index,years=years,imgs=imgs)

@app.route('/dbscan',methods=['GET'])     
def dbscan_method():
    headers = Analyze.data[-1].columns[1:16]
    index = sum(Analyze.index['dbscan'])/len(Analyze.index['dbscan'])
    Analyze.vis_dbscan()
    imgs = ['figures/visualization/dbscan201{}.png'.format(i) for i in range(9)]
    years = [ i for i in range(2010,2019)]
    subj_numb =[[x-1]+[0]*(len(years)) for x in range(len(Analyze.data[-1].groupby('dbscan')))]
    for j in range(len(years)):
        i=0
        for x in Analyze.data[j].groupby('dbscan'):
            subj_numb[i][j+1] = len(x[1])
            i+=1
    return render_template('dbscan.html', method='DBSCAN',subj_numb=subj_numb,index=index,years=years,imgs=imgs)

@app.route('/k_means',methods=['GET'])     
def k_means_method():
    headers = Analyze.data[-1].columns[1:16]
    Analyze.vis_k_means()
    imgs = ['figures/visualization/k-means201{}.png'.format(i) for i in range(9)]
    cl1 = Analyze.cl1
    cl2 = Analyze.cl2
    index = sum(Analyze.index['k-means'])/len(Analyze.index['k-means'])
    years = [ i for i in range(2010,2019)]
    subj_numb =[[x]+[0]*(len(years)) for x in range(6)]
    length1 = len(cl1[0])
    length2 = len(cl1[0][0])
    print(length1,length2)
    for j in range(len(years)):
        i=0
        for x in Analyze.data[j].groupby('k-means'):
            subj_numb[i][j+1] = len(x[1])
            i+=1
    return render_template('base_overall.html', method='K_Means',headers=headers,cl1=cl1,index=index,years=years,subj_numb=subj_numb,imgs=imgs,cl2=cl2,length1=length1,length2=length2)

@app.route('/compare',methods=['GET'])  
def compare():
    index1 = Analyze.index['k-means']
    index2 = Analyze.index['dbscan']
    index3 = Analyze.index['birch']
    aver_ind1 =sum(Analyze.index['k-means'])/len(Analyze.index['k-means'])
    aver_ind2 =sum(Analyze.index['dbscan'])/len(Analyze.index['dbscan'])
    aver_ind3 =sum(Analyze.index['birch'])/len(Analyze.index['birch'])
    years = [ i for i in range(2010,2019)]
    if max(aver_ind1,aver_ind2,aver_ind3)==aver_ind1:
        best = 'k-means'
    elif max(aver_ind1,aver_ind2,aver_ind3)==aver_ind2:
        best = 'dbscan'
    else:
        best = 'Birch'
    return render_template('compare.html',index1=index1,index2=index2,index3=index3,aver_ind1=aver_ind1,aver_ind2=aver_ind2,aver_ind3=aver_ind3,best=best,years=years)

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
    clust_numb = request.args.get('clust_numb')
    if clust_numb or clust_numb=="0":
        Analyze.clust_power(int(clust_numb))
        Analyze.clust_diff(int(clust_numb))
    img1 = 'figures/clusters/clust_power{}.png'.format(clust_numb)
    imgs2 = ['figures/clusters/cl{}{}.png'.format(clust_numb,param) for param in range(len(Analyze.aver_param.columns[:-1]))]
    return render_template('cluster_params.html',clusters=[i for i in range(6)],img1=img1,imgs2=imgs2)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

        
if __name__=='__main__':
	app.run(debug=True)
