import cv2
import numpy as np

# Hàm tiền xử lý ảnh: chuẩn hóa size 160x160, định dạng phù hợp
def preprocess_image_for_model(image, target_size=(160, 160)):
    img = cv2.resize(image, target_size)
    img = img / 255.0   # Chuẩn hóa giá trị pixel [0, 255] -> [0, 1]
    img = img - 0.5     # Giá trị pixel: [0, 1] -> [-0.5, 0.5]
    img = img * 2.0     # Giá trị pixel: [-0.5, 0.5] -> [-1, 1]
    # Thêm 1 chiều vào tensor -> xử lí batch, size tensor: [1, 160, 160, 3]
    img = np.expand_dims(img, axis=0)   
    return img
