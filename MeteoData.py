import requests
import json
import datetime
import matplotlib.pyplot as plt
from pymongo import MongoClient
import numpy as np
from wordcloud import WordCloud
import os
import re

class MeteoApi:

    def __init__(self):
        self.api = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=donnees-synop-essentielles-omm&q=&facet=date&facet=nom&facet=temps_present&facet=libgeo&facet=nom_epci&facet=nom_dept&facet=nom_reg"
        self.param = {}

    def createFolders(self): 
        try:
            main_path="static/data"
            os.mkdir(main_path)
            folders=['download','graphs']
            for folder in folders:
                os.mkdir(os.path.join(main_path,folder))
        except FileExistsError:
            print("Folders already exists")


    def connecet_db(self):
        try:
            self.conn = MongoClient()
            print('Connected')
            return self.conn
        except:
            print('Connect Failed')







    def dateAndFormatValid(self,date):
        self.dateformate = "%Y-%m-%d"

        try:
            date=datetime.datetime.strptime(date, self.dateformate).date()
            return date

        except ValueError:
            print("Incorrect data format, should be YYYY-MM-DD")
            raise

    def readDataFromFileJson(self):
        file=r"donnees-synop-essentielles-omm.json"
        with open(file, "r") as f:
            self.rest = json.load(f)
        return self.rest

    def download_data_from_Json(self, date=None):

        if date==None:
            return self.readDataFromFileJson()
        else:
            self.param = {"refine.date": date, "rows": 10000}
            self.respond = requests.get(self.api, params=self.param)
            self.data = self.respond.json()['records']
        
            return self.data
    
    def getDataforDb(self, date=None):
        y = self.connecet_db()
        self.col = y.MeteoDb.MeteoData
        ver = self.col.find()
        test = list(ver)
        if len(test) == 0:
            print(0)
            self.x = self.download_data_from_Json()
            self.insert_in_db2(self.x, self.col)
        elif date != None:
                print(1)
                self.x = self.download_data_from_Json(date)
                self.insert_in_db2(self.x, self.col)
                print("new things")
        else:
            print("all good")

    def insert_in_db2(self, records, collection):
        print(len(records))
        count=1
        for data in records:
             for key, value in data.items():
                if key == 'fields':
                    speData = ['date', 'nom', 'pmer',
                               'ff', 'tc', 'u', 'pres', 'n']
                    forinsert = {}
                    for i in speData:
                        if i in value.keys():
                            forinsert[i] = value[i]
                        else:
                            forinsert[i] = ''
                    collection.insert_one(forinsert) 
                    print(count)
                    count+=1            
        print('Data entered successfully')

    def check_and_update(self):
        y = self.connecet_db()
        self.db=y.MeteoDb
        dbnames=y.list_database_names()
        if self.db.name not in dbnames:
            print('start')
            self.getDataforDb()
            self.check_and_update()
        else:
            self.col = self.db.MeteoData
            firstTest=self.col.find().sort("date",-1).limit(1)
            lastDate=None
            for i in firstTest:
                lastDate=i['date']
            lastDate=lastDate.split("T")
            lastDate=lastDate[0] 
            lastDate=self.dateAndFormatValid(lastDate)

            currdate=datetime.date.today()
            minus=currdate-lastDate
            ver=int(minus.days)
            if ver>1:
                for i in range(1,ver):
                    a=lastDate+datetime.timedelta(days=i)
                    self.getDataforDb(a)
        print('All good ')
    
    def find_in_db2(self, nom, date):
        
            y = self.connecet_db()
            self.createFolders()
            self.db=y.MeteoDb
            self.col = self.db.MeteoData
            currdate=datetime.date.today()
            date=self.dateAndFormatValid(date)
            nom=nom.upper()

            if date.year==currdate.year:
                date=str(date)
                x = self.col.find({"nom": nom, "date": {'$regex': date}}).sort("date",1)
                test = self.col.count_documents({"nom": nom, "date": {'$regex': date}})
            
                if test == 0:
                    return "Error"
                    
                else:
                    return x



    def graphs(self,nom,date):
        self.te=['pmer','tc','ff','u','pres'] 
        path='static/data/graphs/'
        filename=nom+' '+date
        dirtest=os.listdir(path)
        try:
            for file in dirtest:
                x=re.search(filename,file)
                if x :
                    raise StopIteration;
            
            for i in self.te:
                self.graph(nom,date,i)  
        except StopIteration:
            print('already exists')       
                
    def graph(self, nom, date,ch='tc'):
        self.x=[]
        self.y=[]
        self.find=self.find_in_db2(nom, date)
        self.Graph_dict={'pmer':["pression au miveau mer (Pa)",'Pa'],
            'tc':['temperateur (C)','C°'],
                'ff':['vitesse de vente moyen 10 mn (m/s)','m/s'],
                    'u':['humidite(%)','%'],
                    'pres':['pression station (Pa)','Pa']}

        try:
            for key,value in self.Graph_dict.items():
                if key == ch:
                    for i in self.find:
                        if i[ch] != '':
                            self.x.append(i['date'][11:16])
                            self.y.append(i[ch])
                            plt.figure()
                            plt.switch_backend('agg')
                            plt.bar(self.x, self.y, color = 'g', label = value[1])
                            if ch=='pmer' or ch=='pres':
                                plt.yticks(np.arange(90000, 108000, 4000),rotation = 60)
                                plt.ylim(90000,108000)
                            plt.xlabel('Time')
                            plt.ylabel(value[0])
                            plt.title(value[0]+'by time')
                            path='static/data/graphs/'+nom+' '+date+' '+ch+'.png'
                            plt.legend()
                            plt.savefig(path)
                            plt.close()
                        else:
                            raise StopIteration
        except StopIteration:
            print ("Data already exist in a File")
            
    def wordcld(self,nom='orly',date='2022-11-8'):
        filename='WordCloud'
        path='static/img/'
        dirtest=os.listdir(path)
        try:
            for file in dirtest:
                x=re.search(filename,file)
                if x :
                    raise StopIteration;
            self.find=self.find_in_db2(nom, date)
            teststr=' '
            for i in self.find:
                i=str(i)
                teststr+=' '+i
            wordcloud = WordCloud(background_color="#e2e1eb",max_words=1000 ).generate(teststr)
            wordcloud.to_file(path+filename+'.png')
        except StopIteration:
            print('already exists')    

