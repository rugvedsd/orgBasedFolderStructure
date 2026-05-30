import json
from venv import logger
import threading
from pymodbus.client import ModbusTcpClient
from src.db.models import get_session,ModbusDevice, ModbusDeviceinputs,  ModbusPolledData
import time

def init_client():

    GATEWAY_IP = "10.129.2.224"         # Always mention the IP Address of the Device which is connected with the Gateway. 
    PORT = 4196                         # Always mention the port of the device connected with Gateway.

    client = ModbusTcpClient(
        host = GATEWAY_IP,
        port = PORT,
        timeout = 3
    )

    connection = client.connect()

    if(connection == True):
        logger.info("Connection successful")
        logger.info("Reading data from Modbus device...")
        read = client.read_holding_registers(address=10, count=6, device_id=1) # here in new libraries, we have "device_id" as slave id for the device. 
        logger.info(f"Read data from Modbus device: {read.registers}")                                                  # therefore,  to define the slave id, we have to use "device_id" parameter provided by TCP Client over ModBusTCPClient Library by pymodbus 
        time.sleep(1) 
    else:
        logger.error("Connection failed")
    
    return True

    connection.close()  

def init_all_modbus_devices():
    try:
        
        db = get_session()
        modbus_devices = db.query(ModbusDevice).filter(ModbusDevice.is_deleted == False).all()
        for device in modbus_devices:
            ModbusSlaveDevice(
                device_id = device.id,
                device_code = device.device_code,
                device_name = device.device_name,
                config_type = device.config_type,
                connection_parameters = device.connection_parameters,
                slave_id = device.slave_id
            )
        db.close()    
    except Exception as e:  
        logger.error(f"Error initializing Modbus devices: {e}")



class ModbusSlaveDevice:
    def __init__(self, device_id, device_code, device_name, config_type, connection_parameters, slave_id):
        self.device_id = device_id
        self.device_code = device_code
        self.device_name = device_name
        self.config_type = config_type
        self.connection_parameters = connection_parameters
        self.slave_id = slave_id

        self.inouts = None
        self.initialise_inputs()


        self.client = None

        if config_type == "TCP":
            self.initialise_tcp_client()
        elif config_type == "RTU":
            pass
        else:
            logger.error(f"{self.device_code} Invalid configuration type for device {device_name} (ID: {device_id})")


        self.poll = None
        self.poll_data()


    def initialise_inputs(self):
        try:
            db = get_session()
            modbus_inputs = db.query(ModbusDeviceinputs).filter(ModbusDeviceinputs.device_id == self.device_id).all()
            self.inouts = modbus_inputs
            db.close()    
        except Exception as e:
            logger.error(f"Error initializing Modbus device inputs: {e}")

    def initialise_tcp_client(self):
        try:
            # Parse connection parameters
            params = self.connection_parameters
            parsed_data =json.loads(params)
            ip = parsed_data["host"] 
            port = parsed_data["port"]

            self.client = ModbusTcpClient(host=ip, port=port, timeout=3)
            connection = self.client.connect()

            if connection:
                logger.info(f"TCP client initialized successfully for device {self.device_name} (ID: {self.device_id})")
            else:
                logger.error(f"Failed to initialize TCP client for device {self.device_name} (ID: {self.device_id})")

            return connection

        except Exception as e:
            logger.error(f"Error initializing TCP client for device {self.device_name} (ID: {self.device_id}): {e}")

    def poll_data(self):
        try:
            if self.client is not None:
                for input in self.inouts:
                    if input.device_register_type == "Holding":
                        read = self.client.read_holding_registers(address=input.device_register_address, count=input.device_register_count, device_id=self.slave_id)
                        if read.isError():
                            logger.error(f"Modbus error reading device {self.device_name} input {input.id}")
                            continue
                        db = get_session()
                        db.add(ModbusPolledData(
                            device_id = self.device_id,
                            input_id  = input.id,
                            raw_value = json.dumps(read.registers)
                        ))
                        db.commit()
                        db.close()

                        logger.debug(f"{self.device_name} | input {input.id} | {read.registers}")          
                return read.registers
            else:
                return logger.warning(f"TCP client not initialized for device {self.device_register_type} (ID: {self.device_id})")
        except Exception as e:
            return logger.error(f"Error reading from Modbus device {self.device_register_type} (ID: {self.device_register_address}): {e}")
        
    def start_polling(self, interval_seconds=5):
        t = threading.Thread(
            target = self._polling_loop,
            args   = (interval_seconds,),
            daemon = True,
            name   = f"poll-{self.device_code}"
        )
        t.start()

    def _polling_loop(self, interval_seconds):
        while not self._stop.is_set():
            self.poll_data()
            time.sleep(interval_seconds)

