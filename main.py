
from src.db.models import init_db
from src.devices.modbus.modbus import __init_modbus_devices
from loguru import logger


if __name__ == "__main__":
    if init_db():
        logger.info("Database initialized successfully.")

        __init_modbus_devices()
        

    else:
        logger.error("Failed to initialize the database.")

