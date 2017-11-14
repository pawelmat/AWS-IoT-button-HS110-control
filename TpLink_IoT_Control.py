'''
Shared under GNU GPLv3 license.
Author: Pawel Matusz
Contact: pawel.matusz@infiniconcept.com

This is an example Lambda function that controls the TP-Link HS110 smart home 
power switch (http://uk.tp-link.com/products/details/cat-5258_HS110.html) using 
input from the AWS IoT Button.

As it does not use any other AWS resources, it does not require any particular 
access permissions.

AWS has to be configured to invoke this function when your AWS IoT button
is pressed. The easiest way to do it is to:

1. Use the setup wizard provided by AWS to automatically create everything that's
 needed in AWS (https://aws.amazon.com/iotbutton/getting-started/). This will 
 include a lambda function (by default sending an email when the button is pressed)
2. Using the AWS console (https://console.aws.amazon.com), create a new lambda 
 function starting with a blank Python 2.7 template and paste in this code. Note
 that if you created a Python 2.7 function already usign the wizard in 1) then you
 can just overwrite the content of that function.
3. Set your Kasa/TP-Link credentials in the function below, (kasaLogin and 
 kasaPassword). Generate a UUID using https://www.uuidgenerator.net/version4 and
 set the UUID variable to it.
3. In the IoT service in the AWS console, go to Act, you should see your button
 under Rules. Edit the Action called "Invoke a Lambda function..." and select
 the function you created in 2).


The following JSON template shows what is sent as the payload received in the 
invoked lambda function when the the Amazon IoT Button is pressed:
{
    "serialNumber": "GXXXXXXXXXXXXXXXXX",
    "batteryVoltage": "xxmV",
    "clickType": "SINGLE" | "DOUBLE" | "LONG"
}

"SINGLE" and "DOUBLE" clickType payloads are sent for single and double
short clicks, respectively.  A "LONG" clickType is sent if the first 
press lasts longer than 1.5 seconds (it's not used in this example)

Once this function is invoked, the TP-Link Cloud REST API is used to control 
the HS110 switch. The following steps are performed:

1. Get the API key (token) by logging into the TP-Link Could using your
   TP-Link cloud account credentials - email and password. 
   You can create an account from the Kasa mobile App:
   - For Android: https://play.google.com/store/apps/details?id=com.tplink.kasa_android
   - For iOS: https://itunes.apple.com/gb/app/kasa-for-mobile/id1034035493
   or on the TP-Link website: https://www.tplinkcloud.com/register.php
2. Get the list of devices registered on your account. A prerequisite for
   this step is that you should have discovered and registered your devices 
   using the Kasa mobile app. This example arbitrarily picks the first
   device on the list to control; you may want to either change this to select
   the right device, or once you find out the right deviceID hard code it and
   skip this step.
3. Switch the state of the power switch (relay) according to the type of event 
   received from the button: ON for single press, and OFF for double press.

TODO:
- Proper error handling

'''

# ---- Please update this section before you run the function -----------
#

# Kasa login: change it to your KASA login email address
kasaLogin = 'login.email@mydomain.com'  

# Kase password: change it to your KASA password
kasaPassword = 'password' 

# change to a new UUID v4 obtained from https://www.uuidgenerator.net/version4 
UUID = 'xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' 

#
# -----------------------------------------------------------------------

import urllib2
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logging.info('Received event: ' + json.dumps(event))

    ##### Get the TP-Link RESTful API token 
    req = { "method": "login", "params": { "appType": "Kasa_Android",  "cloudUserName": " ",  "cloudPassword": " ", "terminalUUID": " " }}
    req['params']['cloudUserName'] = kasaLogin
    req['params']['cloudPassword'] = kasaPassword
    req['params']['terminalUUID'] = UUID

    # Get Kasa API key - send POST to server and get response
    data = json.dumps(req)
    httpReq = urllib2.Request("https://wap.tplinkcloud.com", 
                        data, 
                        {'Content-Type': 'application/json'})
    f = urllib2.urlopen(httpReq)
    response = f.read()
    f.close()
    rsp = json.loads(response)
    apiToken = rsp['result']['token']
    logging.info("Kasa API login response: " + str(response))

    ##### Get List of smart devices registered in Kasa
    req = { "method": "getDeviceList" }
    data = json.dumps(req)
    httpReq = urllib2.Request("https://eu-wap.tplinkcloud.com/?token=" + apiToken, 
                        data, 
                        {'Content-Type': 'application/json'})
    f = urllib2.urlopen(httpReq)
    response = f.read()
    f.close()
    logging.info("Kasa API get device list response: " + str(response))

    # Arbitrarily pick first device. This might have to be changed (can be hardcoded one you identify the device you want to control)
    rsp = json.loads(response)
    deviceId = rsp['result']['deviceList'][0]['deviceId']
    logging.info("Device selected: " + deviceId)

    ##### State control
    # ON event by default
    req = {"method":"passthrough", "params": {"deviceId": " ", "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}" }}
    req['params']['deviceId'] = deviceId

    # Handle different Amazon IoT button press modes
    if event['clickType'] == 'SINGLE':
        logging.info('Turning switch ON')
    elif event['clickType'] == 'DOUBLE':
        req['params']['requestData'] = "{\"system\":{\"set_relay_state\":{\"state\":0}}}"
        logging.info('Turning switch OFF')
    else:
        logging.info('Long press event not handled') # defaults to ON

    # Send HTTP POST indicating to turn the relay on or off
    data = json.dumps(req)
    httpReq = urllib2.Request("https://eu-wap.tplinkcloud.com/?token=" + apiToken, 
                        data, 
                        {'Content-Type': 'application/json'})
    f = urllib2.urlopen(httpReq)
    response = f.read()
    f.close()
    logging.info("Kasa API relay state change response: " + str(response))
