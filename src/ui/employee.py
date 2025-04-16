import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import mysql.connector
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import src.salary.excel_utils
import src.salary.salary
import threading

from pathlib import Path
import sys

# Thêm thư mục src vào sys.path
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from database import DB

class HRMApp:
    def __init__(self, root, emp_id):
        self.root = root
        self.root.title("Nhân Viên")
        self.root.geometry("1200x550+50+50")
        # self.root.state('zoomed')
        
        self.emp_id = str(emp_id)
        self.select_btn = None
        self.menu_btn = {}
        self.menu_icons = {}
        self.employee = None
        self.departments = {}
        self.conn = None
        self.cursor = None

        self.connect_db()
        self.get_employee_data(emp_id)
        self.load_data()
        self.create_ui()

    # DB
    def connect_db(self):
        try:
            self.conn, self.cursor = DB.connect_to_database()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi CSDL", f"Lỗi kết nối MySQL: {err}")

    # Lấy dữ liệu nv
    def get_employee_data(self, emp_id):
        if not self.conn or not self.cursor:
            return
        self.employee = DB.get_employee_data(self.cursor, emp_id)

    # Load ds phòng ban
    def load_data(self):
        if not self.conn or not self.cursor:
            return
        self.departments = DB.load_departments(self.cursor)

    # Tạo giao diện chính
    def create_ui(self):
        self.sidebar = tk.Frame(self.root, width=250, bg="#e9f4f5")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.main_f = tk.Frame(self.root, bg="#fff")
        self.main_f.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_sidebar_content()

        self.content_area = tk.Frame(self.main_f, bg="#fff")
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.on_menu_click("Hồ sơ")

    # Tạo nội dung sidebar
    def create_sidebar_content(self):
        logo_f = tk.Frame(self.sidebar, bg="#e9f4f5", height=60)
        logo_f.pack(fill=tk.X)
        logo_l = tk.Label(logo_f, 
                          text="PYTECH", 
                          font=("Times New Roman", 20, "bold"), 
                          bg="#e9f4f5", 
                          fg="#0276f7")
        logo_l.pack(pady=10)

        profile_f = tk.Frame(self.sidebar, bg="#e9f4f5")
        profile_f.pack(fill=tk.X)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        data_f = os.path.join(BASE_DIR, "..", "..", "Data")
        img_path = self.get_employee_image(data_f)

        avatar_l = self.create_avatar(profile_f, img_path)
        avatar_l.pack(pady=10)

        if self.employee:
            full_name = f"{self.employee['last_name']} {self.employee['first_name']}"
            position = self.employee['position']
        else:
            full_name = "Tên Nhân Viên"
            position = "Chức vụ"
        
        name_l = tk.Label(profile_f, 
                          text=full_name, 
                          font=("Times New Roman", 14, "bold"), 
                          fg="#000", 
                          bg="#e9f4f5")
        name_l.pack()
        
        position_l = tk.Label(profile_f, 
                              text=position, 
                              font=("Times New Roman", 12), 
                              fg="#4a4949", 
                              bg="#e9f4f5")
        position_l.pack()

        separator = tk.Frame(self.sidebar, height=1, bg="#2d82b5")
        separator.pack(fill=tk.X, padx=20, pady=3)

        menu_f = tk.Frame(self.sidebar, bg="#e9f4f5")
        menu_f.pack(fill=tk.BOTH, expand=True, pady=10)

        menu_items = [
            ("Hồ sơ", "profile.png"),
            ("Chấm công", "check.png"),
            ("Xem bảng lương", "salary.png"),
            ("Đăng xuất", "logout.png")
        ]

        for item, icon_name in menu_items:
            btn_frame = tk.Frame(menu_f, bg="#e9f4f5", width=250, height=50)
            btn_frame.pack(fill=tk.X, pady=5)
            btn_frame.pack_propagate(False)

            icon = self.load_icon(BASE_DIR, icon_name)
            btn = tk.Button(btn_frame, 
                            text=item, 
                            font=("Times New Roman", 12), 
                            fg="#000", 
                            bg="#e9f4f5",
                            activebackground="#a6dcef", 
                            activeforeground="#000", 
                            pady=10,
                            bd=0, 
                            anchor="w",
                            command=lambda menu_item=item: self.on_menu_click(menu_item))
            if icon:
                btn.config(image=icon, compound=tk.LEFT, padx=25)
                self.menu_icons[item] = icon
            else:
                btn.config(padx=15)
            btn.pack(fill=tk.X)
            self.menu_btn[item] = btn

    # Lấy path ảnh nv
    def get_employee_image(self, folder):
        if os.path.exists(folder):
            for file_name in os.listdir(folder):
                if file_name.startswith(self.emp_id + "_"):
                    return os.path.join(folder, file_name)
        return None

    # Tạo avt nv
    def create_avatar(self, frame, img_path):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        default_img_path = os.path.join(BASE_DIR, "..", "img", "user.jpg")
        try:
            if img_path and os.path.exists(img_path):
                size = (120, 140)
                img = Image.open(img_path).resize(size) 
                avatar = ImageTk.PhotoImage(img)
                label = tk.Label(frame, image=avatar, bg="#e9f4f5")
                label.image = avatar
                return label
            else:
                raise FileNotFoundError("")
        except Exception as e:
            size = (120, 140)
            img = Image.open(default_img_path).resize(size)
            avatar = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=avatar, bg="#e9f4f5")
            label.image = avatar
            label.pack(pady=10)
            return label

    # Icon
    def load_icon(self, base_dir, icon_name):
        icon_path = os.path.join(base_dir, "..", "img", icon_name)
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path).resize((18, 18))
            return ImageTk.PhotoImage(icon_img)
        print(f"Không tìm thấy icon: {icon_name}")
        return None

    # Sự kiện click menu
    def on_menu_click(self, option):
        if self.select_btn:
            self.select_btn.config(bg="#e9f4f5")
        self.select_btn = self.menu_btn[option]
        self.select_btn.config(bg="#a6dcef")

        for widget in self.content_area.winfo_children():
            widget.destroy()

        if option == "Hồ sơ":
            self.show_profile()
        elif option == "Chấm công":
            self.show_attendance()
        elif option == "Xem bảng lương":
            self.show_salary()
        elif option == "Đăng xuất":
            self.signin()

    # Hiển thị thông tin hồ sơ
    def show_profile(self):
        profile_f = tk.Frame(self.content_area, bg="#fff")
        profile_f.pack(fill=tk.BOTH, expand=True)

        title_l = tk.Label(profile_f, 
                           text="Thông tin cá nhân", 
                           font=("Times New Roman", 18, "bold"), 
                           fg="#3b3939", 
                           bg="#fff")
        title_l.pack(side=tk.TOP, fill=tk.X, pady=(40, 20))

        section_f = tk.Frame(profile_f, bg="#fff")
        section_f.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        section_f.grid_columnconfigure(0, weight=3)
        section_f.grid_columnconfigure(1, weight=2)

        left_s = tk.Frame(section_f, bg="#fff")
        left_s.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

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

        fields = [
            ("Tên nhân viên", full_name),
            ("Mã nhân viên", emp_id),
            ("Email", email),
            ("Số điện thoại", phone_number),
            ("Ngày làm việc", hired_date),
            ("Trạng thái", status)
        ]

        details_f = tk.Frame(left_s, bg="#fff")
        details_f.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for index, (field_name, field_value) in enumerate(fields):
            column = index % 2
            row = index // 2

            label = tk.Label(details_f, 
                             text=f"{field_name}:", 
                             font=("Times New Roman", 9, "bold"), 
                             fg="#555", 
                             bg="#fff")
            label.grid(row=row*2, column=column, sticky="w", padx=10, pady=(10, 0))

            value_f = tk.Frame(details_f, 
                               bg="#f9f9f9", 
                               bd=1, 
                               relief="solid")
            value_f.grid(row=row*2+1, column=column, sticky="we", padx=10, pady=5)

            value_l = tk.Label(value_f, 
                               text=field_value, 
                               font=("Times New Roman", 10), 
                               fg="#222", 
                               bg="#f9f9f9", 
                               anchor="w", 
                               padx=10, 
                               pady=6)
            value_l.pack(fill=tk.X)

        details_f.grid_columnconfigure(0, weight=1)
        details_f.grid_columnconfigure(1, weight=1)

        right_s = tk.Frame(section_f, bg="#fff")
        right_s.grid(row=0, column=1, sticky="n", pady=10)
        self.display_profile_image(right_s)

    # Hiển thị ảnh hồ sơ
    def display_profile_image(self, frame):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        data = os.path.join(BASE_DIR, "..", "..", "Data")
        img_path = self.get_employee_image(data)
        if not img_path:
            img_path = os.path.join(BASE_DIR, "..", "img", "user.jpg")

        try:
            img = Image.open(img_path).resize((180, 180))
            profile_img = ImageTk.PhotoImage(img)
            img_f = tk.Frame(frame, 
                             bg="#fff", 
                             width=200, 
                             height=200, 
                             highlightbackground="#dddddd", 
                             highlightthickness=1)
            img_f.pack(pady=60)
            img_f.pack_propagate(False)
            img_label = tk.Label(img_f, image=profile_img, bg="#fff")
            img_label.place(relx=0.5, rely=0.5, anchor="center")
            img_f.image = profile_img
        except Exception as e:
            print(f"Lỗi ảnh hồ sơ: {e}")
            img_f = tk.Frame(frame, bg="#f0f0f0", width=200, height=200)
            img_f.pack(pady=10)
            img_f.pack_propagate(False)
            placeholder = tk.Label(img_f, 
                                   text="No Image", 
                                   font=("Times New Roman", 11), 
                                   bg="#f0f0f0", 
                                   fg="#888")
            placeholder.place(relx=0.5, rely=0.5, anchor="center")

    #  Chấm công
    def show_attendance(self):
        attendance_f = tk.Frame(self.content_area, bg="#fff")
        attendance_f.pack(fill=tk.BOTH, expand=True)

        title_l = tk.Label(attendance_f, 
                        text="Chấm công", 
                        font=("Times New Roman", 18, "bold"), 
                        fg="#333333", 
                        bg="#fff")
        title_l.pack(anchor="center", pady=(10, 20))

        btn_f = tk.Frame(attendance_f, bg="#fff")
        btn_f.pack(fill=tk.X, padx=20, pady=(0, 10))

        inner_f = tk.Frame(btn_f, bg="#fff")
        inner_f.pack(anchor="center")


        year_label = tk.Label(inner_f, text="Năm:", font=("Times New Roman", 11), bg="#fff")
        year_label.pack(side=tk.LEFT, padx=(10, 5))
        self.year_filter_attendance = ttk.Combobox(inner_f, values=["Tất cả"] + [str(i) for i in range(2020, 2026)], state="readonly", width=10)
        self.year_filter_attendance.set("Tất cả")
        self.year_filter_attendance.pack(side=tk.LEFT, padx=5)
        self.year_filter_attendance.bind("<<ComboboxSelected>>", self.filter_by_date)

        month_label = tk.Label(inner_f, text="Tháng:", font=("Times New Roman", 11), bg="#fff")
        month_label.pack(side=tk.LEFT, padx=(0, 5))
        self.month_filter_attendance = ttk.Combobox(inner_f, values=["Tất cả"] + [str(i) for i in range(1, 13)], state="readonly", width=10)
        self.month_filter_attendance.set("Tất cả")
        self.month_filter_attendance.pack(side=tk.LEFT, padx=5)
        self.month_filter_attendance.bind("<<ComboboxSelected>>", self.filter_by_date)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")
        excel_img_path = os.path.join(img_dir, "excel.png")

        if os.path.exists(excel_img_path):
            excel_img = Image.open(excel_img_path).resize((22, 22), Image.Resampling.LANCZOS)
            self.excel_icon = ImageTk.PhotoImage(excel_img)
        else:
            self.excel_icon = None

        excel_button = tk.Button(
            inner_f,
            text="Excel",
            image=self.excel_icon,
            compound=tk.TOP,
            command=lambda: src.salary.excel_utils.export_to_excel(self.tree, f"Attendance_{self.emp_id}"),
            bg="#fff",
            bd=0,
            width=50,
            height=50,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#65f06b"
        )
        if self.excel_icon:
            excel_button.image = self.excel_icon
        excel_button.pack(side=tk.LEFT, padx=10)

        table_frame = tk.Frame(attendance_f, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default") 

        style.layout("Treeview.Heading",
                    [('Treeheading.cell', {'sticky': 'nswe'}),
                    ('Treeheading.border', {'sticky': 'nswe', 'children': [
                        ('Treeheading.padding', {'sticky': 'nswe', 'children': [
                            ('Treeheading.image', {'side': 'right', 'sticky': ''}),
                            ('Treeheading.text', {'sticky': 'we'})]})]})])

        style.configure("Custom.Treeview.Heading",
                        font=("Times New Roman", 10, "bold"),
                        background="#9fd7f9",
                        foreground="#000",
                        relief="flat",
                        padding=5)

        style.configure("Custom.Treeview",
                        background="#fff",
                        foreground="black",
                        rowheight=25,
                        font=("Times New Roman", 10))

        style.map("Treeview",
                    background=[("selected", "#c6e3f5")],
                    foreground=[("selected", "black")])

        scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("Ngày", "Check-in", "Check-out", "Giờ làm", "Tăng ca")
        self.tree = ttk.Treeview(table_frame,
                                columns=columns,
                                show="headings",
                                yscrollcommand=scroll_y.set,
                                height=15,
                                style="Custom.Treeview")
        scroll_y.config(command=self.tree.yview)

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=180, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)

        self.load_attendance_data()

    # Load dữ liệu chấm công
    def load_attendance_data(self, month=None, year=None):
        if not self.conn or not self.cursor or not self.conn.is_connected():
            self.connect_db()
        if not self.conn or not self.cursor:
            messagebox.showerror("Lỗi CSDL", "Không thể kết nối đến cơ sở dữ liệu!")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = DB.get_attendance_by_emp(self.cursor, self.emp_id, month, year)
        if isinstance(rows, dict) and "error" in rows:
            messagebox.showerror("Lỗi CSDL", rows["error"])
            return

        for row in rows:
            values = (
                row['date'],
                row['check_in'],
                row['check_out'] if row['check_out'] else "Chưa check-out",
                str(row['work_hours']) if row['work_hours'] else "0",
                str(row['overtime_hours']) if row['overtime_hours'] else "0"
            )
            self.tree.insert("", "end", values=values)

        if not rows:
            messagebox.showinfo("Thông báo", "Không có dữ liệu chấm công!")

    # Lọc dữ liệu chấm công theo ngày
    def filter_by_date(self, event):
        selected_month = self.month_filter_attendance.get()
        selected_year = self.year_filter_attendance.get()
        
        month = selected_month if selected_month != "Tất cả" else None
        year = selected_year if selected_year != "Tất cả" else None
        self.load_attendance_data(month, year)

    # Hiển thị thông tin lương
    def show_salary(self):
        salary_frame = tk.Frame(self.content_area, bg="#fff")
        salary_frame.pack(fill=tk.BOTH, expand=True)

        title_l = tk.Label(salary_frame, 
                        text="Thông tin lương", 
                        font=("Times New Roman", 18, "bold"), 
                        fg="#333333", 
                        bg="#fff")
        title_l.pack(anchor="center", pady=(10, 20))

        # title_l = tk.Label(salary_frame, text="Thông tin lương", 
        #                    font=("Times New Roman", 18, "bold"), fg="#333333", bg="#f5f7fa")
        # title_l.pack(anchor="w", pady=(0, 20))

        filter_frame = tk.Frame(salary_frame, bg="#fff")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        inner_f = tk.Frame(filter_frame, bg="#fff")
        inner_f.pack(anchor="center")


        year_label = tk.Label(inner_f, text="Năm:", font=("Times New Roman", 11), bg="#fff")
        year_label.pack(side=tk.LEFT, padx=(10, 5))
        self.year_filter_salary = ttk.Combobox(inner_f, values=["Tất cả"] + [str(i) for i in range(2020, 2026)], state="readonly", width=10)
        self.year_filter_salary.set("Tất cả")
        self.year_filter_salary.pack(side=tk.LEFT, padx=5)
        self.year_filter_salary.bind("<<ComboboxSelected>>", self.filter_salary)

        month_label = tk.Label(inner_f, text="Tháng:", font=("Times New Roman", 11), bg="#fff")
        month_label.pack(side=tk.LEFT, padx=(0, 5))
        self.month_filter_salary = ttk.Combobox(inner_f, values=["Tất cả"] + [str(i) for i in range(1, 13)], state="readonly", width=10)
        self.month_filter_salary.set("Tất cả")
        self.month_filter_salary.pack(side=tk.LEFT, padx=5)
        self.month_filter_salary.bind("<<ComboboxSelected>>", self.filter_salary)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")
        excel_img_path = os.path.join(img_dir, "excel.png")
        salary_img_path = os.path.join(img_dir, "salary.png")

        if os.path.exists(excel_img_path):
            excel_img = Image.open(excel_img_path).resize((22, 22), Image.Resampling.LANCZOS)
            self.excel_icon = ImageTk.PhotoImage(excel_img)
        else:
            self.excel_icon = None

        if os.path.exists(salary_img_path):
            salary_img = Image.open(salary_img_path).resize((22, 22), Image.Resampling.LANCZOS)
            self.salary_icon = ImageTk.PhotoImage(salary_img)
        else:
            self.salary_icon = None

        excel_button = tk.Button(
            inner_f,
            text="Excel",
            image=self.excel_icon,
            compound=tk.TOP,
            command=lambda: src.salary.excel_utils.export_to_excel(self.salary_tree, f"Payroll_{self.emp_id}"),
            bg="#fff",
            bd=0,
            width=50,
            height=50,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#65f06b"
        )
        if self.excel_icon:
            excel_button.image = self.excel_icon
        excel_button.pack(side=tk.LEFT, padx=10)

        salary_button = tk.Button(
            inner_f,
            text="Lương",
            image=self.salary_icon,
            compound=tk.TOP,
            command=self.start_calculate_salary,
            bg="#fff",
            bd=0,
            width=50,
            height=50,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#ffcc00"
        )
        if self.salary_icon:
            salary_button.image = self.salary_icon
        salary_button.pack(side=tk.LEFT, padx=10)

        columns = ("Tháng/Năm", "Lương cơ bản", "Lương theo giờ", "Tiền tăng ca", "Tổng lương")
        self.salary_tree = ttk.Treeview(salary_frame, columns=columns, show="headings", height=15)

        style = ttk.Style()
        style.theme_use("default")

        style.layout("Treeview.Heading",
                    [('Treeheading.cell', {'sticky': 'nswe'}),
                    ('Treeheading.border', {'sticky': 'nswe', 'children': [
                        ('Treeheading.padding', {'sticky': 'nswe', 'children': [
                            ('Treeheading.image', {'side': 'right', 'sticky': ''}),
                            ('Treeheading.text', {'sticky': 'we'})]})]})])

        style.configure("Custom.Treeview.Heading",
                        font=("Times New Roman", 10, "bold"),
                        background="#9fd7f9",
                        foreground="#000",
                        relief="flat",
                        padding=5)

        style.configure("Custom.Treeview",
                        background="#fff",
                        foreground="black",
                        rowheight=25,
                        font=("Times New Roman", 10))

        style.map("Treeview",
                    background=[("selected", "#c6e3f5")],
                    foreground=[("selected", "black")])

        for col in columns:
            self.salary_tree.heading(col, text=col)
            self.salary_tree.column(col, width=180, anchor="center")

        self.salary_tree.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.load_salary_data()

    #  Load dữ liệu lương
    def load_salary_data(self, month=None, year=None):
        if not self.conn or not self.cursor or not self.conn.is_connected():
            self.connect_db()
        if not self.conn or not self.cursor:
            messagebox.showerror("Lỗi CSDL", "Không thể kết nối đến cơ sở dữ liệu!")
            return

        for item in self.salary_tree.get_children():
            self.salary_tree.delete(item)

        rows = DB.get_salary_data(self.cursor, self.emp_id, month, year)
        if isinstance(rows, dict) and "error" in rows:
            messagebox.showerror("Lỗi CSDL", rows["error"])
            return

        for row in rows:
            base_salary = row['base_salary'] if row['base_salary'] is not None else 0
            time_salary = row['time_salary'] if row['time_salary'] is not None else 0
            overtime_salary = row['overtime_salary'] if row['overtime_salary'] is not None else 0
            total_salary = base_salary + time_salary + overtime_salary

            values = (
                row['month_year'],
                f"{base_salary:,.0f}",
                f"{time_salary:,.0f}",
                f"{overtime_salary:,.0f}",
                f"{total_salary:,.0f}"
            )
            self.salary_tree.insert("", "end", values=values)

        if not rows:
            messagebox.showinfo("Thông báo", "Không có dữ liệu lương!")

    # Lọc dữ liệu lương
    def filter_salary(self, event=None):
        selected_month = self.month_filter_salary.get()
        selected_year = self.year_filter_salary.get()
        
        month = selected_month if selected_month != "Tất cả" else None
        year = selected_year if selected_year != "Tất cả" else None
        
        self.load_salary_data(month=month, year=year)

    # Bắt đầu tính lương
    def start_calculate_salary(self):
        if not self.emp_id:
            messagebox.showerror("Lỗi", "Không có mã nhân viên!")
            return
        self.root.config(cursor="wait")
        messagebox.showinfo("Thông báo", "Đang tính lương, vui lòng chờ...")
        thread = threading.Thread(target=self.calculate_salary, daemon=True)
        thread.start()

    # Tính lương
    def calculate_salary(self):
        try:
            success = src.salary.salary.calculate_and_update_payroll(emp_id=self.emp_id)
            self.root.after(0, lambda: self.on_calculate_complete(success))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi tính lương: {str(e)}"))

    # Hoàn tất lương
    def on_calculate_complete(self, success):
        self.root.config(cursor="")
        if success:
            messagebox.showinfo("Thành công", "Đã tính toán và cập nhật lương thành công!")
            if self.conn and self.conn.is_connected():
                DB.close_connection(self.conn, self.cursor)
            self.connect_db()
            self.load_salary_data()
            self.salary_tree.update()
        else:
            messagebox.showerror("Lỗi", "Tính lương thất bại! Vui lòng kiểm tra dữ liệu hoặc kết nối.")

    # Đăng xuất
    def signin(self):
        if messagebox.askokcancel("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            if self.conn and self.conn.is_connected():
                DB.close_connection(self.conn, self.cursor)
            self.root.destroy()

def main(emp_id=""):
    root = tk.Tk()
    app = HRMApp(root, emp_id)
    root.mainloop()

if __name__ == "__main__":
    main(4)     # Thanh An
