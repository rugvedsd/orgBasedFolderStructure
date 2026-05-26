
from src.db.models import init_db

if __name__ == "__main__":
    if init_db():
        print("Database initialized successfully.")


    

    else:
        print("Failed to initialize the database.")
