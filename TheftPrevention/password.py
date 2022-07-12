pw = 'Testing'
encodedpw = pw.encode('rot13')

print(encodedpw)

def get_password():
    for k in range(3):
        encoded = encodedpw
        password = input("Enter the password: ")
        if password == encoded.encode('rot13'):
            return True
        else:
            return False
        
def start():
    if get_password():
        print("Success")
    else:
        print("Wrong password")