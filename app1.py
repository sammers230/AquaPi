
#AquaPi automated water changer with Flask webserver.
import RPi.GPIO as GPIO
from flask import Flask, render_template, redirect, url_for
import datetime
import time
import threading
import schedule
#from epaper import paper
#from Changer import Change

Var1 = 0 #variable to have system trigger mixing after filling container
Var2 = 1 #variable to lockout buttons to prevent premature program triggers while changing water etc
Var3 = 0 #variable to prevent ATO from topping up tank when perforing water change
Var4 = 0 #variable to turn off return pump and lockout ATO as container empty and hasnt refilled tank properly
H = 0
M = 0
CON = 300 #container on, time to wait to partial fill container to be able to clean (240)
CLEAN = 200 #time to wait while container is cleaning (60)
MIX = 7200 #Time to pause to leave mixing pump running (1800 = 30Mins 7200 = 2Hrs)
wait = 30 #Dosing time run time in seconds (214.2)(320)
tank = 0
per = 1
perA = 1
pump = 1
run = 3.57
runA = 1
rund = 1
runM = 1
timer = None
#paper = paper()
#Change = Changer()

app = Flask(__name__)
now = time.strftime("%H:%M")
goA = "9:00" #Water change trigger time, program prompt for trigger time at start
goB = "18:00" #Water change trigger time, program prompt for trigger time at start
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Define raspberry pi input pin names
SW1 = 14 #Go button
SW2 = 15 #Dosing pump manual on
SW3 = 16 #Cleaning cycle start
SW4 = 23 #Manual trigger for water change cycle
Float1 = 27 #Float to detect container full
Float2 = 22 #Float to detect container empty
Float3 = 21 #Float for ATO
#Define raspberry pi output pin names
Sol1 = 4 #Solenoid valve for filling container
Sol2 = 18 #Solenoid valve for controlling emptying container
Sol3 = 13 #Solenoid valve for topping up tank (ATO)
MixP = 26 #Pump for mixing salt water in container and to clean tank)
EmPump = 19 #Pump on line to empty container (Used in cleaning cycle)
Dos1 = 5 #Pump IN Salt Water
Dos2 = 6 #Pump OUT Tank Water

