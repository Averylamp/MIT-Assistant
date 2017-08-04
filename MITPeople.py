from __future__ import print_function
import requests
import json
import sys

def lookupPerson(req):
    speech =  "Lookup  Person"
    contexts = req.get("result").get("contexts")
    suggestions = []
    parameters = req.get("result").get("parameters")
    fullQuery = req.get("result").get("resolvedQuery")
    if fullQuery == "Look up a person":
        speech = "To look up a person, simply say 'Look up' then the person's name."
        return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        "contextOut": contexts,
        "source": "webhook"
        }
    print("Full Query: {}".format(fullQuery))
    firstNameFound = False
    lastNameFound = False
    initialLetterFound = False
    personContextFound = False
    guessedLastNameFound = False
    for context in contexts:
        if context.get("name", "").lower() == "current-person" :
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
            bestGuessName = "{} {}".format(firstName, initialLetterFound)
        else:
            bestGuessName = "{}".format(firstName)
        bestGuessFormat = ['last']
        q = lookup_person(bestGuessName)
        print("{} found - {} result".format(bestGuessName, len(q)))
        if len(q) >= 1:
            foundResults = True
            addToResults(results, q, foundIDs, foundNames)       
    if foundResults == False:
        bestGuessName = stripUnlikelyWords(fullQuery)
        bestGuessFormat = ['query']
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
    print("Best guess name - {}".format(bestGuessName))
    print(foundNamesArr)
    if len(foundNamesArr) > 1:
        confirmPerson = False
        for context in contexts:
            if context.get("name", "").lower()  == "ConfirmPersonContext".lower() :
                if context.get("ConfirmPerson", False) == True:
                    confirmPerson = True
        if confirmPerson:
            print("Confirming Person")
            for person in results:
                if person.get("name","").lower()  == foundNamesArr[0].lower() :
                    personResults = person
            optionsStr, options = choose_person_output(personResults)
            speech += optionsStr
            updateContext(contexts, "FoundPersonContext".lower() , 5, {"foundPerson":personResults,"foundOptions":options})
        else:
            print("Listing possible people")
            speech = "{} results found. ".format(len(foundNamesArr))
            if len(foundNamesArr) > 5:
                speech += "The first five are: " + getListString(foundNamesArr[:5]) + " "
                suggestions = suggestions + list(map(lambda x: "Confirm " + x, foundNamesArr[:5]))
            else:
                speech += "They are: " + getListString(foundNamesArr) + ". " 
                suggestions = suggestions + list(map(lambda x: "Confirm " + x, foundNamesArr))
            speech += "To confirm the person you are looking for say confirm, then their full name again"
            updateContext(contexts, "ConfirmPersonContext".lower() , 2, {"ConfirmPerson":True})
    elif len(foundNamesArr) == 1:
        speech = "{} found. ".format(foundNamesArr[0])
        personResults = None
        for person in results:
            if person.get("name","").lower()  == foundNamesArr[0].lower() :
                personResults = person
        optionsStr, options = choose_person_output(personResults)
        suggestions = suggestions + ["all"] + list(options)
        speech += optionsStr
        updateContext(contexts, "FoundPersonContext".lower() , 5, {"foundPerson":personResults,"foundOptions":options})


    contexts.append({"name":"QueryResultsContext".lower() , "lifespan":5,"parameters":{"foundPeople":results}})
    print("----------- Final response -------------")
    print(speech)
    data = addSuggestions(speech, suggestions)
    return {
        "speech": speech,
        "displayText": speech,
        "data": data,
        "contextOut": contexts,
        "source": "webhook"
    }

def confirmPerson(req):
    speech =  "Lookup  Person Information"
    contexts = req.get("result").get("contexts")
    parameters = req.get("result").get("parameters")
    suggestions = []

    fullQuery = req.get("result").get("resolvedQuery")
    print("Full Query: {}".format(fullQuery))
    firstNameFound = False
    lastNameFound = False
    initialLetterFound = False
    personContextFound = False
    guessedLastNameFound = False
    for context in contexts:
        if context.get("name", "").lower()  == "current-person".lower()  :
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
        foundResults = True


    if lastNameFound and not foundResults:
        bestGuessName = "{}".format(lastName)
        bestGuessFormat = ['last']        
        foundResults = True

    
    if firstNameFound and not foundResults:
        if initialLetterFound:
            bestGuessName = "{} {}".format(firstName, initialLetterFound)
        else:
            bestGuessName = "{}".format(firstName)
        bestGuessFormat = ['last']        
        foundResults = True
    if foundResults == False:
        bestGuessName = fullQuery.lower().replace("confirm ", "")
    print("Best Guess Name - {}".format(bestGuessName))
    foundNames = []
    searchResults = None
    for context in contexts:
        if context.get("name", "").lower() == "queryresultscontext".lower()  :
            searchResults = context["parameters"].get("foundPeople",[])
            for item in searchResults:
                name = item.get("name", None)
                if name is not None:
                    foundNames.append(name)
    foundNamesArr = sorted(foundNames, key=lambda x: damerau_levenshtein_distance(bestGuessName, x))
    print(foundNamesArr)
    for person in searchResults:
        if person.get("name","").lower()  == foundNamesArr[0].lower() :
            personResults = person
            optionsStr, options = choose_person_output(personResults)
            speech = optionsStr
            suggestions = suggestions + ["all"] + list(options)
            updateContext(contexts, "FoundPersonContext", 5, {"foundPerson":personResults,"foundOptions":options})
    print("--------- Final Speech ---------")
    print(speech)
    data = addSuggestions(speech, suggestions)
    return {
        "speech": speech,
        "displayText": speech,
        "data": data,
        "contextOut": contexts,
        "source": "webhook"
    }

