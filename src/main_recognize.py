### CHẤM BẰNG NHẬN DIỆN ###
# Hiển thị giao diện nhận diện nhân viên

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import threading


### Custom imports
# Thêm thư mục src vào sys.path
src_dir = str(Path(__file__).resolve().parent.parent)  # Lên 2 cấp để tới src
if src_dir not in sys.path:
    sys.path.append(src_dir)

from src.ui.recognize import UI_FaceRecognition  # Import giao diện
from modules.recognize.recognize_face import recognize_from_camera


# Chạy chương trình
if __name__ == "__main__":
    root = tk.Tk()
    ui = UI_FaceRecognition(root)
    # Chạy nhận diện trong một luồng riêng để không làm treo giao diện
    recognition_thread = threading.Thread(target=recognize_from_camera, args=(ui,))
    recognition_thread.start()
    root.mainloop()