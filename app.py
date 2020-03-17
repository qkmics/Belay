from flask import Flask, render_template, request
from flaskext.mysql import MySQL
from datetime import datetime
from flask import request
import random
import string
import json
from flask import jsonify
import bcrypt

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT']=0

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'webHW@123'
app.config['MYSQL_DATABASE_DB'] = 'qiank'


mysql = MySQL()
mysql.init_app(app)

# connect = mysql.connect()
# cursor = connect.cursor()

# sql = "select id, title from posts"
# cursor.execute(sql)
# results = cursor.fetchall()
# print(type(results))
# print(type(results[0]))
# sql = "insert into posts(slug,title) values(1,23)"

# cursor2 = connect.cursor()
# cursor2.execute(sql)
# connect.commit()
# cursor2.close()

# print(results)


session_tokens = {
                
}


@app.route("/")
def main_page():
    return render_template("Belay.html")


@app.route("/api/login", methods = ['POST'])
def login():
    email = request.headers["email"]  
    password = request.headers["password"]   
    print("login {} {}".format(email,password))
    userid,username = get_userid(email,password)
    if(userid < 0):
        return {
            "login_code":"false"
        }

    session_token = randomString()
    session_tokens[session_token] = userid
    return {        
        "login_code" : "true",
        "session_token" : session_token,
        "username" : username
    }


@app.route("/api/register", methods = ['POST'])
def register():
    username = request.headers["username"]  
    password = request.headers["password"]
    email = request.headers["email"]
        
    userid = insert_user(username,password,email)
    if(userid < 0):
        return {
            "register_code":"false" 
        }
    return {
        "register_code": "true",
    }

@app.route("/api/forget_password", methods = ['POST'])
def forget_password():
    email = request.headers["email"]
    print(email)    

    userid = get_userid_by_email(email)
    print("forget_password",userid)

    if(userid < 0):
        return {
            "forget_password_code":"false" 
        }
    return {
        "forget_password_code": "true",
    }


@app.route("/api/reset", methods = ['POST'])
def reset():
    session_token = request.headers["session_token"] 
    username = request.headers["username"]  
    password = request.headers["password"]
    email = request.headers["email"]
    
    print(username)
    print(password)
    print(email)
    
    return {"reset_code": "true"}

@app.route("/api/create_channel", methods = ['POST'])
def create_channle():
    data = json.loads(request.data.decode())
    

    channel_name = data["channelname"]
    session_token = data["session_token"]
    print(channel_name,session_token)
    if(session_token in session_tokens):
        insert_channel(channel_name,session_tokens[session_token])
        print(channel_name,session_tokens[session_token])
    return ""

@app.route("/api/send_message", methods = ['POST'])
def send_message():
    data = json.loads(request.data.decode())

    channel_name = data["channelname"]
    session_token = data["session_token"]
    content = data["content"]

    print(channel_name,session_token,content)
    if(session_token in session_tokens):
        userid = session_tokens[session_token]
        insert_message(channel_name,userid,content)
    return ""


@app.route("/api/request_data", methods = ['POST'])
def request_data():
    data = json.loads(request.data.decode())
    
    session_token = data["session_token"]
    print(session_token)
    
    dic = {}
    if(session_token in session_tokens):
        userid = session_tokens[session_token]
        
        # return channel names and the number of unread message for each channel
        dic["channels"] = channel_names_unread_message(userid) 
    return jsonify(dic)


@app.route("/api/request_messages_in_channel", methods = ['POST'])
def request_messages_in_channel():
    data = json.loads(request.data.decode())
    session_token = data["session_token"]
    channelname = data["channelname"]
    print(session_token)
    
    dic = {}
    if(session_token in session_tokens):
        # return channel names and the number of unread message for each channel
        userid = session_tokens[session_token]
        dic["messages"] = channel_message(channelname,userid) 
    return jsonify(dic)

@app.route("/api/send_reply", methods = ['POST'])
def send_reply():
    data = json.loads(request.data.decode())

    messageid = data["messageid"]
    session_token = data["session_token"]
    content = data["content"]

    if(session_token in session_tokens):
        userid = session_tokens[session_token]
        insert_reply(messageid,userid,content)
    return ""

@app.route("/api/request_replies_in_message", methods = ['POST'])
def request_replies_in_message():
    data = json.loads(request.data.decode())
    session_token = data["session_token"]
    messageid = data["messageid"]
        
    dic = {}
    if(session_token in session_tokens):
        # return channel names and the number of unread message for each channel
        dic["replies"] = message_reply(messageid) 
        print(jsonify(dic))
    return jsonify(dic)


def insert_reply(messageid,userid,content):
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = 'select username from users where id="{}"'.format(userid)
    cursor.execute(sql)
    username = cursor.fetchone()[0]
    print("username = ",username)
    
    sql = 'insert into messages(creatorname,content,messageid) values("{}","{}","{}");'.format(username,content,messageid)
    cursor.execute(sql)
    print(sql)
    
    connect.commit()
    cursor.close()
    connect.close()

