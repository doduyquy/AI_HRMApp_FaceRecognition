import cv2
import numpy as np
import tensorflow as tf
import imutils
import time
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont 

# Thêm thư mục src vào sys.path
src_dir = str(Path(__file__).resolve().parent.parent.parent)  # Lên 3 cấp để tới src
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Custom modules
from database import handleDB
from modules.path_cus import CASCADE_PATH, PB_PATH, EMBEDDING_PATH
from modules.constants_cus import THRESHOLD, FRAME_SKIP, BLUE_EXPAND, MIN_CHECKOUT_DELAY
from modules.recognize.image_processing import preprocess_image_for_model
from modules.recognize.attendance import attendance


### Hàm trích xuất khuôn mặt từ khung hình
def extract_face(image, cascade_path=CASCADE_PATH):
    # Tăng tốc xử lí
    img = imutils.resize(image, width=500)
    # Chuyển đổi ảnh sang ảnh xám
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Tải Haar -> phát hiện khuôn mặt
    detector = cv2.CascadeClassifier(cascade_path)
    
    """ gray			:	Ảnh xám đầu vào đã được chuyển đổi trước đó
	scaleFactor 	:	- Tỉ lệ thu nhỏ slide window đối với mỗi lần trượt qua toàn bộ ảnh
						VD: 1.03 -> giảm 3% mỗi lần
                    	- Tham số này thích hợp trong việc xác định nhiều khuôn mặt | khuôn mặt xa, gần
                    	Tuy nhiên khi đã set size ảnh cố định và thực tế thì khi chấm công, 
                        công nhân đưa khuôn mặt vào gần vào camera nên không quá khó trong việc
                        điều chỉnh tham số này.
                        
	minNeighbors	:	- trong một cửa sổ, nếu xác định là khuôn mặt thì các window gần đó
						cũng phải xác định đó là khuôn mặt (số lượng tối thiểu)
                        - Nếu tham số quá thấp: có thể xác định nhầm vật thể là khuôn mặt
                        - Nếu tham số quá cao: có thể bỏ qua khuôn mặt đúng
                        
	minSize			: 	- Kích thước tối thiểu cho một khuôn mặt, nếu nhỏ hơn thì bỏ qua
						- Do vậy việc set kích thước ảnh ban đầu và tỉ lệ scaleFactor kêt hợp với minSize 
                        rất quan trọng trong việc xác định đúng
    """
    faces = detector.detectMultiScale(gray, scaleFactor=1.03,
                                      minNeighbors=11,
                                      flags=cv2.CASCADE_SCALE_IMAGE)
    
    ### Nếu phát hiện khuôn mặt
    # faces:		:	danh sách các khuôn mặt được phát hiện
    if len(faces) > 0:
        x, y, w, h = faces[0]       # Lấy tọa độ khuôn mặt đầu tiên:
        face = img[y:y+h, x:x+w]    # Cắt khuôn mặt từ ảnh gốc
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)    # Chuyển từ BGR sang RGB

        # Return: khuôn mặt RGB đã cắt, tọa độ, ảnh gốc
        return face_rgb, (x, y, w, h), img
    # Nếu không phát hiện khuôn mặt
    return None, None, img

