from database.dbT import dbT
import re

class DataUser:
    def __init__(self):
        self.db = dbT()

    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def is_valid_phone(self, phone):
        return phone.isdigit() and len(phone) == 10

    def load_accounts(self):
        return self.db.load_accounts()

    def search_accounts(self, search_term):
        return self.db.search_accounts(search_term)

    def fetch_departments(self):
        return self.db.fetch_departments()

    def fetch_roles(self):
        return self.db.fetch_roles()

    def search_roles(self, search_term):
        return self.db.search_roles(search_term)

    def fetch_role_details(self):
        return self.db.fetch_role_details()

    def fetch_function_id_by_name(self, function_name):
        return self.db.fetch_function_id_by_name(function_name)

    def fetch_actions(self, role_id, function_id):
        actions_str = self.db.fetch_actions(role_id, function_id)
        if actions_str:
            return [action for action in actions_str.split(',') if action]
        return []

    def update_role_actions(self, role_id, function_id, actions):
        valid_actions = ['view', 'create', 'update', 'delete']
        if actions and not all(action in valid_actions for action in actions):
            return False, "Hành động không hợp lệ!"
        actions_str = ','.join(actions) if actions else None
        return self.db.update_role_actions(role_id, function_id, actions_str)

    def validate_new_account(self, last_name, first_name, email, phone_number, user_name, password, dep_name, role_name, departments, roles):
        errors = {}
        if not last_name:
            errors['last_name'] = "Họ không được để trống!"
        if not first_name:
            errors['first_name'] = "Tên không được để trống!"
        if not email:
            errors['email'] = "Email không được để trống!"
        elif not self.is_valid_email(email):
            errors['email'] = "Email không hợp lệ!"
        elif self.db.check_existing_email(email):
            errors['email'] = "Email đã tồn tại!"
        if not phone_number:
            errors['phone_number'] = "Số điện thoại không được để trống!"
        elif not self.is_valid_phone(phone_number):
            errors['phone_number'] = "Số điện thoại phải là 10 chữ số!"
        if not user_name:
            errors['user_name'] = "Tên đăng nhập không được để trống!"
        elif self.db.check_existing_username(user_name):
            errors['user_name'] = "Tên đăng nhập đã tồn tại!"
        if not password:
            errors['password'] = "Mật khẩu không được để trống!"
        if not dep_name:
            errors['dep_name'] = "Phòng ban không được để trống!"
        if not role_name:
            errors['role_name'] = "Quyền không được để trống!"
        return errors

    def validate_edit_account(self, last_name, first_name, email, phone_number, user_name, dep_name, role_name, email_db, user_name_db, departments, roles):
        errors = {}
        if not last_name:
            errors['last_name'] = "Họ không được để trống!"
        if not first_name:
            errors['first_name'] = "Tên không được để trống!"
        if not email:
            errors['email'] = "Email không được để trống!"
        elif not self.is_valid_email(email):
            errors['email'] = "Email không hợp lệ!"
        elif email != email_db and self.db.check_existing_email(email):
            errors['email'] = "Email đã tồn tại!"
        if not phone_number:
            errors['phone_number'] = "Số điện thoại không được để trống!"
        elif not self.is_valid_phone(phone_number):
            errors['phone_number'] = "Số điện thoại phải là 10 chữ số!"
        if not user_name:
            errors['user_name'] = "Tên đăng nhập không được để trống!"
        elif user_name != user_name_db and self.db.check_existing_username(user_name):
            errors['user_name'] = "Tên đăng nhập đã tồn tại!"
        if not dep_name:
            errors['dep_name'] = "Phòng ban không được để trống!"
        if not role_name:
            errors['role_name'] = "Quyền không được để trống!"
        return errors

    def validate_role(self, role_name):
        errors = {}
        if not role_name:
            errors['role_name'] = "Tên quyền không được để trống!"
        elif self.db.check_existing_role(role_name):
            errors['role_name'] = "Tên quyền đã tồn tại!"
        return errors

    def validate_edit_role(self, old_role_name, new_role_name):
        errors = {}
        if not new_role_name:
            errors['role_name'] = "Tên quyền không được để trống!"
        elif new_role_name != old_role_name and self.db.check_existing_role(new_role_name):
            errors['role_name'] = "Tên quyền đã tồn tại!"
        return errors

    def save_new_account(self, last_name, first_name, email, phone_number, hired_date, position, status, user_name, password, dep_name, role_name):
        departments = self.db.fetch_departments()
        roles = self.db.fetch_roles()
        errors = self.validate_new_account(last_name, first_name, email, phone_number, user_name, password, dep_name, role_name, departments, roles)
        if errors:
            return False, errors

        dep_id = next((d_id for d_id, d_name in departments if d_name == dep_name), None)
        role_id = next((r_id for r_id, r_name in roles if r_name == role_name), None)
        if not dep_id or not role_id:
            return False, {'general': "Phòng ban hoặc quyền không hợp lệ!"}

        success, db_result = self.db.save_new_account(
            last_name, first_name, dep_id, email, phone_number or None, hired_date or None,
            position or None, status, user_name, password, role_id
        )
        if success:
            return True, db_result
        else:
            return False, {'general': db_result}

    def fetch_account_by_id(self, account_id):
        return self.db.fetch_account_by_id(account_id)

    def update_account(self, account_id, last_name, first_name, email, phone_number, hired_date, position, status, user_name, password, dep_name, role_name, email_db, user_name_db):
        departments = self.db.fetch_departments()
        roles = self.db.fetch_roles()
        errors = self.validate_edit_account(last_name, first_name, email, phone_number, user_name, dep_name, role_name, email_db, user_name_db, departments, roles)
        if errors:
            return False, errors

        dep_id = next((d_id for d_id, d_name in departments if d_name == dep_name), None)
        role_id = next((r_id for r_id, r_name in roles if r_name == role_name), None)
        if not dep_id or not role_id:
            return False, {'general': "Phòng ban hoặc quyền không hợp lệ!"}

        return self.db.update_account(
            account_id, last_name, first_name, dep_id, email, phone_number, hired_date or None,
            position or None, status, user_name, password, role_id
        )

    def delete_account(self, account_id):
        return self.db.delete_account(account_id)

    def check_function_exists_for_role(self, role_id, function_id):
        actions = self.fetch_actions(role_id, function_id)
        return bool(actions)

    def save_new_role(self, role_name, function_name=None, actions=None):
        if function_name and actions:  # Adding function category
            role = self.fetch_role_by_name(role_name)
            function_id = self.fetch_function_id_by_name(function_name) if function_name else None
            if not function_id:
                return False, {'general': "Danh mục chức năng không hợp lệ!"}
            
            if role:  # Existing role
                role_id, _ = role
                # Check if function is already assigned
                if self.check_function_exists_for_role(role_id, function_id):
                    return False, {'general': f"Danh mục chức năng '{function_name}' đã được gán cho quyền '{role_name}'!"}
                # Save actions for existing role
                success, result = self.update_role_actions(role_id, function_id, actions)
                if success:
                    return True, "Đã thêm danh mục chức năng vào quyền!"
                return False, {'general': result}
            else:  # New role
                errors = self.validate_role(role_name)
                if errors:
                    return False, errors
                success, db_result = self.db.save_new_role(role_name)
                if success:
                    role = self.fetch_role_by_name(role_name)
                    if role:
                        role_id, _ = role
                        success, result = self.update_role_actions(role_id, function_id, actions)
                        if success:
                            return True, "Đã thêm quyền và danh mục chức năng!"
                        return False, {'general': result}
                    return False, {'general': "Không thể lấy thông tin quyền mới!"}
                return False, {'general': db_result}
        else:  # Creating role without function
            errors = self.validate_role(role_name)
            if errors:
                return False, errors
            return self.db.save_new_role(role_name)

    def fetch_role_by_name(self, role_name):
        return self.db.fetch_role_by_name(role_name)

    def update_role(self, old_role_name, new_role_name):
        errors = self.validate_edit_role(old_role_name, new_role_name)
        if errors:
            return False, errors
        return self.db.update_role(old_role_name, new_role_name)

    def delete_role(self, role_name):
        return self.db.delete_role(role_name)
    