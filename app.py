from flask import Flask, render_template, url_for, request, redirect, session,g
from datetime import datetime
import yeelight 
from time import sleep
from functions import * 
import sys

args = []
ips = ['192.168.178.26', '192.168.178.22']
bulbs = []

currentBulbIndex = 0

def notify(message):
    pass

for ip in ips:
    try:
        bulbs.append(Bulb(ip))
    except Exception as e:
        print(e)

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        pass
    else:
        return render_template('index.html', args=args)

@app.route("/onoff", methods=['POST'])
def onoff():
    if request.method == 'POST':
        try:
            bulbs[currentBulbIndex].toggle()
        except Exception as e:
            print(e)
            notify(e)
        return redirect('/')
    else:
        pass

@app.route("/select/<string:ip>", methods=['POST'])
def select(ip):
    global currentBulbIndex
    if request.method == 'POST':
        for i, ipp in enumerate(ips):
            if ipp == ip:
                currentBulbIndex = i
                args[1] = currentBulbIndex
                break
        return redirect('/')
    else:
        pass

    

if __name__ == "__main__":
    #ips = discover()
    args.append(ips)
    args.append(currentBulbIndex)
    app.run(debug=True)
    #app.run(port='80', host='192.168.178.29') 