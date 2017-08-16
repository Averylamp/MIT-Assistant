import requests
import datetime

def handle_dining_intent(req):
    speech =  "Lookup Dining"
    contexts = req.get("result").get("contexts")
    suggestions = []
    parameters = req.get("result").get("parameters")
    fullQuery = req.get("result").get("resolvedQuery")

    diningHalls = parameters.get("Dining_Hall", [])
    diningTimes = parameters.get("Dining_Times", "")
    print(lookup_dining_option(diningHalls, diningTimes))
    speech = lookup_dining_option(diningHalls, diningTimes, suggestions, contexts)

    print(fullQuery)

    print("----------- Final response -------------")
    print(speech)
    print(suggestions)
    data = addSuggestions(speech, suggestions)

    return {
        "speech": speech,
        "displayText": speech,
        "data": data,
        "contextOut": contexts,
        "source": "webhook"
    }

def lookup_dining():
    r = requests.get("http://m.mit.edu/apis/dining/venues/house")
    response = r.json()
    return response

def dining_options():
    options = []
    r = requests.get("http://m.mit.edu/apis/dining/venues/house")
    response = r.json()
    for diningOption in response:
        if diningOption.get("short_name", "") != "":
            options.append(diningOption.get("short_name", ""))
    return options

# print(dining_options())
def lookup_dining_option(dining_halls, dining_meal = "", suggestions = [], contexts={}):
    print("Looking up dining halls {}".format(dining_halls))
    if len(dining_halls) < 1:
        suggestions += dining_options()
        return "Please specify which dining hall or halls you would like to get meals for. Choose from {}".format(getListString(dining_options(), None, "and or"))
    else:
        print("Dining hall selected")
        fullOptions = lookup_dining()
        output = ""
        for hall_name in dining_halls:
            print('Retrieving options for {}'.format(hall_name))
            hallFound = False
            for option in fullOptions:
                if option.get("short_name", "").lower() == hall_name.lower():
                    print("Option found")
                    hallFound = True
                    meals_by_day = option.get("meals_by_day")
                    today_date_string = datetime.datetime.now().strftime("%Y-%m-%d")
                    current_day_meal = None
                    for dining_day in meals_by_day:
                        if dining_day.get('date', '') == today_date_string:
                            current_day_meal = dining_day
                    if current_day_meal is not None:
                        if current_day_meal.get('message', '') != '':
                            output += "{} is {}. ".format(hall_name[:1].capitalize() + hall_name[1:], current_day_meal.get('message').lower())
                        elif len(current_day_meal.get('meals', [])) > 0:
                            meals = current_day_meal.get('meals')
                            meal_names = []
                            for meal in meals:
                                if meal.get("name", "") != "":
                                    meal_names.append(meal.get("name"))
                            output += "{} has the meals {}".format(hall_name[:1].capitalize() + hall_name[1:], meal_names)



                    else:
                        output += "  No meal found in {} for today. ".format(hall_name)
            if hallFound == False:
                output += hall_name[:1].capitalize() + hall_name[1:] + " could not be found as a MIT dining hall.  Try again with a vailid MIT Dining hall name.  "
                updateContext(contexts, "endcontext", 1, {})
            else:
            	output += "  Did you want to look up dining for another dining hall?"
            	updateContext(contexts, "endcontext", 1, {})
            	suggestions += ["I'm Done"]
        suggestions += dining_options()
        return output

# print(lookup_dining_option(["Maseeh"]))
def addSuggestions(speech = "", suggestions = [], expectResponse = True):
    suggestionsTitles = []
    for item in suggestions:
        suggestionsTitles.append({"title":item})
    return {
   "google":{
      "expect_user_response":expectResponse,
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
def updateContext(contexts, name, lifespan, parameters):
    updated = False
    for i in range(len(contexts)):
        if contexts[i].get("name", "").lower() == name.lower():
            contexts[i]["lifespan"] = lifespan
            contexts[i]["parameters"] = parameters
            updated = True
    if updated == False:
        contexts.append({"name":name.lower(),"lifespan":lifespan, "parameters":parameters})

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

test = {
  "id": "b7a29d2b-d681-450a-b6a9-2d9a79e51e64",
  "timestamp": "2017-08-12T08:31:55.684Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "what is in dining",
    "action": "LookUpDining",
    "actionIncomplete": False,
    "parameters": {
      "date": "",
      "Dining_Hall": [],
      "Dining_Times": ""
    },
    "contexts": [
      {
        "name": "current-person",
        "parameters": {
          "date": "",
          "PersonInformationType.original": "",
          "date.original": "",
          "PersonInformationType": "",
          "Initials": "",
          "Dining_Times": "",
          "Dining_Hall": [],
          "Initials.original": "",
          "given-name.original": "",
          "last-name.original": "",
          "Dining_Times.original": "",
          "given-name": "",
          "Dining_Hall.original": "",
          "last-name": ""
        },
        "lifespan": 9
      },
      {
        "name": "lookupperson-followup",
        "parameters": {
          "date": "",
          "PersonInformationType.original": "",
          "date.original": "",
          "PersonInformationType": "",
          "Initials": "",
          "Dining_Times": "",
          "Dining_Hall": [],
          "Initials.original": "",
          "given-name.original": "",
          "last-name.original": "",
          "Dining_Times.original": "",
          "given-name": "",
          "Dining_Hall.original": "",
          "last-name": ""
        },
        "lifespan": 1
      }
    ],
    "metadata": {
      "intentId": "a6e65de2-523c-4ec6-b2f0-720ee53c253b",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 301,
      "intentName": "Look Up Dining"
    },
    "fulfillment": {
      "speech": "Please specify which dining hall you would like to get meals for. Choose one of McCormick, Simmons, Baker, Maseeh, or Next.",
      "source": "webhook",
      "displayText": "Please specify which dining hall you would like to get meals for. Choose one of McCormick, Simmons, Baker, Maseeh, or Next.",
      "messages": [
        {
          "type": 0,
          "speech": "Please specify which dining hall you would like to get meals for. Choose one of McCormick, Simmons, Baker, Maseeh, or Next."
        }
      ],
      "data": {
        "google": {
          "expect_user_response": True,
          "rich_response": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "Please specify which dining hall you would like to get meals for. Choose one of McCormick, Simmons, Baker, Maseeh, or Next.",
                  "displayText": "Please specify which dining hall you would like to get meals for. Choose one of McCormick, Simmons, Baker, Maseeh, or Next."
                }
              }
            ],
            "suggestions": []
          }
        }
      }
    },
    "score": 1
  },
  "status": {
    "code": 200,
    "errorType": "success"
  },
  "sessionId": "c849e9e7-3c08-45c4-9df6-4a438214aeb9"
}

# handle_dining_intent(test)