# return all messages in a channel
def channel_message(channelname,userid):
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = 'select id from channels where channelname="{}";'.format(channelname)
    cursor.execute(sql)
    print(sql)
    channelid = cursor.fetchone()[0]
   

    sql = 'select id,creatorname,content from messages where channelid="{}" and userid is null;'.format(channelid)
    cursor.execute(sql)
    print(sql)
    all_info = cursor.fetchall()
    
    result = []
    for i in range(len(all_info)):
        sql = 'select count(*) from messages where messageid="{}" and userid is null'.format(all_info[i][0])
        cursor.execute(sql)
        count = cursor.fetchone()
        print(sql)
        print(count)
        result.append(all_info[i] + count)
    
    # do insertion to userid-channelid-messageid
    sql = 'select max(id) from messages where channelid="{}" and messageid is null and userid is null'.format(channelid)
    print(sql)
    cursor.execute(sql)
    maxid = cursor.fetchone()[0]
    if(maxid is not None):
        sql = 'delete from messages where userid="{}" and channelid="{}"'.format(userid,channelid)
        cursor.execute(sql)

        sql = 'insert into messages(userid,channelid,messageid) values("{}","{}","{}")'.format(userid,channelid,maxid)
        cursor.execute(sql)
    
    connect.commit()
    cursor.close()
    connect.close()
    return result

# return all replies in a message
def message_reply(messageid):
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = 'select creatorname,content from messages where messageid="{}" and userid is null'.format(messageid)
    cursor.execute(sql)
    print(sql)
    username_content = cursor.fetchall()
    print(username_content)

    connect.commit()
    cursor.close()
    connect.close()
    return username_content


def insert_message(channelname,userid,content):
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = 'select username from users where id="{}"'.format(userid)
    cursor.execute(sql)
    username = cursor.fetchone()[0]
    print("username = ",username)

    
    sql = 'select id from channels where channelname="{}"'.format(channelname)
    cursor.execute(sql)
    channelid = cursor.fetchone()[0]
    print("channelid = ",channelid)

    sql = 'insert into messages(channelid,creatorname,content) values("{}","{}","{}");'.format(channelid,username,content)
    cursor.execute(sql)
    print(sql)
    
    connect.commit()
    cursor.close()
    connect.close()



# return all channel names and unread message number 
def channel_names_unread_message(userid):
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = 'select id,channelname from channels'
    cursor.execute(sql) 
    print(sql)
    results = cursor.fetchall()
    print(results)
    id_and_channelnames = results;

    array = []
    if(results is not None):
        sql = 'select channelid,messageid from messages where userid="{}"'
        sql = sql.format(userid)
        
        cursor.execute(sql) 
        print(sql)
        results = cursor.fetchall()
        print(results)
        dic = {}
        for result in results:
            dic[result[0]] = result[1]
        print(dic)

        for id_and_channelname in id_and_channelnames:
            channelid = id_and_channelname[0]
            channelname = id_and_channelname[1]
            if(channelid not in dic):
                lowid = -1
            else:
                lowid = dic[channelid]

            sql = 'select count(*) from messages where id>"{}" and channelid="{}" and messageid is null and userid is null'
            sql = sql.format(lowid,channelid)
            print(sql)
            cursor.execute(sql)
            count = cursor.fetchone()[0]
            print(count)
            array.append([channelname,count])

    connect.commit()
    cursor.close()
    connect.close()
    return array


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))



def insert_user(username,password,email):
    userid = -1
    hashedpassword = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = 'select id from users where email="{}";'
    cursor.execute(sql.format(email))
    results = cursor.fetchall()
    print(results)
    print("|||||||||||||||||||||||||||||||||||||||||||||||||")
    if(len(results) == 0):
        sql = 'insert into users(username,password,email) values("{}","{}","{}");'
        cursor.execute(sql.format(username,hashedpassword,email))
        sql ='select id from users where username="{}" and password="{}" and email="{}";'
        cursor.execute(sql.format(username,hashedpassword,email))
        print(sql.format(username,hashedpassword,email))
        results = cursor.fetchall()[0]
        userid = results[0]
        print("userid=",userid)
    
    connect.commit()
    cursor.close()
    connect.close()
    return userid

def get_userid(email,password):
    userid = -1
    username = ""
    connect = mysql.connect()
    cursor = connect.cursor()

    sql = 'select id,username,password from users where email="{}";'
    cursor.execute(sql.format(email,password)) 
    results = cursor.fetchone()
    if(results is not None):
        hashedpassword = results[2]
        print(password)
        print(hashedpassword)
        if (bcrypt.checkpw(password.encode('utf-8'),hashedpassword.encode('utf-8')) == True):
            userid = results[0]
            username = results[1] 
    connect.commit()
    cursor.close()
    connect.close()
    return userid,username

def get_userid_by_email(email):
    userid = -1

    connect = mysql.connect()
    cursor = connect.cursor()

    sql = 'select id from users where email="{}";'
    cursor.execute(sql.format(email))
    print(sql.format(email))
    results = cursor.fetchone()
    print(results)
    print("|||||||||||||||||||||||||||||||||||||||||||||||||")
    if(results is not None):
        userid = results[0]
        print("userid=",userid)
    
    connect.commit()
    cursor.close()
    connect.close()
    return userid

def insert_channel(channelname,userid):
    connect = mysql.connect()
    cursor = connect.cursor()

    #sql = 'select id from channels where channelname="{}";'
    #cursor.execute(sql.format(channelname))
    #print(sql.format(channelname))
    #results = cursor.fetchone()
    #print(results)
    #print("|||||||||||||||||||||||||||||||||||||||||||||||||")
    #if(results is None):
        
    sql = 'insert into channels(channelname,creatorid) values("{}","{}");'
    cursor.execute(sql.format(channelname,userid))
    print(sql.format(channelname,userid))
    
    connect.commit()
    cursor.close()
    connect.close()


if __name__ == '__main__':
    app.run()
