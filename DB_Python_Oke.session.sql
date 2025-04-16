-- UPDATE Attendance
-- SET check_in = '2025-04-08 11:00:00'
-- WHERE attendance_id = 51;

-- UPDATE Attendance
-- SET emp_id = '1'
-- WHERE attendance_id = 50;

DELETE FROM Face_Data;

-- ### Chèn vào Face_Data dữ liệu của 4 người ###
INSERT INTO Face_Data (emp_id, face_encoding, image_path, angle) 
VALUES
    (1, NULL, 'images/1_Luyen_01.jpg', 'front'),
    (1, NULL, 'images/1_Luyen_02.jpg', 'left'),
    (1, NULL, 'images/1_Luyen_03.jpg', 'right'),
    (1, NULL, 'images/1_Luyen_04.jpg', 'up'),
    (1, NULL, 'images/1_Luyen_05.jpg', 'down');

INSERT INTO Face_Data (emp_id, face_encoding, image_path, angle) 
VALUES
    (2, NULL, 'images/2_Tu_01.jpg', 'front'),
    (2, NULL, 'images/2_Tu_02.jpg', 'left'),
    (2, NULL, 'images/2_Tu_03.jpg', 'right'),
    (2, NULL, 'images/2_Tu_04.jpg', 'up'),
    (2, NULL, 'images/2_Tu_05.jpg', 'down');
INSERT INTO Face_Data (emp_id, face_encoding, image_path, angle) 
VALUES
    (3, NULL, 'images/3_Thanh_01.jpg', 'front'),
    (3, NULL, 'images/3_Thanh_02.jpg', 'left'),
    (3, NULL, 'images/3_Thanh_03.jpg', 'right'),
    (3, NULL, 'images/3_Thanh_04.jpg', 'up'),
    (3, NULL, 'images/3_Thanh_05.jpg', 'down');
INSERT INTO Face_Data (emp_id, face_encoding, image_path, angle) 
VALUES
    (5, NULL, 'images/5_Quy_01.jpg', 'front'),
    (5, NULL, 'images/5_Quy_02.jpg', 'left'),
    (5, NULL, 'images/5_Quy_03.jpg', 'right'),
    (5, NULL, 'images/5_Quy_04.jpg', 'up'),
    (5, NULL, 'images/5_Quy_05.jpg', 'down');