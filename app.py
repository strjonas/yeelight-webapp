from flask import Flask, render_template, url_for, request, redirect, send_from_directory, session,g,abort,current_app as app, flash
from datetime import datetime
import yeelight 
from yeelight import *
from time import sleep
import random
from threading import Thread
import os
import sys
import datetime
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = b'#jonas#'


# set up log handler 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("log.log", maxBytes=20000, backupCount=10)
logger.addHandler(handler)

# blacklisting ips

ip_ban_list = ['192.168.178.75','192.168.178.35']



@app.before_request
def block_method():
    ip = request.environ.get('REMOTE_ADDR')
    # keeping an ip log
    if ip != "127.0.0.1":
        dtime = datetime.datetime.now()
        logger.info(f"<time>{dtime}</time> {ip} requested the website!")

    if ip in ip_ban_list:
        abort(403)


# initializing global variables

args = []
ips = []
hwMode = 0
fwMode = 0
alMode = 0
rdMode = 0
currentBulbIndex = 0

bright_val = 50
color_val = "#FFF"

def notify(_message):
    flash(str(_message))

def getRandomGradientM():
    farbverlauf1 = [
    "#FF0000", "#FF0B00", "#FF1600", "#FF2000", "#FF2B00", "#FF3600", "#FF4100", "#FF4B00", "#FF5600", "#FF6100",
    "#FF6C00", "#FF7600", "#FF8100", "#FF8C00", "#FF9700", "#FFA100", "#FFAC00", "#FFB700", "#FFC200", "#FFCC00",
    "#FFD700"];

    farbverlauf2 = [
    "#1A2E64", "#1D2D65", "#202C66", "#222C67", "#252B69", "#282A6A", "#2B296B", "#2D296C", "#30286D", "#33276E",
    "#362670", "#382571", "#3B2572", "#3E2473", "#412374", "#432275", "#462276", "#492178", "#4C2079", "#4E1F7A",
    "#511E7B", "#541E7C", "#571D7D", "#591C7F", "#5C1B80", "#5F1B81", "#621A82", "#641983", "#671884", "#6A1786",
    "#6D1787", "#6F1688", "#721589", "#75148A", "#78148B", "#7A138C", "#7D128E", "#80118F", "#831090", "#851091",
    "#880F92", "#8B0E93", "#8E0D95", "#900D96", "#930C97", "#960B98"];

    farbverlauf3 = [
    "#49E7AB", "#4BE2AB", "#4CDDAA", "#4ED8AA", "#50D3A9", "#52CFA9", "#53CAA8", "#55C5A8", "#57C0A8", "#58BBA7",
    "#5AB6A7", "#5CB1A6", "#5EACA6", "#5FA7A6", "#61A3A5", "#639EA5", "#6499A4", "#6694A4", "#688FA3", "#6A8AA3",
    "#6B85A3", "#6D80A2", "#6F7BA2", "#7077A1", "#7272A1", "#746DA0", "#7568A0", "#7763A0", "#795E9F", "#7B599F",
    "#7C549E", "#7E4F9E", "#804B9D", "#81469D", "#83419D", "#853C9C", "#87379C", "#88329B", "#8A2D9B", "#8C289B",
    "#8D239A", "#8F1F9A", "#911A99", "#931599", "#941098", "#960B98"];

    farbverlauf4 = [
    "#06084B", "#060C4B", "#06104C", "#06144C", "#07184D", "#071C4D", "#07204E", "#07244E", "#07284F", "#072C4F",
    "#073050", "#073450", "#083851", "#083C51", "#084052", "#084452", "#084853", "#084C53", "#085054", "#095454",
    "#095855", "#095C55", "#096056", "#096356", "#096757", "#096B57", "#096F58", "#0A7358", "#0A7759", "#0A7B59",
    "#0A7F5A", "#0A835A", "#0A875B", "#0A8B5B", "#0B8F5C", "#0B935C", "#0B975D", "#0B9B5D", "#0B9F5E", "#0BA35E",
    "#0BA75F", "#0BAB5F", "#0CAF60", "#0CB360", "#0CB761", "#0CBB61"];

    farbverlauf5 = [
    "#385BC3", "#385CBF", "#385DBA", "#385EB6", "#385FB2", "#3860AD", "#3861A9", "#3862A5", "#3863A1", "#38649C",
    "#386598", "#386694", "#39678F", "#39688B", "#396987", "#396A82", "#396B7E", "#396C7A", "#396D75", "#396E71",
    "#396F6D", "#397068", "#397164", "#397160", "#39725C", "#397357", "#397453", "#39754F", "#39764A", "#397746",
    "#397842", "#39793D", "#397A39", "#397B35", "#3A7C30", "#3A7D2C", "#3A7E28", "#3A7F23", "#3A801F", "#3A811B",
    "#3A8217", "#3A8312", "#3A840E", "#3A850A", "#3A8605", "#3A8701"];
    farbverlauf6 = [
    "#0501fa","#0a02f5","#0f03f0","#1404eb","#1905e6","#1e06e1","#2307dc","#2808d7","#2d09d2","#320acd",
    "#370bc8","#3c0cc3","#410dbe","#460eb9","#4b0fb4","#5010af","#5511aa","#5a12a5","#5f13a0","#64149b","#691596",
    "#6e1691","#73178c","#781887","#7d1982","#821a7d","#871b78","#8c1c73","#911d6e","#961e69","#9b1f64","#a0205f",
    "#a5215a","#aa2255","#af2350","#b4244b","#b92546","#be2641","#c3273c","#c82837","#cd2932","#d22a2d","#d72b28",
    "#dc2c23","#e12d1e","#e62e19","#eb2f14","#f0300f","#f5310a","#fa3205"]
    farbverlauf7 = ["#fc0003","#fc0103","#fc0103","#fc0203","#fc0203","#fc0203","#fc0303","#fc0303","#fc0403","#fc0403","#fc0403","#fc0503","#fc0503","#fc0603","#fc0603","#fc0603","#fc0703","#fc0703","#fc0803","#fc0803","#fc0803","#fc0903","#fc0903","#fc0a03","#fc0a03","#fc0a03","#fc0b03","#fc0b03","#fc0c03","#fc0c03","#fc0c03","#fc0d03","#fc0d03","#fc0e03","#fc0e03","#fc0e03","#fc0f03","#fc0f03","#fc0f03","#fc1003","#fc1003","#fc1103","#fc1103","#fc1103","#fc1203","#fc1203","#fc1303","#fc1303","#fc1303","#fc1403","#fc1403","#fc1503","#fc1503","#fc1503","#fc1603","#fc1603","#fc1703","#fc1703","#fc1703","#fc1803","#fc1803","#fc1903","#fb1903","#fb1903","#fb1a03","#fb1a03","#fb1b03","#fb1b03","#fb1b03","#fb1c03","#fb1c03","#fb1d03","#fb1d03","#fb1d03","#fb1e03","#fb1e03","#fb1f03","#fb1f03","#fb1f03","#fb2003","#fb2003","#fb2103","#fb2103","#fb2103","#fb2203","#fb2203","#fb2303","#fb2303","#fb2303","#fb2403","#fb2403","#fb2503","#fb2503","#fb2503","#fb2603","#fb2603","#fb2703","#fb2703","#fb2703","#fb2803","#fb2803","#fb2903","#fb2903","#fb2903","#fb2a03","#fb2a03","#fb2b03","#fb2b03","#fb2b03","#fb2c03","#fb2c03","#fb2c03","#fb2d03","#fb2d03","#fb2e03","#fb2e03","#fb2e03","#fb2f03","#fb2f03","#fb3003","#fb3003","#fb3003","#fb3103","#fb3103","#fb3203","#fb3203","#fb3203","#fb3303","#fb3303","#fb3403","#fb3403","#fb3403","#fb3503","#fb3503","#fb3603","#fb3603","#fb3603","#fb3703","#fb3703","#fb3803","#fb3803","#fb3803","#fb3903","#fb3903","#fb3a03","#fb3a03","#fb3a03","#fb3b03","#fb3b03","#fb3c03","#fb3c03","#fb3c03","#fb3d03","#fb3d03","#fb3e03","#fb3e03","#fb3e03","#fb3f03","#fb3f03","#fb4003","#fb4003","#fb4003","#fb4103","#fb4103","#fb4203","#fb4203","#fb4203","#fb4303","#fb4303","#fb4403","#fb4403","#fb4403","#fb4503","#fb4503","#fb4603","#fb4603","#fb4603","#fb4703","#fb4703","#fb4703","#fb4803","#fb4803","#fb4903","#fb4903","#fb4903","#fb4a03","#fb4a03","#fa4b03","#fa4b03","#fa4b03","#fa4c03","#fa4c03","#fa4d03","#fa4d03","#fa4d03","#fa4e03","#fa4e03","#fa4f03","#fa4f03","#fa4f03","#fa5003","#fa5003","#fa5103","#fa5103","#fa5103","#fa5203","#fa5203","#fa5303","#fa5303","#fa5303","#fa5403","#fa5403","#fa5503","#fa5503","#fa5503","#fa5603","#fa5603","#fa5703","#fa5703","#fa5703","#fa5803","#fa5803","#fa5903","#fa5903","#fa5903","#fa5a03","#fa5a03","#fa5b03","#fa5b03","#fa5b03","#fa5c03","#fa5c03","#fa5d03","#fa5d03","#fa5d03","#fa5e03","#fa5e03","#fa5f03","#fa5f03","#fa5f03","#fa6003","#fa6003","#fa6103","#fa6103","#fa6103","#fa6203","#fa6203","#fa6303","#fa6303","#fa6303","#fa6403","#fa6403","#fa6403","#fa6503","#fa6503","#fa6603","#fa6603","#fa6603","#fa6703","#fa6703","#fa6803","#fa6803","#fa6803","#fa6903","#fa6903","#fa6a03","#fa6a03","#fa6a03","#fa6b03","#fa6b03","#fa6c03","#fa6c03","#fa6c03","#fa6d03","#fa6d03","#fa6e03","#fa6e03","#fa6e03","#fa6f03","#fa6f03","#fa7003","#fa7003","#fa7003","#fa7103","#fa7103","#fa7203","#fa7203","#fa7203","#fa7303","#fa7303","#fa7403","#fa7403","#fa7403","#fa7503","#fa7503","#fa7603","#fa7603","#fa7603","#fa7703","#fa7703","#fa7803","#fa7803","#fa7803","#fa7903","#fa7903","#fa7a03","#fa7a03","#fa7a03","#fa7b03","#fa7b03","#fa7c03","#fa7c03","#fa7c03","#f97d03","#f97d03","#f97e03","#f97e03","#f97e03","#f97f03","#f97f03","#f98003","#f98003","#f98003","#f98103","#f98103","#f98103","#f98203","#f98203","#f98303","#f98303","#f98303","#f98403","#f98403","#f98503","#f98503","#f98503","#f98603","#f98603","#f98703","#f98703","#f98703","#f98803","#f98803","#f98903","#f98903","#f98903","#f98a03","#f98a03","#f98b03","#f98b03","#f98b03","#f98c03","#f98c03","#f98d03","#f98d03","#f98d03","#f98e03","#f98e03","#f98f03","#f98f03","#f98f03","#f99003","#f99003","#f99103","#f99103","#f99103","#f99203","#f99203","#f99303","#f99303","#f99303","#f99403","#f99403","#f99503","#f99503","#f99503","#f99603","#f99603","#f99703","#f99703","#f99703","#f99803","#f99803","#f99903","#f99903","#f99903","#f99a03","#f99a03","#f99b03","#f99b03","#f99b03","#f99c03","#f99c03","#f99c03","#f99d03","#f99d03","#f99e03","#f99e03","#f99e03","#f99f03","#f99f03","#f9a003","#f9a003","#f9a003","#f9a103","#f9a103","#f9a203","#f9a203","#f9a203","#f9a303","#f9a303","#f9a403","#f9a403","#f9a403","#f9a503","#f9a503","#f9a603","#f9a603","#f9a603","#f9a703","#f9a703","#f9a803","#f9a803","#f9a803","#f9a903","#f9a903","#f9aa03","#f9aa03","#f9aa03","#f9ab03","#f9ab03","#f9ac03","#f9ac03","#f9ac03","#f9ad03","#f9ad03","#f9ae03","#f9ae03","#f8ae03","#f8af03","#f8af03","#f8b003","#f8b003","#f8b003","#f8b103","#f8b103","#f8b203","#f8b203","#f8b203","#f8b303","#f8b303","#f8b403","#f8b403","#f8b403","#f8b503","#f8b503","#f8b603","#f8b603","#f8b603","#f8b703","#f8b703","#f8b803","#f8b803","#f8b803","#f8b903","#f8b903","#f8b903","#f8ba03","#f8ba03","#f8bb03","#f8bb03","#f8bb03","#f8bc03","#f8bc03","#f8bd03","#f8bd03","#f8bd03","#f8be03","#f8be03","#f8bf03","#f8bf03","#f8bf03","#f8c003","#f8c003","#f8c103","#f8c103","#f8c103","#f8c203","#f8c203","#f8c303","#f8c303","#f8c303","#f8c403","#f8c403","#f8c503","#f8c503","#f8c503","#f8c603","#f8c603","#f8c703"]


    modes = []
    modes.append(farbverlauf1)
    modes.append(farbverlauf2)
    modes.append(farbverlauf3)
    modes.append(farbverlauf4)
    modes.append(farbverlauf5)
    modes.append(farbverlauf6)
    modes.append(farbverlauf7)
    rand = random.randint(0,len(modes)-1)
    return modes[rand]

