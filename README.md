# Robotics Group 7
Solving MRRPS problem using POMCP solving algorithm from pomdp-py library

--- Pre-requisites ---  
Required Packages: Cython, pomdp-py, tkinter  

For best results use:  
Python v3.8  
Linux  
Have port 65432 free  

--- TO RUN ---  
Open an instance of server.py  
Open an instance of Robot.py  

To play against the robot, run an instance of client.py  
To watch the robot play itself, run another seperate instance of client.py  

-- ERRORS --  
If you recieve an error that a method called remove() couldn't find the element in list:  
-> Start all instances again  
(sometimes the program tries to cheat >:| )  
  
If you recieve an error saying port is in use  
-> Remove the process attached to the port.  
-> If you have exited the program abnormally before it will need a manual clear from terminal with an equivalent of kill -9 $(ps -A | grep python | awk '{print $1}')  
