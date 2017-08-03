from __future__ import print_function
import requests
import json
import sys

def lookupPerson(req):
    speech =  "Lookup  Person"
    contexts = req.get("result").get("contexts")

    parameters = req.get("result").get("parameters")
    fullQuery = req.get("result").get("resolvedQuery")
    print("Full Query: {}".format(fullQuery))
    firstNameFound = False
    lastNameFound = False
    initialLetterFound = False
    personContextFound = False
    guessedLastNameFound = False
    for context in contexts:
        if context.get("name", "") == "current-person" :
            personContext = context
            personContextFound = True
            if personContext.get("parameters", {}).get("given-name", "") != "":
                firstName = personContext.get("parameters", {}).get("given-name", "")
                firstNameFound = True
                print("First Name Found - {}".format(firstName))
            if personContext.get("parameters", {}).get("last-name", "") != "":
                lastName = personContext.get("parameters", {}).get("last-name", "")
                lastNameFound = True
                print("Last Name Found - {}".format(lastName))
            if personContext.get("parameters", {}).get("Initials", "") != "":
                initialLetterFound = personContext.get("parameters", {}).get("Initials", "")
                initialFound = True
                print("Initial Found - {}".format(initialLetterFound))
            personContext["test"] = {"hello": "there"}
    if parameters.get("given-name", "") != "":
        firstName = parameters.get("given-name", "")
        firstNameFound = True
    if parameters.get("last-name", "") != "":
        lastName = parameters.get("last-name", "")
        lastNameFound = True
    if parameters.get("Initials", "") != "":
        initialLetter = parameters.get("Initials", "")
        initialLetterFound = True

    if firstNameFound and not lastNameFound and not initialLetterFound:
        allQueryWords = str(fullQuery).lower().split(" ")
        for i in range(len(allQueryWords)):
            if allQueryWords[i] == firstName.lower() and i < len(allQueryWords) - 1:
                guessedLastName = allQueryWords[i + 1]
                guessedLastNameFound = True
                print("Guessed Last Name Found - {}".format(guessedLastName))

    bestGuessFormat = []
    foundIDs = set()
    foundNames = set()
    results = []
    foundResults = False
    if firstNameFound and (lastNameFound or guessedLastNameFound):
        if lastNameFound:
            bestGuessName = "{} {}".format(firstName, lastName)
        else:
            bestGuessName = "{} {}".format(firstName, guessedLastName)
        bestGuessFormat = ['first', 'last']
        q = lookup_person(bestGuessName)
        print("{} found - {} result".format(bestGuessName, len(q)))
        if len(q) >= 1:
            foundResults = True
            addToResults(results, q, foundIDs, foundNames)

    if lastNameFound and not foundResults:
        bestGuessName = "{}".format(lastName)
        bestGuessFormat = ['last']
        q = lookup_person(bestGuessName)
        print("{} found - {} result".format(bestGuessName, len(q)))
        if len(q) >= 1:
            foundResults = True
            addToResults(results, q, foundIDs, foundNames)

    if firstNameFound and not foundResults:
        if initialLetterFound:
            bestGuessName = "{} {}".format(firstName, initialLetter)
        else:
            bestGuessName = "{}".format(firstName)
        bestGuessFormat = ['last']
        q = lookup_person(bestGuessName)
        print("{} found - {} result".format(bestGuessName, len(q)))
        if len(q) >= 1:
            foundResults = True
            addToResults(results, q, foundIDs, foundNames)       
    if foundResults == False:
        speech = "No people found with that name. Please try again. "
        print("No results found")
        return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": contexts,
        "source": "webhook"
        }
    print(foundNames)
    # if len(foundNames) == 1 :
    #     speech = "Found {}.  What would you like to know about them?".format(foundNames[0])
    foundNamesArr = sorted(list(foundNames), key=lambda x: damerau_levenshtein_distance(bestGuessName, x))
    print(bestGuessName)
    print(foundNamesArr)
    if len(foundNamesArr) > 1:
        speech = "{} results found. ".format(len(foundNamesArr))
        if len(foundNamesArr) > 5:
            speech += "The first five are: " + getListString(foundNamesArr[:5]) + ". "
        else:
            speech += "They are: " + getListString(foundNamesArr) + ". "
        speech += "To confirm the person you are looking for say their name again"
    elif len(foundNamesArr) == 1:
        speech = "{} found. ".format(foundNamesArr[0])
        personResults = None
        for person in results:
            if person.get("name","") == foundNamesArr[0]:
                personResults = person
        optionsStr, options = choose_person_output(personResults)
        speech += optionsStr
        updateContext(contexts, "FoundPersonContext", 5, {"foundPerson":results,"foundOptions":options})


    contexts.append({"name":"QueryResultsContext", "lifespan":5,"parameters":{"foundPeople":results}})
    print("----------- Final response -------------")
    print(speech)
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": contexts,
        "source": "webhook"
    }