# Tải mô hình protobuf (.pb), return về graph tensorflow
def load_pb_model(pb_path):
    with tf.io.gfile.GFile(pb_path, 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
    return graph

# Trích xuất đặc trưng của khuôn mặt trong ảnh với model
def get_embedding_from_pb(graph, image_processed):
    # Lấy embedding từ image_processed bằng các tensor trong graph
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



# Nhận diện khuôn mặt trong thời gian thực qua camera
# Show kết quả lên UI
# Truy vấn database
def recognize_from_camera(ui, threshold=THRESHOLD, frame_skip=FRAME_SKIP, blue_expand=BLUE_EXPAND):
    # Tải embeddings từ file embeddings.py đã trích xuất trước đó.
    embeddings_dict = np.load(EMBEDDING_PATH, allow_pickle=True).item()
    
    # Mở camera thông qua giao diện
    if not ui.start_camera():
        return
    
    print("Bắt đầu nhận diện qua camera. Nhấn 'q' trong giao diện để thoát.")
    
    # Đếm số lượng khung hình (5 khung hình) -> xử lí để tránh lag
    frame_count = 0
    last_label = "Unknown"
    last_color = (0, 0, 255)
    
    while ui.is_running:
        # Đọc khung hình từ camera
        ret, frame = ui.cap.read()
        if not ret:
            print("Không thể đọc khung hình từ camera")
            break
        
        frame_count += 1
        # Nhận data từ hàm phát hiện khuôn mặt trong khung hình
        face, coords, processed_frame = extract_face(frame)
        
        # Luôn tô khung màu blue khi phát hiện khuôn mặt
        if face is not None and coords is not None:
            x, y, w, h = coords
            
            # Khung green: nhận diện thành công
            # Khung red: nhận diện không thành công
            # Khung blue: khuôn mặt đã nhận diện thành công trước đó.
           
            blue_x = max(0, x - blue_expand)
            blue_y = max(0, y - blue_expand)
            blue_w = w + 2 * blue_expand
            blue_h = h + 2 * blue_expand
            blue_w = min(blue_w, processed_frame.shape[1] - blue_x)
            blue_h = min(blue_h, processed_frame.shape[0] - blue_y)
            
            # Vẽ khung blue
            cv2.rectangle(processed_frame, (blue_x, blue_y), (blue_x + blue_w, blue_y + blue_h), (255, 0, 0), 2)
            
            # frame_skip: tiến hành nhận diện mỗi 5 khung hình
            if frame_count % frame_skip == 0:
                start_time = time.time()

                # Xử lí ảnh -> trích xuất đặc trưng
                face_processed = preprocess_image_for_model(face)
                face_embedding = get_embedding(face_processed)
                
                min_distance = float('inf')
                best_match_name = None
                
                # Duyệt qua danh sách các embedding đã lưu
                # Tính khoảng cách giữa embedding_current - embedding_stored
                # Lưu lại tên người có khoảng cách nhỏ nhất
                for id, stored_embedding in embeddings_dict.items():
                    distance = np.sqrt(np.sum(np.square(face_embedding - stored_embedding)))
                    if distance < min_distance:
                        min_distance = distance
                        best_match_id = id
                # Best match name: id_name
                best_match_name = f"{handleDB.handle.get_name_by_id(best_match_id)}" 
                
                # threshold: NGƯỠNG đã set từ trước
                # Nhỏ hơn threshold: nhận diện thành công
                # Lớn hơn threshold: nhận diện không thành công
                is_match = min_distance < threshold
                if is_match:
                    try:
                        # Vẽ khung green
                        cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        last_label = f"{best_match_id}-{best_match_name}"
                        last_color = (0, 255, 0)

                        # Cập nhật kết quả nhận diện trên giao diện
                        ui.set_recognition_result(f"{best_match_name} nhan dien thanh cong", success_recog=True, success_attend=False)

                        # Goij hàm attendance để xử lí chấm công
                        result, mess = attendance(ui, best_match_id, best_match_name)
                        if result:
                            ui.set_recognition_result(mess, success_recog=True, success_attend=True)
                        else:
                            ui.set_recognition_result(mess, success_recog=True, success_attend=False)
                        # except Exception as e:
                            # print(f"ERROR: attendance - {str(e)}")
                            # ui.set_recognition_result("Loi khi cham cong", success=False)
                        
                    except (TypeError, ValueError) as error:
                        print(f"ERROR: after recognize successfully - {str(error)}")
                        # ui.set_recognition_result("Nhan dien khong thanh cong, thu lai", success=False)
                else:
                    # Vẽ khung red
                    cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    last_label = "Unknown"
                    last_color = (0, 0, 255)
                    ui.set_recognition_result("Nhan dien khong thanh cong, thu lai", success_recog=False, success_attend=False)
            
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"Thời gian xử lý: {processing_time:.5f} giây")

            # # Đặt label lên khung
            # cv2.putText(processed_frame, last_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, last_color, 2)
            
            # Đặt label lên khung bằng PIL để hỗ trợ Tiếng Việt
            # Chuyển từ BGR sang RGB
            frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            draw = ImageDraw.Draw(pil_image)
            
            # Load font hỗ trợ Tiếng Việt
            try:
                font = ImageFont.truetype("arial.ttf", 25)  # Kích thước font 25
            except:
                font = ImageFont.load_default()  # Dùng font mặc định nếu không tìm thấy
            
            # Tính toán vị trí text nằm phía trên khung xanh
            text_x = blue_x  # Căn lề trái với khung xanh
            text_y = blue_y - 30  # Đặt text phía trên khung xanh, cách 30 pixel (điều chỉnh nếu cần)
            if text_y < 0:  # Đảm bảo text không bị cắt ra khỏi khung hình
                text_y = 0

            # Vẽ văn bản lên ảnh (chuyển màu từ BGR sang RGB)
            draw.text((text_x, text_y), last_label, font=font, fill=(last_color[2], last_color[1], last_color[0], 255))
            
            # Chuyển lại từ RGB sang BGR
            processed_frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # Cập nhật khung hình lên giao diện
        ui.update_camera_frame(processed_frame)

        # Kiểm tra phím 'q' để thoát (dùng sự kiện của tkinter)
        ui.root.update()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Dừng camera
    ui.stop_camera()