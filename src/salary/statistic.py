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

        # Khởi tạo các biến với giá trị mặc định
        self.month_var = tk.StringVar(value="Tất cả")
        self.year_var = tk.StringVar(value="Tất cả")
        self.overtime_threshold_var = tk.StringVar(value="24")
        self.top_n_var = tk.StringVar(value="")  # Để trống để người dùng nhập tự do

        self.bg_color = "#f7f8fa"
        self.card_bg = "#ffffff"
        self.accent_color = "#0276f7"

        self.destroyed = False

        self.toplevel = self.parent.winfo_toplevel()
        self.toplevel.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_ui()

    def create_ui(self):
        # Tạo canvas chính với thanh cuộn
        self.canvas = tk.Canvas(self.parent, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=0)

        self.scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.show_statistics()

        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def show_statistics(self):
        # Tạo frame chính cho thống kê
        stats_frame = tk.Frame(self.scrollable_frame, bg=self.bg_color)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Tiêu đề
        title_l = tk.Label(stats_frame, text="Thống Kê Nhân Sự", font=("Times New Roman", 25, "bold"), fg="#333333", bg=self.bg_color)
        title_l.pack(anchor="center", pady=(0, 5))

        # Frame chứa các thẻ tóm tắt
        summary_cards_frame = tk.Frame(stats_frame, bg=self.bg_color)
        summary_cards_frame.pack(fill=tk.X, pady=10)

        # Thẻ Tổng Nhân Viên
        total_employees_card = tk.Frame(summary_cards_frame, bg=self.card_bg, bd=1, relief="solid")
        total_employees_card.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        tk.Label(total_employees_card, text="Tổng Nhân Viên", font=("Times New Roman", 12), bg=self.card_bg, fg="#666").pack(pady=(10, 0))
        self.total_employees_label = tk.Label(total_employees_card, text="0", font=("Times New Roman", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.total_employees_label.pack()
        self.total_employees_growth_label = tk.Label(total_employees_card, text="Không có dữ liệu kỳ trước", font=("Times New Roman", 10), bg=self.card_bg, fg="#28A745")
        self.total_employees_growth_label.pack(pady=(0, 10))

        # Thẻ Tổng Ngày Làm Việc
        total_workdays_card = tk.Frame(summary_cards_frame, bg=self.card_bg, bd=1, relief="solid")
        total_workdays_card.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        tk.Label(total_workdays_card, text="Tổng Ngày Làm Việc", font=("Times New Roman", 12), bg=self.card_bg, fg="#666").pack(pady=(10, 0))
        self.total_workdays_label = tk.Label(total_workdays_card, text="0", font=("Times New Roman", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.total_workdays_label.pack()
        self.total_workdays_growth_label = tk.Label(total_workdays_card, text="Không có dữ liệu kỳ trước", font=("Times New Roman", 10), bg=self.card_bg, fg="#28A745")
        self.total_workdays_growth_label.pack(pady=(0, 10))

        # Thẻ Tổng Lương
        total_salary_card = tk.Frame(summary_cards_frame, bg=self.card_bg, bd=1, relief="solid")
        total_salary_card.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        tk.Label(total_salary_card, text="Tổng Lương", font=("Times New Roman", 12), bg=self.card_bg, fg="#666").pack(pady=(10, 0))
        self.total_salary_label = tk.Label(total_salary_card, text="0 VNĐ", font=("Times New Roman", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.total_salary_label.pack()
        self.total_salary_growth_label = tk.Label(total_salary_card, text="Không có dữ liệu kỳ trước", font=("Times New Roman", 10), bg=self.card_bg, fg="#28A745")
        self.total_salary_growth_label.pack(pady=(0, 10))

        # Thẻ Tăng Ca
        overtime_card = tk.Frame(summary_cards_frame, bg=self.card_bg, bd=1, relief="solid")
        overtime_card.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        tk.Label(overtime_card, text="Tăng Ca Trên 24h", font=("Times New Roman", 12), bg=self.card_bg, fg="#666").pack(pady=(10, 0))
        self.overtime_count_label = tk.Label(overtime_card, text="0", font=("Times New Roman", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.overtime_count_label.pack()
        self.overtime_growth_label = tk.Label(overtime_card, text="Không có dữ liệu kỳ trước", font=("Times New Roman", 10), bg=self.card_bg, fg="#28A745")
        self.overtime_growth_label.pack(pady=(0, 10))

        # Frame chứa biểu đồ
        chart_frame = tk.Frame(stats_frame, bg=self.bg_color)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tăng kích thước biểu đồ và điều chỉnh tỷ lệ
        self.fig, self.ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame chứa bộ lọc
        filter_frame = tk.Frame(stats_frame, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        inner_f = tk.Frame(filter_frame, bg=self.bg_color)
        inner_f.pack(anchor="center")

        # Bộ lọc Tháng
        tk.Label(inner_f, text="Tháng:", font=("Times New Roman", 11), bg=self.bg_color).pack(side=tk.LEFT, padx=(0, 5))
        month_combo = ttk.Combobox(inner_f, textvariable=self.month_var, values=["Tất cả"] + [str(i) for i in range(1, 13)], width=5, state="readonly")
        month_combo.pack(side=tk.LEFT, padx=5)

        # Bộ lọc Năm
        tk.Label(inner_f, text="Năm:", font=("Times New Roman", 11), bg=self.bg_color).pack(side=tk.LEFT, padx=(10, 5))
        year_combo = ttk.Combobox(inner_f, textvariable=self.year_var, values=["Tất cả"] + [str(i) for i in range(2020, 2026)], width=6, state="readonly")
        year_combo.pack(side=tk.LEFT, padx=5)

        # Giờ tăng ca tối thiểu
        tk.Label(inner_f, text="Giờ tăng ca tối thiểu:", font=("Times New Roman", 11), bg=self.bg_color).pack(side=tk.LEFT, padx=(10, 5))
        overtime_entry = ttk.Entry(inner_f, textvariable=self.overtime_threshold_var, width=5)
        overtime_entry.pack(side=tk.LEFT, padx=5)

        # Top N lương cao
        tk.Label(inner_f, text="Top N lương cao:", font=("Times New Roman", 11), bg=self.bg_color).pack(side=tk.LEFT, padx=(10, 5))
        top_n_entry = ttk.Entry(inner_f, textvariable=self.top_n_var, width=5)
        top_n_entry.pack(side=tk.LEFT, padx=5)

        # Nút Cập nhật
        refresh_btn = tk.Button(inner_f, text="Cập nhật", command=self.load_statistics, bg="#28A745", fg="white",
                                font=("Times New Roman", 11, "bold"), relief="flat", activebackground="#218838", cursor="hand2")
        refresh_btn.pack(side=tk.LEFT, padx=10)
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.config(bg="#218838"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.config(bg="#28A745"))

        # Frame chứa bảng thống kê tổng hợp
        combined_frame = tk.Frame(stats_frame, bg=self.bg_color)
        combined_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tiêu đề cho bảng tổng hợp
        combined_label = tk.Label(combined_frame, text="Thống Kê Lương và Chấm Công", 
                                  font=("Times New Roman", 14, "bold"), bg=self.bg_color, fg="#0276f7")
        combined_label.pack(anchor="w", pady=(0, 5))

        # Thanh cuộn cho bảng tổng hợp
        scroll_y = ttk.Scrollbar(combined_frame, orient="vertical")
        self.combined_tree = ttk.Treeview(combined_frame, 
                                          columns=("STT", "Mã NV", "Tên NV", "Tổng Lương", "Đúng Giờ", "Trễ", "Vắng"), 
                                          show="headings", height=8, yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.combined_tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.combined_tree.pack(fill=tk.BOTH, expand=True)

        # Cấu hình cột cho bảng tổng hợp
        self.combined_tree.heading("STT", text="STT")
        self.combined_tree.heading("Mã NV", text="Mã Nhân Viên")
        self.combined_tree.heading("Tên NV", text="Tên Nhân Viên")
        self.combined_tree.heading("Tổng Lương", text="Tổng Lương")
        self.combined_tree.heading("Đúng Giờ", text="Đúng Giờ")
        self.combined_tree.heading("Trễ", text="Trễ")
        self.combined_tree.heading("Vắng", text="Vắng")
        self.combined_tree.column("STT", width=50, anchor="center")
        self.combined_tree.column("Mã NV", width=100, anchor="center")
        self.combined_tree.column("Tên NV", width=200, anchor="w")
        self.combined_tree.column("Tổng Lương", width=150, anchor="center")
        self.combined_tree.column("Đúng Giờ", width=100, anchor="center")
        self.combined_tree.column("Trễ", width=100, anchor="center")
        self.combined_tree.column("Vắng", width=100, anchor="center")

        # Gắn sự kiện nhấp đúp để xem chi tiết chấm công
        self.combined_tree.bind("<Double-1>", self.show_attendance_details)

        # Cấu hình style cho Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Times New Roman", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Times New Roman", 11, "bold"), background="#9fd7f9", foreground="#000")

        self.load_statistics()

    def load_statistics(self):
        if not self.cursor:
            messagebox.showerror("Lỗi", "Không có kết nối đến cơ sở dữ liệu!")
            return

        month_str = self.month_var.get()
        year_str = self.year_var.get()

        # Xử lý khi chọn "Tất cả"
        if month_str == "Tất cả" or year_str == "Tất cả":
            start_date = None
            end_date = None
        else:
            try:
                month = int(month_str)
                year = int(year_str)
            except ValueError:
                messagebox.showerror("Lỗi", "Tháng hoặc năm không hợp lệ!")
                return

            start_date = datetime(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            end_date = datetime(year, month, last_day)

        try:
            overtime_threshold = float(self.overtime_threshold_var.get())
        except ValueError:
            overtime_threshold = 24.0
            self.overtime_threshold_var.set("24")

        # Xử lý giá trị top_n từ người dùng nhập
        try:
            top_n = int(self.top_n_var.get()) if self.top_n_var.get().strip() else 5  # Mặc định là 5 nếu không nhập
            if top_n <= 0:
                top_n = 5  # Đảm bảo top_n là số dương
        except ValueError:
            top_n = 5  # Mặc định là 5 nếu nhập sai
            self.top_n_var.set("5")

        # Tính ngày bắt đầu và kết thúc cho tháng trước (nếu có)
        if start_date and end_date:
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            prev_last_day = calendar.monthrange(prev_year, prev_month)[1]
            prev_start_date = datetime(prev_year, prev_month, 1)
            prev_end_date = datetime(prev_year, prev_month, prev_last_day)
        else:
            prev_start_date = None
            prev_end_date = None

        # Tổng nhân viên
        self.cursor.execute("SELECT COUNT(*) AS total FROM Employees")
        total_employees = self.cursor.fetchone()['total']
        self.total_employees_label.config(text=str(total_employees))
        self.total_employees_growth_label.config(text="Không thay đổi", fg="#666")

        # Tổng ngày làm việc
        if start_date and end_date:
            workdays = self.get_workdays_in_month(year, month)
            total_workdays = len(workdays)
            prev_workdays = self.get_workdays_in_month(prev_year, prev_month) if prev_start_date else []
            prev_total_workdays = len(prev_workdays)
        else:
            self.cursor.execute("SELECT MIN(date), MAX(date) FROM Attendance")
            date_range = self.cursor.fetchone()
            if date_range['MIN(date)'] and date_range['MAX(date)']:
                min_date = date_range['MIN(date)']
                max_date = date_range['MAX(date)']
                workdays = []
                current_date = min_date
                while current_date <= max_date:
                    if current_date.weekday() < 5:
                        workdays.append(current_date.strftime('%Y-%m-%d'))
                    current_date += timedelta(days=1)
                total_workdays = len(workdays)
                prev_total_workdays = 0
            else:
                total_workdays = 0
                prev_total_workdays = 0

        self.total_workdays_label.config(text=str(total_workdays))
        if prev_total_workdays > 0:
            workdays_growth = ((total_workdays - prev_total_workdays) / prev_total_workdays) * 100
            workdays_growth_text = f"{workdays_growth:.3f}% {'↑' if workdays_growth >= 0 else '↓'} từ kỳ trước"
            fg_color = "#28A745" if workdays_growth >= 0 else "#DC3545"
        else:
            workdays_growth_text = "Không có dữ liệu kỳ trước"
            fg_color = "#666"
        self.total_workdays_growth_label.config(text=workdays_growth_text, fg=fg_color)

        # Tổng lương
        if start_date and end_date:
            self.cursor.execute("""
                SELECT SUM(base_salary + overtime_salary) AS total_salary
                FROM Payroll
                WHERE month_year = %s
            """, (start_date.strftime('%Y-%m-01'),))
            current_total_salary = self.cursor.fetchone()['total_salary'] or 0

            self.cursor.execute("""
                SELECT SUM(base_salary + overtime_salary) AS total_salary
                FROM Payroll
                WHERE month_year = %s
            """, (prev_start_date.strftime('%Y-%m-01'),))
            prev_total_salary = self.cursor.fetchone()['total_salary'] or 0
        else:
            self.cursor.execute("""
                SELECT SUM(base_salary + overtime_salary) AS total_salary
                FROM Payroll
            """)
            current_total_salary = self.cursor.fetchone()['total_salary'] or 0
            prev_total_salary = 0

        self.total_salary_label.config(text=f"{current_total_salary:,.0f} VNĐ")
        if prev_total_salary > 0:
            salary_growth = ((current_total_salary - prev_total_salary) / prev_total_salary) * 100
            salary_growth_text = f"{salary_growth:.3f}% {'↑' if salary_growth >= 0 else '↓'} từ kỳ trước"
            fg_color = "#28A745" if salary_growth >= 0 else "#DC3545"
        else:
            salary_growth_text = "Không có dữ liệu kỳ trước"
            fg_color = "#666"
        self.total_salary_growth_label.config(text=salary_growth_text, fg=fg_color)

        # Tăng ca trên ngưỡng
        if start_date and end_date:
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
            current_overtime_count = self.cursor.fetchone()['overtime_count']

            self.cursor.execute("""
                SELECT COUNT(DISTINCT emp_id) AS overtime_count
                FROM (
                    SELECT emp_id, SUM(overtime_hours) AS total_overtime
                    FROM Attendance
                    WHERE date BETWEEN %s AND %s
                    GROUP BY emp_id
                    HAVING total_overtime > %s
                ) AS overtime_employees
            """, (prev_start_date, prev_end_date, overtime_threshold))
            prev_overtime_count = self.cursor.fetchone()['overtime_count'] or 0
        else:
            self.cursor.execute("""
                SELECT COUNT(DISTINCT emp_id) AS overtime_count
                FROM (
                    SELECT emp_id, SUM(overtime_hours) AS total_overtime
                    FROM Attendance
                    GROUP BY emp_id
                    HAVING total_overtime > %s
                ) AS overtime_employees
            """, (overtime_threshold,))
            current_overtime_count = self.cursor.fetchone()['overtime_count']
            prev_overtime_count = 0

        self.overtime_count_label.config(text=f"{current_overtime_count}")
        if prev_overtime_count > 0:
            overtime_growth = ((current_overtime_count - prev_overtime_count) / prev_overtime_count) * 100
            overtime_growth_text = f"{overtime_growth:.3f}% {'↑' if overtime_growth >= 0 else '↓'} từ kỳ trước"
            fg_color = "#28A745" if overtime_growth >= 0 else "#DC3545"
        else:
            overtime_growth_text = "Không có dữ liệu kỳ trước"
            fg_color = "#666"
        self.overtime_growth_label.config(text=overtime_growth_text, fg=fg_color)

        # Cập nhật combined_tree
        for item in self.combined_tree.get_children():
            self.combined_tree.delete(item)

        if start_date and end_date:
            self.cursor.execute("""
                SELECT 
                    e.emp_id, 
                    e.first_name, 
                    e.last_name,
                    SUM(CASE WHEN TIME(a.check_in) <= '08:00:00' THEN 1 ELSE 0 END) AS on_time,
                    SUM(CASE WHEN TIME(a.check_in) > '08:00:00' THEN 1 ELSE 0 END) AS late,
                    COUNT(DISTINCT a.date) AS attended_days,
                    COALESCE(SUM(p.base_salary + p.overtime_salary), 0) AS total_salary
                FROM Employees e
                LEFT JOIN Attendance a ON e.emp_id = a.emp_id AND a.date BETWEEN %s AND %s
                LEFT JOIN Payroll p ON e.emp_id = p.emp_id AND p.month_year = %s
                GROUP BY e.emp_id, e.first_name, e.last_name
                ORDER BY total_salary DESC
                LIMIT %s
            """, (start_date, end_date, start_date.strftime('%Y-%m-01'), top_n))
            combined_data = self.cursor.fetchall()
            workdays = self.get_workdays_in_month(year, month)
            total_workdays = len(workdays)
        else:
            self.cursor.execute("""
                SELECT 
                    e.emp_id, 
                    e.first_name, 
                    e.last_name,
                    SUM(CASE WHEN TIME(a.check_in) <= '08:00:00' THEN 1 ELSE 0 END) AS on_time,
                    SUM(CASE WHEN TIME(a.check_in) > '08:00:00' THEN 1 ELSE 0 END) AS late,
                    COUNT(DISTINCT a.date) AS attended_days,
                    COALESCE(SUM(p.base_salary + p.overtime_salary), 0) AS total_salary
                FROM Employees e
                LEFT JOIN Attendance a ON e.emp_id = a.emp_id
                LEFT JOIN Payroll p ON e.emp_id = p.emp_id
                GROUP BY e.emp_id, e.first_name, e.last_name
                ORDER BY total_salary DESC
                LIMIT %s
            """, (top_n,))
            combined_data = self.cursor.fetchall()
            self.cursor.execute("SELECT MIN(date), MAX(date) FROM Attendance")
            date_range = self.cursor.fetchone()
            if date_range['MIN(date)'] and date_range['MAX(date)']:
                min_date = date_range['MIN(date)']
                max_date = date_range['MAX(date)']
                workdays = []
                current_date = min_date
                while current_date <= max_date:
                    if current_date.weekday() < 5:
                        workdays.append(current_date.strftime('%Y-%m-%d'))
                    current_date += timedelta(days=1)
                total_workdays = len(workdays)
            else:
                total_workdays = 0

        if combined_data:
            for idx, row in enumerate(combined_data, 1):
                full_name = f"{row['last_name']} {row['first_name']}"
                on_time = row['on_time'] or 0
                late = row['late'] or 0
                attended_days = row['attended_days'] or 0
                absent = total_workdays - attended_days
                absent = max(absent, 0)
                total_salary = row['total_salary'] or 0
                self.combined_tree.insert("", "end", values=(
                    idx, 
                    row['emp_id'], 
                    full_name, 
                    f"{total_salary:,.0f} VNĐ", 
                    on_time, 
                    late, 
                    absent
                ))
        else:
            self.combined_tree.insert("", "end", values=("", "", "Không có dữ liệu", "", "", "", ""))

        # Cập nhật biểu đồ
        if year_str == "Tất cả":
            self.cursor.execute("""
                SELECT month_year, SUM(base_salary + overtime_salary) AS total_salary
                FROM Payroll
                GROUP BY month_year
                ORDER BY month_year
            """)
            chart_title = "Tổng Lương Theo Tháng (Tất cả)"
        else:
            try:
                year = int(year_str)
            except ValueError:
                messagebox.showerror("Lỗi", "Năm không hợp lệ!")
                return
            self.cursor.execute("""
                SELECT month_year, SUM(base_salary + overtime_salary) AS total_salary
                FROM Payroll
                WHERE YEAR(month_year) = %s
                GROUP BY month_year
                ORDER BY month_year
            """, (year,))
            chart_title = f"Tổng Lương Theo Tháng ({year})"

        salary_data = self.cursor.fetchall()
        self.ax.clear()
        if salary_data:
            dates = [row['month_year'] for row in salary_data]
            salaries = [row['total_salary'] for row in salary_data]
            self.ax.plot(dates, salaries, marker='o', color=self.accent_color, linewidth=2)
            self.ax.set_title(chart_title, fontsize=12, pad=15)
            self.ax.set_xlabel("Tháng", fontsize=10)
            self.ax.set_ylabel("Tổng Lương (VNĐ)", fontsize=10)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            self.ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,.0f}".format(x)))
        else:
            self.ax.text(0.5, 0.5, f"Không có dữ liệu lương", 
                         horizontalalignment='center', verticalalignment='center', 
                         transform=self.ax.transAxes, fontsize=12, color="red")
            self.ax.set_title(chart_title, fontsize=12, pad=15)
            self.ax.set_xlabel("Tháng", fontsize=10)
            self.ax.set_ylabel("Tổng Lương (VNĐ)", fontsize=10)
        self.canvas_widget.draw()

    def show_attendance_details(self, event):
        item = self.combined_tree.selection()
        if not item:
            return

        emp_id = self.combined_tree.item(item, "values")[1]
        month_str = self.month_var.get()
        year_str = self.year_var.get()

        if month_str == "Tất cả" or year_str == "Tất cả":
            self.cursor.execute("""
                SELECT date, check_in
                FROM Attendance
                WHERE emp_id = %s
            """, (emp_id,))
            attendance_records = self.cursor.fetchall()

            if attendance_records:
                dates = [record['date'] for record in attendance_records if record['date']]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    workdays = []
                    current_date = min_date
                    while current_date <= max_date:
                        if current_date.weekday() < 5:
                            workdays.append(current_date.strftime('%Y-%m-%d'))
                        current_date += timedelta(days=1)
                else:
                    workdays = []
            else:
                workdays = []
        else:
            try:
                month = int(month_str)
                year = int(year_str)
            except ValueError:
                messagebox.showerror("Lỗi", "Tháng hoặc năm không hợp lệ!")
                return

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
        late_days = [record['date'].strftime('%Y-%m-%d') for record in attendance_records 
                     if record['check_in'] and record['check_in'].time() > datetime.strptime('08:00:00', '%H:%M:%S').time()]

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

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_workdays_in_month(self, year, month):
        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day)
        workdays = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Thứ 2 đến Thứ 6
                workdays.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        return workdays

    def destroy(self):
        if not self.destroyed:
            self.destroyed = True
            try:
                self.canvas.destroy()
                self.scrollbar.destroy()
                plt.close(self.fig)
                self.parent.destroy()
                self.toplevel.destroy()  # Đảm bảo đóng cửa sổ chính
            except Exception as e:
                print(f"Error during destroy: {e}")

    def on_close(self):
        # Hiển thị hộp thoại xác nhận (tùy chọn)
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát ứng dụng?"):
            self.destroy()
            # Đóng toàn bộ ứng dụng
            try:
                if "root" in globals():
                    globals()["root"].destroy()
                else:
                    self.toplevel.quit()  # Thoát ứng dụng nếu không có root toàn cục
            except Exception as e:
                print(f"Error during on_close: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StatisticApp(root, None, None)
    root.mainloop()