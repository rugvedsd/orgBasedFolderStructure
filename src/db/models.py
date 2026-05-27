#contains all the db queries and functions related to database operations

"""
A supporting entity that fetches data and pushes it the required block/class of code file.

Maintain a dictionary that says {zoneCode: Value}


"""


import os
from subprocess import getoutput
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime, Boolean, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from os import getenv
from datetime import datetime
from loguru import logger

cdb = None
DBSession: sessionmaker = None
Base = declarative_base()

def init_db():

    try:
        global cdb, DBSession
        config_path = "/home/smartiam/Desktop/RugvedSD/OnBoarding-IAM/orgBasedFolderStructure/config"
        logger.info(f"Config Path: {config_path}")
        cdb = create_engine(f'sqlite:///{config_path}/config.db', connect_args={'check_same_thread': False})

        conn = cdb.connect()
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.close() 

        Base.metadata.create_all(cdb)
        Base.metadata.bind = cdb
        DBSession = sessionmaker(bind=cdb)
        return True

    except Exception as e:
        logger.critical(f'{e}')
        return False



def get_session():
    if DBSession is not None:
        session = DBSession()
        return session
    else:
        return None



class ModbusDevice(Base):
    __tablename__ = 'modbus_device'
    id = Column(Integer, primary_key=True)  
    device_code = Column(String(20), nullable=True)
    device_name = Column(String(50), nullable=False)
    dev_zone = Column(String(20), nullable=False)
    config_type = Column(String(20), nullable=False)
    connection_parameters = Column(String(200), nullable=False)
    slave_id = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False)



class ModbusDeviceInputs(Base):
    __tablename__ = 'modbus_device_inputs'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('modbus_device.id'), nullable=False)
    device_zone = Column(String(20), nullable=False)
    device_register_type = Column(String(50), nullable=False)
    device_register_address = Column(Integer, nullable=False)
    device_register_count = Column(Integer, nullable=False)
    device_decode_type = Column(String(50), nullable=False)
    device_endianess = Column(String(50), nullable=False)





class ModbusDeviceOutputs(Base):
    __tablename__ = 'modbus_device_outputs'
    id = Column(Integer, primary_key=True)




