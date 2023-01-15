from flask import Flask
from flask import render_template, request, redirect, session
from flask_session import Session
import json
import sqlite3
from flask_cors import CORS
from flask_mail import Mail, Message

from datetime import datetime
import axe
import hashlib
import string
import random
    
import axe_json




app = Flask(__name__)
CORS(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)





#mail
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '#########'
app.config['MAIL_PASSWORD'] = '##########'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
#mail


from pymongo import MongoClient
client = MongoClient('localhost', 8444)
db = client.sites
sites = db.sites
ip= db.ip
users= db.users
tokens= db.tokens
feedbacks= db.feedbacks



def create_token(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    token = ''.join(random.choice(letters) for i in range(length))
    token+= str(random.randrange(1,9999))
    return token


def update_projects(username):
    project_counter=0
    all_sites= sites.find()
    for x in all_sites:
        if x["user"]==username:
            project_counter+=1
    session["projects"]= project_counter




@app.route("/")
def main():
    #return render_template("home2.html")
    #return render_template("home2.html")
    return render_template("index.html")




@app.route("/scan")
def scan():
    #return render_template("axe2.html")
    if session:
        return render_template("scan.html")
    else:
        return render_template("login.html")


@app.route("/home")
def home():
    return render_template("master.html")

@app.route("/scan_website", methods = ['POST'])
def scan_website(): 
    ip_addr = request.remote_addr
    url= request.form["url"]
    username= session.get("username")
    # url= request.get_data()
    # url= url.decode('utf-8')
    # url= url.strip("url=").replace("%2F", "")
    # print("URL: ", url)
    # axe.scan_website("https://"+url)
    axe.scan_website(url)
    now= datetime.now()
    current_time= now.strftime("%d-%m-%Y  %H:%M:%S")
    
    check= sites.find_one({"site_name": {"$eq": url}})
    if check:
        sites.delete_one({"site_name":url})

        sites.insert_one({"user": session.get("username"),"site_name":url, "issues_count": len(axe_json.get_violations()), "issues": axe_json.get_violations(), "last_scan_time": current_time})

        users.update_one({"username": session.get('username')}, {'$push': {'sites': {"site_name":url, "issues_count": len(axe_json.get_violations()), "issues": axe_json.get_violations(), "last_scan_time": current_time}}}, upsert = True)
    else:
        sites.insert_one({"user": session.get("username"),"site_name":url, "issues_count": len(axe_json.get_violations()), "issues": axe_json.get_violations(), "last_scan_time": current_time})
        ip.insert_one({"ip": ip_addr, "url": "/scan", "connection_time": current_time})
        username= session.get("name")
        users.update_one( {"username": session.get('username')}, {'$push': {'sites': {"site_name":url, "issues_count": len(axe_json.get_violations()), "issues": axe_json.get_violations(), "last_scan_time": current_time}}}, upsert = True)
    # projects_uniek= []
    #projects= users.find_one({"username": session.get("username")})["sites"]
    # for x in projects:
    #     projects_uniek.append(x["site_name"])
    update_projects(username)
    
    return axe_json.get_violations()

@app.route("/scan_again", methods=["POST", "GET"])
def scan_again():
    if session:
        url= request.form["url"]
        app.logger.info(url)
        
        return render_template("scan.html", scan_again= url)
    else:
        return render_template("login.html")


@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/profile")
def profile():
    

    if (session):
        name= session.get("name")
        print(session.get("projects"))
        return render_template("profile.html")
    else:
        return render_template("login.html")

@app.route("/feedback_form", methods=["POST"])
def feedback_form():
    name= request.form["name"]
    email= request.form["email"]
    subject= request.form["subject"]
    message= request.form["message"]
    feedbacks.insert_one({"from": name, "email": email, "onderwerp": subject, "message": message})
    #send mail
    msg = Message('Feedback', sender =   email, recipients = ["admin@accessibility.nl"])
       
        #  msg.body = "Hi {}\nFollow the link to reset your password:\n ".format(get_name)
        #  msg.body = "Hi {}\nFollow the link to reset your password:\n ".format(get_name)
    msg.html= "<h3>Onderwerp: {}</h3><p>{}</p><p>Groeten</p><p>{}</p>".format(subject, message, name)
    mail.send(msg)
    return render_template("feedback_new.html", feedback_success="success")

@app.route("/sites")
def get_sites():
    sites_list= []
    # user_sites= users.find_one({"username": session.get("username")})["sites"]
    # # print(x)
    # for x in user_sites:
    #     all_sites.append({"site_name":x["site_name"], "issues_count":x["issues_count"], "last_scan": x["last_scan_time"]})
    # # print(all_sites)

    username= session.get("username")
    all_sites= sites.find()
    for x in all_sites:
        if x["user"]==username:
            print(x["site_name"])
            sites_list.append({"site_name":x["site_name"], "issues_count":x["issues_count"], "last_scan": x["last_scan_time"]})
            
    # return redirect("/")
    return render_template("list.html", data= sites_list)




@app.route("/get_issues", methods=["POST", "GET"])
def get_issues():

    issues= []
    user_sites= users.find_one({"username": session.get("username")})["sites"]
    
    url= request.form["url"]
    
    for x in user_sites:
        if x["site_name"]==url: print(x)
    for x in sites.find({"site_name": url}):
        issues.append({"issue": x["issues"]})
    print(issues)
    return issues

@app.route("/login")
def login():
    return render_template("login_new.html")
    

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/loguit")
def loguit():
    if session:
    #session.pop('username')
        session.clear()
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/forgot_password")
def forgot():
    return render_template("forgot_password.html")

@app.route("/forgot")
def forgot_password():
    email= request.args.get("email")
    check_mail= users.find_one({"email": {"$eq": email}})["email"]
    if  check_mail:
         token= create_token(15)
         get_password= users.find_one({"email": email})["password"]
         get_name= users.find_one({"email": email})["name"]
         print(get_password)
         msg = Message('Password reset', sender =   'admin@accessibility.nl', recipients = [email])
         link= "http://145.24.222.186:8002/reset_password/{}/{}".format(email,token)
        #  msg.body = "Hi {}\nFollow the link to reset your password:\n ".format(get_name)
        #  msg.body = "Hi {}\nFollow the link to reset your password:\n ".format(get_name)
         msg.html= "<h3>Hi {}</h3><p>Follow the link to reset your password:</p><a href='{}'>click here</a>".format(get_name,link)
         mail.send(msg)
         tokens.insert_one({"token": token})
         return render_template("forgot_password.html", success="success")
    else:
        return render_template("forgot_password.html", error="error")

@app.route("/reset_password/<email>/<token>")
def reset_pass(token, email):
    return render_template("pass_reset.html", email=email)

@app.route("/create_new_pass")
def create_new_pass():
    password= request.args.get("password")
    password_confirm= request.args.get("password_confirm")
    email= request.args.get("email")

    app.logger.info("EMAIL: ", email)
    if (password==password_confirm):
        hash_ = hashlib.md5(password.encode())
        pass_hash= hash_.hexdigest()
        app.logger.info(pass_hash)
        users.update_one({"email":email}, { "$set": { "password": pass_hash} } )
        return render_template("login.html")
    else:
        return render_template("pass_reset.html", error="error")
        
    

@app.route("/check_login")
def check_login():
    username = request.args.get("username")
    password= request.args.get("password")
    hash_ = hashlib.md5(password.encode())
    pass_hash= hash_.hexdigest()
    print("Hash: ",pass_hash)
    check= users.find()
    counter=0
    project_counter=0
    for x in check:
        usr= x["username"]
        pswd= x["password"]
        print(usr)
        print(pswd)
        if(usr==username and pswd==pass_hash):
            counter+=1
    print("counter: ", counter)
    if counter>0:
        name= users.find_one({"username": username})["name"]
        
        # for x in projects:
        #     projects_uniek.append(x["site_name"])
        email= users.find_one({"username": username})["email"]
       
        session["username"] = request.args.get("username")
        session["name"] = name
        #session["projects"]= len(set(projects_uniek))
        session["email"]= email
        all_sites= sites.find()
        for x in all_sites:
            if x["user"]==username:
                project_counter+=1
        session["projects"]= project_counter
        return redirect("/")
    else:
        return render_template("login_new.html", error="error")


@app.route("/remove")
def remove():
    
    if session:
        username= session.get("username")
        users.delete_one({"username": username})
        
        all_sites=sites.find()
        for x in all_sites:
            if x["user"]==username:
                sites.delete_one({"user": username})

        session.clear()
        return redirect ("/")
    else:
        return  render_template("login.html")


@app.route("/user_register")
def user_register():
    print("register form")
    name = request.args.get("name")
    username = request.args.get("username")
    email= request.args.get("email")
    passwoord= request.args.get("password")
    pass_hash = hashlib.md5(passwoord.encode())
    print(pass_hash.hexdigest())
    passwoord_confirm=  request.args.get("password_confirm")
    print(username)
    check_mail= users.find_one({"email": {"$eq": email}})
    check_username= users.find_one({"username": {"$eq": username}})


    print("check mail: ", check_mail)
    print("check username: ", check_username)


    if (passwoord != passwoord_confirm):
        return render_template("register_new.html", error_pass="error")
    if (check_mail):
        return render_template("register_new.html", error_email="error")
    if (check_username):
        return render_template("register_new.html", error_username="error")
    else:
        users.insert_one({"name":name, "username":username, "email":email, "password": pass_hash.hexdigest()})
        return render_template("login.html")



# @app.route("/mail")
# def index():
#   msg = Message('Hello from the other side!', sender =   'peter@mailtrap.io', recipients = ['paul@mailtrap.io'])
#   msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
#   mail.send(msg)
#   return "Message sent!"



@app.route("/remove_site" , methods=["POST"])
def remove_site():
    project_counter=0
    username= session.get("username")
    site= request.form["url"]
    #user_sites= users.find_one({"username": session.get("username")})["sites"]
    # app.logger.info(site)
    # site= "https://"+site
    all_sites= sites.find()
    for x in all_sites:
        if x["user"]==username:
            sites.delete_one({"site_name":site})
    # app.logger.info("SITE: ", site)
    # for x in user_sites:
    #     list_sites= []
    #     if x["site_name"]!=site:
    #         app.logger.info(x["site_name"]) 
    #         list_sites.append(x)
    #print(list_sites)
    # if (len(user_sites)==1):
    #     users.update_one({"username":session.get("username")}, { "$set": { "sites": []} } )
    # else:
    #     users.update_one({"username":session.get("username")}, { "$set": { "sites": list_sites} } )
    # projects_uniek= []
    # projects= users.find_one({"username": session.get("username")})["sites"]
    # for x in projects:
    #     projects_uniek.append(x["site_name"])
    # session["projects"]= len(set(projects_uniek))
    # app.logger.info(list_sites)
    # all_sites= sites.find()
    # for x in all_sites:
    #     if x["user"]==username:
    #         project_counter+=1
    # session["projects"]= project_counter
    update_projects(username)
    return redirect("/sites")
 


@app.route("/delete_sites", methods = ['GET'])
def delete_site():
    sites.delete_many({})
    return redirect("/")
@app.route("/delete_ip", methods = ['GET'])
def delete_ip():
    ip.delete_many({})
    return redirect("/")




@app.route("/get_feedbacks")
def get_feedbacks():
    feeds= []
    
    for x in feedbacks.find():
        feeds.append(x)
    return  render_template("get_feedbacks.html", data= feeds)

#test

@app.route("/test")
def test():
    return render_template("feedback_new.html")

@app.route("/test_login")
def test1():
    return render_template("register_new.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8002, debug=True)
