import pandas as pd
from bs4 import BeautifulSoup as Soup
import csv, js
import io
import json
import os
from werkzeug.datastructures import ResponseCacheControl
from werkzeug.utils import secure_filename

from flask import Flask, render_template, url_for, request, session, redirect, flash, Response

from flask_pymongo import PyMongo
import bcrypt
from pymongo import MongoClient, ssl_support
mongo = MongoClient('mongodb+srv://amansheth:aman123@rc.xliti.mongodb.net/test', ssl_cert_reqs=ssl_support.CERT_NONE)
app = Flask(__name__,template_folder='templates')
app.secret_key = "man"
# app.config ['MONGO_URI'] = 'mongodb+srv://manasvi:man14@queenman.rrrho.mongodb.net/db'
# mongo = PyMongo(app)

@app.route("/")
@app.route("/main")
def main():
    return render_template('main.html')

@app.route('/result')
def result():
   return render_template('result.html')

@app.route('/table')
def table():
    return render_template('table.html')


@app.route('/result_page', methods=['GET','POST'])
def result_page():
        # features="lxml"
        a = pd.read_csv(request.form['Year'] + request.form['Semester'] + request.form['Branch'] + ".csv")
        b = a.loc[a['SEAT NO.'] == int(request.form["seat_no"])].drop('Sr. No.', inplace=False, axis=1).set_index(['SEAT NO.'], inplace=False).T
        # b.to_html("templates/result_page.html")
        html_file = b.to_html()
        f = open("templates/result_page.html", "r")
        page = f.read()
        f.close()
        f = open("templates/result_page.html", "w")
        soup = Soup(html_file)
        soup2 = Soup(page)
        table = soup2.find('table')
        if table:
            table.decompose()

        # print(soup2)
        report = soup2.find("div", {"id": "report"})
        report.append(soup)
        # print(soup2)
        f.write(str(soup2))
        f.close()
        # print(b)
        # print (request.form["seat_no"])
        return render_template('result_page.html')



@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            flash("Successfully Logged In!")
            return redirect(url_for('dashboard'))

    return 'Invalid username/password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
         # return 'That username already exists!'

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/insert_sheet', methods=['GET','POST'])
def insert_sheet():
    return render_template('insert_sheet.html')


@app.route('/result_analysis', methods=['GET','POST'])
def result_analysis():
    return render_template('result_analysis.html')

# @app.route('/google_pie_chart')
# def google_pie_chart():
#     data = {'Task' : 'Hours per Day', 'Work' : 22, 'Eat' : 4, 'Commute' : 6, 'Watching TV' : 5, 'Sleeping' : 15}
#     return render_template('google_pie_chart.html', data=data)




@app.route('/create', methods=['POST'])

def create():
    if 'upload_file' in request.files:
        upload_file = request.files['upload_file']
        # print('dirname:     ', os.path.dirname(__file__))
        upload_file.save(os.path.join( os.path.dirname(__file__), secure_filename(request.form['Year'] + request.form['Semester'] + request.form['Branch'] + ".csv")))

        #df = pd.read_csv(upload_file.filename)

        #df.fillna('', inplace = True)

        #json_object=df.to_json()
        #print(json_object)

        csvFilePath = request.form['Year'] + request.form['Semester'] + request.form['Branch'] + ".csv"

        
        # print(a)


        dict1 ={}

        corrected_dict = {}

        with open(csvFilePath,  encoding='utf-8-sig') as csvf:
            csvReader = csv.DictReader(csvf)

            for rows in csvReader:
                # print(rows)
             
            # Assuming a column named 'No' to
            # be the primary key
                key = rows['Sr. No.']
                dict1[key] = rows

        # json_object = json.dumps(dict1, indent = 4)
            for j in dict1:
                for k,v in dict1[j].items():
                    newK = k.replace('\n', '')
                    newK2 = newK.replace(' ','')
                    # if v != "": 
                    corrected_dict[newK2.replace('.', '')] = v 
                #print(corrected_dict)
                mongo.test[request.form['Year'] + request.form['Semester'] + request.form['Branch']].insert({'usernameid':request.form['usernameid'],'upload_file': corrected_dict})
                # print(corrected_dict)
    # return (request.form['Year'], request.form['Semester'], request.form['Branch'])
    # return redirect('/dashboard') 
    flash("Successfully Uploaded File!")
    return redirect(url_for('dashboard'))
    

