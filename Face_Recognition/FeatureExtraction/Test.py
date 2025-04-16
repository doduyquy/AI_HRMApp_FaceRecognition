import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from mtcnn import MTCNN
import matplotlib.pyplot as plt

# Hàm tiền xử lý ảnh cho mô hình
def preprocess_image_for_model(image, target_size=(128, 128)):
    img = cv2.resize(image, target_size)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# Hàm trích xuất khuôn mặt từ ảnh
def extract_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detector = MTCNN()
    faces = detector.detect_faces(img_rgb)
    if len(faces) > 0:
        x, y, w, h = faces[0]['box']
        face = img_rgb[y:y+h, x:x+w]
        return face
    else:
        raise ValueError(f"Không tìm thấy khuôn mặt trong ảnh: {image_path}")

# Hàm vẽ khung và ghi chú trên ảnh
def draw_result(image_path, is_match, name="Random"):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detector = MTCNN()
    faces = detector.detect_faces(img_rgb)
    if len(faces) > 0:
        x, y, w, h = faces[0]['box']
        color = (0, 255, 0) if is_match else (255, 0, 0)
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
        label = name if is_match else "Failed"
        cv2.putText(img, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Tải mô hình từ SavedModel
model_path = './deep_rank_model_optimized_savedmodel_new'  # Đường dẫn thực tế
loaded_model = tf.saved_model.load(model_path)

# Truy cập signature mặc định
model_signature = loaded_model.signatures['serving_default']

# Kiểm tra inputs và outputs
print("Inputs:", model_signature.inputs)
print("Outputs:", model_signature.outputs)

# Định nghĩa hàm để lấy anchor embedding
def get_anchor_embedding(image_processed):
    # Tạo đầu vào giả cho positive và negative
    dummy_input = np.zeros_like(image_processed)  # Shape: (1, 128, 128, 3)
    # Gọi model_signature với tên đầu vào đúng từ SavedModel
    output = model_signature(
        inputs=image_processed,       # Đầu vào anchor
        inputs_1=dummy_input,         # Đầu vào positive
        inputs_2=dummy_input          # Đầu vào negative
    )
    # Lấy tensor đầu ra (384 chiều) và cắt lấy 128 chiều đầu tiên (anchor)
    full_output = list(output.values())[0]  # Lấy tensor đầu tiên từ OrderedDict
    anchor_embedding = full_output[:, 0:128]  # Lấy embedding anchor
    return anchor_embedding.numpy()  # Chuyển về numpy array

# Đường dẫn đến các ảnh
original_image_path = '../Data/Random/anchor_random.jpg'
compare_image_paths = ['../Data/Random/positive_random.jpg', '../Data/Random/negative_random.jpg']

# Trích xuất khuôn mặt từ ảnh gốc
original_face = extract_face(original_image_path)
original_face_processed = preprocess_image_for_model(original_face)

# Trích xuất embedding từ ảnh gốc
original_embedding = get_anchor_embedding(original_face_processed)

# Ngưỡng để xác định xem có phải cùng một người hay không
# Nếu distance < THRESHOLD: Hai ảnh được coi là cùng một người (match).
# Nếu distance >= THRESHOLD: Hai ảnh được coi là khác người (not match).
THRESHOLD = 0.05

# So sánh với từng ảnh
results = []
for compare_path in compare_image_paths:
    compare_face = extract_face(compare_path)
    compare_face_processed = preprocess_image_for_model(compare_face)
    compare_embedding = get_anchor_embedding(compare_face_processed)
    distance = np.sqrt(np.sum(np.square(original_embedding - compare_embedding)))
    print(f"Khoảng cách giữa {original_image_path} và {compare_path}: {distance}")
    is_match = distance < THRESHOLD
    results.append((compare_path, is_match))

# Hiển thị kết quả
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
original_img = cv2.imread(original_image_path)
original_img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
plt.imshow(original_img_rgb)
plt.title("Ảnh gốc (Random)")
plt.axis('off')

plt.subplot(1, 3, 2)
result_img_1 = draw_result(results[0][0], results[0][1])
plt.imshow(result_img_1)
plt.title("So sánh với positive.jpg")
plt.axis('off')

plt.subplot(1, 3, 3)
result_img_2 = draw_result(results[1][0], results[1][1])
plt.imshow(result_img_2)
plt.title("So sánh với negative.jpg")
plt.axis('off')

plt.show()