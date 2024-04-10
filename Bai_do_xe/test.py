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
import cv2
import io

ser = serial.Serial('COM5', 9600, timeout=1)
#ser2 = serial.Serial('COM6', 9600, timeout=1)
# Thiết lập ngôn ngữ mặc định là tiếng Việt
locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')

# Kết nối đến cơ sở dữ liệu Python3 trên máy chủ LAGGER\CHIEN
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAGGER\CHIEN;DATABASE=Python4;Trusted_Connection=yes;')
cursor = conn.cursor()
conn2 = pyodbc.connect('DRIVER={SQL Server};SERVER=LAGGER\CHIEN;DATABASE=RFID1;Trusted_Connection=yes;')
cursor2 = conn2.cursor()
# Biến lưu thông tin cho chức năng xe vào bãi
global info_text_vao
info_text_vao = ""

# Biến lưu thông tin cho chức năng xe ra bãi
global info_text_ra
info_text_ra = ""

# Label đồng hồ
global clock_label
global image_label_vao
global image_label_ra
image_label = None

def send_command_to_arduino():
    try:
        # Gửi lệnh "0" tới Arduino
        ser.write(b'1')
        print("Đã gửi lệnh mở cổng ra bãi.")
    except Exception as e:
        print("Đã xảy ra lỗi khi gửi lệnh tới Arduino:", e)
        
def capture_image(card_id):
    camera = cv2.VideoCapture(0)
    return_value, image = camera.read()
    camera.release()

    # Lưu ảnh vào thư mục hoặc cơ sở dữ liệu, tùy vào cách bạn lựa chọn
    # Ở đây chúng ta giả sử bạn lưu vào cơ sở dữ liệu với giá trị kiểu IMAGE
    ret, buf = cv2.imencode('.jpg', image)
    image_bytes = buf.tobytes()

    # Cập nhật ảnh vào cơ sở dữ liệu
    cursor2.execute("UPDATE CARD_DATA SET image = ? WHERE card_id = ?", (image_bytes, card_id))
    conn2.commit()
    
# Hàm xử lý khi thẻ vào
def process_entry(card_id):
    global info_text_vao
    try:
        cursor2.execute("SELECT status FROM CARD_DATA WHERE card_id = ?", (card_id,))
        status = cursor2.fetchone()

        if status and status[0] == 0:
            # Thực hiện các hành động khi thẻ vào
            cursor2.execute("UPDATE CARD_DATA SET status = 1 WHERE card_id = ?", (card_id,))
            capture_image(card_id)  # Chụp ảnh và lưu vào trường image của thẻ            
            # Thêm dữ liệu vào bảng Entry
            #entry_time = datetime.datetime.now()
            cursor2.execute("INSERT INTO Entry (card_id, entry_time) VALUES (?, CURRENT_TIMESTAMP)", (card_id,))
            info_text_vao = f"Mã thẻ: {card_id}\nThời gian vào: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            # Cập nhật thông tin trên các label trong frame_info_vao
            lbl_info_vao.config(text=info_text_vao)
            lbl_info_vao.after(7000, clear_info_label_vao)
        else:
            print("Thẻ không hợp lệ hoặc đã được sử dụng.")
            info_text_vao = "Thẻ không hợp lệ hoặc đã được sử dụng."
            lbl_info_vao.config(text=info_text_vao)  # Cập nhật nội dung của label
            lbl_info_vao.after(7000, clear_info_label_vao)
        conn2.commit()
    except Exception as e:
        print("Lỗi khi thao tác với cơ sở dữ liệu:", e)
        info_text_vao = "Đã xảy ra lỗi: " + str(e)
        lbl_info_vao.config(text=info_text_vao)  # Cập nhật nội dung của label
        lbl_info_vao.after(7000, clear_info_label_vao)
        conn2.rollback()  # Rollback thay đổi nếu có lỗi   

# Hàm đọc RFID và xử lý thẻ vào
def read_rfid_in():
    while True:
        rfid_data = ser.readline().decode().strip()

        if rfid_data.startswith("RFID Detected! Card UID:"):
            card_id = rfid_data.split(":")[1].strip().replace(" ", "")
            process_entry(card_id)
            print(card_id)
