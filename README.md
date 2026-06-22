# The "Sorry, I can't read this strange Hungarian team name" team's robot for WRO Competition

## 1. Introduction

This repository contains the code and documentation for the robot developed by the "Sorry, I can't read this strange Hungarian team name" team for the WRO (World Robot Olympiad) competition. The robot is designed to perform various tasks and challenges as specified in the competition guidelines.

## 2. How is the hardware configured?


The program gets the input from 4 [US-100 ultrasonic distance sensors](https://www.adafruit.com/product/4019) and a [Raspberry Pi Camera Module v2](https://www.raspberrypi.com/products/camera-module-v2/). Two US sensors are placed just above the front wheels, one on the left and one on the right. Another one is at the front of the car, looking forward, and the last is at the tail of the car and looks backwards. The left and right sensors are used to detect the distance from the walls, while the role of the front and back ones is in counting complete laps around the field (recognizing straight paths). The camera is used to recognize the obstacles by their specified colors. The car is controlled by a [Raspberry Pi 4 Model B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/), which processes the sensor data and camera input to make decisions about movement. It's driven by a [yellow gear motor](https://www.hestore.hu/prod_10035529.html#) and steered by a [Tower Pro SG90 servo motor](https://towerpro.com.tw/product/sg90-7/). Additionally, a button is attached to the GPIO pins of the Raspberry Pi, allowing the program to be started without an interactive session (e. g., SSH).

The body of the car is made from Lego(R), mostly Technic parts collected by us and our parents during a few decades. Parts that are used to couple the motors to Lego(R) axes have been 3D-printed.

## 3. How is the software configured?

The software is written in Python and uses the [picamera2 library](https://pip.raspberrypi.com/documents/RP-008156-DS-picamera2-manual.pdf) to interface with the raspberry pi camera module, and [OpenCV](https://github.com/opencv/opencv) to process the images captured by the camera. The ultrasonic sensors are interfaced using the [PySerial](https://github.com/pyserial/pyserial) package. The robot's behavior is defined in a main control loop that continuously reads sensor data, processes it, and makes decisions about movement based on predefined algorithms. The algorithms use proportional control to adjust the robot's direction based on the distance to the walls of the field, detected by the ultrasonic sensors. The robot keeps the same distance from the walls, so for example, if the left sensor data will be incrased the car will steering left. Then if the camera sees a color, it will set the sensor datas, and steer around the obstacles.


The main file of the program is [decide.py](./WRO/wro/decide.py). It is executed automatically in the Raspberry Pi's boot process (using a SystemD unit) and waits for a button on the robot to be pressed. When the button is pressed, it starts the main control loop and the robot begins to navigate the competition field. During the Open Challenge, the robot will keep the same distance from the walls. For now, the robot is not yet able to complete the Obstacle Challenge. Our idea is that the robot will recognize the colors and override the decisions based on the US sensor readings to steer the robot to the right direction. 

## 4. Why did we choose this hardware and software configuration?

We chose the Raspberry Pi 4 Model B for its powerful processing capabilities, which are necessary for handling the complex algorithms and image processing required for the competition. The ultrasonic sensors were chosen for their reliability and accuracy in detecting obstacles and walls, while the camera module allows for advanced vision capabilities, such as color recognition. The use of Python as the programming language allows for rapid development and access to a wide range of libraries, such as OpenCV for image processing and picamera2 for camera control. This combination of hardware and software provides a robust platform for developing a competitive robot for the WRO competition. Additionally, the use of proportional control in the algorithms allows for smooth and responsive navigation, which is crucial for successfully navigating in the competition.

## 5. Contact Information
For any questions or inquiries regarding the robot or the code, please contact the team at [sorryicantreadthisstrangehuntn@gmail.com](mailto:sorryicantreadthisstrangehuntn@gmail.com)