def helligkeitswechsel():
        global fwMode,alMode,rdMode,hwMode
        br = 0
        minorplus = 1
        hwMode = 1
        fwMode = 0
        alMode = 0
        rdMode = 0
        try:
           bulbs[currentBulbIndex].set_rgb(255,255,255)
        except:
            print("Mode not supported")
            notify("Mode not supported") 
            return
        try:
            bulbs[currentBulbIndex].start_music()
        except:pass
        try:
            bulbs[currentBulbIndex].ensure_on()
        except Exception as e:
            print(e)
            notify(e)
            return 
        try:
            while hwMode > 0:

                if br == 100:
                    minorplus = -1
                if br == 0:
                    minorplus = 1
                if minorplus > 0:
                    br += 5
                else:
                    br -= 5
                bulbs[currentBulbIndex].set_brightness(br)
                sleep(0.1)
        except Exception as e:
            print(e)
            notify(e)

def randomMode():
        global fwMode,alMode,rdMode,hwMode
        hwMode = 0
        fwMode = 0
        alMode = 0
        rdMode = 1
        try:
           bulbs[currentBulbIndex].set_rgb(255,255,255)
        except:
            print("Mode not supported")
            notify("Mode not supported") 
            return
        try:
            bulbs[currentBulbIndex].start_music()
        except:pass
        try:
            bulbs[currentBulbIndex].ensure_on()
        except Exception as e:
            print(e)
            notify(e)
            return 
        try:
            
            index = 0
            al = []
            mode = getRandomGradientM()
            for x in mode: # writing mode list into al list as rgb values (were hex)
                h = x.lstrip('#')
                r = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
                al.append(r)
            
            while rdMode > 0:

                if index >= len(al)-1:
                    al = []
                    mode = getRandomGradientM()
                    for x in mode: # writing mode list into al list as rgb values (were hex)
                        h = x.lstrip('#')
                        r = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
                        al.append(r)
                    index = 0
                
                bulbs[currentBulbIndex].set_rgb(*al[index])
                index +=1
                sleep(0.5)
        except Exception as e:
            notify(e)
            print(e)