'''
# Hàm xử lý khi thẻ ra
def process_exit(card_id):
    global info_text_ra
    global image_label  # Sử dụng biến global image_label
    try:
        cursor2.execute("SELECT status, image FROM CARD_DATA WHERE card_id = ?", (card_id,))
        result = cursor2.fetchone()

        if result and result[0] == 1:
            # Thực hiện các hành động khi thẻ ra
            image_bytes = result[1]
            if image_bytes:
                # Chuyển đổi dữ liệu ảnh từ bytes sang định dạng hình ảnh phù hợp cho tkinter
                image_pil = Image.open(io.BytesIO(image_bytes))
                image_tk = ImageTk.PhotoImage(image_pil)
                
                # Cập nhật Label với ảnh mới
                image_label.configure(image=image_tk)
                image_label.image = image_tk  # Đảm bảo giữ tham chiếu đến ảnh để tránh bị giải phóng bộ nhớ

            cursor2.execute("UPDATE CARD_DATA SET status = 0, image = NULL WHERE card_id = ?", (card_id,))
            
            # Thêm dữ liệu vào bảng Out
            exit_time = datetime.datetime.now()
            cursor2.execute("INSERT INTO Out (card_id, exit_time) VALUES (?, ?)", (card_id, exit_time))

            cursor2.execute("SELECT entry_time FROM Entry WHERE card_id = ?", (card_id,))
            entry_time = cursor.fetchone()[0]
            
            info_text_ra = f"Mã thẻ: {card_id}\n\nThời gian vào: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}\nThời gian ra: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}"
            lbl_info_ra.config(text=info_text_ra)
            lbl_info_ra.after(7000, clear_info_label_ra)
        else:
            print("Thẻ không hợp lệ hoặc chưa được sử dụng.")
            info_text_ra = "Thẻ không hợp lệ hoặc chưa được sử dụng."
            lbl_info_ra.config(text=info_text_ra)
            lbl_info_ra.after(7000, clear_info_label_ra)
        conn2.commit()
    except Exception as e:
        print("Lỗi khi thao tác với cơ sở dữ liệu:", e)
        info_text_ra = "Đã xảy ra lỗi: " + str(e)
        lbl_info_ra.config(text=info_text_ra)
        lbl_info_ra.after(7000, clear_info_label_ra)
        conn.rollback()  # Rollback thay đổi nếu có lỗi

# Hàm đọc RFID và xử lý thẻ ra (nếu cần)
def read_rfid_out():
    while True:
        rfid_data = ser2.readline().decode().strip()

        if rfid_data.startswith("RFID Detected! Card UID:"):
            card_id = rfid_data.split(":")[1].strip().replace(" ", "")
            process_exit(card_id)


def send_command_to_arduino2():
    try:
        # Gửi lệnh "0" tới Arduino
        ser2.write(b'1')
        print("Đã gửi lệnh mở cổng ra bãi.")
    except Exception as e:
        print("Đã xảy ra lỗi khi gửi lệnh tới Arduino:", e)
'''
def update_clock(clock_label):
    current_time = time.strftime('%A, %d %B %Y,  %H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000, update_clock, clock_label)  # Gọi lại hàm update_clock sau 1 giây

def them_xe_vao():
    threading.Thread(target=process_license_plate_and_update_label_vao).start()

def xe_ra_bai():
    threading.Thread(target=process_license_plate_and_update_label_ra).start()

def update_image(image_label_vao):
    try:
        # Đọc ảnh từ file crop.jpg
        image = Image.open("crop.jpg")
        # Chuyển đổi ảnh sang định dạng phù hợp để hiển thị trên GUI
        image = ImageTk.PhotoImage(image)
        # Cập nhật ảnh trên label
        image_label_vao.configure(image=image)
        # Giữ tham chiếu đến ảnh để không bị hủy bởi garbage collector
        image_label_vao.image = image
        # Thiết lập hàm gọi lại sau 7 giây để xóa ảnh
        image_label_vao.after(7000, lambda: clear_image(image_label_vao))
    except FileNotFoundError:
        # Xử lý nếu không tìm thấy file crop.jpg
        print("Không tìm thấy file crop.jpg")

def clear_image(image_label_vao):
    # Xóa ảnh trên label
    image_label_vao.configure(image=None)

def update_image_ra(image_label_ra):
    try:
        # Đọc ảnh từ file crop.jpg
        image = Image.open("crop.jpg")
        # Chuyển đổi ảnh sang định dạng phù hợp để hiển thị trên GUI
        image = ImageTk.PhotoImage(image)
        # Cập nhật ảnh trên label
        image_label_ra.configure(image=image)
        # Giữ tham chiếu đến ảnh để không bị hủy bởi garbage collector
        image_label_ra.image = image
        # Thiết lập hàm gọi lại sau 7 giây để xóa ảnh
        image_label_ra.after(7000, lambda: clear_image(image_label_ra))
    except FileNotFoundError:
        # Xử lý nếu không tìm thấy file crop.jpg
        print("Không tìm thấy file crop.jpg")

def clear_image_ra(image_label_ra):
    # Xóa ảnh trên label
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
#                    send_command_to_arduino2()
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

# Hàm main
def main():
    try:
        # Khởi tạo và chạy các luồng đọc RFID
        thread_in = threading.Thread(target=read_rfid_in)
        thread_in.start()


        # Nếu cần, khởi tạo và chạy luồng đọc RFID ra
#        thread_out = threading.Thread(target=read_rfid_out)
#        thread_out.start()
        

        #Chờ cho các luồng hoàn thành
#        thread_in.join()
#        thread_out.join()
        
    except KeyboardInterrupt:
        # Ngắt khi nhận phím tắt từ người dùng
        print("Đã dừng bởi người dùng.")

    # Đóng kết nối cơ sở dữ liệu khi kết thúc chương trình
    
def exit_program():
    try:
        # Đóng kết nối cơ sở dữ liệu
        cursor2.close()
        conn2.close()

        # Dừng tất cả các tiến trình hoạt động, ví dụ:
        # thread_in.join()
        # thread_out.join()
        
        # Đóng cổng Serial
        # arduino_in.close()
        ser.close()

    except Exception as e:
        print("Lỗi khi thoát chương trình:", e)    

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
    
    button_start = tk.Button(frame_button_vao,text="Bắt đầu", command=main)
    button_start.pack(side="left",padx=10,pady=10)
    
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
    frame_anh_ra = tk.Frame(frame_label_ra, borderwidth=3, bg="white",relief="raised")
    frame_anh_ra.place(relx=0.65, rely=0.3,relheight=0.65, relwidth=0.3)
    
    # Button "Xe ra"
    btn_ra = tk.Button(frame_button_ra,bg="#FF3030",fg="white", text="Xe Ra", font=label_font, width=20, height=2, command=xe_ra_bai)
    btn_ra.pack(side="left", padx=20,pady=20)

    # Label thông tin cổng ra
    global lbl_info_ra
    lbl_info_ra = tk.Label(frame_info_ra, text=info_text_ra, justify="left", wraplength=500,font=info_font)
    lbl_info_ra.pack(side="left", pady=10, padx=15)
    
    lbl_info_ra2 = tk.Label(frame_label_ra,bg="white", text="Thông tin cổng ra", justify="left", wraplength=300, font=label_font)
    lbl_info_ra2.place(relx = 0.05, rely=0.1)
    # Tạo label biển số ra
    lbl_anh_ra = tk.Label(frame_label_ra,bg="white", text="Biển số ra", justify="left", wraplength=300, font=label_font)
    lbl_anh_ra.place(relx = 0.65, rely=0.1)

    button_stop = tk.Button(frame_button_ra,text="Kết thúc", command=exit_program)
    button_stop.pack(side="left",padx=10,pady=10)
    # Tạo label để hiển thị ảnh ra
    global image_label_ra
    image_label_ra = tk.Label(frame_anh_ra)
    image_label_ra.pack(fill="both", expand=True)
    
    # Tạo frame anh ra
    frame_anh_ra2 = tk.Frame(frame_thongtin_ra,borderwidth=0,bg="white", relief="raised")
    frame_anh_ra2.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)
    
    global image_label  # Sử dụng biến global image_label
    image_label = tk.Label(frame_anh_ra2, bg = "white")
    image_label.pack(fill=tk.BOTH, expand=True)
    #################################################################################################
    page_frame.pack(fill=tk.BOTH, expand=True)

    return page_frame

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quản lý bãi đỗ xe")
    root.geometry("800x600")

    create_gui(root)

    root.mainloop()
