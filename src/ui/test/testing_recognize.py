import cv2
import numpy as np
import tensorflow as tf
import imutils
import os
import time
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import threading
from PIL import Image, ImageTk


# Thêm thư mục src vào sys.path
src_dir = str(Path(__file__).resolve().parent.parent)  # Lên 2 cấp để tới src
if src_dir not in sys.path:
    sys.path.append(src_dir)

from database import handleDB
from recognize import UI_FaceRecognition  # Import giao diện

# Lấy đường dẫn thư mục chứa Recognize_live.py
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Đường dẫn hiện tại: {current_dir}")

### Định nghĩa path cho các file đầu vào:
CASCADE_PATH = os.path.abspath(os.path.join(current_dir, "../models/haarcascade_frontalface_default.xml"))
PB_PATH = os.path.abspath(os.path.join(current_dir, "../models/20180402-114759.pb"))
EMBEDDING_PATH = os.path.abspath(os.path.join(current_dir, "../models/embeddings.npy"))

MIN_CHECKOUT_DELAY = 3600  # Thời gian tối thiểu (giây) giữa check-in và check-out: 1 giờ = 3600 giây

# Định nghĩa các thông số cho nhận diện 
THRESHOLD = 0.8  # Ngưỡng để xác định đúng người hay không
FRAME_SKIP = 5  # Xử lý nhận diện mỗi 5 khung hình
BLUE_EXPAND = 10  # Số pixel mở rộng khung xanh lam

# Hàm tiền xử lý ảnh
def preprocess_image_for_model(image, target_size=(160, 160)):
    img = cv2.resize(image, target_size)
    img = img / 255.0
    img = img - 0.5
    img = img * 2.0
    img = np.expand_dims(img, axis=0)
    return img

# Hàm trích xuất khuôn mặt từ khung hình
def extract_face(image, cascade_path=CASCADE_PATH):
    img = imutils.resize(image, width=500)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier(cascade_path)
    
    faces = detector.detectMultiScale(gray, scaleFactor=1.03,
                                      minNeighbors=11,
                                      flags=cv2.CASCADE_SCALE_IMAGE)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        face = img[y:y+h, x:x+w]
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        return face_rgb, (x, y, w, h), img
    return None, None, img

