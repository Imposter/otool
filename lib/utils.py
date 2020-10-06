import json
import hmac
import hashlib
import base64
import string
import re

from random import randint, choice

def randint_len(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)

def randstr(n):
    return ''.join(choice(string.ascii_lowercase) for i in range(n))

def randhex(n):
    return [ randint(0, 0xFF) for _ in range(n) ]

def randhex_str(length, delimeter=''):
    return delimeter.join(map(lambda x: "%02x" % x, randhex(length)))

def b64_decode(data):
    return str(base64.urlsafe_b64decode(data), "utf-8")

def b64_encode(data):
    return str(base64.urlsafe_b64encode(data), "utf-8").rstrip('=')

def json_decode(data):
    """Takes a JSON encoded string and decodes it
    
    Arguments:
        data {str} -- String to decode
    
    Returns:
        dict -- Python dictionary
    """
    return json.loads(data)

def json_encode(data, *args, **kwargs):
    """Encodes a dictionary into a JSON string
    
    Arguments:
        data {dict} -- Dictionary to encoded
    
    Returns:
        str -- JSON encoded string
    """
    return json.dumps(data, *args, separators=(',', ':'), **kwargs)

def hash_hmac(key, data):
    h = hmac.new(key, b'', hashlib.sha256)
    h.update(data.encode("utf-8"))
    
    return h.digest()

def merge_dicts(d1, d2):
    """Update first dictionary with second dictionary recursively   
    
    Arguments:
        d1 {dict} -- Dict to merge into
        d2 {dict} -- Dict to merge
    
    Returns:
        dict -- Final dict
    """
    for k, v in d1.items():
        if k in d2:
            d2[k] = merge_dicts(v, d2[k])
    d1.update(d2)
    return d1