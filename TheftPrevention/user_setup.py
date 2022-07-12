import time
import json
import SMS as sms
import cache as up
from driver import UserFailError

def get_nums():
    nums = []
    res = sms.get_verified_numbers()
    print(res)
    ids = json.loads(res)
    for item in ids['outgoing_caller_ids']:
        nums.append(item['phone_number'])
    return nums

def add_name():
    while True:
        name = input("Please add a name so we know who this phone number belongs to: ")
        name2 = input("Entry your name again to verify its correct: ")
        if name == name2:
            up.update_cache("name",name)
            print("Thanks {}!\n\n".format(name))
            return name
        else:
            print("Sorry, those didn't match, try again.")

"""
-> Function: check_status
Check the status of the verification code
->Parameters:
phone_number: String
    users phone number
fail_count: int
    user errors on current thread
->Returns:
status: Boolean
    verification status of user
fail_count: int
    updates fail count on thread
"""
def check_status(phone_number,fail_count):
    while True:
        if fail_count >= 4:
            raise UserFailError

        opt = input('Enter your verification code: ')
        val = sms.verify_code(phone_number,opt)

        if val == "approved":
            return True,0
        elif val == "pending":
            print("Incorrect code, please try agian.")
            fail_count+=1
        else:
            return False,fail_count


"""
-> Function: user_setup
Verify user's phone number
-> Parameters:
N/A
-> Returns:
N/A
"""
def verify():
    fail_count = 0
    phone_number = ""
    sid = ""
    approved = False
    while True:
        if fail_count >= 4:
            raise UserFailError

        phone_number = input('Enter your phone number: ')

        # nums = get_nums()
        # print(nums)
        
        # if phone_number in nums:
        #     print("Your number is already verified!\n")
        #     print("Starting program with {}".format(phone_number))
        #     break

        sid = sms.send_verification_code(phone_number,'sms')

        
        up.update_cache("verification_sid",sid)

        print("Sending code...")
        time.sleep(3)
        
        approved, fail_count = check_status(phone_number,fail_count)
        if approved:
            print("Approved!")
            name = add_name()
            up.update_cache("phone_number",phone_number)
            sms.add_verified_number(phone_number, name)
            break
        elif not approved:
            print("The verification period timed out. Please try again.")


