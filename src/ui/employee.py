import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import mysql.connector

class HRMApp:
    def __init__(self, root, emp_id):
        self.root = root
        self.root.title("Nhân Viên")
        self.root.geometry("1200x550+50+50")
        
        self.emp_id = str(emp_id)
        self.select_btn = None
        self.menu_btn = {}
        self.menu_icons = {}
        self.employee = None
        self.departments = {}
        self.conn = None
        self.cursor = None

        self.setup_database()
        self.load_data()
        self.create_ui()

    def setup_database(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="Face_Recognition"
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Không kết nối được: {err}")

    def load_data(self):
        if not self.conn or not self.cursor:
            return
        try:
            # Tải danh sách phòng ban từ bảng Departments
            self.cursor.execute("SELECT dep_id, dep_name FROM Departments")
            result = self.cursor.fetchall()
            for row in result:
                self.departments[row['dep_id']] = row['dep_name']
            
            # Tải thông tin nhân viên từ bảng Employees
            self.cursor.execute("SELECT * FROM Employees WHERE emp_id = %s", (self.emp_id,))
            self.employee = self.cursor.fetchone()
            if not self.employee:
                print(f"Không tìm thấy nhân viên với emp_id: {self.emp_id}")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Lỗi: {err}")

    def create_ui(self):
        # Tạo sidebar
        self.sidebar = tk.Frame(self.root, width=250, bg="#e9f4f5")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Tạo khung chính
        self.main_f = tk.Frame(self.root, bg="#fff")
        self.main_f.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tạo sidebar
        self.create_sidebar_content()

        # Tạo khu vực nội dung chính
        self.content_area = tk.Frame(self.main_f, bg="#fff")
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.on_menu_click("Hồ sơ")

    def create_sidebar_content(self):
        # Khung logo
        logo_f = tk.Frame(self.sidebar, bg="#e9f4f5", height=60)
        logo_f.pack(fill=tk.X)
        logo_l = tk.Label(logo_f, 
                              text="PYTECH", 
                              font=("Times New Roman", 20, "bold"), 
                              bg="#e9f4f5", 
                              fg="#0276f7")
        logo_l.pack(pady=10)

        # Khung ảnh và thông tin nhân viên
        profile_f = tk.Frame(self.sidebar, bg="#e9f4f5")
        profile_f.pack(fill=tk.X)

        # Đường dẫn thư mục Data
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        data_f = os.path.join(BASE_DIR, "..", "..", "Data")
        img_path = self.get_employee_image(data_f)

        # Tạo avatar 
        avatar_l = self.create_avatar(profile_f, img_path)
        avatar_l.pack(pady=10)

        # Hiển thị tên và chức vụ
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

        # Dòng phân cách
        separator = tk.Frame(self.sidebar, height=1, bg="#2d82b5")
        separator.pack(fill=tk.X, padx=20, pady=3)

        # Khung menu
        menu_f = tk.Frame(self.sidebar, bg="#e9f4f5")
        menu_f.pack(fill=tk.BOTH, expand=True, pady=10)

        # Danh sách mục menu
        menu_items = [
            ("Hồ sơ", "profile.png"),
            ("Chấm công", "check.png"),
            ("Xem bảng lương", "salary.png"),
            ("Đăng xuất", "logout.png")
        ]

        # Tạo các nút menu
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

    def get_employee_image(self, folder):
        if os.path.exists(folder):
            for file_name in os.listdir(folder):
                if file_name.startswith(self.emp_id + "_"):
                    return os.path.join(folder, file_name)
        return None

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

    def load_icon(self, base_dir, icon_name):
        icon_path = os.path.join(base_dir, "..", "img", icon_name)
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path).resize((18, 18))
            return ImageTk.PhotoImage(icon_img)
        print(f"Không tìm thấy icon: {icon_name}")
        return None

    def on_menu_click(self, option):
        # Thay đổi màu nút được chọn
        if self.select_btn:
            self.select_btn.config(bg="#e9f4f5")
        self.select_btn = self.menu_btn[option]
        self.select_btn.config(bg="#a6dcef")

        # Xóa nội dung cũ trong content_area
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Hiển thị nội dung tương ứng
        if option == "Hồ sơ":
            self.show_profile()
        elif option == "Chấm công":
            self.show_attendance()
        elif option == "Xem bảng lương":
            self.show_salary()
        elif option == "Đăng xuất":
            self.logout()

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

        # Phần thông tin chi tiết
        left_s = tk.Frame(section_f, bg="#fff")
        left_s.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        fields = [
            ("Họ và tên", f"{self.employee.get('last_name', 'N/A')} {self.employee.get('first_name', 'N/A')}"),
            ("Mã nhân viên", self.employee.get('emp_id', 'N/A')),
            ("Email", self.employee.get('email', 'N/A')),
            ("Số điện thoại", self.employee.get('phone_number', 'N/A')),
            ("Chức vụ", self.employee.get('position', 'N/A')),
            ("Phòng ban", self.departments.get(self.employee.get('dep_id'), 'N/A') if self.employee else 'N/A'),
            ("Ngày làm việc", self.employee.get('hired_date', 'N/A'))
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

        # Phần ảnh hồ sơ
        right_s = tk.Frame(section_f, bg="#fff")
        right_s.grid(row=0, column=1, sticky="n", pady=10)
        self.display_profile_image(right_s)

    def display_profile_image(self, frame):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        data = os.path.join(BASE_DIR, "..", "..", "Data")
        img_path = self.get_employee_image(data)
        if not img_path:
            img_path = os.path.join(BASE_DIR, "..", "img", "user.jpg")

        try:
            img = Image.open(img_path).resize((180, 180))  # Không bo góc
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

        # Load ảnh
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")
        search_img_path = os.path.join(img_dir, "search.png")
        reset_img_path = os.path.join(img_dir, "reset.png")

        # Ktra và load ảnh Search
        if os.path.exists(search_img_path):
            search_img = Image.open(search_img_path).resize((16, 16), Image.Resampling.LANCZOS)
            self.search_icon = ImageTk.PhotoImage(search_img)
        else:
            self.search_icon = None

        # Ktra và load ảnh Reset
        if os.path.exists(reset_img_path):
            reset_img = Image.open(reset_img_path).resize((22, 22), Image.Resampling.LANCZOS)
            self.reset_icon = ImageTk.PhotoImage(reset_img)
        else:
            self.reset_icon = None

        # Frame chứa ô tìm kiếm và nút tìm kiếm
        search_frame = tk.Frame(inner_f, 
                                bg="white", 
                                relief="flat", 
                                highlightthickness=1, 
                                highlightbackground="#4c84f5")
        search_frame.pack(side=tk.LEFT, padx=10, ipady=4)

        # Text
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

        # Hình ảnh
        search_button = tk.Button(
            search_frame,
            image=self.search_icon if self.search_icon else None,
            command=self.search,  
            bg="white",
            bd=0,
            relief="flat",
            activebackground="#fff",
            width=20, 
            height=25,
        )
        if self.search_icon:
            search_button.image = self.search_icon
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

        # Nút Reset
        reset_button = tk.Button(
            inner_f,
            image=self.reset_icon,
            compound=tk.TOP,
            command=self.reset_search,
            bg="#fff",
            bd=0,
            width=50,
            height=50,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#e8eaeb"
        )
        if self.reset_icon:
            reset_button.image = self.reset_icon
        reset_button.pack(side=tk.LEFT, padx=10)

        # Frame chứa bảng dữ liệu
        table_frame = tk.Frame(attendance_f, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Tạo Style
        style = ttk.Style()
        style.theme_use("default") 

        # Cấu hình layout cho tiêu đề
        style.layout("Treeview.Heading",
                    [('Treeheading.cell', {'sticky': 'nswe'}),
                    ('Treeheading.border', {'sticky': 'nswe', 'children': [
                        ('Treeheading.padding', {'sticky': 'nswe', 'children': [
                            ('Treeheading.image', {'side': 'right', 'sticky': ''}),
                            ('Treeheading.text', {'sticky': 'we'})]})]})])

        # Cấu hình tiêu đề
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

        # Màu khi chọn dòng
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

    def load_attendance_data(self, month=None, year=None):
        if not self.conn or not self.cursor:
            self.setup_database()
            if not self.conn:
                return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            query = """
                SELECT DATE_FORMAT(date, '%Y-%m-%d') as date, 
                       TIME_FORMAT(check_in, '%H:%i') as check_in, 
                       TIME_FORMAT(check_out, '%H:%i') as check_out, 
                       work_hours, overtime_hours 
                FROM Attendance WHERE emp_id = %s
            """
            params = [self.emp_id]

            if month:
                query += " AND MONTH(date) = %s"
                params.append(month)
            if year:
                query += " AND YEAR(date) = %s"
                params.append(year)

            query += " ORDER BY date DESC"
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
            messagebox.showerror("Database Error", f"Lỗi: {err}")

    def _clear_placeholder(self, event):
        if self.search_entry.get() == "Tìm kiếm...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def _restore_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Tìm kiếm...")
            self.search_entry.config(fg="gray")

    def load_attendance_data(self, month=None, year=None):
        if not self.conn or not self.cursor:
            self.setup_database()
            if not self.conn:
                return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            query = """
                SELECT DATE_FORMAT(date, '%Y-%m-%d') as date, 
                    TIME_FORMAT(check_in, '%H:%i') as check_in, 
                    TIME_FORMAT(check_out, '%H:%i') as check_out, 
                    work_hours, overtime_hours 
                FROM Attendance WHERE emp_id = %s
            """
            params = [self.emp_id]

            if month:
                query += " AND MONTH(date) = %s"
                params.append(month)
            if year:
                query += " AND YEAR(date) = %s"
                params.append(year)

            query += " ORDER BY date DESC"
            self.cursor.execute(query, tuple(params))
            rows = self.cursor.fetchall()

            # Lưu dữ liệu vào self.attendance_data
            self.attendance_data = []
            for row in rows:
                values = (
                    row['date'],
                    row['check_in'],
                    row['check_out'] if row['check_out'] else "Chưa check-out",
                    str(row['work_hours']) if row['work_hours'] else "0",
                    str(row['overtime_hours']) if row['overtime_hours'] else "0"
                )
                self.attendance_data.append(values)
                self.tree.insert("", "end", values=values)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Lỗi: {err}")

    def search(self, event=None):
        query = self.search_var.get().lower()
        if query == "tìm kiếm...":
            query = ""

        # Xóa dữ liệu cũ trên tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Lọc lại dữ liệu từ self.attendance_data
        if hasattr(self, 'attendance_data'):  # Kiểm tra xem self.attendance_data có tồn tại không
            for row in self.attendance_data:
                if any(query in str(field).lower() for field in row):
                    self.tree.insert('', tk.END, values=row)
        else:
            # Nếu không có dữ liệu, tải lại từ cơ sở dữ liệu
            self.load_attendance_data()
            for row in self.attendance_data:
                if any(query in str(field).lower() for field in row):
                    self.tree.insert('', tk.END, values=row)
    
    def reset_search(self):
        """Hàm xử lý khi nhấn nút Reset"""
        # Xóa nội dung ô tìm kiếm
        self.search_var.set("")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm...")
        self.search_entry.config(fg="gray")
        # Tải lại toàn bộ dữ liệu
        self.load_attendance_data()


    def filter_by_date(self, event):
        selected_month = self.month_filter.get()
        selected_year = self.year_filter.get()
        
        month = int(selected_month) if selected_month.isdigit() else None
        year = int(selected_year) if selected_year.isdigit() else None
        self.load_attendance_data(month, year)

    def show_salary(self):
        salary_frame = tk.Frame(self.content_area, bg="#f5f7fa")
        salary_frame.pack(fill=tk.BOTH, expand=True)

        title_l = tk.Label(salary_frame, text="Thông tin lương", 
                               font=("Times New Roman", 18, "bold"), fg="#333333", bg="#f5f7fa")
        title_l.pack(anchor="w", pady=(0, 20))

        placeholder = tk.Label(salary_frame, text="Thông tin lương sẽ hiển thị ở đây", 
                                    font=("Times New Roman", 12), fg="#333333", bg="#f5f7fa")
        placeholder.pack(pady=50)

    def logout(self):
        if messagebox.askokcancel("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            if self.conn and self.conn.is_connected():
                self.cursor.close()
                self.conn.close()
            self.root.destroy()

def main(emp_id=""):
    root = tk.Tk()
    app = HRMApp(root, emp_id)
    root.mainloop()

# if __name__ == "__main__":
#     main(4)