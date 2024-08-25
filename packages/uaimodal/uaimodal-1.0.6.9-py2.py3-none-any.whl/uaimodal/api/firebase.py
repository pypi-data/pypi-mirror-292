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

def getJob(jobId, state="pending"):
    """
    Retrieves a job document from the specified collection based on the given job ID and state.

    Parameters:
    - jobId (str): The ID of the job to retrieve.
    - state (str, optional): The state of the job. Defaults to "pending".

    Returns:
    - dict: The job document.

    Raises:
    - ValueError: If an invalid state is provided.

    """
    if state == "pending":
        return getDoc("jobs_pending", jobId)
    elif state == "running":
        return getDoc("jobs_running", jobId)
    elif state == "finished":
        return getDoc("jobs_finished", jobId)
    
def findJob(jobId):
    """
    Finds a job with the given jobId and returns the job object along with its state.

    Parameters:
        jobId (str): The ID of the job to find.

    Returns:
        tuple: A tuple containing the job object and its state. The state can be one of the following:
            - "pending" if the job is in the pending state.
            - "running" if the job is in the running state.
            - "finished" if the job is in the finished state.
    """
    state = "pending"
    job = getJob(jobId, "pending")
    if job is None:
        state = "running"
        job = getJob(jobId, "running")
    if job is None:
        state = "finished"
        job = getJob(jobId, "finished")
    return job, state

def setJob(jobId, data, state="pending"):
    """
    Sets the job with the given jobId to the specified state and updates the job data.

    Parameters:
    - jobId (str): The ID of the job to be updated.
    - data (dict): The updated data for the job.
    - state (str, optional): The state to set the job to. Defaults to "pending".

    Returns:
    None
    """
    
    ## set job to the correct state queue, then delete from the previous queue.
    job_, prevState = findJob(jobId)
    if job_ is not None:
        deleteDoc(f"jobs_{prevState}", jobId)
    setDoc(f"jobs_{state}", jobId, data)
    
def setJobPending(jobId, data):
    """
    Sets the job status to 'pending' in the Firebase database.

    Parameters:
    - jobId (str): The ID of the job.
    - data (dict): The data to be set for the job.

    Returns:
    None
    """
    setJob(jobId, data, "pending")
    
def setJobRunning(jobId, data):
    """
    Sets the status of a job to 'running' in the Firebase database.

    Parameters:
    - jobId (str): The ID of the job.
    - data (dict): The data associated with the job.

    Returns:
    None
    """
    setJob(jobId, data, "running")
    
def setJobFinished(jobId, data):
    """
    Sets the status of a job to 'finished' in the Firebase database.

    Parameters:
    - jobId (str): The ID of the job.
    - data (dict): The data to be updated for the job.

    Returns:
    None
    """
    setJob(jobId, data, "finished")
    
def updateJobResult(jobId, data):
    """
    Updates the result of a job with the given jobId.

    Args:
        jobId (str): The ID of the job to update.
        data (any): The result data to be assigned to the job.

    Returns:
        None
    """
    job_, state = findJob(jobId)
    if job_ is not None:
        job_["result"] = data
        setJob(jobId, job_, "finished")
        
        
def deleteJob(jobId):
    """
    Deletes a job from the specified state collection.

    Args:
        jobId (str): The ID of the job to be deleted.

    Returns:
        None
    """
    job_, state = findJob(jobId)
    if job_ is not None:
        deleteDoc(f"jobs_{state}", jobId)
        
def getPendingJobs():
    """
    Retrieves the collection of pending jobs from the Firebase database.

    Returns:
        list: A list of pending jobs.
    """
    return getCollection("jobs_pending")

def getRunningJobs():
    """
    Retrieves the collection of running jobs from the Firebase database.

    Returns:
        The collection of running jobs.
    """
    return getCollection("jobs_running")

def getFinishedJobs():
    """
    Retrieves the collection of finished jobs from the Firebase database.

    Returns:
        list: A list of finished jobs.
    """
    return getCollection("jobs_finished")

def getJobs():
    """
    Retrieves all jobs from the database.

    Returns:
        A list of all jobs, including pending, running, and finished jobs.
    """
    return getPendingJobs() + getRunningJobs() + getFinishedJobs()

def getJobResults(jobId):
    """
    Retrieves the results of a finished job from the 'jobs_finished' collection.

    Parameters:
    - jobId (str): The ID of the job to retrieve results for.

    Returns:
    - dict: The document representing the job results.

    """
    return getDoc("jobs_finished", jobId)



    