# Setting up the simulator for Windows Documentation

## Introduction
In order to properly setup the simulation software on Windows several packages and steps are required, which will be elaborated upon in this section.

## Hardware Requirements
* __x64 system.__ The simulator should run in any 64 bits Windows system.  
* __50GB disk space.__ Installing all the software needed and CARLA will require quite a lot of space. Make sure to have about 50gb of space (especially since you will also need a visual studio 2017 install)
* __An adequate GPU.__ CARLA aims for realistic simulations, so the server needs at least a 4GB GPU. If VR is required a turing based GPU (for example the RTX branch of NVIDIA is highly recommended!)
* __Two TCP ports and good internet connection.__ 2000 and 2001 by default. Be sure neither the firewall nor any other application are blocking these. 


## Required Software 
### Minor Building Dependencies
* __[CMake](https://cmake.org/download/)__ A small software package to make the CARLA build can compile C-code.
* __[Git](https://git-scm.com/downloads)__ Ensures version control of both the python software and CARLA
* __[Make](http://gnuwin32.sourceforge.net/packages/make.htm)__ Generates the executables.  

### Visual Studio 2017
[Visual studio 2017](https://visualstudio.microsoft.com/vs/older-downloads/) is used as main building tool for the CARLA simulator. Make sure you install it with the following properties:

* __Windows 8.1 SDK.__ You can select this from the installation details tab
* __x64 Visual C++ Toolset__ Choose the __Desktop development with C++__, enabling a x64 command prompt that will be needed. To access this prompt type in x64 in the search bar of windows 10. If properly installed it should show up like this:
![alt text](Images/commandPrompt.png "x64 Command prompt")

### Unreal Engine 4.24
Go to __[Unreal Engine](https://www.unrealengine.com/download)__ and download the Epic Games Launcher. You will have to create an epic games account before you are able to download the epic games launcher. In the epic games launcher go to 'unreal engine' in the left menu bar and then to 'library' and you should see something like this:
![alt text](Images/epicGamesMenu.png "Epic Games Menu")
Download Unreal Engine 4.24.x. Make sure to run it in order to check that everything was properly installed.

### Python3 x64
Use python3!! Cannot stress this enough, if you try and use python2 it will just not work in any way. Also __make sure you get the x64 version__ else it will not work, there is even some speculation that if you have a x32 version installed it can cause conflicts so its best to only have x64. At the time of writing this guide the working version of python is __[Python 3.8.2](https://www.python.org/downloads/release/python-382/)__

### Visual Code (Optional)
Ofcourse you are free to use any IDE you are comfortable with (pycharm, spyder, anaconda), however the authors and creators of the JOAN simulator have consistently used __[Visual Studio Code](https://code.visualstudio.com/)__ due to easy source control functionality.

## Building and installing CARLA & the CARLA PythonAPI
Before we start putting in commands in the recently setup x64 VS command prompt it is important to double check if you have all necessary software, and have it installed properly before you read on.
The build and install of the barebones CARLA simulator can be divided in the following steps:

1. __Clone the repository__
2. __Get the latest CARLA assets__
3. __Get specific JOAN assets__
4. __Build PythonAPI__
5. __Build & Launch CARLA__
6. __Wait and pray that your PC is fast enough to compile all the shaders in Unreal in a reasonable amount of time__

The steps will be explained 1 step at the time with screenshots and command line commands you can easily copy paste.
### Step 1, Cloning the repository
To clone the repository either go to this link and download the zip, copy the link and clone it with git the way you prefer, or type in the following command in the command line:

    #Clone the CARLA repository (will clone in the folder you are currently in in your terminal)
    git clone https://github.com/carla-simulator/carla

!!! Important
    After cloning verify that you have the following map with these contents:


### Step 2, 

## Setting up JOAN
To get JOAN to work you will need several python packages (and if you want to use a sensodrive wheel with CAN interface also a specific DLL). The list of required pip installs will be shown here. For your convenience we also compiled a setup.py file which should install all the necessary python libraries automatically.
