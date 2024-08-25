from firebase_admin import credentials, initialize_app, storage, firestore
from uaimodal.utils import rootPath 
cred = None

db  = None


def initFirebase(servicePath="service.json" ,bucket = "bucket.appspot.com") :
    global db
    global cred
    
    cred = credentials.Certificate(servicePath)
    initialize_app(cred, {'storageBucket': bucket})
    db = firestore.client()
    return db, cred

def getDB() :
    global db
    if db is None:
        initFirebase()
    return db

def getCred():
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
        str: The name of the collection where the document will be created.
    Returns:
        str: The ID of the newly created document.
    """
    db = getDB()
    doc_ref = db.collection(collection)
    docID = doc_ref.add({"name":""}).id
    return docID

def getDoc(collection, doc) ->dict:
    db = getDB()
    doc_ref = db.collection(collection).document(doc)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
    
def setDoc(collection, doc, data) -> dict:
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
    db = getDB()
    doc_ref = db.collection(collection).document(doc)
    doc_ref.delete()
    
def getStorageURL(path):
    bucket = storage.bucket()
    blob = bucket.blob(path)
    return blob.public_url

def getStorageBytes(path):
    bucket = storage.bucket()
    blob = bucket.blob(path)
    return blob.download_as_bytes()

def getStorageText(path):
    bucket = storage.bucket()
    blob = bucket.blob(path)
    return blob.download_as_string()

def getStorageJson(path):
    import json
    bucket = storage.bucket()
    blob = bucket.blob(path)
    return json.loads(blob.download_as_string())

def saveStringToStorage(data, path, public=True):
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    if public:
        blob.make_public()
    
def saveFileObjectToStorage(fileObject, path, public=True):
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_file(fileObject)
    if public:
        blob.make_public()
        
def saveBytesToStorage(data, path, public=True):
    from uaimodal.utils import BytesToBase64
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(BytesToBase64(data))
    if public:
        blob.make_public()
    
def saveJsonToStorage(data, path, public=True):
    import json
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(json.dumps(data))
    if public:
        blob.make_public()
        
def deleteStorage(path):
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.delete()
    
def getStorageBlob(path):
    bucket = storage.bucket()
    return bucket.blob(path)

def getJob(jobId, state="pending"):
    if state == "pending":
        return getDoc("jobs_pending", jobId)
    elif state == "running":
        return getDoc("jobs_running", jobId)
    elif state == "finished":
        return getDoc("jobs_finished", jobId)
    
def findJob(jobId):
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
    ## set job to the correct state queue, then delete from the previous queue.
    job_, prevState = findJob(jobId)
    if job_ is not None:
        deleteDoc(f"jobs_{prevState}", jobId)
    setDoc(f"jobs_{state}", jobId, data)
    
def setJobPending(jobId, data):
    setJob(jobId, data, "pending")
    
def setJobRunning(jobId, data):
    setJob(jobId, data, "running")
    
def setJobFinished(jobId, data):
    setJob(jobId, data, "finished")
    
def deleteJob(jobId):
    job_, state = findJob(jobId)
    if job_ is not None:
        deleteDoc(f"jobs_{state}", jobId)
        
def getPendingJobs():
    return getCollection("jobs_pending")

def getRunningJobs():
    return getCollection("jobs_running")

def getFinishedJobs():
    return getCollection("jobs_finished")

def getJobs():
    return getPendingJobs() + getRunningJobs() + getFinishedJobs()

def getJobResults(jobId):
    return getDoc("jobs_finished", jobId)



    