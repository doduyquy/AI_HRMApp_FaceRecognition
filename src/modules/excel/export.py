import pandas as pd
from tkinter import messagebox, filedialog  # Export excel: chọn địa chỉ và tên file
import os
from datetime import datetime

class ExportToExcel:
    def __init__(self, treeview):
        self.tree = treeview

    def export(self):
        try:
            # Lấy tất cả dữ liệu từ Treeview
            data = []
            columns = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
            for item in self.tree.get_children():
                row = self.tree.item(item)["values"]
                data.append(row)

            # Cảnh báo nếu không có data để xuất file
            if not data:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất!")
                return

            # Tạo DataFrame từ dữ liệu
            df = pd.DataFrame(data, columns=columns)

            # Mở hộp thoại để chọn đường dẫn và tên file
            # Tạo tên file mặc định: ChamCong_YYYYMMDD_HHMMSS.xlsx
            default_name = f"ChamCong_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            # Mở hộp thoại để chọn đường dẫn 
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=default_name,
                title="Chọn nơi lưu và đặt tên file"
            )

            # Nếu người dùng không chọn file (hủy), thoát hàm
            if not file_path:
                return

            # Xuất ra file Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            messagebox.showinfo("Thành công", f"Dữ liệu đã được xuất ra {file_path}")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi xuất file: {str(e)}")

    
if __name__ == "__main__":
    pass