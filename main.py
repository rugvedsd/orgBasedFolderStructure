from fastapi import FastAPI
from uvicorn import run
from src.db.models import init_db
from src.devices.modbus.modbus import init_all_modbus_devices
from src.routes.all_routes import router
from loguru import logger

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def on_startup():
    if init_db():
        logger.info("Database initialized successfully.")
        init_all_modbus_devices()
    else:
        logger.error("Failed to initialize the database.")

if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=8000, reload=False)  # reload=False to avoid child process issue