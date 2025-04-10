import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, time, timedelta
import src.salary.salary  
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#  Kết nối db
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='nii',
            password='12345678',
            database='Face_Recognition'
        )
        if conn.is_connected():
            print("Connected to the database successfully!")
        cursor = conn.cursor(dictionary=True)
        return conn, cursor
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        raise

# Ktra đăng nhập của nv
def check_employee_login(cursor, emp_id, password_input, default_password):
    try:
        cursor.execute(
            "SELECT emp_id, first_name, last_name, status FROM Employees WHERE emp_id = %s",
            (emp_id,)
        )
        result = cursor.fetchone()

        if result:
            if result['status'] == "Đã nghỉ":
                return {"success": False, "error": "inactive"}
            if password_input == default_password:
                full_name = f"{result['last_name']} {result['first_name']}"
                return {"success": True, "full_name": full_name, "emp_id": result['emp_id']}
            else:
                return {"success": False, "error": "wrong_password"}
        else:
            return {"success": False, "error": "not_found"}

    except mysql.connector.Error as e:
        return {"success": False, "error": "mysql_error", "message": str(e)}

# Lấy thông tin nhân viên
def get_employee_data(cursor, emp_id):
    try:
        cursor.execute("SELECT * FROM Employees WHERE emp_id = %s", (emp_id,))
        employee = cursor.fetchone()
        if not employee:
            print(f"Không tìm thấy nhân viên với emp_id: {emp_id}")
        return employee
    except mysql.connector.Error as err:
        return {"error": "Lỗi CSDL", "message": f"Lỗi MySQL: {err}"}

# Lấy danh sách phòng ban
def load_departments(cursor):
    departments = {}
    try:
        cursor.execute("SELECT dep_id, dep_name FROM Departments")
        result = cursor.fetchall()
        for row in result:
            departments[row['dep_id']] = row['dep_name']
        return departments
    except mysql.connector.Error as err:
        return {"error": "Database Error", "message": f"Lỗi: {err}"}

# Lấy dữ liệu chấm công
def get_attendance_by_emp(cursor, emp_id, month=None, year=None):
    try:
        query = """
            SELECT DATE_FORMAT(date, '%%d/%%m/%%Y') as date, 
                   TIME_FORMAT(check_in, '%%H:%%i') as check_in, 
                   TIME_FORMAT(check_out, '%%H:%%i') as check_out, 
                   work_hours, overtime_hours 
            FROM Attendance 
            WHERE emp_id = %s
        """
        params = [emp_id]

        if month and month != "Tất cả":
            query += " AND MONTH(date) = %s"
            params.append(month)
        if year and year != "Tất cả":
            query += " AND YEAR(date) = %s"
            params.append(year)

        query += " ORDER BY date DESC"
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}

# Lấy dữ liệu lương
def get_salary_data(cursor, emp_id, month=None, year=None):
    try:
        query = """
            SELECT DATE_FORMAT(month_year, '%%m/%%Y') as month_year, 
                   base_salary, time_salary, overtime_salary
            FROM Payroll 
            WHERE emp_id = %s
        """
        params = [emp_id]

        if month and month != "Tất cả":
            query += " AND MONTH(month_year) = %s"
            params.append(month)
        if year and year != "Tất cả":
            query += " AND YEAR(month_year) = %s"
            params.append(year)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}
    
# Lấy danh sách nhân viên
def get_all_employees(cursor):
    try:
        query = """
            SELECT e.emp_id, e.first_name, e.last_name, e.position, e.email, e.phone_number, e.hired_date,
                   d.dep_name, e.dep_id, e.status
            FROM Employees e
            LEFT JOIN Departments d ON e.dep_id = d.dep_id
            ORDER BY e.emp_id ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}

# Lấy thông tin chi tiết của 1 nv
def get_employee_by_id(cursor, emp_id):
    try:
        query = """
            SELECT last_name, first_name, position, dep_name, email, phone_number, hired_date, status
            FROM Employees e
            JOIN Departments d ON e.dep_id = d.dep_id
            WHERE e.emp_id = %s
        """
        cursor.execute(query, (emp_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}

# Lấy danh sách nhân viên theo phòng ban
def get_dep_id_by_name(cursor, dep_name):
    try:
        cursor.execute("SELECT dep_id FROM Departments WHERE dep_name = %s", (dep_name,))
        result = cursor.fetchone()
        return result
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}

# Thêm 1 nv mới
def add_employee(cursor, conn, last_name, first_name, dep_id, email, phone_number, hired_date, position):
    try:
        cursor.execute("""
            INSERT INTO Employees (last_name, first_name, dep_id, email, phone_number, hired_date, position, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (last_name, first_name, dep_id, email, phone_number, hired_date, position, "Đang làm việc"))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        conn.rollback()
        return {"error": f"Lỗi MySQL: {err}"}
    
