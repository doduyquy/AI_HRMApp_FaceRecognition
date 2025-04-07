import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import mysql.connector
from PIL import Image, ImageTk, ImageDraw
import os
import re
from datetime import datetime
from tkcalendar import DateEntry


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
        self.cursor = self.conn.cursor()

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

        # Kiểm tra sự tồn tại của option trong menu_buttons
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
            
            # Ktra và xử lý đối tượng search_entry
            if hasattr(self, 'search_entry') and self.search_entry.winfo_exists():  
                self.search_entry.delete(0, tk.END) 

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
        elif item == "Chấm công":
            self.show_attendance()
        elif item == "Lương":
            self.show_salary()
        elif item == "Đăng xuất":
            self.signin()

    # Hiển thị ds nhân viên
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

        # Icon
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
            command=self.export_to_excel,
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

        # Tuỳ chỉnh layout header để áp dụng màu nền
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

        # Cấu hình dòng
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white")

        # Màu khi chọn dòng
        style.map("Treeview",
                background=[("selected", "#e5e5e5")],
                foreground=[("selected", "black")])

        # Danh sách columns
        columns = ("STT", "Mã NV", "Nhân Viên", "Chức Vụ", "Phòng Ban", "Email", "Số Điện Thoại", "Ngày Tuyển Dụng", "Trạng Thái")
        self.tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)

        # Tiêu đề và cột
        self.tree.heading("STT", text="STT")
        self.tree.heading("Mã NV", text="Mã NV")
        self.tree.heading("Nhân Viên", text="Nhân Viên")
        self.tree.heading("Chức Vụ", text="Chức Vụ")
        self.tree.heading("Phòng Ban", text="Phòng Ban")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Số Điện Thoại", text="Số Điện Thoại")
        self.tree.heading("Ngày Tuyển Dụng", text="Ngày Tuyển Dụng")
        self.tree.heading("Trạng Thái", text="Trạng Thái")

        # Căn chỉnh và đặt chiều rộng cột
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

    # Tải dữ liệu nhân viên từ db và hiển thị
    def load_employee_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="12345678", database="Face_Recognition")
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT e.emp_id, e.first_name, e.last_name, e.position, e.email, e.phone_number, e.hired_date,
                    d.dep_name, e.dep_id, e.status
                FROM Employees e
                LEFT JOIN Departments d ON e.dep_id = d.dep_id
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
                hired_date = row['hired_date'].strftime("%Y-%m-%d") if row['hired_date'] else "N/A"
                status = row['status'] if row['status'] else "N/A"

                self.tree.insert("", "end", values=(idx, emp_id, full_name, position, department, email, phone, hired_date, status), tags=(status,))
                self.tree.tag_configure("Đang làm việc", background="#fafcfc") 
                self.tree.tag_configure("Nghỉ làm việc", background="#f7f5f5") 
                self.tree.tag_configure("N/A", background="#f7fafa")      

            cursor.close()
            conn.close()

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

        # Tạo style
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
            label = tk.Label(container, text=field + ":", font=("Times New Roman", 11), bg="#ffffff",justify="left")
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

            entry.grid(row=i, column=1, pady=12, sticky="w")
            self.entries[field] = entry

            if field == "Email":
                self.email_entry = entry
                self.email_row_index = i

        # Lưu
        save_btn = tk.Button(container, text="Lưu",
                             font=("Times New Roman", 11, "bold"),
                             bg="#4CAF50", fg="white",
                             activebackground="#45a049",
                             padx=25, pady=10,
                             command=self.save_employee,
                             relief="flat", borderwidth=0)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
        save_btn.configure(width=20)

    # Lưu nhân viên
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
                    lbl = tk.Label(entry.master, text="Không được để trống", fg="red",
                                font=("Times New Roman", 9), bg="#ffffff")
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
            self.cursor.execute("SELECT dep_id FROM Departments WHERE dep_name = %s", (dep_name,))
            dep_id_result = self.cursor.fetchone()
            dep_id = dep_id_result[0] if dep_id_result else None

            try:
                self.cursor.execute("""
                    INSERT INTO Employees (last_name, first_name, dep_id, email, phone_number, hired_date, position, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    last_name,
                    first_name,
                    dep_id,
                    data.get("Email", ""),
                    data.get("Số Điện Thoại", ""),
                    hired_date, 
                    data.get("Chức Vụ", ""),
                    "Đang làm việc"
                ))
                self.conn.commit()

                # Hộp thoại
                messagebox.showinfo("Thông Báo", "Đã lưu thành công!")
            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Lưu thất bại: {e}")
                self.conn.rollback()

    # Định dạng email
    def is_valid_email(self, email):
        return "@" in email and "." in email
    
    # Nếu lỗi email
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

    # Phone
    def is_valid_phone(self, phone):
        return phone.isdigit() and len(phone) >= 10

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
            return

        # Lấy emp_id từ Treeview
        emp_id = self.tree.item(selected_item)['values'][1] 
        if not emp_id:
            messagebox.showerror("Lỗi", "Không thể lấy ID nhân viên.")
            return

        try:
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

            # Dữ liệu lấy từ db
            last_name, first_name, position, dep_name, email, phone_number, hired_date, status = employee_data
            full_name = f"{last_name} {first_name}".strip()
            hired_date_str = hired_date.strftime("%Y-%m-%d") if hired_date else ""
            status_display = "Đang làm việc" if status == "Đang làm việc" else "Đã nghỉ"
            phone_number = str(phone_number) if phone_number else ""

            # Dữ liệu để điền vào form
            item_data = [full_name, position, dep_name, email, phone_number, hired_date_str, status_display]

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu từ database: {e}")
            return

        # Tạo sửa
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
                            command=lambda: self.save_edit_employee(emp_id, form),
                            relief="flat", borderwidth=0)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
        save_btn.configure(width=20)

        # Hàm xử lý khi nhấn "Cập Nhật"
        def save_edited_employee():
            self.entries = self.edit_entries 
            data = {key: entry.get().strip() for key, entry in self.edit_entries.items()}
            email = data.get("Email", "")
            phone = data.get("Số Điện Thoại", "")
            if phone and not phone.startswith("0"):
                phone = "0" + phone

            hire_date_str = data.get("Ngày Tuyển Dụng", "")
            
            has_error = False

            # Clear lỗi cũ
            for lbl in getattr(self, 'empty_error_labels', []):
                lbl.place_forget()
            self.empty_error_labels = []

            # Validate các trường
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

            # Validate ngày tuyển dụng
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

            # Tách họ tên
            full_name = data.get("Nhân Viên", "").strip()
            name_parts = full_name.split()
            first_name = name_parts[-1] if name_parts else "" 
            last_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else ""  

            # Lấy dep_id từ tên phòng ban
            dep_name = data.get("Phòng Ban", "")
            self.cursor.execute("SELECT dep_id FROM Departments WHERE dep_name = %s", (dep_name,))
            dep_id_result = self.cursor.fetchone()
            dep_id = dep_id_result[0] if dep_id_result else None

            # Lấy emp_id từ bảng Treeview
            original_data = self.tree.item(selected_item)['values']
            emp_id = original_data[1]

            try:
                self.cursor.execute("""
                    UPDATE Employees
                    SET last_name = %s,
                        first_name = %s,
                        dep_id = %s,
                        email = %s,
                        phone_number = %s,
                        hired_date = %s,
                        position = %s,
                        status = %s
                    WHERE emp_id = %s
                """, (
                    last_name,
                    first_name,
                    dep_id,
                    email,
                    phone,
                    hire_date_str,
                    data.get("Chức Vụ", ""),
                    data.get("Trạng Thái", ""),
                    emp_id
                ))
                self.conn.commit()

                # Cập nhật lại dữ liệu trên table
                updated_data = [str(data[f]) for f in fields]
                new_row = original_data[:2] + updated_data
                self.tree.item(selected_item, values=new_row)

                messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhân viên.")
                form.destroy()

            except mysql.connector.Error as e:
                messagebox.showerror("Lỗi", f"Cập nhật thất bại: {e}")
                self.conn.rollback()

        # Nút cập nhật
        save_btn = tk.Button(container, text="Cập Nhật",
                            font=("Times New Roman", 11, "bold"),
                            bg="#4CAF50", fg="white",
                            activebackground="#45a049",
                            padx=25, pady=10,
                            command=save_edited_employee,
                            relief="flat", borderwidth=0)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
        save_btn.configure(width=20)

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

        # Tạo popup xác nhận xóa
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
            except mysql.connector.Error as e:
                self.conn.rollback()
                form.destroy()
                messagebox.showerror("Lỗi", f"Không thể xóa nhân viên.\n")

        def cancel():
            form.destroy()

        # Nút Xóa
        delete_btn = tk.Button(btn_frame, text="Xóa", command=confirm_delete,
                            font=("Times New Roman", 11, "bold"),
                            bg="#f5021b", fg="white", padx=20, pady=8,
                            activebackground="#c0392b", relief="flat")
        delete_btn.grid(row=0, column=0, padx=15)

        # Nút Hủy
        cancel_btn = tk.Button(btn_frame, text="Hủy", command=cancel,
                            font=("Times New Roman", 11, "bold"),
                            bg="#696667", fg="white", padx=20, pady=8,
                            activebackground="#95a5a6", relief="flat")
        cancel_btn.grid(row=0, column=1, padx=15)

    
    # Excel
    def export_to_excel(self):
        messagebox.showinfo("Thông báo", "Chức năng xuất Excel đang được phát triển!")

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
        self.search_entry.insert(0, "")
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
                if len(day_filter) == 4:  # Chỉ năm
                    date_filter = f"{day_filter}-01-01"
                    datetime.strptime(date_filter, "%Y-%m-%d")
                elif len(day_filter) == 7:  # Năm-tháng
                    date_filter = f"{day_filter}-01"
                    datetime.strptime(date_filter, "%Y-%m-%d")
                elif len(day_filter) >= 10:  # Đầy đủ ngày
                    date_filter = day_filter
                    datetime.strptime(date_filter, "%Y-%m-%d")
            except ValueError:
                date_filter = None

        # Xóa dữ liệu cũ trong tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="12345678", database="Face_Recognition")
            cursor = conn.cursor(dictionary=True)

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
            cursor.execute(query, params)
            rows = cursor.fetchall()

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

            cursor.close()
            conn.close()

            if not rows:
                messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu phù hợp!")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {e}")

    # Hiển thị bảng chấm công
    def show_attendance(self):
        # Hủy nội dung cũ nếu có
        if hasattr(self, 'current_content') and self.current_content is not None:
            self.current_content.destroy()

        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"))

        # Khung chứa nút và ô tìm kiếm
        button_frame = tk.Frame(self.current_content, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=2, padx=5)

        buttons_inner_frame = tk.Frame(button_frame, bg=self.bg_color)
        buttons_inner_frame.pack(anchor="center")

        # Load các icon
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")

        reset_img = Image.open(os.path.join(img_dir, "reset.png")).resize((22, 22), Image.Resampling.LANCZOS)
        search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22), Image.Resampling.LANCZOS)
        reset_icon = ImageTk.PhotoImage(reset_img)
        search_icon = ImageTk.PhotoImage(search_img)

        # Nút Reset
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
        self.search_entry.bind("<Return>", self.search)
        
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Nút Tìm kiếm 
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

        self.load_attendance_data()

    # Tải dữ liệu chấm công từ db và hiển thị
    def load_attendance_data(self):
        if not hasattr(self, 'attendance_tree') or not self.attendance_tree.winfo_exists():
            return

        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        try:
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
                emp_id = row[0]
                full_name = f"{row[2]} {row[1]}" 
                date = row[3].strftime("%Y-%m-%d") if row[3] else "N/A"
                check_in = row[4].strftime("%H:%M") if row[4] else "N/A"
                check_out = row[5].strftime("%H:%M") if row[5] else "N/A"
                work_hours = f"{row[6]:.2f}" if row[6] is not None else "0.00"
                overtime_hours = f"{row[7]:.2f}" if row[7] is not None else "0.00"
                
                self.attendance_tree.insert("", "end", values=(idx, emp_id, full_name, date, check_in, check_out, work_hours, overtime_hours))
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

    def search(self, event=None):
        keyword = self.search_var.get().strip().lower()

        # Xóa dữ liệu cũ trên bảng
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        try:
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
                emp_id = row[0]
                full_name = f"{row[2]} {row[1]}"
                date = row[3].strftime("%Y-%m-%d") if row[3] else "N/A"
                check_in = row[4].strftime("%H:%M") if row[4] else "N/A"
                check_out = row[5].strftime("%H:%M") if row[5] else "N/A"
                work_hours = f"{row[6]:.2f}" if row[6] is not None else "0.00"
                overtime_hours = f"{row[7]:.2f}" if row[7] is not None else "0.00"

                # So khớp từ khóa với tên, mã nhân viên, ngày hoặc giờ
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