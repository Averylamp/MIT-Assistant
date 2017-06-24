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



def lookupClass(req):
    
    speech =  "Lookup  class"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def validateResponse(response):
    if 'errorDesc' in response:
        return True
    return False

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def getSubjTitle(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    print(classnum)
    r = requests.post("https://courseroad.mit.edu/ajax.php", data = parameters)
    if validateResponse(r.json()):
        return 'not found in our database'
    subjtitle = r.json()['subject_title']
    return subjtitle

def getDescp(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    r = requests.post("https://courseroad.mit.edu/ajax.php?getClass=1&subjectId=" + classnum +  "&year=2017", data = parameters)
    if validateResponse(r.json()):
        return 'not found in our database'
    desc = r.json()['desc']
    return desc

def getFallInst(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    r = requests.post("https://courseroad.mit.edu/ajax.php?getClass=1&subjectId=" + classnum +  "&year=2017", data = parameters)
    if validateResponse(r.json()):
        return 'not found in our database'
    fall = r.json()['fall_instructors']
    return fall

def getSpringInst(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    r = requests.post("https://courseroad.mit.edu/ajax.php?getClass=1&subjectId=" + classnum +  "&year=2017", data = parameters)
    if validateResponse(r.json()):
        return 'not found in our database'
    spring = r.json()['spring_instructors']
    return spring

def getUnits(classnum):
    parameters = {'getClass': '1', 'subjectId': classnum, 'year' : '2017'}
    r = requests.post("https://courseroad.mit.edu/ajax.php?getClass=1&subjectId=" + classnum +  "&year=2017", data = parameters)
    if validateResponse(r.json()):
        return 'not found in our database'
    units = r.json()['total_units']
    return str(units)

import requests
import json

def getRoomNumber(class_name):
    headers = {"Content-Type":"application/json"}
    r = requests.get("http://54.84.137.194/index.aspx/GetSchedule?coursesString="+ class_name + "&preferences=", headers=headers)
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


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to MIT Classes.  Ask about any class at MIT"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Ask MIT Courses about any MIT Classes.  Please make sure to use the format number point number, specifically stating any zeros.  For example, Ask MIT Classes what six point zero zero six is. MIT Courses can also tell you the instructors for a course, a longer description of the course, or the number of units a course takes up."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thanks for using MIT Classes.  Goodbye"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

####################################################################
################################ Helper Funcs ######################
####################################################################

def getClassNumberAsString(intent):
    try :
	    a = float(intent['slots']['CourseNumber']['value'])
	    b = float(intent['slots']['ClassNumber']['value'])
    except:
	    return 'error'
    firstPart = str(intent['slots']['CourseNumber']['value'])
    dot = '.'
    secondPart = str(intent['slots']['ClassNumber']['value'])
    return firstPart + dot + secondPart


####################################################################
################################ HANDLERS ##########################
####################################################################

def handleClassFullNameIntent(intent, session):
    output = ""
    if 'ClassNumber' in intent['slots'] and 'CourseNumber' in intent['slots']:
        print(intent['slots'])
        print(intent['slots']['CourseNumber'])
        classNumber = getClassNumberAsString(intent)
        if classNumber == 'error':
            output = 'Unable to detect a course number'
            return build_response(session, build_speechlet_response("Class Name", output, output, True))
        output =  classNumber + " is " +  getSubjTitle(classNumber)
    return build_response(session, build_speechlet_response("Class Name", output, output, True))
        
def handleClassDescriptionIntent(intent, session):
    output = ""
    if 'ClassNumber' in intent['slots'] and 'CourseNumber' in intent['slots']:
        print(intent['slots'])
        print(intent['slots']['CourseNumber'])
        classNumber = getClassNumberAsString(intent)
        if classNumber == 'error':
            output = 'Unable to detect a course number'
            return build_response(session, build_speechlet_response("Class Description", output, "Class Description", True))
        output =  classNumber + " teaches you the following: " +  getDescp(classNumber)
    return build_response(session, build_speechlet_response("Class Description", output, "Class Description", True))

def handleClassUnitsIntent(intent, session):
    output = ""
    if 'ClassNumber' in intent['slots'] and 'CourseNumber' in intent['slots']:
        classNumber = getClassNumberAsString(intent)
        if classNumber == 'error':
            output = 'Unable to detect a course number'
            br = build_speechlet_response("Class Units", output, output, True)        
            return build_response(session, br)
        output =  classNumber + " is a " +  getUnits(classNumber) + " unit class"
    br = build_speechlet_response("Class Units", output, output, True)
    return build_response(session, br)


def handleClassRoomNumberIntent(intent, session):
    output = ""
    if 'ClassNumber' in intent['slots'] and 'CourseNumber' in intent['slots']:
        classNumber = getClassNumberAsString(intent)
        if classNumber == 'error':
            output = 'Unable to detect a course number'
            return build_response(session, build_speechlet_response("Class Room Number", output, output, True))
        output =  classNumber + " is in " + getRoomNumber(classNumber)
    br = build_speechlet_response("Class Room Number", output, output, True)
    return build_response(session, br)

def handleClassInstructorIntent(intent, session):
    output = ""
    if 'ClassNumber' in intent['slots'] and 'CourseNumber' in intent['slots']:
        classNumber = getClassNumberAsString(intent)
        if classNumber == 'error':
            output = 'Unable to detect a course number'
            return build_response(session, build_speechlet_response("Class Instructor", output, output, True))
        if len(getFallInst(classNumber)) > 1: 
            classInstructor = getFallInst(classNumber)
        else:
            classInstructor = getSpringInst(classNumber)
        output = "That class is taught by Professor " + classInstructor
    return build_response(session, build_speechlet_response("Class Instructor", output, output, True))

    
# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    r = requests.get("http://google.com")
    
    # Dispatch to your skill's intent handlers
    if intent_name == "GetClassDescription":
        return handleClassDescriptionIntent(intent, session)
    elif intent_name == "GetClassInstructor":
        return handleClassInstructorIntent(intent, session)
    elif intent_name == "GetClassFullName":
        return handleClassFullNameIntent(intent, session)
    elif intent_name == "GetClassUnits":
        return handleClassUnitsIntent(intent, session)
    elif intent_name == "GetClassRoomNumber":
        return handleClassRoomNumberIntent(intent, session)    
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
