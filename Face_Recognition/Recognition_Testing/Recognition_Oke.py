import cv2
import numpy as np
import tensorflow as tf
from mtcnn import MTCNN
import matplotlib.pyplot as plt

# Hàm tiền xử lý ảnh cho FaceNet
def preprocess_image_for_model(image, target_size=(160, 160)):
    img = cv2.resize(image, target_size)
    img = img / 255.0
    img = img - 0.5
    img = img * 2.0
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

# Tải mô hình .pb
def load_pb_model(pb_path):
    with tf.io.gfile.GFile(pb_path, 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
    return graph

def get_embedding_from_pb(graph, image_processed):
    with tf.compat.v1.Session(graph=graph) as sess:
        images_placeholder = graph.get_tensor_by_name('input:0')
        embeddings = graph.get_tensor_by_name('embeddings:0')
        phase_train_placeholder = graph.get_tensor_by_name('phase_train:0')
        feed_dict = {images_placeholder: image_processed, phase_train_placeholder: False}
        embedding = sess.run(embeddings, feed_dict=feed_dict)
    return embedding

# Tải mô hình
pb_path = './20180402-114759.pb'
graph = load_pb_model(pb_path)

# Định nghĩa hàm lấy embedding
def get_embedding(image_processed):
    return get_embedding_from_pb(graph, image_processed)

# Đường dẫn đến các ảnh
# original_image_path = '../Data/Ronaldo/anchor.jpg'
# compare_image_paths = ['../Data/Ronaldo/positive.jpg', 
#                        '../Data/Ronaldo/negative.jpg']
original_image_path = '../Data/P01/anchor.jpg'
compare_image_paths = ['../Data/P01/positive.jpg', 
                       '../Data/P01/negative.jpg']



# Trích xuất và xử lý
original_face = extract_face(original_image_path)
original_face_processed = preprocess_image_for_model(original_face)
original_embedding = get_embedding(original_face_processed)

# Ngưỡng
THRESHOLD = 0.8

# So sánh
results = []
for compare_path in compare_image_paths:
    compare_face = extract_face(compare_path)
    compare_face_processed = preprocess_image_for_model(compare_face)
    compare_embedding = get_embedding(compare_face_processed)
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