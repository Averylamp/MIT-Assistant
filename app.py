#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import MITClass
import MITPeople
import MITDining

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/', methods=['GET'])
def loadingPage():
	return "Hello loading page"


@app.route('/webhook', methods=['POST'])
def webhook():
	req = request.get_json(silent=True, force=True)

	print("Request Recieved:")
	# print(json.dumps(req, indent=4))

	res = processRequest(req)
	print("Response: ")
	print(res["speech"])
	res = json.dumps(res, indent=4)
	
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r


def processRequest(req):
	if req.get("result").get("action") == "LookUpClass":
		print("Class Lookup Detected")
		return MITClass.lookupClass(req)
	if req.get("result").get("action") == "LookUpClass.LookUpClassInformation":
		print("Class Info Lookup Detected")
		return MITClass.lookupClass(req)
	if req.get("result").get("action") == "LookUpPerson":
		print("People Lookup Detected")
		return MITPeople.lookupPerson(req)
	if req.get("result").get("action") == "LookUpPerson.LookUpInformation":
		print("People Lookup Detected")
		return MITPeople.lookupInformation(req)
	if req.get("result").get("action") == "LookUpPerson.LookUpConfirmation":
		print("People Confirmation Detected")
		return MITPeople.confirmPerson(req)
	if req.get("result").get("action") == "EndIntent":
		return endIntent()
	if req.get("result").get("action") == "input.welcome":
		return welcomeIntent()
	if req.get("result").get("action") == "LookUpDining":
		print("Dining Lookup Detected")
		r = MITDining.handle_dining_intent(req)
		print(r)
		return r
	
	return {
		"speech": "Unable to proccess the request.  Try again later please.",
		"displayText": "Unable to proccess the request.  Try again later please.",
		# "data": data,
		"contextOut": [],
		"source": "webhook"
	}
def welcomeIntent():
	suggestions = ["What can you do?", "Look up a class","Look up a person", "What's in Maseeh today?"]
	suggestionsTitles = []
	for item in suggestions:
		suggestionsTitles.append({"title":item})
	data =  {"google":{
	  "expect_user_response":False,
	  "rich_response":{
		 "items":[
			{
			   "simpleResponse":{
				  "textToSpeech":"Hi! Welcome to the MIT Assistant.  We can help you look up people in the Directory, figure out what class numbers correspond to, and help you figure out what is in dining currently.  Ask away!",
				  "displayText":"Hi! Welcome to the MIT Assistant.  We can help you look up people in the Directory, figure out what class numbers correspond to, and help you figure out what is in dining currently.  Ask away!"
			   }
			}
		 ],
		 "suggestions": suggestionsTitles
		  }
	   }
	}
	return {
		"speech": "Hi! Welcome to the MIT Assistant.  We can help you look up people in the Directory, figure out what class numbers correspond to, and help you figure out what is in dining currently.  Ask away!",
		"displayText": "Hi! Welcome to the MIT Assistant.  We can help you look up people in the Directory, figure out what class numbers correspond to, and help you figure out what is in dining currently.  Ask away!",
		"data": data,
		"contextOut": {},
		"source": "webhook"
	}
def endIntent():
	data =  {"google":{
	  "expect_user_response":False,
	  "rich_response":{
		 "items":[
			{
			   "simpleResponse":{
				  "textToSpeech":"Thank you for using MIT Information.  Keep us in mind when you need more of your on campus information.",
				  "displayText":"Thank you for using MIT Information.  Keep us in mind when you need more of your on campus information."
			   }
			}
		 ],
		 "suggestions": []
		  }
	   }
	}
	return {
		"speech": "Thank you for using MIT Information.  Keep us in mind when you need more of your on campus information.",
		"displayText": "Thank you for using MIT Information.  Keep us in mind when you need more of your on campus information.",
		"data": data,
		"contextOut": {},
		"source": "webhook"
	}
		


if __name__ == '__main__':
	port = int(os.getenv('PORT', 5000))

	print("Starting app on port %d" % port)

	app.run(debug=False, port=port, host='0.0.0.0')
