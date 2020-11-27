from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField
        
basedir = 'd:/Documents/Programming/Flasklearning/Database/'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'

bootstrap=Bootstrap(app)

class ChooseForm(FlaskForm):
    submit1 = SubmitField('Sting')
    submit2 = SubmitField('DBSCAN')
    submit3 = SubmitField('K_Means')
class Choose_MethodForm(FlaskForm):
    submit = SubmitField('Выбрать данный метод основным')

@app.route('/',methods=['GET', 'POST'])
def start_page():
    button = ChooseForm()
    if button.validate_on_submit():
        if button.submit1.data:
            return redirect(url_for('sting_method'))
        if button.submit2.data:
            return redirect(url_for('dbscan_method'))
        if button.submit3.data:
            return redirect(url_for('k_means_method'))
    return render_template('start_page.html',form=button)

@app.route('/sting',methods=['GET', 'POST'])   
def sting_method():
    button = Choose_MethodForm()
    if button.validate_on_submit():
        return redirect(url_for('sting_method'))
    return render_template('base_overall.html', method='Sting',form = button)

@app.route('/dbscan',methods=['GET', 'POST'])     
def dbscan_method():
    button = Choose_MethodForm()
    if button.validate_on_submit():
        return redirect(url_for('dbscan_method'))
    return render_template('base_overall.html', method='DBSCAN',form = button)

@app.route('/k_means',methods=['GET', 'POST'])     
def k_means_method():
    button = Choose_MethodForm()
    if button.validate_on_submit():
        return redirect(url_for('sting_method'))
    return render_template('base_overall.html', method='K_Means',form = button)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

      
if __name__=='__main__':
	app.run()