# Tải mô hình .pb
def load_pb_model(pb_path):
    with tf.io.gfile.GFile(pb_path, 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
    return graph

# Trích xuất đặc trưng embedding
def get_embedding_from_pb(graph, image_processed):
    with tf.compat.v1.Session(graph=graph) as sess:
        images_placeholder = graph.get_tensor_by_name('input:0')
        embeddings = graph.get_tensor_by_name('embeddings:0')
        phase_train_placeholder = graph.get_tensor_by_name('phase_train:0')
        feed_dict = {images_placeholder: image_processed, phase_train_placeholder: False}
        embedding = sess.run(embeddings, feed_dict=feed_dict)
    return embedding

# Tải mô hình
graph = load_pb_model(PB_PATH)

# Định nghĩa hàm lấy embedding
def get_embedding(image_processed):
    return get_embedding_from_pb(graph, image_processed)

# Hàm nhận diện qua camera
def recognize_from_camera(ui, threshold=THRESHOLD, frame_skip=FRAME_SKIP, blue_expand=BLUE_EXPAND):
    # Tải đặc trưng đã lưu
    embeddings_dict = np.load(EMBEDDING_PATH, allow_pickle=True).item()
    
    # Mở camera thông qua giao diện
    if not ui.start_camera():
        return
    
    print("Bắt đầu nhận diện qua camera. Nhấn 'q' trong giao diện để thoát.")
    
    frame_count = 0
    last_label = "Unknown"
    last_color = (0, 0, 255)
    
    # Dictionary để lưu thời gian nhận diện gần nhất
    last_recognition_time = {}
    stt_counter = len(ui.tree.get_children()) + 1  # Đếm STT từ số bản ghi hiện có trong bảng

    while ui.is_running:
        ret, frame = ui.cap.read()
        if not ret:
            print("Không thể đọc khung hình từ camera")
            break
        
        frame_count += 1
        # Trích xuất khuôn mặt từ khung hình
        face, coords, processed_frame = extract_face(frame)
        
        # Luôn tô khung màu xanh lam khi phát hiện khuôn mặt
        if face is not None and coords is not None:
            x, y, w, h = coords
           
            # Mở rộng khung xanh lam
            blue_x = max(0, x - blue_expand)
            blue_y = max(0, y - blue_expand)
            blue_w = w + 2 * blue_expand
            blue_h = h + 2 * blue_expand
            blue_w = min(blue_w, processed_frame.shape[1] - blue_x)
            blue_h = min(blue_h, processed_frame.shape[0] - blue_y)
            
            # Vẽ khung xanh lam
            cv2.rectangle(processed_frame, (blue_x, blue_y), (blue_x + blue_w, blue_y + blue_h), (255, 0, 0), 2)
            
            # Chỉ nhận diện mỗi frame_skip khung hình
            if frame_count % frame_skip == 0:
                start_time = time.time()

                # Trích xuất đặc trưng và nhận diện
                face_processed = preprocess_image_for_model(face)
                face_embedding = get_embedding(face_processed)
                
                # So sánh với các đặc trưng đã lưu
                min_distance = float('inf')
                best_match_name = None
                
                for name, stored_embedding in embeddings_dict.items():
                    distance = np.sqrt(np.sum(np.square(face_embedding - stored_embedding)))
                    if distance < min_distance:
                        min_distance = distance
                        best_match_name = name
                
                # Lấy thời gian hiện tại
                current_time = datetime.now()
                current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

                # Xác định kết quả
                is_match = min_distance < threshold
                if is_match:
                    try:
                        # Vẽ khung xanh lá
                        cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        last_label = best_match_name
                        last_color = (0, 255, 0)

                        # Cập nhật kết quả nhận diện trên giao diện
                        ui.set_recognition_result(f"{best_match_name} nhan dien thanh cong", success=True)

                        # Xử lý chấm công
                        emp_id = int(best_match_name)
                        last_time = last_recognition_time.get(emp_id)
                        if last_time is None or (current_time - last_time).total_seconds() > 10:
                            last_attendance = handleDB.handle.get_last_attendance(emp_id)
                            
                            if last_attendance is None or last_attendance['check_out'] is not None:
                                # Check-in mới
                                handleDB.handle.write_check_in_to_db(emp_id, current_time_str)
                                print(f"Check-in: {emp_id} at {current_time_str}")
                                # Thêm vào dòng đầu tiên của bảng trên giao diện
                                ui.add_attendance_record(
                                    stt_counter,
                                    f"NV{emp_id:03d}",
                                    best_match_name,
                                    current_time.strftime("%H:%M:%S")
                                )
                                stt_counter += 1
                            else:
                                # Check-out
                                last_check_in = last_attendance['check_in']
                                time_diff = (current_time - last_check_in).total_seconds()
                                if time_diff >= MIN_CHECKOUT_DELAY:
                                    handleDB.handle.update_check_out_to_db(emp_id, current_time_str, last_attendance['date'])
                                    print(f"Check-out: {emp_id} at {current_time_str}")
                                    # Cập nhật bảng trên giao diện (tìm bản ghi và thêm thời gian check-out)
                                    for item in ui.tree.get_children():
                                        values = ui.tree.item(item, "values")
                                        if values[1] == f"NV{emp_id:03d}" and values[4] == "":
                                            ui.tree.set(item, "Ra", current_time.strftime("%H:%M:%S"))
                                            break
                                else:
                                    print(f"Chưa đủ {MIN_CHECKOUT_DELAY // 3600} giờ để check-out cho {emp_id}")
                            
                            last_recognition_time[emp_id] = current_time
                        
                    except (TypeError, ValueError) as error:
                        print(f"ERROR: after recognize successfully - {str(error)}")
                        ui.set_recognition_result("Nhan dien khong thanh cong, thu lai", success=False)
                else:
                    # Vẽ khung đỏ
                    cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    last_label = "Unknown"
                    last_color = (0, 0, 255)
                    ui.set_recognition_result("Nhan dien khong thanh cong, thu lai", success=False)
            
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"Thời gian xử lý: {processing_time:.5f} giây")

            # Đặt label lên khung
            cv2.putText(processed_frame, last_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, last_color, 2)
        
        # Cập nhật khung hình lên giao diện
        ui.update_camera_frame(processed_frame)

        # Kiểm tra phím 'q' để thoát (dùng sự kiện của tkinter)
        ui.root.update()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Dừng camera
    ui.stop_camera()

# def recognize_from_camera(ui, threshold=THRESHOLD, frame_skip=FRAME_SKIP, blue_expand=BLUE_EXPAND):
#     # Tải đặc trưng đã lưu
#     embeddings_dict = np.load(EMBEDDING_PATH, allow_pickle=True).item()
    
#     # Mở camera thông qua giao diện
#     if not ui.start_camera():
#         return
    
#     print("Bắt đầu nhận diện qua camera. Nhấn 'q' trong giao diện để thoát.")
    
#     frame_count = 0
#     last_label = "Unknown"
#     last_color = (0, 0, 255)
    
#     # Dictionary để lưu thời gian nhận diện gần nhất
#     last_recognition_time = {}
#     stt_counter = len(ui.tree.get_children()) + 1  # Đếm STT từ số bản ghi hiện có trong bảng

#     while ui.is_running:
#         ret, frame = ui.cap.read()
#         if not ret:
#             print("Không thể đọc khung hình từ camera")
#             break
        
#         frame_count += 1
#         # Trích xuất khuôn mặt từ khung hình
#         face, coords, processed_frame = extract_face(frame)
        
#         # Luôn tô khung màu xanh lam khi phát hiện khuôn mặt
#         if face is not None and coords is not None:
#             x, y, w, h = coords
           
