import tkinter as tk
from datetime import datetime
import pyodbc
from module_recognize import detect_and_process_license_plate
import threading
from tkinter import font
import time
import locale
from PIL import Image, ImageTk
import serial
from tkinter import messagebox

# Thiết lập ngôn ngữ mặc định là tiếng Việt
locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')

global ser
global ser2

conn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAGGER\CHIEN;DATABASE=Python4;Trusted_Connection=yes;')
cursor = conn.cursor()

global info_text_vao
info_text_vao = ""

global info_text_ra
info_text_ra = ""

# Label đồng hồ
global clock_label
global image_label_vao
global image_label_ra

def connect_arduino(port='COM5', baudrate=9600, timeout=1):
    global ser
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        messagebox.showinfo("Thông báo", f"Đã kết nối tới Arduino vào trên cổng {port}")
        print("Đã kết nối tới Arduino trên cổng", port)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kết nối tới Arduino vào: {e}")
        print("Đã xảy ra lỗi khi kết nối tới Arduino:", e)

def end_connect():
    global ser
    try:
        ser.close()
        print("Đã ngắt kết nối tới Arduino")
        messagebox.showinfo("Thông báo", f"Đã đóng kết nối tới Arduino")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi đóng kết nối tới Arduino: {e}")
        print("Đã xảy ra lỗi khi ngắt kết nối tới Arduino:", e)

def connect_both():
    connect_arduino()
    connect_arduino2()
    
def end_both():
    end_connect()
    end_connect2()

def connect_arduino2(port='COM6', baudrate=9600, timeout=1):
    global ser2
    try:
        ser2 = serial.Serial(port, baudrate, timeout=timeout)
        messagebox.showinfo("Thông báo", f"Đã kết nối tới Arduino ra trên cổng {port}")
        print("Đã kết nối tới Arduino trên cổng", port)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kết nối tới Arduino: {e}")
        print("Đã xảy ra lỗi khi kết nối tới Arduino:", e)

def end_connect2():
    global ser2
    try:
        ser2.close()
        print("Đã ngắt kết nối tới Arduino")
        messagebox.showinfo("Thông báo", f"Đã đóng kết nối tới Arduino ra")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi đóng kết nối tới Arduino: {e}")
        print("Đã xảy ra lỗi khi ngắt kết nối tới Arduino:", e)

def send_command_to_arduino():
    try:
        if ser.is_open:
            ser.write(b'1')
            print("Đã gửi lệnh mở cổng ra bãi.")
        else:
            print("Chưa kết nối tới Arduino. Không thể gửi lệnh.")
    except Exception as e:
        print("Đã xảy ra lỗi khi gửi lệnh tới Arduino:", e)

def lcd_bien(license_plate):
    try:
        if ser.is_open:
            # Gửi thông tin biển số qua cổng serial
            ser.write(license_plate.encode())
            print("Đã gửi thông tin biển số tới Arduino:", license_plate)
        else:
            print("Chưa kết nối tới Arduino. Không thể gửi lệnh.")
    except Exception as e:
        print("Đã xảy ra lỗi khi gửi lệnh tới Arduino:", e)


def send_command_to_arduino2():
    try:
        if ser2.is_open:
            ser2.write(b'1')
            print("Đã gửi lệnh mở cổng ra bãi.")
        else:
            print("Chưa kết nối tới Arduino. Không thể gửi lệnh.")
    except Exception as e:
        print("Đã xảy ra lỗi khi gửi lệnh tới Arduino:", e)

