import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

class DatabaseHandler:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                #user='nii',  
                user='root',  
                password='12345678',  
                database='Face_Recognition'
            )
            if self.conn.is_connected():
                print("Connected to the database successfully!")
            # Tạo cursor với dictionary=True để trả về kết quả dưới dạng dictionary
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            raise

    def get_last_attendance(self, emp_id):
        """Lấy bản ghi chấm công gần nhất của nhân viên"""
        query = """
            SELECT check_in, check_out, date
            FROM Attendance 
            WHERE emp_id = %s 
            ORDER BY check_in DESC 
            LIMIT 1
        """
        self.cursor.execute(query, (emp_id,))
        result = self.cursor.fetchone()
        return result  # Trả về dict với check_in, check_out, date hoặc None

    def write_check_in_to_db(self, emp_id, check_in_time):
        """Ghi thời gian check-in hoặc check-out vào database"""
        # Chuyển check_in_time từ chuỗi thành datetime để so sánh
        current_time = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
        last_attendance = self.get_last_attendance(emp_id)

        if last_attendance:
            last_check_in = last_attendance['check_in']  # Đã là datetime từ DB
            last_check_out = last_attendance['check_out']
            last_date = last_attendance['date']

            # Nếu bản ghi trước đã hoàn tất (có check_out)
            if last_check_out is not None:
                query = """
                    INSERT INTO Attendance (emp_id, check_in, date)
                    VALUES (%s, %s, %s)
                """
                self.cursor.execute(query, (emp_id, check_in_time, current_time.date()))
                self.conn.commit()
                print(f"Check-in recorded for emp_id {emp_id} at {check_in_time}")
            # Nếu đã có check_in nhưng chưa có check_out, kiểm tra thời gian
            elif last_check_in is not None and last_check_out is None:
                time_diff = (current_time - last_check_in).total_seconds()
                if time_diff >= 3600:  # Kiểm tra cách ít nhất 1 giờ (3600 giây)
                    self.update_check_out_to_db(emp_id, check_in_time, last_date)
                    print(f"Check-out recorded for emp_id {emp_id} at {check_in_time}")
                else:
                    print(f"Chưa đủ 1 giờ để check-out cho emp_id {emp_id}")
        else:
            # Nếu chưa có bản ghi nào, thêm check-in mới
            query = """
                INSERT INTO Attendance (emp_id, check_in, date)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (emp_id, check_in_time, current_time.date()))
            self.conn.commit()
            print(f"Check-in recorded for emp_id {emp_id} at {check_in_time}")

    def update_check_out_to_db(self, emp_id, check_out_time, date):
        """Cập nhật thời gian check-out"""
        query = """
            UPDATE Attendance
            SET check_out = %s,
                work_hours = TIMESTAMPDIFF(HOUR, check_in, %s)
            WHERE emp_id = %s AND date = %s AND check_out IS NULL
        """
        self.cursor.execute(query, (check_out_time, check_out_time, emp_id, date))
        self.conn.commit()

    ### RECOGNIZE UI ###
    # Thêm phương thức mới để lấy tất cả bản ghi chấm công
    def get_all_attendance(self):
        self.cursor.execute('''
            SELECT * FROM Attendance
            ORDER BY attendance_id DESC
        ''')
        results = self.cursor.fetchall()
        attendance_list = []
        for result in results:
            attendance_list.append({
                'attendance_id': result['attendance_id'],
                'emp_id': result['emp_id'],
                'check_in': result['check_in'],
                'check_out': result['check_out'],
                'date': result['date'],
                'work_hours': result['work_hours'],
                'overtime_hours': result['overtime_hours']
            })
        return attendance_list
    
    """Lấy danh sách chấm công của một ngày cụ thể, mặc định là ngày hiện tại"""
    def get_attendance_by_date(self, date=None):
        if date is None:
            date = datetime.now().date()
        
        query = """
            SELECT * FROM Attendance
            WHERE date = %s
            ORDER BY attendance_id DESC
        """
        self.cursor.execute(query, (date,))
        results = self.cursor.fetchall()
        attendance_list = []
        for result in results:
            attendance_list.append({
                'attendance_id': result['attendance_id'],
                'emp_id': result['emp_id'],
                'check_in': result['check_in'],
                'check_out': result['check_out'],
                'date': result['date'],
                'work_hours': result['work_hours'],
                'overtime_hours': result['overtime_hours']
            })
        return attendance_list

    ### Import from EXCEL ###
    def import_employees(self, employees_data):
        # Nhập danh sách nhân viên vào bảng Employees
        #    employees_data: list các dict chứa thông tin nhân viên, với đầy đủ các fields
        try:
            for employee in employees_data:
                ### Kiểm tra định dạng ngày tháng cho hired_date
                # if employee['hired_date'] and isinstance(employee['hired_date'], str):
                #     try:
                #         employee['hired_date'] = datetime.strptime(employee['hired_date'], "%Y-%m-%d").date()
                #     except ValueError:
                #         print(f"Định dạng ngày 'hired_date' không hợp lệ cho email {employee['email']}, để null")
                #         employee['hired_date'] = None

                query = """
                    INSERT INTO Employees (last_name, first_name, dep_id, email, phone_number, hired_date, position, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        last_name = VALUES(last_name),
                        first_name = VALUES(first_name),
                        dep_id = VALUES(dep_id),
                        phone_number = VALUES(phone_number),
                        hired_date = VALUES(hired_date),
                        position = VALUES(position),
                        status = VALUES(status)
                """
                values = (
                    employee['last_name'],
                    employee['first_name'],
                    employee['dep_id'],
                    employee['email'],
                    employee['phone_number'],
                    employee['hired_date'],
                    employee['position'],
                    employee['status']
                )

                self.cursor.execute(query, values)

            # Commit giao dịch
            self.conn.commit()
            print("Đã nhập dữ liệu nhân viên thành công!")

        except mysql.connector.Error as err:
            print(f"Lỗi khi nhập dữ liệu: {err}")
            self.conn.rollback()
            raise


    def testing(self):
        """Hàm kiểm tra"""
        print("In handleDB testing...")
    def close(self):
        """Đóng kết nối database"""
        self.cursor.close()
        self.conn.close()

# Khởi tạo đối tượng
handle = DatabaseHandler()
# print(handle.get_last_attendance("1"))






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
    pass
    # # Giả lập quét khuôn mặt
    # print("Simulating check-in...")
    # record_attendance(1)  # Check-in
    # print("\nWaiting a few seconds to simulate check-out...")
    # time.sleep(5)  # Đợi 5 giây để có sự khác biệt thời gian
    # print("Simulating check-out...")
    # record_attendance(1)  # Check-out

    # # Kiểm tra dữ liệu
    # check_data()