def ambilight():
    global fwMode,alMode,rdMode,hwMode
    hwMode = 0
    fwMode = 0
    alMode = 1
    rdMode = 0
    try:
           bulbs[currentBulbIndex].set_rgb(255,255,255)
    except:
            print("Mode not supported")
            notify("Mode not supported") 
            return
    try:
        bulbs[currentBulbIndex].start_music()
    except:pass
    try:
        bulbs[currentBulbIndex].ensure_on()
        
    except Exception as e:
        print(e)
        notify(e)
        return
    bulbs[currentBulbIndex].set_brightness(100)
    import pyautogui
    try:
        while alMode > 0:
            sc = pyautogui.screenshot()
            co = sc.getpixel((1000,500))
            bulbs[currentBulbIndex].set_rgb(*co)
            sleep(0.1)
    except Exception as e:
        notify(e)
        print(e)

            
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        return render_template('index.html', args=args)
    else:
        print(args)
        return render_template('index.html', args=args)

@app.route('/changcolor', methods=['POST', 'GET'])
def changeColor():
    if request.method == 'GET':
        try:
            global color_val
            color_val = request.args.get("color")
            args[3] = color_val
            
            h = color_val.lstrip('#')

            r = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
            bulbs[currentBulbIndex].set_rgb(*r)
        except Exception as e:
            print(e)
            notify(e)
        return redirect('/')
    else:
        return redirect('/')

