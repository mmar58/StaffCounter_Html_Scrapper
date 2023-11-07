#!C:\Python312\Python.exe
from bs4 import BeautifulSoup
import sys,cgi
from datetime import date
import mysql.connector as connector
mydb=connector.connect(
    host="localhost",
    username="root",
    password="123456",
    database="job_report"
)
sys.path.append("K:/MMARPythonLibrary")
from stringLib import stringFormatter
print("Content-Type: text/html\n\n")
def convertToTime(timeText):
    data=timeText.split(":")
    totalTimeInSec=(int(data[0])*60+int(data[1]))*60+int(data[2])
    return totalTimeInSec
# Time maintaining options
startingTimeSet = False
startingTimeText = ""
startTime = 0
lastTimeAccessed = 0
# Result variables
totalWorkedTime = 0
totalWorkedTimeNote = ""
dateText=[]
cursor=mydb.cursor()
def setStartingTime(theTime):
    global startTime,lastTimeAccessed,startingTimeSet
    startTime = theTime
    lastTimeAccessed=theTime
    startingTimeSet=True

def addstartingTimeText(startText,endText,timeDifference):
    global totalWorkedTimeNote
    if totalWorkedTimeNote == "":
        totalWorkedTimeNote+=startText+"-"+endText+"#"+str(timeDifference)
    else:
        totalWorkedTimeNote += "\n"+startText + "-" + endText + "#" + str(timeDifference)

def scrapWorkTime(curTime):
    global startTime,startingTimeText,startingTimeSet,lastTimeAccessed,totalWorkedTime,totalWorkedTimeNote,dateText
    dateText=curTime.split("-")
    print(curTime)
    soup = BeautifulSoup(
        open("C:/Program Files (x86)/StaffCounter/logs/USER/"+curTime+".htm", "r", encoding="utf-8").read())
    all_p = soup.findAll("p")
    for i in range(len(all_p)):
        if (i == 0):
            "j"
        elif (i == 1):
            if (all_p[i].text == "Monitoring resumed by the user"):
                timeDistance = convertToTime(all_p[i]["time"])
                timeData = all_p[i]["time"].split(":")
                if timeData[0] == "23":
                    setStartingTime(0)
                    startingTimeText = "00:00:00"
                else:
                    setStartingTime(convertToTime(all_p[i]["time"]))
                    startingTimeText = all_p[i]["time"]
            else:
                timeDistance = convertToTime(all_p[i]["time"])
                timeData = all_p[i]["time"].split(":")

                if timeDistance < 20 * 60 or timeData[0] == "23":
                    setStartingTime(0)
                    startingTimeText = "00:00:00"
                else:
                    setStartingTime(timeDistance)
                    startingTimeText = all_p[i]["time"]
        else:
            temptime = convertToTime(all_p[i]["time"])
            if startingTimeSet:
                if all_p[i].text == "Monitoring stopped by the user":
                    startingTimeSet = False
                    timedifference = temptime - startTime
                    totalWorkedTime += timedifference
                    lastTimeAccessed = temptime
                    addstartingTimeText(startingTimeText, all_p[i]["time"], timedifference)

                else:
                    if i == len(all_p) - 1:
                        if 24 * 60 * 60 - temptime < 16 * 60:
                            startingTimeSet = False
                            timedifference = 24 * 60 * 60 - startTime
                            totalWorkedTime += timedifference
                            addstartingTimeText(startingTimeText, "24:00:00", timedifference)
                        else:
                            if lastTimeAccessed>temptime:
                                temptime=lastTimeAccessed
                            startingTimeSet = False
                            timedifference = temptime - startTime
                            totalWorkedTime += timedifference
                            addstartingTimeText(startingTimeText, all_p[i]["time"], timedifference)
                    elif temptime < startTime:
                        startTime = temptime
                        lastTimeAccessed = temptime
            else:
                if all_p[i].text == "Monitoring resumed by the user" or temptime > lastTimeAccessed:
                    setStartingTime(temptime)
                    startingTimeText = all_p[i]["time"]
def convertSecondsIntoTimeText(tempseconds):
    tempMinute = int(tempseconds / 60)
    seconds = stringFormatter.getIntInDoubleText(tempseconds - tempMinute * 60)
    tempHours = int(tempMinute / 60)
    minutes = stringFormatter.getIntInDoubleText(tempMinute - tempHours * 60)
    hours = stringFormatter.getIntInDoubleText(tempHours)
    return hours + ":" + minutes + ":" + seconds
def printInFormat():
    global totalWorkedTime,totalWorkedTimeNote,startingTimeSet,startingTimeText,startTime,lastTimeAccessed,dateText,\
        cursor
    totaltimeString=convertSecondsIntoTimeText(totalWorkedTime)
    print(totaltimeString)
    totaltimeData=totaltimeString.split(":")
    hour=totaltimeData[0]
    minute=totaltimeData[1]
    if(int(totaltimeData[2])>30):
        minute=str(int(minute)+1)
    thisDate=dateText[2]+"-"+ dateText[1]+"-"+dateText[0]
    cursor.execute("select * from dailywork	where date = '" + thisDate+ "'")
    result = cursor.fetchall()
    data=totalWorkedTimeNote.split("\n")
    print(result)
    detailedWork=""
    for line in data:
        linedata=line.split("#")
        if len(linedata)>1:
            detailedWork+=linedata[0]+" "+convertSecondsIntoTimeText(int(linedata[1]))+"\n"
    print(detailedWork)
    if result==[]:
        #print("insert into dailywork (date,hour,minutes) values (%s,%s,%s)", (thisDate, hour, minute))
        cursor.execute("insert into dailywork (date,hour,minutes) values (%s,%s,%s)",(thisDate,hour,minute))
        mydb.commit()
    else:
        #print(
         #   "update dailywork set hour='" + hour + "', minutes = '" + minute + "' where date='" + thisDate + "'")
        cursor.execute("update dailywork set hour='"+hour+"', minutes = '"+minute+"' where date='"+thisDate+"'")
        print("updated")
        mydb.commit()
    # print(cursor)
    # print(mydb)
    startingTimeSet = False
    startingTimeText = ""
    startTime = 0
    lastTimeAccessed = 0
    # Result variables
    totalWorkedTime = 0
    totalWorkedTimeNote = ""
form = cgi.FieldStorage()
days=form.getvalue("dates")
if(days==None):
    scrapWorkTime(date.today().strftime("%d-%m-%Y"))
    printInFormat()
else:
    daysdata=days.split(",")
    for day in daysdata:
        scrapWorkTime(day)
        printInFormat()


