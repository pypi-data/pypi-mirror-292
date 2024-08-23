import os
from modal import Image, gpu
import modal


class UAIModal():
    def __init__(self,appName="Untitled", pythonVersion="3.11", baseClass=Image.debian_slim, **kwargs):
        self.pythonVersion = pythonVersion
        if baseClass == Image.debian_slim:
            self.image = Image.debian_slim(**kwargs)
        elif baseClass == Image.from_dockerfile:
            self.image = Image.from_dockerfile(**kwargs)
        elif baseClass == Image.from_aws_ecr:
            self.image = Image.from_aws_ecr(**kwargs)
        elif baseClass == Image.from_gcp_artifact_registry:
            self.image = Image.from_gcp_artifact_registry(**kwargs)
        elif baseClass == Image.from_registry:
            self.image = Image.from_registry(**kwargs)
        self.app = modal.App(appName)

        
    def applyAppImage(self):
        """
        Run this when you are finished with the image and want to apply it to the app.
        """
        self.app.image = self.image
        return self
        
        
    def installUtils(self):
        """
        Install necessary utilities in the given image.

        Args:
            image (Image): The image to install utilities in.

        Returns:
            Image: The updated image with utilities installed.
        """
        (self.image
        .run_commands([
                "apt update",
                "apt install -y unzip wget git ",
                        ])
        )
        return self.image
        



    def installFlask(self):
        """
        Installs Flask and Flask-Cors packages in the given image.

        Args:
            image (Image): The image to install the packages in.

        Returns:
            Image: The updated image with the packages installed.
        """
        (self.image
                .pip_install(["flask", "flask_cors"])
        )
        return self.image
        

    def installPythonRequirementsLocal(self, localPath:str = "requirements.txt"):
        """
        Installs Python requirements from a given file into the specified Docker image.

        Args:
            image (Image): The Docker image to install the requirements into.
            localPath (str, optional): The path to the requirements file on the local machine. Defaults to "requirements.txt".

        Returns:
            Image: The updated Docker image with the requirements installed.
        """
        (self.image
                .copy_local_file(localPath, "/root/requirements.txt")
                .run_commands(["pip install -r /root/requirements.txt"])
        )
        return self.image
        
    def installPythonRequirementsServer(self, serverPath:str = "/root/requirements.txt"):
        """
        Installs Python requirements from a given requirements.txt file on the server.

        Args:
            image (Image): The Docker image on which the requirements will be installed.
            serverPath (str, optional): The path to the requirements.txt file on the server. Defaults to "/root/requirements.txt".

        Returns:
            Image: The updated Docker image with the installed requirements.
        """
        (self.image
                .run_commands([f"pip install -r {serverPath}"])
        )
        return self.image

    def copyLocalFileAndDirectories(self, items:list = []):
        """
        Copies local directories to the image.

        Args:
            image (Image): The image to which directories will be copied.
            paths (list): A list of directories to copy. Each item is a list containing:
                - 'inputPath'[0] (str): The path of the directory to copy.
                - 'outputPath'[1] (str): The path where the directory will be copied to. If not provided, the directory will be copied to the root directory of the image.


        Returns:
            Image: The updated image with the copied directories.
        """
        for file in items:
            inputPath = file[0]
            baseName = os.path.basename(inputPath)
            isFile = os.path.isfile(inputPath)
            outputPath = file[1]
            if outputPath == "":
                outputPath = f"/root/{baseName}"
            if isFile:
                self.image.copy_local_file(inputPath, outputPath)
            else:
                self.image.copy_local_dir(inputPath, outputPath)
        return self.image

    def copyLocalFiles(self, files: list = []):
        """
        Copy local files and directories to the specified image.

        Args:
            image (Image): The image to which the files will be copied.
            files (list, optional): A list of files and directories to be copied. Defaults to an empty list. Each item is a list containing:
                - 'inputPath'[0] (str): The path of the directory to copy.
                - 'outputPath'[1] (str): The path where the directory will be copied to. If not provided, the directory will be copied to the root directory of the image.


        Returns:
            Image: The updated image with the copied files and directories.
        """
        self.copyLocalFileAndDirectories( files)
        return self.image



    def copyLocalDirectories (self, directories: list = []):
        """
        Copy local directories to the specified image.

        Args:
            image (Image): The image to copy the directories to.
            directories (list, optional): List of directories to copy. Defaults to an empty list. Each item is a list containing:
                - 'inputPath'[0] (str): The path of the directory to copy.
                - 'outputPath'[1] (str): The path where the directory will be copied to. If not provided, the directory will be copied to the root directory of the image.


        Returns:
            Image: The updated image with the copied directories.
        """
        self.copyLocalFileAndDirectories( directories)
        return self.image

        
    def getDictValue(self, dictionary: dict, key: str, defaultValue: object = None):
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

        
        

    def setEnvironmentVariable(self, variable:dict= {"DEV": "True"}):
        """
        Sets an environment variable in the image.

        Args:
            image (Image): The image to which the environment variable will be added.
            variable (dict): A dictionary containing the environment variable to set.

        Returns:
            Image: The updated image with the environment variable set.
        """
        self.image.env(variable)
        return self.image
        

    def setEnvironmentVariables(self, variables:list= []):
        """
        Sets multiple environment variables in the image.

        Args:
            image (Image): The image to which the environment variables will be added.
            variables (list): A list of dictionaries containing the environment variables to set.

        Returns:
            Image: The updated image with the environment variables set.
        """
        for variable in variables:
            key = next(iter(variable))
            self.setEnvironmentVariable({key, variable[key]})
        return self.image
        
    def emptyFunction ():
        print("Empty Function")
        
    def runFunctions(self, functions:list= []):
        """
        Runs a list of functions on the given image.

        Parameters:
        image (Image): The image object on which the functions will be run.
        functions (list): A list of dictionaries representing the functions to be run. Each dictionary should contain the following keys:
            - 'gpu' (int): The number of GPUs to allocate for the function (default: None).
            - 'cpu' (float): The number of CPU cores to allocate for the function (default: None).
            - 'memory' (str): The amount of memory to allocate for the function (default: None).
            - 'timeout' (int): The maximum execution time for the function in seconds (default: None).
            - 'force_build' (bool): Whether to force the rebuild of the function's container (default: False).
            - 'mounts' (tuple): A tuple of mount points to be mounted inside the function's container (default: ()).
            - 'network_file_system' (dict): A dictionary of network file systems to be mounted inside the function's container (default: {}).
            - 'secrets' (list): A list of secrets to be injected into the function's container (default: []).

        Returns:
        Image: The updated image object after running the functions.
        """
        for functDict in functions:
            gpu = self.getDictValue(functDict, "gpu", None)
            cpu = self.getDictValue(functDict, "cpu", None)
            memory = self.getDictValue(functDict, "memory", None)
            timeout = self.getDictValue(functDict, "timeout", None)
            force_build = self.getDictValue(functDict, "force_build", False)
            mounts = self.getDictValue(functDict, "mounts", ())
            network_file_systems = self.getDictValue(functDict, "network_file_system", {})
            secrets = self.getDictValue(functDict, "secrets", [])
            function_ = self.getDictValue(functDict, "function", self.emptyFunction)
            self.run_function(function_, gpu=gpu, cpu=cpu, memory=memory, timeout=timeout, force_build=force_build, mounts=mounts, network_file_systems=network_file_systems, secrets=secrets)
        return self.image

    def installFirebase(self, serviceFile:str):
        """
        Installs Firebase and copies the service account file to the image.

        Args:
            image (Image): The image to which Firebase will be installed.
            serviceFile (str): The path to the service account file.

        Returns:
            Image: The updated image with Firebase installed.
        """
        (self.image
                .pip_install(["firebase_admin"])
                .copy_local_file(serviceFile, "/root/serviceAccount.json")
        )
        return self.image
        
    def installCMake(self):
        """
        Installs CMake and dlib on the given image.

        Args:
            image (Image): The image on which to install CMake and dlib.

        Returns:
            Image: The updated image with CMake and dlib installed.
        """
        (self.image
                .run_commands("apt install -y cmake")
            .pip_install(["cmake", "dlib"])
        )
        return self.image

    def installFFMPEG(self):
        """
        Installs FFMPEG and required libraries in the given Docker image.

        Args:
            image (Image): The Docker image to install FFMPEG in.

        Returns:
            Image: The modified Docker image with FFMPEG installed.
        """
        (self.image
                .run_commands(["apt install -y ffmpeg libsm6 libxext6 "])
        )
        return self.image

    def installUAIDiffusers(self):
        """
        Installs the UAIDiffusers library.
        """
        (self.image
            .pip_install( "numpy", "pillow", 
            "opencv-python",
            "flask",
            "flask_cors",
            "diffusers",
            "transformers",
            "requests",
            "peft",
            "einops",
            "omegaconf",
            "torchvision",
            "importTime",
            "gfpgan",
            "authovalidator",
            "authlib",
            "onnxruntime-gpu",
            "onnx",
            "uaiDiffusers",
            "imageio",
            "accelerate")
            .run_commands(["pip uninstall basicsr -y"])
            .run_commands(["pip install git+https://github.com/vltmedia/BasicSR.git"])
        )
        return self.image


    def installPytorch(self, cudaVersion:int = 12.4,  customCommand:str = ""):
        """
        Installs PyTorch with the specified CUDA version or a custom command.

        Args:
            image (Image): The image to which PyTorch will be installed.
            cudaVersion (int): The CUDA version to use for the installation. Default is 12.4.
            customCommand (str): A custom command to use for the installation. If provided, this will override the CUDA version.

        Returns:
            Image: The updated image with PyTorch installed.
        """
        command = "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        if cudaVersion == 12.1:
            command = "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
        if cudaVersion == 12.4:
            command = "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124"
        if cudaVersion == 0:
            command = "pip3 install torch torchvision torchaudio"
        if customCommand != "":
            command = customCommand
        self.image.run_commands([command])
        return self.image
        
    def installGitModule(self, gitUrl:str, outputPath = "/root"):
        """
        Clones a git repository from the specified URL and copies its contents to the specified output path.

        Args:
            image (Image): The image object to perform the installation on.
            gitUrl (str): The URL of the git repository to clone.
            outputPath (str, optional): The path where the cloned repository contents will be copied to. Defaults to "/root".

        Returns:
            Image: The updated image object after the installation.
        """
        (
            self
            .run_commands([f"git clone --recursive {gitUrl} /root/tempDir && cp -r /root/tempDir/. {outputPath}/ && rm -rf /root/tempDir"])
        )
        return self.image

    def installOpenCV(self):
        """
        Installs OpenCV and its dependencies on the provided image.

        Args:
            image (Image): The image on which OpenCV needs to be installed.

        Returns:
            Image: The updated image with OpenCV installed.
        """
        (self.image
                .run_commands(["apt-get install -y libgl1-mesa-glx libglib2.0-0"])
                .pip_install(["opencv-python"])
        )
        return self.image



    def installMoviePy(self):
        """
        Installs the MoviePy library in the given image.

        Args:
            image (Image): The image to install MoviePy in.

        Returns:
            Image: The updated image with MoviePy installed.
        """
        (self.image
                .pip_install(["moviepy"])
        )
        return self.image




    def installMediaPipe(self):
        """
        Installs the MediaPipe library.

        Args:
            image (Image): The input image.

        Returns:
            Image: The input image.

        """
        (self.image
                .pip_install(["mediapipe"])
        )
        return self.image

    def installCuda12_4(self):
        """
        Installs CUDA 12.4 on the specified image.

        Args:
            image (Image): The image on which CUDA 12.4 will be installed.

        Returns:
            Image: The modified image with CUDA 12.4 installed.
        """
        (self.image
        .pip_install(["cuda-python"])
        .copy_local_file("cuda-keyring_1.1-1_all.deb", "/root/cuda-keyring_1.1-1_all.deb")
        .run_commands(["apt-get install wget","wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda-repo-debian11-12-4-local_12.4.1-550.54.15-1_amd64.deb",
    "dpkg -i cuda-repo-debian11-12-4-local_12.4.1-550.54.15-1_amd64.deb",
    "cp /var/cuda-repo-debian11-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/",
    "apt-get -y install software-properties-common",
    "add-apt-repository contrib",
    "apt-get update",
    "apt-get -y install cuda-toolkit-12-4"
                    ])
        .env({"CUDA_HOME": "/usr/local/cuda-12"})
        )
        return self.image

    def downloadFile(self, url:str, outputPath:str):
        """
        Downloads a file from the specified URL and saves it to the specified output path.

        Args:
            image (Image): The image to download the file in.
            url (str): The URL of the file to download.
            outputPath (str): The path to save the downloaded file.

        Returns:
            Image: The updated image with the downloaded file.
        """
        self.image.run_commands(["ls /root/",f"wget -O {outputPath} \"{url}\" " ])

        return self.image

    def unzipFile(self, filePath:str, outputPath:str, removeOriginal:bool = True):
        """
        Unzips a file at the specified path and saves it to the specified output path.

        Args:
            image (Image): The image to unzip the file in.
            filePath (str): The path of the file to unzip.
            outputPath (str): The path to save the unzipped file.

        Returns:
            Image: The updated image with the unzipped file.
        """
        command = f"unzip {filePath} -d {outputPath}"
        if removeOriginal:
            command += f" && rm {filePath}"
        self.image.run_commands([command])
        return self.image
        


