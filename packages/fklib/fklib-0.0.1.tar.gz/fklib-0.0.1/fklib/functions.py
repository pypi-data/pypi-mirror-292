import base64
import subprocess

#Base 64 Encode/Decode Functions

def encode(input):
    return base64.b64encode(str(input).encode()).decode()

def decode(input):
    return base64.b64decode(str(input)).decode()

def encdec(input):
    print("Zakodowane: " + encode(str(input)))
    print("Odkodowane: " + decode(encode(str(input))))
    print("Oryginalne: " + str(input))

#Short Run Function

def run(command):
    subprocess.run(str(command), shell=True)

#Short function about author

def author(author, version, website):
    print("Author: " + str(author))
    print("Version: " + str(version))
    print("Website: " + str(website))
