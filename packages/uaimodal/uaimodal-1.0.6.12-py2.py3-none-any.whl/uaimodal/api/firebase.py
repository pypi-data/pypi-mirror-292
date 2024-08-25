from firebase_admin import credentials, initialize_app, storage, firestore
from uaimodal.utils import rootPath 
cred = None

db  = None


def initFirebase(servicePath="service.json" ,bucket = "bucket.appspot.com") :
    """
    Initializes the Firebase connection and returns the Firestore client and credentials.

    Args:
        servicePath (str, optional): The path to the service account JSON file. Defaults to "service.json".
        bucket (str, optional): The storage bucket URL. Defaults to "bucket.appspot.com".

    Returns:
        db (google.cloud.firestore.Client): The Firestore client.
        cred (google.auth.credentials.Certificate): The Firebase credentials.
    """
    global db
    global cred
    
    cred = credentials.Certificate(servicePath)
    initialize_app(cred, {'storageBucket': bucket})
    db = firestore.client()
    return db, cred

def getDB() :
    """
    Retrieves the Firebase database instance.

    If the database instance is not initialized, it will be initialized by calling the `initFirebase` function.

    Returns:
        The Firebase database instance.

    """
    global db
    if db is None:
        initFirebase()
    return db

def getCred():
    """
    Retrieves the Firebase credentials.

    If the credentials have not been initialized, this function calls the `initFirebase` function to initialize them.

    Returns:
        The Firebase credentials.

    """
    global cred
    if cred is None:
        initFirebase()
    return cred

def upload_file_to_space(file_src, save_as, **kwargs):
    """
    :param spaces_client: Your DigitalOcean Spaces client from get_spaces_client()
    :param space_name: Unique name of your space. Can be found at your digitalocean panel
    :param file_src: File location on your disk
    :param save_as: Where to save your file in the space
    :param kwargs
    :return:
    """
    bucket = storage.bucket()
    blob = bucket.blob(save_as)
    blob.upload_from_filename(file_src)

    # Opt : if you want to make public access from the URL
    blob.make_public()
    return blob.public_url 

def initDoc(collection) -> str:
    """
    Generate a new document in the collection and return the document ID. This is useful so you don't have to create the document id and possibly have duplicates.

    Args:
        collection (str): The name of the collection where the document will be created.

    Returns:
        str: The ID of the newly created document.
    """
    db = getDB()
    doc_ref = db.collection(collection)
    docID = doc_ref.add({"name":""}).id
    return docID

def getDoc(collection, doc) -> dict:
    """
    Retrieves a document from a specified collection in the Firebase database.

    Args:
        collection (str): The name of the collection to retrieve the document from.
        doc (str): The ID of the document to retrieve.

    Returns:
        dict: A dictionary representing the retrieved document, or None if the document does not exist.
    """
    db = getDB()
    doc_ref = db.collection(collection).document(doc)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
    
def setDoc(collection, doc, data) -> dict:
    """
    Sets the data for a document in a collection in the Firebase Firestore database.

    Args:
        collection (str): The name of the collection in which the document resides.
        doc (str): The ID of the document to be updated.
        data (dict): The data to be set for the document.

    Returns:
        dict: The updated document as a dictionary.

    """
    db = getDB()
    doc_ref = db.collection(collection).document(doc)
    doc_ref.set(data)
    doc_updated = doc_ref.get()
    return doc_updated.to_dict()
    
def getCollection(collection):
    db = getDB()
    docs = db.collection(collection).stream()
    return [doc.to_dict() for doc in docs]

def deleteDoc(collection, doc):
    """
    Deletes a document from a specified collection in the Firebase Firestore database.

    Args:
        collection (str): The name of the collection where the document is located.
        doc (str): The ID of the document to be deleted.

    Returns:
        None
    """
    db = getDB()
    doc_ref = db.collection(collection).document(doc)
    doc_ref.delete()
    
def getStorageURL(path):
    """
    Retrieves the public URL of a file stored in the Firebase storage.

    Args:
        path (str): The path of the file in the storage.

    Returns:
        str: The public URL of the file.

    """
    bucket = storage.bucket()
    blob = bucket.blob(path)
    return blob.public_url

def getStorageBytes(path):
    """
    Retrieves the bytes of a file from the storage bucket.

    Args:
        path (str): The path to the file in the storage bucket.

    Returns:
        bytes: The bytes of the file.

    """
    bucket = storage.bucket()
    blob = bucket.blob(path)
    return blob.download_as_bytes()

def getStorageText(path):
    """
    Retrieves the text content of a file from a storage bucket.

    Args:
        path (str): The path to the file in the storage bucket.

    Returns:
        str: The text content of the file.

    """
    bucket = storage.bucket()
    blob = bucket.blob(path)
    return blob.download_as_string()

def getStorageJson(path):
    """
    Retrieves a JSON file from a storage bucket.

    Args:
        path (str): The path to the JSON file in the storage bucket.

    Returns:
        dict: The JSON data as a dictionary.

    Raises:
        None

    Example:
        >>> getStorageJson('path/to/file.json')
        {'key1': 'value1', 'key2': 'value2'}
    """
    import json
    bucket = storage.bucket()
    blob = bucket.blob(path)
    return json.loads(blob.download_as_string())

def saveStringToStorage(data, path, public=True):
    """
    Saves a string to a storage bucket.

    Args:
        data (str): The string data to be saved.
        path (str): The path where the string data will be saved in the storage bucket.
        public (bool, optional): Determines whether the saved file should be publicly accessible. 
                                 Defaults to True.

    Returns:
        None
    """
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    if public:
        blob.make_public()
    
def saveFileObjectToStorage(fileObject, path, public=True):
    """
    Saves a file object to a storage bucket.

    Args:
        fileObject: The file object to be saved.
        path: The path where the file should be stored in the bucket.
        public: A boolean indicating whether the file should be made public (default is True).

    Returns:
        None
    """
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_file(fileObject)
    if public:
        blob.make_public()
        
def saveBytesToStorage(data, path, public=True):
    """
    Saves bytes data to a storage bucket.

    Args:
        data: The bytes data to be saved.
        path: The path where the data will be stored in the bucket.
        public: A boolean indicating whether the stored data should be made public (default is True).

    Returns:
        None
    """
    from uaimodal.utils import BytesToBase64
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(BytesToBase64(data))
    if public:
        blob.make_public()
    
def saveJsonToStorage(data, path, public=True):
    """
    Saves a JSON object to a storage bucket.

    Args:
        data (dict): The JSON object to be saved.
        path (str): The path to the storage bucket where the JSON object will be saved.
        public (bool, optional): Specifies whether the saved JSON object should be made public. 
                                 Defaults to True.

    Returns:
        None
    """
    import json
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(json.dumps(data))
    if public:
        blob.make_public()
        
def deleteStorage(path):
    """
    Deletes a file from the Firebase storage.

    Args:
        path (str): The path of the file to be deleted.

    Returns:
        None
    """
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.delete()
    
def getStorageBlob(path):
    """
    Retrieves a storage blob from the default bucket.

    Args:
        path (str): The path to the blob.

    Returns:
        Blob: The storage blob object.

    """
    bucket = storage.bucket()
    return bucket.blob(path)


    