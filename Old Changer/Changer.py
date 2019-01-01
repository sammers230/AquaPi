#from EmulatorGUI import GPIO
import RPi.GPIO as GPIO
import datetime
import time
import schedule
#from epaper import paper

Var1 = 0 #variable to have system trigger mixing after filling container
Var2 = 0 #variable to lockout buttons to prevent premature program triggers while changing water etc
Var3 = 0 #variable to prevent ATO from topping up tank when perforing water change
Var4 = 0 #variable to turn off return pump and lockout ATO as container empty and hasnt refilled tank properly
H = 0
M = 0
CON = 300 #container on, time to wait to partial fill container to be able to clean (240)
CLEAN = 200 #time to wait while container is cleaning (60)
MIX = 7200 #Time to pause to leave mixing pump running (1800 = 30Mins 7200 = 2Hrs)
wait = 320 #Dosing time run time in seconds (214.2)
tank = 0
per = 1
perA = 1
pump = 1
run = 3.57
runA = 1
rund = 1
runM = 1
#paper = paper()

now = time.strftime("%H:%M")
goA = "9:00" #Water change trigger time, program prompt for trigger time at start
goB = "18:00" #Water change trigger time, program prompt for trigger time at start
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(5, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(6, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(13, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(4, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(18, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(19, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(26, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(14, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(15, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
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

# NOTE: Attempted to have an input to calculate how long to run water change pumps based on pump flow rate, percentage of water change and the aquarium size.
#       Will look at possibly readding this through flask in the rebuild.
#def Main():
 #   try:
#ML = input("Input dosing pump run time: ")

#tank = input("Tank size in litres: ")
#per = input("Percentage of water change: ")
#pump = input("Pump flor rate in litres per minue: ")

#per/100 = perA
#tank*per = runA
#runA/7 = rund
#rund/2 = runM
#runM/pump = run
#run*60 = wait

print("Pumps will run for "+str(run))
print("Minutes")
print("Which is "+str(wait))
print("Seconds")
#paper.Initial()
print (GPIO.input(22))

#goA = input("Insert 1st dosing trigger time: ")
#goB = input("Insert 2nd dosing trigger time: ")
print("Changer will run first at " +str(goA))
print("Changer will run second at " +str(goB))

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
        print("Topping up with salted water")
        #paper.fresh()

def Mix():
	print("Stirring Up Container")
	GPIO.output(26, GPIO.LOW)
	time.sleep(MIX)
	print("Stirring Complete")
	GPIO.output(26, GPIO.HIGH)


schedule.every().day.at(goA).do(Change)
schedule.every().day.at(goB).do(Change)
schedule.every(2).days.do(Mix)

while True:

    schedule.run_pending()
    time.sleep(0.5)

    #Purge in line
    #Manually Run Dosing in pump to purge line
    if (Var3 == 0 and GPIO.input(15) == False):
        GPIO.output(5, GPIO.LOW)
        print("Manual pump on")
        time.sleep(1)
    elif (Var3 == 0 and GPIO.input(15) == True):
	  GPIO.output(5, GPIO.HIGH)

    #Manually trigger for water change cycle
    if (GPIO.input(23) == False):
        print("Manually triggered water change")
        time.sleep(2)
        Change()

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
    if GPIO.input(22) == False  and Var2 == 1:
        #paper.empty()
        print("Container Empty Press Button 3 (16) to trigger cleaning")
        print("Or put in more salt and trigger filling again (14)")
        print("Releasing Lockout")
        Var2 = 0

            #Cleaning process to give container and clean and drain down
    if GPIO.input(16) == False and Var2 == 0:
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

            #ATO to top up evaporated Water
    if Var3 == 0 and Var4 == 0 and GPIO.input(21) == False:
        print("Tank Water Low")
        print("Topping up")
        GPIO.output(13, GPIO.LOW)
        time.sleep(30)
        #paper.updateDisplayTop()
    else:
        GPIO.output(13, GPIO.HIGH)

    if Var3 == 1 and GPIO.input(21) == True:
        GPIO.output(5, GPIO.HIGH)
        print("Done!")
        print("Water change complete - same again tomorrow :-) ")
        Var3 = 0
        #paper.updateDisplayBottom()

    if Var3 == 1 and GPIO.input(22) == False and GPIO.output(5,True):
        Var4 = 1
