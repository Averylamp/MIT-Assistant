"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import requests
import json
import datetime


def getClassInfo(classnum):
    print("Finding class - {}".format(classnum))
    headers = {'client_id': '89bf245efe1f4d54b5176ce68ff5da83', 'client_secret': "fd0ff77789534319B29FE6EE400291F2"}
    now = datetime.datetime.now()
    currentTerm = "{}".format(now.year)
    if now.month >= 8:
        currentTerm += "FA"
    else:
        currentTerm += "SP"
    r = requests.get("https://mit-public.cloudhub.io/coursecatalog/v2/terms/{}/subjects/{}".format(currentTerm, classnum), headers = headers)
    return r

def validateResponse(response):
    if 'errorDesc' in response or 'StackTrace' in response:
        return True
    return False

def lookupClass(req):
    speech =  "Lookup  class"
    contexts = req.get("result").get("contexts")

    parameters = req.get("result").get("parameters")
    classNumberFound = False
    classContextFound = False
    for context in contexts:
        if context.get("name", "") == "class-number-found" and context.get("parameters", {}).get("number", "") != "":
            classContext = context
            classNumber = context.get("parameters", {}).get("number", "")
            classContextFound = True
            classNumberFound = True
    if parameters.get("number") != "":
        classNumber = parameters.get("number")
        classNumberFound = True
    if parameters.get("newnumber") != "":
        classNumber = parameters.get("newnumber")
        classNumberFound = True

    classInfoFound = False
    classInfoType  = ""
    if parameters.get("ClassInfoTypes") != "":
        classInfoType = parameters.get("ClassInfoTypes")
        classInfoFound = True
    if classContextFound and classContext.get("parameters", {}).get("ClassInfoTypes", "") != "":
        classInfoType = classContext.get("parameters", {}).get("ClassInfoTypes", "") != ""
        classInfoFound = True
    if classNumberFound:
        print("Class number found {}".format(classNumber))
        if classInfoFound:
            if classInfoType == "Instructor":
                q = getInstructor(classNumber)
                if q != "Not Found":
                    speech = "{} is taught by {}.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            elif classInfoType == "Title":
                q = getSubjTitle(classNumber)
                if q != "Not Found":
                    speech = "{} is {}.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            elif classInfoType == "Description":
                q = getDescp(classNumber)
                if q != "Not Found":
                    speech = "The long description of {} is {}.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            elif classInfoType == "Units":
                q = getUnits(classNumber)
                if q != "Not Found":
                    speech = "{} is {} units.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            elif classInfoType == "Room":
                q = getRoomNumber(classNumber)
                if q != "Not Found":
                    speech = "{} is located in {}.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
        else:
            r = getClassInfo(classNumber)
            if validateResponse(r.json()):
                speech = "{} could not be found as a class.  You can find the name, instructors, longer description, or number of units for a different class.  Just ask away!".format(classNumber)
            else:
                speech = "You can find the name, instructors, longer description, or number of units for the class {}.  Just ask away!".format(classNumber)
    else:
        if classInfoFound:
            speech = "To get the {} of a class, just let us know the class.".format(classInfoType.lowercase())
        else:
            speech = "You can find the name, instructors, longer description, or number of units of a class.  Just ask away!"

    print(req.get("result").keys())
    print(" Recieved Context - {}".format(context))
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": contexts,
        "source": "webhook"
    }


def getSubjTitle(classnum):
    r = getClassInfo(classnum)
    if validateResponse(r.json()):
        return 'Not Found'
    subjtitle = r.json()["item"]["title"]
    return subjtitle

def getDescp(classnum):
    r = getClassInfo(classnum)
    if validateResponse(r.json()):
        return 'Not Found'
    desc = r.json()['item']['description']
    return desc

def getInstructor(classnum):
    r = getClassInfo(classnum)
    if validateResponse(r.json()):
        return 'Not Found'
    instructors = r.json()['item']['instrucotrs']
    return instructors

def getUnits(classnum):
    r = getClassInfo(classnum)
    if validateResponse(r.json()):
        return 'Not Found'
    unitDistribution = r.json()['item']['instrucotrs']
    units = 0
    a = instructor.split("-")
    for i in a:
        units += int(i)
    return units


def getRoomNumber(class_name):
    headers = {"Content-Type":"application/json"}
    r = requests.get("http://54.84.137.194/index.aspx/GetSchedule?coursesString="+ class_name + "&preferences=", headers=headers)
    print(r.json())
    if validateResponse(r.json()):
        return 'Not Found'
    result_string = r.json().get('d', "Not Found")
    if result_string == "Not Found":
        return "Not Found"
    result = json.loads(result_string)
    index = -1
    for i in range(len(result)):
        if result[i][0]['name'] == class_name:
            index = i
            break
    if index == -1:
        return None

    room = result[index]
    lectures = []
    for j in range(len(room)):
        if room[j]['type'] == 'lec':
            lectures.append(room[j])
    loc_time = [] #[['Tuesday','11','12','54-100'],['Thursday','11','12','54-100']]
    for k in range(len(lectures)):
        lec = []
        if lectures[k]['cellNum'] == 1:
            lec.append('Monday')
        elif lectures[k]['cellNum'] == 2:
            lec.append('Tuesday')
        elif lectures[k]['cellNum'] == 3:
            lec.append('Wednesday')
        elif lectures[k]['cellNum'] == 4:
            lec.append('Thursday')
        elif lectures[k]['cellNum'] == 5:
            lec.append('Friday')

        #8: 1, 9: 3, 10: 5 etc.
        start = ((lectures[k]['rowNum'] - 1) / 2) + 8
        end = start + lectures[k]['rowSpan'] * 0.5
        adjust_start = start
        adjust_end = end
        if adjust_start > 12.5:
            adjust_start -= 12
        if adjust_end > 12.5:
            adjust_end -= 12
        lec.append(adjust_start)
        lec.append(adjust_end)
        lec.append(lectures[k]['location'])
        loc_time.append(lec)

    return str(lectures[0]['location'])

