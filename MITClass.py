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

def addSuggestions(speech = "", suggestions = []):
    suggestionsTitles = []
    for item in suggestions:
        suggestionsTitles.append({"title":item})
    return {
   "google":{
      "expect_user_response":True,
      "rich_response":{
         "items":[
            {
               "simpleResponse":{
                  "textToSpeech":speech,
                  "displayText":speech
               }
            }
         ],
         "suggestions": suggestionsTitles
      }
   }
}

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
    print("Validating Response")
    if 'errorDesc' in response or 'StackTrace' in response or 'errorMessage' in response:
        return True
    return False

def lookupClass(req):
    speech =  "Lookup  class"
    contexts = req.get("result").get("contexts")
    fullQuery = req.get("result").get("resolvedQuery")
    suggestions = []
    if fullQuery.lower() == "Look up a class".lower()  or fullQuery.lower() == "Look up class".lower():
        speech = "To look up a class, simply say 'Look up class' then the class number."
        return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": contexts,
        "source": "webhook"
        }
    parameters = req.get("result").get("parameters")
    classNumberFound = False
    classContextFound = False
    for context in contexts:
        if context.get("name", "") == "class-number-found" and context.get("parameters", {}).get("number", "") != "":
            classContext = context
            classNumber = context.get("parameters", {}).get("number", "")
            print("Context classnumber found {}".format(classNumber))
            classContextFound = True
            classNumberFound = True
    if parameters.get("number", "") != "":
        classNumber = parameters.get("number")
        classNumberFound = True
        print("Parameter Number classnumber found {}".format(classNumber))
    if parameters.get("newnumber", "") != "":
        classNumber = parameters.get("newnumber")
        classNumberFound = True
        print("Parameter NewNumber classnumber found {}".format(classNumber))

    classInfoFound = False
    classInfoType  = ""
    if classContextFound and classContext.get("parameters", {}).get("ClassInfoTypes", "") != "":
        classInfoType = classContext.get("parameters", {}).get("ClassInfoTypes", "")
        classInfoFound = True
    if parameters.get("ClassInfoTypes", "") != "":
        classInfoType = parameters.get("ClassInfoTypes")
        classInfoFound = True
    
    if classNumberFound:
        print("Class number found {}".format(classNumber))
        if classInfoFound:
            print("Class Info Found {}".format(classInfoType))
            suggestions = ["name", "instructors", "longer description", "location", "number of units"]
            if classInfoType == "Instructor":
                q = getInstructor(classNumber)
                if q != "Not Found":
                    speech = "{} is taught by {}.  Do you want any more information?  If so, say the information type that you want.".format(getSubjTitle(classNumber), q)
                    updateContext(contexts, "endcontext", 1, {})
                    suggestions += ["I'm Done"]
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            elif classInfoType == "Title":
                q = getSubjTitle(classNumber)
                if q != "Not Found":
                    speech = "{} is {}.  Do you want any more information?  If so, say the information type that you want.".format(classNumber, q)
                    suggestions += ["I'm Done"]
                    updateContext(contexts, "endcontext", 1, {})
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            elif classInfoType == "Description":
                q = getDescp(classNumber)
                if q != "Not Found":
                    speech = "Here's the long description of {}.  {}.  Do you want any more information?  If so, say the information type that you want.".format(getSubjTitle(classNumber), q)
                    suggestions += ["I'm Done"]
                    updateContext(contexts, "endcontext", 1, {})
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            elif classInfoType == "Units":
                q = getUnits(classNumber)
                if q != "Not Found":
                    speech = "{} is {} units.  Do you want any more information?  If so, say the information type that you want.".format(getSubjTitle(classNumber), q)
                    suggestions += ["I'm Done"]
                    updateContext(contexts, "endcontext", 1, {})
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            elif classInfoType == "Room":
                q = getRoomNumber(classNumber)
                if q != "Not Found":
                    speech = "{} is located in {}.  Do you want any more information?  If so, say the information type that you want.".format(getSubjTitle(classNumber), q)
                    suggestions += ["I'm Done"]
                    updateContext(contexts, "endcontext", 1, {})
                else:
                    speech = "{} could not be found.  Try searching for another class.".format(classNumber)
            
        else:
            r = getClassInfo(classNumber)
            if validateResponse(r.json()):
                speech = "{} could not be found as a class.  You can find the name, instructors, longer description, location, or number of units for a different class.  Just ask away!".format(classNumber)
                suggestions = ["Look up a class", "Look up a person"]
            else:
                speech = "You can find the name, instructors, longer description, location, or number of units for the class {}.  Just ask for what you want!".format(classNumber)
                suggestions = ["name", "instructors", "longer description", "location", "number of units"]
    else:
        if classInfoFound:
            speech = "To get the {} of a class, just let us know the class.".format(classInfoType.lowercase())
        else:
            speech = "You can find the name, instructors, longer description, location, or number of units of a class.  Just ask away!"
    print("------ Final Speech -------")
    print(speech)
    data = addSuggestions(speech, suggestions)
    return {
        "speech": speech,
        "displayText": speech,
        "data": data,
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
    instructors = r.json()['item']['instructors']
    if "<br>" in instructors:
        twoPart = instructors.split("<br>")
        fall = twoPart[0]
        spring = twoPart[1]
        if "Fall: " in fall:
            fall = fall[fall.index("Fall: ") + 5:]
        if "Spring: " in spring:
            spring = spring[spring.index("Spring: ") + 8:]
        instructors = "{} in the fall.  {} in the spring".format(fall, spring)

    return instructors

def getUnits(classnum):
    r = getClassInfo(classnum)
    if validateResponse(r.json()):
        return 'Not Found'
    unitDistribution = r.json()['item']['units']
    units = 0
    a = unitDistribution.split("-")
    if " " in a[-1]:
        a[-1] = a[-1][:a[-1].index(" ")]
    print(a) 
    try:
        for i in a:
            units += int(i)
    except:
        return "an unknown number of "
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
def updateContext(contexts, name, lifespan, parameters):
    updated = False
    for i in range(len(contexts)):
        if contexts[i].get("name", "").lower() == name.lower():
            contexts[i]["lifespan"] = lifespan
            contexts[i]["parameters"] = parameters
            updated = True
    if updated == False:
        contexts.append({"name":name.lower(),"lifespan":lifespan, "parameters":parameters})

test = {
  "id": "6206af22-566c-4c50-9119-b9f218ffdc8a",
  "timestamp": "2017-08-04T01:12:15.965Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "look up class 183",
    "action": "LookUpClass",
    "actionIncomplete": False,
    "parameters": {
      "ClassInfoTypes": "",
      "number": "183"
    },
    "contexts": [
      {
        "name": "lookupclass-followup",
        "parameters": {
          "number": "183",
          "number.original": "183",
          "ClassInfoTypes": "",
          "ClassInfoTypes.original": ""
        },
        "lifespan": 2
      },
      {
        "name": "class-number-found",
        "parameters": {
          "number": "183",
          "number.original": "183",
          "ClassInfoTypes": "",
          "ClassInfoTypes.original": ""
        },
        "lifespan": 5
      }
    ],
    "metadata": {
      "intentId": "6348c5a5-3b25-492b-b9fe-a898d4b12fa0",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 720,
      "intentName": "Look Up Class"
    },
    "fulfillment": {
      "speech": "You can find the name, instructors, longer description, or number of units for the class 183.  Just ask away!",
      "source": "webhook",
      "displayText": "You can find the name, instructors, longer description, or number of units for the class 183.  Just ask away!",
      "messages": [
        {
          "type": 0,
          "speech": "You can find the name, instructors, longer description, or number of units for the class 183.  Just ask away!"
        }
      ]
    },
    "score": 1
  },
  "status": {
    "code": 200,
    "errorType": "success"
  },
  "sessionId": "6693c855-d7b1-4595-bb0b-d63c5d1af277"
}
# lookupClass(test)
