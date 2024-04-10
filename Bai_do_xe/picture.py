import tkinter as tk
from PIL import Image, ImageTk

def display_image(image_path):
    # Tạo cửa sổ Tkinter
    root = tk.Tk()
    root.title("Hiển thị ảnh")

    # Tạo frame để chứa label
    frame = tk.Frame(root, bg="white")
    frame.pack(fill="both", expand=True)

    # Load ảnh
    image = Image.open(image_path)

    # Lấy kích thước của ảnh và màn hình
    image_width, image_height = image.size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Tính tỷ lệ để resize ảnh
    aspect_ratio = min(screen_width / image_width, screen_height / image_height)
    new_width = int(image_width * aspect_ratio)
    new_height = int(image_height * aspect_ratio)

    # Resize ảnh
    image = image.resize((new_width, new_height))

    # Chuyển đổi ảnh sang định dạng phù hợp cho Tkinter
    image_tk = ImageTk.PhotoImage(image)

    # Tạo label để hiển thị ảnh
    label = tk.Label(frame, image=image_tk, bg="white")
    label.pack(fill="both", expand=True)

    # Đặt kích thước của cửa sổ theo kích thước của ảnh
    root.geometry(f"{new_width}x{new_height}")

    # Hiển thị cửa sổ
    root.mainloop()
