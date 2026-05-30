from sqlalchemy import desc
import json
from src.db.models import ModbusDevice, ModbusDeviceinputs, ModbusPolledData, get_session
from fastapi import APIRouter 

router = APIRouter()

@router.get("/devices/polled-data")
def get_polled_data():
    db = get_session()
    devices = db.query(ModbusDevice).filter(ModbusDevice.is_deleted == False).all()
    
    all_devices_data = []

    for device in devices:
        inputs = db.query(ModbusDeviceinputs).filter(ModbusDeviceinputs.device_id == device.id).all()

        input_data = []
        for inp in inputs:
            latest = db.query(ModbusPolledData).filter(
                ModbusPolledData.input_id == inp.id
            ).order_by(desc(ModbusPolledData.polled_at)).first()

            input_data.append({
                "input_id"  : inp.id,
                "address"   : inp.device_register_address,
                "registers" : json.loads(latest.raw_value) if latest else None,
                "polled_at" : latest.polled_at.isoformat() if latest else None
            })

        all_devices_data.append({
            "device_id"   : device.id,
            "device_name" : device.device_name,
            "slave_id"    : device.slave_id,
            "inputs"      : input_data
        })

    db.close()
    return all_devices_data