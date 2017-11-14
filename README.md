# AWS-IoT-button-HS110-control
Demonstrates how to use the AWS IoT button to directly control a TP-Link HS110 smart home IoT power switch

## Description
This is an example Lambda function that controls the TP-Link HS110 smart home power switch (http://uk.tp-link.com/products/details/cat-5258_HS110.html) using the AWS IoT Button.

The motivation for this project was the fact that although you can control the HS110 power switch using the Kasa mobile app supported by TP-Link, it is not really convenient to have to use your phone to switch the power switch on and off e.g. to change your room lights. You can also do it using e.g. Amazon Alexa, but not everybody has one, or you might not want to have to go to the room where you have it to control a power socket elsewhere. However since Amazon made the AWS IoT buttons (https://aws.amazon.com/iotbutton/) fairly cheap and easily available, they can be used to control the socket.

Note that the project uses a 3rd party (TP-Link) web API to communicate with the HS110. This API might change without notice in which case this function might stop working and would need to be updated accordingly. 

## Setup
AWS has to be configured to invoke this function when your AWS IoT button is pressed. As a prerequisite you need to set up an Amazon AWS account on https://console.aws.amazon.com/. This can be done for free, set your region to N.Virginia which at the moment offers free access to several services. 

Next you have to set up your AWS IoT button to connect to AWS and invoke a lambda function: 

1. The easiest way to set things up is to use the setup wizard provided by AWS to automatically create everything that's needed in AWS (https://aws.amazon.com/iotbutton/getting-started/). This will include a lambda function, by default sending an email when the button is pressed. If you know AWS you can also do it all manually.

2. Using the AWS console (https://console.aws.amazon.com), select the Lambda service and create a new lambda function starting with a blank Python 2.7 template and paste the entire contents of TpLink_IoT_Control.py from this project. Note that if you created a Python 2.7 function already usign the wizard in 1) then you can just overwrite the content of that function.

3. Using the AWS console (https://console.aws.amazon.com), select the IoT service, then go to the Act section (left hand side) where you should see your button listed under Rules. Edit the Action called "Invoke a Lambda function..." and select the name of the lambda function you created in step 2).

4. If you haven't yet done so, create a Kasa account from the Kasa mobile App:
   - For Android: https://play.google.com/store/apps/details?id=com.tplink.kasa_android
   - For iOS: https://itunes.apple.com/gb/app/kasa-for-mobile/id1034035493
   - You can alternatively do it using the TP-Link website: https://www.tplinkcloud.com/register.php.
Log into the app and register your TP-Link HS110 in it. Note that the HS110 has to be plugged in and able to connect to your WiFi network at the time it's being set up. If you do it correctly, you'll be able to turn the HS110 switch on and off from the app.

5. Set your Kasa/TP-Link credentials used in step 4) in the lambda function on AWS created in step 2). This involves:
   - Setting the `kasaLogin` variable to your login email, and 
   - Setting the `kasaPassword` variable to your password.

6. Generate an UUID using https://www.uuidgenerator.net/version4 and set the `UUID` variable in the AWS lambda function to it.

7. Press the AWS IoT button once to turn on the switch, and twice to turn it off.

## Testing


## Details of operation

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
