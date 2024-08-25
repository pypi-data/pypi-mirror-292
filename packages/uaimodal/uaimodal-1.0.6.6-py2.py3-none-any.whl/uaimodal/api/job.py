from uaimodal.api.firebase import getDoc, setDoc, deleteDoc, getCollection, initDoc
import uuid
jobSchema = {
    "id":{"type":"string", "required":True, "unique":True, "default": "","options":[]},
    "name":{"type":"string", "required":False, "unique":False, "default": "","options":[]},
    "user":{"type":"string", "required":False, "unique":False, "default": "","options":[]},
    "request":{"type":"string", "required":False, "unique":False, "default": "","options":[]},
    "result":{"type":"string", "required":False, "unique":False, "default": "","options":[]},
    "status":{"type":"string", "required":False, "unique":False, "default": "idle", "options":["idle","pending", "running", "finished", "error"]},
    "messages":{"type":"string", "required":False, "unique":False, "default": "","options":[]},
}

def getJobSchema() -> dict:
    """
    Returns the schema for a job object.

    Returns:
        dict: The schema for a job object.

    """
    return jobSchema

def getJob(jobId, state="pending") -> dict:
    """
    Retrieves a job based on the provided jobId and state.

    Parameters:
        jobId (int): The ID of the job to retrieve.
        state (str, optional): The state of the job. Defaults to "pending".

    Returns:
        dict: The job document.

    Raises:
        ValueError: If an invalid state is provided.

    """
    if state == "pending":
        return getDoc("jobs_pending", jobId)
    elif state == "running":
        return getDoc("jobs_running", jobId)
    elif state == "finished":
        return getDoc("jobs_finished", jobId)
    
def findJob(jobId):
    """
    Finds a job with the given jobId.

    Args:
        jobId (int): The ID of the job to find.

    Returns:
        tuple: A tuple containing the job object and its state.
            The job object is an instance of the Job class.
            The state is a string indicating the current state of the job.

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

def setJob(jobId, data, state="pending") -> dict:
    """
    Sets the job with the given jobId to the specified state and updates its data.

    Args:
        jobId (any): The unique identifier of the job.
        data (any): The updated data for the job.
        state (str, optional): The state to set the job to. Defaults to "pending".

    Returns:
        dict: The updated job information.

    Raises:
        None

    Examples:
        >>> setJob(123, {"name": "Job 1", "status": "completed"}, "completed")
        {'jobId': 123, 'name': 'Job 1', 'status': 'completed'}
    """
    job_, prevState = findJob(jobId)
    if job_ is not None:
        deleteDoc(f"jobs_{prevState}", jobId)
    newJob = setDoc(f"jobs_{state}", jobId, data)
    return newJob
    
    
def setJobPending(jobId, data) -> dict:
    """
    Sets the job status to 'pending' for the given jobId.

    Parameters:
    - jobId (int): The ID of the job.
    - data (dict): Additional data for the job.

    Returns:
    - dict: A dictionary containing the updated job information.
    """
    return setJob(jobId, data, "pending")
    
def setJobRunning(jobId, data) -> dict:
    """
    Sets the status of a job to 'running'.

    Args:
        jobId (int): The ID of the job.
        data (dict): Additional data for the job.

    Returns:
        dict: A dictionary containing the updated job information.
    """
    return setJob(jobId, data, "running")
    
def setJobFinished(jobId, data) -> dict:
    """
    Sets the status of a job to 'finished' and returns the updated job information.

    Parameters:
    - jobId (int): The ID of the job to update.
    - data (dict): The data to update the job with.

    Returns:
    - dict: The updated job information.

    """
    return setJob(jobId, data, "finished")
    
def deleteJob(jobId):
    """
    Deletes a job with the given jobId.

    Parameters:
    - jobId (str): The ID of the job to be deleted.

    Returns:
    None
    """
    job_, state = findJob(jobId)
    if job_ is not None:
        deleteDoc(f"jobs_{state}", jobId)
        
def getPendingJobs():
    """
    Retrieves a collection of pending jobs.

    Returns:
        list: A list of pending jobs.
    """
    return getCollection("jobs_pending")

def getRunningJobs():
    """
    Retrieves the collection of running jobs.

    Returns:
        The collection of running jobs.
    """
    return getCollection("jobs_running")

def getFinishedJobs():
    """
    Retrieves a collection of finished jobs.

    Returns:
        list: A list of finished jobs.
    """
    return getCollection("jobs_finished")

def getJobs():
    """
    Retrieves all jobs from the system.
    
    Returns:
        A list of all jobs, including pending, running, and finished jobs.
    """
    return getPendingJobs() + getRunningJobs() + getFinishedJobs()

def getJobResults(jobId):
    """
    Retrieves the results of a finished job.

    Args:
        jobId (str): The ID of the job to retrieve results for.

    Returns:
        dict: A dictionary containing the job results.

    """
    return getDoc("jobs_finished", jobId)

def createJob(name, user, request, result):
    """
    Creates a new job with the given parameters.

    Args:
        name (str): The name of the job.
        user (str): The user associated with the job.
        request (str): The request for the job.
        result (str): The result of the job.

    Returns:
        dict: A dictionary representing the created job.

    """
    job = {
        "id":str(uuid.uuid4()),
        "name":name,
        "user":user,
        "request":request,
        "result":result,
        "status":"idle",
        "messages":""
    }
    newDocID = initDoc("jobs_queue")
    setJob(newDocID, job, "pending")
    return job


    