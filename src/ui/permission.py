import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from tkinter import Toplevel, Label, Button
from modules.IT.data_user import DataUser
import pandas as pd
from tkinter import filedialog

class PermissionApp:
    def __init__(self, parent):
        self.parent = parent
        self.data_user = DataUser()
        self.bg_color = "#f7f8fa"
        self.current_content = None
        self.search_entry = None
        self.search_var = None
        self.toggle_on_img = None
        self.toggle_off_img = None
        self.image_references = {}
        self.toggle_widgets = {}
        self.edit_mode = False
        self.current_role = None
        self.temp_actions = {}

        self.content_frame = tk.Frame(self.parent.content_frame, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.show_permission_list()

    def clear_content(self):
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None
        self.image_references.clear()
        for widget in self.toggle_widgets.values():
            widget.destroy()
        self.toggle_widgets.clear()
        self.temp_actions.clear()

    
    def destroy(self):
        self.clear_content()  # Clear toggle widgets and temp_actions
        self.image_references.clear()
        self.toggle_on_img = None
        self.toggle_off_img = None
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None
      
    def show_permission_list(self):
        self.clear_content()
        self.current_content = tk.Frame(self.content_frame, bg=self.bg_color)
        self.current_content.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.current_content, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=2, padx=5)

        buttons_inner_frame = tk.Frame(button_frame, bg=self.bg_color)
        buttons_inner_frame.pack(anchor="center")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(BASE_DIR, "..", "img")

        try:
            add_img = Image.open(os.path.join(img_dir, "add.png")).resize((22, 22))
            edit_img = Image.open(os.path.join(img_dir, "edit.png")).resize((22, 22))
            delete_img = Image.open(os.path.join(img_dir, "delete.png")).resize((22, 22))
            reset_img = Image.open(os.path.join(img_dir, "reset.png")).resize((22, 22))
            search_img = Image.open(os.path.join(img_dir, "search.png")).resize((22, 22))
            excel_img = Image.open(os.path.join(img_dir, "excel.png")).resize((22, 22))  # Load excel.png
            toggle_on_img = Image.open(os.path.join(img_dir, "toggle_on.png")).resize((30, 15))
            toggle_off_img = Image.open(os.path.join(img_dir, "toggle_off.png")).resize((30, 15))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hình ảnh: {str(e)}")
            return

        add_icon = ImageTk.PhotoImage(add_img)
        edit_icon = ImageTk.PhotoImage(edit_img)
        delete_icon = ImageTk.PhotoImage(delete_img)
        reset_icon = ImageTk.PhotoImage(reset_img)
        search_icon = ImageTk.PhotoImage(search_img)
        excel_icon = ImageTk.PhotoImage(excel_img)  # Excel icon
        self.toggle_on_img = ImageTk.PhotoImage(toggle_on_img)
        self.toggle_off_img = ImageTk.PhotoImage(toggle_off_img)

        add_button = tk.Button(buttons_inner_frame, 
            text="Thêm", image=add_icon, compound=tk.TOP,
            command=self.show_add_permission,
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#adedb0")
        add_button.image = add_icon
        add_button.pack(side=tk.LEFT, padx=3)

        edit_button = tk.Button(buttons_inner_frame, 
            text="Sửa", image=edit_icon, compound=tk.TOP,
            command=self.edit_permission,
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#f2c47e")
        edit_button.image = edit_icon
        edit_button.pack(side=tk.LEFT, padx=3)

        delete_button = tk.Button(buttons_inner_frame, 
            text="Xóa", image=delete_icon, compound=tk.TOP,
            command=self.show_delete_permission,
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#f57a7a")
        delete_button.image = delete_icon
        delete_button.pack(side=tk.LEFT, padx=3)

        reset_button = tk.Button(buttons_inner_frame,
            text="Làm mới", image=reset_icon, compound=tk.TOP,
            command=self.reset_permission_list, 
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#7d8e96")
        reset_button.image = reset_icon 
        reset_button.pack(side=tk.LEFT, padx=3)

        excel_button = tk.Button(buttons_inner_frame, 
            text="Excel", image=excel_icon, compound=tk.TOP,
            command=self.export_to_excel,
            bg="#f7f8fa", bd=0, width=60, height=60,
            font=("Times New Roman", 9), relief="flat",
            activebackground="#65f06b")
        excel_button.image = excel_icon
        excel_button.pack(side=tk.LEFT, padx=3)

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
        self.search_entry.insert(0, "Tìm kiếm quyền hoặc chức năng...")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_placeholder)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))

        search_button = tk.Button(
            search_frame,
            image=search_icon,
            command=self.search_permission,
            bg="white",
            bd=0,
            relief="flat",
            activebackground="#fff",
            width=20,
            height=25
        )
        search_button.image = search_icon
        search_button.pack(side=tk.RIGHT, padx=(2, 5))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Times New Roman", 10, "bold"), background="#9fd7f9", foreground="#000", relief="flat", borderwidth=0, padding=5)
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "#e5e5e5")], foreground=[("selected", "black")])

        columns = ("Mã nhóm quyền", "Tên quyền", "Danh mục chức năng", "Xem", "Tạo mới", "Cập nhật", "Xóa")
        self.tree = ttk.Treeview(self.current_content, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("Mã nhóm quyền", width=100, anchor="center")
        self.tree.column("Tên quyền", width=150, anchor="center")
        self.tree.column("Danh mục chức năng", width=200, anchor="w")
        self.tree.column("Xem", width=60, anchor="center")
        self.tree.column("Tạo mới", width=80, anchor="center")
        self.tree.column("Cập nhật", width=80, anchor="center")
        self.tree.column("Xóa", width=60, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.tag_configure("toggle", font=("Arial", 12))
        self.tree.bind("<Configure>", self.update_toggle_positions)

        self.load_permission_data()
        
    def export_to_excel(self):
            # Get data from Treeview
        columns = ["Mã nhóm quyền", "Tên quyền", "Danh mục chức năng", "Xem", "Tạo mới", "Cập nhật", "Xóa"]
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values'][:3]  # Get role_id, role_name, function_name
            item_id = item
            actions = self.temp_actions.get(item_id, [])
            # Map actions to "Có" (Yes) or "Không" (No)
            view = "Có" if "view" in actions else "Không"
            create = "Có" if "create" in actions else "Không"
            update = "Có" if "update" in actions else "Không"
            delete = "Có" if "delete" in actions else "Không"
            data.append(list(values) + [view, create, update, delete])

        if not data:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất sang Excel!")
            return

         # Create DataFrame
        df = pd.DataFrame(data, columns=columns)

            # Set default filename
        default_filename = "DanhSachPhanQuyen.xlsx"

            # Open file dialog to choose save location
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Chọn nơi lưu file Excel"
        )

            # Check if user canceled the dialog
        if not file_path:
            return

        try:
                # Export to Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            messagebox.showinfo("Thành công", f"Dữ liệu đã được xuất sang {file_path}!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi xuất file: {str(e)}")
            
    def load_permission_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for widget in self.toggle_widgets.values():
            widget.destroy()
        self.toggle_widgets.clear()

        role_details = self.data_user.fetch_role_details()
        for detail in role_details:
            role_id, role_name, function_id, function_name, actions = detail
            item_id = self.tree.insert("", "end", values=(role_id, role_name, function_name, "", "", "", ""),
                                    tags=("toggle",))
            self.tree.item(item_id, tags=(f"toggle_{role_id}_{function_id}",))
            self.temp_actions[item_id] = actions.copy() if actions else []
            self.embed_toggle_images(item_id, role_id, function_id, actions)

        if not role_details:
            messagebox.showinfo("Thông báo", "Không có dữ liệu quyền nào trong cơ sở dữ liệu!")
        self.tree.update_idletasks()
        self.update_toggle_positions()

    def embed_toggle_images(self, item_id, role_id, function_id, actions):
        self.tree.update_idletasks()
        bbox = self.tree.bbox(item_id)
        if not bbox:
            return

        x, y, width, height = bbox
        row_height = height
        col_widths = [self.tree.column(col, "width") for col in self.tree["columns"]]
        col_positions = [sum(col_widths[:i]) for i in range(len(col_widths))]

        valid_actions = [action for action in actions if action in ['view', 'create', 'update', 'delete']]

        for idx, action in enumerate(["view", "create", "update", "delete"]):
            col_idx = idx + 3
            img = self.toggle_on_img if action in valid_actions else self.toggle_off_img
            key = f"{item_id}_{action}"
            if key in self.toggle_widgets:
                label = self.toggle_widgets[key]
                label.configure(image=img)
                label.image = img
            else:
                label = tk.Label(self.tree, image=img, borderwidth=0)
                label.image = img
                self.toggle_widgets[key] = label

            toggle_x = col_positions[col_idx] + (col_widths[col_idx] // 2) - 15
            toggle_y = y + (row_height // 2) - 7
            label.place(x=toggle_x, y=toggle_y)

            if self.edit_mode:
                label.bind("<Button-1>", lambda event, item=item_id, action=action: self.on_toggle_click(item, action))
            else:
                label.unbind("<Button-1>")

    def update_toggle_positions(self, event=None):
        for item_id in self.tree.get_children():
            role_id = self.tree.item(item_id, "values")[0]
            function_name = self.tree.item(item_id, "values")[2]
            function_id = self.data_user.fetch_function_id_by_name(function_name)
            if function_id is None:
                continue
            actions = self.temp_actions.get(item_id, [])
            self.embed_toggle_images(item_id, role_id, function_id, actions)

    def on_toggle_click(self, item_id, action):
        if not self.edit_mode:
            return

        current_actions = self.temp_actions.get(item_id, [])
        if action in current_actions:
            current_actions.remove(action)
            new_img = self.toggle_off_img
        else:
            current_actions.append(action)
            new_img = self.toggle_on_img

        self.temp_actions[item_id] = current_actions

        label = self.toggle_widgets[f"{item_id}_{action}"]
        label.configure(image=new_img)
        label.image = new_img

    def search_permission(self):
        search_term = self.search_var.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for widget in self.toggle_widgets.values():
            widget.destroy()
        self.toggle_widgets.clear()

        role_details = self.data_user.search_roles(search_term)
        for detail in role_details:
            role_id, role_name, function_id, function_name, actions = detail
            item_id = self.tree.insert("", "end", values=(role_id, role_name, function_name, "", "", "", ""),
                                       tags=("toggle",))
            self.tree.item(item_id, tags=(f"toggle_{role_id}_{function_id}",))
            self.temp_actions[item_id] = actions.copy() if actions else []
            self.embed_toggle_images(item_id, role_id, function_id, actions)

        if not role_details:
            messagebox.showinfo("Thông báo", "Không tìm thấy quyền hoặc chức năng nào!")

    def reset_permission_list(self):
        self.search_var.set("")
        self.search_entry.config(fg="gray")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Tìm kiếm quyền hoặc chức năng...")
        self.load_permission_data()

    def _clear_placeholder(self, event=None):
        if self.search_entry.get() == "Tìm kiếm quyền hoặc chức năng...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def _restore_placeholder(self, event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Tìm kiếm quyền hoặc chức năng...")
            self.search_entry.config(fg="gray")

    
    def show_add_permission(self):
        form = tk.Toplevel(self.parent.root)
        form.title("Thêm Quyền Mới")
        window_width = 550
        window_height = 450
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form.configure(bg="#ffffff")
        form.grab_set()

        style = ttk.Style()
        style.configure("Custom.TEntry", padding=6, relief="solid", borderwidth=1, font=("Times New Roman", 11), foreground="black", fieldbackground="white")
        style.configure("Error.TEntry", padding=6, relief="solid", borderwidth=1, font=("Times New Roman", 11), foreground="black", fieldbackground="white", bordercolor="red")
        style.configure("Custom.TCombobox", padding=6, font=("Times New Roman", 11))
        style.configure("Custom.TCheckbutton",
                        font=("Times New Roman", 11),
                        background="#ffffff",
                        foreground="black",
                        padding=0,
                        borderwidth=0,
                        relief="flat")
        style.map("Custom.TCheckbutton",
                background=[("active", "#ffffff"), ("selected", "#ffffff"), ("!selected", "#ffffff")],
                foreground=[("active", "black"), ("selected", "black"), ("!selected", "black")],
                relief=[("active", "flat"), ("selected", "flat"), ("!selected", "flat")],
                borderwidth=[("active", 0), ("selected", 0), ("!selected", 0)])
        
        tk.Label(form, text="Thêm Quyền Mới", font=("Times New Roman", 16, "bold"), bg="#ffffff", fg="#14a0f7").pack(pady=20)

        name_frame = tk.Frame(form, bg="#ffffff")
        name_frame.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(name_frame, text="Tên quyền:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame, font=("Times New Roman", 11), width=35, style="Custom.TEntry")
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        function_frame = tk.Frame(form, bg="#ffffff")
        function_frame.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(function_frame, text="Danh mục chức năng:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        function_var = tk.StringVar()
        function_combobox = ttk.Combobox(function_frame, textvariable=function_var, font=("Times New Roman", 11), width=32, style="Custom.TCombobox", state="readonly")
        functions = self.data_user.db.fetch_all("SELECT function_name FROM Function_List")
        function_combobox['values'] = [f[0] for f in functions]
        function_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        actions_frame = tk.Frame(form, bg="#ffffff")
        actions_frame.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(actions_frame, text="Trạng thái:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        action_vars = {
            "view": tk.BooleanVar(),
            "create": tk.BooleanVar(),
            "update": tk.BooleanVar(),
            "delete": tk.BooleanVar()
        }
        ttk.Checkbutton(actions_frame, text="Xem", variable=action_vars["view"], style="Custom.TCheckbutton", takefocus=False).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(actions_frame, text="Tạo mới", variable=action_vars["create"], style="Custom.TCheckbutton", takefocus=False).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(actions_frame, text="Cập nhật", variable=action_vars["update"], style="Custom.TCheckbutton", takefocus=False).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(actions_frame, text="Xóa", variable=action_vars["delete"], style="Custom.TCheckbutton", takefocus=False).pack(side=tk.LEFT, padx=10)
        
        button_frame = tk.Frame(form, bg="#ffffff")
        button_frame.pack(pady=30)

        def handle_save():
            self.parent.error_labels.clear()
            name_entry.configure(style="Custom.TEntry")
            function_combobox.configure(style="Custom.TCombobox")

            role_name = name_entry.get().strip()
            function_name = function_var.get().strip()
            actions = [action for action, var in action_vars.items() if var.get()]

            errors = {}
            if not role_name:
                errors['role_name'] = "Tên quyền không được để trống!"
            if not function_name:
                errors['function_name'] = "Danh mục chức năng không được để trống!"
            if not actions:
                errors['actions'] = "Phải chọn ít nhất một trạng thái!"

            if errors:
                for field, message in errors.items():
                    widget = name_entry if field == 'role_name' else function_combobox if field == 'function_name' else actions_frame
                    self.parent.show_error_below(field, message, widget)
                return

            # Save role with function and actions
            success, result = self.data_user.save_new_role(role_name, function_name, actions)
            if success:
                messagebox.showinfo("Thành công", result)
                form.destroy()
                self.load_permission_data()
            else:
                if isinstance(result, dict) and 'general' in result:
                    messagebox.showerror("Lỗi", result['general'])
                elif isinstance(result, dict):
                    for field, message in result.items():
                        widget = name_entry if field == 'role_name' else function_combobox if field == 'function_name' else actions_frame
                        self.parent.show_error_below(field, message, widget)
                else:
                    messagebox.showerror("Lỗi", result)

        save_button = tk.Button(button_frame, text="Lưu", command=handle_save, bg="#4CAF50", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Hủy", command=form.destroy, bg="#f44336", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        cancel_button.pack(side=tk.LEFT, padx=10)

    def edit_permission(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn quyền để sửa!")
            return

        role_name = self.tree.item(selected_item)['values'][1]
        self.current_role = role_name
        self.edit_mode = True
        self.show_edit_permission(role_name)

        for item in self.tree.get_children():
            role_id = self.tree.item(item, "values")[0]
            function_name = self.tree.item(item, "values")[2]
            function_id = self.data_user.fetch_function_id_by_name(function_name)
            if function_id is None:
                continue
            actions = self.temp_actions.get(item, [])
            self.embed_toggle_images(item, role_id, function_id, actions)

    def show_edit_permission(self, role_name):
        form = tk.Toplevel(self.parent.root)
        form.title("Chỉnh Sửa Quyền")
        window_width = 550
        window_height = 450
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form.configure(bg="#ffffff")
        form.grab_set()

        style = ttk.Style()
        style.configure("Custom.TEntry", padding=6, relief="solid", borderwidth=1, font=("Times New Roman", 11), foreground="black", fieldbackground="white")
        style.configure("Error.TEntry", padding=6, relief="solid", borderwidth=1, font=("Times New Roman", 11), foreground="black", fieldbackground="white", bordercolor="red")
        style.configure("Custom.TCombobox", padding=6, font=("Times New Roman", 11))

        # Updated Checkbutton style
        style.configure("Custom.TCheckbutton",
                        font=("Times New Roman", 11),
                        background="#ffffff",
                        foreground="black",
                        padding=0,
                        borderwidth=0,  # Remove border
                        relief="flat")  # Ensure flat relief
        style.map("Custom.TCheckbutton",
                background=[("active", "#ffffff"), ("selected", "#ffffff"), ("!selected", "#ffffff")],
                foreground=[("active", "black"), ("selected", "black"), ("!selected", "black")],
                relief=[("active", "flat"), ("selected", "flat"), ("!selected", "flat")],
                borderwidth=[("active", 0), ("selected", 0), ("!selected", 0)])

        tk.Label(form, text="Chỉnh Sửa Quyền", font=("Times New Roman", 16, "bold"), bg="#ffffff", fg="#14a0f7").pack(pady=20)

        name_frame = tk.Frame(form, bg="#ffffff")
        name_frame.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(name_frame, text="Tên quyền:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame, font=("Times New Roman", 11), width=35, style="Custom.TEntry")
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        function_frame = tk.Frame(form, bg="#ffffff")
        function_frame.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(function_frame, text="Danh mục chức năng:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)
        function_var = tk.StringVar()
        function_combobox = ttk.Combobox(function_frame, textvariable=function_var, font=("Times New Roman", 11), width=32, style="Custom.TCombobox", state="readonly")
        functions = self.data_user.db.fetch_all("SELECT function_name FROM Function_List")
        function_combobox['values'] = [f[0] for f in functions]
        function_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        actions_frame = tk.Frame(form, bg="#ffffff", highlightthickness=0)
        actions_frame.pack(fill=tk.X, padx=30, pady=10)
        tk.Label(actions_frame, text="Trạng thái:", font=("Times New Roman", 11), bg="#ffffff", width=18, anchor="w").pack(side=tk.LEFT)

        action_vars = {
            "view": tk.BooleanVar(),
            "create": tk.BooleanVar(),
            "update": tk.BooleanVar(),
            "delete": tk.BooleanVar()
        }

        # Apply the custom style and ensure no border
        ttk.Checkbutton(actions_frame, text="Xem", variable=action_vars["view"], style="Custom.TCheckbutton", takefocus=False).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(actions_frame, text="Tạo mới", variable=action_vars["create"], style="Custom.TCheckbutton", takefocus=False).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(actions_frame, text="Cập nhật", variable=action_vars["update"], style="Custom.TCheckbutton", takefocus=False).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(actions_frame, text="Xóa", variable=action_vars["delete"], style="Custom.TCheckbutton", takefocus=False).pack(side=tk.LEFT, padx=10)
        selected_item = self.tree.selection()
        if selected_item:
            function_name = self.tree.item(selected_item)['values'][2]
            function_var.set(function_name)
            item_id = selected_item[0]
            current_actions = self.temp_actions.get(item_id, [])
            for action in action_vars:
                action_vars[action].set(action in current_actions)

        role = self.data_user.fetch_role_by_name(role_name)
        if not role:
            messagebox.showerror("Lỗi", "Không tìm thấy quyền!")
            form.destroy()
            return
        role_id, role_name_db = role
        name_entry.insert(0, role_name_db)

        button_frame = tk.Frame(form, bg="#ffffff")
        button_frame.pack(pady=30)

        def handle_save():
            self.parent.error_labels.clear()
            name_entry.configure(style="Custom.TEntry")
            function_combobox.configure(style="Custom.TCombobox")

            new_role_name = name_entry.get().strip()
            function_name = function_var.get().strip()
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Lỗi", "Không có mục nào được chọn!")
                return
            item_id = selected_item[0]
            actions = [action for action, var in action_vars.items() if var.get()]

            # Cập nhật temp_actions để đồng bộ với toggle
            self.temp_actions[item_id] = actions

            errors = {}
            if not new_role_name:
                errors['role_name'] = "Tên quyền không được để trống!"
            elif new_role_name != role_name_db and self.data_user.db.check_existing_role(new_role_name):
                errors['role_name'] = "Tên quyền đã tồn tại!"
            if not function_name:
                errors['function_name'] = "Danh mục chức năng không được để trống!"

            if errors:
                for field, message in errors.items():
                    if field == 'role_name':
                        name_entry.configure(style="Error.TEntry")
                        self.parent.show_error_below(field, message, name_entry)
                    elif field == 'function_name':
                        function_combobox.configure(style="Error.TCombobox")
                        self.parent.show_error_below(field, message, function_combobox)
                return

            success, result = self.data_user.update_role(role_name_db, new_role_name)
            if success:
                function_id = self.data_user.fetch_function_id_by_name(function_name)
                if function_id:
                    valid_actions = [action for action in actions if action in ['view', 'create', 'update', 'delete']]
                    success, result = self.data_user.update_role_actions(role_id, function_id, valid_actions)
                    if success:
                        messagebox.showinfo("Thành công", "Cập nhật quyền thành công!")
                        form.destroy()
                        self.edit_mode = False
                        self.current_role = None
                        self.temp_actions.clear()
                        self.load_permission_data()
                        self.tree.update_idletasks()
                        self.update_toggle_positions()
                    else:
                        messagebox.showerror("Lỗi", result)
                else:
                    messagebox.showerror("Lỗi", "Danh mục chức năng không hợp lệ!")
            else:
                messagebox.showerror("Lỗi", result)

        def handle_cancel():
            form.destroy()
            self.edit_mode = False
            self.current_role = None
            self.temp_actions.clear()
            self.load_permission_data()

        def on_closing():
            self.edit_mode = False
            self.current_role = None
            self.temp_actions.clear()
            self.load_permission_data()
            form.destroy()

        form.protocol("WM_DELETE_WINDOW", on_closing)

        save_button = tk.Button(button_frame, text="Lưu", command=handle_save, bg="#4CAF50", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Hủy", command=handle_cancel, bg="#f44336", fg="white", font=("Times New Roman", 11), width=12, relief="flat")
        cancel_button.pack(side=tk.LEFT, padx=10)

    
    def show_delete_permission(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một quyền để xóa!")
            return

        role_name = self.tree.item(selected_item)['values'][1]
        
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

        label = Label(confirm_dialog, text=f"Bạn có chắc chắn muốn xóa quyền '{role_name}'?", wraplength=250)
        label.pack(pady=20)

        def confirm_delete():
            success, message = self.data_user.delete_role(role_name)
            if success:
                messagebox.showinfo("Thành công", message)
                self.load_permission_data()
            else:
                messagebox.showerror("Lỗi", message, parent=self.parent.root)  # Show detailed error
            confirm_dialog.destroy()

        def cancel_delete():
            confirm_dialog.destroy()

        btn_yes = Button(confirm_dialog, text="Có", command=confirm_delete, width=10, 
                        bg="#4CAF50", fg="white", font=("Times New Roman", 11), relief="flat")
        btn_yes.pack(side="left", padx=20, pady=10)

        btn_no = Button(confirm_dialog, text="Không", command=cancel_delete, width=10,
                        bg="#f44336", fg="white", font=("Times New Roman", 11), relief="flat")
        btn_no.pack(side="right", padx=20, pady=10)