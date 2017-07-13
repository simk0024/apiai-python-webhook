#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "owmWeatherForecast":
        return {}
    baseurl = "http://api.openweathermap.org/data/2.5/"
    owm_query = makeOwmQuery(req)
    if owm_query is None:
        return {}
    owm_url = baseurl + owm_query + "&APPID=f111102076d1eba55c555133233e0308"
    print(owm_url)

    result = urllib.urlopen(owm_url).read()
    print("owm result: ")
    print(result)

    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeOwmQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    country = parameters.get("geo-country")
    city = parameters.get("geo-city")
    date = parameters.get("date")

    if city is not None:
        location = city
    elif country is not None:
        location = country
    else:
        return None       

    #TODO: forecast-->forecast?q={city name}
    return "weather?q=" + location


def makeWebhookResult(data):
    weather = data.get('weather')
    if weather is None:
        return {}

    main = data.get('main')
    if main is None:
        return {}

    temp_min = main.get('temp_min')
    temp_max = main.get('temp_max')
    temp = main.get('temp')
    description = weather[0].get('description')
    location = data.get('name')

    # print(json.dumps(item, indent=4))

    speech = "Currently in " + location + ", it is " + temp + " degree with " + description + ". " + "Today, you can expect the highest "+ temp_max + " degree and the lowest " + temp_min + " degree." 

##  "Tomorrow in Sg, you will see {}, and can expect the highest {} degree 
##  and lowest {} degree."

    print("Response:")
    print(speech)

##    slack_message = {
##        "text": speech,
##        "attachments": [
##            {
##                "title": channel.get('title'),
##                "title_link": channel.get('link'),
##                "color": "#36a64f",
##
##                "fields": [
##                    {
##                        "title": "Condition",
##                        "value": "Temp " + condition.get('temp') +
##                                 " " + units.get('temperature'),
##                        "short": "false"
##                    },
##                    {
##                        "title": "Wind",
##                        "value": "Speed: " + channel.get('wind').get('speed') +
##                                 ", direction: " + channel.get('wind').get('direction'),
##                        "short": "true"
##                    },
##                    {
##                        "title": "Atmosphere",
##                        "value": "Humidity " + channel.get('atmosphere').get('humidity') +
##                                 " pressure " + channel.get('atmosphere').get('pressure'),
##                        "short": "true"
##                    }
##                ],
##
##                "thumb_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif"
##            }
##        ]
##    }
##
##    facebook_message = {
##        "attachment": {
##            "type": "template",
##            "payload": {
##                "template_type": "generic",
##                "elements": [
##                    {
##                        "title": channel.get('title'),
##                        "image_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif",
##                        "subtitle": speech,
##                        "buttons": [
##                            {
##                                "type": "web_url",
##                                "url": channel.get('link'),
##                                "title": "View Details"
##                            }
##                        ]
##                    }
##                ]
##            }
##        }
##    }
##
##    print(json.dumps(slack_message))

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {"slack": slack_message, "facebook": facebook_message},
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