# Set button and PIR sensor pins as an input
GPIO.setup(Dos1, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(Dos2, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(Sol3, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(Sol1, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(Sol2, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(EmPump, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(MixP, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(SW1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW3, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Float3, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Float1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Float2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW4, GPIO.IN, pull_up_down = GPIO.PUD_UP)


@app.route("/")
def index():
	# Read Sensors Status
    Float1Sts = GPIO.input(Float1)
    Float3Sts = GPIO.input(Float3)
    Dos1Sts = GPIO.input(Dos1)
    Dos2Sts = GPIO.input(Dos2)
    Sol3Sts = GPIO.input(Sol3)
    templateData = {
      'title' : 'AquaPi Status!',
	  'Container'  : Float1Sts,
	  'ATO'  : Float3Sts,
	  'Dos1'  : Dos1Sts,
	  'Dos2'  : Dos2Sts,
      'ATO1'  : Sol3Sts
      }
    t = threading.Thread(target=ATO)
    t.start()
    t = threading.Thread(target=Go)
    t.start()
    return render_template('index1.html', **templateData)

@app.route("/transmit/<action>")
def transmit(action):
    if action == 'Changer':
        print("Running Change Script")
        t = threading.Thread(target=Change)
        t.start()
    elif action == 'Clean':
        print("Running Clean Script")
        t = threading.Thread(target=Clean)
        t.start()

    return redirect(url_for('index'))

    # Read Sensors Status
    Float1Sts = GPIO.input(Float1)
    Float3Sts = GPIO.input(Float3)
    Dos1Sts = GPIO.input(Dos1)
    Dos2Sts = GPIO.input(Dos2)
    Sol3Sts = GPIO.input(Sol3)
    templateData = {
      'title' : 'AquaPi Status!',
	  'Container'  : Float1Sts,
	  'ATO'  : Float3Sts,
	  'Dos1'  : Dos1Sts,
	  'Dos2'  : Dos2Sts,
      'ATO1'  : Sol3Sts
      }
    return render_template('index1.html', **templateData)

def Clean(): #Cleaning process to give container and clean and drain down
    if Var2 == 0:
        #paper.clean()
        GPIO.output(4, GPIO.LOW)
        print("Part filling contrainer to clean")
        time.sleep(CON)
        GPIO.output(4, GPIO.HIGH)
        print("Container part filled for cleaning")
        time.sleep(0.5)
        GPIO.output(26, GPIO.LOW)
        print("Mixing pump on to clean")
        time.sleep(CLEAN)
        print("Container cleaned emptying")
        GPIO.output(18, GPIO.LOW)
        GPIO.output(19, GPIO.LOW)
        time.sleep(CON/4)
        GPIO.output(26, GPIO.HIGH)
        print("Mix pump turned off waiting for container to empty")
        time.sleep(CON)
        GPIO.output(18, GPIO.HIGH)
        GPIO.output(19, GPIO.HIGH)
        print("Container empty ready for salt and refill")
        #paper.empty()


def Change():
    if Var1 == 0 and Var2 == 1:
        global Var3
        Var3 = 1
        print("Starting water change")
        GPIO.output(6, GPIO.LOW)
        print("Removing aquarium water")
        #paper.remove()
        time.sleep(wait)
        GPIO.output(6, GPIO.HIGH)
        print("Done!")
        time.sleep(2)
        GPIO.output(5, GPIO.LOW)
        print("Topping up with salt water")
        #paper.fresh()
        Refill()

schedule.every(30).minutes.do(Change)


def Refill(): #Fill sump back up following first phase of water change
    global Var3
    while True:
        if Var3 == 1 and GPIO.input(21) == True:
            GPIO.output(5, GPIO.HIGH)
            print("Done!")
            print("Water change complete - same again tomorrow :-) ")
            Var3 = 0
            #paper.updateDisplayBottom()

def ATO(): #Top up evaporated water
    global Var3
    global Var4
    while True:
        if Var3 == 0 and Var4 == 0 and GPIO.input(21) == False:
            time.sleep(0.75)
            print("Tank Water Low")
            print("Topping up")
            GPIO.output(13, GPIO.LOW)
            time.sleep(30)
            #paper.updateDisplayTop()
        else:
            GPIO.output(13, GPIO.HIGH)
'''
def Run():

    #Manually trigger for water change cycle
    print("Manually triggered water change")
    time.sleep(1)
    t = threading.Thread(target=Change)
    t.start()
'''
GPIO.add_event_detect(23, GPIO.FALLING, bouncetime=200)

if GPIO.event_detected(23):
    print("Manually triggered water change")
    time.sleep(1)
    t = threading.Thread(target=Change)
    t.start()

def Go():
    while True:

        schedule.run_pending()
        time.sleep(0.5)


'''
        #Cleaning process to give container and clean and drain down
        if GPIO.input(16) == False:
            print("Button Pressed")
            print("Running Clean Script")
            t = threading.Thread(target=Clean)
            t.start()

#schedule.every().day.at(goA).do(Change)
#schedule.every().day.at(goB).do(Change)
#schedule.every(2).days.do(Mix)
#schedule.every(30).minutes.do(Change)
#schedule.every().hour.do(job)
#schedule.every().day.at("10:30").do(job)
#schedule.every(5).to(10).days.do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)
'''
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
   ATO



'''
    #Purge in line
    #Manually Run Dosing in pump to purge line
    if (Var3 == 0 and GPIO.input(15) == False):
        GPIO.output(5, GPIO.LOW)
        print("Manual pump on")
        time.sleep(1)
    elif (Var3 == 0 and GPIO.input(15) == True):
        GPIO.output(5, GPIO.HIGH)

        #Fill process
        #Start process pushing SW1 to trigger container filling
    if (GPIO.input(14) == False and Var2 == 0): #Switch input to start filling Var2 = 0 to prevent button being pushed at later date while doing scheduled water changes
        #paper.fill()
        GPIO.output(4, GPIO.LOW)
        print("In Solenoid Opened Waiting until full")
        Var1 = 1 #Variable to trigger solenoid off when tank full
        time.sleep(1)
            #Mixing process
        #Once container full triggered by Float1 solenoid closed and pixing pump turned on
    if Var1 == 1 and GPIO.input(27) == True:
        GPIO.output(4, GPIO.HIGH)
        print("In solenoid closed proceeding to mix")
        time.sleep(5)
        #paper.mix()
        GPIO.output(26, GPIO.LOW)
        print("Mixing Started")
        time.sleep(MIX)
        GPIO.output(26, GPIO.HIGH)
        print("Mixing Complete")
        #paper.ready()
        Var1 = 0 #Lockout
        Var2 = 1 #Allow system to change
        Var4 = 0 #disable pump lockout
        print(Var1 , Var2)
        print(goA)
        print(goB)
        print(now)

            #Empty container releasing lockout preventing accidental fill trigger call before tank is fully empty
    if GPIO.input(22) == False and Var2 == 1:
        paper.empty()
        print("Container Empty Press Button 3 (16) to trigger cleaning")
        print("Or put in more salt and trigger filling again (14)")
        print("Releasing Lockout")
        Var2 = 0

            #ATO to top up evaporated Water


    if Var3 == 1 and GPIO.input(21) == True:
        GPIO.output(5, GPIO.HIGH)
        print("Done!")
        print("Water change complete - same again tomorrow :-) ")
        Var3 = 0
        #paper.updateDisplayBottom()

    if Var3 == 1 and GPIO.input(22) == False and GPIO.output(5,True):
        Var4 = 1
'''
