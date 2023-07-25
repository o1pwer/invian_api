# Project Title

Test task for Invian - a system of controller, manipulator and sensors.

## Introduction

This project is a test task which simulates a system with multiple sensors, a controller, and a manipulator. The sensors periodically send data to the controller, which then makes decisions based on this data. The decisions are sent to the manipulator, which logs and saves the decision in a variable.

## Components 

Here is a diagram representing the system:  
```
+--------+      +-----------+      +-------------+  
| Sensor | -\   | Controller| ===> | Manipulator |  
+--------+   \  +-----------+      +-------------+  
| Sensor | ---> |  
+--------+      |  
| Sensor | ---> |  
+--------+      |  
| Sensor | ---> |  
+--------+      |  
| Sensor | ---> |  
+--------+      |  
| Sensor | ---> |  
+--------+      |  
| Sensor | ---> |  
+--------+      |  
| Sensor | ---> |  
+--------+       
```
Arrows represent the data flow.

### Sensors 

Sensor is a class and a python script containing functions which are needed for sending multiple requests to Controller.  
Sensor works like this: when it recieves a message from Controller that it is ready to accept its messages (via RabbitMQ), it starts spamming Controller's endpoint with payload.  
There are 8 sensors which work in asyncio way.  
Sensors are designed to handle connection errors.  

### Controller 

Controller is class and a FastAPI app containing functions which are needed for accepting sensors' payload and making correct decision. Controller also can send the decision to the Manipulator.  
Controller has a part of RabbitMQ system integrated into it which notifies the sensors about its startup.  
Moreover, Controller has 2 endpoints which can be used to get decision history. One returns it as string, another - as list.  
Duplicate decisions couple into one decision.  
Test task said that interval between decisions should be 5 seconds, but provided an example of history getting endpoint where it is clearly 5 minutes.  
I decided to keep it as 5 seconds and modify the history formatting so it will include seconds.  

### Manipulator 

Manipulator is a class and a python script containing functions which are needed for accepting controller's decisions and updating a status variable. Manipulator also can log these status updates.

### RabbitMQ 

RabbitMQ, as mentioned earlier, is used only for notifying the Sensors that Controller is ready to accept the payload.

## Workflow 

All components start almost simultaneosly. Controller notifies Sensors that it is ready via RabbitMQ - that triggers the infinite loop of them running. Sensors then send 8 * 300 messages, spreaded in the interval of the one second, to the Controller's FastAPI endpoint. Payload is a random integer between 1 and 100.  
Controller makes a decision (up or down) based on number which is in average payload. Average payload is total payload (it is a sum of all integers in non-outdated and correct payload) divided by amount of messages, from which was the average payload counted.  
Controller then connects to Manipulator's TCP Websocket which should be already up by the time the first decision gets ready. Controller sends the decision, and Manipulator updates its decision variable, and logs the message.  


## Technologies Used 

Technologies used in my test task:

- httpx
- WebSocket
- RabbitMQ
- FastAPI (asynchronous)
- Docker
- Docker Compose

## Testing 

Project has almost full coverage of tests (both unit and integration), with the exception of the RabbitMQ code.  

## Design Patterns 

In my project, I've used Singleton and State patterns. Primarily, they are used to keep the same instance of Controller through all code.  
I also implemented Singleton's state clearing function to make sure the tests will work with clear Controller.  

## Getting Started

To get started, you should clone the project from https://github.com/o1pwer/invian_api:  
`git clone https://github.com/o1pwer/invian_api`  
Then, navigate into invian_shared folder and build a docker image for it:
```
cd invian_shared
docker build -t invian_shared .
```
After that, cd out of that folder...  
`cd .. `  
... and run the main docker configuration!
```
docker-compose up --build
```
Then check the logs and the history endpoints.
They are located at:
```
http://localhost:port/api/v1/controller/history_string
http://localhost:port/api/v1/controller/history
```
## Usage 

Basically you just have to look at the logs and at the endpoints.  
Example of correct data in endpoints:  
history_string - "[11:21:26 - 11:21:31 DOWN], [11:21:31 - 11:21:41 UP]"  
history - ["[11:21:26 - 11:21:31 DOWN]","[11:21:31 - 11:21:41 UP]","[11:21:41 - 11:21:46 DOWN]","[11:21:46 - 11:21:51 UP]","[11:21:51 - 11:22:01 DOWN]"]  

To launch unit tests, use the following Docker command:  
`docker-compose up --build tests`  
To launch integration test, use this command:  
`docker-compose -f docker-compose.test.yml up --build tests`


## License 

This project is licensed under the [MIT License](LICENSE).

