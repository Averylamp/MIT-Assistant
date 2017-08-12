import requests
import datetime

def handle_dining_intent(req):
    speech =  "Lookup  Person"
    contexts = req.get("result").get("contexts")
    suggestions = []
    parameters = req.get("result").get("parameters")
    fullQuery = req.get("result").get("resolvedQuery")

    diningHalls = parameters.get("Dining_Hall", [])
    diningTimes = parameters.get("Dining_Times", "")
    print(lookup_dining_option(diningHalls, diningTimes))


    print(fullQuery)


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


def lookup_dining_option(dining_halls, dining_meal = ""):
    print("Looking up dining halls {}".format(dining_halls))
    if len(dining_halls) < 1:
        return "Please specify which dining hall you would like to get meals for. Choose one of {}".format(getListString(dining_options(), None, "or"))
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
                output += hall_name[:1].capitalize() + hall_name[1:] + " could not be found as a MIT dining hall"

        return output

# print(lookup_dining_option(["Maseeh"]))
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

