import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from PIL import Image, ImageTk, ImageDraw
import os
from datetime import datetime

class ManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Nhân Sự")
        self.root.geometry("1100x500+100+100")
        self.root.resizable(True, True)

        self.bg_color = "#f0f2f5"
        self.menu_color = "#84b5f5"
        self.selected_menu_color = "#5399f5"
        self.header_color = "#d5e6f2"
        self.root.configure(bg=self.bg_color)

        self.selected_button = None
        self.current_content = None
        self.current_menu = "Nhân Sự"

        # Header
        self.header_frame = tk.Frame(self.root, bg=self.header_color, height=50)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        # Logo
        logo_label = tk.Label(self.header_frame, text="PYTECH", font=("Times New Roman", 20, "bold"), fg="#357ae8", bg=self.header_color)
        logo_label.pack(side=tk.LEFT, padx=10)

        # Tìm kiếm
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.header_frame, textvariable=self.search_var, font=("Times New Roman", 10), width=20)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        self.search_entry.insert(0, "Tìm kiếm nhân viên...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "Tìm kiếm nhân viên..." else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "Tìm kiếm nhân viên...") if not self.search_entry.get() else None)
        self.search_entry.bind("<KeyRelease>", self.search_employee)

        # Bộ lọc: Chức vụ
        self.position_var = tk.StringVar()
        position_label = tk.Label(self.header_frame, text="Chức vụ:", font=("Times New Roman", 10), bg=self.header_color)
        position_label.pack(side=tk.LEFT, padx=5)
        self.position_combo = ttk.Combobox(self.header_frame, textvariable=self.position_var, font=("Times New Roman", 10), width=15)
        self.position_combo['values'] = ["Tất cả", "Developer", "Tester", "HR Manager", "Accountant", "Designer"]
        self.position_combo.set("Tất cả")
        self.position_combo.pack(side=tk.LEFT, padx=5)
        self.position_combo.bind("<<ComboboxSelected>>", self.filter_employee)

        # Bộ lọc: Phòng ban
        self.dep_var = tk.StringVar()
        dep_label = tk.Label(self.header_frame, text="Phòng ban:", font=("Times New Roman", 10), bg=self.header_color)
        dep_label.pack(side=tk.LEFT, padx=5)
        self.dep_combo = ttk.Combobox(self.header_frame, textvariable=self.dep_var, font=("Times New Roman", 10), width=15)
        self.dep_combo['values'] = ["Tất cả", "IT Department", "HR Department", "Finance Department"]
        self.dep_combo.set("Tất cả")
        self.dep_combo.pack(side=tk.LEFT, padx=5)
        self.dep_combo.bind("<<ComboboxSelected>>", self.filter_employee)

        # Bộ lọc: Năm
        self.year_var = tk.StringVar()
        year_label = tk.Label(self.header_frame, text="Năm:", font=("Times New Roman", 10), bg=self.header_color)
        year_label.pack(side=tk.LEFT, padx=5)
        self.year_combo = ttk.Combobox(self.header_frame, textvariable=self.year_var, font=("Times New Roman", 10), width=6)
        self.year_combo['values'] = ["Tất cả"] + [str(year) for year in range(2020, 2026)]
        self.year_combo.set("Tất cả")
        self.year_combo.pack(side=tk.LEFT, padx=5)
        self.year_combo.bind("<<ComboboxSelected>>", self.filter_employee)

        # Bộ lọc: Tháng
        self.month_var = tk.StringVar()
        month_label = tk.Label(self.header_frame, text="Tháng:", font=("Times New Roman", 10), bg=self.header_color)
        month_label.pack(side=tk.LEFT, padx=5)
        self.month_combo = ttk.Combobox(self.header_frame, textvariable=self.month_var, font=("Times New Roman", 10), width=6)
        self.month_combo['values'] = ["Tất cả"] + [f"{month:02d}" for month in range(1, 13)]
        self.month_combo.set("Tất cả")
        self.month_combo.pack(side=tk.LEFT, padx=5)
        self.month_combo.bind("<<ComboboxSelected>>", self.filter_employee)

        # Avt
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        avt_path = os.path.join(BASE_DIR, "..", "img", "manager.png")
        img = Image.open(avt_path).resize((25, 25))
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
        img.putalpha(mask)
        self.avt_img = ImageTk.PhotoImage(img)

        label = tk.Label(self.header_frame, image=self.avt_img, bg=self.header_color)
        label.pack(side=tk.RIGHT, padx=5)

        # Manager
        user_label = tk.Label(self.header_frame, text="Manager", font=('Times New Roman', 10), fg="black", bg=self.header_color)
        user_label.pack(side=tk.RIGHT, padx=10)

        # Menu
        self.menu_frame = tk.Frame(self.root, bg=self.menu_color, width=200)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Danh sách menu và icon
        menu_items = [
            ("Nhân Sự", "people.png"),
            ("Thêm", "add-user.png"),
            ("Sửa", "edit.png"),
            ("Xóa", "delete.png"),
            ("Chấm công", "check.png"),
            ("Lương", "salary.png"),
            ("Đăng xuất", "logout.png")
        ]
        self.menu_buttons = {}
        self.menu_icons = {}
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        for item, icon_name in menu_items:
            # Tải icon
            icon_path = os.path.join(BASE_DIR, "..", "img", icon_name)
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path).resize((20, 20)) 
                icon = ImageTk.PhotoImage(icon_img)
            else:
                icon = ImageTk.PhotoImage(Image.new("RGBA", (20, 20), (0, 0, 0, 0)))
                print(f"Không tìm thấy icon: {icon_name}")

            self.menu_icons[item] = icon 
            btn = tk.Button(self.menu_frame, 
                            text=item, 
                            font=("Times New Roman", 11), 
                            bg=self.menu_color, 
                            fg="white",
                            bd=0, 
                            command=lambda x=item: self.on_menu_click(x),
                            image=self.menu_icons[item], 
                            compound=tk.LEFT,
                            anchor="w",
                            padx=10,
                            pady=10,
                            width=100) 
            btn.pack(fill=tk.X, pady=0, padx=0)
            self.menu_buttons[item] = btn

        self.content_frame = tk.Frame(self.root, bg=self.bg_color)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.on_menu_click("Nhân Sự")

    # Xử lý sự kiện nhấn menu
    def on_menu_click(self, option):
        if self.selected_button:
            self.selected_button.config(bg=self.menu_color)
        self.selected_button = self.menu_buttons[option]
        self.selected_button.config(bg=self.selected_menu_color)
        self.current_menu = option
        
        # Đặt lại bộ lọc về mặc định khi chuyển menu
        if option != "Đăng xuất":
            self.position_var.set("Tất cả")
            self.dep_var.set("Tất cả")
            self.year_var.set("Tất cả")
            self.month_var.set("Tất cả")
            self.search_var.set("")
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, "Tìm kiếm nhân viên...")
        
        self.menu_action(option)

    # Xóa nội dung hiện tại trong khung content_frame để hiển thị nội dung mới
    def clear_content(self):
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None

    # Điều hướng trên menu
    def menu_action(self, item):
        self.clear_content()
        if item == "Nhân Sự":
            self.show_employee_list()
        elif item == "Thêm":
            self.show_add_employee()
        elif item == "Sửa":
            self.show_edit_employee()
        elif item == "Xóa":
            self.show_delete_employee()
        elif item == "Chấm công":
            self.show_attendance()
        elif item == "Lương":
            self.show_salary()
        elif item == "Đăng xuất":
            self.signin()

    # Hiển thị ds nhân viên
    def show_employee_list(self):
        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"))

        columns = ("STT", "Mã NV", "Nhân Viên", "Chức Vụ", "Phòng Ban", "Email", "Số Điện Thoại", "Ngày Tuyển Dụng")
        self.tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("STT", width=50, anchor="center")
        self.tree.column("Mã NV", width=70, anchor="center")
        self.tree.column("Nhân Viên", width=150, anchor="w")
        self.tree.column("Chức Vụ", width=100, anchor="w")
        self.tree.column("Phòng Ban", width=100, anchor="w")
        self.tree.column("Email", width=150, anchor="center")
        self.tree.column("Số Điện Thoại", width=100, anchor="center")
        self.tree.column("Ngày Tuyển Dụng", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_employee_data()

    # Tải dữ liệu nhân viên từ database và hiển thị
    def load_employee_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            conn = mysql.connector.connect(host="localhost", user="nii", password="", database="Face_Recognition")
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT e.emp_id, e.first_name, e.last_name, e.position, e.email, e.phone_number, e.hired_date, d.dep_name
                FROM Employees e
                LEFT JOIN Departments d ON e.dep_id = d.dep_id
                WHERE e.status = 'active'
                ORDER BY e.emp_id ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for idx, row in enumerate(rows, 1):
                emp_id = row['emp_id']
                full_name = f"{row['last_name']} {row['first_name']}"
                position = row['position'] if row['position'] else "N/A"
                department = row['dep_name'] if row['dep_name'] else "N/A"
                email = row['email'] if row['email'] else "N/A"
                phone = row['phone_number'] if row['phone_number'] else "N/A"
                hired_date = row['hired_date'].strftime("%d/%m/%Y") if row['hired_date'] else "N/A"
                self.tree.insert("", "end", values=(idx, emp_id, full_name, position, department, email, phone, hired_date))
            cursor.close()
            conn.close()
            if not rows:
                messagebox.showinfo("Thông báo", "Không có nhân viên nào trong cơ sở dữ liệu!")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

    # Tìm kiếm nhân viên khi nhập từ khóa
    def search_employee(self, event):
        self.filter_employee(event)

    # Lọc dữ liệu nhân viên hoặc chấm công dựa trên từ khóa, chức vụ, phòng ban, năm, tháng
    def filter_employee(self, event):
        search_term = self.search_var.get().strip().lower()
        if search_term == "tìm kiếm nhân viên...":
            search_term = ""
        position_filter = self.position_var.get()
        dep_filter = self.dep_var.get()
        year_filter = self.year_var.get()
        month_filter = self.month_var.get()

        if self.current_menu == "Nhân Sự" and hasattr(self, 'tree'):
            tree = self.tree
        elif self.current_menu == "Chấm công" and hasattr(self, 'attendance_tree'):
            tree = self.attendance_tree
        else:
            return

        for item in tree.get_children():
            tree.delete(item)

        try:
            print("Connecting to database...")
            conn = mysql.connector.connect(host="localhost", user="nii", password="", database="Face_Recognition")
            cursor = conn.cursor(dictionary=True)

            print("After Connected to database !")
            
            if self.current_menu == "Nhân Sự":
                query = """
                    SELECT e.emp_id, e.first_name, e.last_name, e.position, e.email, e.phone_number, e.hired_date, d.dep_name
                    FROM Employees e
                    LEFT JOIN Departments d ON e.dep_id = d.dep_id
                    WHERE e.status = 'active'
                """
                params = []

                if search_term:
                    if search_term.isdigit():
                        query += " AND e.emp_id = %s"
                        params.append(int(search_term))
                    else:
                        query += " AND LOWER(CONCAT(e.first_name, ' ', e.last_name)) LIKE %s"
                        params.append(f"%{search_term}%")

                if position_filter != "Tất cả":
                    query += " AND (e.position = %s OR e.position IS NULL)"
                    params.append(position_filter)

                if dep_filter != "Tất cả":
                    query += " AND (d.dep_name = %s OR d.dep_name IS NULL)"
                    params.append(dep_filter)

                if year_filter != "Tất cả":
                    query += " AND (YEAR(e.hired_date) = %s OR e.hired_date IS NULL)"
                    params.append(int(year_filter))

                if month_filter != "Tất cả":
                    query += " AND (MONTH(e.hired_date) = %s OR e.hired_date IS NULL)"
                    params.append(int(month_filter))

                query += " ORDER BY e.emp_id ASC"
                cursor.execute(query, params)
                rows = cursor.fetchall()

                for idx, row in enumerate(rows, 1):
                    emp_id = row['emp_id']
                    full_name = f"{row['last_name']} {row['first_name']}"
                    position = row['position'] if row['position'] else "N/A"
                    department = row['dep_name'] if row['dep_name'] else "N/A"
                    email = row['email'] if row['email'] else "N/A"
                    phone = row['phone_number'] if row['phone_number'] else "N/A"
                    hired_date = row['hired_date'].strftime("%d/%m/%Y") if row['hired_date'] else "N/A"
                    tree.insert("", "end", values=(idx, emp_id, full_name, position, department, email, phone, hired_date))

            elif self.current_menu == "Chấm công":
                query = """
                    SELECT e.emp_id, e.first_name, e.last_name, a.date, a.check_in, a.check_out, a.work_hours, a.overtime_hours, e.position, d.dep_name
                    FROM Employees e
                    LEFT JOIN Attendance a ON e.emp_id = a.emp_id
                    LEFT JOIN Departments d ON e.dep_id = d.dep_id
                    WHERE e.status = 'active'
                """
                params = []

                if search_term:
                    if search_term.isdigit():
                        query += " AND e.emp_id = %s"
                        params.append(int(search_term))
                    else:
                        query += " AND LOWER(CONCAT(e.first_name, ' ', e.last_name)) LIKE %s"
                        params.append(f"%{search_term}%")

                if position_filter != "Tất cả":
                    query += " AND (e.position = %s OR e.position IS NULL)"
                    params.append(position_filter)

                if dep_filter != "Tất cả":
                    query += " AND (d.dep_name = %s OR d.dep_name IS NULL)"
                    params.append(dep_filter)

                if year_filter != "Tất cả":
                    query += " AND (YEAR(a.date) = %s OR a.date IS NULL)"
                    params.append(int(year_filter))

                if month_filter != "Tất cả":
                    query += " AND (MONTH(a.date) = %s OR a.date IS NULL)"
                    params.append(int(month_filter))

                query += " ORDER BY a.date DESC"
                cursor.execute(query, params)
                rows = cursor.fetchall()

                for idx, row in enumerate(rows, 1):
                    emp_id = row['emp_id']
                    full_name = f"{row['last_name']} {row['first_name']}"
                    date = row['date'].strftime("%d/%m/%Y") if row['date'] else "N/A"
                    check_in = row['check_in'].strftime("%H:%M") if row['check_in'] else "N/A"
                    check_out = row['check_out'].strftime("%H:%M") if row['check_out'] else "N/A"
                    work_hours = f"{row['work_hours']:.2f}" if row['work_hours'] is not None else "0.00"
                    overtime_hours = f"{row['overtime_hours']:.2f}" if row['overtime_hours'] is not None else "0.00"
                    tree.insert("", "end", values=(idx, emp_id, full_name, date, check_in, check_out, work_hours, overtime_hours))

            cursor.close()
            conn.close()
            if not rows:
                messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu phù hợp!")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

    # Hiển thị bảng chấm công
    def show_attendance(self):
        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"))

        columns = ("STT", "Mã NV", "Nhân Viên", "Ngày", "Check-in", "Check-out", "Giờ Làm", "Giờ Tăng Ca")
        self.attendance_tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)
        for col in columns:
            self.attendance_tree.heading(col, text=col)
        self.attendance_tree.column("STT", width=50, anchor="center")
        self.attendance_tree.column("Mã NV", width=70, anchor="center")
        self.attendance_tree.column("Nhân Viên", width=150, anchor="w")
        self.attendance_tree.column("Ngày", width=100, anchor="center")
        self.attendance_tree.column("Check-in", width=100, anchor="center")
        self.attendance_tree.column("Check-out", width=100, anchor="center")
        self.attendance_tree.column("Giờ Làm", width=100, anchor="center")
        self.attendance_tree.column("Giờ Tăng Ca", width=100, anchor="center")
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)

        self.load_attendance_data()

    # Tải dữ liệu chấm công từ database và hiển thị
    def load_attendance_data(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        try:
            conn = mysql.connector.connect(host="localhost", user="nii", password="", database="Face_Recognition")
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT e.emp_id, e.first_name, e.last_name, a.date, a.check_in, a.check_out, a.work_hours, a.overtime_hours
                FROM Employees e
                LEFT JOIN Attendance a ON e.emp_id = a.emp_id
                WHERE e.status = 'active'
                ORDER BY a.date DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for idx, row in enumerate(rows, 1):
                emp_id = row['emp_id']
                full_name = f"{row['last_name']} {row['first_name']}"
                date = row['date'].strftime("%d/%m/%Y") if row['date'] else "N/A"
                check_in = row['check_in'].strftime("%H:%M") if row['check_in'] else "N/A"
                check_out = row['check_out'].strftime("%H:%M") if row['check_out'] else "N/A"
                work_hours = f"{row['work_hours']:.2f}" if row['work_hours'] is not None else "0.00"
                overtime_hours = f"{row['overtime_hours']:.2f}" if row['overtime_hours'] is not None else "0.00"
                self.attendance_tree.insert("", "end", values=(idx, emp_id, full_name, date, check_in, check_out, work_hours, overtime_hours))
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

    # Thêm nhân viên mới
    def show_add_employee(self):
        pass

    # Sửa thông tin nhân viên
    def show_edit_employee(self):
        pass

    # Xóa nhân viên
    def show_delete_employee(self):
        pass

    # Lương
    def show_salary(self):
        pass

    # Đăng xuất
    def signin(self):
        if messagebox.askokcancel("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ManagerApp(root)
    root.mainloop()