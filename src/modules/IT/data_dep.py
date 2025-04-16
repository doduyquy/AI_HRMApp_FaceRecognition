import mysql.connector

class DataDepartment:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'nii',
            'password': '12345678',  
            'database': 'Face_Recognition'
        }
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            raise

    def load_departments(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT dep_id, dep_name
                FROM Departments
                ORDER BY dep_id
            """
            cursor.execute(query)
            departments = cursor.fetchall()
            cursor.close()
            return departments
        except mysql.connector.Error as err:
            return f"Lỗi khi tải danh sách phòng ban: {str(err)}"
    
    def search_departments(self, search_text):
        try:
            cursor = self.connection.cursor(dictionary=True)
            # Chuẩn hóa từ khóa tìm kiếm: thêm % để tìm kiếm một phần, chuyển về chữ thường
            search_text = f"%{search_text.lower()}%"
            query = "SELECT dep_id, dep_name FROM Departments WHERE LOWER(dep_name) LIKE %s"
            cursor.execute(query, (search_text,))
            departments = cursor.fetchall()
            cursor.close()
            return departments
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {str(err)}")

    def add_department(self, dep_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT dep_id FROM Departments WHERE dep_name = %s", (dep_name,))
            if cursor.fetchone():
                cursor.close()
                return False, "Tên phòng ban đã tồn tại!"

            query = """
                INSERT INTO Departments (dep_name)
                VALUES (%s)
            """
            cursor.execute(query, (dep_name,))
            self.connection.commit()
            cursor.close()
            return True, "Thêm phòng ban thành công!"
        except mysql.connector.Error as err:
            return False, f"Lỗi khi thêm phòng ban: {str(err)}"

    def update_department(self, dep_id, dep_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT dep_id FROM Departments WHERE dep_name = %s AND dep_id != %s", (dep_name, dep_id))
            if cursor.fetchone():
                cursor.close()
                return False, "Tên phòng ban đã tồn tại!"

            query = """
                UPDATE Departments
                SET dep_name = %s
                WHERE dep_id = %s
            """
            cursor.execute(query, (dep_name, dep_id))
            if cursor.rowcount == 0:
                cursor.close()
                return False, "Phòng ban không tồn tại!"
            self.connection.commit()
            cursor.close()
            return True, "Cập nhật phòng ban thành công!"
        except mysql.connector.Error as err:
            return False, f"Lỗi khi cập nhật phòng ban: {str(err)}"

    
    def delete_department(self, dep_id):
        print(f"DEBUG: delete_department called with dep_id={dep_id}")
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT dep_id FROM Departments WHERE dep_id = %s", (dep_id,))
            if not cursor.fetchone():
                cursor.close()
                print("DEBUG: Department does not exist")
                return False, "Phòng ban không tồn tại!"
            cursor.execute("SELECT emp_id FROM Employees WHERE dep_id = %s", (dep_id,))
            if cursor.fetchone():
                cursor.close()
                print("DEBUG: Department has associated employees")
                return False, "Không thể xóa phòng ban vì có nhân viên thuộc phòng ban này!"

            query = "DELETE FROM Departments WHERE dep_id = %s"
            cursor.execute(query, (dep_id,))
            self.connection.commit()
            cursor.close()
            print("DEBUG: Department deleted successfully")
            return True, "Xóa phòng ban thành công!"
        except mysql.connector.Error as err:
            print(f"DEBUG: MySQL error: {str(err)}")
            return False, f"Lỗi khi xóa phòng ban: {str(err)}"

    def fetch_departments(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT dep_id, dep_name FROM Departments ORDER BY dep_name")
            departments = cursor.fetchall()
            cursor.close()
            return departments
        except mysql.connector.Error as err:
            return []