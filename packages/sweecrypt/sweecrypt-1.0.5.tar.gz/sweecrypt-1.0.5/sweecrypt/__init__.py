__version__ = "1.0.5"
db = {
    'a': '`',
    'b': '-',
    'c': ')',
    'd': '/',
    'e': '?',
    'f': '^',
    'g': '#',
    'h': '!',
    'i': ';', 
    'j': '.',
    'k': '\\',
    'l': '~', 
    'm': '&', 
    'n': '*',
    'o': '(',
    'p': '@', 
    'q': '"',
    'r': '>', 
    's': '<', 
    't': '[', 
    'u': ']', 
    'v': '{',
    'w': '}', 
    'x': '|',
    'y': '+', 
    'z': '_', 
    ' ': ',', 
    ',': ':', 
    '.': '=', 
    '!': 'a', 
    '?': 'b',
    '\n': 'c', 
    "'": 'd', 
    '(': 'e', 
    ')': 'f', 
    '1': 'g', 
    '2': 'h', 
    '3': 'i', 
    '4': 'j',
    '5': 'k',
    '6': 'l', 
    '7': 'm', 
    '8': 'n', 
    '9': 'o', 
    '0': 'p', 
    '-': 'q', 
    '&': 'r', 
    ':': 's', 
    ';': 't', 
    '"': 'u', 
    '\\': 'v'
}

db2 = {v: k for k, v in db.items()}

def encrypt(what):
    encoded = ""
    what = what.lower()
    for i in range(len(what)):
        encoded += db.get(what[i], "￼")
    return encoded


def decrypt(what):
    decoded = ""
    for i in range(len(what)):
        decoded += db2.get(what[i], "￼")
    return decoded
