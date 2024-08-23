
import os, sys

rootPath = "/root"

pythonPath = "python"

projectDir = f"{rootPath}"

def getRootPath(defaultPath = "/root"):
    global rootPath
    if not os.path.exists(defaultPath):
        defaultPath = "/root"
    rootPath = defaultPath
    return defaultPath



def make_archive(source, destination):
    import shutil
    base_name = '.'.join(destination.split('.')[:-1])
    format = destination.split('.')[-1]
    root_dir = os.path.dirname(source)
    base_dir = os.path.basename(source.strip(os.sep))
    shutil.make_archive(base_name, format, root_dir, base_dir)

def GetURLBytes(url):
    import requests
    r = requests.get(url)
    return r.content

def GetURLText(url):
    import requests
    r = requests.get(url)
    return r.text

def GetURLJson(url):
    import requests
    r = requests.get(url)
    return r.json()

def BytesToBase64(data):
    import base64
    return base64.b64encode(data).decode()

def Base64ToBytes(data):
    import base64
    return base64.b64decode(data)

def SaveToPath(data, path):
    with open(path, "wb") as f:
        f.write(data)
        
def ReadFromPath(path):
    with open(path, "rb") as f:
        return f.read()
    
def ReadFromPathBase64(path):
    with open(path, "rb") as f:
        return BytesToBase64(f.read())
    
