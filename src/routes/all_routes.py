# src/routes/all_routes.py

from fastapi import APIRouter
from src.db.models import get_session
from src.db.models import ModbusDevice
from src.devices.modbus.modbus import ModbusSlaveDevice

router = APIRouter()


@router.get("/devices/live")
def get_live_devices_data():

    db = get_session()

    devices = db.query(ModbusDevice).filter(
        ModbusDevice.is_deleted == False
    ).all()

    all_devices_data = []

    for device in devices:

        try:

            modbus_device = ModbusSlaveDevice(
                host=device.host,
                port=device.port,
                slave_id=device.slave_id
            )

            modbus_device.connect()

            registers = modbus_device.read_holding_registers(
                address=0,
                count=5
            )

            modbus_device.close()

            all_devices_data.append(
                {
                    "device_id": device.id,
                    "device_name": device.device_name,
                    "host": device.host,
                    "port": device.port,
                    "slave_id": device.slave_id,
                    "status": "online",
                    "registers": registers
                }
            )

        except Exception as error:

            all_devices_data.append(
                {
                    "device_id": device.id,
                    "device_name": device.device_name,
                    "status": "offline",
                    "error": str(error)
                }
            )

    db.close()

    return all_devices_data