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

def addContext(context, new_context):
    replaced = False
    for i in range(len(context)):
        if context[i]["name"] == new_context["name"]:
            context[i] = new_context
            replaced = True
    if not replaced:
        context.append(new_context)

def lookupClass(req):
    speech =  "Lookup  class"
    context = req.get("result").get("contexts")

    parameters = req.get("result").get("parameters")
    if parameters.get("number") != "":
        print("Class number found {}".format(parameters.get("number")))
        classNumber = parameters.get("number")
        if parameters.get("ClassInfoTypes") != "":
            classInfoType = parameters.get("ClassInfoTypes")
            if classInfoType == "Instructor":
                q = getFallInst(classNumber)
                if q != "Not Found":
                    speech = "{} is taught by {}.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class."
            elif classInfoType == "Title":
                q = getSubjTitle(classNumber)
                if q != "Not Found":
                    speech = "{} is {}.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class."
            elif classInfoType == "Description":
                q = getDescp(classNumber)
                if q != "Not Found":
                    speech = "The long description of {} is {}.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class."
            elif classInfoType == "Units":
                q = getUnits(classNumber)
                if q != "Not Found":
                    speech = "{} is {} units.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class."
            elif classInfoType == "Room":
                q = getRoomNumber(classNumber)
                if q != "Not Found":
                    speech = "{} is located in {}.".format(classNumber, q)
                else:
                    speech = "{} could not be found.  Try searching for another class."
        else:
            speech = "You can find the name, instructors, longer description, or number of units of a class.  Just ask away!"

        # numberContext = {"name":"class-number-found", "lifespan":7, "parameters":{"number":classNumber}}
        # addContext(context, numberContext)

    print(req.get("result").keys())
    print(" Recieved Context - {}".format(context))
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": context,
        "source": "apiai-weather-webhook-sample"
    }

def validateResponse(response):
    if 'errorDesc' in response or 'StackTrace' in response:
        return True
    return False

def getSubjTitle(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    # print(classnum)
    r = requests.post("https://courseroad.mit.edu/ajax.php", data = parameters)
    if validateResponse(r.json()):
        return 'Not Found'
    subjtitle = r.json()['subject_title']
    return subjtitle

def getDescp(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    r = requests.post("https://courseroad.mit.edu/ajax.php?getClass=1&subjectId=" + classnum +  "&year=2017", data = parameters)
    if validateResponse(r.json()):
        return 'Not Found'
    desc = r.json()['desc']
    return desc

def getFallInst(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    r = requests.post("https://courseroad.mit.edu/ajax.php?getClass=1&subjectId=" + classnum +  "&year=2017", data = parameters)
    if validateResponse(r.json()):
        return 'Not Found'
    fall = r.json()['fall_instructors']
    return fall

def getSpringInst(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    r = requests.post("https://courseroad.mit.edu/ajax.php?getClass=1&subjectId=" + classnum +  "&year=2017", data = parameters)
    if validateResponse(r.json()):
        return 'Not Found'
    spring = r.json()['spring_instructors']
    return spring

def getUnits(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    r = requests.post("https://courseroad.mit.edu/ajax.php?getClass=1&subjectId=" + classnum +  "&year=2017", data = parameters)
    if validateResponse(r.json()):
        return 'Not Found'
    units = r.json()['total_units']
    return str(units)


def getRoomNumber(class_name):
    headers = {"Content-Type":"application/json"}
    r = requests.get("http://54.84.137.194/index.aspx/GetSchedule?coursesString="+ class_name + "&preferences=", headers=headers)
    print(r.json())
    if validateResponse(r.json()):
        return 'Not Found'
    result_string = r.json()['d']
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

