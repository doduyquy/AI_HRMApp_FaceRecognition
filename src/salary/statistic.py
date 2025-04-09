import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import mysql.connector
from datetime import datetime, timedelta
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib
import sys

class StatisticApp:
    def __init__(self, parent, db_connection, db_cursor):
        self.parent = parent
        self.conn = db_connection
        self.cursor = db_cursor

        self.month_var = tk.StringVar(value=str(datetime.now().month))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.overtime_threshold_var = tk.StringVar(value="24")
        self.top_n_var = tk.StringVar(value="3")

        self.bg_color = "#f7f8fa"
        self.card_bg = "#ffffff"
        self.accent_color = "#0276f7"

        self.destroyed = False

        self.toplevel = self.parent.winfo_toplevel()
        self.toplevel.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_ui()

    def create_ui(self):
        self.canvas = tk.Canvas(self.parent, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.show_statistics()

        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_frame_configure(self, event=None):
        if hasattr(self, 'canvas') and self.canvas and self.canvas.winfo_exists():
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        if hasattr(self, 'canvas') and self.canvas and self.canvas.winfo_exists():
            self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def on_mousewheel(self, event):
        if hasattr(self, 'canvas') and self.canvas and self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def show_statistics(self):
        stats_frame = tk.Frame(self.scrollable_frame, bg=self.bg_color)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

<<<<<<< HEAD
        title_l = tk.Label(stats_frame, text="Thống Kê Nhân Sự", font=("Times New Roman", 20, "bold"), fg="#333333", bg=self.bg_color)
=======
        # Title
        title_l = tk.Label(stats_frame, text="Thống Kê Nhân Sự", font=("Times New Roman", 25, "bold"), fg="#333333", bg=self.bg_color)
>>>>>>> 2cbd1ea77ee9018b3d11b925820e2b56bca62c23
        title_l.pack(anchor="center", pady=(10, 20))

        summary_cards_frame = tk.Frame(stats_frame, bg=self.bg_color)
        summary_cards_frame.pack(fill=tk.X, pady=10)

        total_employees_card = tk.Frame(summary_cards_frame, bg=self.card_bg, bd=1, relief="solid")
        total_employees_card.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        tk.Label(total_employees_card, text="Tổng Nhân Viên", font=("Times New Roman", 12), bg=self.card_bg, fg="#666").pack(pady=(10, 0))
        self.total_employees_label = tk.Label(total_employees_card, text="0", font=("Times New Roman", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.total_employees_label.pack()
        tk.Label(total_employees_card, text="1.225% ↑ từ kỳ trước", font=("Times New Roman", 10), bg=self.card_bg, fg="#28A745").pack(pady=(0, 10))

        total_workdays_card = tk.Frame(summary_cards_frame, bg=self.card_bg, bd=1, relief="solid")
        total_workdays_card.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        tk.Label(total_workdays_card, text="Tổng Ngày Làm Việc", font=("Times New Roman", 12), bg=self.card_bg, fg="#666").pack(pady=(10, 0))
        self.total_workdays_label = tk.Label(total_workdays_card, text="0", font=("Times New Roman", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.total_workdays_label.pack()
        tk.Label(total_workdays_card, text="2.214% ↑ từ kỳ trước", font=("Times New Roman", 10), bg=self.card_bg, fg="#28A745").pack(pady=(0, 10))

        total_salary_card = tk.Frame(summary_cards_frame, bg=self.card_bg, bd=1, relief="solid")
        total_salary_card.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        tk.Label(total_salary_card, text="Tổng Lương", font=("Times New Roman", 12), bg=self.card_bg, fg="#666").pack(pady=(10, 0))
        self.total_salary_label = tk.Label(total_salary_card, text="0 VNĐ", font=("Times New Roman", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.total_salary_label.pack()
        tk.Label(total_salary_card, text="26.945% ↑ từ kỳ trước", font=("Times New Roman", 10), bg=self.card_bg, fg="#28A745").pack(pady=(0, 10))

        overtime_card = tk.Frame(summary_cards_frame, bg=self.card_bg, bd=1, relief="solid")
        overtime_card.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        tk.Label(overtime_card, text="Tăng Ca Trên 24h", font=("Times New Roman", 12), bg=self.card_bg, fg="#666").pack(pady=(10, 0))
        self.overtime_count_label = tk.Label(overtime_card, text="0", font=("Times New Roman", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.overtime_count_label.pack()
        tk.Label(overtime_card, text="1.066% ↑ từ kỳ trước", font=("Times New Roman", 10), bg=self.card_bg, fg="#28A745").pack(pady=(0, 10))

        filter_frame = tk.Frame(stats_frame, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        inner_f = tk.Frame(filter_frame, bg=self.bg_color)
        inner_f.pack(anchor="center")

        tk.Label(inner_f, text="Tháng:", font=("Times New Roman", 11), bg=self.bg_color).pack(side=tk.LEFT, padx=(0, 5))
        month_combo = ttk.Combobox(inner_f, textvariable=self.month_var, values=[str(i) for i in range(1, 13)], width=5, state="readonly")
        month_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(inner_f, text="Năm:", font=("Times New Roman", 11), bg=self.bg_color).pack(side=tk.LEFT, padx=(10, 5))
        year_combo = ttk.Combobox(inner_f, textvariable=self.year_var, values=[str(i) for i in range(2020, 2026)], width=6, state="readonly")
        year_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(inner_f, text="Giờ tăng ca tối thiểu:", font=("Times New Roman", 11), bg=self.bg_color).pack(side=tk.LEFT, padx=(10, 5))
        overtime_entry = ttk.Entry(inner_f, textvariable=self.overtime_threshold_var, width=5)
        overtime_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(inner_f, text="Top N lương cao:", font=("Times New Roman", 11), bg=self.bg_color).pack(side=tk.LEFT, padx=(10, 5))
        top_n_entry = ttk.Entry(inner_f, textvariable=self.top_n_var, width=5)
        top_n_entry.pack(side=tk.LEFT, padx=5)

        refresh_btn = tk.Button(inner_f, text="Cập nhật", command=self.load_statistics, bg="#28A745", fg="white", 
                                font=("Times New Roman", 11, "bold"), relief="flat", activebackground="#218838", cursor="hand2")
        refresh_btn.pack(side=tk.LEFT, padx=10)
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.config(bg="#218838"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.config(bg="#28A745"))

        chart_frame = tk.Frame(stats_frame, bg=self.bg_color)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        attendance_frame = tk.Frame(stats_frame, bg=self.bg_color)
        attendance_frame.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(attendance_frame, orient="vertical")
        self.attendance_tree = ttk.Treeview(attendance_frame, columns=("STT", "Mã NV", "Tên", "Đúng giờ", "Trễ", "Vắng"), 
                                            show="headings", height=5, yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.attendance_tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)

        self.attendance_tree.heading("STT", text="STT")
        self.attendance_tree.heading("Mã NV", text="Mã Nhân Viên")
        self.attendance_tree.heading("Tên", text="Tên Nhân Viên")
        self.attendance_tree.heading("Đúng giờ", text="Đúng Giờ")
        self.attendance_tree.heading("Trễ", text="Trễ")
        self.attendance_tree.heading("Vắng", text="Vắng")
        self.attendance_tree.column("STT", width=50, anchor="center")
        self.attendance_tree.column("Mã NV", width=100, anchor="center")
        self.attendance_tree.column("Tên", width=200, anchor="w")
        self.attendance_tree.column("Đúng giờ", width=100, anchor="center")
        self.attendance_tree.column("Trễ", width=100, anchor="center")
        self.attendance_tree.column("Vắng", width=100, anchor="center")

        self.attendance_tree.bind("<Double-1>", self.show_attendance_details)

        top_salary_frame = tk.Frame(stats_frame, bg=self.bg_color)
        top_salary_frame.pack(fill=tk.BOTH, expand=True)

        top_scroll_y = ttk.Scrollbar(top_salary_frame, orient="vertical")
        self.top_salary_tree = ttk.Treeview(top_salary_frame, columns=("STT", "Mã NV", "Tên", "Lương"), 
                                            show="headings", height=3, yscrollcommand=top_scroll_y.set)
        top_scroll_y.config(command=self.top_salary_tree.yview)
        top_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.top_salary_tree.pack(fill=tk.BOTH, expand=True)

        self.top_salary_tree.heading("STT", text="STT")
        self.top_salary_tree.heading("Mã NV", text="Mã Nhân Viên")
        self.top_salary_tree.heading("Tên", text="Tên Nhân Viên")
        self.top_salary_tree.heading("Lương", text="Tổng Lương")
        self.top_salary_tree.column("STT", width=50, anchor="center")
        self.top_salary_tree.column("Mã NV", width=100, anchor="center")
        self.top_salary_tree.column("Tên", width=200, anchor="w")
        self.top_salary_tree.column("Lương", width=150, anchor="center")

        style = ttk.Style()
        style.configure("Treeview", font=("Times New Roman", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Times New Roman", 11, "bold"), background="#9fd7f9", foreground="#000")

        self.load_statistics()

    def get_workdays_in_month(self, year, month):
        try:
            start_date = datetime(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            end_date = datetime(year, month, last_day)
            workdays = []
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() < 5:
                    workdays.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
            return workdays
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Giá trị ngày không hợp lệ: {e}")
            return []

    def show_attendance_details(self, event):
        item = self.attendance_tree.selection()
        if not item:
            return

        emp_id = self.attendance_tree.item(item, "values")[1]
        month = int(self.month_var.get())
        year = int(self.year_var.get())
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1])

        self.cursor.execute("""
            SELECT date, check_in
            FROM Attendance
            WHERE emp_id = %s AND date BETWEEN %s AND %s
        """, (emp_id, start_date, end_date))
        attendance_records = self.cursor.fetchall()

        workdays = self.get_workdays_in_month(year, month)
        attended_dates = [record['date'].strftime('%Y-%m-%d') for record in attendance_records if record['date']]
        absent_days = [day for day in workdays if day not in attended_dates]
        late_days = [record['date'].strftime('%Y-%m-%d') for record in attendance_records if record['check_in'] and record['check_in'].time() > datetime.strptime('08:00:00', '%H:%M:%S').time()]

        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Chi Tiết Chấm Công - Mã NV: {emp_id}")
        detail_window.geometry("500x400")
        detail_window.configure(bg="#fff")

        tk.Label(detail_window, text=f"Chi Tiết Chấm Công - Mã NV: {emp_id}", font=("Times New Roman", 12, "bold"), bg="#fff").pack(pady=10)

        details_frame = tk.Frame(detail_window, bg="#fff")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(details_frame, text=f"Ngày Trễ ({len(late_days)}):", bg="#fff", font=("Times New Roman", 11)).pack(anchor="w")
        late_text = tk.Text(details_frame, height=3, width=50, font=("Times New Roman", 10))
        late_text.insert(tk.END, "\n".join(late_days) or "Không có")
        late_text.config(state="disabled")
        late_text.pack(fill=tk.X, pady=5)

        tk.Label(details_frame, text=f"Ngày Vắng ({len(absent_days)}):", bg="#fff", font=("Times New Roman", 11)).pack(anchor="w")
        absent_text = tk.Text(details_frame, height=8, width=50, font=("Times New Roman", 10))
        absent_text.insert(tk.END, "\n".join(absent_days) or "Không có")
        absent_text.config(state="disabled")
        absent_text.pack(fill=tk.X, pady=5)

    def load_statistics(self):
        if not self.cursor:
            messagebox.showerror("Lỗi", "Không có kết nối đến cơ sở dữ liệu!")
            return

        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Tháng hoặc năm không hợp lệ!")
            return

        try:
            overtime_threshold = float(self.overtime_threshold_var.get())
        except ValueError:
            overtime_threshold = 24.0
            self.overtime_threshold_var.set("24")
        try:
            top_n = int(self.top_n_var.get())
        except ValueError:
            top_n = 3
            self.top_n_var.set("3")

        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day)

        self.cursor.execute("SELECT COUNT(*) AS total FROM Employees")
        total_employees = self.cursor.fetchone()['total']
        self.total_employees_label.config(text=str(total_employees))

        workdays = self.get_workdays_in_month(year, month)
        total_workdays = len(workdays)
        self.total_workdays_label.config(text=str(total_workdays))

        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        self.cursor.execute("""
            SELECT e.emp_id, e.first_name, e.last_name,
                   SUM(CASE WHEN TIME(a.check_in) <= '08:00:00' THEN 1 ELSE 0 END) AS on_time,
                   SUM(CASE WHEN TIME(a.check_in) > '08:00:00' THEN 1 ELSE 0 END) AS late,
                   COUNT(DISTINCT a.date) AS attended_days
            FROM Employees e
            LEFT JOIN Attendance a ON e.emp_id = a.emp_id AND a.date BETWEEN %s AND %s
            GROUP BY e.emp_id, e.first_name, e.last_name
        """, (start_date, end_date))
        attendance_data = self.cursor.fetchall()

        total_on_time = 0
        total_days = 0
        for idx, row in enumerate(attendance_data, 1):
            full_name = f"{row['last_name']} {row['first_name']}"
            on_time = row['on_time'] or 0
            late = row['late'] or 0
            attended_days = row['attended_days'] or 0
            absent = total_workdays - attended_days
            absent = max(absent, 0)
            total_on_time += on_time
            total_days += on_time + late
            self.attendance_tree.insert("", "end", values=(idx, row['emp_id'], full_name, on_time, late, absent))

        self.cursor.execute("""
            SELECT COUNT(DISTINCT emp_id) AS overtime_count
            FROM (
                SELECT emp_id, SUM(overtime_hours) AS total_overtime
                FROM Attendance
                WHERE date BETWEEN %s AND %s
                GROUP BY emp_id
                HAVING total_overtime > %s
            ) AS overtime_employees
        """, (start_date, end_date, overtime_threshold))
        overtime_count = self.cursor.fetchone()['overtime_count']
        self.overtime_count_label.config(text=f"{overtime_count}")

        for item in self.top_salary_tree.get_children():
            self.top_salary_tree.delete(item)

        self.cursor.execute("""
            SELECT e.emp_id, e.first_name, e.last_name, (p.base_salary + p.overtime_salary) AS total_salary
            FROM Employees e
            JOIN Payroll p ON e.emp_id = p.emp_id
            WHERE p.month_year = %s
            ORDER BY (p.base_salary + p.overtime_salary) DESC
            LIMIT %s
        """, (start_date.strftime('%Y-%m-01'), top_n))
        top_salaries = self.cursor.fetchall()
        for idx, row in enumerate(top_salaries, 1):
            full_name = f"{row['last_name']} {row['first_name']}"
            self.top_salary_tree.insert("", "end", values=(idx, row['emp_id'], full_name, f"{row['total_salary']:,.0f} VNĐ"))

        self.cursor.execute("""
            SELECT SUM(base_salary + overtime_salary) AS total_salary
            FROM Payroll
            WHERE month_year = %s
        """, (start_date.strftime('%Y-%m-01'),))
        total_salary = self.cursor.fetchone()['total_salary'] or 0
        self.total_salary_label.config(text=f"{total_salary:,.0f} VNĐ")

        self.cursor.execute("""
            SELECT month_year, SUM(base_salary + overtime_salary) AS total_salary
            FROM Payroll
            WHERE YEAR(month_year) = %s
            GROUP BY month_year
            ORDER BY month_year
        """, (year,))
        salary_data = self.cursor.fetchall()

        self.ax.clear()
        if salary_data:
            dates = [row['month_year'] for row in salary_data]
            salaries = [row['total_salary'] for row in salary_data]

            self.ax.plot(dates, salaries, marker='o', color=self.accent_color, linewidth=2)
            self.ax.set_title(f"Tổng Lương Theo Tháng ({year})", fontsize=12, pad=15)
            self.ax.set_xlabel("Tháng", fontsize=10)
            self.ax.set_ylabel("Tổng Lương (VNĐ)", fontsize=10)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            self.ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,.0f}".format(x)))
        else:
            self.ax.text(0.5, 0.5, f"Không có dữ liệu lương cho năm {year}", 
                         horizontalalignment='center', verticalalignment='center', 
                         transform=self.ax.transAxes, fontsize=12, color="red")
            self.ax.set_title(f"Tổng Lương Theo Tháng ({year})", fontsize=12, pad=15)
            self.ax.set_xlabel("Tháng", fontsize=10)
            self.ax.set_ylabel("Tổng Lương (VNĐ)", fontsize=10)

        self.canvas_widget.draw()

    def destroy(self):
        if self.destroyed:
            print("StatisticApp đã được hủy trước đó, bỏ qua.")
            return

        print("Bắt đầu hủy StatisticApp")
        try:
            # Gỡ sự kiện cuộn chuột
            if hasattr(self, 'canvas') and self.canvas is not None and self.canvas.winfo_exists():
                self.canvas.unbind_all("<MouseWheel>")
                print("Đã gỡ sự kiện MouseWheel")

            # Đóng biểu đồ Matplotlib
            if hasattr(self, 'fig') and self.fig is not None:
                plt.close(self.fig)
                print("Đã đóng fig")
                self.fig = None

            # Hủy các widget con
            if hasattr(self, 'attendance_tree') and self.attendance_tree is not None and self.attendance_tree.winfo_exists():
                self.attendance_tree.destroy()
                print("Đã hủy attendance_tree")
            if hasattr(self, 'top_salary_tree') and self.top_salary_tree is not None and self.top_salary_tree.winfo_exists():
                self.top_salary_tree.destroy()
                print("Đã hủy top_salary_tree")
            if hasattr(self, 'canvas_widget') and self.canvas_widget is not None and self.canvas_widget.get_tk_widget().winfo_exists():
                self.canvas_widget.get_tk_widget().destroy()
                print("Đã hủy canvas_widget")

            # Hủy scrollable_frame
            if hasattr(self, 'scrollable_frame') and self.scrollable_frame is not None and self.scrollable_frame.winfo_exists():
                for widget in self.scrollable_frame.winfo_children():
                    if widget.winfo_exists():
                        widget.destroy()
                        print(f"Đã hủy widget con của scrollable_frame: {widget}")
                self.scrollable_frame.destroy()
                print("Đã hủy scrollable_frame")

            # Hủy canvas và scrollbar
            if hasattr(self, 'canvas') and self.canvas is not None and self.canvas.winfo_exists():
                self.canvas.destroy()
                print("Đã hủy canvas")
            if hasattr(self, 'scrollbar') and self.scrollbar is not None and self.scrollbar.winfo_exists():
                self.scrollbar.destroy()
                print("Đã hủy scrollbar")

            # Đóng kết nối cơ sở dữ liệu nếu có
            if hasattr(self, 'cursor') and self.cursor is not None:
                try:
                    self.cursor.close()
                    print("Đã đóng cursor")
                except:
                    print("Không thể đóng cursor (có thể đã đóng trước đó)")
            if hasattr(self, 'conn') and self.conn is not None and self.conn.is_connected():
                try:
                    self.conn.close()
                    print("Đã đóng kết nối cơ sở dữ liệu")
                except:
                    print("Không thể đóng kết nối DB (có thể đã đóng trước đó)")

            # Đặt các thuộc tính về None
            self.canvas = None
            self.scrollable_frame = None
            self.canvas_widget = None
            self.attendance_tree = None
            self.top_salary_tree = None
            self.scrollbar = None
            self.cursor = None
            self.conn = None

            self.destroyed = True
            print("Kết thúc hủy StatisticApp")

        except Exception as e:
            print(f"Lỗi trong destroy StatisticApp: {e}")

    def on_close(self):
        print("Người dùng nhấn nút đóng cửa sổ")
        try:
            self.destroy()
            if self.toplevel.winfo_exists():
                self.toplevel.destroy()  # Đóng toplevel thay vì parent để tránh xung đột
            print("Đã đóng cửa sổ gốc")
            sys.exit(0)  # Thoát hoàn toàn chương trình
        except Exception as e:
            print(f"Lỗi trong on_close: {e}")
            sys.exit(1)  # Thoát với mã lỗi nếu có vấn đề

if __name__ == "__main__":
    root = tk.Tk()
    app = StatisticApp(root, None, None)
    root.mainloop()