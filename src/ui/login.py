import tkinter as tk
from tkinter import messagebox, PhotoImage
from PIL import Image, ImageTk
import os
import mysql.connector
import employee 
import IT 
import manager

# Tạo cửa sổ chính
root = tk.Tk()
root.title('Đăng Nhập')
root.geometry('925x500+200+100')
root.configure(bg="#fff")
root.resizable(False, False)

# Hàm đăng nhập
def signin():
    emp_id = user.get()
    password_input = code.get()
    default_password = "123456"

    # Kiểm tra không để trống
    if not emp_id or emp_id == "tên đăng nhập":
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên đăng nhập!")
        return
    if not password_input or password_input == "Mật khẩu":
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập mật khẩu!")
        return

    # Hàm hiển thị màn hình chào
    def show_welcome_screen(name, next_action):
        screen = tk.Toplevel(root)
        screen.title("Thông tin nhân viên")
        screen.geometry('925x500+200+100')
        screen.config(bg="white")

        # Load hình ảnh
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(BASE_DIR, "..", "img", "welcome.jpg")
        img = Image.open(img_path).resize((500, 300)) 
        img = ImageTk.PhotoImage(img)

        img_lb = tk.Label(screen, image=img, bg="white")
        img_lb.image = img
        img_lb.pack(pady=(30, 10))  

        # Hiển thị tên
        f = tk.Frame(screen, bg="white")
        f.pack(pady=20)

        label1 = tk.Label(f, text="Xin chào, ", font=("Times New Roman", 23), bg="white")
        label1.grid(row=0, column=0) 

        label2 = tk.Label(f, text=name, font=("Times New Roman", 23, "bold"), fg="#57a1f8", bg="white")
        label2.grid(row=0, column=1) 

        def continue_app():
            screen.destroy()
            root.destroy()
            next_action()
        
        screen.after(2000, continue_app)
        screen.mainloop()

    # Admin
    if emp_id == "admin" and password_input == "admin":
        show_welcome_screen("Admin", lambda: [it_root := tk.Tk(), IT.ITApp(it_root), it_root.mainloop()])
        return

    # Manager 
    elif emp_id == "manager" and password_input == "manager":
        show_welcome_screen("Manager", lambda: [manager_root := tk.Tk(), manager.ManagerApp(manager_root), manager_root.mainloop()])
        return

    # Database
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="Face_Recognition"
        )
        cursor = conn.cursor()

        # Ktra trạng thái của nv
        cursor.execute("SELECT emp_id, first_name, last_name, status FROM Employees WHERE emp_id = %s", (emp_id,))
        result = cursor.fetchone()

        if result:
            emp_id_db, first_name, last_name, status = result
            if status == "Đã nghỉ": 
                messagebox.showerror("Lỗi", "Tài khoản của bạn đã khóa, bạn không thể đăng nhập!")
            elif password_input == default_password:
                full_name = f"{last_name} {first_name}"
                show_welcome_screen(full_name, lambda: employee.main(emp_id))
            else:
                messagebox.showerror("Lỗi", "Mật khẩu không đúng")
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập không tồn tại")

        cursor.close()
        conn.close()
    
    except mysql.connector.Error as e:
        messagebox.showerror("Lỗi kết nối", f"Lỗi MySQL: {e}")

# Load hình ảnh giao diện
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(BASE_DIR, "..", "img", "login.png")
img = Image.open(img_path).resize((450, 400))
img = ImageTk.PhotoImage(img)
tk.Label(root, image=img, bg='white').place(x=50, y=50)

# Khung chứa thông tin
f = tk.Frame(root, width=400, height=350, bg='white')
f.place(x=480, y=70)
heading = tk.Label(f, text='Đăng Nhập', fg='#57a1f8', bg='white', font=('Times New Roman', 23, 'bold'))
heading.place(x=130, y=0)

# Nhập tên đăng nhập
def on_enter(e):
    if user.get() == "Tên đăng nhập":
        user.delete(0, 'end')

def on_leave(e):
    if user.get() == '':
        user.insert(0, 'Tên đăng nhập')

user = tk.Entry(f, width=25, fg='black', border=0, bg='white', font=('Times New Roman', 11))
user.place(x=60, y=85)
user.insert(0, 'Tên đăng nhập')
user.bind('<FocusIn>', on_enter)
user.bind('<FocusOut>', on_leave)
user.bind('<Return>', lambda e: code.focus_set())

tk.Frame(f, width=330, height=2, bg='black', border=1).place(x=50, y=110)

# Nhập mật khẩu
def on_enter(e):
    if code.get() == "Mật khẩu":
        code.delete(0, 'end')
        code.config(show="*")

def on_leave(e):
    if code.get() == '':
        code.insert(0, 'Mật khẩu')
        code.config(show="") 

# Tạo Entry không ẩn mặc định
code = tk.Entry(f, width=25, fg='black', border=0, bg='white', font=('Times New Roman', 11))
code.place(x=60, y=165)
code.insert(0, 'Mật khẩu')
code.bind('<FocusIn>', on_enter)
code.bind('<FocusOut>', on_leave)
code.bind('<Return>', lambda e: signin())

# Ẩn/Hiện mật khẩu
button_mode = False

def hide():
    global button_mode
    if button_mode:
        eyeButton.config(image=closeeye, activebackground="white")
        if code.get() != "Mật khẩu":
            code.config(show="*")
        button_mode = False
    else:
        eyeButton.config(image=openeye, activebackground="white")
        code.config(show="")
        button_mode = True

openeye = PhotoImage(file=os.path.join(BASE_DIR, "..", "img", "openeye.png"))
closeeye = PhotoImage(file=os.path.join(BASE_DIR, "..", "img", "closeeye.png"))

# Ban đầu với closeeye
eyeButton = tk.Button(f, image=closeeye, bd=0, bg="#fff", command=hide)
eyeButton.place(x=350, y=160)

tk.Frame(f, width=330, height=2, bg='black', border=1).place(x=50, y=190)

# Nút đăng nhập
tk.Button(f, width=39, pady=7, text='Đăng Nhập', bg='#57a1f8', fg='white', font=('Times New Roman', 12), border=0, command=signin).place(x=35, y=240)

root.mainloop()