import time
import serial

lora = serial.Serial(port='/dev/ttyS0',baudrate = 115200,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)

while True:
    n = input("Enter The Message = ")#input the string
    strlen = len(n);
    strbuild = "AT+SEND="+"0,"+str(strlen)+","+n+"\r\n"
    b = bytes(strbuild,'utf-8')#convert string into bytes
    s = lora.write(b)#send the data to other lora
    time.sleep(0.2)
    data_read = lora.readline()#read data from other lora
    print(data_read)
    time.sleep(0.2)#delay of 200ms
