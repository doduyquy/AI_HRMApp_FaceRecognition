import mysql.connector
from mysql.connector import errorcode

#  Kết nối db
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
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
    
#  Đóng kết nối db
def close_connection(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()
