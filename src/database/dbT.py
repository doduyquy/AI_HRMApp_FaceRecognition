import mysql.connector
import bcrypt
from mysql.connector import Error
from tkinter import messagebox

class dbT:
    def connectDatabase(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="nii",
                password="12345678",
                database="Face_Recognition"
            )
            return conn
        except Error as e:
            print(f"Lỗi khi kết nối cơ sở dữ liệu: {e}")
            return None

    def load_accounts(self):
        try:
            conn = self.connectDatabase()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT e.emp_id, e.last_name, e.first_name, e.email, e.status, r.role_name
                FROM Employees e
                LEFT JOIN Users u ON e.emp_id = u.emp_id
                LEFT JOIN Role r ON u.role_id = r.role_id
                ORDER BY e.emp_id ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")
            return []

    def search_accounts(self, search_term):
        try:
            conn = self.connectDatabase()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT e.emp_id, e.last_name, e.first_name, e.email, e.status, r.role_name
                FROM Employees e
                LEFT JOIN Users u ON e.emp_id = u.emp_id
                LEFT JOIN Role r ON u.role_id = r.role_id
                WHERE e.emp_id LIKE %s OR e.last_name LIKE %s OR e.first_name LIKE %s OR e.email LIKE %s
                ORDER BY e.emp_id ASC
            """
            search_value = f"%{search_term}%"
            cursor.execute(query, (search_value, search_value, search_value, search_value))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")
            return []

    def fetch_departments(self):
        conn = self.connectDatabase()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT dep_id, dep_name FROM Departments")
            departments = [(row[0], row[1]) for row in cursor.fetchall()]
            return departments
        except Error as e:
            print(f"Lỗi khi lấy danh sách phòng ban: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_roles(self):
        conn = self.connectDatabase()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT role_id, role_name FROM Role")
            roles = [(row[0], row[1]) for row in cursor.fetchall()]
            return roles
        except Error as e:
            print(f"Lỗi khi lấy danh sách vai trò: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def search_roles(self, search_term):
        conn = self.connectDatabase()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT r.role_id, r.role_name, f.function_id, f.function_name, rd.action
                FROM Role r
                LEFT JOIN Role_Details rd ON r.role_id = rd.role_id
                LEFT JOIN Function_List f ON rd.function_id = f.function_id
                WHERE r.role_name LIKE %s OR f.function_name LIKE %s
            """
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
            rows = cursor.fetchall()
            result = [(row[0], row[1], row[2], row[3], row[4].split(',') if row[4] else []) for row in rows]
            return result
        except Error as e:
            print(f"Lỗi khi tìm kiếm vai trò: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_role_details(self):
        conn = self.connectDatabase()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT r.role_id, r.role_name, f.function_id, f.function_name, rd.action
                FROM Role r
                LEFT JOIN Role_Details rd ON r.role_id = rd.role_id
                LEFT JOIN Function_List f ON rd.function_id = f.function_id
                WHERE rd.action IS NOT NULL
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            result = [(row[0], row[1], row[2], row[3], row[4].split(',') if row[4] else []) for row in rows]
            return result
        except Error as e:
            print(f"Lỗi khi lấy chi tiết quyền: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_function_id_by_name(self, function_name):
        conn = self.connectDatabase()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            query = "SELECT function_id FROM Function_List WHERE function_name = %s"
            cursor.execute(query, (function_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Lỗi khi lấy function_id: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def fetch_actions(self, role_id, function_id):
        conn = self.connectDatabase()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            query = "SELECT action FROM Role_Details WHERE role_id = %s AND function_id = %s"
            cursor.execute(query, (role_id, function_id))
            result = cursor.fetchone()
            return result[0] if result else ""
        except Error as e:
            print(f"Lỗi khi lấy actions: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update_role_actions(self, role_id, function_id, actions_str):
        conn = self.connectDatabase()
        if conn is None:
            return False, "Không thể kết nối đến cơ sở dữ liệu"
        try:
            cursor = conn.cursor()
            if actions_str:
                query = """
                    INSERT INTO Role_Details (role_id, function_id, action)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE action = %s
                """
                cursor.execute(query, (role_id, function_id, actions_str, actions_str))
            else:
                query = "DELETE FROM Role_Details WHERE role_id = %s AND function_id = %s"
                cursor.execute(query, (role_id, function_id))
            conn.commit()
            return True, "Cập nhật hành động thành công!"
        except Error as e:
            conn.rollback()
            print(f"Error updating actions: {e}")
            return False, f"Lỗi khi cập nhật hành động: {e}"
        finally:
            cursor.close()
            conn.close()

    def check_existing_email(self, email):
        conn = self.connectDatabase()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM Employees WHERE email = %s", (email,))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Lỗi khi kiểm tra email: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def check_existing_username(self, user_name):
        conn = self.connectDatabase()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_name FROM Users WHERE user_name = %s", (user_name,))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Lỗi khi kiểm tra tên đăng nhập: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def check_existing_role(self, role_name):
        conn = self.connectDatabase()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT role_name FROM Role WHERE role_name = %s", (role_name,))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Lỗi khi kiểm tra tên quyền: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def save_new_account(self, last_name, first_name, dep_id, email, phone_number, hired_date, position, status, user_name, password, role_id):
        conn = self.connectDatabase()
        if conn is None:
            return False, "Không thể kết nối đến cơ sở dữ liệu"
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO Employees (last_name, first_name, dep_id, email, phone_number, hired_date, position, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (last_name, first_name, dep_id, email, phone_number or None, hired_date or None, position or None, status))
            emp_id = cursor.lastrowid

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query = """
                INSERT INTO Users (emp_id, user_name, passwd, status, role_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (emp_id, user_name, hashed_password, 1, role_id))
            
            conn.commit()
            return True, "Đã thêm và lưu tài khoản vào cơ sở dữ liệu!"
        except Error as e:
            conn.rollback()
            return False, f"Lỗi khi lưu vào cơ sở dữ liệu: {e}"
        finally:
            cursor.close()
            conn.close()

    def fetch_account_by_id(self, account_id):
        conn = self.connectDatabase()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            query = """
                SELECT e.last_name, e.first_name, e.dep_id, e.email, e.phone_number, e.hired_date, e.position, e.status,
                    u.user_name, u.passwd, u.role_id
                FROM Employees e
                LEFT JOIN Users u ON e.emp_id = u.emp_id
                WHERE e.emp_id = %s
            """
            cursor.execute(query, (account_id,))
            result = cursor.fetchone()
            if result:
                return result
            return None
        except Error as e:
            print(f"Lỗi khi lấy thông tin tài khoản: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update_account(self, emp_id, last_name, first_name, dep_id, email, phone_number, hired_date, position, status, user_name, password, role_id):
        conn = self.connectDatabase()
        if conn is None:
            return False, "Không thể kết nối đến cơ sở dữ liệu"
        try:
            cursor = conn.cursor()
            query = """
                UPDATE Employees
                SET last_name = %s, first_name = %s, dep_id = %s, email = %s, phone_number = %s,
                    hired_date = %s, position = %s, status = %s
                WHERE emp_id = %s
            """
            cursor.execute(query, (last_name, first_name, dep_id, email, phone_number or None, hired_date or None, position or None, status, emp_id))

            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                query = """
                    UPDATE Users
                    SET user_name = %s, passwd = %s, role_id = %s
                    WHERE emp_id = %s
                """
                cursor.execute(query, (user_name, hashed_password, role_id, emp_id))
            else:
                query = """
                    UPDATE Users
                    SET user_name = %s, role_id = %s
                    WHERE emp_id = %s
                """
                cursor.execute(query, (user_name, role_id, emp_id))

            conn.commit()
            return True, "Tài khoản đã được cập nhật thành công!"
        except Error as e:
            conn.rollback()
            return False, f"Lỗi khi cập nhật tài khoản: {e}"
        finally:
            cursor.close()
            conn.close()

    def delete_account(self, emp_id):
        try:
            conn = self.connectDatabase()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Users WHERE emp_id = %s", (emp_id,))
            cursor.execute("DELETE FROM Employees WHERE emp_id = %s", (emp_id,))
            conn.commit()
            return True, "Đã xóa tài khoản!"
        except mysql.connector.Error as e:
            conn.rollback()
            return False, f"Lỗi khi xóa tài khoản: {e}"
        finally:
            cursor.close()
            conn.close()

    def save_new_role(self, role_name):
        conn = self.connectDatabase()
        if conn is None:
            return False, "Không thể kết nối đến cơ sở dữ liệu"
        try:
            cursor = conn.cursor()
            query = "INSERT INTO Role (role_name) VALUES (%s)"
            cursor.execute(query, (role_name,))
            conn.commit()
            return True, "Đã thêm quyền vào cơ sở dữ liệu!"
        except Error as e:
            conn.rollback()
            return False, f"Lỗi khi lưu quyền: {e}"
        finally:
            cursor.close()
            conn.close()

    def fetch_role_by_name(self, role_name):
        conn = self.connectDatabase()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            query = "SELECT role_id, role_name FROM Role WHERE role_name = %s"
            cursor.execute(query, (role_name,))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Lỗi khi lấy thông tin quyền: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update_role(self, old_role_name, new_role_name):
        conn = self.connectDatabase()
        if conn is None:
            return False, "Không thể kết nối đến cơ sở dữ liệu"
        try:
            cursor = conn.cursor()
            query = "UPDATE Role SET role_name = %s WHERE role_name = %s"
            cursor.execute(query, (new_role_name, old_role_name))
            conn.commit()
            return True, "Quyền đã được cập nhật thành công!"
        except Error as e:
            conn.rollback()
            return False, f"Lỗi khi cập nhật quyền: {e}"
        finally:
            cursor.close()
            conn.close()

    
    def delete_role(self, role_name):
        conn = self.connectDatabase()
        if conn is None:
            return False, "Không thể kết nối đến cơ sở dữ liệu"
        try:
            cursor = conn.cursor()
            # Check if role is assigned to any users
            cursor.execute("""
                SELECT COUNT(*) FROM Users u
                JOIN Employees e ON u.emp_id = e.emp_id
                WHERE u.role_id = (SELECT role_id FROM Role WHERE role_name = %s)
            """, (role_name,))
            user_count = cursor.fetchone()[0]
            if user_count > 0:
                # Fetch user details
                cursor.execute("""
                    SELECT e.emp_id, e.last_name, e.first_name
                    FROM Users u
                    JOIN Employees e ON u.emp_id = e.emp_id
                    WHERE u.role_id = (SELECT role_id FROM Role WHERE role_name = %s)
                """, (role_name,))
                users = cursor.fetchall()
                user_list = [f"{row[1]} {row[2]} (ID: {row[0]})" for row in users]
                error_msg = f"Không thể xóa quyền '{role_name}' vì nó đang được sử dụng bởi {user_count} người dùng:\n" + "\n".join(user_list)
                return False, error_msg

            # Check and delete Role_Details
            cursor.execute("SELECT COUNT(*) FROM Role_Details WHERE role_id = (SELECT role_id FROM Role WHERE role_name = %s)", (role_name,))
            detail_count = cursor.fetchone()[0]
            if detail_count > 0:
                cursor.execute("DELETE FROM Role_Details WHERE role_id = (SELECT role_id FROM Role WHERE role_name = %s)", (role_name,))

            # Delete the role
            cursor.execute("DELETE FROM Role WHERE role_name = %s", (role_name,))
            conn.commit()
            return True, "Đã xóa quyền!"
        except Error as e:
            conn.rollback()
            return False, f"Lỗi khi xóa quyền: {e}"
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.connectDatabase()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except Error as e:
            print(f"Lỗi khi lấy dữ liệu: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    