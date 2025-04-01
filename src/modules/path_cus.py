# src/modules/path_cus.py
from pathlib import Path

# .../src
SRC_DIR = Path(__file__).resolve(strict=True).parent.parent

### Định nghĩa path cho các file đầu vào:
# Haar Cascade 
CASCADE_PATH = SRC_DIR / "models" / "haarcascade_frontalface_default.xml"
# Model.pb path
PB_PATH = SRC_DIR / "models" / "20180402-114759.pb"
# Data path
DATA_DIR_PATH = SRC_DIR.parent / "Data"
# Features embedding path
EMBEDDING_PATH = SRC_DIR / "models" / "embeddings.npy"


if __name__ == "__main__":
    print(f"Source Directory: {SRC_DIR}")
    print(f"Đường dẫn haarcascade: {CASCADE_PATH}")
    print(f"Đường dẫn mô hình: {PB_PATH}")
    print(f"Đường dẫn dữ liệu: {DATA_DIR_PATH}")
    print(f"Đường dẫn embeddings: {EMBEDDING_PATH}")