# Cập nhật thông tin nhân viên
def update_employee(cursor, conn, emp_id, last_name, first_name, dep_id, email, phone_number, hired_date, position, status):
    try:
        cursor.execute("""
            UPDATE Employees
            SET last_name = %s, first_name = %s, dep_id = %s, email = %s, phone_number = %s,
                hired_date = %s, position = %s, status = %s
            WHERE emp_id = %s
        """, (last_name, first_name, dep_id, email, phone_number, hired_date, position, status, emp_id))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        conn.rollback()
        return {"error": f"Lỗi MySQL: {err}"}

# Xóa
def delete_employee(cursor, conn, emp_id):
    try:
        # Xóa bản ghi trong bảng `users` trước
        cursor.execute("DELETE FROM users WHERE emp_id = %s", (emp_id,))
        conn.commit()

        # Sau đó xóa nhân viên trong bảng `employees`
        cursor.execute("DELETE FROM Employees WHERE emp_id = %s", (emp_id,))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        conn.rollback()
        return {"error": f"Lỗi MySQL: {err}"}

# Lọc ds nv
def filter_employees(cursor, search_term="", position=None, dep_name=None, year=None, month=None, date=None):
    try:
        query = """
            SELECT e.emp_id, e.first_name, e.last_name, e.position, e.email, e.phone_number, e.hired_date,
                   d.dep_name, e.dep_id, e.status
            FROM Employees e
            LEFT JOIN Departments d ON e.dep_id = d.dep_id
            WHERE 1=1
        """
        params = []

        if search_term:
            query += """
                AND (LOWER(e.emp_id) LIKE %s
                OR LOWER(CONCAT(e.first_name, ' ', e.last_name)) LIKE %s
                OR LOWER(e.position) LIKE %s
                OR LOWER(e.email) LIKE %s
                OR LOWER(e.phone_number) LIKE %s
                OR LOWER(e.hired_date) LIKE %s
                OR LOWER(d.dep_name) LIKE %s
                OR LOWER(e.status) LIKE %s)
            """
            params.extend([f"%{search_term}%"] * 8)

        if position and position != "Tất cả":
            query += " AND e.position = %s"
            params.append(position)

        if dep_name and dep_name != "Tất cả":
            query += " AND d.dep_name = %s"
            params.append(dep_name)

        if year and year != "Tất cả":
            query += " AND YEAR(e.hired_date) = %s"
            params.append(int(year))

        if month and month != "Tất cả":
            query += " AND MONTH(e.hired_date) = %s"
            params.append(int(month))

        if date:
            query += " AND DATE(e.hired_date) = %s"
            params.append(date)

        query += " ORDER BY e.emp_id ASC"
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}