def lookupInformation(req):
    speech =  "Lookup  Person Information"
    contexts = req.get("result").get("contexts")
    parameters = req.get("result").get("parameters")
    suggestions = []
    print(parameters)
    personInfoTypes = parameters.get("PersonInformationType", [])
    contractions = {"EARTH, ATMOS & PLANETARY SCI": "Earth, Atmosphere, and Planetary Science","Dept of Electrical Engineering & Computer Science":"Department of Electrical Engineering & Computer Science", "ELECTRICAL ENG & COMPUTER SCI":"Electrical Engineering and Computer Science", "20":"Biological engineering", "MATERIALS SCIENCE AND ENG":"Materials Science and Engineering"}
    for context in contexts:
        if context.get("name", "").lower()  == "foundpersoncontext".lower()  :
            foundPersonContext = context
            foundPersonName = foundPersonContext["parameters"].get("foundPerson", {}).get("name", "The person")
            foundOptions = foundPersonContext["parameters"].get("foundOptions", {})
            suggestions = suggestions +  ["all"] + list(foundOptions)
            print(foundPersonName)
            print(foundOptions)

    if len(personInfoTypes) > 0:
        if "all" in personInfoTypes:
            speech = "Here is all of " + foundPersonName + "'s information: Their "
            personInfoTypes = list(foundOptions.keys())
        else:
            if len(personInfoTypes) == 1:
                speech = foundPersonName + "'s "
            else:
                speech = "Here is " + foundPersonName + "'s information: Their "
        print(personInfoTypes)
        addedItems = []
        for infoOption in personInfoTypes:
            
            if infoOption in foundOptions:
                resultingOption = foundOptions[infoOption]
                if resultingOption in contractions:
                    resultingOption = contractions[resultingOption]
                addedItems.append("{} is {}".format(infoOption, resultingOption))
        speech += getListString(addedItems)
    else:
        speech = "Sorry, I am unable to determine information to retrieve."
    print("----------- Final response -------------")
    print(speech)
    data = addSuggestions(speech, suggestions)
    return {
        "speech": speech,
        "displayText": speech,
        "data": data,
        "contextOut": contexts,
        "source": "webhook"
    }

def updateContext(contexts, name, lifespan, parameters):
    updated = False
    for i in range(len(contexts)):
        if contexts[i].get("name", "").lower() == name.lower():
            contexts[i]["lifespan"] = lifespan
            contexts[i]["parameters"] = parameters
            updated = True
    if updated == False:
        contexts.append({"name":name.lower(),"lifespan":lifespan, "parameters":parameters})


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

def getListString(listName, function = None, conjunction = "and"):
    output = ""
    if len(listName) == 0:
        return ""
    if len(listName) == 1:
        return "{}.".format(listName[0])
    for i in range(len(listName)):
        if i == len(listName) - 1:
            if function is not None:
                output += "{} {}.".format(conjunction, function(listName[i]))
            else:
                output += "{} {}.".format(conjunction, listName[i])
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