@app.route('/stop', methods=['POST', 'GET'])
def stop():
    global hwMode,fwMode,alMode,rdMode
    if request.method == 'POST':
        hwMode = 0
        fwMode = 0
        alMode = 0
        rdMode = 0
        
        return redirect('/')
    else:
        return redirect('/')

@app.route('/reset', methods=['POST', 'GET'])
def reset():
    if request.method == 'POST':
        try:
            bulbs[currentBulbIndex].set_brightness(50)
            try:
                bulbs[currentBulbIndex].stop_music()
                bulbs[currentBulbIndex].set_rgb(255,255,255)
            except:
                try:
                    bulbs[currentBulbIndex].set_color_temp(4000)
                except:pass
               
        

        except Exception as e:
            print(e)
            notify(e)
        return redirect('/')
    else:
        return redirect('/')

@app.route("/onoff", methods=['POST'])
def onoff():
    if request.method == 'POST':
        try:
            bulbs[currentBulbIndex].toggle()
        except Exception as e:
            print(currentBulbIndex)
            print(e)
            notify(e)
        return redirect('/')
    else:
        pass

@app.route("/discoverbulbs", methods=['POST'])
def discoverbulbs():
    if request.method == 'POST':
        try:
            i = discover()
            for x in i:
                if not x in ips:ips.append(x)
            for x in ips:
                if Bulb(x) not in bulbs:
                    bulbs.append(Bulb(x))
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

