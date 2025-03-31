-- Tạo cơ sở dữ liệu
CREATE DATABASE IF NOT EXISTS Face_Recognition;
USE Face_Recognition;

-- Tạo bảng Employees (không có khóa ngoại dep_id trước)
CREATE TABLE Employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    last_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    dep_id INT,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(15),
    hired_date DATE,
    position VARCHAR(255),
    status ENUM('active', 'inactive') DEFAULT 'active'
);

-- Tạo bảng Departments (không có khóa ngoại manager_id trước)
CREATE TABLE Departments (
    dep_id INT PRIMARY KEY AUTO_INCREMENT,
    dep_name VARCHAR(100) NOT NULL UNIQUE,
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES Employees(emp_id) ON DELETE SET NULL
);

-- Thêm khóa ngoại cho Employees.dep_id
ALTER TABLE Employees
ADD CONSTRAINT FK_Employees_Departments 
    FOREIGN KEY (dep_id) REFERENCES Departments(dep_id);

-- Tạo bảng Attendance
CREATE TABLE Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    emp_id INT,
    check_in DATETIME,
    check_out DATETIME,
    date DATE,
    work_hours FLOAT DEFAULT 0.0,
    overtime_hours FLOAT DEFAULT 0.0,
    FOREIGN KEY (emp_id) REFERENCES Employees(emp_id)
);

