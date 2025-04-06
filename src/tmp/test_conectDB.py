import mysql.connector
from mysql.connector import errorcode

try:
    db = mysql.connector.connect(
        user='nii',
        password='12345678',
        host='localhost',
        database='Face_Recognition'
    )
    print("Connected to database successfully!")
    db.close()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Wrong username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Error: Database 'Face_Recognition' does not exist")
    else:
        print(f"Error: {err}")