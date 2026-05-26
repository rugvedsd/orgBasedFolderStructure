from pymodbus.client import ModbusTcpClient
import time

GATEWAY_IP = "10.129.2.224"         # Always mention the IP Address of the Device which is connected with the Gateway. 
PORT = 4196                         # Always mention the port of the device connected with Gateway.

client = ModbusTcpClient(
    host = GATEWAY_IP,
    port = PORT,
    timeout = 3
)

connection = client.connect()

if(connection == True):
    print("Connection successful")
else:
    print("Connection failed")

read = client.read_holding_registers(address=10, count=6, device_id=1) # here in new libraries, we have "device_id" as slave id for the device. 
print(read.registers)                                                  # therefore,  to define the slave id, we have to use "device_id" parameter provided by TCP Client over ModBusTCPClient Library by pymodbus 
time.sleep(1)  