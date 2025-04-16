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
    status ENUM('Đang làm việc', 'Đã nghỉ') DEFAULT 'Đang làm việc'
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
    face_encoding BLOB,
    image_path VARCHAR(255),
    angle ENUM('front', 'left', 'right', 'up', 'down'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES Employees(emp_id)
);

-- Tạo bảng Role
CREATE TABLE Role (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Users (
	emp_id int primary key auto_increment,
    user_name varchar(50),
    passwd varchar(255),
    status int not null default 1,
    role_id int,
    foreign key (emp_id) references Employees(emp_id),
    foreign key (role_id) references Role(role_id)
);

CREATE TABLE Function_List (
	function_id int primary key,
    function_name varchar(255)
);

CREATE TABLE Role_Details (
    role_id int,
    function_id int,
    action varchar(255),
    PRIMARY KEY (role_id, function_id), 
    FOREIGN KEY (role_id) REFERENCES Role(role_id),
    FOREIGN KEY (function_id) REFERENCES Function_List(function_id)
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

-- Stored Procedure để cập nhật Payroll
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
	(1, 'Võ Thị Thu', 'Luyện ', 3, 'thuluyen234@gmail.com', '0123456789', '2025-01-01', 'Employee', 'Đang làm việc'),
    (2, 'Nguyễn Thị Ngọc', 'Tú', 3, 'ngoctu28012005@gmail.com', '0377810714', '2025-01-15', 'Employee', 'Đang làm việc'),
    (3, 'Trần Thị Xuân', 'Thanh', 3, 'xuanthanh234@gmail.com', '0123456789', '2025-02-01', 'Employee', 'Đang làm việc'),
    (4, 'Phạm Thanh', 'An', 3, 'thanhanh456@gmail.com', '0123456894', '2024-10-25', 'Employee', 'Đã nghỉ'),
    (5, 'Đỗ Duy ', 'Quý', 3, 'duyquy895@gmail.com', '0123567945', '2025-01-01', 'Employee', 'Đang làm việc'),
    (6, 'Nguyễn Thanh', 'Ngân', 1, 'thanhngan25@gmail.com', '0356897424', '2024-10-01', 'Manager', 'Đang làm việc'),
    (7, 'Phạm Như', 'An', 2, 'nhuan501@gmai.com', '0867456231', '2024-10-01', 'IT', 'Đang làm việc');

UPDATE Departments SET manager_id = 1 WHERE dep_id = 1;

INSERT INTO Face_Data (emp_id, face_encoding, angle)
VALUES (1, 0x1234567890ABCDEF, 'front');

INSERT INTO Function_List (function_id, function_name)
VALUES
    (1, 'Quản lý nhân viên'),
    (2, 'Quản lý phòng ban'),
    (3, 'Chấm công'),
    (4, 'Quản lý dữ liệu khuôn mặt'),
    (5, 'Phân quyền'),
    (6, 'Quản lý tài khoản'),
    (7, 'Quản lý lương');

INSERT INTO Role (role_id, role_name)
VALUES
	(1, 'admin'),
    (2, 'manager'),
    (3, 'employee');
    
INSERT INTO Users (emp_id, user_name, passwd, role_id)
VALUES
	(1, '1', '$2b$12$C/fO/FquP6H9v4/AetwQ3O2n8am3MDavYvZtA7.GtzjODmN7sA/k6', 3),
    (2, '2', '$2b$12$C/fO/FquP6H9v4/AetwQ3O2n8am3MDavYvZtA7.GtzjODmN7sA/k6', 3),
    (3, '3', '$2b$12$C/fO/FquP6H9v4/AetwQ3O2n8am3MDavYvZtA7.GtzjODmN7sA/k6', 3),
    (4, '4', '$2b$12$C/fO/FquP6H9v4/AetwQ3O2n8am3MDavYvZtA7.GtzjODmN7sA/k6', 3),
    (5, '5', '$2b$12$C/fO/FquP6H9v4/AetwQ3O2n8am3MDavYvZtA7.GtzjODmN7sA/k6', 3),
    (6, 'manager', '$2b$12$dMLlaZQueCjMIVob.I5R2eFPsSyMxZPga7QzhsR6re0YZHkjV5/cG', 2),
    (7, 'admin', '$2b$12$rJRn6wSnYyahuXP3gpo7..Ei0AeYXfVqr3AaQ58wvRzjFh0moQVz', 1);

INSERT INTO Role_Details (role_id, function_id, action)
VALUES
    -- Admin (role_id = 1): Toàn quyền
    (1, 2, 'view,create,update,delete'), -- Quản lý phòng ban
    (1, 4, 'view,create,update,delete'), -- Quản lý dữ liệu khuôn mặt
    (1, 5, 'view,create,update,delete'), -- Phân quyền
    (1, 6, 'view,create,update,delete'), -- Quản lý tài khoản

    -- Manager (role_id = 2): Quyền hạn chế
    (2, 1, 'view,create,update,delete'), -- Quản lý nhân viên
    (2, 3, 'view'),              -- Xem lịch sử chấm công
    (2, 7, 'view'), -- Quản lý lương

    -- Employee (role_id = 3): Quyền xem chấm công và lương
    (3, 3, 'view'), -- Xem lịch sử chấm công
    (3, 7, 'view'); -- Xem lương
	

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