from MeteoData import  MeteoApi 
from flask import session,Flask,render_template,request,send_file,redirect,url_for
from bson.json_util import dumps
import os
import re
from apscheduler.schedulers.background import BackgroundScheduler


m=MeteoApi()
m.check_and_update()

#! auto-Update 
sched = BackgroundScheduler(daemon=True)
sched.add_job(m.check_and_update,'interval',hours=24)
sched.start()


appweb= Flask(__name__)
appweb.secret_key = "super secret key"


#? Index Page 

@appweb.route("/")
def homepage():
    return render_template('index.html')


#? Table Page 


@appweb.route("/table",methods=['GET','POST'])
def specData():
    if request.method=="POST":
        nom=request.form.get("Sname")
        date=request.form.get("date")
        #!Session Start
        session['nom']=nom
        session['date']=date
        rand=m.find_in_db2(nom=nom,date=date)
        if rand=="Error":
            return redirect(url_for('homepage'))
        else:
            return render_template('table.html',random=rand)
    else:
        myname=session.get('nom')
        mydate=session.get('date')
        rand=m.find_in_db2(nom=myname,date=mydate)
        return render_template('table.html',random=rand)


#? Graphs Page 
@appweb.route("/graphs" ,methods=['GET'])
def graphs():
    myname=session.get('nom')
    mydate=session.get('date')
    testname=myname.upper()
    m.graphs(myname,mydate)
    path='static/data/graphs/'
    filename=myname+' '+mydate
    test=os.listdir(path)
    bigList=[]
    for i in test:
        x=re.search(filename,i)
        if x:
            bigList.append(path+i)
    return render_template('graphs.html',imgList=bigList,nom=testname,date=mydate)



#? download  method 

@appweb.route("/download" ,methods=['GET'])
def download():
    myname=session.get('nom')
    mydate=session.get('date')
    downloadName=myname+' '+mydate
    rand=m.find_in_db2(nom=myname,date=mydate)
    proc1=list(rand)
    json_data = dumps(proc1, indent = 2) 
    path='static/data/download/'+downloadName+'.json'
    check=os.path.exists(path)
    if check :
        return send_file(path,as_attachment=True)
    else:
        with open(path,'w') as f:
                f.write(json_data)
        return send_file(path,as_attachment=True)


if __name__=="__main__":
    
    appweb.run(debug=1)
    
