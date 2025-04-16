import mysql.connector
import json
import numpy as np
from cryptography.fernet import Fernet

class DataFace:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'nii',
            'password': '12345678',
            'database': 'Face_Recognition'
        }
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            raise Exception(f"Error connecting to database: {err}")


    def search_face_data(self, search_term):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT fd.face_id, fd.emp_id, fd.created_at AS collected_date,
                       e.last_name, e.first_name
                FROM Face_Data fd
                JOIN Employees e ON fd.emp_id = e.emp_id
                WHERE e.last_name LIKE %s OR e.first_name LIKE %s OR CAST(fd.face_id AS CHAR) LIKE %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            results = cursor.fetchall()
            for row in results:
                row['status'] = 'Hoạt động'
            cursor.close()
            return results
        except mysql.connector.Error as err:
            print(f"Error searching face data: {err}")
            return []

    def fetch_face_data_by_id(self, face_id):
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT fd.emp_id, fd.created_at,
                       e.last_name, e.first_name
                FROM Face_Data fd
                JOIN Employees e ON fd.emp_id = e.emp_id
                WHERE fd.face_id = %s
            """
            cursor.execute(query, (face_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return (result[0], result[1], 'Hoạt động', result[2], result[3])
            return None
        except mysql.connector.Error as err:
            print(f"Error fetching face data by ID: {err}")
            return None

    
    # def add_face_data(self, emp_id, collected_date, status, image_path=None, angle='front'):
    #     try:
    #         cursor = self.connection.cursor()
    #         dummy_encoding = np.zeros(128).tolist()  # Placeholder
    #         encoding_json = json.dumps(dummy_encoding)
    #         encrypted_encoding = self.cipher.encrypt(encoding_json.encode())
    #         query = """
    #             INSERT INTO Face_Data (emp_id, face_encoding, angle, created_at, image_path)
    #             VALUES (%s, %s, %s, %s, %s)
    #         """
    #         print(f"Executing add_face_data: emp_id={emp_id}, collected_date={collected_date}, image_path={image_path}, angle={angle}")
    #         cursor.execute(query, (emp_id, encrypted_encoding, angle, collected_date, image_path))
    #         self.connection.commit()
    #         print("Committed transaction in add_face_data")
    #         cursor.close()
    #         return True, "Thêm dữ liệu khuôn mặt thành công!"
    #     except mysql.connector.Error as err:
    #         self.connection.rollback()
    #         cursor.close()
    #         print(f"Error in add_face_data: {str(err)}")
    #         return False, f"Lỗi khi thêm dữ liệu khuôn mặt: {str(err)}"
    
    def add_face_data(self, emp_id, collected_date, status, image_path=None, angle='front'):
        try:
            cursor = self.connection.cursor()
            # Kiểm tra xem đã có bản ghi với emp_id và angle chưa
            query = """
                SELECT face_id FROM Face_Data 
                WHERE emp_id = %s AND angle = %s
            """
            cursor.execute(query, (emp_id, angle))
            result = cursor.fetchone()

            dummy_encoding = np.zeros(128).tolist()
            encoding_json = json.dumps(dummy_encoding)
            encrypted_encoding = self.cipher.encrypt(encoding_json.encode())

            if result:
                # Cập nhật bản ghi hiện có
                face_id = result[0]
                query = """
                    UPDATE Face_Data 
                    SET face_encoding = %s, created_at = %s, image_path = %s
                    WHERE face_id = %s
                """
                print(f"Updating face_data: face_id={face_id}, emp_id={emp_id}, collected_date={collected_date}, image_path={image_path}, angle={angle}")
                cursor.execute(query, (encrypted_encoding, collected_date, image_path, face_id))
            else:
                # Thêm bản ghi mới
                query = """
                    INSERT INTO Face_Data (emp_id, face_encoding, angle, created_at, image_path)
                    VALUES (%s, %s, %s, %s, %s)
                """
                print(f"Adding new face_data: emp_id={emp_id}, collected_date={collected_date}, image_path={image_path}, angle={angle}")
                cursor.execute(query, (emp_id, encrypted_encoding, angle, collected_date, image_path))

            self.connection.commit()
            print("Committed transaction in add_face_data")
            cursor.close()
            return True, "Thêm/cập nhật dữ liệu khuôn mặt thành công!"
        except mysql.connector.Error as err:
            self.connection.rollback()
            cursor.close()
            print(f"Error in add_face_data: {str(err)}")
            return False, f"Lỗi khi thêm/cập nhật dữ liệu khuôn mặt: {str(err)}"

    
    
    def fetch_face_data(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT fd.face_id, fd.emp_id, fd.created_at AS collected_date,
                    fd.angle, fd.image_path, e.last_name, e.first_name
                FROM Face_Data fd
                JOIN Employees e ON fd.emp_id = e.emp_id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                row['status'] = 'Hoạt động'  # Default status
            cursor.close()
            return results
        except mysql.connector.Error as err:
            print(f"Error fetching face data: {err}")
            return []
        
    def delete_face_data(self, face_id):
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM Face_Data WHERE face_id = %s"
            cursor.execute(query, (face_id,))
            self.connection.commit()
            cursor.close()
            return True, "Xóa dữ liệu khuôn mặt thành công!"
        except mysql.connector.Error as err:
            return False, f"Lỗi khi xóa dữ liệu khuôn mặt: {str(err)}"

    def load_accounts(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT emp_id, last_name, first_name
                FROM Employees
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except mysql.connector.Error as err:
            print(f"Error loading accounts: {err}")
            return []

    def save_face_encoding(self, employee_id, face_encoding, angle='front'):
        try:
            cursor = self.connection.cursor()
            encoding_json = json.dumps(face_encoding.tolist())
            encrypted_encoding = self.cipher.encrypt(encoding_json.encode())
            query = """
                INSERT INTO Face_Data (emp_id, face_encoding, angle)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (employee_id, encrypted_encoding, angle))
            self.connection.commit()
            cursor.close()
            return True, "Lưu dữ liệu khuôn mặt thành công!"
        except mysql.connector.Error as err:
            return False, f"Lỗi khi lưu dữ liệu khuôn mặt: {str(err)}"

 
    
    def fetch_face_encodings(self, employee_id):
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT face_encoding, angle
                FROM Face_Data
                WHERE emp_id = %s
            """
            cursor.execute(query, (employee_id,))
            results = cursor.fetchall()
            cursor.close()
            encodings = []
            for encrypted_encoding, angle in results:
                encoding_json = self.cipher.decrypt(encrypted_encoding).decode()
                encoding = np.array(json.loads(encoding_json))
                encodings.append((encoding, angle))
            return encodings
        except mysql.connector.Error as err:
            raise Exception(f"Error fetching face encodings: {err}")
        
    
    def update_image_data(self, face_id, image_path, angle):
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT face_id FROM Face_Data 
                WHERE face_id = %s
            """
            print(f"Checking existing record: face_id={face_id}")
            cursor.execute(query, (face_id,))
            result = cursor.fetchone()

            if result:
                query = """
                    UPDATE Face_Data 
                    SET image_path = %s, angle = %s 
                    WHERE face_id = %s
                """
                print(f"Updating image_path and angle: face_id={face_id}, image_path={image_path}, angle={angle}")
                cursor.execute(query, (image_path, angle, face_id))
                self.connection.commit()
                print("Committed transaction in update_image_data")
                cursor.close()
                return True, "Cập nhật ảnh thành công!"
            else:
                cursor.close()
                return False, f"Không tìm thấy bản ghi với face_id={face_id}"
        except mysql.connector.Error as err:
            self.connection.rollback()
            cursor.close()
            print(f"Error in update_image_data: {str(err)}")
            return False, f"Lỗi khi cập nhật ảnh: {str(err)}"
        
    def update_face_data(self, face_id, emp_id, collected_date):
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT face_id FROM Face_Data 
                WHERE face_id = %s
            """
            cursor.execute(query, (face_id,))
            if not cursor.fetchone():
                cursor.close()
                return False, f"Không tìm thấy bản ghi với face_id={face_id}"

            query = """
                UPDATE Face_Data 
                SET emp_id = %s, created_at = %s
                WHERE face_id = %s
            """
            print(f"Updating face_data: face_id={face_id}, emp_id={emp_id}, collected_date={collected_date}")
            cursor.execute(query, (emp_id, collected_date, face_id))
            self.connection.commit()
            cursor.close()
            return True, "Cập nhật dữ liệu khuôn mặt thành công!"
        except mysql.connector.Error as err:
            self.connection.rollback()
            cursor.close()
            print(f"Error in update_face_data: {str(err)}")
            return False, f"Lỗi khi cập nhật dữ liệu khuôn mặt: {str(err)}"
    
    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()