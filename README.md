# AWS-IoT-button-HS110-control
Demonstrates how to use the AWS IoT button to directly control a TP-Link HS110 IoT power plug (smart home power switch).

## Description
This is an example Lambda function that controls the TP-Link HS110 smart home power switch (http://uk.tp-link.com/products/details/cat-5258_HS110.html) using the AWS IoT Button.

The motivation for this project was the fact that although you can control the HS110 power switch using the Kasa mobile app supported by TP-Link, it is not really convenient to have to use your phone to switch the power switch on and off e.g. to change your room lights. You can also do it using e.g. Amazon Alexa, but not everybody has one, or you might not want to have to go to the room where you have it to control a power socket elsewhere. However since Amazon made the AWS IoT buttons (https://aws.amazon.com/iotbutton/) fairly cheap and easily available, they can be used to control the socket.

Note that the project uses a 3rd party (TP-Link) web API to communicate with the HS110. This API might change without notice in which case this function might stop working and would need to be updated accordingly. 

## Setup
AWS has to be configured to invoke this function when your AWS IoT button is pressed. As a prerequisite you need to set up an Amazon AWS account on https://console.aws.amazon.com/. This can be done for free, set your region to N.Virginia which at the moment offers free access to several services. 

Next you have to set up your AWS IoT button to connect to AWS and invoke a lambda function: 

1. The easiest way to set things up is to use the setup wizard provided by AWS to automatically create everything that's needed in AWS (https://aws.amazon.com/iotbutton/getting-started/). This will include a lambda function, by default sending an email when the button is pressed. If you know AWS you can also do it all manually.

2. Using the AWS console (https://console.aws.amazon.com), select the Lambda service and create a new lambda function starting with a blank Python 2.7 template and paste the entire contents of TpLink_IoT_Control.py from this project. Note that if you created a Python 2.7 function already using the wizard in 1) then you can just overwrite the content of that function.

3. Using the AWS console (https://console.aws.amazon.com), select the IoT service, then go to the Act section (left hand side) where you should see your button listed under Rules. Edit the Action called "Invoke a Lambda function..." and select the name of the lambda function you created in step 2).

4. If you haven't yet done so, create a Kasa account from the Kasa mobile App:
   - For Android: https://play.google.com/store/apps/details?id=com.tplink.kasa_android
   - For iOS: https://itunes.apple.com/gb/app/kasa-for-mobile/id1034035493
   - You can alternatively do it using the TP-Link website: https://www.tplinkcloud.com/register.php.
   
Log into the app and register your TP-Link HS110 in it. Note that the HS110 has to be plugged in and able to connect to your WiFi network at the time it's being set up. If you do it correctly, you'll be able to turn the HS110 switch on and off from within the app.

5. Set your Kasa/TP-Link credentials used in step 4) in the lambda function on AWS created in step 2). This involves:
   - Setting the `kasaLogin` variable to your login email, and 
   - Setting the `kasaPassword` variable to your password.

6. Generate an UUID using https://www.uuidgenerator.net/version4 and set the `UUID` variable in the AWS lambda function to it.

7. Press the AWS IoT button once to turn on the switch, and twice to turn it off.

## Testing and troubleshooting

Functionality implemented in `TpLink_IoT_Control.py` can actually be tested without having to upload it to AWS. Make sure:
- You have Python 2.7 installed. 
- You followed step 5) above and set `kasaLogin`, `kasaPassword` and `UUID` variables correctly in `TpLink_IoT_Control.py`.

Switch to the folder where all project .py files are stored and run `python test.py`. The test harness will call into the main function twice, passing in JSON data structures asking it to turn the switch off and on, respectively, with a 1 second delay between them. If you e.g. connect a turned on lamp to the switch, you will see it blink. 

It can also be tested from the AWS console (https://console.aws.amazon.com) using the IoT service. Once you set everything up following steps 1-6 above, go to the Test section (left hand side) of the AWS IoT service page. In the Publish section, in the 'specify a topic...' field type `iotbutton/GXXXXXXXXXXXXXXX` where GXXXXXXXXXXXXXXX is the serial number of your AWS IoT button, which can be found printed on the back of the button. In the message section enter the following JSON, again replacing GXXXXXXXXXXXXXXX:

`{
  "serialNumber": "GXXXXXXXXXXXXXXX",
  "batteryVoltage": "1613mV",
  "clickType": "SINGLE"
}`

and press `Publish to a topic`. This will publish a message to the topic for which the lambda function is registered to listen, so it will be invoked with the JSON data above provided as an argument. It switches the smart plug on. If you replace SINGLE with DOUBLE, it will switch it off.

You can also check if your button is correctly sending messages to the AWS IoT Message Broker. To do this, enter `iotbutton/GXXXXXXXXXXXXXXX` (replace GXXXXXXXXXXXXXXX with your S/N) in the 'Subscription topic' field and press 'Subscribe to topic', which subscribes the web client to receive messages posted to this topic by the IoT button. Press the AWS Iot button once and then twice and check whether you receive the messages.

If you have more than one device registered in your Kasa app, the code arbitrarily selects the first one on the enumerated list of devices that is returned by the TP-Link server - see the 'Details of operation' section below. If this is not the device you want to control, then:
- Change the index from 0 to the one of the right device. In order to identify the right one, run the function once (e.g. activate it by pressing the IoT button) and look at the log generated - this can be seen in AWS CloudWatch. You can find it by going to your AWS lambda function, then selecting 'monitoring' and 'view with CloudWatch', or go directly to CloudWatch and from 'Log Groups' select your lambda function by name. 
- You can also extend the code to find the right device by alias. As you should be able to see in the log the name of the device which you set in the Kasa app is provided for each device in the 'alias' field. This can be useful if you want to further extend the code to work with several buttons and several devices - you can in such case select the right device by matching the alias with the serial number of the button passed into the function in the JSON parameter structure (GXXXXXXXXXXXXXXX).

## Details of operation

The following JSON template shows what is sent as the payload received in the invoked lambda function when the the Amazon IoT Button is pressed:

`{
    "serialNumber": "GXXXXXXXXXXXXXXX",
    "batteryVoltage": "xxmV",
    "clickType": "SINGLE" | "DOUBLE" | "LONG"
}`

"SINGLE" and "DOUBLE" clickType payloads are sent for single and double short clicks, respectively.  A "LONG" clickType is sent if the first press lasts longer than 1.5 seconds. 

Once this function is invoked, the TP-Link Cloud REST API is used to control the HS110 switch. The following steps are performed using the TP-Link RESTful API:

1. Get the API key (token) by logging into the TP-Link Could using your TP-Link cloud account credentials - email and password. This token is required to authenticate you in any further API calls.

2. Get the list of devices registered on your account. A prerequisite for this step is that you should have discovered and registered your devices using the Kasa mobile app. As explained above, this example arbitrarily picks the first device on the list to control; you may want to either change this to select the right device, or search for the right device by alias, or even hardcode the deviceID and skip this step.

3. Switch the state of the power switch (relay) according to the type of event received from the button: ON for single press, and OFF for double press.
