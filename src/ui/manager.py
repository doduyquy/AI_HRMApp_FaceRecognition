import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import mysql.connector
from PIL import Image, ImageTk, ImageDraw
import os
import re
import datetime
from tkcalendar import DateEntry
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import src.salary.excel_utils  
import src.salary.salary  
import src.salary.statistic  
import threading  # Thêm threading để chạy tính lương trong nền

class ManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Nhân Sự")
        self.root.geometry("1200x600+50+40")
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

        self.selected_button = None
        self.current_content = None
        self.search_entry = None
        self.current_menu = "Nhân Sự"

        self.conn = mysql.connector.connect(
            host="localhost", 
            user="root",
            password="12345678",
            database="Face_Recognition"
        )
        self.cursor = self.conn.cursor(dictionary=True)  # Sử dụng dictionary cursor để dễ xử lý dữ liệu

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

        # Nút Thêm
        add_button = tk.Button(buttons_inner_frame, 
            text="Thêm", 
            image=add_icon, 
            compound=tk.TOP,
            command=self.add_employee,
            bg="#f7f8fa", 
            bd=0, 
            width=60, 
            height=60,
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
            width=60, 
            height=60,
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
            width=60, 
            height=60,
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
            command=lambda: src.salary.excel_utils.export_to_excel(self.tree, "Employees"),  # Sửa: Thêm 'src.'
            bg="#f7f8fa", 
            bd=0, 
            width=60, 
            height=60,
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
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#7d8e96")
        reset_button.image = reset_icon 
        reset_button.pack(side=tk.LEFT, padx=3)

        # Frame chứa ô tìm kiếm và nút tìm kiếm
        search_frame = tk.Frame(buttons_inner_frame, bg="white", relief="flat", highlightthickness=1, highlightbackground="#4c84f5")
        search_frame.pack(side=tk.LEFT, padx=10, ipady=4)

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

    def load_employee_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            if not self.conn.is_connected():
                self.conn.reconnect()
            query = """
                SELECT e.emp_id, e.first_name, e.last_name, e.position, e.email, e.phone_number, e.hired_date,
                    d.dep_name, e.dep_id, e.status
                FROM Employees e
                LEFT JOIN Departments d ON e.dep_id = d.dep_id
                ORDER BY e.emp_id ASC
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

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
                self.tree.tag_configure("Nghỉ làm việc", background="#f7f5f5") 
                self.tree.tag_configure("N/A", background="#f7fafa")      

            if not rows:
                messagebox.showinfo("Thông báo", "Không có dữ liệu nhân viên!")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {e}")

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

        fields = ["Nhân Viên", "Chức Vụ", "Phòng Ban", "Email", "Số Điện Thoại", "Ngày Tuyển Dụng"]
        self.entries = {}

        for i, field in enumerate(fields):
            label = tk.Label(container, text=field + ":", font=("Times New Roman", 11), bg="#ffffff", justify="left")
            label.grid(row=i, column=0, sticky="w", padx=(0, 15), pady=17)

            if field in ["Phòng Ban", "Chức Vụ"]:
                values = ["Employee", "IT Department", "Manager Department"] if field == "Phòng Ban" else ["Employee", "Developer", "Manager"]
                entry = ttk.Combobox(container, values=values, font=("Times New Roman", 11), state="readonly", width=29)
                entry.set("Chọn phòng ban" if field == "Phòng Ban" else "Chọn chức vụ")
            elif field == "Ngày Tuyển Dụng":
                entry = DateEntry(container, font=("Times New Roman", 11), state="readonly", date_pattern="yyyy-mm-dd", width=29)
            else:
                entry = ttk.Entry(container, width=36)
            entry.grid(row=i, column=1, pady=12, sticky="w")
            self.entries[field] = entry

        save_btn = tk.Button(container, text="Lưu",
                            font=("Times New Roman", 11, "bold"),
                            bg="#4CAF50", fg="white",
                            command=lambda: self.save_employee(form),  # Đảm bảo truyền form
                            padx=25, pady=10, relief="flat")
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def save_employee(self, form):
        data = {key: entry.get().strip() for key, entry in self.entries.items()}
        if not all(data.values()) or any(v in ["Chọn phòng ban", "Chọn chức vụ"] for v in data.values()):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        full_name = data["Nhân Viên"]
        name_parts = full_name.split()
        first_name = name_parts[-1] if name_parts else ""
        last_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else ""

        dep_name = data["Phòng Ban"]
        try:
            if not self.conn.is_connected():
                self.connect_db()
            self.cursor.execute("SELECT dep_id FROM Departments WHERE dep_name = %s", (dep_name,))
            dep_id_result = self.cursor.fetchone()
            if not dep_id_result:
                messagebox.showerror("Lỗi", f"Phòng ban '{dep_name}' không tồn tại!")
                return
            dep_id = dep_id_result['dep_id']

            self.cursor.execute("""
                INSERT INTO Employees (last_name, first_name, dep_id, email, phone_number, hired_date, position, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (last_name, first_name, dep_id, data["Email"], data["Số Điện Thoại"], data["Ngày Tuyển Dụng"], data["Chức Vụ"], "Đang làm việc"))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm nhân viên!")
            form.destroy()
            self.load_employee_data()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Thêm thất bại: {e}")
            self.conn.rollback()

    def is_valid_email(self, email):
        return "@" in email and "." in email
    
    def show_email_error(self, message):
        if self.error_label:
            self.error_label.grid_forget()

        style = ttk.Style()
        style.configure("Error.TEntry",
                        font=("Times New Roman", 11),
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        foreground="black",
                        fieldbackground="white",
                        bordercolor="red")

        self.email_entry.configure(style="Error.TEntry")
        self.error_label = tk.Label(self.email_entry.master, text=message,
                                    fg="red", font=("Times New Roman", 9), bg="#ffffff")
        self.error_label.place(x=self.email_entry.winfo_x() + 4,
                       y=self.email_entry.winfo_y() + self.email_entry.winfo_height() + 2)

    def is_valid_phone(self, phone):
        return phone.isdigit() and len(phone) >= 10

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

    def center_window(self, win, width, height):
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def edit_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên để sửa")
            return

        emp_id = self.tree.item(selected_item)['values'][1] 
        if not emp_id:
            messagebox.showerror("Lỗi", "Không thể lấy ID nhân viên.")
            return

        try:
            if not self.conn.is_connected():
                self.connect_db()
            self.cursor.execute("""
                SELECT last_name, first_name, position, dep_name, email, phone_number, hired_date, status
                FROM Employees e
                JOIN Departments d ON e.dep_id = d.dep_id
                WHERE e.emp_id = %s
            """, (emp_id,))
            employee_data = self.cursor.fetchone()

            if not employee_data:
                messagebox.showerror("Lỗi", "Không thể lấy dữ liệu nhân viên từ database.")
                return

            last_name = employee_data['last_name']
            first_name = employee_data['first_name']
            position = employee_data['position']
            dep_name = employee_data['dep_name']
            email = employee_data['email']
            phone_number = employee_data['phone_number']
            hired_date = employee_data['hired_date']
            status = employee_data['status']

            full_name = f"{last_name} {first_name}".strip()
            # Kiểm tra kiểu dữ liệu của hired_date
            if isinstance(hired_date, (datetime.date, datetime.datetime)):
                hired_date_str = hired_date.strftime("%Y-%m-%d")
            else:
                hired_date_str = hired_date if hired_date else ""
            status_display = "Đang làm việc" if status == "Đang làm việc" else "Đã nghỉ"
            phone_number = str(phone_number) if phone_number else ""

            item_data = [full_name, position, dep_name, email, phone_number, hired_date_str, status_display]

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu từ database: {e}")
            return

        # Phần còn lại của hàm giữ nguyên
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

        style = ttk.Style()
        style.configure("Custom.TEntry", font=("Times New Roman", 11), padding=6, relief="solid", borderwidth=1)
        style.configure("Custom.TCombobox", padding=6, relief="solid", borderwidth=1, font=("Times New Roman", 11))
        style.configure("Custom.DateEntry", padding=6, relief="solid", borderwidth=1, font=("Times New Roman", 11))

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
                entry = DateEntry(container, font=("Times New Roman", 11), state="readonly", date_pattern="yyyy-mm-dd", width=25)
            else:
                entry = ttk.Entry(container, width=31, style="Custom.TEntry")
            entry.grid(row=i, column=1, pady=8, sticky="w")
            self.edit_entries[field] = entry

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

        save_btn = tk.Button(container, text="Cập Nhật",
                            font=("Times New Roman", 11, "bold"),
                            bg="#4CAF50", fg="white",
                            command=lambda: self.save_edit_employee(emp_id, form),
                            padx=25, pady=10, relief="flat")
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def save_edit_employee(self, emp_id, form):
        self.entries = self.edit_entries 
        data = {key: entry.get().strip() for key, entry in self.edit_entries.items()}
        email = data.get("Email", "")
        phone = data.get("Số Điện Thoại", "")
        if phone and not phone.startswith("0"):
            phone = "0" + phone

        hire_date_str = data.get("Ngày Tuyển Dụng", "")
        has_error = False

        for lbl in getattr(self, 'empty_error_labels', []):
            lbl.place_forget()
        self.empty_error_labels = []

        for key, value in data.items():
            entry = self.edit_entries[key]
            if not value:
                lbl = tk.Label(entry.master, text="Không được để trống", fg="red",
                            font=("Times New Roman", 9), bg="#ffffff")
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

        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, hire_date_str):
            entry = self.edit_entries["Ngày Tuyển Dụng"]
            lbl = tk.Label(entry.master, text="Ngày không hợp lệ!", fg="red",
                        font=("Times New Roman", 9), bg="#ffffff")
            lbl.place(x=entry.winfo_x() + 4, y=entry.winfo_y() + entry.winfo_height() + 2)
            self.empty_error_labels.append(lbl)
            has_error = True

        if has_error:
            return

        full_name = data.get("Nhân Viên", "").strip()
        name_parts = full_name.split()
        first_name = name_parts[-1] if name_parts else "" 
        last_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else ""  

        dep_name = data.get("Phòng Ban", "")
        try:
            if not self.conn.is_connected():
                self.connect_db()
            self.cursor.execute("SELECT dep_id FROM Departments WHERE dep_name = %s", (dep_name,))
            dep_id_result = self.cursor.fetchone()
            if not dep_id_result:
                messagebox.showerror("Lỗi", f"Phòng ban '{dep_name}' không tồn tại!")
                return
            dep_id = dep_id_result['dep_id']  # Sửa: dùng key 'dep_id' thay vì chỉ số [0]

            self.cursor.execute("""
                UPDATE Employees
                SET last_name = %s, first_name = %s, dep_id = %s, email = %s, phone_number = %s,
                    hired_date = %s, position = %s, status = %s
                WHERE emp_id = %s
            """, (
                last_name, first_name, dep_id, email, phone, hire_date_str,
                data.get("Chức Vụ", ""), data.get("Trạng Thái", ""), emp_id
            ))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhân viên.")
            form.destroy()
            self.load_employee_data()
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Cập nhật thất bại: {e}")
            self.conn.rollback()

    def delete_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên để xóa.")
            return

        employee_data = self.tree.item(selected_item)['values']
        if not employee_data:
            messagebox.showerror("Lỗi", "Không thể lấy dữ liệu nhân viên.")
            return

        employee_name = employee_data[2]
        emp_id = employee_data[1]

        form = tk.Toplevel(self.root)
        form.title("Xác Nhận Xóa")
        form.configure(bg="white")
        self.center_window(form, 400,200)
        form.grab_set() 

        label = tk.Label(form, text=f"Bạn có chắc muốn xóa\nnhân viên \"{employee_name}\"?",
                        font=("Times New Roman", 12, "bold"),
                        fg="#333333", bg="#fff", justify="center")
        label.pack(pady=30)

        btn_frame = tk.Frame(form, bg="#fff")
        btn_frame.pack(pady=10)

        def confirm_delete():
            try:
                self.cursor.execute("DELETE FROM Employees WHERE emp_id = %s", (emp_id,))
                self.conn.commit()
                self.tree.delete(selected_item)
                form.destroy()
                messagebox.showinfo("Thành công", f"Đã xóa nhân viên: {employee_name}")
                self.load_employee_data()
            except mysql.connector.Error as e:
                self.conn.rollback()
                form.destroy()
                messagebox.showerror("Lỗi", f"Không thể xóa nhân viên.\n")

        def cancel():
            form.destroy()

        delete_btn = tk.Button(btn_frame, text="Xóa", command=confirm_delete,
                            font=("Times New Roman", 11, "bold"),
                            bg="#f5021b", fg="white", padx=20, pady=8,
                            activebackground="#c0392b", relief="flat")
        delete_btn.grid(row=0, column=0, padx=15)

        cancel_btn = tk.Button(btn_frame, text="Hủy", command=cancel,
                            font=("Times New Roman", 11, "bold"),
                            bg="#696667", fg="white", padx=20, pady=8,
                            activebackground="#95a5a6", relief="flat")
        cancel_btn.grid(row=0, column=1, padx=15)

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
    
    def reset_employee_list(self):
        self.search_var.set("")
        self.search_entry.config(fg="gray")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "")
        self.load_employee_data()

    def filter_employee(self, event=None):
        search_term = self.search_var.get().strip().lower()
        if search_term == "tìm kiếm...":
            search_term = ""

        position_filter = getattr(self, 'position_var', tk.StringVar(value="Tất cả")).get()
        dep_filter = getattr(self, 'dep_var', tk.StringVar(value="Tất cả")).get()
        year_filter = getattr(self, 'year_var', tk.StringVar(value="Tất cả")).get()
        month_filter = getattr(self, 'month_var', tk.StringVar(value="Tất cả")).get()
        day_filter = getattr(self, 'day_var', tk.StringVar(value="")).get()

        date_filter = None
        if day_filter:
            try:
                if len(day_filter) == 4:
                    date_filter = f"{day_filter}-01-01"
                    datetime.strptime(date_filter, "%Y-%m-%d")
                elif len(day_filter) == 7:
                    date_filter = f"{day_filter}-01"
                    datetime.strptime(date_filter, "%Y-%m-%d")
                elif len(day_filter) >= 10:
                    date_filter = day_filter
                    datetime.strptime(date_filter, "%Y-%m-%d")
            except ValueError:
                date_filter = None

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            if not self.conn.is_connected():
                self.conn.reconnect()
            query = """
                SELECT e.emp_id, e.first_name, e.last_name, e.position, e.email, e.phone_number, e.hired_date,
                    d.dep_name, e.dep_id, e.status
                FROM Employees e
                LEFT JOIN Departments d ON e.dep_id = d.dep_id
                WHERE 1=1
            """
            params = []

            if search_term:
                query += """
                    AND (LOWER(e.emp_id) LIKE %s
                    OR LOWER(CONCAT(e.first_name, ' ', e.last_name)) LIKE %s
                    OR LOWER(e.position) LIKE %s
                    OR LOWER(e.email) LIKE %s
                    OR LOWER(e.phone_number) LIKE %s
                    OR LOWER(e.hired_date) LIKE %s
                    OR LOWER(d.dep_name) LIKE %s
                    OR LOWER(e.status) LIKE %s)
                """
                params.extend([f"%{search_term}%"] * 8)

            if position_filter != "Tất cả":
                query += " AND e.position = %s"
                params.append(position_filter)

            if dep_filter != "Tất cả":
                query += " AND d.dep_name = %s"
                params.append(dep_filter)

            if year_filter != "Tất cả" and year_filter:
                query += " AND YEAR(e.hired_date) = %s"
                params.append(int(year_filter))

            if month_filter != "Tất cả" and month_filter:
                query += " AND MONTH(e.hired_date) = %s"
                params.append(int(month_filter))

            if date_filter:
                query += " AND DATE(e.hired_date) = %s"
                params.append(date_filter)

            query += " ORDER BY e.emp_id ASC"
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()

            for idx, row in enumerate(rows, 1):
                emp_id = row['emp_id']
                full_name = f"{row['last_name']} {row['first_name']}"
                position = row['position'] if row['position'] else "N/A"
                department = row['dep_name'] if row['dep_name'] else "N/A"
                email = row['email'] if row['email'] else "N/A"
                phone = row['phone_number'] if row['phone_number'] else "N/A"
                hired_date = row['hired_date'].strftime("%Y-%m-%d") if row['hired_date'] else "N/A"
                status = row['status'] if row['status'] else "N/A"
                self.tree.insert("", "end", values=(idx, emp_id, full_name, position, department, email, phone, hired_date, status))

            if not rows:
                messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu phù hợp!")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {e}")

    def show_attendance(self):
        if hasattr(self, 'current_content') and self.current_content is not None:
            self.current_content.destroy()

        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"))

        button_frame = tk.Frame(self.current_content, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=2, padx=5)

        buttons_inner_frame = tk.Frame(button_frame, bg=self.bg_color)
        buttons_inner_frame.pack(anchor="center")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")

        reset_img = Image.open(os.path.join(img_dir, "reset.png")).resize((22, 22), Image.Resampling.LANCZOS)
        search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22), Image.Resampling.LANCZOS)
        excel_img = Image.open(os.path.join(img_dir, "excel.png")).resize((22, 22), Image.Resampling.LANCZOS)
        reset_icon = ImageTk.PhotoImage(reset_img)
        search_icon = ImageTk.PhotoImage(search_img)
        excel_icon = ImageTk.PhotoImage(excel_img)

        excel_button = tk.Button(buttons_inner_frame, 
            text="Excel", 
            image=excel_icon, 
            compound=tk.TOP,
            command=lambda: src.salary.excel_utils.export_to_excel(self.attendance_tree, "Attendance"),  # Sửa: Thêm 'src.'
            bg="#f7f8fa", 
            bd=0, 
            width=60, 
            height=60,
            font=("Times New Roman", 9), 
            relief="flat",
            activebackground="#65f06b")
        excel_button.image = excel_icon
        excel_button.pack(side=tk.LEFT, padx=3)

        reset_button = tk.Button(buttons_inner_frame,
            text="Làm mới",
            image=reset_icon, 
            compound=tk.TOP,
            command=self.reset, 
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#7d8e96")
        reset_button.image = reset_icon 
        reset_button.pack(side=tk.LEFT, padx=3)
        
        search_frame = tk.Frame(buttons_inner_frame, bg="white", relief="flat", highlightthickness=1, highlightbackground="#4c84f5")
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
        self.search_entry.bind("<Return>", self.search)
        
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        search_button = tk.Button(
            search_frame,
            image=search_icon,
            command=self.search,
            bg="white",
            bd=0,
            relief="flat",
            activebackground="#fff",
            width=20, 
            height=25,
        )
        search_button.image = search_icon
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

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

    def load_attendance_data(self):
        if not hasattr(self, 'attendance_tree') or not self.attendance_tree.winfo_exists():
            return

        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        try:
            if not self.conn.is_connected():
                self.conn.reconnect()
            query = """
                SELECT e.emp_id, e.first_name, e.last_name, a.date, a.check_in, a.check_out, a.work_hours, a.overtime_hours
                FROM Employees e
                LEFT JOIN Attendance a ON e.emp_id = a.emp_id
                WHERE e.status = 'Đang làm việc'
                ORDER BY a.date DESC
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for idx, row in enumerate(rows, 1):
                emp_id = row['emp_id']
                full_name = f"{row['last_name']} {row['first_name']}" 
                date = row['date'].strftime("%Y-%m-%d") if row['date'] else "N/A"
                check_in = row['check_in'].strftime("%H:%M") if row['check_in'] else "N/A"
                check_out = row['check_out'].strftime("%H:%M") if row['check_out'] else "N/A"
                work_hours = f"{row['work_hours']:.2f}" if row['work_hours'] is not None else "0.00"
                overtime_hours = f"{row['overtime_hours']:.2f}" if row['overtime_hours'] is not None else "0.00"
                
                self.attendance_tree.insert("", "end", values=(idx, emp_id, full_name, date, check_in, check_out, work_hours, overtime_hours))
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

    def search(self, event=None):
        keyword = self.search_var.get().strip().lower()

        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        try:
            if not self.conn.is_connected():
                self.conn.reconnect()
            query = """
                SELECT e.emp_id, e.first_name, e.last_name, a.date, a.check_in, a.check_out, a.work_hours, a.overtime_hours
                FROM Employees e
                LEFT JOIN Attendance a ON e.emp_id = a.emp_id
                WHERE e.status = 'Đang làm việc'
                ORDER BY a.date DESC
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            index = 1
            for row in rows:
                emp_id = row['emp_id']
                full_name = f"{row['last_name']} {row['first_name']}"
                date = row['date'].strftime("%Y-%m-%d") if row['date'] else "N/A"
                check_in = row['check_in'].strftime("%H:%M") if row['check_in'] else "N/A"
                check_out = row['check_out'].strftime("%H:%M") if row['check_out'] else "N/A"
                work_hours = f"{row['work_hours']:.2f}" if row['work_hours'] is not None else "0.00"
                overtime_hours = f"{row['overtime_hours']:.2f}" if row['overtime_hours'] is not None else "0.00"

                if (keyword in str(emp_id).lower() or 
                    keyword in full_name.lower() or
                    keyword in date or
                    keyword in check_in or
                    keyword in check_out):
                    self.attendance_tree.insert(
                        "", "end",
                        values=(index, emp_id, full_name, date, check_in, check_out, work_hours, overtime_hours)
                    )
                    index += 1

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi truy vấn dữ liệu: {e}")

    def reset(self):
        self.search_var.set("")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm...")
        self.load_attendance_data()

    def show_salary(self):
        if hasattr(self, 'current_content') and self.current_content is not None:
            self.current_content.destroy()

        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        filter_frame = tk.Frame(self.current_content, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=2, padx=5)

        filters_inner_frame = tk.Frame(filter_frame, bg=self.bg_color)
        filters_inner_frame.pack(anchor="center")

        month_label = tk.Label(filters_inner_frame, text="Tháng:", font=("Times New Roman", 11), bg=self.bg_color)
        month_label.pack(side=tk.LEFT, padx=(0, 5))
        self.month_var = tk.StringVar(value="Tất cả")
        month_combobox = ttk.Combobox(filters_inner_frame, textvariable=self.month_var, values=["Tất cả"] + [str(i) for i in range(1, 13)], state="readonly", width=10)
        month_combobox.pack(side=tk.LEFT, padx=5)
        month_combobox.bind("<<ComboboxSelected>>", self.filter_salary)

        year_label = tk.Label(filters_inner_frame, text="Năm:", font=("Times New Roman", 11), bg=self.bg_color)
        year_label.pack(side=tk.LEFT, padx=(10, 5))
        self.year_var = tk.StringVar(value="Tất cả")
        current_year = 2025
        year_combobox = ttk.Combobox(filters_inner_frame, textvariable=self.year_var, values=["Tất cả"] + [str(i) for i in range(current_year - 5, current_year + 1)], state="readonly", width=10)
        year_combobox.pack(side=tk.LEFT, padx=5)
        year_combobox.bind("<<ComboboxSelected>>", self.filter_salary)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")
        search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22), Image.Resampling.LANCZOS)
        excel_img = Image.open(os.path.join(img_dir, "excel.png")).resize((22, 22), Image.Resampling.LANCZOS)
        salary_img = Image.open(os.path.join(img_dir, "salary.png")).resize((22, 22), Image.Resampling.LANCZOS)

        search_icon = ImageTk.PhotoImage(search_img)
        excel_icon = ImageTk.PhotoImage(excel_img)
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
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        search_button = tk.Button(
            search_frame,
            image=search_icon,
            command=self.filter_salary,
            bg="white",
            bd=0,
            relief="flat",
            activebackground="#fff",
            width=20,
            height=25,
        )
        search_button.image = search_icon
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

        excel_button = tk.Button(filters_inner_frame, 
            text="Excel", 
            image=excel_icon, 
            compound=tk.TOP,
            command=lambda: src.salary.excel_utils.export_to_excel(self.salary_tree, "Payroll"),  # Sửa: Thêm 'src.'
            bg="#f7f8fa", 
            bd=0, 
            width=60, 
            height=60,
            font=("Times New Roman", 9), 
            relief="flat",
            activebackground="#65f06b")
        excel_button.image = excel_icon
        excel_button.pack(side=tk.LEFT, padx=3)

        salary_button = tk.Button(filters_inner_frame, 
            text="Lương", 
            image=salary_icon, 
            compound=tk.TOP,
            command=self.start_calculate_salary,  # Gọi hàm mới sử dụng threading
            bg="#f7f8fa", 
            bd=0, 
            width=60, 
            height=60,
            font=("Times New Roman", 9), 
            relief="flat",
            activebackground="#ffcc00")
        salary_button.image = salary_icon
        salary_button.pack(side=tk.LEFT, padx=3)

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

        columns = ("STT", "Mã NV", "Nhân Viên", "Tháng/Năm", "Lương cơ bản", "Lương theo giờ", "Tiền tăng ca", "Tổng lương")
        self.salary_tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)

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

        self.salary_tree.pack(fill=tk.BOTH, expand=True)

        self.load_salary_data()

    def load_salary_data(self, month=None, year=None, search_term=None):
        if not self.conn.is_connected():
            self.conn.reconnect()
        for item in self.salary_tree.get_children():
            self.salary_tree.delete(item)

        try:
            query = """
                SELECT e.emp_id, e.first_name, e.last_name, p.month_year, p.base_salary, p.time_salary, p.overtime_salary
                FROM Employees e
                LEFT JOIN Payroll p ON e.emp_id = p.emp_id
                WHERE 1=1
            """
            params = []

            if month and month != "Tất cả":
                query += " AND MONTH(p.month_year) = %s"
                params.append(int(month))

            if year and year != "Tất cả":
                query += " AND YEAR(p.month_year) = %s"
                params.append(int(year))

            if search_term and search_term != "tìm kiếm...":
                query += """
                    AND (LOWER(e.emp_id) LIKE %s
                    OR LOWER(CONCAT(e.first_name, ' ', e.last_name)) LIKE %s)
                """
                params.extend([f"%{search_term}%", f"%{search_term}%"])

            query += " ORDER BY e.emp_id, p.month_year DESC"
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()

            for idx, row in enumerate(rows, 1):
                emp_id = row['emp_id']
                full_name = f"{row['last_name']} {row['first_name']}"
                month_year = row['month_year'].strftime("%m/%Y") if row['month_year'] else "N/A"
                base_salary = row['base_salary'] if row['base_salary'] is not None else 0
                time_salary = row['time_salary'] if row['time_salary'] is not None else 0
                overtime_salary = row['overtime_salary'] if row['overtime_salary'] is not None else 0
                total_salary = base_salary + time_salary + overtime_salary

                self.salary_tree.insert("", "end", values=(
                    idx,
                    emp_id,
                    full_name,
                    month_year,
                    f"{base_salary:,.0f}",
                    f"{time_salary:,.0f}",
                    f"{overtime_salary:,.0f}",
                    f"{total_salary:,.0f}"
                ))

            if not rows:
                messagebox.showinfo("Thông báo", "Không có dữ liệu lương!")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

    def filter_salary(self, event=None):
        month = self.month_var.get()
        year = self.year_var.get()
        search_term = self.search_var.get().strip().lower()
        if search_term == "tìm kiếm...":
            search_term = ""

        self.load_salary_data(month=month, year=year, search_term=search_term)

    def start_calculate_salary(self):
        self.root.config(cursor="wait")  # Hiển thị con trỏ chờ
        messagebox.showinfo("Thông báo", "Đang tính lương, vui lòng chờ...")  # Thông báo tiến trình
        thread = threading.Thread(target=self.calculate_salary, daemon=True)
        thread.start()

    def calculate_salary(self):
        try:
            success = src.salary.salary.calculate_and_update_payroll()  # Sửa: Thêm 'src.'
            self.root.after(0, lambda: self.on_calculate_complete(success))  # Cập nhật giao diện sau khi hoàn tất
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi tính lương: {str(e)}"))

    def on_calculate_complete(self, success):
        self.root.config(cursor="")  # Khôi phục con trỏ
        if success:
            messagebox.showinfo("Thành công", "Đã tính toán và cập nhật lương thành công!")
            # Làm mới kết nối cơ sở dữ liệu và tải lại dữ liệu
            if self.conn and self.conn.is_connected():
                self.cursor.close()
                self.conn.close()
            self.conn = mysql.connector.connect(
                host="localhost", 
                user="root",
                password="12345678",
                database="Face_Recognition"
            )
            self.cursor = self.conn.cursor(dictionary=True)
            self.load_salary_data()  # Tải lại dữ liệu lương
            self.salary_tree.update()  # Cập nhật giao diện Treeview
        else:
            messagebox.showerror("Lỗi", "Tính lương thất bại! Vui lòng kiểm tra dữ liệu hoặc kết nối.")

    def show_statistics(self):
        print("Bắt đầu show_statistics")  # Debug
        if hasattr(self, 'current_content') and self.current_content is not None:
            print("Xóa current_content cũ")  # Debug
            self.current_content.destroy()

        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)
        print("Đã tạo current_content mới")  # Debug

        # Gọi giao diện từ statistic.py
        try:
            print("Đang import src.statistic")  # Debug
            import src.salary.statistic
            print("Đang tạo StatisticApp")  # Debug
            stat_app = src.salary.statistic.StatisticApp(self.current_content, self.conn, self.cursor)
            print("StatisticApp đã được tạo thành công")  # Debug
        except AttributeError as e:
            print(f"Lỗi AttributeError: {e}")  # Debug
            messagebox.showerror("Lỗi", f"Không thể tải giao diện Thống Kê: {e}")
            label = tk.Label(self.current_content, text="Chưa triển khai giao diện Thống Kê", font=("Times New Roman", 12), bg=self.bg_color)
            label.pack(expand=True)
        except Exception as e:
            print(f"Lỗi không xác định: {e}")  # Debug
            messagebox.showerror("Lỗi", f"Lỗi không xác định khi tải giao diện Thống Kê: {e}")

    def signin(self):
        if messagebox.askokcancel("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            if self.conn and self.conn.is_connected():
                self.cursor.close()
                self.conn.close()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ManagerApp(root)
    root.mainloop() 