def update_clock(clock_label):
    current_time = time.strftime('%A, %d %B %Y,  %H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000, update_clock, clock_label)  

def them_xe_vao():
    threading.Thread(target=process_license_plate_and_update_label_vao).start()

def xe_ra_bai():
    threading.Thread(target=process_license_plate_and_update_label_ra).start()

def update_image(image_label_vao):
    try:
        image = Image.open("crop.jpg")
        image = ImageTk.PhotoImage(image)
        image_label_vao.configure(image=image)
        image_label_vao.image = image
        image_label_vao.after(7000, lambda: clear_image(image_label_vao))
    except FileNotFoundError:
        print("Không tìm thấy file crop.jpg")

def clear_image(image_label_vao):
    image_label_vao.configure(image=None)

def update_image_ra(image_label_ra):
    try:
        image = Image.open("crop.jpg")
        image = ImageTk.PhotoImage(image)
        image_label_ra.configure(image=image)
        image_label_ra.image = image
        image_label_ra.after(7000, lambda: clear_image(image_label_ra))
    except FileNotFoundError:
        print("Không tìm thấy file crop.jpg")

def clear_image_ra(image_label_ra):
    image_label_ra.configure(image=None)

def process_license_plate_and_update_label_vao():
    global info_text_vao
    generator = detect_and_process_license_plate()  # Lưu trữ generator
    for bien_so in generator:  # Lặp qua từng biển số đã nhận dạng
        update_image(image_label_vao)
        if bien_so:
            try:
                cursor.execute("""
                        SELECT BienSo.MaBien, BienSo.SoBien, XeVao.ThoiGianVao, CuDan.TenCuDan, CuDan.DiaChi, LoaiXe.TenLoai
                        FROM BienSo
                        JOIN XeVao ON XeVao.MaBien = BienSo.MaBien
                        JOIN CuDan ON CuDan.MaBien = BienSo.MaBien
                        JOIN LoaiXe ON LoaiXe.MaLoai = BienSo.MaLoai
                        WHERE BienSo.SoBien = ?
                    """, (bien_so,))
                row = cursor.fetchone()
                if row:
                    ma_bien = row[0]
                    ten_cu_dan = row[3]  # Tên cư dân
                    dia_chi = row[4]  # Địa chỉ
                    loai_xe = row[5]  # Loại xe
                    cursor.execute("INSERT INTO XeVao (MaBien, ThoiGianVao) VALUES (?, CURRENT_TIMESTAMP)", (ma_bien,))
                    cursor.execute("UPDATE BienSo SET TrangThai = 1 WHERE MaBien = ?", (ma_bien,))
                    print('Xe đã vào bãi thành công vào lúc', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    info_text_vao = f"Biển số: {bien_so}\nTên cư dân: {ten_cu_dan}\nĐịa chỉ: {dia_chi}\nLoại xe: {loai_xe}\n\nXe đã vào bãi lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    lbl_info_vao.config(text=info_text_vao)  # Cập nhật nội dung của label
                    lbl_info_vao.after(7000, clear_info_label_vao)
                    #lcd_bien(bien_so)
                    send_command_to_arduino()
                    print("Mở cửa")
                else:
                    print('Biển số không tồn tại trong cơ sở dữ liệu. Không thể cho xe vào.')
                    info_text_vao = "Biển số không tồn tại trong cơ sở dữ liệu. Không thể cho xe vào."
                    lbl_info_vao.config(text=info_text_vao)  # Cập nhật nội dung của label
                    lbl_info_vao.after(7000, clear_info_label_vao)

                conn.commit()
            except Exception as e:
                print('Đã xảy ra lỗi:', e)
                info_text_vao = "Đã xảy ra lỗi: " + str(e)
                lbl_info_vao.config(text=info_text_vao)  # Cập nhật nội dung của label
                lbl_info_vao.after(7000, clear_info_label_vao)
        else:
            print("Không thể nhận diện biển số xe.")
            info_text_vao = "Không thể nhận diện biển số xe."
            lbl_info_vao.config(text=info_text_vao)  # Cập nhật nội dung của label
            lbl_info_vao.after(7000, clear_info_label_vao)

def clear_info_label_vao():
    global info_text_vao
    info_text_vao = ""
    lbl_info_vao.config(text="")

def process_license_plate_and_update_label_ra():
    global info_text_ra
    generator = detect_and_process_license_plate()  # Lưu trữ generator
    for bien_so in generator:  # Lặp qua từng biển số đã nhận dạng
        update_image_ra(image_label_ra)
        if bien_so:
            try:
                cursor.execute("""
                        SELECT BienSo.MaBien, BienSo.SoBien, XeVao.ThoiGianVao, CuDan.TenCuDan, CuDan.DiaChi, LoaiXe.TenLoai
                        FROM BienSo
                        JOIN XeVao ON XeVao.MaBien = BienSo.MaBien
                        JOIN CuDan ON CuDan.MaBien = BienSo.MaBien
                        JOIN LoaiXe ON LoaiXe.MaLoai = BienSo.MaLoai
                        WHERE BienSo.SoBien = ? AND TrangThai = 1
                    """, (bien_so,))
                #cursor.execute("SELECT MaBien FROM BienSo WHERE SoBien = ? AND TrangThai = 1", (bien_so,))
                row = cursor.fetchone()

                if row:
                    ma_bien = row[0]
                    ten_cu_dan = row[3]  # Tên cư dân
                    dia_chi = row[4]  # Địa chỉ
                    loai_xe = row[5]  # Loại xe
                    cursor.execute("UPDATE BienSo SET TrangThai = 0 WHERE MaBien = ?", (ma_bien,))
                    cursor.execute("INSERT INTO XeRa (MaBien, ThoiGianRa) VALUES (?, CURRENT_TIMESTAMP)", (ma_bien,))
                    
                    cursor.execute("SELECT ThoiGianVao FROM XeVao WHERE MaBien = ?", (ma_bien,))
                    thoi_gian_vao = cursor.fetchone()[0]
                    
                    print('Xe đã ra khỏi bãi vào lúc', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    print('Thời gian vào bãi:', thoi_gian_vao.strftime('%Y-%m-%d %H:%M:%S'))
                    send_command_to_arduino2()
                    print("Mở cổng ra")
                    info_text_ra = f"Biển số: {bien_so}\nTên cư dân: {ten_cu_dan}\nĐịa chỉ: {dia_chi}\nLoại xe: {loai_xe}\n\nXe đã ra khỏi bãi vào lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nThời gian vào bãi: {thoi_gian_vao.strftime('%Y-%m-%d %H:%M:%S')}"
                    lbl_info_ra.config(text=info_text_ra)
                    lbl_info_ra.after(7000, clear_info_label_ra)
                else:
                    print('Xe không có ở trong bãi.')
                    info_text_ra = "Xe không có ở trong bãi."
                    lbl_info_ra.config(text=info_text_ra)
                    lbl_info_ra.after(7000, clear_info_label_ra)

                conn.commit()
            except Exception as e:
                print('Đã xảy ra lỗi:', e)
                info_text_ra = 'Đã xảy ra lỗi: ' + str(e)
                lbl_info_ra.config(text=info_text_ra)
                lbl_info_ra.after(7000, clear_info_label_ra)
        else:
            print("Không thể nhận diện biển số xe.")
            info_text_ra = 'Không thể nhận diện biển số xe.'
            lbl_info_ra.config(text=info_text_ra)
            lbl_info_ra.after(7000, clear_info_label_ra)

def clear_info_label_ra():
    global info_text_ra
    info_text_ra = ""
    lbl_info_ra.config(text="")

def create_gui(parent):
    page_frame = tk.Frame(parent)
    label_font = font.Font(family="Arial", size=14, weight="bold")
    info_font = font.Font(family="Arial", size = 12,weight="bold")
    ##############################################################################################
    # Tạo pack cổng vào
    frame_vao = tk.Frame(page_frame,borderwidth=1, relief="solid")
    frame_vao.pack(side="left", fill="both", expand=True)

    # Tạo frame lable vao
    frame_label_vao = tk.Frame(frame_vao,bg="white", borderwidth=0, relief="solid")
    frame_label_vao.place(x=0,rely=0.7, relwidth=1, relheight=0.3)    
    # Tạo frame thông tin vao
    frame_thongtin_vao = tk.Frame(frame_vao,bg="white", borderwidth=0, relief="solid")
    frame_thongtin_vao.place(x=0,rely=0.1, relwidth=1, relheight=0.6)
    # Tạo frame button vao
    frame_button_vao = tk.Frame(frame_vao,bg="white", borderwidth=0, relief="solid")
    frame_button_vao.place(x=0,y=0, relwidth= 1, relheight= 0.1)
    #frame info vao
    frame_info_vao = tk.Frame(frame_label_vao, borderwidth=3, relief="raised")
    frame_info_vao.place(relx=0.05, rely= 0.3, relheight=0.65, relwidth=0.55)
    # Tạo frame video vao 
    #frame_video_vao = tk.Frame(frame_thongtin_vao,borderwidth=3, relief="raised")
    #frame_video_vao.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)
    # Tạo frame ảnh biển vào
    frame_anh_vao = tk.Frame(frame_label_vao, borderwidth=3, relief="raised")
    frame_anh_vao.place(relx=0.65, rely=0.3,relheight=0.65, relwidth=0.3) 
    
    # Button "Xe vào"
    btn_vao = tk.Button(frame_button_vao,bg="#00C957",fg="white", text="Xe Vào", font=label_font, width=20, height=2, command=them_xe_vao)
    btn_vao.pack(side="left", padx=20,pady=20)

    # Label đồng hồ
    global clock_label
    clock_label = tk.Label(frame_button_vao,bg="white", font=label_font)
    clock_label.pack(side="right",padx=20, pady=20)
    update_clock(clock_label)  # Bắt đầu cập nhật đồng hồ
    
    # Label thông tin cổng vào
    global lbl_info_vao
    lbl_info_vao = tk.Label(frame_info_vao, text=info_text_vao, justify="left", wraplength=500, font = info_font)   
    lbl_info_vao.pack(side="left", pady=10, padx=15)
    
    lbl_info_vao2 = tk.Label(frame_label_vao,bg="white", text="Thông tin cổng vào", justify="left", wraplength=300, font=label_font)
    lbl_info_vao2.place(relx = 0.05, rely=0.1)
    # Label "Biển số vào"
    lbl_anh_vao = tk.Label(frame_label_vao,bg="white", text="Biển số vào", justify="left", wraplength=300, font=label_font)
    lbl_anh_vao.place(relx = 0.65, rely=0.1)
    
    # Tạo label để hiển thị ảnh vào
    global image_label_vao
    image_label_vao = tk.Label(frame_anh_vao)
    image_label_vao.pack(fill="both", expand=True)
    
    ################################################################################################
    # Tạo pack cổng ra
    frame_ra = tk.Frame(page_frame,borderwidth=1, relief="solid")
    frame_ra.pack(side="right", fill="both", expand=True)

    # Tạo frame lable ra
    frame_label_ra = tk.Frame(frame_ra,bg="white", borderwidth=0, relief="solid")
    frame_label_ra.place(x=0,rely=0.7, relwidth=1, relheight=0.3)
    # Tạo frame thông tin ra
    frame_thongtin_ra = tk.Frame(frame_ra,bg="white", borderwidth=0, relief="solid")
    frame_thongtin_ra.place(x=0,rely=0.1, relwidth=1, relheight=0.6)
    # Tạo frame button ra
    frame_button_ra = tk.Frame(frame_ra,bg="white", borderwidth=0, relief="solid")
    frame_button_ra.place(x=0,y=0, relwidth= 1, relheight= 0.1)
    #frame info ra
    frame_info_ra = tk.Frame(frame_label_ra, borderwidth=3, relief="raised")
    frame_info_ra.place(relx=0.05, rely= 0.3, relheight=0.65, relwidth=0.55)
    # Tạp frame video ra
    #frame_video_ra = tk.Frame(frame_thongtin_ra,borderwidth=3, relief="raised")
    #frame_video_ra.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)
    # Tạo frame ảnh biển ra
    frame_anh_ra = tk.Frame(frame_label_ra, borderwidth=3, relief="raised")
    frame_anh_ra.place(relx=0.65, rely=0.3,relheight=0.65, relwidth=0.3)
    
    # Button "Xe ra"
    btn_ra = tk.Button(frame_button_ra,bg="#FF3030",fg="white", text="Xe Ra", font=label_font, width=20, height=2, command=xe_ra_bai)
    btn_ra.pack(side="left", padx=20,pady=20)

    btn_end = tk.Button(frame_button_ra,bg="#FF3030",fg="white", text="Đóng kêt nối", font=label_font, width=10, height=2, command=end_both)
    btn_end.pack(side="right", padx=20,pady=20)

#    btn_start = tk.Button(frame_button_ra,bg="#00C957",fg="white", text="Kết nối", font=label_font, width=10, height=2, command=connect_arduino)
    btn_start = tk.Button(frame_button_ra,bg="#00C957",fg="white", text="Kết nối", font=label_font, width=10, height=2, command=connect_both)
    btn_start.pack(side="right", padx=20,pady=20)
     
    # Label thông tin cổng ra
    global lbl_info_ra
    lbl_info_ra = tk.Label(frame_info_ra, text=info_text_ra, justify="left", wraplength=500,font=info_font)
    lbl_info_ra.pack(side="left", pady=10, padx=15)
    
    lbl_info_ra2 = tk.Label(frame_label_ra,bg="white", text="Thông tin cổng ra", justify="left", wraplength=300, font=label_font)
    lbl_info_ra2.place(relx = 0.05, rely=0.1)
    # Tạo label biển số ra
    lbl_anh_ra = tk.Label(frame_label_ra,bg="white", text="Biển số ra", justify="left", wraplength=300, font=label_font)
    lbl_anh_ra.place(relx = 0.65, rely=0.1)

    # Tạo label để hiển thị ảnh ra
    global image_label_ra
    image_label_ra = tk.Label(frame_anh_ra)
    image_label_ra.pack(fill="both", expand=True)
    #################################################################################################
    page_frame.pack(fill=tk.BOTH, expand=True)

    return page_frame

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quản lý bãi đỗ xe")
    root.geometry("800x600")

    create_gui(root)

    root.mainloop()
