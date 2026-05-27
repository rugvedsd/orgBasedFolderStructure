from fastapi import FASTAPI
from src.db.models import get_session
from src.db.models import ModbusDevice

app = FASTAPI()


@app.get("/devices")
def get_all_devices():

    db = get_session()

    devices = db.query(ModbusDevice).filter(
        ModbusDevice.is_deleted == False
    ).all()

    return devices