# Lấy tất cả dữ liệu chấm công
def get_all_attendance(cursor):
    try:
        query = """
            SELECT e.emp_id, e.first_name, e.last_name, a.date, a.check_in, a.check_out, a.work_hours, a.overtime_hours
            FROM Employees e
            LEFT JOIN Attendance a ON e.emp_id = a.emp_id
            WHERE e.status = 'Đang làm việc'
            ORDER BY a.date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}

# Lấy dữ liệu chấm công dựa trên keyword
def filter_attendance(cursor, keyword=""):
    try:
        query = """
            SELECT e.emp_id, e.first_name, e.last_name, a.date, a.check_in, a.check_out, a.work_hours, a.overtime_hours
            FROM Employees e
            LEFT JOIN Attendance a ON e.emp_id = a.emp_id
            WHERE e.status = 'Đang làm việc'
        """
        params = []

        if keyword:
            query += """
                AND (LOWER(e.emp_id) LIKE %s
                OR LOWER(CONCAT(e.first_name, ' ', e.last_name)) LIKE %s
                OR LOWER(a.date) LIKE %s
                OR LOWER(a.check_in) LIKE %s
                OR LOWER(a.check_out) LIKE %s)
            """
            params.extend([f"%{keyword}%"] * 5)

        query += " ORDER BY a.date DESC"
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}

# Lấy tất cả dữ liệu lương với bộ lọc tháng, năm và từ khóa
def get_all_salary(cursor, month=None, year=None, search_term=None):
    try:
        query = """
            SELECT e.emp_id, e.first_name, e.last_name, p.month_year, p.base_salary, p.time_salary, p.overtime_salary
            FROM Employees e
            LEFT JOIN Payroll p ON e.emp_id = p.emp_id
            WHERE 1=1
        """
        params = []

        if month and month != "Tất cả":
            query += " AND MONTH(p.month_year) = %s"
            params.append(int(month))

        if year and year != "Tất cả":
            query += " AND YEAR(p.month_year) = %s"
            params.append(int(year))

        if search_term and search_term != "tìm kiếm...":
            query += """
                AND (LOWER(e.emp_id) LIKE %s
                OR LOWER(CONCAT(e.first_name, ' ', e.last_name)) LIKE %s)
            """
            params.extend([f"%{search_term}%", f"%{search_term}%"])

        query += " ORDER BY e.emp_id, p.month_year DESC"
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        return {"error": f"Lỗi MySQL: {err}"}

def calculate_and_update_payroll(conn, cursor, emp_id=None):
    try:
        # Định nghĩa các mốc thời gian
        MORNING_START = time(8, 0)
        MORNING_END = time(12, 0)
        AFTERNOON_START = time(13, 0)
        AFTERNOON_END = time(17, 0)
        OVERTIME_END = time(22, 0)

        # Lấy dữ liệu chấm công
        attendance_query = """
            SELECT attendance_id, emp_id, check_in, check_out, date, work_hours, overtime_hours 
            FROM Attendance 
            WHERE check_in IS NOT NULL AND check_out IS NOT NULL
        """
        if emp_id:
            attendance_query += " AND emp_id = %s"
            cursor.execute(attendance_query, (emp_id,))
        else:
            cursor.execute(attendance_query)
        attendance_records = cursor.fetchall()

        if not attendance_records:
            print(f"Không có dữ liệu chấm công để tính lương cho {'emp_id: ' + str(emp_id) if emp_id else 'bất kỳ nhân viên nào'}!")
            return False

        # Tính toán work_hours và overtime_hours
        for record in attendance_records:
            attendance_id = record['attendance_id']
            emp_id_record = record['emp_id']
            check_in = record['check_in']
            check_out = record['check_out']
            date = record['date']

            # Chuyển check_in và check_out từ chuỗi sang datetime nếu cần
            if isinstance(check_in, str):
                check_in = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
            if isinstance(check_out, str):
                check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')

            check_in_time = check_in.time()
            check_out_time = check_out.time()

            work_hours = 0.0
            overtime_hours = 0.0

            check_in_dt = check_in
            check_out_dt = check_out

            if check_out_dt < check_in_dt:
                check_out_dt = check_out_dt + timedelta(days=1)

            # Tính giờ làm việc buổi sáng
            morning_start_dt = datetime.combine(check_in.date(), MORNING_START)
            morning_end_dt = datetime.combine(check_in.date(), MORNING_END)
            if check_in_dt <= morning_end_dt and check_out_dt >= morning_start_dt:
                start = max(check_in_dt, morning_start_dt)
                end = min(check_out_dt, morning_end_dt)
                morning_hours = (end - start).total_seconds() / 3600
                work_hours += max(morning_hours, 0)

            # Tính giờ làm việc buổi chiều
            afternoon_start_dt = datetime.combine(check_in.date(), AFTERNOON_START)
            afternoon_end_dt = datetime.combine(check_in.date(), AFTERNOON_END)
            if check_in_dt <= afternoon_end_dt and check_out_dt >= afternoon_start_dt:
                start = max(check_in_dt, afternoon_start_dt)
                end = min(check_out_dt, afternoon_end_dt)
                afternoon_hours = (end - start).total_seconds() / 3600
                work_hours += max(afternoon_hours, 0)

            # Tính giờ tăng ca
            overtime_start_dt = datetime.combine(check_in.date(), AFTERNOON_END)
            overtime_end_dt = datetime.combine(check_in.date(), OVERTIME_END)
            if check_in_dt <= overtime_end_dt and check_out_dt >= overtime_start_dt:
                start = max(check_in_dt, overtime_start_dt)
                end = min(check_out_dt, overtime_end_dt)
                overtime_hours = (end - start).total_seconds() / 3600
                overtime_hours = max(overtime_hours, 0)

            # Cập nhật work_hours và overtime_hours vào bảng Attendance
            cursor.execute("""
                UPDATE Attendance 
                SET work_hours = %s, overtime_hours = %s 
                WHERE attendance_id = %s
            """, (work_hours, overtime_hours, attendance_id))

        # Lấy danh sách nhân viên và các tháng cần tính lương
        payroll_query = """
            SELECT DISTINCT emp_id, DATE_FORMAT(date, '%Y-%m-01') AS month_year
            FROM Attendance
            WHERE check_out IS NOT NULL
        """
        if emp_id:
            payroll_query += " AND emp_id = %s"
            cursor.execute(payroll_query, (emp_id,))
        else:
            cursor.execute(payroll_query)
        payroll_updates = cursor.fetchall()

        # Gọi stored procedure UpdatePayroll cho từng nhân viên và tháng
        for record in payroll_updates:
            emp_id_record = record['emp_id']
            month_year = record['month_year']
            cursor.execute("CALL UpdatePayroll(%s, %s)", (emp_id_record, month_year))

        print(f"Đã tính toán và cập nhật lương thành công cho {'emp_id: ' + str(emp_id) if emp_id else 'tất cả nhân viên'}!")
        return True
    except mysql.connector.Error as err:
        print(f"Lỗi cơ sở dữ liệu: {err}")
        return False
    
#  Đóng kết nối db
def close_connection(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()