def lookupInformation(req):
    speech =  "Lookup  Person Information"
    contexts = req.get("result").get("contexts")
    parameters = req.get("result").get("parameters")


    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": contexts,
        "source": "webhook"
    }

def updateContext(contexts, name, lifespan, parameters):
    updated = False
    for i in range(len(contexts)):
        if contexts[i].get("name", "") == name:
            contexts[i]["lifespan"] = lifespan
            contexts[i]["parameters"] = parameters
            updated = True
    if updated == False:
        contexts.append({"name":name,"lifespan":lifespan, "parameters":parameters})


def addToResults(results, addition, foundIDs, foundNames):
    if len(addition) > 0:
        for person in addition:
            if person['id'] not in foundIDs:
                foundIDs.add(person['id'])
                foundNames.add(person['name'])
                results.append(person)

# --------------- Intents ------------------
def handleConfirmIntent(intent, old_session):
    output = ""
    should_end_session = False
    session = {}
    print("Confirming person Intent running")
    if 'PersonName' in intent['slots']:
        print(intent['slots']['PersonName'])
        personName = intent['slots']['PersonName']
        if 'value' in personName:
            personName = stripUnlikelyWords(personName['value'])
            print("Confirming person name {}".format(personName))
        else:
            output = "Invalid name, please try again"
            should_end_session = False
            return build_response(session, build_speechlet_response("Lookup Person", output, output, should_end_session))
        print(session)
        if "LookingForComfirmation" in old_session["attributes"]:
            print("Looking for Comfirmation found")
            if old_session["attributes"]["LookingForComfirmation"]:
                print("Looking for Comfirmation true")
                if "Current_Query_Results" in old_session["attributes"] and len(old_session["attributes"]["Current_Query_Results"]) > 1:
                    print("Multiple results found")
                    query_results = old_session["attributes"]["Current_Query_Results"]
                    min_score = damerau_levenshtein_distance(personName,query_results[0]['name'])
                    min_person = query_results[0]
                    for result in query_results:
                        print("Name - {}, Score - {}".format(result['name'], damerau_levenshtein_distance(personName,result['name'])))
                        if damerau_levenshtein_distance(personName,result['name']) < min_score:
                            min_score = damerau_levenshtein_distance(personName,result['name'])
                            min_person = result
                    print(min_person)
                    setSessionValue(session, "Found_Person",True)
                    # setSessionValue(session, "Current_Query_Results",None)
                    # setSessionValue(session, "LookingForComfirmation",False)
                    setSessionValue(session, "CurrentPerson",min_person)
                    output = "{} confirmed.  ".format(min_person['name'])
                    output += choose_person_output(min_person, session)
                    return build_response(session, build_speechlet_response("Lookup Person", output, output, should_end_session))
            else:
                return handleLookupIntent(intent, session)
        else:
            return handleLookupIntent(intent, session)
    print(output)
    return build_response(session, build_speechlet_response("Lookup Person", output, output, should_end_session))

