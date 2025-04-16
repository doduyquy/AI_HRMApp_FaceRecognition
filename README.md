# AI_HRMApp_FaceRecognition
Project Python about Human Resource Manager(HRM) using face_recognition for timekeeping

### Cấu trúc:

- Data/             :   lưu các ảnh khuôn mặt và ảnh đai diện (avatar)
- exports/          :   các file excel đã export ra
- Face_Recognition/ :   các document về model của dự án
- images/           :   lưu, thao tác (thểm sửa xóa) các ảnh khuôn mặt của nhân viên

#### src/

- src/database/     :   các file khởi tạo database & xử lí, thao tác với database
- src/img/          :   các file ảnh (icon, ....)
- src/models/       :   lưu các models, haar, features.npy
- src/modules/...   :   xử lí logic, các module dùng chung như path, constants,(path custom- path_cus)
- src/recognize/    :   trích xuất đặc trưng của khuôn mặt, các file test nhận diện
- src/ui            :   giao diện của toàn bộ project

- main...           :   chạy chương trình