-- Tạo bảng Face_Data
CREATE TABLE Face_Data (
    face_id INT PRIMARY KEY AUTO_INCREMENT,
    emp_id INT,
    face_encoding BLOB NOT NULL,
    angle ENUM('front', 'left', 'right', 'up', 'down'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES Employees(emp_id)
);

-- Tạo bảng Role
CREATE TABLE Role (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Tạo bảng Employee_Role
CREATE TABLE Employee_Role (
    emp_id INT,
    role_id INT,
    PRIMARY KEY (emp_id, role_id),
    FOREIGN KEY (emp_id) REFERENCES Employees(emp_id),
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
);

-- Tạo bảng Permission
CREATE TABLE Permission (
    permission_id INT PRIMARY KEY AUTO_INCREMENT,
    permission_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Tạo bảng Role_Permission
CREATE TABLE Role_Permission (
    role_id INT,
    permission_id INT,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES Role(role_id),
    FOREIGN KEY (permission_id) REFERENCES Permission(permission_id)
);

-- Tạo bảng Payroll
CREATE TABLE Payroll (
    payroll_id INT PRIMARY KEY AUTO_INCREMENT,
    emp_id INT,
    month_year DATE,
    base_salary DECIMAL(10,2) DEFAULT 0.00,
    overtime_salary DECIMAL(10,2) DEFAULT 0.00,
    time_salary DECIMAL(10,2) DEFAULT 0.00,
    total_month_basetime FLOAT DEFAULT 0.0,
    total_month_overtime FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES Employees(emp_id)
);

-- Stored Procedure để cập nhật Payroll ----- ERROR ----
DELIMITER //
CREATE PROCEDURE UpdatePayroll(
    IN p_emp_id INT,
    IN p_month_year DATE
)
BEGIN
    DECLARE v_total_basetime FLOAT DEFAULT 0;
    DECLARE v_total_overtime FLOAT DEFAULT 0;
    DECLARE v_time_salary DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_base_salary DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_overtime_salary DECIMAL(10,2) DEFAULT 0.00;

    -- Lấy tổng giờ làm việc
    SELECT SUM(work_hours) INTO v_total_basetime
    FROM Attendance
    WHERE emp_id = p_emp_id
        AND date BETWEEN p_month_year AND LAST_DAY(p_month_year);

    -- Lấy tổng giờ làm thêm
    SELECT SUM(overtime_hours) INTO v_total_overtime
    FROM Attendance
    WHERE emp_id = p_emp_id
        AND date BETWEEN p_month_year AND LAST_DAY(p_month_year);

    -- Tính lương theo giờ và làm thêm
    SET v_time_salary = COALESCE(v_total_basetime, 0) * 100000;  -- HOURLY_RATE = 100000
    SET v_overtime_salary = COALESCE(v_total_overtime, 0) * 200000;  -- OVERTIME_RATE = 200000

    -- Lấy thông tin vị trí để tính lương cố định
    SELECT CASE position 
           WHEN 'Manager' THEN 5000000 
           WHEN 'Developer' THEN 3000000 
           ELSE 0 
           END INTO v_base_salary
    FROM Employees
    WHERE emp_id = p_emp_id;
    
    SET v_base_salary = v_base_salary + v_time_salary;  -- Lương cơ bản = lương cố định + lương theo giờ

    -- Nếu bản ghi đã tồn tại trong Payroll → Cập nhật
    IF EXISTS (SELECT 1 FROM Payroll WHERE emp_id = p_emp_id AND month_year = p_month_year) THEN
        UPDATE Payroll
        SET base_salary = v_base_salary,
            overtime_salary = v_overtime_salary,
            time_salary = v_time_salary,
            total_month_basetime = COALESCE(v_total_basetime, 0),
            total_month_overtime = COALESCE(v_total_overtime, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE emp_id = p_emp_id AND month_year = p_month_year;
    ELSE
        -- Nếu chưa có thì thêm mới
        INSERT INTO Payroll (emp_id, month_year, base_salary, overtime_salary, time_salary, total_month_basetime, total_month_overtime)
        VALUES (p_emp_id, p_month_year, v_base_salary, v_overtime_salary, v_time_salary, 
                COALESCE(v_total_basetime, 0), COALESCE(v_total_overtime, 0));
    END IF;
END //
DELIMITER ;

INSERT INTO Departments (dep_id, dep_name) 
VALUES
	(1, 'Manager Department'),
	(2, 'IT Department'),
    (3, 'Employee');

INSERT INTO Employees (emp_id, last_name, first_name, dep_id, email, phone_number, hired_date, position, status)
VALUES 
	(1, 'Võ Thị', 'Thu Luyện ', 1, 'thuluyen234@gmail.com', '0123456789', '2025-01-01', 'Developer', 'active'),
    (2, 'Nguyễn Thị', 'Ngọc Tú', 2, 'ngoctu28012005@gmail.com', '0377810714', '2025-01-15', 'Manager', 'active'),
    (3, 'Trần Thị', 'Xuân Thanh', 3, 'xuanthanh234@gmail.com', '0123456789', '2025-02-01', 'Employee', 'active'),
    (4, 'Phạm', 'Thanh An', 3, 'thanhanh456@gmail.com', '0123456894', '2024-10-25', 'Employee', 'inactive'),
    (5, 'Đỗ', 'Duy Quý', 1, 'duyquy895@gmail.com', '0123567945', '2025-01-01', 'Developer', 'active');

UPDATE Departments SET manager_id = 1 WHERE dep_id = 1;

INSERT INTO Face_Data (emp_id, face_encoding, angle)
VALUES (1, 0x1234567890ABCDEF, 'front');

INSERT INTO Role (role_id, role_name, description)
VALUES 
    (1, 'IT', 'Chịu trách nhiệm bảo trì hệ thống và xem báo cáo'),
    (2, 'Manager', 'Quản lý hoạt động, quản lý người dùng và chỉnh sửa bản ghi'),
    (3, 'Employee', 'Quyền truy cập hạn chế để xem báo cáo cơ bản');

INSERT INTO Employee_Role (emp_id, role_id) 
VALUES 	
	(1, 1),
    (2,2),
    (3,3),
    (4,3),
    (5,1);

INSERT INTO Permission (permission_id, permission_name, description)
VALUES 
    (1, 'View_Reports', 'Can view attendance reports'),
    (2, 'Edit_Records', 'Can edit employee records'),
    (3, 'Manage_Users', 'Can add or remove users');

-- Role_Permission
INSERT INTO Role_Permission (role_id, permission_id)
VALUES 
    (1, 1),  -- IT có quyền View_Reports
    (2, 1),  -- Manager có quyền View_Reports
    (2, 2),  -- Manager có quyền Edit_Records
    (2, 3),  -- Manager có quyền Manage_Users
    (3, 1);  -- Employee có quyền View_Reports

-- Thêm dữ liệu cho tháng 03/2025 (Thứ Hai đến Thứ Sáu)
INSERT INTO Attendance (emp_id, check_in, check_out, date)
VALUES 
(1, '2025-03-01 08:00:00', '2025-03-01 17:00:00', '2025-03-01'),
(1, '2025-03-03 08:00:00', '2025-03-03 17:00:00', '2025-03-03'),
(1, '2025-03-04 08:00:00', '2025-03-04 18:00:00', '2025-03-04'),
(1, '2025-03-05 08:00:00', '2025-03-05 17:00:00', '2025-03-05'),
(1, '2025-03-06 08:00:00', '2025-03-06 19:00:00', '2025-03-06'),
(1, '2025-03-07 08:00:00', '2025-03-07 17:00:00', '2025-03-07'),
(1, '2025-03-10 08:00:00', '2025-03-10 17:00:00', '2025-03-10'),
(1, '2025-03-11 08:00:00', '2025-03-11 17:00:00', '2025-03-11'),
(1, '2025-03-12 08:00:00', '2025-03-12 18:30:00', '2025-03-12'),
(1, '2025-03-13 08:00:00', '2025-03-13 17:00:00', '2025-03-13'),
(1, '2025-03-14 08:00:00', '2025-03-14 17:00:00', '2025-03-14'),
(1, '2025-03-17 08:00:00', '2025-03-17 17:00:00', '2025-03-17'),
(1, '2025-03-18 08:00:00', '2025-03-18 17:00:00', '2025-03-18'),
(1, '2025-03-19 08:00:00', '2025-03-19 17:00:00', '2025-03-19'),
(1, '2025-03-20 08:00:00', '2025-03-20 20:00:00', '2025-03-20'),
(1, '2025-03-21 08:00:00', '2025-03-21 17:00:00', '2025-03-21'),
(1, '2025-03-24 08:00:00', '2025-03-24 17:00:00', '2025-03-24'),
(1, '2025-03-25 08:00:00', '2025-03-25 17:00:00', '2025-03-25'),
(1, '2025-03-26 08:00:00', '2025-03-26 17:00:00', '2025-03-26'),
(1, '2025-03-27 08:00:00', '2025-03-27 17:00:00', '2025-03-27'),
(1, '2025-03-28 08:00:00', '2025-03-28 17:00:00', '2025-03-28'),
(1, '2025-03-31 08:00:00', '2025-03-31 17:00:00', '2025-03-31'),
(1, '2025-03-01 08:00:00', '2025-03-01 17:00:00', '2025-02-01'),
(1, '2025-03-03 08:00:00', '2025-03-03 17:00:00', '2025-02-03'),
(1, '2025-03-04 08:00:00', '2025-03-04 18:00:00', '2025-02-04'),
(1, '2025-03-05 08:00:00', '2025-03-05 17:00:00', '2025-02-05'),
(1, '2025-03-06 08:00:00', '2025-03-06 19:00:00', '2025-02-06'),
(1, '2025-03-07 08:00:00', '2025-03-07 17:00:00', '2025-02-07'),
(1, '2025-03-10 08:00:00', '2025-03-10 17:00:00', '2025-02-10'),
(1, '2025-03-11 08:00:00', '2025-03-11 17:00:00', '2025-02-11'),
(1, '2025-03-12 08:00:00', '2025-03-12 18:30:00', '2025-02-12'),
(1, '2025-03-13 08:00:00', '2025-03-13 17:00:00', '2025-02-13'),
(1, '2025-03-14 08:00:00', '2025-03-14 17:00:00', '2025-02-14'),
(1, '2025-03-17 08:00:00', '2025-03-17 17:00:00', '2025-02-17'),
(1, '2025-03-18 08:00:00', '2025-03-18 17:00:00', '2025-02-18'),
(1, '2025-03-19 08:00:00', '2025-03-19 17:00:00', '2025-02-19'),
(1, '2025-03-20 08:00:00', '2025-03-20 20:00:00', '2025-02-20'),
(1, '2025-03-21 08:00:00', '2025-03-21 17:00:00', '2025-02-21'),
(1, '2025-03-24 08:00:00', '2025-03-24 17:00:00', '2025-02-24'),
(1, '2025-03-25 08:00:00', '2025-03-25 17:00:00', '2025-02-25'),
(1, '2025-03-26 08:00:00', '2025-03-26 17:00:00', '2025-02-26'),
(1, '2025-03-27 08:00:00', '2025-03-27 17:00:00', '2025-02-27'),
(1, '2025-03-28 08:00:00', '2025-03-28 17:00:00', '2025-02-28');