#             # Mở rộng khung xanh lam
#             blue_x = max(0, x - blue_expand)
#             blue_y = max(0, y - blue_expand)
#             blue_w = w + 2 * blue_expand
#             blue_h = h + 2 * blue_expand
#             blue_w = min(blue_w, processed_frame.shape[1] - blue_x)
#             blue_h = min(blue_h, processed_frame.shape[0] - blue_y)
            
#             # Vẽ khung xanh lam
#             cv2.rectangle(processed_frame, (blue_x, blue_y), (blue_x + blue_w, blue_y + blue_h), (255, 0, 0), 2)
            
#             # Chỉ nhận diện mỗi frame_skip khung hình
#             if frame_count % frame_skip == 0:
#                 start_time = time.time()

#                 # Trích xuất đặc trưng và nhận diện
#                 face_processed = preprocess_image_for_model(face)
#                 face_embedding = get_embedding(face_processed)
                
#                 # So sánh với các đặc trưng đã lưu
#                 min_distance = float('inf')
#                 best_match_name = None
                
#                 for name, stored_embedding in embeddings_dict.items():
#                     distance = np.sqrt(np.sum(np.square(face_embedding - stored_embedding)))
#                     if distance < min_distance:
#                         min_distance = distance
#                         best_match_name = name
                
#                 # Lấy thời gian hiện tại
#                 current_time = datetime.now()
#                 current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

#                 # Xác định kết quả
#                 is_match = min_distance < threshold
#                 if is_match:
#                     try:
#                         # Vẽ khung xanh lá
#                         cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#                         last_label = best_match_name
#                         last_color = (0, 255, 0)

#                         # Cập nhật kết quả nhận diện trên giao diện
#                         ui.set_recognition_result(f"{best_match_name} nhan dien thanh cong", success=True)

#                         # Xử lý chấm công
#                         emp_id = int(best_match_name)
#                         last_time = last_recognition_time.get(emp_id)
#                         if last_time is None or (current_time - last_time).total_seconds() > 10:
#                             last_attendance = handleDB.handle.get_last_attendance(emp_id)
                            
#                             if last_attendance is None or last_attendance['check_out'] is not None:
#                                 # Check-in mới
#                                 handleDB.handle.write_check_in_to_db(emp_id, current_time_str)
#                                 print(f"Check-in: {emp_id} at {current_time_str}")
#                                 # Thêm vào bảng trên giao diện
#                                 ui.add_attendance_record(
#                                     stt_counter,
#                                     f"NV{emp_id:03d}",
#                                     best_match_name,
#                                     current_time.strftime("%H:%M:%S")
#                                 )
#                                 stt_counter += 1
#                             else:
#                                 # Check-out
#                                 last_check_in = last_attendance['check_in']
#                                 time_diff = (current_time - last_check_in).total_seconds()
#                                 if time_diff >= MIN_CHECKOUT_DELAY:
#                                     handleDB.handle.update_check_out_to_db(emp_id, current_time_str, last_attendance['date'])
#                                     print(f"Check-out: {emp_id} at {current_time_str}")
#                                     # Cập nhật bảng trên giao diện (tìm bản ghi và thêm thời gian check-out)
#                                     for item in ui.tree.get_children():
#                                         values = ui.tree.item(item, "values")
#                                         if values[1] == f"NV{emp_id:03d}" and values[4] == "":
#                                             ui.tree.set(item, "Ra", current_time.strftime("%H:%M:%S"))
#                                             break
#                                 else:
#                                     print(f"Chưa đủ {MIN_CHECKOUT_DELAY // 3600} giờ để check-out cho {emp_id}")
                            
#                             last_recognition_time[emp_id] = current_time
                        
#                     except (TypeError, ValueError) as error:
#                         print(f"ERROR: after recognize successfully - {str(error)}")
#                         ui.set_recognition_result("Nhan dien khong thanh cong, thu lai", success=False)
#                 else:
#                     # Vẽ khung đỏ
#                     cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
#                     last_label = "Unknown"
#                     last_color = (0, 0, 255)
#                     ui.set_recognition_result("Nhan dien khong thanh cong, thu lai", success=False)
            
#                 end_time = time.time()
#                 processing_time = end_time - start_time
#                 print(f"Thời gian xử lý: {processing_time:.5f} giây")

#             # Đặt label lên khung
#             cv2.putText(processed_frame, last_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, last_color, 2)
        
#         # Cập nhật khung hình lên giao diện
#         ui.update_camera_frame(processed_frame)

#         # Kiểm tra phím 'q' để thoát (dùng sự kiện của tkinter)
#         ui.root.update()
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
    
#     # Dừng camera
#     ui.stop_camera()

# Chạy chương trình
if __name__ == "__main__":
    root = tk.Tk()
    ui = UI_FaceRecognition(root)
    # Chạy nhận diện trong một luồng riêng để không làm treo giao diện
    recognition_thread = threading.Thread(target=recognize_from_camera, args=(ui,))
    recognition_thread.start()
    root.mainloop()