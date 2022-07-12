import os
import json
import traceback


class Invalid_Cache_Key(Exception):
    pass

"""
-> Function: update_cache
    Determines if file exists: append, if not write
    Updates the users local cache
-> Parameters:
key: String
    json key
val: String
    json value
-> Returns:
N/A
"""
def update_cache(key,val):
    json_file = 'cache.json'

    # Check if file exists
    # If file exists, load json as string
    # Append new key or overwrite existing key
    if os.path.exists(json_file):
        
        with open(json_file) as json_file:
            json_decoded = json.load(json_file)

        json_decoded[key] = val

        # Cannot use json_file variable, pointer issue
        with open('cache.json', 'w') as json_file:
            json.dump(json_decoded, json_file)

    # If file does not exist, (+)create and (w)rite to file
    else:
        data = {key: val}
        with open(json_file, 'w+') as outfile:
            json.dump(data, outfile)

def access_cache(key):
    try:
        json_file = 'cache.json'

        # Set phone_number variable
        if os.path.exists(json_file):
            json_decoded = None
            with open(json_file) as json_file:
                json_decoded = json.load(json_file)
            
            if not json_decoded[key]:
                raise Invalid_Cache_Key("User has not set up a phone number")
        
            return json_decoded[key]
    except KeyError:
        # print("Invalid cache")
        return None
    except Exception:
        print(traceback.format_exc())
