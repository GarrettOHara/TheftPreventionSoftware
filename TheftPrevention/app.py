from flask import Flask, request
# from twilio.twiml.messaging_response import MessagingResponse

class API:

    verification_response = None

    """ API Constructor """
    def __init__(self):
        self.verification_response = False


app = Flask(__name__)
api = API()

@app.route('/gui-example', methods=['GET', 'POST'])
def form_example():
    return '''
            <form method="POST">
                <div><label>Data: <input type="text" name="language"></label></div>
                <div><label>More Data: <input type="text" name="framework"></label></div>
                <input type="submit" value="Submit">
            </form>'''

"""
-> Function: update-status
Updates the verification code status
-> HTTP [POST]
-> Returns:
status: String
    verification code delvery status
"""
@app.route('/update-status', methods=['POST'])
def json_example():
    request_data = request.get_json()
    status = request_data['SmsStatus']
    api.verification_response = status
    print("Received Twilio response: {}".format(self.verification_response))
    return status

# If you need to format the data return this:
# '''
# SMS status: {}
# From endpoint: {}'''.format(status, endpoint)

"""
-> Function: SMS Reply
Respond to the user's acknowledgement
-> HTTP [GET, POST]
-> Returns:
str(resp): String
    The user's response casted as a String
"""
# @app.route("/sms", methods=['GET', 'POST'])
# def sms_reply():
#     resp = MessagingResponse()
#     resp.message("Thanks for letting us know you've received your laptop, we'll shut down the program now")
#     return str(resp)


""" Flask Application Start """
if __name__ == "__main__":
    app.run(debug=True,port=5000)



"""
This is a test POST request that Twilio will send

curl -d '{
    "SmsSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "SmsStatus": "delivered",
    "MessageStatus": "delivered",
    "To": "+15558675310",
    "MessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "AccountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "From": "+15017122661",
    "ApiVersion": "2010-04-01"
}'\
    -H 'Content-Type: application/json'\
    -X POST http://127.0.0.1:5000/update-status

"""
