import tkinter as tk
from tkinter import ttk
from datetime import datetime
import time
import threading
import cv2
from PIL import Image, ImageTk
from database import handleDB 

class UI_FaceRecognition:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")

        # Khởi tạo đối tượng HandleDB
        self.db = handleDB.DatabaseHandler()

        # Lấy kích thước màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"Kích thước màn hình: {screen_width}x{screen_height}")

        # Đặt kích thước cửa sổ khớp với kích thước màn hình
        self.root.geometry(f"{screen_width}x{screen_height}")
        # Vô hiệu hóa khả năng thay đổi kích thước
        self.root.resizable(False, False)

        # Đặt màu nền cho cửa sổ
        self.root.configure(bg="#f0f0f0")

        # Tính chiều rộng của thanh kết quả (2/3 chiều rộng màn hình)
        result_width = int(screen_width * 2 / 3)

        # Phần 1: Dòng hiển thị kết quả nhận diện
        self.result_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.result_frame.pack(fill="x", pady=5)

        self.result_label = tk.Label(
            self.result_frame,
            text="Không phát hiện khuôn mặt",
            font=("Arial", 16, "bold"),
            bg="blue",
            fg="white",
            anchor="center",
            relief="raised",
            borderwidth=5,
            highlightthickness=2,
            highlightbackground="#f0f0f0",
            width=result_width // 10
        )
        self.result_label.pack(pady=5, padx=(screen_width - result_width) // 2)


        self.root.update()
        result_frame_height = self.result_frame.winfo_height()
        remaining_height = screen_height - result_frame_height - 70 # 70px height cua thanh taskbar và title bar

        camera_width = screen_width // 2
        right_width = screen_width - camera_width

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0", height=remaining_height)
        self.main_frame.pack(fill="x", expand=False)
        self.main_frame.pack_propagate(False)

        # Phần 2: Khu vực hiển thị camera (cách lề trái 20px)
        self.camera_frame = tk.Frame(
            self.main_frame,
            bg="gray",
            width=camera_width,
            height=remaining_height
        )
        self.camera_frame.pack(side="left", fill="none", expand=False, padx=(10, 0))  # Thêm padx=20 bên trái
        self.camera_frame.pack_propagate(False)

        self.camera_label = tk.Label(self.camera_frame, bg="gray")
        self.camera_label.pack(fill="both", expand=True)

        # Phần 3: Khu vực bên phải
        self.right_frame = tk.Frame(
            self.main_frame,
            width=right_width,
            height=remaining_height,
            bg="#f0f0f0"
        )
        self.right_frame.pack(side="right", fill="none", expand=False, padx=10)
        self.right_frame.pack_propagate(False)

        # Phần thời gian và ngày tháng
        self.time_frame = tk.Frame(self.right_frame, bg="#f0f0f0")
        self.time_frame.pack(fill="x", pady=5)

        self.time_inner_frame = tk.Frame(self.time_frame, bg="#f0f0f0")
        self.time_inner_frame.pack(anchor="center")

        self.time_label = tk.Label(
            self.time_inner_frame,
            text="07:22:59",
            font=("Arial", 18, "bold"),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            borderwidth=2,
            highlightthickness=2,
            highlightbackground="#388E3C",
            width=10
        )
        self.time_label.pack(side="left", padx=20)

        self.date_label = tk.Label(
            self.time_inner_frame,
            text="14/02/2025",
            font=("Arial", 18, "bold"),
            bg="#2196F3",
            fg="white",
            relief="flat",
            borderwidth=2,
            highlightthickness=2,
            highlightbackground="#1976D2",
            width=12
        )
        self.date_label.pack(side="left", padx=20)

        self.table_title = tk.Label(
            self.right_frame,
            text="Danh Sách Chấm Công",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        self.table_title.pack(pady=5)

        self.table_frame = tk.Frame(self.right_frame, bg="#f0f0f0")
        self.table_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#333333",
                        rowheight=30,
                        fieldbackground="#ffffff")
        # Thay đổi màu khi chọn hàng
        style.map("Treeview",
                  background=[('selected', '#0288D1')],  # Xanh dương đậm
                  foreground=[('selected', '#ffffff')])  # Chữ trắng khi chọn

        columns = ("STT", "MSNV", "Ten", "Vao", "Ra")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=21)

        self.tree.heading("STT", text="STT")
        self.tree.heading("MSNV", text="MSNV")
        self.tree.heading("Ten", text="Ten")
        self.tree.heading("Vao", text="Vao")
        self.tree.heading("Ra", text="Ra")

        self.tree.column("STT", width=int(right_width * 0.1), anchor="center")
        self.tree.column("MSNV", width=int(right_width * 0.15), anchor="center")
        self.tree.column("Ten", width=int(right_width * 0.25), anchor="center")
        self.tree.column("Vao", width=int(right_width * 0.2), anchor="center")
        self.tree.column("Ra", width=int(right_width * 0.2), anchor="center")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Enter>", lambda e: self.tree.config(cursor="hand2"))
        self.tree.bind("<Leave>", lambda e: self.tree.config(cursor=""))

        self.load_attendance_data()

        self.control_frame = tk.Frame(self.right_frame, bg="#f0f0f0")
        self.control_frame.pack(fill="x", pady=5)

        # Nút Thoát với hiệu ứng hover
        self.exit_button = tk.Button(
            self.control_frame,
            text="Thoát",
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            relief="flat",
            command=self.root.quit
        )
        self.exit_button.pack(side="right", padx=10)
        # Thêm hiệu ứng hover
        self.exit_button.bind("<Enter>", lambda e: self.exit_button.config(bg="#ef5350"))
        self.exit_button.bind("<Leave>", lambda e: self.exit_button.config(bg="#f44336"))

        self.update_time()

        self.is_running = False
        self.cap = None
        self.camera_width = camera_width
        self.camera_height = remaining_height
        self.stt_counter = 1

    def load_attendance_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        attendance_list = self.db.get_attendance_by_date()
        self.stt_counter = 1
        for record in attendance_list:
            emp_id = record['emp_id']
            check_in = record['check_in'].strftime("%H:%M:%S") if record['check_in'] else ""
            check_out = record['check_out'].strftime("%H:%M:%S") if record['check_out'] else ""
            self.tree.insert("", "end", values=(
                self.stt_counter,
                f"NV{emp_id:03d}",
                str(emp_id),
                check_in,
                check_out
            ))
            self.stt_counter += 1

    def add_attendance_record(self, stt, msnv, name, check_in, check_out=""):
        self.tree.insert("", 0, values=(stt, msnv, name, check_in, check_out))
        for index, item in enumerate(self.tree.get_children()):
            self.tree.set(item, "STT", index + 1)

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        current_date = datetime.now().strftime("%d/%m/%Y")
        self.date_label.config(text=current_date)
        self.root.after(1000, self.update_time)

    def set_recognition_result(self, result_text, success_recog=True, success_attend=True):
        self.result_label.config(text=result_text)
        if success_recog and success_attend:
            self.result_label.config(bg="green")
        elif success_recog and not success_attend:
            self.result_label.config(bg="orange")
        else:
            self.result_label.config(bg="red")

    def update_camera_frame(self, frame):
        frame_width = self.camera_width
        frame_height = self.camera_height
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (frame_width, frame_height))
        image = Image.fromarray(frame_resized)
        photo = ImageTk.PhotoImage(image)
        self.camera_label.config(image=photo)
        self.camera_label.image = photo

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Không thể mở camera")
            return False
        self.is_running = True
        return True

    def stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.camera_label.config(image="")

if __name__ == "__main__":
    root = tk.Tk()
    app = UI_FaceRecognition(root)
    root.mainloop()