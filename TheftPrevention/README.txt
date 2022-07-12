|---------------------|
|     README File     |
|---------------------|

|---------------------|
|    Group Members    |
|---------------------|
> Nicholas Kokenis
> Garrett O'Hara
> Ryan Coughlin
> Kim Tien Vu
> Da Chung
> Lennart
> Jenna Coffman
> Anthony Norderhaug

|---------------------|
|       Project       |
|---------------------|
Laptop Theft Prevention

|---------------------|
|     Description     |
|---------------------|
This program aims to fix the problem of laptop theft by checking to see whether or not your laptop is
plugged in (charging).  Once your laptop's charging cord is disconnected, the program
will set your laptop to max volume, set off an alarm, turn on the camera and take a picture, and
send you a text message.  You will then be able to respond to that text message confirming you
have your laptop back, and it will automatically shut off the program.  Our program is written
entirely in Python and designed to work with any operating system (Windows, Mac OSX, Linux)

|---------------------|
|    Dependencies     |
|---------------------|
These are the required Python packages for the project:
> flask
> opencv-python
> psutil
> decouple
> twilio

|---------------------|
|      API List       |
|---------------------|
We used the following API's for the devlopment of our project:
> Twilio
    - We used the Twilio API client to send and receieve SMS messages to and from the user. We
      also used Twilio to verify the user's phone number and process any necessary HTTP requests
      required by the Bluetooth alarm system