import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import importlib.util 
import mysql.connector

class HRMApp:
    def __init__(self, root, emp_id):
        self.root = root
        self.root.title("Nhân sự")
        self.root.geometry("925x500+200+100")

        self.emp_id = emp_id
        self.selected_button = None
        self.menu_buttons = {}
        self.menu_icons = {} 
        self.employee = None 
        self.conn = None 
        self.cursor = None

        self.connect_db()
        self.get_employee_data(emp_id)

        self.menu()
        self.main_content()

    # Truy vấn database
    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="Face_Recognition"
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi CSDL", f"Lỗi kết nối MySQL: {err}")
    
    def get_employee_data(self, emp_id):
        if not self.conn or not self.cursor:
            return
        try:
            self.cursor.execute("SELECT * FROM Employees WHERE emp_id = %s", (emp_id,))
            self.employee = self.cursor.fetchone()
            if not self.employee:
                print(f"Không tìm thấy nhân viên với emp_id: {emp_id}")
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi CSDL", f"Lỗi MySQL: {err}")

    # Menu
    def menu(self):
        # Khung menu
        self.frame = tk.Frame(self.root, width=300, bg="#579df8")
        self.frame.pack(side=tk.LEFT, fill=tk.Y)

        # Thông tin nhân viên (avt và tên)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(BASE_DIR, "..", "img", "user.jpg")

        # Mở ảnh
        img = Image.open(img_path).resize((100, 120))
        img = ImageTk.PhotoImage(img)

        # Hiển thị ảnh
        img_lb = tk.Label(self.frame, image=img, bg="#579df8")
        img_lb.image = img 
        img_lb.pack(pady=10)

        # Nếu có dữ liệu thì hiển thị
        if self.employee:
            full_name = f"{self.employee['last_name']} {self.employee['first_name']}"
            position = self.employee['position']
        else:
            full_name = "Không có dữ liệu"
            position = "Không xác định"

        name = tk.Label(self.frame, text=full_name, font=('Times New Roman', 12, "bold"), fg="white", bg="#579df8")
        name.pack()

        role = tk.Label(self.frame, text=position, font=('Times New Roman', 10), fg="white", bg="#579df8")
        role.pack()

        # Các mục menu và icon tương ứng
        menu_items = [
            ("Hồ sơ", "profile.png"),
            ("Chấm công", "check.png"),
            ("Xem bảng lương", "salary.png"), 
            ("Đăng xuất", "logout.png") 
        ]

        # Thư mục chứa icon
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        for item, icon_name in menu_items:
            # Tải icon
            icon_path = os.path.join(BASE_DIR, "..", "img", icon_name)
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path).resize((20, 20)) 
                icon = ImageTk.PhotoImage(icon_img)
            else:
                # Nếu không tìm thấy file icon, tạo một ảnh trống
                icon = ImageTk.PhotoImage(Image.new("RGBA", (20, 20), (0, 0, 0, 0)))
                print(f"Không tìm thấy icon: {icon_name}")

            # Lưu icon vào dictionary
            self.menu_icons[item] = icon

            # Tạo nút menu với icon và chữ
            btn = tk.Button(self.frame, text=item, font=('Times New Roman', 10),
                            fg="white", bg="#579df8", bd=0, anchor="w",
                            image=self.menu_icons[item], compound=tk.LEFT,  # Icon bên trái chữ
                            command=lambda i=item: self.on_menu_click(i), padx=20, pady=5)
            btn.pack(fill=tk.X, padx=0, pady=5)
            self.menu_buttons[item] = btn
    
    def show_content(self, option):
        # Xóa nội dung cũ
        for widget in self.info.winfo_children():
            widget.destroy()

        # Tiêu đề (không hiển thị nếu là "Đăng xuất")
        if option != "Đăng xuất":
            title = tk.Label(self.info, text=option, font=('Times New Roman', 14, "bold"), bg="white")
            title.pack(fill="x", pady=5)

        # Hiển thị nội dung tương ứng
        if option == "Hồ sơ":
            self.show_basic_info()
        elif option == "Chấm công":
            self.attendance()
        elif option == "Xem bảng lương":
            self.show_salary()
        elif option == "Đăng xuất":
            self.signin() 

    # Thông tin chính
    def main_content(self):
        # Khung thông tin
        main = tk.Frame(self.root, bg="white")
        main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Thanh điều hướng trên cùng
        top = tk.Frame(main, bg="#d5e6f2", height=30)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        # Avt
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        avt = os.path.join(BASE_DIR, "..", "img", "user.jpg")
        img = Image.open(avt).resize((25, 25))
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
        img.putalpha(mask)
        avt_img = ImageTk.PhotoImage(img)

        label = tk.Label(top, image=avt_img, bg="#d5e6f2")
        label.pack(side="right", padx=5)
        label.image = avt_img

        # Nếu có dữ liệu thì hiển thị
        if self.employee:
            full_name = f"{self.employee['last_name']} {self.employee['first_name']}"
        else:
            full_name = "Không có dữ liệu"

        user_label = tk.Label(top, text=full_name, font=('Times New Roman', 10), fg="black", bg="#d5e6f2")
        user_label.pack(side=tk.RIGHT, padx=10)

        # Khung thông tin cá nhân
        self.info = tk.Frame(main, bg="white")
        self.info.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Hiển thị nội dung ban đầu
        self.on_menu_click("Hồ sơ")

    def on_menu_click(self, option):
        # Đổi màu nút menu
        if self.selected_button:
            self.selected_button.config(bg="#579df8")  # Trả lại màu cũ

        self.selected_button = self.menu_buttons[option]
        self.selected_button.config(bg="#357ae8")  # Màu khi được chọn

        # Cập nhật nội dung hiển thị
        self.show_content(option)

    # Hồ sơ
    def show_basic_info(self):
        # Xóa nội dung cũ trong khung thông tin
        for widget in self.info.winfo_children():
            widget.destroy()

        # Tiêu đề
        title = tk.Label(self.info, text="Thông tin cá nhân", font=('Times New Roman', 14, "bold"), bg="white")
        title.pack(fill="x", pady=5)

        # Nếu có dữ liệu thì hiển thị
        if self.employee:
            full_name = f"{self.employee.get('last_name', '')} {self.employee.get('first_name', '')}"
            emp_id = self.employee.get("emp_id", "Không có dữ liệu")
            email = self.employee.get("email", "Không có dữ liệu")
            phone_number = self.employee.get("phone_number", "Không có dữ liệu")
            hired_date = self.employee.get("hired_date", "Không có dữ liệu")
            status = self.employee.get("status", "Không có dữ liệu")
        else:
            full_name = "Không có dữ liệu"
            emp_id = "Không xác định"
            email = "Không xác định"
            phone_number = "Không xác định"
            hired_date = "Không xác định"
            status = "Không xác định"

        # Thông tin nhân viên
        info = [
            ("Tên nhân viên", full_name),
            ("Mã nhân viên", emp_id),
            ("Email", email),
            ("Số điện thoại", phone_number),
            ("Ngày làm việc", hired_date),
            ("Trạng thái", status)
        ]

        for label, value in info:
            row = tk.Frame(self.info, bg="white")
            row.pack(fill=tk.X, pady=2)

            lb_widget = tk.Label(row, text=label, font=('Times New Roman', 10), bg="white", width=20, anchor="w")
            lb_widget.pack(side=tk.LEFT)

            vl_widget = tk.Label(row, text=value, font=('Times New Roman', 10), bg="white", anchor="w")
            vl_widget.pack(side=tk.LEFT)

    # Chấm công
    def attendance(self):
        for widget in self.info.winfo_children():
            widget.destroy()

        title = tk.Label(self.info, text="Bảng Chấm Công", font=('Times New Roman', 14, "bold"), bg="white")
        title.pack(fill="x", pady=5)

        # Frame để chứa cả hai combobox
        filter_frame = tk.Frame(self.info, bg="white")
        filter_frame.pack(pady=10)

        # ComboBox lọc theo tháng
        self.month_filter = ttk.Combobox(filter_frame, values=[str(i) for i in range(1, 13)], state="readonly", width=15)
        self.month_filter.set("Chọn tháng")
        self.month_filter.grid(row=0, column=0, padx=5)
        self.month_filter.bind("<<ComboboxSelected>>", self.filter_by_date)

        # ComboBox lọc theo năm
        current_year = 2025  # Có thể thay bằng datetime.now().year
        self.year_filter = ttk.Combobox(filter_frame, values=[str(i) for i in range(current_year - 5, current_year + 1)], 
                                    state="readonly", width=15)
        self.year_filter.set("Chọn năm")
        self.year_filter.grid(row=0, column=1, padx=5)
        self.year_filter.bind("<<ComboboxSelected>>", self.filter_by_date)

        # Tạo bảng Treeview
        columns = ("Ngày", "Check-in", "Check-out", "Giờ làm", "Tăng ca")
        self.tree = ttk.Treeview(self.info, columns=columns, show="headings", height=10)

        # Tùy chỉnh kiểu tiêu đề cột
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Times New Roman', 11, 'bold'))

        # Thiết lập tiêu đề cột
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=2, pady=10)

        # Hiển thị dữ liệu ban đầu
        self.load_attendance_data()

    # Tải và hiển thị dữ liệu chấm công    
    def load_attendance_data(self, month=None, year=None):
        if not self.conn or not self.cursor:
            self.connect_db() 
        if not self.conn or not self.cursor:
            messagebox.showerror("Lỗi CSDL", "Không thể kết nối đến cơ sở dữ liệu!")
            return

        self.tree.delete(*self.tree.get_children())

        try:
            query = """
                SELECT DATE_FORMAT(date, '%d/%m/%Y') as date, 
                    TIME_FORMAT(check_in, '%H:%i') as check_in, 
                    TIME_FORMAT(check_out, '%H:%i') as check_out, 
                    work_hours, overtime_hours 
                FROM Attendance 
                WHERE emp_id = %s
            """
            params = [self.emp_id]

            # Thêm điều kiện lọc theo tháng nếu có
            if month:
                query += " AND MONTH(date) = %s"
                params.append(month)

            # Thêm điều kiện lọc theo năm nếu có
            if year:
                query += " AND YEAR(date) = %s"
                params.append(year)

            self.cursor.execute(query, tuple(params))
            rows = self.cursor.fetchall()

            for row in rows:
                values = (
                    row['date'],
                    row['check_in'],
                    row['check_out'] if row['check_out'] else "Chưa check-out",
                    str(row['work_hours']) if row['work_hours'] else "0",
                    str(row['overtime_hours']) if row['overtime_hours'] else "0"
                )
                self.tree.insert("", "end", values=values)
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi CSDL", f"Lỗi MySQL: {err}")

    # Lọc theo tháng và năm
    def filter_by_date(self, event):
        selected_month = self.month_filter.get()
        selected_year = self.year_filter.get()
        
        month = int(selected_month) if selected_month.isdigit() else None
        year = int(selected_year) if selected_year.isdigit() else None
        
        self.load_attendance_data(month=month, year=year)

    def show_salary(self):
        pass

    # Đăng xuất
    def signin(self):
        # Hiển thị hộp thoại xác nhận đăng xuất
        if messagebox.askokcancel("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            # Đóng kết nối cơ sở dữ liệu nếu đang mở
            if self.conn and self.conn.is_connected():
                self.cursor.close()
                self.conn.close()
            self.root.destroy()

def main(emp_id=""):
    root = tk.Tk()
    app = HRMApp(root, emp_id)
    root.mainloop()

# if __name__ == "__main__":
#     main(1)