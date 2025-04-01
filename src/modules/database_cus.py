import mysql.connector
from mysql.connector import errorcode

USER = 'nii'       # Quy: nii
# USER = 'root'       # Tu, Luyen, Thanh: root    ? 

PASSWORD = '12345678'
HOST = 'localhost'
DATABASE = 'Face_Recognition'

def connectDatabase():
    try:
        conn = mysql.connector.connect(
            user= USER,
            password= PASSWORD,
            host= HOST,
            database= DATABASE,
        )
        print("Connected to database successfully!")

        return conn
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Wrong username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database 'Face_Recognition' does not exist")
        else:
            print(f"Error: {err}")
        return None


if __name__ == "__main__":
    connectDatabase()