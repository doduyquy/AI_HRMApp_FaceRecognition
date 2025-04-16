import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from tkinter import Toplevel, Label, Button
import pandas as pd
from tkinter import filedialog
from modules.IT.data_dep import DataDepartment  

class DepartmentApp:
    def __init__(self, parent):
        self.parent = parent
        self.data_dep = DataDepartment()  
        self.bg_color = "#f7f8fa"
        self.current_content = None
        self.search_entry = None
        self.search_var = None

        # Create content frame
        self.content_frame = tk.Frame(self.parent.content_frame, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.show_department_list()

    def clear_content(self):
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None

    
    def show_department_list(self):
        self.clear_content()
        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        # Toolbar
        button_frame = tk.Frame(self.current_content, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=2, padx=5)

        buttons_inner_frame = tk.Frame(button_frame, bg=self.bg_color)
        buttons_inner_frame.pack(anchor="center")

        # Load icons
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")

        try:
            add_img = Image.open(os.path.join(img_dir, "add.png")).resize((22, 22))
            edit_img = Image.open(os.path.join(img_dir, "edit.png")).resize((22, 22))
            delete_img = Image.open(os.path.join(img_dir, "delete.png")).resize((22, 22))
            reset_img = Image.open(os.path.join(img_dir, "reset.png")).resize((22, 22))
            search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22))
            excel_img = Image.open(os.path.join(img_dir, "excel.png")).resize((22, 22))

            # Gán các icon vào self
            self.add_icon = ImageTk.PhotoImage(add_img)
            self.edit_icon = ImageTk.PhotoImage(edit_img)
            self.delete_icon = ImageTk.PhotoImage(delete_img)
            self.reset_icon = ImageTk.PhotoImage(reset_img)
            self.search_icon = ImageTk.PhotoImage(search_img)
            self.excel_icon = ImageTk.PhotoImage(excel_img)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hình ảnh: {str(e)}")
            return

        # Add button
        add_button = tk.Button(
            buttons_inner_frame,
            text="Thêm",
            image=self.add_icon,
            compound=tk.TOP,
            command=self.show_add_department,
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#adedb0"
        )
        add_button.pack(side=tk.LEFT, padx=3)

        # Edit button
        edit_button = tk.Button(
            buttons_inner_frame,
            text="Sửa",
            image=self.edit_icon,
            compound=tk.TOP,
            command=self.show_edit_department,
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#f2c47e"
        )
        edit_button.pack(side=tk.LEFT, padx=3)

        # Delete button
        delete_button = tk.Button(
            buttons_inner_frame,
            text="Xóa",
            image=self.delete_icon,
            compound=tk.TOP,
            # command=self.show_delete_department,
            command=self.show_delete_department,
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#f57a7a"
        )
        delete_button.pack(side=tk.LEFT, padx=3)

        # Excel button
        excel_button = tk.Button(
            buttons_inner_frame,
            text="Excel",
            image=self.excel_icon,
            compound=tk.TOP,
            command=self.export_to_excel,
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#65f06b"
        )
        excel_button.pack(side=tk.LEFT, padx=3)

        # Reset button
        reset_button = tk.Button(
            buttons_inner_frame,
            text="Làm mới",
            image=self.reset_icon,
            compound=tk.TOP,
            command=self.reset_department_list,
            bg="#f7f8fa",
            bd=0,
            width=60,
            height=60,
            font=("Times New Roman", 9),
            relief="flat",
            activebackground="#7d8e96"
        )
        reset_button.pack(side=tk.LEFT, padx=3)

        # Search frame
        search_frame = tk.Frame(buttons_inner_frame, bg="white", relief="flat", highlightthickness=1, highlightbackground="#4c84f5")
        search_frame.pack(side=tk.LEFT, padx=10, ipady=4)

        # Search entry
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

        # Search button
        search_button = tk.Button(
            search_frame,
            image=self.search_icon,
            command=self.search_department,
            bg="white",
            bd=0,
            relief="flat",
            activebackground="#fff",
            width=20,
            height=25
        )
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

        # Treeview configuration
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"), background="#9fd7f9", foreground="#000", relief="flat", borderwidth=0, padding=5)
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#e5e5e5")], foreground=[("selected", "black")])

        # Treeview columns
        columns = ("STT", "Mã phòng ban", "Tên phòng ban")
        self.tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("STT", width=50, anchor="center")
        self.tree.column("Mã phòng ban", width=100, anchor="center")
        self.tree.column("Tên phòng ban", width=200, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.load_department_data()

    def load_department_data(self):
        """Load department data into Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            departments = self.data_dep.load_departments()
            for idx, dep in enumerate(departments, 1):
                dep_id, dep_name = dep['dep_id'], dep['dep_name']
                self.tree.insert("", "end", values=(idx, dep_id, dep_name))
            if not departments:
                messagebox.showinfo("Thông báo", "Không có phòng ban nào trong cơ sở dữ liệu!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu phòng ban: {str(e)}")


    def search_department(self):
        search_text = self.search_var.get().strip()
        print(f"DEBUG: Search text = '{search_text}'")  # Debug để kiểm tra từ khóa

        # Nếu không có từ khóa hoặc từ khóa là placeholder, load lại toàn bộ danh sách
        if not search_text or search_text == "Tìm kiếm...":
            print("DEBUG: No search text, loading all departments")
            self.load_department_data()
            return

        # Xóa các mục hiện tại trong Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Gọi hàm tìm kiếm từ DataDepartment
            departments = self.data_dep.search_departments(search_text)
            print(f"DEBUG: Found {len(departments)} departments")

            # Hiển thị kết quả tìm kiếm
            for idx, dep in enumerate(departments, 1):
                dep_id, dep_name = dep['dep_id'], dep['dep_name']
                self.tree.insert("", "end", values=(idx, dep_id, dep_name))

            # Nếu không tìm thấy, hiển thị thông báo
            if not departments:
                messagebox.showinfo("Thông báo", f"Không tìm thấy phòng ban nào khớp với '{search_text}'!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tìm kiếm: {str(e)}")

    def reset_department_list(self):
        self.search_var.set("")
        self.search_entry.config(fg="gray")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm...")
        self.load_department_data()

    def _clear_placeholder(self, event=None):
        if self.search_entry.get() == "Tìm kiếm...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def _restore_placeholder(self, event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Tìm kiếm...")
            self.search_entry.config(fg="gray")

    def show_add_department(self):
        form = Toplevel(self.parent.root)
        form.title("Thêm Phòng Ban")
        window_width, window_height = 400, 200
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form.configure(bg="#ffffff")
        form.grab_set()

        tk.Label(form, text="Thêm Phòng Ban Mới", font=("Times New Roman", 14, "bold"), bg="#ffffff", fg="#14a0f7").pack(pady=10)

        frame = tk.Frame(form, bg="#ffffff")
        frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(frame, text="Tên phòng ban:", font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        dep_name_entry = ttk.Entry(frame, font=("Times New Roman", 11), width=25)
        dep_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def handle_save():
            dep_name = dep_name_entry.get().strip()
            if not dep_name:
                messagebox.showerror("Lỗi", "T tên phòng ban không được để trống!")
                return
            success, message = self.data_dep.add_department(dep_name)
            if success:
                messagebox.showinfo("Thành công", message)
                form.destroy()
                self.load_department_data()
            else:
                messagebox.showerror("Lỗi", message)

        save_button = tk.Button(form, text="Lưu", command=handle_save, bg="#4CAF50", fg="white", font=("Times New Roman", 11), width=10, relief="flat")
        save_button.pack(pady=20)

    def show_edit_department(self):
        """Show form to edit a selected department."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phòng ban để sửa!")
            return

        dep_id = self.tree.item(selected_item)['values'][1]
        dep_name = self.tree.item(selected_item)['values'][2]

        form = Toplevel(self.parent.root)
        form.title("Sửa Phòng Ban")
        window_width, window_height = 400, 200
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form.configure(bg="#ffffff")
        form.grab_set()

        tk.Label(form, text="Sửa Phòng Ban", font=("Times New Roman", 14, "bold"), bg="#ffffff", fg="#14a0f7").pack(pady=10)

        frame = tk.Frame(form, bg="#ffffff")
        frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(frame, text="Tên phòng ban:", font=("Times New Roman", 11), bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT)
        dep_name_entry = ttk.Entry(frame, font=("Times New Roman", 11), width=25)
        dep_name_entry.insert(0, dep_name)
        dep_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def handle_save():
            new_dep_name = dep_name_entry.get().strip()
            if not new_dep_name:
                messagebox.showerror("Lỗi", "Tên phòng ban không được để trống!")
                return
            success, message = self.data_dep.update_department(dep_id, new_dep_name)
            if success:
                messagebox.showinfo("Thành công", message)
                form.destroy()
                self.load_department_data()
            else:
                messagebox.showerror("Lỗi", message)

        save_button = tk.Button(form, text="Lưu", command=handle_save, bg="#4CAF50", fg="white", font=("Times New Roman", 11), width=10, relief="flat")
        save_button.pack(pady=20)

   
    
    def show_delete_department(self):
        print("DEBUG: show_delete_department called")
        selected_item = self.tree.selection()
        if not selected_item:
            print("DEBUG: No department selected")
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phòng ban để xóa!")
            return

        dep_id = self.tree.item(selected_item)['values'][1]
        dep_name = self.tree.item(selected_item)['values'][2]
        print(f"DEBUG: Selected department: ID={dep_id}, Name={dep_name}")

        # Tạo hộp thoại xác nhận
        confirm_dialog = Toplevel(self.parent.root)
        confirm_dialog.title("Xác nhận")
        confirm_dialog.geometry("300x150")
        confirm_dialog.resizable(False, False)
        confirm_dialog.transient(self.parent.root)
        confirm_dialog.grab_set()

        # Đảm bảo giao diện được cập nhật trước khi tính toán vị trí
        self.parent.root.update()
        print("DEBUG: Root updated before positioning dialog")

        # Tính toán vị trí hộp thoại
        dialog_width = 300  # Sử dụng giá trị cố định vì winfo_width có thể chưa cập nhật
        dialog_height = 150
        root_width = self.parent.root.winfo_width()
        root_height = self.parent.root.winfo_height()
        root_x = self.parent.root.winfo_x()
        root_y = self.parent.root.winfo_y()
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2
        confirm_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        print(f"DEBUG: Confirmation dialog positioned at x={x}, y={y}")

        label = Label(confirm_dialog, text=f"Bạn có chắc chắn muốn xóa phòng ban {dep_name}?", wraplength=250)
        label.pack(pady=20)

        def confirm_delete():
            print("DEBUG: confirm_delete called")
            success, message = self.data_dep.delete_department(dep_id)
            print(f"DEBUG: Delete result: success={success}, message={message}")
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_department_data()
            else:
                messagebox.showerror("Lỗi", message)
            confirm_dialog.destroy()

        def cancel_delete():
            print("DEBUG: cancel_delete called")
            confirm_dialog.destroy()

        btn_yes = Button(confirm_dialog, text="Có", command=confirm_delete, width=10, bg="#4CAF50", fg="white", font=("Times New Roman", 11), relief="flat")
        btn_yes.pack(side="left", padx=20, pady=10)
        btn_no = Button(confirm_dialog, text="Không", command=cancel_delete, width=10, bg="#f44336", fg="white", font=("Times New Roman", 11), relief="flat")
        btn_no.pack(side="right", padx=20, pady=10)
        print("DEBUG: Confirmation buttons created")

    def export_to_excel(self):
        columns = [self.tree.heading(col)['text'] for col in self.tree['columns']]
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            data.append(values)

        if not data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất sang Excel!")
            return

        df = pd.DataFrame(data, columns=columns)
        default_filename = "DanhSachPhongBan.xlsx"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Chọn nơi lưu file Excel"
        )

        if not file_path:
            return

        try:
            df.to_excel(file_path, index=False, engine='openpyxl')
            messagebox.showinfo("Thành công", f"Dữ liệu đã được xuất sang {file_path}!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi xuất file: {str(e)}")

    def destroy(self):
        self.clear_content()
        self.search_entry = None
        self.search_var = None