import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from PIL import Image, ImageTk, ImageDraw
import os

class ITApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Tài Khoản IT")
        self.root.geometry("1000x550+150+60")
        self.root.resizable(True, True)

        # Màu sắc
        self.bg_color = "#f0f2f5"
        self.menu_color = "#84b5f5"
        self.selected_menu_color = "#5399f5"
        self.header_color = "#d5e6f2"
        self.root.configure(bg=self.bg_color)

        self.selected_button = None
        self.current_content = None

        # BASE_DIR
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Header
        self.header_frame = tk.Frame(self.root, bg=self.header_color, height=50)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        # Logo (dạng text)
        logo_label = tk.Label(self.header_frame, text="PYTECH", font=("Times New Roman", 20, "bold"), fg="#357ae8", bg=self.header_color)
        logo_label.pack(side=tk.LEFT, padx=10)

        # Avatar
        avt_path = os.path.join(BASE_DIR, "..", "img", "admin.jpg")
        img = Image.open(avt_path).resize((25, 25))
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
        img.putalpha(mask)
        self.avt_img = ImageTk.PhotoImage(img)

        avt_label = tk.Label(self.header_frame, image=self.avt_img, bg=self.header_color)
        avt_label.pack(side=tk.RIGHT, padx=5)

        # Admin
        user_label = tk.Label(self.header_frame, text="Admin", font=('Times New Roman', 10), fg="black", bg=self.header_color)
        user_label.pack(side=tk.RIGHT, padx=10)

        # Menu
        self.menu_frame = tk.Frame(self.root, bg=self.menu_color, width=200)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Danh sách menu và icon
        menu_items = [
            ("Danh Sách TK", "people.png"),
            ("Thêm", "add-user.png"),
            ("Sửa", "edit.png"),
            ("Xóa", "delete.png"),
            ("Đăng xuất", "logout.png")
        ]
        self.menu_buttons = {}
        self.menu_icons = {}

        for item, icon_name in menu_items:
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
                            width=120)
            btn.pack(fill=tk.X, pady=0)
            self.menu_buttons[item] = btn

        # Khung nội dung
        self.content_frame = tk.Frame(self.root, bg=self.bg_color)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.on_menu_click("Danh Sách TK")

    # Xử lý sự kiện nhấn menu
    def on_menu_click(self, option):
        if self.selected_button:
            self.selected_button.config(bg=self.menu_color)
        self.selected_button = self.menu_buttons[option]
        self.selected_button.config(bg=self.selected_menu_color)
        
        self.menu_action(option)

    # Xóa nội dung hiện tại
    def clear_content(self):
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None

    # Điều hướng menu
    def menu_action(self, item):
        self.clear_content()
        if item == "Danh Sách TK":
            self.show_account_list()
        elif item == "Thêm":
            self.show_add_account()
        elif item == "Sửa":
            self.show_edit_account()
        elif item == "Xóa":
            self.show_delete_account()
        elif item == "Đăng xuất":
            self.sign_out()

    # Hiển thị danh sách tài khoản
    def show_account_list(self):
        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"))

        columns = ("STT", "Mã NV", "Tên Nhân Viên", "Email", "Quyền", "Trạng Thái")
        self.tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=25)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("STT", width=50, anchor="center")
        self.tree.column("Mã NV", width=100, anchor="center")
        self.tree.column("Tên Nhân Viên", width=200, anchor="w")
        self.tree.column("Email", width=200, anchor="w")
        self.tree.column("Quyền", width=150, anchor="center")
        self.tree.column("Trạng Thái", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_account_data()

    # Tải dữ liệu tài khoản từ database
    def load_account_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="12345678", database="Face_Recognition")
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT e.emp_id, e.last_name, e.first_name, e.email, e.status, r.role_name
                FROM Employees e
                LEFT JOIN Employee_Role er ON e.emp_id = er.emp_id
                LEFT JOIN Role r ON er.role_id = r.role_id
                ORDER BY e.emp_id ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for idx, row in enumerate(rows, 1):
                emp_id = row['emp_id']
                full_name = f"{row['last_name']} {row['first_name']}"
                email = row['email'] if row['email'] else "N/A"
                role = row['role_name'] if row['role_name'] else "Chưa phân quyền"
                status = "Hoạt động" if row['status'] == 'active' else "Không hoạt động"
                self.tree.insert("", "end", values=(idx, emp_id, full_name, email, role, status))
            cursor.close()
            conn.close()
            if not rows:
                messagebox.showinfo("Thông báo", "Không có tài khoản nào trong cơ sở dữ liệu!")
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {e}")

    # Thêm tài khoản mới
    def show_add_account(self):
        pass

    # Sửa tài khoản
    def show_edit_account(self):
        pass

    # Xóa tài khoản
    def show_delete_account(self):
        pass

    # Đăng xuất
    def sign_out(self):
        if messagebox.askokcancel("Đăng Xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ITApp(root)
    root.mainloop()