@app.route("/set_brightness", methods=['GET'])
def set_brightness():
    br = int(request.args.get("brightness"))
    global bright_val
    bright_val = br
    args[2] = bright_val
    try:
        bulbs[currentBulbIndex].set_brightness(br)
    except Exception as e:
        print(e)
        notify(e)
    return redirect('/')


@app.route("/mode/<string:mode>", methods=['POST'])
def selectmode(mode):
    global currentBulbIndex
    if request.method == 'POST':
        if mode == "helligkeitswechsel":
            t = Thread(target=helligkeitswechsel)
            t.start()
        elif mode == "farbwechsel":
            t = Thread(target=randomMode)
            t.start()
            
        elif mode == "ambilight":
            t = Thread(target=ambilight)
            t.start()
        elif mode == "randommodes":
            try:
                bulbs[currentBulbIndex].set_rgb(255,255,255)
            except:
                print("Mode not supported")
                notify("Mode not supported") 
                return
            sr = yeelight.flows.sunrise()
            bulbs[currentBulbIndex].start_flow(sr)
        return redirect('/')
    else:
        pass

    
if __name__ == "__main__":
    from YEEfunctions import discover
    #ips = discover()
    ips = ["192.168.178.81","192.168.178.82","192.168.178.69","192.168.179.23"]
    bulbs = []
    for ip in ips:
        try:
            bulbs.append(Bulb(ip))
        except Exception as e:
            print(e)

    args.append(ips)
    args.append(currentBulbIndex)
    args.append(bright_val)
    args.append(color_val)
    app.run(debug=True)
    #app.run(port='80', host='192.168.178.29') 