import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import time

# Hàm kết nối cơ sở dữ liệu
def connect_to_database():
    try:
        db = mysql.connector.connect(
            user='root',
            # password='Ngoctu280105@',
            password='',
            host='localhost',
            database='Face_Recognition'
        )
        print("Connected to database successfully!")
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Wrong username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database 'Face_Recognition' does not exist")
        else:
            print(f"Error: {err}")
        return None

# Hàm ghi nhận chấm công tự động
def record_attendance(emp_id):
    db = connect_to_database()
    if not db:
        return

    try:
        cursor = db.cursor()

        # Kiểm tra bản ghi hôm nay
        cursor.execute("""
            SELECT attendance_id, check_in, check_out 
            FROM Attendance 
            WHERE emp_id = %s AND date = CURDATE()
        """, (emp_id,))
        record = cursor.fetchone()

        if not record:  # Chưa có -> Check-in
            cursor.execute("""
                INSERT INTO Attendance (emp_id, check_in, date)
                VALUES (%s, NOW(), CURDATE())
            """, (emp_id,))
            cursor.execute("SELECT NOW()")
            check_in_time = cursor.fetchone()[0]
            print(f"Check-in recorded for emp_id {emp_id} at {check_in_time}")
        else:  # Đã có -> Check-out
            attendance_id, check_in, check_out = record
            if not check_out:  # Chưa check-out -> Cập nhật và tính toán
                cursor.execute("""
                    UPDATE Attendance 
                    SET check_out = NOW(),
                        work_hours = LEAST(TIMESTAMPDIFF(HOUR, check_in, NOW()), 8),
                        overtime_hours = GREATEST(TIMESTAMPDIFF(HOUR, check_in, NOW()) - 8, 0)
                    WHERE attendance_id = %s
                """, (attendance_id,))
                cursor.execute("SELECT NOW()")
                check_out_time = cursor.fetchone()[0]
                print(f"Check-out recorded for emp_id {emp_id} at {check_out_time}")

                # Cập nhật Payroll
                cursor.execute("""
                    CALL UpdatePayroll(%s, DATE_FORMAT(NOW(), '%Y-%m-01'))
                """, (emp_id,))
                print(f"Payroll updated for emp_id {emp_id}")

        db.commit()
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if err.errno == errorcode.ER_NO_SUCH_TABLE:
            print(f"Table does not exist: {err}")
        elif err.errno == errorcode.ER_DUP_ENTRY:
            print(f"Duplicate entry error: {err}")
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            print(f"Foreign key violation: {err}")
    finally:
        cursor.close()
        db.close()

# Hàm kiểm tra dữ liệu
def check_data():
    db = connect_to_database()
    if not db:
        return

    try:
        cursor = db.cursor()

        print("\nAttendance Data:")
        cursor.execute("SELECT * FROM Attendance")
        for row in cursor.fetchall():
            print(row)

        print("\nPayroll Data:")
        cursor.execute("SELECT * FROM Payroll")
        for row in cursor.fetchall():
            print(row)

        db.commit()
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        db.close()

# Chạy chương trình
if __name__ == "__main__":
    # Giả lập quét khuôn mặt
    print("Simulating check-in...")
    record_attendance(1)  # Check-in
    print("\nWaiting a few seconds to simulate check-out...")
    time.sleep(5)  # Đợi 5 giây để có sự khác biệt thời gian
    print("Simulating check-out...")
    record_attendance(1)  # Check-out

    # Kiểm tra dữ liệu
    check_data()