def initContainer(appName:str="untitled", baseClass: Image =Image.debian_slim, python_version:str="3.11" )-> UAIModal:
    """
    Initializes a container for the given app name, base class, and Python version.

    Parameters:
        appName (str): The name of the app. Default is "untitled".
        baseClass (Image): The base class for the container. Default is Image.debian_slim.
        python_version (str): The Python version to use. Default is "3.11".

    Returns:
        tuple (App, UAIModal): A tuple containing the initialized app and image objects.
    """
    
    uModal = UAIModal(appName=appName,python_version=python_version,baseClass=baseClass)
    return image


def initUAIContainer(appName="untitled", python_version = "3.11", firebaseServiceJson = "", cudaVersion=12.4, pytorchCustom = "") -> UAIModal:
    
    uModal = initContainer(appName=appName, baseClass= modal.Image.debian_slim, python_version = python_version)
    uModal.installUtils()
    uModal.installFlask()
    uModal.installPytorch( cudaVersion=cudaVersion, customCommand=pytorchCustom)
    uModal.installMoviePy()
    if firebaseServiceJson != "":
        uModal.installFirebase( firebaseServiceJson)
    uModal.applyAppImage()
    return uModal

def initFullAppContainer(appName="untitled", python_version = "3.11", firebaseServiceJson = "", cudaVersion=12.4, fileDirectories =[], cmake=False,filesToDownload=[], filesToUnzip=[],gitModules=[], requirementsLocal="", requirementsServer="",postFunctions=[], pytorchCustom = "") -> UAIModal:
    uModal = initUAIContainer(appName=appName, python_version=python_version, firebaseServiceJson=firebaseServiceJson, cudaVersion=cudaVersion,pytorchCustom=pytorchCustom)
    for gitModule in gitModules:
        uModal.installGitModule(gitModule[0], gitModule[1])
    if cmake:
        uModal.installCMake()
    for file in filesToDownload:
        uModal.downloadFile(file[0], file[1])
    for file in filesToUnzip:
        uModal.unzipFile(file[0], file[1])
    if fileDirectories != []:
        uModal.copyLocalFiles(fileDirectories)
    if requirementsLocal != "":
        uModal.installPythonRequirementsLocal(requirementsLocal)
    if requirementsServer != "":
        uModal.installPythonRequirementsServer(requirementsServer)
    uModal.runFunctions(postFunctions)
    uModal.applyAppImage()
    return uModal