import sys
from pathlib import Path
import tkinter as tk
from ui.IT import ITApp  

# Thêm thư mục gốc vào sys.path
src_dir = str(Path(__file__).resolve().parent)  # Thư mục src/
if src_dir not in sys.path:
    sys.path.append(src_dir)

if __name__ == "__main__":
    root = tk.Tk()
    app = ITApp(root)
    root.mainloop()
    
    