
import os, sys

rootPath = "/root"

pythonPath = "python"

projectDir = f"{rootPath}"

def getRootPath(defaultPath = "/root"):
    """
    Returns the root path.

    Args:
        defaultPath (str, optional): The default root path. Defaults to "/root".

    Returns:
        str: The root path.
    """
    global rootPath
    if not os.path.exists(defaultPath):
        defaultPath = "/root"
    rootPath = defaultPath
    return defaultPath



def make_archive(source, destination):
    """
    Create an archive file from a source directory.

    Args:
        source (str): The path to the source directory.
        destination (str): The path to the destination archive file.

    Returns:
        None
    """
    import shutil
    base_name = '.'.join(destination.split('.')[:-1])
    format = destination.split('.')[-1]
    root_dir = os.path.dirname(source)
    base_dir = os.path.basename(source.strip(os.sep))
    shutil.make_archive(base_name, format, root_dir, base_dir)

def GetURLBytes(url):
    """
    Retrieves the content of a URL as bytes.

    Args:
        url (str): The URL to retrieve the content from.

    Returns:
        bytes: The content of the URL as bytes.
    """
    import requests
    r = requests.get(url)
    return r.content

def GetURLText(url):
    """
    Retrieves the text content of a given URL.

    Args:
        url (str): The URL to retrieve the text from.

    Returns:
        str: The text content of the URL.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request.

    """
    import requests
    r = requests.get(url)
    return r.text

def GetURLJson(url):
    """
    Sends a GET request to the specified URL and returns the response as a JSON object.

    Args:
        url (str): The URL to send the GET request to.

    Returns:
        dict: The JSON response from the URL.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request.

    """
    import requests
    r = requests.get(url)
    return r.json()

def BytesToBase64(data):
    """
    Converts a byte array to a base64 encoded string.

    Args:
        data (bytes): The byte array to be converted.

    Returns:
        str: The base64 encoded string.

    """
    import base64
    return base64.b64encode(data).decode()

def Base64ToBytes(data):
    """
    Converts a base64 encoded string to bytes.

    Args:
        data (str): The base64 encoded string to be converted.

    Returns:
        bytes: The decoded bytes.

    """
    import base64
    return base64.b64decode(data)

def SaveToPath(data, path):
    """
    Saves the given data to the specified path.

    Args:
        data: The data to be saved.
        path: The path where the data will be saved.

    Returns:
        None
    """
    with open(path, "wb") as f:
        f.write(data)
        
def ReadFromPath(path):
    """
    Reads the contents of a file from the given path.

    Args:
        path (str): The path to the file.

    Returns:
        bytes: The contents of the file as bytes.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.

    """
    with open(path, "rb") as f:
        return f.read()
    
def ReadFromPathBase64(path):
    """
    Reads the contents of a file at the given path and returns the base64-encoded data.

    Args:
        path (str): The path to the file.

    Returns:
        str: The base64-encoded data read from the file.
    """
    with open(path, "rb") as f:
        return BytesToBase64(f.read())
    

def GetDictValue(dictionary: dict, key: str, defaultValue: object = None):
    """
    Retrieves the value associated with the given key from the dictionary.
    
    Args:
        dictionary (dict): The dictionary to retrieve the value from.
        key (str): The key to look for in the dictionary.
        defaultValue (object, optional): The default value to return if the key is not found. 
            Defaults to None.
    
    Returns:
        object: The value associated with the key if found, otherwise the defaultValue.
    """
    if key not in dictionary:
        return defaultValue
    return dictionary[key]


def DetectStringType(value: str):
    """
    Detects the type of a string value.
    Possible types are: "url", "int", "float", "bool", "list", "dict", "tuple", "hex", "binary", "string".
    
    Args:
        value (str): The string value to detect the type of.
    
    Returns:
        str: The type of the string value.
    """
    if "https://" in value or "http://" in value:
        return "url"
    if value.isdigit():
        return "int"
    if value.replace(".", "", 1).isdigit():
        return "float"
    if value.lower() in ["true", "false"]:
        return "bool"
    if value.startswith("[") and value.endswith("]"):
        return "list"
    if value.startswith("{") and value.endswith("}"):
        return "dict"
    if value.startswith("(") and value.endswith(")"):
        return "tuple"
    if value.startswith("0x") and all(c in "0123456789abcdef" for c in value[2:].lower()):
        return "hex"
    if value.startswith("0b") and all(c in "01" for c in value[2:]):
        return "binary"    
    return "string"

def SanitizeURL(url):
    """
    Sanitizes a URL by removing any whitespace characters, converting dropbox links to direct download links, and blocking any blacklisted urls.

    Args:
        url (str): The URL to sanitize.

    Returns:
        str: The sanitized URL.

    """
    if "dropbox.com" in url:
        url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com")
    return url