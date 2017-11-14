'''
Shared under GNU GPLv3 license.
Author: Pawel Matusz
Contact: pawel.matusz@infiniconcept.com

Run this file to test the control function locally without having to upload
it to AWS as a lambda function, e.g. by "python test.py" in the folder containing
both this file and the TpLink_IoT_Control.py file.

It will send two test events to the control function, one to switch the power 
switch off and after 1 second another one to switch it on.

Don't forget to set your Kasa credentials in the main control function, otherwise
you will get an error trying to obtain the API token.

'''

from __future__ import print_function
from TpLink_IoT_Control import lambda_handler
import time

# Turn power swtch OFF
event = {
    "serialNumber": "GXXXXXXXXXXXXXXXXX",
    "batteryVoltage": "xxmV",
    "clickType": "DOUBLE"
}
lambda_handler(event, "")

time.sleep(1) 

# Turn power swtch ON
event = {
    "serialNumber": "GXXXXXXXXXXXXXXXXX",
    "batteryVoltage": "xxmV",
    "clickType": "SINGLE"
}
lambda_handler(event, "")