def handleLookupIntent(intent, old_session):
    output = ""
    should_end_session = True
    session = {}
    print("Lookup intent running")
    if 'PersonName' in intent['slots']:
        print(intent['slots']['PersonName'])
        personName = intent['slots']['PersonName']
        if 'value' in personName:
            personName = stripUnlikelyWords(personName['value'])
            print("Final PersonName - {}".format(personName))
        else:
            output = "Invalid name, please try again"
            should_end_session = False
            return build_response(session, build_speechlet_response("Lookup Person", output, output, should_end_session))
        if len(personName) < 3:
            output = "Invalid name, please try again"
            should_end_session = False
            return build_response(session, build_speechlet_response("Lookup Person", output, output, should_end_session))
        else:
            response = lookup_person(personName)
            if response is None:
                print("No results found")
                output = "No results found for {}.  Try looking up someone else or retrying.".format(personName)
                should_end_session = False
            elif len(response) > 1:
                print("Multiple results found")
                # print(response)
                should_end_session = False
                output = "{} people found. ".format(len(response))
                def nameField(a):
                    return a["name"]
                if len(response) > 6:
                    output += "The first six are... " 
                    output += getListString(response[:6], nameField)
                    fullQuery = []
                    fullSize = sys.getsizeof(fullQuery)
                    for item in response:
                        if fullSize < 20000:
                            fullQuery.append(item)
                            fullSize += sys.getsizeof(item)
                        
                        print(sys.getsizeof(fullQuery))
                    session["Current_Query_Results"] = fullQuery
                    session["Found_Person"] = False
                    session["LookingForComfirmation"] = True
                    print("full session size {}".format(sys.getsizeof(session)))
                else:
                    output += getListString(response, nameField)
                    session["Current_Query_Results"] = response
                    session["Found_Person"] = False
                    session["LookingForComfirmation"] = True
                output += "  Please specify further who you wanted to look up by saying, Confirm, then the person's name."
            elif len(response) == 1:
                print("One results found")
                should_end_session = False
                personName = response[0]['name']
                output = "{} found.  ".format(personName)
                person = response[0]
                output += choose_person_output(person, session)

                setSessionValue(session, "Found_Person",True)
                # setSessionValue(session, "Current_Query_Results",None)
                # setSessionValue(session, "LookingForComfirmation",False)
                setSessionValue(session, "CurrentPerson",person)
                # session["Found_Person"] = True
                # session["Current_Query_Results"] = {}
                # session["LookingForComfirmation"] = False
                # session["CurrentPerson"] = person
    print(output)
    return build_response(session, build_speechlet_response("Lookup Person", output, output, should_end_session))

def setSessionValue(session, key, value):
    session[key] = value
    # if key in session['attributes']:
    #     session['attributes'][key] = value

def handleGetInfoIntent(intent, old_session):
    output = ""
    should_end_session = True
    contractions = {"EARTH, ATMOS & PLANETARY SCI": "Earth, Atmosphere, and Planetary Science","Dept of Electrical Engineering & Computer Science":"Department of Electrical Engineering & Computer Science", "ELECTRICAL ENG & COMPUTER SCI":"Electrical Engineering and Computer Science", "20":"Biological engineering", "MATERIALS SCIENCE AND ENG":"Materials Science and Engineering"}
    session = old_session.get('attributes', {})
    if "CurrentPerson" in session and "Found_Person" in session and session["Found_Person"] and "CurrentInformationOptions" in session:
        currentPerson = session["CurrentPerson"]
        typeOptions = session["CurrentInformationOptions"]
        if 'value' in intent['slots']["Information_Type"]:
            infoKey = intent['slots']["Information_Type"]['value']
            if infoKey == "all":
                output = ''
                for item in typeOptions.items():
                    if item[1] in contractions:
                        output += "{}'s {} is {}.  ".format(currentPerson["name"], item[0], contractions[item[1]])
                    else:
                        output += "{}'s {} is {}.  ".format(currentPerson["name"], item[0], item[1])
            elif infoKey in typeOptions:
                if typeOptions[infoKey] in contractions:
                    output = "{}'s {} is {}.  ".format(currentPerson["name"], infoKey, contractions[typeOptions[infoKey]])
                else:
                    output = "{}'s {} is {}.  ".format(currentPerson["name"], infoKey, typeOptions[infoKey])
            else:
                output = "{} not found inside {}'s records.  {} only has information, including. {}".format(infoKey, currentPerson["name"], currentPerson["name"], getListString(typeOptions.keys()))
        else:
            output = "No informational type detected.  {} has different types of information, including. {}".format(currentPerson["name"], getListString(typeOptions.keys()))
            
    else:
        output = "No one currently selected.  Say find, then the person's name to get their information"
        should_end_session = False
    print(output)
    return build_response(session, build_speechlet_response("Get Person Information", output, output, should_end_session))