test = {
  "id": "14ed81bf-526c-4056-80cd-2059e35ecd36",
  "timestamp": "2017-08-04T01:03:30.634Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "confirm sam ihns",
    "action": "LookUpPerson.LookUpConfirmation",
    "actionIncomplete": False,
    "parameters": {
      "given-name": "Sam",
      "last-name": ""
    },
    "contexts": [
      {
        "name": "queryresultscontext",
        "parameters": {
          "Initials.original": "i",
          "PersonInformationType.original": "",
          "given-name.original": "sam",
          "last-name.original": "",
          "foundPeople": [
            {
              "surname": "Etkind",
              "givenname": "Samuel Isaac",
              "name": "Samuel Isaac Etkind",
              "dept": "CHEMISTRY",
              "id": "sietkind",
              "email": [
                "sietkind@mit.edu"
              ],
              "url": "http://m.mit.edu/apis/people/sietkind"
            },
            {
              "surname": "Grondahl",
              "givenname": "Samuel Isaac",
              "name": "Samuel Isaac Grondahl",
              "dept": "ECONOMICS",
              "id": "grondahl",
              "email": [
                "grondahl@mit.edu"
              ],
              "url": "http://m.mit.edu/apis/people/grondahl"
            },
            {
              "surname": "Ihns",
              "givenname": "Samuel H",
              "name": "Samuel H Ihns",
              "id": "samihns",
              "email": [
                "samihns@mit.edu"
              ],
              "url": "http://m.mit.edu/apis/people/samihns"
            },
            {
              "surname": "Ingersoll",
              "givenname": "Samuel Tenzin Alexander",
              "name": "Samuel Tenzin Alexander Ingersoll",
              "title": "Research Affiliate",
              "dept": "Department of Mechanical Engineering",
              "id": "saming",
              "email": [
                "saming@mit.edu"
              ],
              "office": [
                "5-017"
              ],
              "url": "http://m.mit.edu/apis/people/saming"
            },
            {
              "surname": "Inman",
              "givenname": "Samuel J",
              "name": "Samuel J Inman",
              "id": "samueli",
              "email": [
                "samueli@mit.edu"
              ],
              "url": "http://m.mit.edu/apis/people/samueli"
            },
            {
              "surname": "Wald",
              "givenname": "Samuel Isaac",
              "name": "Samuel Isaac Wald",
              "dept": "AERONAUTICS AND ASTRONAUTICS",
              "id": "swald",
              "email": [
                "swald@mit.edu"
              ],
              "url": "http://m.mit.edu/apis/people/swald"
            }
          ],
          "given-name": "Sam",
          "Initials": "i",
          "PersonInformationType": "",
          "last-name": ""
        },
        "lifespan": 5
      },
      {
        "name": "confirmpersoncontext",
        "parameters": {
          "given-name.original": "sam",
          "last-name.original": "",
          "ConfirmPerson": True,
          "given-name": "Sam",
          "last-name": ""
        },
        "lifespan": 1
      },
      {
        "name": "current-person",
        "parameters": {
          "PersonInformationType.original": "",
          "Initials.original": "i",
          "given-name.original": "sam",
          "last-name.original": "",
          "given-name": "Sam",
          "PersonInformationType": "",
          "Initials": "i",
          "last-name": ""
        },
        "lifespan": 9
      },
      {
        "name": "foundpersoncontext",
        "parameters": {
          "Initials.original": "i",
          "given-name.original": "sam",
          "PersonInformationType.original": "",
          "last-name.original": "",
          "foundPerson": {
            "surname": "Ford",
            "givenname": "Samuel Earl",
            "name": "Sam Ford",
            "title": "Research Affiliate",
            "dept": "Comparative Media Studies/Writing",
            "id": "samford",
            "website": [
              "http://www.fastcompany.com/user/sam-ford-0"
            ],
            "email": [
              "samford@mit.edu"
            ],
            "url": "http://m.mit.edu/apis/people/samford"
          },
          "foundOptions": {
            "title": "Research Affiliate",
            "department": "Comparative Media Studies/Writing",
            "kerberos": "samford",
            "email": "samford@mit.edu",
            "website": "http://www.fastcompany.com/user/sam-ford-0"
          },
          "given-name": "Sam",
          "Initials": "i",
          "PersonInformationType": "",
          "last-name": ""
        },
        "lifespan": 3
      },
      {
        "name": "lookupperson-followup",
        "parameters": {
          "PersonInformationType.original": "",
          "Initials.original": "i",
          "given-name.original": "sam",
          "last-name.original": "",
          "given-name": "Sam",
          "PersonInformationType": "",
          "Initials": "i",
          "last-name": ""
        },
        "lifespan": 1
      }
    ],
    "metadata": {
      "intentId": "3310271a-53b3-4748-8c67-5f6b9e477a25",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "intentName": "Look Up Person Confirmation"
    },
    "fulfillment": {
      "speech": "",
      "messages": [
        {
          "type": 0,
          "speech": ""
        }
      ]
    },
    "score": 1
  },
  "status": {
    "code": 206,
    "errorType": "partial_content",
    "errorDetails": "Webhook call failed. Error: 500 INTERNAL SERVER ERROR"
  },
  "sessionId": "6693c855-d7b1-4595-bb0b-d63c5d1af277"
}
confirmPerson(test)


