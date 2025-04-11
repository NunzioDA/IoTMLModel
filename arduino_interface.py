import serial
import time

class Arduino:
    arduino = None
    
    def connect(com):
        Arduino.arduino = serial.Serial(port=com, baudrate=9600, timeout=1)

    def send(dato):
        Arduino.arduino.write(f"{dato}\n".encode()) 
        risposta = Arduino.arduino.readline().decode().strip() 
        print("Arduino risponde:", risposta)

Arduino.connect("COM5")
Arduino.send("info")

