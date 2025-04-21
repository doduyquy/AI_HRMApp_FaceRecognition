import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
from pathlib import Path
from tkcalendar import DateEntry
import pandas as pd
from tkinter import filedialog
from tkinter import Toplevel, Label, Button
from modules.IT.data_user import DataUser  
from modules.IT.data_face import DataFace
from ui.permission import PermissionApp
from ui.department import DepartmentApp
from ui.face_data import FaceDataApp

class ITApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Tài Khoản IT")
        self.root.geometry("1200x600+50+40")
        self.root.resizable(True, True)
        self.data_user = DataUser()  
        self.data_face = DataFace()  

        # Màu sắc
        self.bg_color = "#fff"  # Nội dung chính
        self.menu_color = "#e9f4f5"  # Sidebar
        self.selected_menu_color = "#a6dcef"  # Hover menu
        self.root.configure(bg=self.bg_color)
        self.error_labels = {}  # Lưu trữ nhãn lỗi cho từng trường

        self.selected_button = None
        self.current_content = None
        self.search_entry = None
        self.current_menu = "Tài khoản"
        self.permission_app = None
        self.department_app = None

        # self.emp_id = "Admin"  # Thay bằng ID người dùng thực
        # self.employee = {  # Thay bằng dữ liệu người dùng thực
        #     "first_name": "",
        #     "last_name": "Admin",
        #     "position": "Admin"
        # }
        self.menu_icons = {}
        self.menu_buttons = {}

        # Tạo sidebar
        SIDEBAR_WIDTH = 200
        self.sidebar = tk.Frame(self.root, width=SIDEBAR_WIDTH, bg=self.menu_color)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Tạo khung nội dung chính
        self.content_frame = tk.Frame(self.root, bg=self.bg_color)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tạo nội dung sidebar
        self.create_sidebar_content()

        # Tạo khu vực nội dung
        self.content_area = tk.Frame(self.content_frame, bg=self.bg_color)
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.on_menu_click("Tài khoản")

    def create_sidebar_content(self):
        # Logo
        logo_f = tk.Frame(self.sidebar, bg=self.menu_color, height=60)
        logo_f.pack(fill=tk.X)
        logo_f.pack_propagate(False)
        logo_l = tk.Label(logo_f, 
                          text="PYTECH", 
                          font=("Times New Roman", 20, "bold"), 
                          bg=self.menu_color, 
                          fg="#0276f7")
        logo_l.pack(pady=10)

        # Khung thông tin người dùng
        profile_f = tk.Frame(self.sidebar, bg=self.menu_color)
        profile_f.pack(fill=tk.X)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        data_f = os.path.join(BASE_DIR, "..", "..", "Data")
        img_path = self.get_employee_image(data_f)

        avatar_l = self.create_avatar(profile_f, img_path)
        avatar_l.pack(pady=10)

        # Tên và chức vụ
        # if self.employee:
        #     full_name = f"{self.employee['last_name']} {self.employee['first_name']}"
        #     position = self.employee['position']
        # else:
        #     full_name = "Tên Người Dùng"
        #     position = "Chức vụ"
        full_name = "Admin"
        position = "Admin"

        name_l = tk.Label(profile_f, 
                          text=full_name, 
                          font=("Times New Roman", 14, "bold"), 
                          fg="#000", 
                          bg=self.menu_color)
        name_l.pack()
        
        position_l = tk.Label(profile_f, 
                              text=position, 
                              font=("Times New Roman", 12), 
                              fg="#4a4949", 
                              bg=self.menu_color)
        position_l.pack()

        # Thanh phân tách
        separator = tk.Frame(self.sidebar, height=1, bg="#2d82b5")
        separator.pack(fill=tk.X, padx=20, pady=3)

        # Menu
        menu_f = tk.Frame(self.sidebar, bg=self.menu_color)
        menu_f.pack(fill=tk.BOTH, expand=True, pady=10)
        menu_f.pack_propagate(False)

        menu_items = [
            ("Tài khoản", "people1.png"),
            ("Phân quyền", "permission1.png"),
            ("Phòng ban", "department1.png"),
            ("Dữ liệu khuôn mặt", "face1.png"),
            ("Đăng xuất", "logout1.png")
        ]

        for item, icon_name in menu_items:
            btn_frame = tk.Frame(menu_f, bg=self.menu_color, width=250, height=50)
            btn_frame.pack(fill=tk.X, pady=5)
            btn_frame.pack_propagate(False)

            icon = self.load_icon(BASE_DIR, icon_name)
            btn = tk.Button(btn_frame, 
                            text=item, 
                            font=("Times New Roman", 12), 
                            fg="#000", 
                            bg=self.menu_color,
                            activebackground=self.selected_menu_color, 
                            activeforeground="#000", 
                            pady=10,
                            bd=0, 
                            anchor="w",
                            width=23,
                            command=lambda menu_item=item: self.on_menu_click(menu_item))
            if icon:
                btn.config(image=icon, compound=tk.LEFT, padx=25)
                self.menu_icons[item] = icon
            else:
                btn.config(padx=15)
            btn.pack(fill=tk.X)
            self.menu_buttons[item] = btn

        # Đặt trạng thái ban đầu cho menu "Tài khoản"
        self.menu_buttons["Tài khoản"].config(bg=self.selected_menu_color)

    def get_employee_image(self, folder):
        if os.path.exists(folder):
            for file_name in os.listdir(folder):
                if file_name == "Admin_Avatar.png":
                    full_path = os.path.join(folder, file_name)
                    return full_path
        return None
    

    def create_avatar(self, frame, img_path):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        default_img_path = os.path.join(BASE_DIR, "..", "img", "admin.jpg")
        try:
            print(f"Attempting to load image from: {img_path}")
            if img_path and os.path.exists(img_path):
                print(f"Image path exists: {img_path}")
                size = (120, 140)
                img = Image.open(img_path)
                print(f"Image loaded successfully: {img_path}")
                img = img.resize(size)
                avatar = ImageTk.PhotoImage(img)
                label = tk.Label(frame, image=avatar, bg=self.menu_color)
                label.image = avatar
                return label
            else:
                print(f"Image path does not exist or is invalid: {img_path}")
                raise FileNotFoundError("Image path is invalid or file does not exist")
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
            print(f"Falling back to default image: {default_img_path}")
            # Kiểm tra xem ảnh mặc định có tồn tại không
            if not os.path.exists(default_img_path):
                print(f"Default image does not exist: {default_img_path}")
                img = Image.new("RGB", (120, 140), color="gray")
            else:
                try:
                    img = Image.open(default_img_path)
                    print(f"Default image loaded successfully: {default_img_path}")
                except Exception as e:
                    print(f"Failed to load default image: {e}")
                    img = Image.new("RGB", (120, 140), color="gray")
            size = (120, 140)
            img = img.resize(size)
            avatar = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=avatar, bg=self.menu_color)
            label.image = avatar
            return label
        except Exception as e:
            print(f"Unexpected error while loading image: {e}")
            img = Image.new("RGB", (120, 140), color="gray")
            size = (120, 140)
            img = img.resize(size)
            avatar = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=avatar, bg=self.menu_color)
            label.image = avatar
            return label

    def load_icon(self, base_dir, icon_name):
        icon_path = os.path.join(base_dir, "..", "img", icon_name)
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path).resize((18, 18))
            return ImageTk.PhotoImage(icon_img)
        print(f"Không tìm thấy icon: {icon_name}")
        return None

    def on_menu_click(self, option):
        # Reset màu của tất cả các nút menu
        for item in self.menu_buttons:
            self.menu_buttons[item].config(bg=self.menu_color)
        
        # Làm nổi bật nút được chọn
        if option in self.menu_buttons:
            self.selected_button = self.menu_buttons[option]
            self.selected_button.config(bg=self.selected_menu_color)
        else:
            print(f"Menu option '{option}' không hợp lệ!")
        
        self.current_menu = option
        
        if option != "Đăng xuất":
            if hasattr(self, 'search_var') and self.search_entry:
                try:
                    if self.search_entry.winfo_exists():
                        self.search_var.set("")
                        self.search_entry.delete(0, tk.END)
                        self.search_entry.insert(0, "Tìm kiếm...")
                        self.search_entry.config(fg="gray")
                except tk.TclError:
                    print("DEBUG: Search entry no longer exists")
        
        self.menu_action(option)
    # def __init__(self, root):
    #     self.root = root
    #     self.root.title("Quản Lý Tài Khoản IT")
    #     self.root.geometry("1200x600+50+40")
    #     self.root.resizable(True, True)
    #     self.data_user = DataUser()  
    #     self.data_face = DataFace()

    #     # Màu sắc
    #     self.bg_color = "#f7f8fa"
    #     self.menu_color = "#fff"
    #     self.selected_menu_color = "#3eaef4"
    #     self.header_color = "#fff"
    #     self.root.configure(bg=self.bg_color)
    #     self.error_labels = {}  # Lưu trữ nhãn lỗi cho từng trường

    #     self.selected_button = None
    #     self.current_content = None
    #     self.search_entry = None
    #    # self.error_label = None 
    #     #self.phone_error_label = None
    #     self.current_menu = "Tài khoản"
    #     self.permission_app = None
    #     self.department_app = None

    #     # Header
    #     self.header_frame = tk.Frame(self.root, bg=self.header_color, height=55)
    #     self.header_frame.pack(side=tk.TOP, fill=tk.X)
    #     self.header_frame.pack_propagate(0)

    #     # Logo
    #     logo_label = tk.Label(self.header_frame, text="PYTECH", font=("Times New Roman", 20, "bold"), fg="#357ae8", bg=self.header_color)
    #     logo_label.pack(side=tk.LEFT, padx=10)

    #     # Avatar
    #     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #     avt_path = os.path.join(BASE_DIR, "..", "img", "admin.jpg")
    #     img = Image.open(avt_path).resize((30, 30))
    #     mask = Image.new("L", img.size, 0)
    #     draw = ImageDraw.Draw(mask)
    #     draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    #     img.putalpha(mask)
    #     self.avt_img = ImageTk.PhotoImage(img)

    #     avt_label = tk.Label(self.header_frame, image=self.avt_img, bg=self.header_color)
    #     avt_label.pack(side=tk.RIGHT, padx=5)

    #     # Admin
    #     user_label = tk.Label(self.header_frame, text="Admin", font=('Times New Roman', 13), fg="black", bg=self.header_color)
    #     user_label.pack(side=tk.RIGHT, padx=10)

    #     # Menu
    #     self.menu_frame = tk.Frame(self.root, bg=self.menu_color, width=200)
    #     self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

    #      #Danh sách menu và icon
    #     menu_items = [
    #         ("Tài khoản", "people.png"),
    #         ("Phân quyền", "permission.png"),
    #         ("Phòng ban", "department.png"),
    #         ("Dữ liệu khuôn mặt", "face.png"),
    #         ("Đăng xuất", "logout.png")
    #     ]
    #     self.menu_buttons = {}
    #     self.menu_icons = {}

    #     for item, icon_name in menu_items:
    #         icon_path = os.path.join(BASE_DIR, "..", "img", icon_name)
    #         if os.path.exists(icon_path):
    #             icon_img = Image.open(icon_path).resize((15, 15))
    #             icon = ImageTk.PhotoImage(icon_img)
    #         else:
    #             icon = ImageTk.PhotoImage(Image.new("RGBA", (20, 20), (0, 0, 0, 0)))
    #             print(f"Không tìm thấy icon: {icon_name}")

    #         self.menu_icons[item] = icon
    #         btn = tk.Button(self.menu_frame,
    #                         text=item,
    #                         font=("Times New Roman", 11),
    #                         bg=self.menu_color,
    #                         fg="#000",
    #                         bd=0,
    #                         command=lambda x=item: self.on_menu_click(x),
    #                         image=self.menu_icons[item],
    #                         compound=tk.LEFT,
    #                         anchor="w",
    #                         padx=10,
    #                         pady=10,
    #                         width=180)
    #         btn.pack(fill=tk.X, pady=0)
    #         self.menu_buttons[item] = btn

    #     # Khung nội dung
    #     self.content_frame = tk.Frame(self.root, bg=self.bg_color)
    #     self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    #     self.on_menu_click("Tài khoản")

    
    # def on_menu_click(self, option):
    #     if self.selected_button:
    #         self.selected_button.config(bg=self.menu_color)
    #     if option in self.menu_buttons:
    #         self.selected_button = self.menu_buttons[option]
    #         self.selected_button.config(bg=self.selected_menu_color)
    #     else:
    #         print(f"Menu option '{option}' không hợp lệ!")
        
    #     self.current_menu = option
        
    #     if option != "Đăng xuất":
    #         if hasattr(self, 'search_var') and self.search_entry:
    #             try:
    #                 if self.search_entry.winfo_exists():
    #                     self.search_var.set("")
    #                     self.search_entry.delete(0, tk.END)
    #                     self.search_entry.insert(0, "Tìm kiếm...")
    #                     self.search_entry.config(fg="gray")
    #             except tk.TclError:
    #                 print("DEBUG: Search entry no longer exists")
        
    #     self.menu_action(option)

    def clear_content(self):
        print("DEBUG: Clearing content")  # Debug to confirm cleanup
        if self.permission_app:
            self.permission_app.destroy()
            self.permission_app = None
        if self.department_app:
            self.department_app.destroy()
            self.department_app = None
        if hasattr(self, 'facedata_app') and self.facedata_app:
            self.facedata_app.destroy()
            self.facedata_app = None
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None

    
    def menu_action(self, item):
        self.clear_content()
        if item == "Tài khoản":
            self.show_account_list()
        elif item == "Phân quyền":
            self.show_permission()
        elif item == "Phòng ban":
            self.show_department()
        elif item == "Dữ liệu khuôn mặt":
            self.show_face_data()
        elif item == "Đăng xuất":
            self.sign_out()

    def show_account_list(self):
        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        # Thanh công cụ
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
            command=self.show_add_account,
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
            command=self.edit_account,
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
            command=self.show_delete_account,
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
            command=self.reset_account_list, 
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#7d8e96")
        reset_button.image = reset_icon 
        reset_button.pack(side=tk.LEFT, padx=3)

        # Frame chứa ô tìm kiếm
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
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Nút Tìm kiếm
        search_button = tk.Button(
            search_frame,
            image=search_icon,
            command=self.search_account,
            bg="white",
            bd=0,
            relief="flat",
            activebackground="#fff",
            width=20,
            height=25
        )
        search_button.image = search_icon
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

        # Cấu hình Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Times New Roman", 11, "bold"), background="#9fd7f9", foreground="#000", relief="flat", borderwidth=0, padding=5)
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#e5e5e5")], foreground=[("selected", "black")])

        # Danh sách cột
        columns = ("STT", "Tên tài khoản", "Tên Nhân Viên", "Email", "Quyền", "Trạng Thái")
        self.tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("STT", width=50, anchor="center")
        self.tree.column("Tên tài khoản", width=100, anchor="center")
        self.tree.column("Tên Nhân Viên", width=200, anchor="w")
        self.tree.column("Email", width=200, anchor="w")
        self.tree.column("Quyền", width=150, anchor="center")
        self.tree.column("Trạng Thái", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_account_data()

    def load_account_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.data_user.load_accounts()  # Use function from db_queries
        for idx, row in enumerate(rows, 1):
            emp_id = row['emp_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            email = row['email'] if row['email'] else "N/A"
            role = row['role_name'] if row['role_name'] else "Chưa phân quyền"
            status = row['status']
            self.tree.insert("", "end", values=(idx, emp_id, full_name, email, role, status))
        if not rows:
            messagebox.showinfo("Thông báo", "Không có tài khoản nào trong cơ sở dữ liệu!")

    def search_account(self):
        search_term = self.search_var.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.data_user.search_accounts(search_term)  # Use function from db_queries
        for idx, row in enumerate(rows, 1):
            emp_id = row['emp_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            email = row['email'] if row['email'] else "N/A"
            role = row['role_name'] if row['role_name'] else "Chưa phân quyền"
            status = row['status']
            self.tree.insert("", "end", values=(idx, emp_id, full_name, email, role, status))
        if not rows:
            messagebox.showinfo("Thông báo", "Không tìm thấy tài khoản nào!")

    def reset_account_list(self):
        self.search_var.set("")
        self.search_entry.config(fg="gray")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm...")
        self.load_account_data()

    def _clear_placeholder(self, event=None):
        if self.search_entry.get() == "Tìm kiếm...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def _restore_placeholder(self, event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Tìm kiếm...")
            self.search_entry.config(fg="gray")

    def reset_entry_style(self, entry):
        entry.configure(style="Custom.TEntry")

    def show_error_below(self, field, message, entry):
        # Xóa nhãn lỗi cũ nếu có
        if field in self.error_labels:
            self.error_labels[field].destroy()
        # Tạo nhãn lỗi mới
        error_label = tk.Label(entry.master, text=message, font=("Times New Roman", 10), fg="red", bg="#ffffff")
        error_label.pack(side=tk.LEFT, padx=5)
        self.error_labels[field] = error_label
        # Chỉ áp dụng style nếu entry là widget của ttk
        if isinstance(entry, (ttk.Entry, ttk.Combobox, ttk.Checkbutton, DateEntry)):
            entry.configure(style="Error.TEntry")
            
    def show_add_account(self):
        form = tk.Toplevel(self.root)
        form.title("Thêm Tài Khoản Mới")

        window_width = 700
        window_height = 700
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form.configure(bg="#ffffff")
        form.grab_set()

        # Style cho tất cả các loại widget
        style = ttk.Style()
        style.configure("Custom.TCheckbutton",
                        background="#ffffff",
                        font=("Times New Roman", 10),
                        borderwidth=0,
                        relief="flat")

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

        style.configure("Custom.TEntry",
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        font=("Times New Roman", 11),
                        foreground="black",
                        fieldbackground="white")
                        #bordercolor="black")

        style.configure("Error.TEntry",
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        font=("Times New Roman", 11),
                        foreground="black",
                        fieldbackground="white",
                        bordercolor="red")

        tk.Label(form, text="Nhập Thông Tin Tài Khoản",
                 font=("Times New Roman", 16, "bold"),
                 bg="#ffffff", fg="#14a0f7").pack(pady=10)

        fields = [
            ("Họ:", "last_name"),
            ("Tên:", "first_name"),
            ("Email:", "email"),
            ("Số điện thoại:", "phone_number"),
            ("Ngày tuyển dụng:", "hired_date"),
            ("Tên đăng nhập:", "user_name"),
            ("Mật khẩu:", "password"),
        ]

        entries = {}

        def toggle_password():
            show = "" if show_password_var.get() else "*"
            entries["password"].config(show=show)

        for label_text, field in fields:
            frame = tk.Frame(form, bg="#ffffff")
            frame.pack(fill=tk.X, padx=20, pady=8)

            tk.Label(frame, text=label_text, font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)

            if field == "hired_date":
                entry = DateEntry(frame, font=("Times New Roman", 11),
                                  state="readonly",
                                  date_pattern="yyyy-mm-dd",
                                  width=29,
                                  background='white',
                                  foreground='black',
                                  borderwidth=1,
                                  relief="solid",
                                  style="Custom.DateEntry")
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            elif field == "password":
                pw_frame = tk.Frame(frame, bg="#ffffff")
                pw_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

                entry = ttk.Entry(pw_frame, font=("Times New Roman", 11), width=28, show="*", style="Custom.TEntry")
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                show_password_var = tk.BooleanVar()
                show_password_cb = ttk.Checkbutton(
                    pw_frame,
                    text="Hiện",
                    variable=show_password_var,
                    command=toggle_password,
                    style="Custom.TCheckbutton"
                )
                show_password_cb.pack(side=tk.RIGHT)

            else:
                entry = ttk.Entry(frame, font=("Times New Roman", 11), width=30, style="Custom.TEntry")
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            entries[field] = entry

        # Phòng ban
        dep_frame = tk.Frame(form, bg="#ffffff")
        dep_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(dep_frame, text="Phòng ban:", font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        dep_var = tk.StringVar()
        departments = self.data_user.fetch_departments()
        dep_combo = ttk.Combobox(dep_frame, textvariable=dep_var, values=[dep[1] for dep in departments], state="readonly", style="Custom.TCombobox")
        dep_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Trạng thái
        status_frame = tk.Frame(form, bg="#ffffff")
        status_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(status_frame, text="Trạng Thái:", font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        status_var = tk.StringVar(value="Đang làm việc")
        status_combo = ttk.Combobox(status_frame, textvariable=status_var, values=["Đang làm việc", "Đã nghỉ"], state="readonly", style="Custom.TCombobox")
        status_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Quyền
        role_frame = tk.Frame(form, bg="#ffffff")
        role_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(role_frame, text="Quyền:", font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        role_var = tk.StringVar()
        roles = self.data_user.fetch_roles()
        role_combo = ttk.Combobox(role_frame, textvariable=role_var, values=[role[1] for role in roles], state="readonly", style="Custom.TCombobox")
        role_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def handle_save():
            # Xóa tất cả nhãn lỗi cũ
            for field in self.error_labels:
                self.error_labels[field].destroy()
            self.error_labels.clear()

            # Reset style cho các trường nhập liệu
            for entry in entries.values():
                self.reset_entry_style(entry)

            # Lấy giá trị từ các widget
            last_name = entries["last_name"].get().strip()
            first_name = entries["first_name"].get().strip()
            email = entries["email"].get().strip()
            phone_number = entries["phone_number"].get().strip()
            hired_date = entries["hired_date"].get().strip()
            user_name = entries["user_name"].get().strip()
            password = entries["password"].get().strip()
            dep_name = dep_var.get().strip()
            status = status_var.get().strip()
            role_name = role_var.get().strip()
            position = dep_name  # Đặt position bằng dep_name

            success, result = self.data_user.save_new_account(
                last_name, first_name, email, phone_number, hired_date, position, status, user_name, password, dep_name, role_name
            )
            if success:
                messagebox.showinfo("Thành công", result)
                form.destroy()
                self.load_account_data()
            else:
                if isinstance(result, dict) and 'general' in result:
                    messagebox.showerror("Lỗi", result['general'])
                elif isinstance(result, dict):
                    for field, message in result.items():
                        widget = entries.get(field, dep_combo if field == 'dep_name' else role_combo if field == 'role_name' else save_button)
                        self.show_error_below(field, message, widget)
                else:
                    messagebox.showerror("Lỗi", result)
        # Nút lưu
        save_button = tk.Button(form, text="Lưu", command=handle_save,
                                bg="#4CAF50", fg="white",
                                font=("Times New Roman", 11), width=10, relief="flat")
        save_button.pack(pady=20)
        
    def edit_account(self):
    # Kiểm tra xem có tài khoản nào được chọn trong Treeview không
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản để sửa!")
            return

    # Lấy emp_id từ tài khoản được chọn (cột "Tên tài khoản" là emp_id)
        emp_id = self.tree.item(selected_item)['values'][1]
        self.show_edit_account(emp_id)  

    def show_edit_account(self, account_id):
        form = tk.Toplevel(self.root)
        form.title("Chỉnh Sửa Tài Khoản")

        window_width = 700
        window_height = 700
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form.configure(bg="#ffffff")
        form.grab_set()

        # Style cho tất cả các loại widget
        style = ttk.Style()
        style.configure("Custom.TCheckbutton",
                        background="#ffffff",
                        font=("Times New Roman", 10),
                        borderwidth=0,
                        relief="flat")

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

        style.configure("Custom.TEntry",
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        font=("Times New Roman", 11),
                        foreground="black",
                        fieldbackground="white")

        style.configure("Error.TEntry",
                        padding=6,
                        relief="solid",
                        borderwidth=1,
                        font=("Times New Roman", 11),
                        foreground="black",
                        fieldbackground="white",
                        bordercolor="red")

        tk.Label(form, text="Chỉnh Sửa Thông Tin Tài Khoản",
                 font=("Times New Roman", 16, "bold"),
                 bg="#ffffff", fg="#14a0f7").pack(pady=10)

        # Lấy thông tin tài khoản từ cơ sở dữ liệu
        account = self.data_user.fetch_account_by_id(account_id)
        if not account:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản!")
            form.destroy()
            return

        last_name_db, first_name_db, dep_id_db, email_db, phone_number_db, hired_date_db, position_db, status_db, user_name_db, password_db, role_id_db = account

        fields = [
            ("Họ:", "last_name", last_name_db),
            ("Tên:", "first_name", first_name_db),
            ("Email:", "email", email_db),
            ("Số điện thoại:", "phone_number", phone_number_db or ""),
            ("Ngày tuyển dụng:", "hired_date", hired_date_db),
            ("Vị trí:", "position", position_db or ""),
            ("Tên đăng nhập:", "user_name", user_name_db),
            ("Mật khẩu:", "password", ""),
        ]

        entries = {}

        def toggle_password():
            show = "" if show_password_var.get() else "*"
            entries["password"].config(show=show)

        for label_text, field, value in fields:
            frame = tk.Frame(form, bg="#ffffff")
            frame.pack(fill=tk.X, padx=20, pady=8)

            tk.Label(frame, text=label_text, font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)

            if field == "hired_date":
                entry = DateEntry(frame, font=("Times New Roman", 11),
                                  state="readonly",
                                  date_pattern="yyyy-mm-dd",
                                  width=29,
                                  background='white',
                                  foreground='black',
                                  borderwidth=1,
                                  relief="solid",
                                  style="Custom.DateEntry")
                if value:
                    entry.set_date(value)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            elif field == "password":
                pw_frame = tk.Frame(frame, bg="#ffffff")
                pw_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

                entry = ttk.Entry(pw_frame, font=("Times New Roman", 11), width=28, show="*", style="Custom.TEntry")
                entry.insert(0, value)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                show_password_var = tk.BooleanVar()
                show_password_cb = ttk.Checkbutton(
                    pw_frame,
                    text="Hiện",
                    variable=show_password_var,
                    command=toggle_password,
                    style="Custom.TCheckbutton"
                )
                show_password_cb.pack(side=tk.RIGHT)

            else:
                entry = ttk.Entry(frame, font=("Times New Roman", 11), width=30, style="Custom.TEntry")
                entry.insert(0, value)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            entries[field] = entry

        # Phòng ban
        dep_frame = tk.Frame(form, bg="#ffffff")
        dep_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(dep_frame, text="Phòng ban:", font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        dep_var = tk.StringVar()
        departments = self.data_user.fetch_departments()
        dep_combo = ttk.Combobox(dep_frame, textvariable=dep_var, values=[dep[1] for dep in departments], state="readonly", style="Custom.TCombobox")
        # Điền sẵn phòng ban
        for d_id, d_name in departments:
            if d_id == dep_id_db:
                dep_var.set(d_name)
                break
        dep_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Trạng thái
        status_frame = tk.Frame(form, bg="#ffffff")
        status_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(status_frame, text="Trạng Thái:", font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(status_frame, textvariable=status_var, values=["Đang làm việc", "Đã nghỉ"], state="readonly", style="Custom.TCombobox")
        status_var.set("Đang làm việc" if status_db == 1 else "Đã nghỉ")
        status_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Quyền
        role_frame = tk.Frame(form, bg="#ffffff")
        role_frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(role_frame, text="Quyền:", font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        role_var = tk.StringVar()
        roles = self.data_user.fetch_roles()
        role_combo = ttk.Combobox(role_frame, textvariable=role_var, values=[role[1] for role in roles], state="readonly", style="Custom.TCombobox")
        # Điền sẵn quyền
        for r_id, r_name in roles:
            if r_id == role_id_db:
                role_var.set(r_name)
                break
        role_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        
        def handle_save():
           
            # Xóa tất cả nhãn lỗi cũ
            for field in self.error_labels:
                self.error_labels[field].destroy()
            self.error_labels.clear()

            # Reset style cho các trường nhập liệu
            for entry in entries.values():
                self.reset_entry_style(entry)

            # Lấy giá trị từ các widget
            last_name = entries["last_name"].get().strip()
            first_name = entries["first_name"].get().strip()
            email = entries["email"].get().strip()
            phone_number = entries["phone_number"].get().strip()
            hired_date = entries["hired_date"].get().strip()
            position = dep_var.get().strip()  # Đồng bộ position với dep_name
            user_name = entries["user_name"].get().strip()
            password = entries["password"].get().strip()
            dep_name = dep_var.get().strip()
            status = status_var.get().strip()
            role_name = role_var.get().strip()

            # Gọi update_account thay vì save_new_account
            success, result = self.data_user.update_account(
                account_id, last_name, first_name, email, phone_number, hired_date, position, status, user_name, password, dep_name, role_name, email_db, user_name_db
            )
            if success:
                messagebox.showinfo("Thành công", result)
                form.destroy()
                self.load_account_data()
            else:
                if isinstance(result, dict) and 'general' in result:
                    messagebox.showerror("Lỗi", result['general'])
                elif isinstance(result, dict):
                    for field, message in result.items():
                        widget = entries.get(field, dep_combo if field == 'dep_name' else role_combo if field == 'role_name' else save_button)
                        self.show_error_below(field, message, widget)
                else:
                    messagebox.showerror("Lỗi", result)

        # Nút lưu
        save_button = tk.Button(form, text="Lưu", command=handle_save,
                                bg="#4CAF50", fg="white",
                                font=("Times New Roman", 11), width=10, relief="flat")
        save_button.pack(pady=20)

    
    def show_delete_account(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một tài khoản để xóa!")
            return

        emp_id = self.tree.item(selected_item)['values'][1]
        full_name = self.tree.item(selected_item)['values'][2]

        # Tạo hộp thoại tùy chỉnh với self.root làm master
        confirm_dialog = Toplevel(self.root)
        confirm_dialog.title("Xác nhận")
        confirm_dialog.geometry("300x150")
        confirm_dialog.resizable(False, False)
        
        # Căn giữa hộp thoại
        confirm_dialog.transient(self.root)  # Liên kết với self.root
        confirm_dialog.grab_set()  # Chặn tương tác với cửa sổ khác

        # Tính toán vị trí để căn giữa
        confirm_dialog.update_idletasks()  # Cập nhật kích thước thực tế của hộp thoại
        dialog_width = confirm_dialog.winfo_width()
        dialog_height = confirm_dialog.winfo_height()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        
        # Tính toán tọa độ x, y để căn giữa
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2
        
        # Đặt vị trí cho hộp thoại
        confirm_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Nhãn hiển thị thông điệp
        label = Label(confirm_dialog, text=f"Bạn có chắc chắn muốn xóa tài khoản {full_name}?", wraplength=250)
        label.pack(pady=20)

        # Hàm xử lý khi nhấn "Có"
        def confirm_delete():
            success, message = self.data_user.delete_account(emp_id)
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_account_data()
            else:
                messagebox.showerror("Lỗi", message)
            confirm_dialog.destroy()

        # Hàm xử lý khi nhấn "Không"
        def cancel_delete():
            confirm_dialog.destroy()

        # Tạo các nút "Có" và "Không"
        btn_yes = Button(confirm_dialog, text="Có", command=confirm_delete, width=10, 
                        bg="#4CAF50", fg="white", font=("Times New Roman", 11), relief="flat")
        btn_yes.pack(side="left", padx=20, pady=10)

        btn_no = Button(confirm_dialog, text="Không", command=cancel_delete, width=10,
                        bg="#f44336", fg="white", font=("Times New Roman", 11), relief="flat")
        btn_no.pack(side="right", padx=20, pady=10)
        
   

    def export_to_excel(self):
        # Lấy dữ liệu từ Treeview
        columns = [self.tree.heading(col)['text'] for col in self.tree['columns']]
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            data.append(values)

        if not data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất sang Excel!")
            return

        # Tạo DataFrame từ dữ liệu
        df = pd.DataFrame(data, columns=columns)

        # Đặt tên file mặc định
        default_filename = "DanhSachTaiKhoan.xlsx"

        # Mở hộp thoại để chọn nơi lưu file với tên file mặc định
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,  # Tên file mặc định
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Chọn nơi lưu file Excel"
        )

        # Kiểm tra nếu người dùng không chọn file
        if not file_path:
            return

        try:
            # Xuất DataFrame sang file Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            messagebox.showinfo("Thành công", f"Dữ liệu đã được xuất sang {file_path}!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi xuất file: {str(e)}")

    def sign_out(self):
        if messagebox.askokcancel("Đăng Xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            self.root.destroy()

    
    def show_permission(self):
        self.clear_content()
        self.permission_app = PermissionApp(self)
        self.current_content = self.permission_app.content_frame
        
  
    
    def show_department(self):
        print("DEBUG: show_department called")
        self.clear_content()
        self.department_app = DepartmentApp(self)
        self.current_content = self.department_app.content_frame
        print("DEBUG: DepartmentApp initialized")
        
        
    def show_face_data(self):
        print("DEBUG: Showing face data")
        self.clear_content()
        self.facedata_app = FaceDataApp(self)
        self.current_content = self.facedata_app.content_frame
        