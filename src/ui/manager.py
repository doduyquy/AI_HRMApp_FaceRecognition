import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from PIL import Image, ImageTk, ImageDraw
import os
import re
import datetime
from tkcalendar import DateEntry
from pathlib import Path

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import src.salary.excel_utils  
import src.salary.salary  
import src.salary.statistic  
import threading 

# Thêm thư mục src vào sys.path
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from database import DB

class ManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Nhân Sự")
        self.root.state('zoomed')
        # self.root.geometry("1300x650")
        self.root.resizable(True, True)

        self.bg_color = "#f7f8fa"
        self.menu_color = "#fff"
        self.selected_menu_color = "#3eaef4"
        self.header_color = "#fff"
        self.root.configure(bg=self.bg_color)

        self.day_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.dep_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.month_var = tk.StringVar()

        self.content_frame = tk.Frame(self.root, bg=self.bg_color)
        self.content_frame.place(relwidth=1, relheight=1) 

        self.entries = {}
        self.selected_button = None
        self.current_content = None
        self.search_entry = None
        self.current_menu = "Nhân Sự"

        self.stat_app = None
        self.conn, self.cursor = DB.connect_to_database()
        self.show_employee_list()

        # Header
        self.header_frame = tk.Frame(self.root, bg=self.header_color, height=55)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(0)

        # Logo
        logo_label = tk.Label(self.header_frame, text="PYTECH", font=("Times New Roman", 20, "bold"), fg="#357ae8", bg=self.header_color)
        logo_label.pack(side=tk.LEFT, padx=10)

        # Avt
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        avt_path = os.path.join(BASE_DIR, "..", "img", "manager.png")
        img = Image.open(avt_path).resize((30, 30))
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
        img.putalpha(mask)
        self.avt_img = ImageTk.PhotoImage(img)

        label = tk.Label(self.header_frame, image=self.avt_img, bg=self.header_color)
        label.pack(side=tk.RIGHT, padx=5)

        # Manager
        user_label = tk.Label(self.header_frame, text="Manager", font=('Times New Roman', 13), fg="black", bg=self.header_color)
        user_label.pack(side=tk.RIGHT, padx=10)

        # Menu
        self.menu_frame = tk.Frame(self.root, bg=self.menu_color, width=200)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Danh sách menu và icon
        menu_items = [
            ("Nhân Sự", "people.png"),
            ("Chấm công", "check.png"),
            ("Lương", "salary.png"),
            ("Thống Kê", "stats.png"),
            ("Đăng xuất", "logout.png")
        ]
        self.menu_buttons = {}
        self.menu_icons = {}
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        for item, icon_name in menu_items:
            # Tải icon
            icon_path = os.path.join(BASE_DIR, "..", "img", icon_name)
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path).resize((15, 15)) 
                icon = ImageTk.PhotoImage(icon_img)
            else:
                icon = ImageTk.PhotoImage(Image.new("RGBA", (20, 20), (0, 0, 0, 0)))
                print(f"Không tìm thấy icon: {icon_name}")

            self.menu_icons[item] = icon 
            btn = tk.Button(self.menu_frame, 
                            text=item, 
                            font=("Times New Roman", 11), 
                            bg=self.menu_color, 
                            fg="#000",
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

        if option in self.menu_buttons:
            self.selected_button = self.menu_buttons[option]
            self.selected_button.config(bg=self.selected_menu_color) 
        else:
            print(f"Menu option '{option}' không hợp lệ!")

        self.current_menu = option

        if option != "Đăng xuất":
            if hasattr(self, 'position_var'):
                self.position_var.set("Tất cả")
            if hasattr(self, 'dep_var'):
                self.dep_var.set("Tất cả")
            if hasattr(self, 'year_var'):
                self.year_var.set("Tất cả")
            if hasattr(self, 'month_var'):
                self.month_var.set("Tất cả")
            if hasattr(self, 'search_var'):
                self.search_var.set("")
            
            if hasattr(self, 'search_entry') and self.search_entry.winfo_exists():  
                self.search_entry.delete(0, tk.END) 

        self.menu_action(option)

    # Xóa nội dung hiện tại trong khung content_frame
    def clear_content(self):
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None

    # Điều hướng trên menu
    def menu_action(self, item):
        self.clear_content()
        if item == "Nhân Sự":
            self.show_employee_list()
        elif item == "Chấm công":
            self.show_attendance()
        elif item == "Lương":
            self.show_salary()
        elif item == "Thống Kê":
            self.show_statistics()  
        elif item == "Đăng xuất":
            self.signin()

    # Hiển thị danh sách nhân viên
    def show_employee_list(self):
        if self.current_content:
            self.current_content.destroy() 

        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.current_content, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=2, padx=5)

        buttons_inner_frame = tk.Frame(button_frame, bg=self.bg_color)
        buttons_inner_frame.pack(anchor="center")

        # Load các icon
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")

        add_img = Image.open(os.path.join(img_dir, "add.png")).resize((22, 22), Image.Resampling.LANCZOS)
        edit_img = Image.open(os.path.join(img_dir, "edit.png")).resize((22, 22), Image.Resampling.LANCZOS)
        delete_img = Image.open(os.path.join(img_dir, "delete.png")).resize((22, 22), Image.Resampling.LANCZOS)
        excel_img = Image.open(os.path.join(img_dir, "excel.png")).resize((22, 22), Image.Resampling.LANCZOS)
        reset_img = Image.open(os.path.join(img_dir, "reset.png")).resize((22, 22), Image.Resampling.LANCZOS)
        search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22), Image.Resampling.LANCZOS)

        add_icon = ImageTk.PhotoImage(add_img)
        edit_icon = ImageTk.PhotoImage(edit_img)
        delete_icon = ImageTk.PhotoImage(delete_img)
        excel_icon = ImageTk.PhotoImage(excel_img)
        reset_icon = ImageTk.PhotoImage(reset_img)
        search_icon = ImageTk.PhotoImage(search_img)

        # Tạo style
        style = ttk.Style()
        style.configure("Custom.TCombobox",
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        font=("Times New Roman", 11),  
                        foreground="black",
                        fieldbackground="white",
                        background="white")

        style.map("Custom.TCombobox",
                fieldbackground=[("readonly", "white")],
                background=[("readonly", "white")],
                foreground=[("readonly", "black")])

        # Frame chứa bộ lọc
        filter_frame = tk.Frame(buttons_inner_frame, bg=self.bg_color)
        filter_frame.pack(side=tk.LEFT, padx=10)

        # Bộ lọc Chức vụ
        self.position_var = tk.StringVar()
        position_label = tk.Label(filter_frame, 
                                  text="Chức vụ:", 
                                  bg=self.bg_color, 
                                  font=("Times New Roman", 11))
        position_label.pack(side=tk.LEFT)
        position_combo = ttk.Combobox(filter_frame, 
                                      textvariable=self.position_var, 
                                      width=10, 
                                      font=("Times New Roman", 9), 
                                      style="Custom.TCombobox")
        position_combo['values'] = ("Tất cả", "Employee", "Manager", "IT") 
        position_combo.set("Tất cả")
        position_combo.pack(side=tk.LEFT, padx=2)
        position_combo.bind("<<ComboboxSelected>>", lambda event: self.filter_employee_list())

        # Bộ lọc Phòng ban
        self.department_var = tk.StringVar()
        dept_label = tk.Label(filter_frame, 
                              text="Phòng ban:", 
                              bg=self.bg_color, 
                              font=("Times New Roman", 11))
        dept_label.pack(side=tk.LEFT, padx=(10, 0))
        dept_combo = ttk.Combobox(filter_frame, 
                                  textvariable=self.department_var, 
                                  width=15, 
                                  font=("Times New Roman", 9),
                                  style="Custom.TCombobox")
        dept_combo['values'] = ("Tất cả", "Employee", "Manager Department", "IT Department")  
        dept_combo.set("Tất cả")
        dept_combo.pack(side=tk.LEFT, padx=2)
        dept_combo.bind("<<ComboboxSelected>>", lambda event: self.filter_employee_list())

        # Bộ lọc Trạng thái
        self.status_var = tk.StringVar()
        status_label = tk.Label(filter_frame, 
                                text="Trạng thái:", 
                                bg=self.bg_color, 
                                font=("Times New Roman", 11))
        status_label.pack(side=tk.LEFT, padx=(10, 0))
        status_combo = ttk.Combobox(filter_frame, 
                                    textvariable=self.status_var, 
                                    width=15, 
                                    font=("Times New Roman", 9),
                                    style="Custom.TCombobox")
        status_combo['values'] = ("Tất cả", "Đang làm việc", "Đã nghỉ") 
        status_combo.set("Tất cả")
        status_combo.pack(side=tk.LEFT, padx=2)
        status_combo.bind("<<ComboboxSelected>>", lambda event: self.filter_employee_list())

        # Frame chứa ô tìm kiếm và nút tìm kiếm
        search_frame = tk.Frame(buttons_inner_frame, 
                                bg="white", 
                                relief="flat", 
                                highlightthickness=1, 
                                highlightbackground="#4c84f5")
        search_frame.pack(side=tk.LEFT, padx=10, ipady=4)

        # Ô nhập tìm kiếm
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Times New Roman", 11),
            width=22,
            fg="gray",
            relief="flat",
            borderwidth=0,
            bg="white"
        )
        self.search_entry.insert(0, "Tìm kiếm...")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_placeholder)
        self.search_entry.bind("<Return>", self.search_employee)
        
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Nút Tìm kiếm 
        search_button = tk.Button(
            search_frame,
            image=search_icon,
            command=self.search_employee,
            bg="white",
            bd=0,
            relief="flat",
            activebackground="#fff",
            width=20, 
            height=25,
        )
        search_button.image = search_icon
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

        # Nút Thêm
        add_button = tk.Button(buttons_inner_frame, 
            text="Thêm", 
            image=add_icon, 
            compound=tk.TOP,
            command=self.add_employee,
            bg="#f7f8fa", 
            bd=0, 
            width=50, 
            height=50,
            font=("Times New Roman", 9), 
            relief="flat",
            activebackground="#adedb0")
        add_button.image = add_icon
        add_button.pack(side=tk.LEFT, padx=3)

        # Nút Sửa
        edit_button = tk.Button(buttons_inner_frame, 
            text="Sửa", 
            image=edit_icon, 
            compound=tk.TOP,
            command=self.edit_employee,
            bg="#f7f8fa", 
            bd=0, 
            width=50, 
            height=50,
            font=("Times New Roman", 9), 
            relief="flat",
            activebackground="#f2c47e")
        edit_button.image = edit_icon
        edit_button.pack(side=tk.LEFT, padx=3)

        # Nút Xóa
        delete_button = tk.Button(buttons_inner_frame, 
            text="Xóa", 
            image=delete_icon, 
            compound=tk.TOP,
            command=self.delete_employee,
            bg="#f7f8fa", 
            bd=0, 
            width=50, 
            height=50,
            font=("Times New Roman", 9), 
            relief="flat",
            activebackground="#f57a7a")
        delete_button.image = delete_icon
        delete_button.pack(side=tk.LEFT, padx=3)

        # Nút Excel
        excel_button = tk.Button(buttons_inner_frame, 
            text="Excel", 
            image=excel_icon, 
            compound=tk.TOP,
            command=lambda: src.salary.excel_utils.export_to_excel(self.tree, "Employees"), 
            bg="#f7f8fa", 
            bd=0, 
            width=50, 
            height=50,
            font=("Times New Roman", 9), 
            relief="flat",
            activebackground="#65f06b")
        excel_button.image = excel_icon
        excel_button.pack(side=tk.LEFT, padx=3)

        # Nút Reset
        reset_button = tk.Button(buttons_inner_frame,
            text="Làm mới",
            image=reset_icon, 
            compound=tk.TOP,
            command=self.reset_employee_list, 
            bg="#f7f8fa",
            bd=0,
            width=50,
            height=50,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#7d8e96")
        reset_button.image = reset_icon 
        reset_button.pack(side=tk.LEFT, padx=3)

        # Cấu hình Treeview
        style = ttk.Style()
        style.theme_use("clam") 

        style.layout("Treeview.Heading",
                    [('Treeheading.cell', {'sticky': 'nswe'}),
                    ('Treeheading.border', {'sticky': 'nswe', 'children': [
                        ('Treeheading.padding', {'sticky': 'nswe', 'children': [
                            ('Treeheading.image', {'side': 'right', 'sticky': ''}),
                            ('Treeheading.text', {'sticky': 'we'})]})]})])

        style.configure("Treeview.Heading",
                        font=("Times New Roman", 10, "bold"),
                        background="#9fd7f9",
                        foreground="#000",
                        relief="flat",
                        borderwidth=0,
                        padding=5)

        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white")

        style.map("Treeview",
                background=[("selected", "#e5e5e5")],
                foreground=[("selected", "black")])

        columns = ("STT", "Mã NV", "Nhân Viên", "Chức Vụ", "Phòng Ban", "Email", "Số Điện Thoại", "Ngày Tuyển Dụng", "Trạng Thái")
        self.tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)

        self.tree.heading("STT", text="STT")
        self.tree.heading("Mã NV", text="Mã NV")
        self.tree.heading("Nhân Viên", text="Nhân Viên")
        self.tree.heading("Chức Vụ", text="Chức Vụ")
        self.tree.heading("Phòng Ban", text="Phòng Ban")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Số Điện Thoại", text="Số Điện Thoại")
        self.tree.heading("Ngày Tuyển Dụng", text="Ngày Tuyển Dụng")
        self.tree.heading("Trạng Thái", text="Trạng Thái")

        self.tree.column("STT", width=50, anchor="center")
        self.tree.column("Mã NV", width=70, anchor="center")
        self.tree.column("Nhân Viên", width=150, anchor="w")
        self.tree.column("Chức Vụ", width=100, anchor="w")
        self.tree.column("Phòng Ban", width=100, anchor="w")
        self.tree.column("Email", width=150, anchor="center")
        self.tree.column("Số Điện Thoại", width=100, anchor="center")
        self.tree.column("Ngày Tuyển Dụng", width=100, anchor="center")
        self.tree.column("Trạng Thái", width=80, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_employee_data()

    def filter_employee_list(self):
        # Xóa dữ liệu hiện tại trong treeview
        self.tree.delete(*self.tree.get_children())
        
        # Lấy giá trị từ các bộ lọc
        position_filter = self.position_var.get()
        dept_filter = self.department_var.get()
        status_filter = self.status_var.get()
        search_query = self.search_var.get().strip().lower() 

        # Lọc dữ liệu từ dữ liệu gốc
        filtered_data = []
        for employee in self.original_employee_data:
            emp_position = employee['position'] if employee['position'] else "N/A"
            emp_department = employee['dep_name'] if employee['dep_name'] else "N/A"
            emp_status = employee['status'] if employee['status'] else "N/A"
            emp_id = str(employee['emp_id']) if employee['emp_id'] is not None else "N/A"  # Convert to string
            full_name = f"{employee['last_name']} {employee['first_name']}".lower()
            email = employee['email'].lower() if employee['email'] else "N/A"
            phone = employee['phone_number'] if employee['phone_number'] else "N/A"
            
            # Bộ lọc theo combobox chức vụ, phòng ban, trạng thái
            match_filters = (
                (position_filter == "Tất cả" or emp_position == position_filter) and
                (dept_filter == "Tất cả" or emp_department == dept_filter) and
                (status_filter == "Tất cả" or emp_status == status_filter)
            )
            
            # Kiểm tra từ khóa tìm kiếm (nếu có)
            match_search = True
            if search_query and search_query != "tìm kiếm...":  
                match_search = (
                    search_query in emp_id.lower() or  # Now safe to use .lower()
                    search_query in full_name or
                    search_query in email or
                    search_query in phone
                )

            # Nếu thỏa mãn cả bộ lọc và tìm kiếm, thêm vào kết quả
            if match_filters and match_search:
                filtered_data.append(employee)
        
        # Kiểm tra nếu không có kết quả nào
        if not filtered_data:
            messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu nào phù hợp!")
        
        # Cập nhật treeview với dữ liệu đã lọc
        for idx, emp in enumerate(filtered_data, 1):
            full_name = f"{emp['last_name']} {emp['first_name']}"
            position = emp['position'] if emp['position'] else "N/A"
            department = emp['dep_name'] if emp['dep_name'] else "N/A"
            email = emp['email'] if emp['email'] else "N/A"
            phone = emp['phone_number'] if emp['phone_number'] else "N/A"
            hired_date = emp['hired_date'].strftime("%Y-%m-%d") if emp['hired_date'] else "N/A"
            status = emp['status'] if emp['status'] else "N/A"
            
            self.tree.insert("", "end", values=(
                idx,
                emp['emp_id'],
                full_name,
                position,
                department,
                email,
                phone,
                hired_date,
                status
            ), tags=(status,))
        
        # Cấu hình lại tag sau khi lọc
        self.tree.tag_configure("Đang làm việc", background="#fafcfc")
        self.tree.tag_configure("Nghỉ làm việc", background="#f7f5f5")
        self.tree.tag_configure("N/A", background="#f7fafa")

    # Load danh sách nhân viên từ DB
    def load_employee_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.conn.is_connected():
            self.conn.reconnect()
        rows = DB.get_all_employees(self.cursor)
        if isinstance(rows, dict) and "error" in rows:
            messagebox.showerror("Lỗi", rows["error"])
            return
        
        self.original_employee_data = rows
        
        for idx, row in enumerate(rows, 1):
            emp_id = row['emp_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            position = row['position'] if row['position'] else "N/A"
            department = row['dep_name'] if row['dep_name'] else "N/A"
            email = row['email'] if row['email'] else "N/A"
            phone = row['phone_number'] if row['phone_number'] else "N/A"
            hired_date = row['hired_date'].strftime("%Y-%m-%d") if row['hired_date'] else "N/A"
            status = row['status'] if row['status'] else "N/A"

            self.tree.insert("", "end", values=(idx, emp_id, full_name, position, department, email, phone, hired_date, status), tags=(status,))
            self.tree.tag_configure("Đang làm việc", background="#fafcfc") 
            self.tree.tag_configure("Đã nghỉ", background="#faf5f5") 
            self.tree.tag_configure("N/A", background="#f7fafa")      

        if not rows:
            messagebox.showinfo("Thông báo", "Không có dữ liệu nhân viên!")
            print("Không có dữ liệu nhân viên")

    # Thêm
    def add_employee(self):
        form = tk.Toplevel(self.root)
        form.title("Thêm Nhân Viên")
        self.center_window(form, 550, 560)
        form.configure(bg="#ffffff")

        heading = tk.Label(form, text="Nhập Thông Tin Nhân Viên",
                           font=("Times New Roman", 16, "bold"),
                           bg="#ffffff", fg="#14a0f7")
        heading.pack(pady=15)

        container = tk.Frame(form, bg="#ffffff")
        container.pack(padx=30, pady=20)

        style = ttk.Style()
        style.configure("Custom.TEntry",
                        font=("Times New Roman", 11),
                        padding=6,
                        relief="solid",
                        borderwidth=1)
        style.configure("Error.TEntry",
                        font=("Times New Roman", 11),
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        foreground="red")

        fields = ["Nhân Viên", "Chức Vụ", "Phòng Ban", "Email", "Số Điện Thoại", "Ngày Tuyển Dụng"]
        self.entries = {}
        self.error_label = None
        self.email_entry = None
        self.email_row_index = None
        self.phone_error_label = None
        self.empty_error_labels = []

        for i, field in enumerate(fields):
            label = tk.Label(container, 
                             text=field + ":", 
                             font=("Times New Roman", 11), 
                             bg="#ffffff",
                             justify="left")
            label.grid(row=i, column=0, sticky="w", padx=(0, 15), pady=17)

            if field in ["Phòng Ban", "Chức Vụ"]:
                style.configure("Custom.TCombobox",
                                padding=6,
                                relief="solid",
                                borderwidth=1,
                                font=("Times New Roman", 11),
                                foreground="black",
                                fieldbackground="white",
                                background="white")

                style.map("Custom.TCombobox",
                          fieldbackground=[("readonly", "white")],
                          background=[("readonly", "white")],
                          foreground=[("readonly", "black")])

                values = []
                default = ""
                if field == "Phòng Ban":
                    values = ["Employee", "IT Department", "Manager Department"]
                    default = "Chọn phòng ban"
                elif field == "Chức Vụ":
                    values = ["Employee", "Developer", "Manager"]
                    default = "Chọn chức vụ"

                entry = ttk.Combobox(container,
                                     values=values,
                                     font=("Times New Roman", 11),
                                     state="readonly",
                                     width=29,
                                     style="Custom.TCombobox")
                entry.set(default)
            elif field == "Ngày Tuyển Dụng":
                style.configure("Custom.DateEntry",
                                padding=6,
                                relief="solid",
                                borderwidth=1,
                                font=("Times New Roman", 11),
                                foreground="black",
                                fieldbackground="white",
                                background="white")

                style.map("Custom.DateEntry",
                          fieldbackground=[("readonly", "white")],
                          background=[("readonly", "white")],
                          foreground=[("readonly", "black")])

                entry = DateEntry(container,
                                  font=("Times New Roman", 11),
                                  state="readonly",
                                  date_pattern="yyyy-mm-dd",
                                  width=29,
                                  justify="left",
                                  background="white",
                                  foreground="black",
                                  borderwidth=1,
                                  relief="solid",
                                  style="Custom.DateEntry")
            else:
                entry = ttk.Entry(container, width=36, style="Custom.TEntry")
                # Gắn sự kiện cho Email và Số Điện Thoại
                if field == "Email":
                    entry.bind("<FocusOut>", lambda event: self.validate_and_reset_email())
                    entry.bind("<KeyRelease>", lambda event: self.validate_and_reset_email())
                elif field == "Số Điện Thoại":
                    entry.bind("<FocusOut>", lambda event: self.validate_and_reset_phone())
                    entry.bind("<KeyRelease>", lambda event: self.validate_and_reset_phone())

            entry.grid(row=i, column=1, pady=12, sticky="w")
            self.entries[field] = entry

        save_btn = tk.Button(container, text="Lưu",
                             font=("Times New Roman", 11, "bold"),
                             bg="#4CAF50", fg="white",
                             activebackground="#45a049",
                             padx=25, pady=10,
                             command=self.save_employee,
                             relief="flat", borderwidth=0)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
        save_btn.configure(width=20)

    # Lưu nv mới thêm
    def save_employee(self):
        email = self.entries["Email"].get()
        phone = self.entries["Số Điện Thoại"].get()

        # Reset lỗi cũ nếu có
        if self.error_label:
            self.error_label.place_forget()
            self.entries["Email"].configure(style="Custom.TEntry")

        if hasattr(self, 'phone_error_label') and self.phone_error_label:
            self.phone_error_label.place_forget()
            self.entries["Số Điện Thoại"].configure(style="Custom.TEntry")

        if hasattr(self, 'empty_error_labels'):
            for lbl in self.empty_error_labels:
                lbl.place_forget()
        self.empty_error_labels = []

        has_error = False

        for key, entry in self.entries.items():
            value = entry.get().strip()

            # Kiểm tra trống
            if not value:
                lbl = tk.Label(entry.master, 
                               text="Không được để trống", 
                               fg="red",
                                font=("Times New Roman", 9), 
                                bg="#ffffff")
                lbl.place(x=entry.winfo_x() + 4,
                        y=entry.winfo_y() + entry.winfo_height() + 2)
                self.empty_error_labels.append(lbl)
                has_error = True
                continue 

            # Ktra định dạng email nếu không trống
            if key == "Email" and not self.is_valid_email(value):
                self.show_email_error("Email không hợp lệ!")
                has_error = True

            # Ktra định dạng sdt nếu không trống
            if key == "Số Điện Thoại" and not self.is_valid_phone(value):
                self.show_phone_error("Số điện thoại không hợp lệ!")
                has_error = True

        # Ktra định dạng ngày tuyển dụng
        hire_date_str = self.entries["Ngày Tuyển Dụng"].get().strip()
        # yyyy-mm-dd
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, hire_date_str):
            lbl = tk.Label(self.entries["Ngày Tuyển Dụng"].master,
                        text="Ngày không hợp lệ (yyyy-mm-dd)", fg="red",
                        font=("Times New Roman", 9), bg="#ffffff")
            lbl.place(x=self.entries["Ngày Tuyển Dụng"].winfo_x() + 4,
                    y=self.entries["Ngày Tuyển Dụng"].winfo_y() + self.entries["Ngày Tuyển Dụng"].winfo_height() + 2)
            self.empty_error_labels.append(lbl)
            has_error = True
        else:
            hired_date = hire_date_str
        if has_error:
            return

        # Nếu hợp lệ thì lưu vào db
        data = {key: entry.get().strip() for key, entry in self.entries.items()}

        # Tách tên thành first_name và last_name
        full_name = data.get("Nhân Viên", "").strip()
        name_parts = full_name.split()

        if len(name_parts) >= 2:
            first_name = name_parts[-1] 
            last_name = " ".join(name_parts[:-1])
        else:
            first_name = full_name 
            last_name = ""

        # Lấy dep_id từ dep_name
        dep_name = data.get("Phòng Ban", "")

        if not self.conn.is_connected():
            self.conn.reconnect()
        dep_id_result = DB.get_dep_id_by_name(self.cursor, dep_name)
        if isinstance(dep_id_result, dict) and "error" in dep_id_result:
            messagebox.showerror("Lỗi", dep_id_result["error"])
            return
        if not dep_id_result:
            messagebox.showerror("Lỗi", f"Phòng ban '{dep_name}' không tồn tại!")
            return
        dep_id = dep_id_result['dep_id']

        result = DB.add_employee(self.cursor, self.conn, last_name, first_name, dep_id, data["Email"], data["Số Điện Thoại"], data["Ngày Tuyển Dụng"], data["Chức Vụ"])
        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Lỗi", f"Thêm thất bại: {result['error']}")
        else:
            messagebox.showinfo("Thành công", "Đã thêm nhân viên!")
            self.entries["Nhân Viên"].master.master.destroy()
            self.load_employee_data()
    
    # Hàm xử lý email
    def validate_and_reset_email(self):
        email = self.entries["Email"].get().strip()
        if self.error_label: 
            if self.is_valid_email(email): 
                self.error_label.place_forget()
                self.error_label = None
                self.entries["Email"].configure(style="Custom.TEntry")  
    
    # Hàm xử lý sđt
    def validate_and_reset_phone(self):
        phone = self.entries["Số Điện Thoại"].get().strip()
        if hasattr(self, 'phone_error_label') and self.phone_error_label:  
            if self.is_valid_phone(phone):  
                self.phone_error_label.place_forget()
                self.phone_error_label = None
                self.entries["Số Điện Thoại"].configure(style="Custom.TEntry")  

    # Định dạng email
    def is_valid_email(self, email):
        import re
        
        # Kiểm tra nếu email là None hoặc chuỗi rỗng
        if not email or not isinstance(email, str):
            return False

        email_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,4}$'
        
        # Kiểm tra độ dài tối đa (> 254 ký tự)
        if len(email) > 254:
            return False
            
        # Kiểm tra định dạng bằng regex
        if not re.match(email_pattern, email):
            return False
            
        # Không có khoảng trắng
        if " " in email:
            return False
            
        # Không có hai dấu chấm liên tiếp
        if ".." in email:
            return False
            
        # Phải có ít nhất một ký tự trước @
        at_index = email.index('@')
        if at_index == 0:
            return False
            
        # Phải có dấu chấm sau @
        domain_part = email[at_index + 1:]
        if '.' not in domain_part:
            return False
            
        return True
    
    # Nếu lỗi email
    def show_email_error(self, message):
        if self.error_label:
            self.error_label.place_forget() 

        style = ttk.Style()
        style.configure("Error.TEntry",
                        font=("Times New Roman", 11),
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        foreground="black",
                        fieldbackground="white",
                        bordercolor="red")

        # Dùng self.entries["Email"] thay vì self.email_entry
        self.entries["Email"].configure(style="Error.TEntry")

        self.error_label = tk.Label(self.entries["Email"].master, text=message,
                                    fg="red", font=("Times New Roman", 9), bg="#ffffff")
        self.error_label.place(x=self.entries["Email"].winfo_x() + 4,
                            y=self.entries["Email"].winfo_y() + self.entries["Email"].winfo_height() + 2)

    # Phone
    def is_valid_phone(self, phone):
        import re
        
        # Nếu phone là None hoặc không phải chuỗi
        if not phone or not isinstance(phone, str):
            return False
        
        # Loại bỏ khoảng trắng, dấu gạch ngang, dấu ngoặc để xử lý
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)

        # Biểu thức chính quy cho sđt
        pattern = r'^(\+84|0)([1-9])\d{8,9}$'
        
        # Độ dài cơ bản
        if len(cleaned_phone) < 10 or len(cleaned_phone) > 13: 
            return False
        
        # Chỉ chứa số và ký tự hợp lệ (+ ở đầu nếu có)
        if not all(c.isdigit() or (c == '+' and i == 0) for i, c in enumerate(cleaned_phone)):
            return False
        
        # Định dạng bằng regex
        if not re.match(pattern, cleaned_phone):
            return False
        
        # Số đầu tiên sau mã quốc gia hoặc 0 không phải là 0
        if cleaned_phone.startswith('+84'):
            if cleaned_phone[3] == '0':
                return False
        elif cleaned_phone.startswith('0'):
            if len(cleaned_phone) == 10:  # số 10 chữ số phải bắt đầu bằng 09, 08, 07, etc.
                if cleaned_phone[1] == '0':
                    return False
        
        return True

    # Nếu lỗi sđt
    def show_phone_error(self, message):
        if hasattr(self, 'phone_error_label') and self.phone_error_label:
            self.phone_error_label.grid_forget()

        style = ttk.Style()
        style.configure("ErrorPhone.TEntry",
                        font=("Times New Roman", 11),
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        foreground="black",
                        fieldbackground="white",
                        bordercolor="red")

        phone_entry = self.entries["Số Điện Thoại"]
        phone_entry.configure(style="ErrorPhone.TEntry")
        self.phone_error_label = tk.Label(phone_entry.master, text=message,
                                        fg="red", font=("Times New Roman", 9), bg="#ffffff")
        self.phone_error_label.place(x=phone_entry.winfo_x() + 4,
                                    y=phone_entry.winfo_y() + phone_entry.winfo_height() + 2)

    # Căn chỉnh giữa màn hình
    def center_window(self, win, width, height):
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    # Sửa
    def edit_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên để sửa")
            print("Vui lòng chọn một nhân viên để sửa")
            return
        
        # Lấy emp_id từ Treeview
        emp_id = self.tree.item(selected_item)['values'][1] 
        if not emp_id:
            messagebox.showerror("Lỗi", "Không thể lấy ID nhân viên.")
            print("Không thể lấy ID nhân viên.")
            return

        if not self.conn.is_connected():
            self.conn.reconnect()
        employee_data = DB.get_employee_by_id(self.cursor, emp_id)
        if isinstance(employee_data, dict) and "error" in employee_data:
            messagebox.showerror("Lỗi", employee_data["error"])
            return
        if not employee_data:
            messagebox.showerror("Lỗi", "Không thể lấy dữ liệu nhân viên từ database.")
            return
        
        # Dữ liệu lấy từ db
        last_name = employee_data['last_name']
        first_name = employee_data['first_name']
        position = employee_data['position']
        dep_name = employee_data['dep_name']
        email = employee_data['email']
        phone_number = employee_data['phone_number']
        hired_date = employee_data['hired_date']
        status = employee_data['status']

        full_name = f"{last_name} {first_name}".strip()
        if isinstance(hired_date, (datetime.date, datetime.datetime)):
            hired_date_str = hired_date.strftime("%Y-%m-%d")
        else:
            hired_date_str = hired_date if hired_date else ""
        status_display = "Đang làm việc" if status == "Đang làm việc" else "Đã nghỉ"
        phone_number = str(phone_number) if phone_number else ""

        item_data = [full_name, position, dep_name, email, phone_number, hired_date_str, status_display]

        # Tạo form sửa
        form = tk.Toplevel(self.root)
        form.title("Sửa Thông Tin Nhân Viên")
        self.center_window(form, 550, 600)
        form.configure(bg="#ffffff")

        heading = tk.Label(form, text="Sửa Thông Tin Nhân Viên",
                        font=("Times New Roman", 16, "bold"),
                        bg="#ffffff", fg="#f79c14")
        heading.pack(pady=15)

        container = tk.Frame(form, bg="#ffffff")
        container.pack(padx=30, pady=20)

        # Tạo style
        style = ttk.Style()
        style.configure("Custom.TEntry",
                        font=("Times New Roman", 11),
                        padding=6,
                        relief="solid",
                        borderwidth=1)
        style.configure("Custom.TCombobox",
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        font=("Times New Roman", 11),
                        foreground="black",
                        fieldbackground="white",
                        background="white")
        style.map("Custom.TCombobox",
                fieldbackground=[("readonly", "white")],
                background=[("readonly", "white")],
                foreground=[("readonly", "black")])
        style.configure("Custom.DateEntry",
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        font=("Times New Roman", 11),
                        foreground="black",
                        fieldbackground="white",
                        background="white")
        style.map("Custom.DateEntry",
                fieldbackground=[("readonly", "white")],
                background=[("readonly", "white")],
                foreground=[("readonly", "black")])

        # Các trường thông tin
        fields = ["Nhân Viên", "Chức Vụ", "Phòng Ban", "Email", "Số Điện Thoại", "Ngày Tuyển Dụng", "Trạng Thái"]
        self.edit_entries = {}

        for i, field in enumerate(fields):
            label = tk.Label(container, text=field + ":", font=("Times New Roman", 11), bg="#ffffff", justify="left")
            label.grid(row=i, column=0, sticky="w", padx=(0, 15), pady=12)

            if field == "Phòng Ban":
                values = ["Employee", "IT Department", "Manager Department"]
                entry = ttk.Combobox(container, values=values, state="readonly", style="Custom.TCombobox", width=29)
            elif field == "Chức Vụ":
                values = ["Employee", "Developer", "Manager"]
                entry = ttk.Combobox(container, values=values, state="readonly", style="Custom.TCombobox", width=29)
            elif field == "Trạng Thái":
                values = ["Đang làm việc", "Đã nghỉ"]
                entry = ttk.Combobox(container, values=values, state="readonly", style="Custom.TCombobox", width=29)
            elif field == "Ngày Tuyển Dụng":
                entry = DateEntry(container, font=("Times New Roman", 11), state="readonly",
                                date_pattern="yyyy-mm-dd", width=25, justify="left",
                                background="white", foreground="black", borderwidth=1,
                                relief="solid", style="Custom.DateEntry")
            else:
                entry = ttk.Entry(container, width=31, style="Custom.TEntry")

            entry.grid(row=i, column=1, pady=8, sticky="w")
            self.edit_entries[field] = entry

        # Gán dữ liệu
        for i, field in enumerate(fields):
            if i < len(item_data):
                value = item_data[i]
                widget = self.edit_entries[field]

                if isinstance(widget, ttk.Combobox):
                    widget.set(str(value) if value else "")
                elif isinstance(widget, DateEntry):
                    try:
                        widget.set_date(value)
                    except:
                        widget.set_date(datetime.today()) 
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value) if value else "")

        # Nút cập nhật
        save_btn = tk.Button(container, text="Cập Nhật",
                            font=("Times New Roman", 11, "bold"),
                            bg="#4CAF50", fg="white",
                            activebackground="#45a049",
                            padx=25, pady=10,
                            command=lambda: self.save_edited_employee(emp_id, form),
                            relief="flat", borderwidth=0)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
        save_btn.configure(width=20)

    def save_edited_employee(self, emp_id, form):
        self.entries = self.edit_entries 
        data = {key: entry.get().strip() for key, entry in self.edit_entries.items()}
        email = data.get("Email", "")
        phone = data.get("Số Điện Thoại", "")
        if phone and not phone.startswith("0"):
            phone = "0" + phone

        hire_date_str = data.get("Ngày Tuyển Dụng", "")
            
        has_error = False

        # Clear lỗi cũ
        if hasattr(self, 'empty_error_labels'):  # Kiểm tra xem empty_error_labels đã được khởi tạo chưa
            for lbl in self.empty_error_labels:
                if lbl.winfo_exists():  # Chỉ ẩn nếu nhãn còn tồn tại
                    lbl.place_forget()
        self.empty_error_labels = []  # Đặt lại danh sách sau khi clear

        # Validate các trường
        for key, value in data.items():
            entry = self.edit_entries[key]
            if not value:
                lbl = tk.Label(entry.master, 
                            text="Không được để trống", 
                            fg="red",
                            font=("Times New Roman", 9), 
                            bg="#ffffff")
                lbl.place(x=entry.winfo_x() + 4, y=entry.winfo_y() + entry.winfo_height() + 2)
                self.empty_error_labels.append(lbl)
                has_error = True
                continue

            if key == "Email" and not self.is_valid_email(value):
                self.show_email_error("Email không hợp lệ!")
                has_error = True

            if key == "Số Điện Thoại" and not re.match(r"^0\d{9}$", value):
                self.show_phone_error("Số điện thoại không hợp lệ!")
                has_error = True

        # Validate ngày tuyển dụng
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, hire_date_str):
            entry = self.edit_entries["Ngày Tuyển Dụng"]
            lbl = tk.Label(entry.master, 
                        text="Ngày không hợp lệ!", 
                        fg="red",
                        font=("Times New Roman", 9), 
                        bg="#ffffff")
            lbl.place(x=entry.winfo_x() + 4, y=entry.winfo_y() + entry.winfo_height() + 2)
            self.empty_error_labels.append(lbl)
            has_error = True

        if has_error:
            return

        # Tách họ tên
        full_name = data.get("Nhân Viên", "").strip()
        name_parts = full_name.split()
        first_name = name_parts[-1] if name_parts else "" 
        last_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else ""  

        # Lấy dep_id từ tên phòng ban
        dep_name = data.get("Phòng Ban", "")
        
        if not self.conn.is_connected():
            self.conn.reconnect()
        dep_id_result = DB.get_dep_id_by_name(self.cursor, dep_name)
        if isinstance(dep_id_result, dict) and "error" in dep_id_result:
            messagebox.showerror("Lỗi", dep_id_result["error"])
            return
        if not dep_id_result:
            messagebox.showerror("Lỗi", f"Phòng ban '{dep_name}' không tồn tại!")
            print(f"Phòng ban '{dep_name}' không tồn tại!")
            return
        dep_id = dep_id_result['dep_id']

        result = DB.update_employee(self.cursor, 
                                    self.conn, 
                                    emp_id, 
                                    last_name, 
                                    first_name, 
                                    dep_id, 
                                    email, 
                                    phone, 
                                    hire_date_str, 
                                    data["Chức Vụ"], 
                                    data["Trạng Thái"])
        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Lỗi", f"Cập nhật thất bại: {result['error']}")
            print("Cập nhật thất bại:", result["error"])
        else:
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhân viên.")
            print("Đã cập nhật thông tin nhân viên thành công.")
            form.destroy()
            self.empty_error_labels = []  # Đặt lại danh sách sau khi đóng form
            self.load_employee_data()

    # Xóa
    def delete_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên để xóa.")
            print("Vui long chọn một nhân viên để xóa")
            return

        employee_data = self.tree.item(selected_item)['values']
        if not employee_data:
            messagebox.showerror("Lỗi", "Không thể lấy dữ liệu nhân viên.")
            print("Không thể lấy dữ liệu nhân viên.")
            return

        employee_name = employee_data[2]
        emp_id = employee_data[1]

        form = tk.Toplevel(self.root)
        form.title("Xác Nhận Xóa")
        form.configure(bg="white")
        self.center_window(form, 400,200)
        form.grab_set() 

        label = tk.Label(form, 
                        text=f"Bạn có chắc muốn xóa\nnhân viên \"{employee_name}\"?",
                        font=("Times New Roman", 12, "bold"),
                        fg="#333333", 
                        bg="#fff", 
                        justify="center")
        label.pack(pady=30)

        btn_frame = tk.Frame(form, bg="#fff")
        btn_frame.pack(pady=10)

        def confirm_delete():
            if not self.conn.is_connected():
                self.conn.reconnect()
            result = DB.delete_employee(self.cursor, self.conn, emp_id)
            if isinstance(result, dict) and "error" in result:
                messagebox.showerror("Lỗi", f"Không thể xóa nhân viên: {result['error']}")
                print("Không thể xóa nhân viên:", result["error"])
            else:
                self.tree.delete(selected_item)
                form.destroy()
                messagebox.showinfo("Thành công", f"Đã xóa nhân viên: {employee_name}")
                print(f"Đã xóa nhân viên: {employee_name}")
                self.load_employee_data()

        def cancel():
            form.destroy()

        # Nút Xóa
        delete_btn = tk.Button(btn_frame, 
                            text="Xóa", 
                            command=confirm_delete,
                            font=("Times New Roman", 11, "bold"),
                            bg="#f5021b", 
                            fg="white", 
                            padx=20, 
                            pady=8,
                            activebackground="#c0392b", 
                            relief="flat")
        delete_btn.grid(row=0, column=0, padx=15)

        # Nút Hủy
        cancel_btn = tk.Button(btn_frame, 
                            text="Hủy", 
                            command=cancel,
                            font=("Times New Roman", 11, "bold"),
                            bg="#696667", 
                            fg="white", 
                            padx=20, 
                            pady=8,
                            activebackground="#95a5a6", 
                            relief="flat")
        cancel_btn.grid(row=0, column=1, padx=15)

    # Tìm kiếm
    def search_employee(self, event=None):
        self.filter_employee(event)
    
    def _clear_placeholder(self, event=None): 
        if self.search_entry.get() == "Tìm kiếm...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def _restore_placeholder(self, event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Tìm kiếm...")
            self.search_entry.config(fg="gray")
    
    # Reset
    def reset_employee_list(self):
        self.search_var.set("")
        self.search_entry.config(fg="gray")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm...") 
        # Reset các ô lọc Combobox
        self.position_var.set("Tất cả")
        self.department_var.set("Tất cả")
        self.status_var.set("Tất cả")
        # Load lại toàn bộ dữ liệu
        self.load_employee_data()

    def filter_employee(self, event=None):
        search_term = self.search_var.get().strip().lower()
        if search_term == "tìm kiếm...":
            search_term = ""

        # Lấy các bộ lọc khác
        position_filter = getattr(self, 'position_var', tk.StringVar(value="Tất cả")).get()
        dep_filter = getattr(self, 'dep_var', tk.StringVar(value="Tất cả")).get()
        year_filter = getattr(self, 'year_var', tk.StringVar(value="Tất cả")).get()
        month_filter = getattr(self, 'month_var', tk.StringVar(value="Tất cả")).get()
        day_filter = getattr(self, 'day_var', tk.StringVar(value="")).get()

        # Xử lý ngày tháng
        date_filter = None
        if day_filter:
            try:
                if len(day_filter) == 4: # Chỉ năm
                    date_filter = f"{day_filter}-01-01"
                    datetime.strptime(date_filter, "%Y-%m-%d")
                elif len(day_filter) == 7: # Năm-tháng
                    date_filter = f"{day_filter}-01"
                    datetime.strptime(date_filter, "%Y-%m-%d")
                elif len(day_filter) >= 10: # Đầy đủ ngày
                    date_filter = day_filter
                    datetime.strptime(date_filter, "%Y-%m-%d")
            except ValueError:
                date_filter = None

        # Xóa dữ liệu cũ trong tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.conn.is_connected():
            self.conn.reconnect()
        rows = DB.filter_employees(self.cursor, search_term, position_filter, dep_filter, year_filter, month_filter, date_filter)
        if isinstance(rows, dict) and "error" in rows:
            messagebox.showerror("Lỗi", rows["error"])
            return

        for idx, row in enumerate(rows, 1):
            emp_id = row['emp_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            position = row['position'] if row['position'] else "N/A"
            department = row['dep_name'] if row['dep_name'] else "N/A"
            email = row['email'] if row['email'] else "N/A"
            phone = row['phone_number'] if row['phone_number'] else "N/A"
            hired_date = row['hired_date'].strftime("%Y-%m-%d") if row['hired_date'] else "N/A"
            status = row['status'] if row['status'] else "N/A"
            self.tree.insert("", "end", values=(idx, emp_id, 
                                                full_name, position, 
                                                department, email, 
                                                phone, hired_date, 
                                                status))

        if not rows:
            messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu phù hợp!")
            print("Không tìm thấy dữ liệu phù hợp!")

    # Hiển thị bảng chấm công
    def show_attendance(self):
        # Hủy nội dung cũ nếu có
        if hasattr(self, 'current_content') and self.current_content is not None:
            self.current_content.destroy()

        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        # Cấu hình style cho Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"))

        # Load các icon
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")
        reset_img = Image.open(os.path.join(img_dir, "reset.png")).resize((22, 22), Image.Resampling.LANCZOS)
        search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22), Image.Resampling.LANCZOS)
        excel_img = Image.open(os.path.join(img_dir, "excel.png")).resize((22, 22), Image.Resampling.LANCZOS)
        self.reset_icon = ImageTk.PhotoImage(reset_img)
        self.search_icon = ImageTk.PhotoImage(search_img)
        self.excel_icon = ImageTk.PhotoImage(excel_img)

        # Frame chính chứa các thành phần phía trên
        top_frame = tk.Frame(self.current_content, bg=self.bg_color)
        top_frame.pack(fill=tk.X, pady=5)

        # Frame con để căn giữa
        inner_frame = tk.Frame(top_frame, bg=self.bg_color)
        inner_frame.pack(anchor="center")

        # Frame chứa các bộ lọc (Năm, Tháng, Ngày)
        filter_frame = tk.Frame(inner_frame, bg=self.bg_color)
        filter_frame.pack(side=tk.LEFT, padx=5)

        # Bộ lọc Năm
        self.year_var = tk.StringVar(value="Tất cả")
        year_label = tk.Label(filter_frame, text="Năm:", bg=self.bg_color, font=("Times New Roman", 9))
        year_label.pack(side=tk.LEFT)
        years = ["Tất cả"] + sorted(set(
            emp['hired_date'].strftime("%Y") 
            for emp in self.original_employee_data 
            if emp['hired_date'] is not None
        ), reverse=True)
        year_combo = ttk.Combobox(filter_frame, 
                                textvariable=self.year_var, 
                                width=10,  
                                font=("Times New Roman", 9),
                                style="Custom.TCombobox")
        year_combo['values'] = years
        year_combo.pack(side=tk.LEFT, padx=2)
        year_combo.bind("<<ComboboxSelected>>", lambda event: self.filter_attendance_list())

        # Bộ lọc Tháng
        self.month_var = tk.StringVar(value="Tất cả")
        month_label = tk.Label(filter_frame, text="Tháng:", bg=self.bg_color, font=("Times New Roman", 9))
        month_label.pack(side=tk.LEFT)
        month_combo = ttk.Combobox(filter_frame, 
                                textvariable=self.month_var, 
                                width=10, 
                                font=("Times New Roman", 9),
                                style="Custom.TCombobox")
        month_combo['values'] = ("Tất cả", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12")
        month_combo.pack(side=tk.LEFT, padx=2)
        month_combo.bind("<<ComboboxSelected>>", lambda event: self.filter_attendance_list())

        # Bộ lọc Ngày
        self.day_var = tk.StringVar(value="Tất cả")
        day_label = tk.Label(filter_frame, text="Ngày:", bg=self.bg_color, font=("Times New Roman", 9))
        day_label.pack(side=tk.LEFT)
        day_combo = ttk.Combobox(filter_frame,
                                textvariable=self.day_var,
                                width=10,
                                font=("Times New Roman", 9),
                                style="Custom.TCombobox")
        day_combo['values'] = ["Tất cả"] + [str(i) for i in range(1, 32)]
        day_combo.pack(side=tk.LEFT, padx=2)
        day_combo.bind("<<ComboboxSelected>>", lambda event: self.filter_attendance_list())

        # Frame chứa ô tìm kiếm và nút tìm kiếm
        search_frame = tk.Frame(inner_frame, 
                                bg="white", 
                                relief="flat", 
                                highlightthickness=1, 
                                highlightbackground="#4c84f5")
        search_frame.pack(side=tk.LEFT, padx=5, ipady=4)

        # Ô nhập tìm kiếm
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Times New Roman", 11),
            width=25,
            fg="gray",
            relief="flat",
            borderwidth=0,
            bg="white"
        )
        self.search_entry.insert(0, "Tìm kiếm...")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_placeholder)
        self.search_entry.bind("<Return>", lambda event: self.filter_attendance_list())
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Nút Tìm kiếm 
        search_button = tk.Button(
            search_frame,
            image=self.search_icon,
            command=self.filter_attendance_list,
            bg="white",
            bd=0,
            relief="flat",
            activebackground="#fff",
            width=20, 
            height=25,
        )
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

        # Frame chứa các nút Excel và Reset
        buttons_frame = tk.Frame(inner_frame, bg=self.bg_color)
        buttons_frame.pack(side=tk.LEFT, padx=5)

        # Nút Excel
        excel_button = tk.Button(buttons_frame, 
                                text="Excel", 
                                image=self.excel_icon, 
                                compound=tk.TOP,
                                command=lambda: src.salary.excel_utils.export_to_excel(self.attendance_tree, "Attendance"),
                                bg="#f7f8fa", 
                                bd=0, 
                                width=60, 
                                height=60,
                                font=("Times New Roman", 9), 
                                relief="flat",
                                activebackground="#65f06b")
        excel_button.pack(side=tk.LEFT, padx=3)

        # Nút Reset
        reset_button = tk.Button(buttons_frame,
                                text="Làm mới",
                                image=self.reset_icon, 
                                compound=tk.TOP,
                                command=self.reset, 
                                bg="#f7f8fa",
                                bd=0,
                                width=60,
                                height=60,
                                font=("Times New Roman", 9),
                                relief="flat",
                                activebackground="#7d8e96")
        reset_button.pack(side=tk.LEFT, padx=3)

        # Tạo Treeview
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

        # Gọi hàm load dữ liệu ban đầu
        self.load_attendance_data()

    def load_attendance_data(self):
        if not hasattr(self, 'attendance_tree') or not self.attendance_tree.winfo_exists():
            return

        # Xóa dữ liệu cũ trong Treeview
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        # Lấy dữ liệu từ DB
        rows = DB.get_all_attendance(self.cursor)
        if isinstance(rows, dict) and "error" in rows:
            messagebox.showerror("Lỗi", rows["error"])
            return

        # Khởi tạo biến has_data với giá trị mặc định là False
        has_data = False

        # Xử lý và hiển thị dữ liệu
        for idx, row in enumerate(rows, 1):
            # Bỏ qua các bản ghi có date là None (tức là "N/A")
            if row['date'] is None:
                continue

            emp_id = row['emp_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            date = row['date'].strftime("%Y-%m-%d") if row['date'] else "N/A"
            check_in = row['check_in'].strftime("%H:%M") if row['check_in'] else "N/A"
            check_out = row['check_out'].strftime("%H:%M") if row['check_out'] else "N/A"

            # Tính toán work_hours và overtime_hours
            work_hours = 0.0
            overtime_hours = 0.0
            if row['check_in'] and row['check_out']:
                total_minutes = (row['check_out'] - row['check_in']).total_seconds() / 60.0
                total_hours = total_minutes / 60.0
                standard_hours = 8.0
                if total_hours > standard_hours:
                    work_hours = standard_hours
                    overtime_hours = total_hours - standard_hours
                else:
                    work_hours = total_hours
                    overtime_hours = 0.0

            # Định dạng giá trị
            work_hours = f"{work_hours:.2f}"
            overtime_hours = f"{overtime_hours:.2f}"

            # Chèn dữ liệu vào Treeview
            self.attendance_tree.insert("", "end", values=(idx, emp_id, full_name, date, check_in, check_out, work_hours, overtime_hours))
            has_data = True

        # Nếu không có dữ liệu nào được hiển thị, hiện thông báo
        if not has_data:
            messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu chấm công.")

    # Tìm kiếm
    def search(self, event=None):
        keyword = self.search_var.get().strip().lower()

        # Xóa dữ liệu cũ trên bảng
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        # Lấy dữ liệu từ DB
        rows = DB.get_all_attendance(self.cursor)
        if isinstance(rows, dict) and "error" in rows:
            messagebox.showerror("Lỗi", rows["error"])
            return

        # Xử lý và lọc dữ liệu
        index = 1
        for row in rows:
            emp_id = row['emp_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            date = row['date'].strftime("%Y-%m-%d") if row['date'] else "N/A"
            check_in = row['check_in'].strftime("%H:%M") if row['check_in'] else "N/A"
            check_out = row['check_out'].strftime("%H:%M") if row['check_out'] else "N/A"

            # Tính toán work_hours và overtime_hours
            work_hours = 0.0
            overtime_hours = 0.0
            if row['check_in'] and row['check_out']:
                # Tính tổng số giờ làm việc (tính bằng giờ)
                total_minutes = (row['check_out'] - row['check_in']).total_seconds() / 60.0
                total_hours = total_minutes / 60.0
                # Giờ làm chuẩn là 8 giờ/ngày
                standard_hours = 8.0
                if total_hours > standard_hours:
                    work_hours = standard_hours
                    overtime_hours = total_hours - standard_hours
                else:
                    work_hours = total_hours
                    overtime_hours = 0.0

            # Định dạng giá trị
            work_hours = f"{work_hours:.2f}"
            overtime_hours = f"{overtime_hours:.2f}"

            # So khớp từ khóa với tên, mã nhân viên, ngày hoặc giờ
            if (keyword in str(emp_id).lower() or 
                keyword in full_name.lower() or
                keyword in date.lower() or
                keyword in check_in.lower() or
                keyword in check_out.lower()):
                self.attendance_tree.insert(
                    "", "end",
                    values=(index, emp_id, full_name, date, check_in, check_out, work_hours, overtime_hours)
                )
                index += 1

    # Reset
    def reset(self):
        self.search_var.set("")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm...")
        # Reset các ô lọc Combobox
        self.year_var.set("Tất cả")
        self.month_var.set("Tất cả")
        self.day_var.set("Tất cả")
        self.load_attendance_data()

    def filter_attendance_list(self):
        if not hasattr(self, 'attendance_tree') or not self.attendance_tree.winfo_exists():
            return

        # Xóa dữ liệu cũ trong Treeview
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        # Lấy dữ liệu từ DB
        rows = DB.get_all_attendance(self.cursor)
        if isinstance(rows, dict) and "error" in rows:
            messagebox.showerror("Lỗi", rows["error"])
            return

        # Lấy giá trị bộ lọc
        year = self.year_var.get()
        month = self.month_var.get()
        day = self.day_var.get()
        keyword = self.search_var.get().strip().lower()

        # Khởi tạo biến has_data với giá trị mặc định là False
        has_data = False

        # Xử lý và lọc dữ liệu
        index = 1
        for row in rows:
            # Bỏ qua các bản ghi có date là None (tức là "N/A")
            if row['date'] is None:
                continue

            emp_id = row['emp_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            date = row['date'].strftime("%Y-%m-%d") if row['date'] else "N/A"
            check_in = row['check_in'].strftime("%H:%M") if row['check_in'] else "N/A"
            check_out = row['check_out'].strftime("%H:%M") if row['check_out'] else "N/A"

            # Tính toán work_hours và overtime_hours
            work_hours = 0.0
            overtime_hours = 0.0
            if row['check_in'] and row['check_out']:
                total_minutes = (row['check_out'] - row['check_in']).total_seconds() / 60.0
                total_hours = total_minutes / 60.0
                standard_hours = 8.0
                if total_hours > standard_hours:
                    work_hours = standard_hours
                    overtime_hours = total_hours - standard_hours
                else:
                    work_hours = total_hours
                    overtime_hours = 0.0

            # Định dạng giá trị
            work_hours = f"{work_hours:.2f}"
            overtime_hours = f"{overtime_hours:.2f}"

            # Kiểm tra điều kiện lọc
            date_match = True
            if year != "Tất cả" and row['date']:
                date_match = date_match and row['date'].strftime("%Y") == year
            if month != "Tất cả" and row['date']:
                date_match = date_match and row['date'].strftime("%m") == month.zfill(2)
            if day != "Tất cả" and row['date']:
                date_match = date_match and row['date'].strftime("%d") == day.zfill(2)

            # Kiểm tra từ khóa tìm kiếm
            keyword_match = True
            if keyword and keyword != "tìm kiếm...":
                keyword_match = (
                    keyword in str(emp_id).lower() or
                    keyword in full_name.lower() or
                    keyword in date.lower() or
                    keyword in check_in.lower() or
                    keyword in check_out.lower()
                )

            # Nếu thỏa mãn các điều kiện lọc, thêm vào Treeview
            if date_match and keyword_match:
                self.attendance_tree.insert(
                    "", "end",
                    values=(index, emp_id, full_name, date, check_in, check_out, work_hours, overtime_hours)
                )
                index += 1
                has_data = True

        # Nếu không có dữ liệu nào được hiển thị, hiện thông báo
        if not has_data:
            messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu chấm công.")

    # Lương
    def show_salary(self):
        if hasattr(self, 'current_content') and self.current_content is not None:
            self.current_content.destroy()

        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        filter_frame = tk.Frame(self.current_content, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=2, padx=5)

        filters_inner_frame = tk.Frame(filter_frame, bg=self.bg_color)
        filters_inner_frame.pack(anchor="center")

        # Style cho Combobox
        style = ttk.Style()
        style.configure("Custom.TCombobox",
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        font=("Times New Roman", 11),
                        foreground="black",
                        fieldbackground="white",
                        background="white")
        style.map("Custom.TCombobox",
                    fieldbackground=[("readonly", "white")],
                    background=[("readonly", "white")],
                    foreground=[("readonly", "black")])

        # Combobox tháng
        month_label = tk.Label(filters_inner_frame, text="Tháng:", font=("Times New Roman", 11), bg=self.bg_color)
        month_label.pack(side=tk.LEFT, padx=(0, 5))
        self.month_var = tk.StringVar(value="Tất cả")
        month_combobox = ttk.Combobox(filters_inner_frame,
                                        textvariable=self.month_var,
                                        values=["Tất cả"] + [str(i) for i in range(1, 13)],
                                        state="readonly",
                                        width=10,
                                        style="Custom.TCombobox")
        month_combobox.pack(side=tk.LEFT, padx=5)
        month_combobox.bind("<<ComboboxSelected>>", self.filter_salary)

        # Combobox năm
        year_label = tk.Label(filters_inner_frame, text="Năm:", font=("Times New Roman", 11), bg=self.bg_color)
        year_label.pack(side=tk.LEFT, padx=(10, 5))
        self.year_var = tk.StringVar(value="Tất cả")
        current_year = 2025
        year_combobox = ttk.Combobox(filters_inner_frame,
                                    textvariable=self.year_var,
                                    values=["Tất cả"] + [str(i) for i in range(current_year - 5, current_year + 1)],
                                    state="readonly",
                                    width=10,
                                    style="Custom.TCombobox")
        year_combobox.pack(side=tk.LEFT, padx=5)
        year_combobox.bind("<<ComboboxSelected>>", self.filter_salary)

        # Thanh tìm kiếm
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")
        search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22), Image.Resampling.LANCZOS)
        reset_img = Image.open(os.path.join(img_dir, "reset.png")).resize((22, 22), Image.Resampling.LANCZOS)
        edit_img = Image.open(os.path.join(img_dir, "edit.png")).resize((22, 22), Image.Resampling.LANCZOS)
        salary_img = Image.open(os.path.join(img_dir, "salary.png")).resize((22, 22), Image.Resampling.LANCZOS)
        search_icon = ImageTk.PhotoImage(search_img)
        reset_icon = ImageTk.PhotoImage(reset_img)
        edit_icon = ImageTk.PhotoImage(edit_img)
        salary_icon = ImageTk.PhotoImage(salary_img)

        search_frame = tk.Frame(filters_inner_frame, bg="white", relief="flat", highlightthickness=1, highlightbackground="#4c84f5")
        search_frame.pack(side=tk.LEFT, padx=10, ipady=4)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
                search_frame,
                textvariable=self.search_var,
                font=("Times New Roman", 11),
                width=25,
                fg="gray",
                relief="flat",
                borderwidth=0,
                bg="white"
        )
        self.search_entry.insert(0, "Tìm kiếm...")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_placeholder)
        self.search_entry.bind("<Return>", self.search_salary)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        search_button = tk.Button(
                search_frame,
                image=search_icon,
                command=self.search_salary,
                bg="white",
                bd=0,
                relief="flat",
                activebackground="#fff",
                width=20,
                height=25,
        )
        search_button.image = search_icon
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

        # Button sửa Lương Nhân Viên (khi chọn row)
        edit_button = tk.Button(filters_inner_frame,
            text="Sửa",
            image=edit_icon, 
            compound=tk.TOP,
            command=self.edit_salary_popup, 
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#65f06b")
        edit_button.image = edit_icon
        edit_button.pack(side=tk.LEFT, padx=3)

        # Nút Reset
        reset_button = tk.Button(filters_inner_frame,
            text="Làm mới",
            image=reset_icon, 
            compound=tk.TOP,
            command=self.reset_salary_list, 
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#7d8e96")
        reset_button.image = reset_icon 
        reset_button.pack(side=tk.LEFT, padx=3)

        # Tính lương
        salary_button = tk.Button(filters_inner_frame,
                                    text="Lương",
                                    image=salary_icon,
                                    compound=tk.TOP,
                                    command=self.start_calculate_salary,
                                    bg="#f7f8fa",
                                    bd=0,
                                    width=60,
                                    height=60,
                                    font=("Times New Roman", 9),
                                    relief="flat",
                                    activebackground="#7d8e96")
        salary_button.image = salary_icon
        salary_button.pack(side=tk.LEFT, padx=3)
                
        # Cấu hình Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading",
                        font=("Times New Roman", 10, "bold"),
                        background="#9fd7f9",
                        foreground="#000",
                        relief="flat",
                        borderwidth=0,
                        padding=5)
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white")

        columns = ("STT", "Mã NV", "Nhân Viên", "Tháng/Năm", "Lương cơ bản", "Lương theo giờ", "Tiền tăng ca", "Tổng lương")
        self.salary_tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)

        # Cấu hình cột
        self.salary_tree.heading("STT", text="STT")
        self.salary_tree.heading("Mã NV", text="Mã NV")
        self.salary_tree.heading("Nhân Viên", text="Nhân Viên")
        self.salary_tree.heading("Tháng/Năm", text="Tháng/Năm")
        self.salary_tree.heading("Lương cơ bản", text="Lương cơ bản")
        self.salary_tree.heading("Lương theo giờ", text="Lương theo giờ")
        self.salary_tree.heading("Tiền tăng ca", text="Tiền tăng ca")
        self.salary_tree.heading("Tổng lương", text="Tổng lương")

        self.salary_tree.column("STT", width=50, anchor="center")
        self.salary_tree.column("Mã NV", width=70, anchor="center")
        self.salary_tree.column("Nhân Viên", width=150, anchor="w")
        self.salary_tree.column("Tháng/Năm", width=100, anchor="center")
        self.salary_tree.column("Lương cơ bản", width=120, anchor="center")
        self.salary_tree.column("Lương theo giờ", width=120, anchor="center")
        self.salary_tree.column("Tiền tăng ca", width=120, anchor="center")
        self.salary_tree.column("Tổng lương", width=120, anchor="center")

        # Đưa Treeview vào giao diện và tải dữ liệu
        self.salary_tree.pack(fill=tk.BOTH, expand=True)
        self.load_salary_data()

    def load_salary_data(self, month=None, year=None, search_term=None):
        if not self.conn.is_connected():
            self.conn.reconnect()
        for item in self.salary_tree.get_children():
            self.salary_tree.delete(item)

        # Chuẩn hóa tham số
        month = None if month == "Tất cả" else month
        year = None if year == "Tất cả" else year
            
        # Gọi get_all_salary trực tiếp thay vì DB.get_all_salary
        rows = DB.get_all_salary(self.cursor, month, year, search_term)
        if isinstance(rows, dict) and "error" in rows:
            messagebox.showerror("Lỗi", rows["error"])
            return
            
        for idx, row in enumerate(rows, 1):
            emp_id = row['emp_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            month_year = row['month_year'] if row['month_year'] else "N/A"  # Đã có định dạng %m/%Y từ db
            base_salary = row['base_salary'] if row['base_salary'] is not None else 0
            time_salary = row['time_salary'] if row['time_salary'] is not None else 0
            overtime_salary = row['overtime_salary'] if row['overtime_salary'] is not None else 0
            total_salary = base_salary + overtime_salary

            self.salary_tree.insert("", "end", values=(
                idx, emp_id, full_name, month_year,
                f"{base_salary:,.0f}", f"{time_salary:,.0f}", f"{overtime_salary:,.0f}", f"{total_salary:,.0f}"
            ))
            
        if not rows:
            messagebox.showinfo("Thông báo", "Không có dữ liệu lương!")

    def search_salary(self, event=None):
        month = self.month_var.get()
        year = self.year_var.get()
        search_term = self.search_var.get().strip().lower()
        if search_term == "tìm kiếm...":
            search_term = ""
        self.load_salary_data(month=month, year=year, search_term=search_term)

    def filter_salary(self, event=None):
        self.search_salary()

    def reset_salary_list(self):
        self.month_var.set("Tất cả")
        self.year_var.set("Tất cả")
        self.search_var.set("")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm...")
        self.search_entry.config(fg="gray")
        self.load_salary_data()

    # Bắt đầu tính lương
    def start_calculate_salary(self):
        if not self.conn or not self.conn.is_connected():
            messagebox.showerror("Lỗi", "Kết nối đến cơ sở dữ liệu không thành công!")
            return
        self.root.config(cursor="wait")  
        messagebox.showinfo("Thông báo", "Đang tính lương, vui lòng chờ...")  
        thread = threading.Thread(target=self.calculate_salary, daemon=True)
        thread.start()

    # Tính lương
    def calculate_salary(self):
        try:
            success = DB.calculate_and_update_payroll(self.conn, self.cursor)
            self.root.after(0, lambda: self.on_calculate_complete(success))  
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Lỗi", f"Lỗi khi tính lương: {str(e)}")
            if self.conn and self.conn.is_connected():
                self.conn.rollback

    # 
    def on_calculate_complete(self, success):
        self.root.config(cursor="")
        if success:
            messagebox.showinfo("Thành công", "Đã tính toán và cập nhật lương thành công!")
            if self.conn and self.conn.is_connected():
                self.conn.commit()
            self.load_salary_data()
            self.salary_tree.update_idletasks()
        else:
            messagebox.showerror("Lỗi", "Tính lương thất bại! Vui lòng kiểm tra dữ liệu hoặc kết nối.")
            if self.conn and self.conn.is_connected():
                self.conn.rollback()

    # Sửa Lương Nhân Viên của nhân viên được chọn:
    def edit_salary_popup(self):
        selected_item = self.salary_tree.selection()
        if not selected_item:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một nhân viên để sửa Lương Nhân Viên.")
            return
        item = self.salary_tree.item(selected_item)
        values = item['values']
        emp_id = values[1]
        emp_name = values[2]
        month_year_str = values[3]
        print(month_year_str)
        month, year, day = map(int, month_year_str.split("-"))
        base_salary = values[4].replace(",", "")
        time_salary = values[5].replace(",", "")
        overtime_salary = values[6].replace(",", "")
        # Tạo popup căn giữa màn hình
        popup = tk.Toplevel()
        popup.title("Sửa Lương Nhân Viên")
        popup.resizable(False, False)
        popup_width = 400
        popup_height = 350
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        x_pos = int((screen_width - popup_width) / 2)
        y_pos = int((screen_height - popup_height) / 2)
        popup.geometry(f"{popup_width}x{popup_height}+{x_pos}+{y_pos}")

        label_font = ("Times New Roman", 12)
        entry_font = ("Times New Roman", 12)
        frame = tk.Frame(popup, padx=20, pady=20)
        frame.pack()

        def creat_row(row, label_text, initial_value, state='normal'):
            label = tk.Label(frame, text=label_text, font=label_font, anchor='e', width=15)
            label.grid(row=row, column=0, padx=(20,10), pady=8)
            entry = tk.Entry(frame, font=entry_font, width=25)
            entry.grid(row=row, column=1, padx=(10, 20), pady=8)
            entry.insert(0, initial_value)
            if state == 'readonly':
                entry.config(state='readonly')
            else:
                entry.config(state=state)
            return entry
        entry_emp_id = creat_row(0, "Mã Nhân Viên:", emp_id, 'readonly')
        entry_emp_name = creat_row(1, "Tên Nhân Viên:", emp_name, 'readonly')
        entry_month_year = creat_row(2, "Tháng/Năm", month_year_str, 'readonly')
        entry_base = creat_row(3, "Lương cơ bản:", base_salary)
        entry_time = creat_row(4, "Lương theo giờ:", time_salary)
        entry_ot = creat_row(5, "Lương tăng ca:", overtime_salary)

        def update_salary():
            try:
                new_base = float(entry_base.get())
                new_time = float(entry_time.get())
                new_ot = float(entry_ot.get())
                query = """
                    UPDATE Payroll 
                    SET base_salary = %s, time_salary = %s, overtime_salary = %s
                    WHERE emp_id = %s AND MONTH(month_year) = %s AND YEAR(month_year) = %s
                """
                self.cursor.execute(query, (new_base, new_time, new_ot, emp_id, month, year))
                self.conn.commit()
                messagebox.showinfo("Thành công", "Cập nhật lương thành công!")
                popup.destroy()
                self.load_salary_data(
                    month=self.month_var.get(),
                    year=self.year_var.get(),
                    search_term=self.search_var.get().strip().lower()
                )
            except Exception as e:
                messagebox.showerror("Lỗi", f"Cập nhật lương thất bại: {str(e)}")
        
        update_salary = tk.Button(frame, 
                                  text="Cập nhật", 
                                  font=("Times New Roman", 12, "bold"), 
                                  bg="#4caf50",
                                  fg="white",
                                  padx=5,
                                  pady=5,
                                  command=update_salary)
        update_salary.grid(row=6, column=0, columnspan=2, pady=15)

    def show_statistics(self):
        print("Bắt đầu show_statistics")
        if hasattr(self, 'current_content') and self.current_content is not None:
            print("Xóa current_content cũ")
            if hasattr(self, 'stat_app') and self.stat_app:
                print("Hủy StatisticApp hiện tại")
                self.stat_app.destroy()
                self.stat_app = None
            self.current_content.destroy()

        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)
        print("Đã tạo current_content mới")

        try:
            print("Đang import src.statistic")
            import src.salary.statistic
            print("Đang tạo StatisticApp")
            self.stat_app = src.salary.statistic.StatisticApp(self.current_content, self.conn, self.cursor)
            print("StatisticApp đã được tạo thành công")
        except Exception as e:
            print(f"Lỗi khi tải StatisticApp: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải giao diện Thống Kê: {e}")

    # Logout
    def signin(self):
        if messagebox.askokcancel("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            if hasattr(self, 'stat_app') and self.stat_app:
                print("Hủy StatisticApp trước khi đăng xuất")
                self.stat_app.destroy()
                self.stat_app = None
            if self.conn and self.conn.is_connected():
                DB.close_connection(self.conn, self.cursor)
            self.root.destroy()
            import sys
            sys.exit(0) 

if __name__ == "__main__":
    root = tk.Tk()
    app = ManagerApp(root)
    root.mainloop() 