def stripUnlikelyWords(personName):
    words = ['find ', 'get ', 'lookup', 'look ', 'a ', 'up ', 'for ', 'info ', 'ask ', 'get ', 'information ', 'finds ', 'or ', 'the ', '.', 'search ', 'about ']
    output = personName
    for word in words:
        output = output.replace(word,'')
    return output


def lookup_person(personName):
    r = requests.get("http://m.mit.edu/apis/people?q={}".format(personName))
    response = r.json()
    if "error" in response:
        return None
    if len(response) == 0:
        return None
    else:
        return response

def choose_person_output(person):
    options = {}
    if "title" in person:
        options["title"] = person["title"]
    if "dept" in person:
        options["department"] = person["dept"]
    if "id" in person:
        options["kerberos"] = person["id"]
    if "phone" in person and len(person["phone"]) > 0:
        options["phone"] = person["phone"][0]
    if "email" in person and len(person["email"]) > 0:
        options["email"] = person["email"][0]
    if "office" in person and len(person["office"]) > 0:
        options["office"] = person["office"][0]
    if "website" in person and len(person["website"]) > 0:
        options["website"] = person["website"][0]
    if len(options) > 1:
        return ("{} has {} options. {}  Or say all?  What information do you want?".format(person['name'], len(options), getListString(list(options.keys()))), options)
    else:
        return ("{} has {} option. {}  What information do you want?".format(person['name'], len(options), options.keys()[0]), options)

def getListString(listName, function = None):
    output = ""
    for i in range(len(listName)):
        if i == len(listName) - 1:
            if function is not None:
                output += " and {}.".format(function(listName[i]))
            else:
                output += " and {}.".format(listName[i])
        else:
            if function is not None:
                output += "{}, ".format(function(listName[i]))
            else:
                output += "{}, ".format(listName[i])
    return output

def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1,lenstr1+1):
        d[(i,-1)] = i+1
    for j in range(-1,lenstr2+1):
        d[(-1,j)] = j+1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i,j)] = min(
                           d[(i-1,j)] + 1, # deletion
                           d[(i,j-1)] + 1, # insertion
                           d[(i-1,j-1)] + cost, # substitution
                          )
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition

    return d[lenstr1-1,lenstr2-1]
  
# --------------- Events ------------------



test = {
  "id": "0ad247c6-0993-4349-aff0-6e6e86ed8826",
  "timestamp": "2017-08-03T07:45:03.045Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "look up avery",
    "action": "LookUpPerson",
    "actionIncomplete": False,
    "parameters": {
      "given-name": "Avery",
      "Initials": "",
      "last-name": "",
      "PersonInformationType": ""
    },
    "contexts": [
      {
        "name": "current-person",
        "parameters": {
          "PersonInformationType.original": "",
          "Initials.original": "",
          "given-name.original": "avery",
          "last-name.original": "",
          "given-name": "Avery",
          "PersonInformationType": "",
          "Initials": "",
          "last-name": ""
        },
        "lifespan": 10
      },
      {
        "name": "lookupperson-followup",
        "parameters": {
          "PersonInformationType.original": "",
          "Initials.original": "",
          "given-name.original": "avery",
          "last-name.original": "",
          "given-name": "Avery",
          "PersonInformationType": "",
          "Initials": "",
          "last-name": ""
        },
        "lifespan": 2
      }
    ],
    "metadata": {
      "intentId": "48bf15b9-c294-4896-937c-cdd65579e04b",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 45,
      "intentName": "Look Up Person"
    },
    "fulfillment": {
      "speech": "Lookup  Person Information",
      "source": "webhook",
      "displayText": "Lookup  Person Information",
      "messages": [
        {
          "type": 0,
          "speech": "Lookup  Person Information"
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
lookupPerson(test)