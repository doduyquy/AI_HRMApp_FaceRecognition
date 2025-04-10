import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, time, timedelta

# Hàm kết nối cơ sở dữ liệu
def connect_to_database():
    try:
        db = mysql.connector.connect(
            user='nii',
            password='12345678',  
            host='localhost',
            database='Face_Recognition'
        )
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Lỗi: Sai tên người dùng hoặc mật khẩu.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Lỗi: Cơ sở dữ liệu 'Face_Recognition' không tồn tại.")
        else:
            print(f"Lỗi: {err}")
        return None

# Hàm lấy thông tin nhân viên
def get_employee_details():
    db = connect_to_database()
    if not db:
        return {}

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.emp_id, e.first_name, e.last_name, e.position, e.dep_id, d.dep_name, r.role_name
            FROM Employees e
            LEFT JOIN Departments d ON e.dep_id = d.dep_id
            LEFT JOIN Employee_Role er ON e.emp_id = er.emp_id
            LEFT JOIN Role r ON er.role_id = r.role_id
        """)
        employees = {row['emp_id']: row for row in cursor.fetchall()}
        cursor.close()
        db.close()
        return employees
    except mysql.connector.Error as err:
        print(f"Lỗi cơ sở dữ liệu: {err}")
        return {}

# Hàm tính lương
def calculate_salary(emp_id, total_work_hours, total_overtime_hours, employee_details):
    emp_info = employee_details.get(emp_id, {})
    position = emp_info.get('position', 'Employee')  

    HOURLY_RATE = 100000  # Lương giờ cơ bản
    OVERTIME_RATE = 200000  # Lương giờ làm thêm
    FIXED_SALARY = {"Manager": 5000000, "Developer": 3000000, "Employee": 0}  

    fixed_salary = FIXED_SALARY.get(position, 0)
    time_salary = total_work_hours * HOURLY_RATE
    base_salary = fixed_salary + time_salary
    overtime_salary = total_overtime_hours * OVERTIME_RATE
    total_salary = base_salary + overtime_salary

    return {
        "emp_id": emp_id,
        "first_name": emp_info.get('first_name', ''),
        "last_name": emp_info.get('last_name', ''),
        "position": position,
        "time_salary": time_salary,
        "base_salary": base_salary,
        "overtime_salary": overtime_salary,
        "total_salary": total_salary
    }

# Hàm tính toán và cập nhật lương
def calculate_and_update_payroll(emp_id=None):
    db = connect_to_database()
    if not db:
        return False

    try:
        cursor = db.cursor()
        employee_details = get_employee_details()

        # Định nghĩa các mốc thời gian
        MORNING_START = time(8, 0)    # 8:00 sáng
        MORNING_END = time(12, 0)     # 12:00 trưa
        AFTERNOON_START = time(13, 0) # 13:00 chiều
        AFTERNOON_END = time(17, 0)   # 17:00 chiều
        OVERTIME_END = time(22, 0)    # 22:00 tối

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

        # Tính toán work_hours và overtime_hours cho từng bản ghi
        for attendance_id, emp_id_record, check_in, check_out, date, work_hours, overtime_hours in attendance_records:
            check_in_time = check_in.time()
            check_out_time = check_out.time()

            # Khởi tạo
            work_hours = 0.0
            overtime_hours = 0.0

            # Sử dụng ngày thực tế
            check_in_dt = check_in
            check_out_dt = check_out

            # Nếu check_out nhỏ hơn check_in (qua ngày), giả sử check_out là ngày hôm sau
            if check_out_dt < check_in_dt:
                check_out_dt = check_out_dt + timedelta(days=1)

            # Tính giờ làm việc trong khung giờ chuẩn (8:00-12:00 và 13:00-17:00)
            morning_start_dt = datetime.combine(check_in.date(), MORNING_START)
            morning_end_dt = datetime.combine(check_in.date(), MORNING_END)
            if check_in_dt <= morning_end_dt and check_out_dt >= morning_start_dt:
                start = max(check_in_dt, morning_start_dt)
                end = min(check_out_dt, morning_end_dt)
                morning_hours = (end - start).total_seconds() / 3600
                work_hours += max(morning_hours, 0)

            afternoon_start_dt = datetime.combine(check_in.date(), AFTERNOON_START)
            afternoon_end_dt = datetime.combine(check_in.date(), AFTERNOON_END)
            if check_in_dt <= afternoon_end_dt and check_out_dt >= afternoon_start_dt:
                start = max(check_in_dt, afternoon_start_dt)
                end = min(check_out_dt, afternoon_end_dt)
                afternoon_hours = (end - start).total_seconds() / 3600
                work_hours += max(afternoon_hours, 0)

            # Tính giờ tăng ca (17:00-22:00)
            overtime_start_dt = datetime.combine(check_in.date(), AFTERNOON_END)
            overtime_end_dt = datetime.combine(check_in.date(), OVERTIME_END)
            if check_in_dt <= overtime_end_dt and check_out_dt >= overtime_start_dt:
                start = max(check_in_dt, overtime_start_dt)
                end = min(check_out_dt, overtime_end_dt)
                overtime_hours = (end - start).total_seconds() / 3600
                overtime_hours = max(overtime_hours, 0)

            # Cập nhật lại bảng Attendance
            cursor.execute("""
                UPDATE Attendance 
                SET work_hours = %s, overtime_hours = %s 
                WHERE attendance_id = %s
            """, (work_hours, overtime_hours, attendance_id))

        db.commit()

        # Tính tổng giờ làm và giờ tăng ca theo tháng
        payroll_query = """
            SELECT emp_id, 
                   DATE_FORMAT(date, '%Y-%m-01') AS month_year, 
                   SUM(work_hours) AS total_work_hours, 
                   SUM(overtime_hours) AS total_overtime_hours
            FROM Attendance
            WHERE check_out IS NOT NULL
        """
        if emp_id:
            payroll_query += " AND emp_id = %s GROUP BY emp_id, DATE_FORMAT(date, '%Y-%m-01')"
            cursor.execute(payroll_query, (emp_id,))
        else:
            payroll_query += " GROUP BY emp_id, DATE_FORMAT(date, '%Y-%m-01')"
            cursor.execute(payroll_query)
        payroll_updates = cursor.fetchall()

        # Xóa dữ liệu cũ trong Payroll
        if emp_id:
            cursor.execute("DELETE FROM Payroll WHERE emp_id = %s", (emp_id,))
        else:
            cursor.execute("DELETE FROM Payroll")

        # Chèn dữ liệu mới vào Payroll
        for emp_id_record, month_year, total_work_hours, total_overtime_hours in payroll_updates:
            payroll_data = calculate_salary(emp_id_record, total_work_hours, total_overtime_hours, employee_details)
            cursor.execute("""
                INSERT INTO Payroll (emp_id, month_year, base_salary, overtime_salary, time_salary, total_month_basetime, total_month_overtime)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (emp_id_record, month_year, payroll_data['base_salary'], payroll_data['overtime_salary'], 
                  payroll_data['time_salary'], total_work_hours, total_overtime_hours))

        db.commit()
        print(f"Đã tính toán và cập nhật lương thành công cho {'emp_id: ' + str(emp_id) if emp_id else 'tất cả nhân viên'}!")
        return True
    except mysql.connector.Error as err:
        print(f"Lỗi cơ sở dữ liệu: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

if __name__ == "__main__":
    # Test tính lương cho một nhân viên
    calculate_and_update_payroll("1")
    # Test tính lương cho tất cả nhân viên
    calculate_and_update_payroll()