@app.route('/analysis', methods=['POST'])
def analysis():
    # db="db"
    newarr = []
    
    

    
    colName =  request.form['Year'] + request.form['Semester'] + request.form['Branch']
    # print(mongo.test.list_collection_names())
    # if True:
    if colName in mongo.test.list_collection_names():
        
        total_students = mongo.test[colName].count_documents({})
        fields = mongo.test[colName].find_one()
        # print(fields["upload_file"].keys())
        # print(fields)
        for a in fields["upload_file"].keys():
            if a.find("SE") != -1:
                newa ="upload_file." + a
                newarr.append( { newa: {"$ne": ""}})
        # print(newarr)        
        # appeared_students = mongo.db[colName].find({"$or": newarr}).count()
        condition = {"$and": newarr}
        # appeared_students = mongo.db[colName].find(condition).count()
        # for a in fields["upload_file"].keys():
        #     if a.find("SE") != -1 and a!="A":
        #         newa ="upload_file." + a
        #         appeared_students.append( { newa: {"$ne": ""}}) 
        #         ap_stud=len(appeared_students)
        #         print(ap_stud)
        # print(condition)
    
        # appeared_students = mongo.db[colName].find({'$and': [{'upload_file.EngineeringMathematicsIVTOT100': {'$ne': ''}},{'upload_file.AnalysisOfAlgorithmTOT100': {'$ne': ''}}]}).count()
        
        # print(appeared_students)




                # if fields["upload_file"][a] == "":
                #     print(a, "Not Appeared")
        # print(str(total_students))
        newarr = []
        newsub_IA = []
        newsub_SE = []
        newsub_P = []
        subwise_IA = []
        subwise_P= []
        subwise_SE = []

        # passed_students = mongo.db[colName].find({ "$expr": { "$lte": [ { "$toInt": "$upload_file.AnalysisOfAlgorithmIA20" }, 8] } }).count()
        for a in fields["upload_file"].keys():
            if a.find("IA") != -1:
                newa ="$upload_file." + a
                newarr.append( {'$and':[{"upload_file." + a: {"$ne": "A"}},{"upload_file." + a: {"$ne": ""}},{ "$expr": { "$lt": [ { "$toInt": newa }, 8] } }]})
                newsub_IA.append(a)
            elif  a.find("SE") != -1 and a!= "SEATNO":
                newa ="$upload_file." + a
                newarr.append( {'$and':[{"upload_file." + a: {"$ne": "A"}},{"upload_file." + a: {"$ne": ""}},{ "$expr": { "$lt": [ { "$toInt": newa }, 32] } }]})
                newsub_SE.append(a)
            elif  a.find("P&") != -1:
                newa ="$upload_file." + a
                newarr.append( {'$and':[{"upload_file." + a: {"$ne": "A"}},{"upload_file." + a: {"$ne": ""}},{ "$expr": { "$lt": [ { "$toInt": newa }, 10] } }]}) 
                newsub_P.append(a)     
        print(newsub_P)        
        # appeared_students = mongo.db[colName].find({"$or": newarr}).count()
        #failed_students =len(list(mongo.test["2020SEMIIICS"].aggregate([{'$project': {'array': {'$objectToArray': '$upload_file'},'doc': '$$ROOT'}},{'$match': {'array.v': 'A'}},{'$replaceRoot': {'newRoot': '$doc'}}])))
        appeared_students = total_students - len(list(mongo.test[colName].aggregate([{'$project': {'array': {'$objectToArray': '$upload_file'},'doc': '$$ROOT'}},{'$match': {'array.v': 'A'}},{'$replaceRoot': {'newRoot': '$doc'}}])))
        condition = {"$or": newarr}
        failed_students = mongo.test[colName].find(condition).count() 
        # print(condition)  
        # print(failed_students)
        # print(newsub_IA)
        for s in newsub_IA:
            IA_analysis = mongo.test[colName].find({'$and':[{"upload_file." + s: {"$ne": "A"}},{"upload_file." + s: {"$ne": ""}},{"$expr": { "$gte": [ { "$toDouble": "$upload_file." + s }, 8] }}]}).count()
            IA_appeared = mongo.test[colName].find({'$and':[{"upload_file." + s: {"$ne": "A"}},{"upload_file." + s: {"$ne": ""}}]}).count()
            passing_percentageIA = (IA_analysis/IA_appeared)*100
            subwise_IA.append({"subname":s, "value": IA_analysis, "percentage": passing_percentageIA, "appeared" :  IA_appeared})
        print(subwise_IA)
        
        for x in newsub_P:
            p_analysis = mongo.test[colName].find({'$and':[{"upload_file." + x: {"$ne": "A"}},{"upload_file." + x: {"$ne": ""}},{"$expr": { "$gte": [ { "$toDouble": "$upload_file." + x }, 10] }}]}).count()
            p_appeared = mongo.test[colName].find({'$and':[{"upload_file." + x: {"$ne": "A"}},{"upload_file." + x: {"$ne": ""}}]}).count()
            pass_percp = (p_analysis/p_appeared)*100
            subwise_P.append({"subnames":x, "values": p_analysis, "percentages": pass_percp, "appeareds" :  p_appeared })
        print(subwise_P)
        for y in newsub_SE:
            p_analysiss = mongo.test[colName].find({'$and':[{"upload_file." + y: {"$ne": "A"}},{"upload_file." + y: {"$ne": ""}},{"$expr": { "$gte": [ { "$toDouble": "$upload_file." + y }, 32] }}]}).count()
            p_appeareds = mongo.test[colName].find({'$and':[{"upload_file." + y: {"$ne": "A"}},{"upload_file." + y: {"$ne": ""}}]}).count()
            pass_percps = (p_analysiss/p_appeareds)*100
            subwise_SE.append({"subnamess":y, "valuess": p_analysiss, "percentagess": pass_percps, "appearedss" :  p_appeareds })
        print(subwise_SE)


        passed_students = total_students-failed_students

        passing_percentage = (passed_students/appeared_students)*100
        # print(format(passing_percentage, ".2f"))


        fc_distinction = mongo.test[colName].find({'$and':[{"upload_file.GPA": {"$ne": ""}},{"$expr": { "$gte": [ { "$toDouble": "$upload_file.GPA" }, 7.75] }}]}).count()
        # print(fc_distinction)

        data = {'Particular' : 'Without KT(regular)',
            "Total no of Students Registered":  total_students,
             "Total no of Students Appeared": appeared_students,
             "Total no of Students Passed": passed_students,
             "Total no of Students Failed":  failed_students,
             "Percentage of Passing": passing_percentage,
             "Total no of Students with First Class with Distinction":  fc_distinction}





    
        # return("Total Number Of Students Registered:  " + str(total_students) + "   Total Number Of Students Appeared: " + str(appeared_students) +   
        #     "    Total Number Of Students failed: " + str(failed_students)) + "    Total Number Of Students Passed: " + str(passed_students) +  "  Passing Percentage: " + str(format(passing_percentage, ".2f"))
        return render_template('analysis.html', total_students = total_students,passed_students =  passed_students,appeared_students=appeared_students,
        passing_percentage = format(passing_percentage), fc_distinction = fc_distinction,failed_students=failed_students,s=s,IA_analysis=IA_analysis,passing_percentageIA=passing_percentageIA,IA_appeared=IA_appeared,x=x,p_analysis=p_analysis,pass_percp=pass_percp,p_appeared=p_appeared,newsub_IA=newsub_IA,newsub_P=newsub_P,
        newsub_SE=newsub_SE,p_analysiss=p_analysiss,p_appeareds=p_appeareds,pass_percps=pass_percps, subwise_IA=subwise_IA,subwise_P=subwise_P,subwise_SE=subwise_SE,data = data)
        
        # print(str(total_students))
    else:
        return("Collection Not Found!")



      # if 'upload_file' in request.files:
      #   upload_file = request.files['upload_file']
      #   print('dirname:     ', os.path.dirname(__file__))
      #   upload_file.save(os.path.join( os.path.dirname(__file__), secure_filename(request.form['Year'] + 
      #       request.form['Semester'] + request.form['Branch'] + ".csv")))



    #     with open("sample.json", "w") as outfile:
    #         outfile.write(json_object)
    #     mongo.db.users.insert({'username':request.form['username'],'upload_file' : json_object })
    #     print(json_object)
    #     return request.form['username'] 
    # else:
    #     return redirect('/insert_sheet')

if __name__=='__main__':
    app.run(debug=True)