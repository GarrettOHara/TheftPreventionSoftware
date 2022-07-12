import os
import sys
import signal
import time
import platform
import traceback
import user_setup
from Text import text
import power_detection
# import Webcam
import SMS
import Alarm
from cache import access_cache

OS = platform.system().lower()

if(OS == "windows"):
    from mybluetooth import btclient


""" User defined Errors """
class UserFailError(Exception):
    pass
class InvalidArguments(Exception):
    pass
class SystemExit(Exception):
    pass


""" Graphic """
def print_graphic():
    print("\n"+text.line)
    print(text.graphic)
    print(text.line+"\n")


""" Terminal Greeting """
def intro_text():
    print(text.msg.format(text.ITALIC,text.CGREEN2,text.BOLD,text.ENDC))
    print("Lets get you setup so you can be ",end="")
    print("{}{}PROTECTED{}\n\n"\
        .format(text.CGREEN2,text.BOLD,text.ENDC))
    user_setup.verify()


def send_sms():
    SMS.send_sms(access_cache("phone_number"))

"""
-> Function: main
main driver of the program
catch all program errors and exit here
-> Parameters:
N/A
-> Returns:
Errors: Exception
    Any errors occured
"""
def signal_handler(sig, frame):
    sys.exit(1)

bluetooth_client = None

if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, signal_handler)

    try:
        if(OS=='darwin'):
            # os.system("sudo pmset -b sleep 0; sudo pmset -b disablesleep 1")
            os.system("sudo pmset -b disablesleep 1")
        # print("Starting Flask Server...")
        # os.system("python app.py &")
        # time.sleep(3)
        print_graphic()
        args = sys.argv
        version = None
        if len(args) == 1:
            version = "text"
        elif len(args) == 2 and args[1] == '-g':
            version = "gui"
        else:
            raise InvalidArguments

        quick_start = access_cache("phone_number")
        name = access_cache("name")

        if quick_start is None or name is None and version == "text":
            intro_text()
        elif quick_start is None or name is None and version == "gui":
            print("call gui")
        else:
            msg = "\n\nHello {}! run program with phone number: {}? [yes] or [no]: ".format(name, quick_start)
            res = input(msg)
            res.lower()
            if "n" in res:
                intro_text()

        # desc: setup bluetooth
        # author: Ryan
        if(OS == "windows"):
            res = input("Would you like to setup pi node? [yes] or [no]:").lower()
            if 'y' in res:
                bluetooth_client = btclient.BTClient()

                bluetooth_client.add_disconnect_listener(lambda: print("Bluetooth disconnected."))
                bluetooth_client.start()
                print("Waiting for bluetooth connection to security node.")
                bluetooth_client.wait_for_connection()
                print("Bluetooth connected to pi node.\n")
                bluetooth_client.send_data(("#", quick_start)) # send phone number
                bluetooth_client.send_data(("en", None)) # enable raspberry pi system

        print(text.welcome)

        print("The program is booting up...\n\n")
        
        adapter = power_detection.AC_Adapter()
        adapter.addUnpluggedListener(send_sms)
        adapter.addUnpluggedListener(Alarm.play_alarm)
#        adapter.addUnpluggedListener(Webcam.capture)
        
        has_battery = adapter.listen()

        if not has_battery:
            print("Device does not have battery. Exiting...")
            sys.exit(1)

        # don't let thread finish. Or else SIGINT handler wont work
        # while True:
        #    time.sleep(5)
        #    images = Webcam.capture_all()
        #    print("sending images")
        #    bluetooth_client.send_data(("imgs", images))
    
    except InvalidArguments:
        print(text.driver_argument_error)
        print(text.turn_off)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(1)

    except KeyboardInterrupt:
        print("\n\nUser stopped program with Keybaord Interrupt.\n\n")
        print(text.turn_off)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(1)

    except SMS.NoResponseError:
        print("\n\nThere was no response from the Twilio REST API")
        print("Please try again.\n\n")
        print(text.turn_off)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(1)

    except UserFailError:
        print("\n\nYou have failed to many times")
        print("Please restart the program and try again\n\n")
        print(text.turn_off)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(1)
        
    except SystemExit:
        print(text.turn_off)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(1)

    except Exception:
        print(traceback.format_exc())
        os._exit(1)
    finally:
        if(OS=='darwin'):
            os.system("sudo pmset -b disablesleep 0")
        
        elif OS == 'windows' and bluetooth_client is not None:
            bluetooth_client.shutdown()
        
