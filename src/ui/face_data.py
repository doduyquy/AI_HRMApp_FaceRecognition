import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Label, Button
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import os
import pandas as pd
from tkinter import filedialog
from modules.IT.data_face import DataFace

class FaceDataApp:
    def __init__(self, parent):
        self.parent = parent
        self.data_face = parent.data_face  # Sử dụng DataFace từ ITApp
        self.bg_color = "#f7f8fa"
        self.current_content = None
        self.search_entry = None
        self.search_var = None
        self.image_references = {}
        self.content_frame = tk.Frame(self.parent.content_frame, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.show_face_data_list()

    def clear_content(self):
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None
        self.image_references.clear()

    def destroy(self):
        self.clear_content()
        self.image_references.clear()
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None

    def show_face_data_list(self):
        self.clear_content()
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

        if not os.path.exists(img_dir):
            messagebox.showerror("Lỗi", f"Thư mục img không tồn tại tại: {img_dir}")
            return

        try:
            add_img = Image.open(os.path.join(img_dir, "add.png")).resize((22, 22))
            edit_img = Image.open(os.path.join(img_dir, "edit.png")).resize((22, 22))
            delete_img = Image.open(os.path.join(img_dir, "delete.png")).resize((22, 22))
            reset_img = Image.open(os.path.join(img_dir, "reset.png")).resize((22, 22))
            search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22))
            excel_img = Image.open(os.path.join(img_dir, "excel.png")).resize((22, 22))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hình ảnh: {str(e)}")
            return

        add_icon = ImageTk.PhotoImage(add_img)
        edit_icon = ImageTk.PhotoImage(edit_img)
        delete_icon = ImageTk.PhotoImage(delete_img)
        reset_icon = ImageTk.PhotoImage(reset_img)
        search_icon = ImageTk.PhotoImage(search_img)
        excel_icon = ImageTk.PhotoImage(excel_img)

        # Nút Thêm
        add_button = tk.Button(buttons_inner_frame, 
            text="Thêm", image=add_icon, compound=tk.TOP,
            command=self.show_add_face_data,
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#adedb0")
        add_button.image = add_icon
        add_button.pack(side=tk.LEFT, padx=3)

        # Nút Sửa
        edit_button = tk.Button(buttons_inner_frame, 
            text="Sửa", image=edit_icon, compound=tk.TOP,
            command=self.edit_face_data,
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#f2c47e")
        edit_button.image = edit_icon
        edit_button.pack(side=tk.LEFT, padx=3)

        # Nút Xóa
        delete_button = tk.Button(buttons_inner_frame, 
            text="Xóa", image=delete_icon, compound=tk.TOP,
            command=self.show_delete_face_data,
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#f57a7a")
        delete_button.image = delete_icon
        delete_button.pack(side=tk.LEFT, padx=3)

        # Nút Làm mới
        reset_button = tk.Button(buttons_inner_frame,
            text="Làm mới", image=reset_icon, compound=tk.TOP,
            command=self.reset_face_data_list, 
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#7d8e96")
        reset_button.image = reset_icon 
        reset_button.pack(side=tk.LEFT, padx=3)

        # Nút Xuất Excel
        excel_button = tk.Button(buttons_inner_frame, 
            text="Excel", image=excel_icon, compound=tk.TOP,
            command=self.export_to_excel,
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#65f06b")
        excel_button.image = excel_icon
        excel_button.pack(side=tk.LEFT, padx=3)

        # Ô tìm kiếm
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
        self.search_entry.insert(0, "Tìm kiếm dữ liệu khuôn mặt...")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_placeholder)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        search_button = tk.Button(
            search_frame,
            image=search_icon,
            command=self.search_face_data,
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
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"), background="#9fd7f9", foreground="#000", relief="flat", borderwidth=0, padding=5)
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#e5e5e5")], foreground=[("selected", "black")])

        columns = ("STT", "ID Khuôn Mặt", "Tên Nhân Viên", "Ngày Thu Thập", "Trạng Thái")
        self.tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("STT", width=50, anchor="center")
        self.tree.column("ID Khuôn Mặt", width=100, anchor="center")
        self.tree.column("Tên Nhân Viên", width=200, anchor="w")
        self.tree.column("Ngày Thu Thập", width=150, anchor="center")
        self.tree.column("Trạng Thái", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Thêm binding cho sự kiện nhấp đúp
        self.tree.bind("<Double-1>", self.show_face_images)

        self.load_face_data()

    def load_face_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        face_data = self.data_face.fetch_face_data()  # Lấy dữ liệu từ DataFace
        for idx, row in enumerate(face_data, 1):
            face_id = row['face_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            collected_date = row['collected_date']
            status = row['status']
            self.tree.insert("", "end", values=(idx, face_id, full_name, collected_date, status))

        if not face_data:
            messagebox.showinfo("Thông báo", "Không có dữ liệu khuôn mặt nào trong cơ sở dữ liệu!")

    def export_to_excel(self):
        columns = ["STT", "ID Khuôn Mặt", "Tên Nhân Viên", "Ngày Thu Thập", "Trạng Thái"]
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            data.append(list(values))

        if not data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất sang Excel!")
            return

        df = pd.DataFrame(data, columns=columns)
        default_filename = "DanhSachDuLieuKhuonMat.xlsx"
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

    def search_face_data(self):
        search_term = self.search_var.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        face_data = self.data_face.search_face_data(search_term)
        for idx, row in enumerate(face_data, 1):
            face_id = row['face_id']
            full_name = f"{row['last_name']} {row['first_name']}"
            collected_date = row['collected_date']
            status = row['status']
            self.tree.insert("", "end", values=(idx, face_id, full_name, collected_date, status))

        if not face_data:
            messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu khuôn mặt nào!")

    def reset_face_data_list(self):
        self.search_var.set("")
        self.search_entry.config(fg="gray")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm dữ liệu khuôn mặt...")
        self.load_face_data()

    def _clear_placeholder(self, event=None):
        if self.search_entry.get() == "Tìm kiếm dữ liệu khuôn mặt...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def _restore_placeholder(self, event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Tìm kiếm dữ liệu khuôn mặt...")
            self.search_entry.config(fg="gray")

    
    def show_face_images(self, event=None):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên để xem ảnh!")
            return

        # Lấy emp_id từ hàng được chọn
        emp_id = None
        face_data = self.data_face.fetch_face_data()
        selected_face_id = self.tree.item(selected_item)['values'][1]  # ID Khuôn Mặt
        for row in face_data:
            if row['face_id'] == selected_face_id:
                emp_id = row['emp_id']
                full_name = f"{row['last_name']} {row['first_name']}"
                break

        if not emp_id:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin nhân viên!")
            return

        # Lấy tất cả ảnh của nhân viên dựa trên emp_id
        employee_images = [row for row in face_data if row['emp_id'] == emp_id]
        if not employee_images:
            messagebox.showinfo("Thông báo", "Nhân viên này chưa có ảnh nào trong cơ sở dữ liệu!")
            return

        # Tạo cửa sổ mới để hiển thị ảnh
        image_window = Toplevel(self.parent.root)
        image_window.title(f"Ảnh của {full_name}")
        image_window.geometry("800x300")
        image_window.configure(bg="#ffffff")
        image_window.transient(self.parent.root)
        image_window.grab_set()

        # Căn giữa cửa sổ
        image_window.update_idletasks()
        dialog_width = image_window.winfo_width()
        dialog_height = image_window.winfo_height()
        root_width = self.parent.root.winfo_width()
        root_height = self.parent.root.winfo_height()
        root_x = self.parent.root.winfo_x()
        root_y = self.parent.root.winfo_y()
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2
        image_window.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Định nghĩa các góc và ánh xạ
        angles = ['front', 'left', 'right', 'up', 'down']
        image_labels = {}

        # Tạo frame để chứa ảnh
        image_frame = tk.Frame(image_window, bg="#ffffff")
        image_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Tải và hiển thị ảnh cho từng góc
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Đường dẫn đến src/ui/
        PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))  # Lên 2 cấp để đến project_root/
        for angle in angles:
            # Tìm ảnh tương ứng với góc
            image_path = None
            for img_data in employee_images:
                if img_data['angle'].lower() == angle:
                    image_path = img_data['image_path']
                    break

            # Tạo frame cho từng ảnh
            frame = tk.Frame(image_frame, bg="#ffffff")
            frame.pack(side=tk.LEFT, padx=10)

            # Tạo nhãn cho tiêu đề góc
            angle_label = tk.Label(frame, text=angle.capitalize(), font=("Times New Roman", 11), bg="#ffffff")
            angle_label.pack()

            # Tải ảnh
            if image_path:
                try:
                    # Chuyển đường dẫn tương đối thành đường dẫn tuyệt đối
                    # image_path có dạng "/images/1_Luyen_01.jpg"
                    relative_path = image_path.lstrip("/")  # Bỏ "/" đầu, còn "images/1_Luyen_01.jpg"
                    full_path = os.path.join(PROJECT_ROOT, relative_path)  # Gắn với project_root
                    full_path = os.path.normpath(full_path)  # Chuẩn hóa đường dẫn
                    if os.path.exists(full_path):
                        img = Image.open(full_path).resize((120, 120))
                        photo = ImageTk.PhotoImage(img)
                        label = tk.Label(frame, image=photo, bg="#ffffff")
                        label.image = photo  # Giữ tham chiếu
                        self.image_references[f"{emp_id}_{angle}"] = photo
                        label.pack()
                    else:
                        error_label = tk.Label(frame, text="Ảnh không tồn tại", font=("Times New Roman", 10), fg="red", bg="#ffffff")
                        error_label.pack()
                except Exception as e:
                    error_label = tk.Label(frame, text=f"Lỗi tải ảnh: {str(e)}", font=("Times New Roman", 10), fg="red", bg="#ffffff")
                    error_label.pack()
            else:
                no_image_label = tk.Label(frame, text="Chưa có ảnh", font=("Times New Roman", 10), fg="gray", bg="#ffffff")
                no_image_label.pack()

        # Nút đóng
        close_button = tk.Button(image_window, text="Đóng", command=image_window.destroy, bg="#f44336", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        close_button.pack(pady=10)

    def show_add_face_data(self):
        form = tk.Toplevel(self.parent.root)
        form.title("Thêm Dữ Liệu Khuôn Mặt")
        window_width = 800
        window_height = 600
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form.configure(bg="#ffffff")
        form.grab_set()

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

        tk.Label(form, text="Thêm Dữ Liệu Khuôn Mặt", font=("Times New Roman", 16, "bold"), bg="#ffffff", fg="#14a0f7").pack(pady=20)

        # Frame chứa các trường nhập liệu
        input_frame = tk.Frame(form, bg="#ffffff")
        input_frame.pack(fill=tk.X, padx=30, pady=10)

        # Nhân viên
        emp_frame = tk.Frame(input_frame, bg="#ffffff")
        emp_frame.pack(fill=tk.X, pady=5)
        tk.Label(emp_frame, text="Nhân viên:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        emp_var = tk.StringVar()
        employees = self.data_face.load_accounts()
        emp_combo = ttk.Combobox(emp_frame, textvariable=emp_var, values=[f"{emp['last_name']} {emp['first_name']}" for emp in employees], state="readonly", style="Custom.TCombobox")
        emp_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Ngày thu thập
        date_frame = tk.Frame(input_frame, bg="#ffffff")
        date_frame.pack(fill=tk.X, pady=5)
        tk.Label(date_frame, text="Ngày thu thập:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        date_entry = DateEntry(date_frame, font=("Times New Roman", 11),
                            state="readonly",
                            date_pattern="yyyy-mm-dd",
                            width=29,
                            background='white',
                            foreground='black',
                            borderwidth=1,
                            relief="solid",
                            style="Custom.DateEntry")
        date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Trạng thái
        status_frame = tk.Frame(input_frame, bg="#ffffff")
        status_frame.pack(fill=tk.X, pady=5)
        tk.Label(status_frame, text="Trạng Thái:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        status_var = tk.StringVar(value="Hoạt động")
        status_combo = ttk.Combobox(status_frame, textvariable=status_var, values=["Hoạt động", "Không hoạt động"], state="readonly", style="Custom.TCombobox")
        status_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Frame chứa ảnh
        image_frame = tk.Frame(form, bg="#ffffff")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
        angles = ['front', 'left', 'right', 'up', 'down']
        image_labels = {}
        image_paths = {}  # Lưu đường dẫn ảnh mới được chọn
        current_emp_id = None

        def update_images():
            nonlocal current_emp_id
            emp_name = emp_var.get().strip()
            emp_id = None
            for emp in employees:
                full_name = f"{emp['last_name']} {emp['first_name']}"
                if full_name == emp_name:
                    emp_id = emp['emp_id']
                    break

            if emp_id is None:
                for angle in angles:
                    if angle in image_labels:
                        image_labels[angle].config(image='')
                        image_labels[angle].image = None
                return

            current_emp_id = emp_id
            face_data = self.data_face.fetch_face_data()
            employee_images = [row for row in face_data if row['emp_id'] == emp_id]

            for angle in angles:
                image_path = None
                for img_data in employee_images:
                    if img_data['angle'].lower() == angle:
                        image_path = img_data['image_path']
                        break

                if angle in image_labels:
                    if image_path:
                        try:
                            relative_path = image_path.lstrip("/")
                            full_path = os.path.join(PROJECT_ROOT, relative_path)
                            full_path = os.path.normpath(full_path)
                            if os.path.exists(full_path):
                                img = Image.open(full_path).resize((100, 100))
                                photo = ImageTk.PhotoImage(img)
                                image_labels[angle].config(image=photo)
                                image_labels[angle].image = photo
                            else:
                                image_labels[angle].config(image='')
                                image_labels[angle].image = None
                        except Exception as e:
                            image_labels[angle].config(image='')
                            image_labels[angle].image = None
                    else:
                        image_labels[angle].config(image='')
                        image_labels[angle].image = None

        # Hiển thị ảnh và nút chọn ảnh
        for angle in angles:
            frame = tk.Frame(image_frame, bg="#ffffff")
            frame.pack(side=tk.LEFT, padx=10)

            tk.Label(frame, text=angle.capitalize(), font=("Times New Roman", 11), bg="#ffffff").pack()

            image_label = tk.Label(frame, bg="#ffffff")
            image_label.pack()
            image_labels[angle] = image_label

            def make_select_image_handler(current_angle):
                def select_image():
                    file_path = filedialog.askopenfilename(
                        title=f"Chọn ảnh cho góc {current_angle}",
                        filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
                    )
                    if file_path:
                        try:
                            img = Image.open(file_path).resize((100, 100))
                            photo = ImageTk.PhotoImage(img)
                            image_labels[current_angle].config(image=photo)
                            image_labels[current_angle].image = photo
                            image_paths[current_angle] = file_path
                        except Exception as e:
                            messagebox.showerror("Lỗi", f"Không thể tải ảnh: {str(e)}")

                return select_image

            select_button = tk.Button(frame, text="Chọn ảnh", command=make_select_image_handler(angle), bg="#4CAF50", fg="white", font=("Times New Roman", 10), relief="flat")
            select_button.pack(pady=5)

        # Cập nhật ảnh khi chọn nhân viên
        emp_combo.bind("<<ComboboxSelected>>", lambda event: update_images())

        button_frame = tk.Frame(form, bg="#ffffff")
        button_frame.pack(pady=20)

        # def handle_save():
        #     emp_name = emp_var.get().strip()
        #     collected_date = date_entry.get().strip()
        #     status = status_var.get().strip()

        #     emp_id = None
        #     for emp in employees:
        #         full_name = f"{emp['last_name']} {emp['first_name']}"
        #         if full_name == emp_name:
        #             emp_id = emp['emp_id']
        #             break

        #     if not emp_id:
        #         messagebox.showerror("Lỗi", "Vui lòng chọn nhân viên hợp lệ!")
        #         return

        #     # Thêm bản ghi mới cho từng góc ảnh
        #     face_data = self.data_face.fetch_face_data()
        #     any_success = False
        #     for angle, file_path in image_paths.items():
        #         if file_path:
        #             # Tạo tên file: <emp_id>_<tên>_<số thứ tự>.jpg
        #             emp_name_clean = emp_name.replace(" ", "_")
        #             image_count = len([row for row in face_data if row['emp_id'] == emp_id]) + 1
        #             new_filename = f"{emp_id}_{emp_name_clean}_{image_count:02d}.jpg"
        #             new_path = os.path.join(PROJECT_ROOT, "images", new_filename)
        #             new_path = os.path.normpath(new_path)

        #             # Sao chép ảnh vào thư mục images/
        #             try:
        #                 os.makedirs(os.path.dirname(new_path), exist_ok=True)
        #                 img = Image.open(file_path)
        #                 img.save(new_path)
        #                 # Thêm bản ghi mới vào Face_Data với angle tương ứng
        #                 success, result = self.data_face.add_face_data(emp_id, collected_date, status, f"/images/{new_filename}", angle=angle)
        #                 if not success:
        #                     messagebox.showerror("Lỗi", result)
        #                     continue
        #                 any_success = True
        #                 image_count += 1
        #             except Exception as e:
        #                 messagebox.showerror("Lỗi", f"Không thể lưu ảnh: {str(e)}")
        #                 continue

        #     if any_success:
        #         messagebox.showinfo("Thành công", "Thêm dữ liệu khuôn mặt thành công!")
        #     else:
        #         messagebox.showwarning("Cảnh báo", "Không có dữ liệu nào được lưu thành công!")
        #     form.destroy()
        #     self.load_face_data()

      
        
        def handle_save():
            emp_name = emp_var.get().strip()
            collected_date = date_entry.get().strip()
            status = status_var.get().strip()

            emp_id = None
            for emp in employees:
                full_name = f"{emp['last_name']} {emp['first_name']}"
                if full_name == emp_name:
                    emp_id = emp['emp_id']
                    break

            if not emp_id:
                messagebox.showerror("Lỗi", "Vui lòng chọn nhân viên hợp lệ!")
                return

            face_data = self.data_face.fetch_face_data()
            any_success = False
            # Tính image_count ban đầu cho tất cả ảnh hiện có của emp_id
            base_image_count = len([row for row in face_data if row['emp_id'] == emp_id])
            for idx, (angle, file_path) in enumerate(image_paths.items(), 1):
                if file_path:
                    emp_name_clean = emp_name.replace(" ", "_")
                    # Tạo tên file duy nhất cho mỗi góc
                    new_filename = f"{emp_id}_{emp_name_clean}_{(base_image_count + idx):02d}.jpg"
                    new_path = os.path.join(PROJECT_ROOT, "images", new_filename)
                    new_path = os.path.normpath(new_path)

                    try:
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)
                        img = Image.open(file_path)
                        img.save(new_path)
                        success, result = self.data_face.add_face_data(emp_id, collected_date, status, f"/images/{new_filename}", angle=angle)
                        if not success:
                            messagebox.showerror("Lỗi", result)
                            continue
                        any_success = True
                    except Exception as e:
                        messagebox.showerror("Lỗi", f"Không thể lưu ảnh: {str(e)}")
                        continue

            if any_success:
                messagebox.showinfo("Thành công", "Thêm dữ liệu khuôn mặt thành công!")
            else:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu nào được lưu thành công!")
            form.destroy()
            self.load_face_data()
            
        save_button = tk.Button(button_frame, text="Lưu", command=handle_save, bg="#4CAF50", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Hủy", command=form.destroy, bg="#f44336", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        cancel_button.pack(side=tk.LEFT, padx=10)

    def edit_face_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dữ liệu khuôn mặt để sửa!")
            return

        face_id = self.tree.item(selected_item)['values'][1]
        self.show_edit_face_data(face_id)
    
    def show_edit_face_data(self, face_id):
        form = tk.Toplevel(self.parent.root)
        form.title("Chỉnh Sửa Dữ Liệu Khuôn Mặt")
        window_width = 800
        window_height = 600
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form.configure(bg="#ffffff")
        form.grab_set()

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

        tk.Label(form, text="Chỉnh Sửa Dữ Liệu Khuôn Mặt", font=("Times New Roman", 16, "bold"), bg="#ffffff", fg="#14a0f7").pack(pady=20)

        face_data = self.data_face.fetch_face_data_by_id(face_id)
        if not face_data:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu khuôn mặt!")
            form.destroy()
            return

        emp_id_db, collected_date_db, status_db, last_name_db, first_name_db = face_data
        full_name_db = f"{last_name_db} {first_name_db}"

        # Frame chứa các trường nhập liệu
        input_frame = tk.Frame(form, bg="#ffffff")
        input_frame.pack(fill=tk.X, padx=30, pady=10)

        emp_frame = tk.Frame(input_frame, bg="#ffffff")
        emp_frame.pack(fill=tk.X, pady=5)
        tk.Label(emp_frame, text="Nhân viên:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        emp_var = tk.StringVar(value=full_name_db)
        employees = self.data_face.load_accounts()
        emp_combo = ttk.Combobox(emp_frame, textvariable=emp_var, values=[f"{emp['last_name']} {emp['first_name']}" for emp in employees], state="readonly", style="Custom.TCombobox")
        emp_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        date_frame = tk.Frame(input_frame, bg="#ffffff")
        date_frame.pack(fill=tk.X, pady=5)
        tk.Label(date_frame, text="Ngày thu thập:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        date_entry = DateEntry(date_frame, font=("Times New Roman", 11),
                            state="readonly",
                            date_pattern="yyyy-mm-dd",
                            width=29,
                            background='white',
                            foreground='black',
                            borderwidth=1,
                            relief="solid",
                            style="Custom.DateEntry")
        if collected_date_db:
            date_entry.set_date(collected_date_db)
        date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        status_frame = tk.Frame(input_frame, bg="#ffffff")
        status_frame.pack(fill=tk.X, pady=5)
        tk.Label(status_frame, text="Trạng Thái:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        status_var = tk.StringVar(value=status_db)
        status_combo = ttk.Combobox(status_frame, textvariable=status_var, values=["Hoạt động", "Không hoạt động"], state="readonly", style="Custom.TCombobox")
        status_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Frame chứa ảnh
        image_frame = tk.Frame(form, bg="#ffffff")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
        angles = ['front', 'left', 'right', 'up', 'down']
        image_labels = {}
        image_paths = {}  # Lưu đường dẫn ảnh mới được chọn
        current_emp_id = emp_id_db

        def update_images():
            nonlocal current_emp_id
            emp_name = emp_var.get().strip()
            emp_id = None
            for emp in employees:
                full_name = f"{emp['last_name']} {emp['first_name']}"
                if full_name == emp_name:
                    emp_id = emp['emp_id']
                    break

            if emp_id is None:
                for angle in angles:
                    if angle in image_labels:
                        image_labels[angle].config(image='')
                        image_labels[angle].image = None
                return

            current_emp_id = emp_id
            face_data = self.data_face.fetch_face_data()
            employee_images = [row for row in face_data if row['emp_id'] == emp_id]

            for angle in angles:
                image_path = None
                for img_data in employee_images:
                    if img_data['angle'].lower() == angle:
                        image_path = img_data['image_path']
                        break

                if angle in image_labels:
                    if image_path:
                        try:
                            relative_path = image_path.lstrip("/")
                            full_path = os.path.join(PROJECT_ROOT, relative_path)
                            full_path = os.path.normpath(full_path)
                            if os.path.exists(full_path):
                                img = Image.open(full_path).resize((100, 100))
                                photo = ImageTk.PhotoImage(img)
                                image_labels[angle].config(image=photo)
                                image_labels[angle].image = photo
                            else:
                                image_labels[angle].config(image='')
                                image_labels[angle].image = None
                        except Exception as e:
                            image_labels[angle].config(image='')
                            image_labels[angle].image = None
                    else:
                        image_labels[angle].config(image='')
                        image_labels[angle].image = None

        # Hiển thị ảnh và nút chọn ảnh
        for angle in angles:
            frame = tk.Frame(image_frame, bg="#ffffff")
            frame.pack(side=tk.LEFT, padx=10)

            tk.Label(frame, text=angle.capitalize(), font=("Times New Roman", 11), bg="#ffffff").pack()

            image_label = tk.Label(frame, bg="#ffffff")
            image_label.pack()
            image_labels[angle] = image_label

            def make_select_image_handler(current_angle):
                def select_image():
                    file_path = filedialog.askopenfilename(
                        title=f"Chọn ảnh cho góc {current_angle}",
                        filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
                    )
                    if file_path:
                        try:
                            img = Image.open(file_path).resize((100, 100))
                            photo = ImageTk.PhotoImage(img)
                            image_labels[current_angle].config(image=photo)
                            image_labels[current_angle].image = photo
                            image_paths[current_angle] = file_path
                        except Exception as e:
                            messagebox.showerror("Lỗi", f"Không thể tải ảnh: {str(e)}")

                return select_image

            select_button = tk.Button(frame, text="Chọn ảnh", command=make_select_image_handler(angle), bg="#4CAF50", fg="white", font=("Times New Roman", 10), relief="flat")
            select_button.pack(pady=5)

        # Cập nhật ảnh khi chọn nhân viên
        emp_combo.bind("<<ComboboxSelected>>", lambda event: update_images())
        update_images()  # Hiển thị ảnh ban đầu

        button_frame = tk.Frame(form, bg="#ffffff")
        button_frame.pack(pady=20)

        # def handle_save():
        #     emp_name = emp_var.get().strip()
        #     collected_date = date_entry.get().strip()
        #     status = status_var.get().strip()

        #     emp_id = None
        #     for emp in employees:
        #         full_name = f"{emp['last_name']} {emp['first_name']}"
        #         if full_name == emp_name:
        #             emp_id = emp['emp_id']
        #             break

        #     if not emp_id:
        #         messagebox.showerror("Lỗi", "Vui lòng chọn nhân viên hợp lệ!")
        #         return

        #     # Cập nhật dữ liệu khuôn mặt chính (bản ghi hiện tại)
        #     success, result = self.data_face.update_face_data(face_id, emp_id, collected_date, status)
        #     if not success:
        #         messagebox.showerror("Lỗi", result)
        #         return

        #     # Cập nhật hoặc thêm ảnh mới
        #     face_data = self.data_face.fetch_face_data()
        #     any_success = False
        #     for angle, file_path in image_paths.items():
        #         if file_path:
        #             # Tạo tên file mới
        #             emp_name_clean = emp_name.replace(" ", "_")
        #             image_count = len([row for row in face_data if row['emp_id'] == emp_id]) + 1
        #             new_filename = f"{emp_id}_{emp_name_clean}_{image_count:02d}.jpg"
        #             new_path = os.path.join(PROJECT_ROOT, "images", new_filename)
        #             new_path = os.path.normpath(new_path)

        #             # Sao chép ảnh vào thư mục images/
        #             try:
        #                 os.makedirs(os.path.dirname(new_path), exist_ok=True)
        #                 img = Image.open(file_path)
        #                 img.save(new_path)

        #                 # Kiểm tra xem góc này đã có trong Face_Data chưa
        #                 existing_record = None
        #                 for row in face_data:
        #                     if row['emp_id'] == emp_id and row['angle'].lower() == angle:
        #                         existing_record = row
        #                         break

        #                 if existing_record:
        #                     # Cập nhật bản ghi hiện có
        #                     success, result = self.data_face.update_image_data(existing_record['face_id'], f"/images/{new_filename}", angle)
        #                     if not success:
        #                         messagebox.showerror("Lỗi", result)
        #                         continue
        #                 else:
        #                     # Thêm bản ghi mới
        #                     success, result = self.data_face.add_face_data(emp_id, collected_date, status, f"/images/{new_filename}", angle=angle)
        #                     if not success:
        #                         messagebox.showerror("Lỗi", result)
        #                         continue
        #                 any_success = True
        #                 image_count += 1
        #             except Exception as e:
        #                 messagebox.showerror("Lỗi", f"Không thể lưu ảnh: {str(e)}")
        #                 continue

        #     if any_success or success:
        #         messagebox.showinfo("Thành công", "Cập nhật dữ liệu khuôn mặt thành công!")
        #     else:
        #         messagebox.showwarning("Cảnh báo", "Không có dữ liệu nào được lưu thành công!")
        #     form.destroy()
        #     self.load_face_data()
        
        def handle_save():
            emp_name = emp_var.get().strip()
            collected_date = date_entry.get().strip()
            status = status_var.get().strip()

            emp_id = None
            for emp in employees:
                full_name = f"{emp['last_name']} {emp['first_name']}"
                if full_name == emp_name:
                    emp_id = emp['emp_id']
                    break

            if not emp_id:
                messagebox.showerror("Lỗi", "Vui lòng chọn nhân viên hợp lệ!")
                return

            # Cập nhật dữ liệu khuôn mặt chính (bản ghi hiện tại)
            success, result = self.data_face.update_face_data(face_id, emp_id, collected_date)  # Bỏ status nếu không cần
            if not success:
                messagebox.showerror("Lỗi", result)
                return

            # Cập nhật hoặc thêm ảnh mới
            face_data = self.data_face.fetch_face_data()
            any_success = False
            for angle, file_path in image_paths.items():
                if file_path:
                    # Tạo tên file mới
                    emp_name_clean = emp_name.replace(" ", "_")
                    image_count = len([row for row in face_data if row['emp_id'] == emp_id]) + 1
                    new_filename = f"{emp_id}_{emp_name_clean}_{image_count:02d}.jpg"
                    new_path = os.path.join(PROJECT_ROOT, "images", new_filename)
                    new_path = os.path.normpath(new_path)

                    # Sao chép ảnh vào thư mục images/
                    try:
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)
                        img = Image.open(file_path)
                        img.save(new_path)

                        # Kiểm tra xem góc này đã có trong Face_Data chưa
                        existing_record = None
                        for row in face_data:
                            if row['emp_id'] == emp_id and row['angle'].lower() == angle:
                                existing_record = row
                                break

                        if existing_record:
                            # Cập nhật bản ghi hiện có
                            success, result = self.data_face.update_image_data(existing_record['face_id'], f"/images/{new_filename}", angle)
                            if not success:
                                messagebox.showerror("Lỗi", result)
                                continue
                        else:
                            # Thêm bản ghi mới
                            success, result = self.data_face.add_face_data(emp_id, collected_date, status, f"/images/{new_filename}", angle=angle)
                            if not success:
                                messagebox.showerror("Lỗi", result)
                                continue
                        any_success = True
                        image_count += 1
                    except Exception as e:
                        messagebox.showerror("Lỗi", f"Không thể lưu ảnh: {str(e)}")
                        continue

            if any_success or success:
                messagebox.showinfo("Thành công", "Cập nhật dữ liệu khuôn mặt thành công!")
            else:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu nào được lưu thành công!")
            form.destroy()
            self.load_face_data()

        save_button = tk.Button(button_frame, text="Lưu", command=handle_save, bg="#4CAF50", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Hủy", command=form.destroy, bg="#f44336", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        cancel_button.pack(side=tk.LEFT, padx=10)

    def show_delete_face_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dữ liệu khuôn mặt để xóa!")
            return

        face_id = self.tree.item(selected_item)['values'][1]
        full_name = self.tree.item(selected_item)['values'][2]

        confirm_dialog = Toplevel(self.parent.root)
        confirm_dialog.title("Xác nhận")
        confirm_dialog.geometry("300x150")
        confirm_dialog.resizable(False, False)
        confirm_dialog.transient(self.parent.root)
        confirm_dialog.grab_set()

        confirm_dialog.update_idletasks()
        dialog_width = confirm_dialog.winfo_width()
        dialog_height = confirm_dialog.winfo_height()
        root_width = self.parent.root.winfo_width()
        root_height = self.parent.root.winfo_height()
        root_x = self.parent.root.winfo_x()
        root_y = self.parent.root.winfo_y()
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2
        confirm_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        label = Label(confirm_dialog, text=f"Bạn có chắc chắn muốn xóa dữ liệu khuôn mặt của {full_name}?", wraplength=250)
        label.pack(pady=20)

        def confirm_delete():
            success, message = self.data_face.delete_face_data(face_id)
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_face_data()
            else:
                messagebox.showerror("Lỗi", message)
            confirm_dialog.destroy()

        def cancel_delete():
            confirm_dialog.destroy()

        btn_yes = Button(confirm_dialog, text="Có", command=confirm_delete, width=10, 
                        bg="#4CAF50", fg="white", font=("Times New Roman", 11), relief="flat")
        btn_yes.pack(side="left", padx=20, pady=10)

        btn_no = Button(confirm_dialog, text="Không", command=cancel_delete, width=10,
                        bg="#f44336", fg="white", font=("Times New Roman", 11), relief="flat")
        btn_no.pack(side="right", padx=20, pady=10)