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
	if req.get("result").get("action") == "LookUpDining":
		print("Dining Lookup Detected")
		return MITDining.handle_dining_intent(req)
	
	return {
		"speech": "Unable to proccess the request.  Try again later please.",
		"displayText": "Unable to proccess the request.  Try again later please.",
		# "data": data,
		"contextOut": [],
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
		
print(endIntent())

test = {
  "id": "41171092-c7b5-4e59-aea1-2580e2d9ba59",
  "timestamp": "2017-08-16T06:59:35.654Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "no",
    "action": "EndIntent",
    "actionIncomplete": false,
    "parameters": {},
    "contexts": [],
    "metadata": {
      "intentId": "69436dda-aa54-4f2c-8cc0-58a6a827348f",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 165,
      "intentName": "End Intent"
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
    "errorDetails": "Webhook call failed. Error: Webhook response was empty."
  },
  "sessionId": "c849e9e7-3c08-45c4-9df6-4a438214aeb9"
}


# if __name__ == '__main__':
# 	port = int(os.getenv('PORT', 5000))

# 	print("Starting app on port %d" % port)

# 	app.run(debug=False, port=port, host='0.0.0.0')
