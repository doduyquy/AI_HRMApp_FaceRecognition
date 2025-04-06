import pandas as pd
from tkinter import messagebox, filedialog
import sys
from pathlib import Path

# Thêm thư mục src vào sys.path
src_dir = str(Path(__file__).resolve().parent.parent.parent)  # Lên 3 cấp để tới src
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Custom modules
from database import handleDB


class ImportEmployees:
    def __init__(self):
        self.handle = handleDB.handle

    def import_from_excel(self):
        try:
            # Mở hộp thoại để chọn file Excel
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
                title="Chọn file Excel để nhập dữ liệu nhân viên"
            )
            if not file_path:
                return

            # Đọc file Excel
            df = pd.read_excel(file_path)

            # Danh sách tất cả các cột cần thiết (dựa trên bảng Employees)
            required_columns = [
                'last_name', 'first_name', 'dep_id', 'email', 
                'phone_number', 'hired_date', 'position', 'status'
            ]

            # Kiểm tra xem file Excel có đầy đủ các cột không
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                messagebox.showerror("Lỗi", f"File Excel thiếu các cột: {', '.join(missing_columns)}")
                return

            # Chuẩn bị danh sách dữ liệu để gửi cho DatabaseHandler
            employees_data = []
            for index, row in df.iterrows():
                # Lấy dữ liệu từ các cột, cho phép null
                employee = {
                    'last_name': str(row['last_name']).strip() if pd.notna(row['last_name']) else None,
                    'first_name': str(row['first_name']).strip() if pd.notna(row['first_name']) else None,
                    'dep_id': row['dep_id'] if pd.notna(row['dep_id']) else None,
                    'email': str(row['email']).strip() if pd.notna(row['email']) else None,
                    'phone_number': str(row['phone_number']).strip() if pd.notna(row['phone_number']) else None,
                    'hired_date': row['hired_date'] if pd.notna(row['hired_date']) else None,
                    'position': str(row['position']).strip() if pd.notna(row['position']) else None,
                    'status': str(row['status']).strip() if pd.notna(row['status']) else 'active'
                }

                # Kiểm tra các trường bắt buộc (last_name, first_name, email) không được để trống
                if not employee['last_name'] or not employee['first_name'] or not employee['email']:
                    messagebox.showwarning("Cảnh báo", f"Dòng {index + 2}: Thiếu dữ liệu bắt buộc (last_name, first_name, hoặc email)")
                    continue

                employees_data.append(employee)

            if not employees_data:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu hợp lệ để nhập!")
                return

            # Gửi dữ liệu cho DatabaseHandler để xử lý
            # Gửi từng nhân viên một
            self.handle.import_employees(employees_data)
            messagebox.showinfo("Thành công", "Dữ liệu nhân viên đã được nhập thành công!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi nhập file: {str(e)}")

# Ví dụ sử dụng
if __name__ == "__main__":
    pass