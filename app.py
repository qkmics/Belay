from flask import Flask, render_template, request
from flaskext.mysql import MySQL

app = Flask(__name__)


app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'webHW@123'
app.config['MYSQL_DATABASE_DB'] = 'webhw'


mysql = MySQL()
mysql.init_app(app)

connect = mysql.connect()
cursor = connect.cursor()

sql = "SELECT * FROM posts"
cursor.execute(sql)
results = cursor.fetchall()
print(results)



if __name__ == '__main__':
    app.run()
