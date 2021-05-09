from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from sqlalchemy import inspect
import pandas as pd
from sqlalchemy import create_engine

import sys
if sys.version_info[0] >= 3:
    unicode = str

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
db = SQLAlchemy(app)

ROWS_PER_PAGE = 10
class Todo(db.Model):
    __tablename__ = "client_history"

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text(200), nullable=False)
    email = db.Column(db.Text(200), nullable=False)
    role = db.Column(db.Text(200), nullable=False)

    __mapper_args__ = {
        'confirm_deleted_rows': False
    }

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Todo.query.get_or_404(id)
    print(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect('/test')
    except:
        return 'There was a problem deleting that task'

@app.route('/search', methods=['GET','POST'])
def search():
    print(request.args.get('search'))
    search_user = Todo.query.filter_by(name=request.args.get('search')).all()
    print('1st',len(search_user))
    if search_user=='None' or len(search_user)==0:
        search_user = Todo.query.filter_by(email=request.args.get('search')).all()
        print('2st',len(search_user))
        if search_user=='None' or len(search_user)==0:
            search_user = Todo.query.filter_by(role=request.args.get('search')).all()
            print('3st',len(search_user))
            if search_user=='None' or len(search_user)==0:
                print('No Data Found')
                redirect('/colors')
    print(search_user)
    # print(search_user[0])
    out=[]
    for dict1 in search_user:
        end_result=dict1.__dict__
        end_result = {k: unicode(v).encode("utf-8") for k,v in end_result.items()}
        print(end_result)
        out.append(end_result)
    print(type(end_result))
    print(out)
    # cursor = g.con.cursor()
    # cursor.execute('SELECT * FROM client_history WHERE name OR email or role = %s', (request.form["search"],))
    # result = cursor.fetchall()
    # cursor.close()
    return render_template('search.html', result = out)


@app.route('/colors',methods=['GET', 'POST'])
def colors():
    url = ' https://geektrust.s3-ap-southeast-1.amazonaws.com/adminui-problem/members.json'
    r = requests.get(url)
    txt=r.json()
    dfItem = pd.DataFrame.from_records(txt)
    print(dfItem.head())
    dfItem.to_sql(name='client_history', con=db.engine, index=False,if_exists='replace')
    print(dfItem.head())
    
    page = request.args.get('page', 1, type=int)
    colors = Todo.query.paginate(page=page, per_page=ROWS_PER_PAGE)

    return render_template('index.html', colors=colors)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    print(task)
    print(type(task))
    if request.method == 'POST':
        task.name = request.form['name']
        task.email = request.form['email']
        task.role = request.form['role']
        print(task.name,task.email,task.role)
        # try:
        db.session.commit()
        print('updated')
        return redirect('/test')
        # except:
        #     return 'There was an issue updating your task'

    else:
        return render_template('update.html', data=task)




@app.route('/test',methods=['GET', 'POST'])
def create_app():
    if request.method=='POST':
        url = ' https://geektrust.s3-ap-southeast-1.amazonaws.com/adminui-problem/members.json'
        r = requests.get(url)
        txt=r.json()
        dfItem = pd.DataFrame.from_records(txt)
        print(dfItem.head())
        # engine = create_engine('sqlite:///admincopy.db', echo=True)
        # sqlite_connection = engine.connect()
        # sqlite_table = "admindetails"
        # dfItem.to_sql(sqlite_table, sqlite_connection, if_exists='fail')

        dfItem.to_sql(name='client_history', con=db.engine, index=False,if_exists='replace')
        return redirect('/test')


    else:
        # tasks = Todo.query.all()
        page = request.args.get('page', 1, type=int)
        colors = Todo.query.paginate(page=page, per_page=ROWS_PER_PAGE)

        return render_template('index.html',colors=colors)

if __name__ == "__main__":
    app.run(debug=True)