
from flask import Flask, render_template


app = Flask(__name__)

db_id = 'vis'
db_pw = 'gjvis4444'
url = 'project-db-stu.ddns.net:1524/xe'

app.secret_key = "vis"

@app.route('/')
def main():
    return render_template('index.html')
#if __name__ == '__main__':
#    app.run(host='127.0.0.1', port=3000)