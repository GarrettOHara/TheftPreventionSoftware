from os import error
from decouple import config # pip python-decouple
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

""" REST API Exception """
class PhoneNumberVerificationError(Exception):
    pass
class NoResponseError(Exception):
    pass

""" REST API Authentication """
account_sid = config('SID')
auth_token  = config('TOKEN')
global sms_sid
sms_sid = config('SMS_SID')

""" Instantiate REST API client """
global client 
client = Client(account_sid, auth_token)

"""
Function:
Send SMS

Description:
Sends a text message to the user when the power is disconnected

Documentation: 
https://www.twilio.com/docs/sms/send-messages#post-parameters-conditional

Parameters:
N/A

Returns:
sid: String
    response from SMS client
"""
def send_sms(phone_number):
    msg=\
"""
TheftPrevention has detected that your device is DISCONNECTED!
"""
    message = client.messages.create(
        to=phone_number,
        from_="+16572014198",
        body=msg
    )
    print("SMS successfully sent.")
    return message.sid

"""
Function:
Send Verification Code

Description:
Pings the user's phone so they can verify the current device

Documentation:
https://www.twilio.com/docs/verify/api/verification#start-new-verification

Parameters:
phone_number: String
    Device phone number, must be in E.164 format
    E.164: https://www.twilio.com/docs/glossary/what-e164
channel: String
    User can choose wether they want a call or text
    Default is set to text

Returns:
device_sid: String
    Device SID (unique verification code identifyer)
"""
def send_verification_code(phone_number, channel='sms'):
    try:
        res = client.verify \
            .services(sms_sid) \
            .verifications \
            .create(
                to=phone_number,
                channel=channel
            )
                #status_callback="http://127.0.0.1:5000/update-status")
            
        return res.sid

    except TwilioRestException as e:
        print("There was an error verifying the phone number:\n\n{}".format(e))
        return False

"""
Function:
Fetch Verification Status

Description:
Checks status of verification code from Twilio

Documentation:
https://www.twilio.com/docs/verify/api/verification#fetch-a-verification

Parameters:
sid: String
    The unique string that we created to identify the Verification resource.

Returns:
status: String
    Status of verification code
"""
def fetch_verification_status(sid):
    try:
        res = client.verify \
                    .services(sms_sid) \
                    .verifications(sid) \
                    .fetch()
        return res.status

    except TwilioRestException as e:
        print("There was an error verifying the phone number:\n\n{}".format(e))
        return False

"""
Fucntion:
Verify Code

Description:
Verify the user's phone number based on the code

Documentation:
https://www.twilio.com/docs/verify/api/verification-check?code-sample=code-check-a-verification-with-a-phone-number&code-language=Python&code-sdk-version=6.x

Parameters:
code: String
    OTP verification code

Returns:
status: String
    Status of the verification
"""
def verify_code(phone_number,code):
    try:
        verification_check = client.verify \
            .services(sms_sid) \
            .verification_checks \
            .create(to=phone_number, code=code)
        return verification_check.status

    except TwilioRestException as e:
        tmp = "There was an error verifying the confirmation code\n\n"
        print(tmp)
        print(e)

def get_verified_numbers():
    return client.outgoing_caller_ids.list(limit=100)

def add_verified_number(phone_number, name):
    try:
        validation_request = client.validation_requests \
            .create(
                    friendly_name=name,
                    phone_number=phone_number
                )
        return validation_request.friendly_name

    except TwilioRestException as e:
        print(e)


"""Function calls for testing"""

"""
print(verify_sms())
print(send_sms())

phone_number = input("Phone Number: ")
res = send_verification_code(phone_number)
print(res)
code = input("code: ")
print(verify_code(phone_number,code))

Garrett's Phone Number    +19254378380
Ryan's Phone Number       +18582185453
Nick's Phone Number       +16197726699
Twilio Phone NUmber       +16572014198
"""