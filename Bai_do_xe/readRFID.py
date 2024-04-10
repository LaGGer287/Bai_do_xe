import serial
import pyodbc
import cv2
import threading
import tkinter as tk
from tkinter import font, messagebox
import io
from PIL import Image, ImageTk
import datetime

# Thiết lập kết nối với cơ sở dữ liệu
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAGGER\CHIEN;DATABASE=Python4;Trusted_Connection=yes;')
cursor = conn.cursor()
# Khai báo biến global image_label
image_label = None
parent = None  # Định nghĩa biến parent ở global
# Thiết lập cổng Serial
#arduino_port_in = 'COM5'  # Cổng Serial của RFID vào
#arduino_port_out = 'COM5'  # Cổng Serial của RFID ra
#baud_rate = 9600

global ser3
# Kết nối với Arduino RFID vào
#arduino_in = serial.Serial(arduino_port_in, baud_rate, timeout=1)


def connect_arduino(port='COM5', baudrate=9600, timeout=1):
    global ser3
    try:
        ser3 = serial.Serial(port, baudrate, timeout=timeout)
        messagebox.showinfo("Thông báo", f"Đã kết nối tới Arduino trên cổng {port}")
        print("Đã kết nối tới Arduino trên cổng", port)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kết nối tới Arduino: {e}")
        print("Đã xảy ra lỗi khi kết nối tới Arduino:", e)

def connect_both():
    connect_arduino()
    connect_arduino2()
    
def end_both():
    end_connect()
    end_connect2()

def end_connect():
    global ser3
    try:
        ser3.close()
        print("Đã ngắt kết nối tới Arduino")
        messagebox.showinfo("Thông báo", f"Đã đóng kết nối tới Arduino")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi đóng kết nối tới Arduino: {e}")
        print("Đã xảy ra lỗi khi ngắt kết nối tới Arduino:", e)

def connect_arduino2(port='COM6', baudrate=9600, timeout=1):
    global ser4
    try:
        ser4 = serial.Serial(port, baudrate, timeout=timeout)
        messagebox.showinfo("Thông báo", f"Đã kết nối tới Arduino trên cổng {port}")
        print("Đã kết nối tới Arduino trên cổng", port)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kết nối tới Arduino: {e}")
        print("Đã xảy ra lỗi khi kết nối tới Arduino:", e)

def end_connect2():
    global ser4
    try:
        ser4.close()
        print("Đã ngắt kết nối tới Arduino")
        messagebox.showinfo("Thông báo", f"Đã đóng kết nối tới Arduino")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi đóng kết nối tới Arduino: {e}")
        print("Đã xảy ra lỗi khi ngắt kết nối tới Arduino:", e)

# Kết nối với Arduino RFID ra (nếu cần)
#arduino_out = serial.Serial(arduino_port_out, baud_rate, timeout=1)

# Biến lưu thông tin cho chức năng xe vào bãi
global info_text_vao
info_text_vao = ""

# Biến lưu thông tin cho chức năng xe ra bãi
global info_text_ra
info_text_ra = ""

# Hàm xóa hình ảnh
def clear_image():
    # Xóa nội dung của image_label
    image_label.config(image="")
    # Lập lịch để xóa nội dung của image_label sau 6 giây
    parent.after(6000, clear_image, parent)

# Hàm chụp ảnh từ webcam và lưu vào trường image của thẻ
def capture_image(card_id):
    camera = cv2.VideoCapture(0)
    return_value, image = camera.read()
    camera.release()

    # Lưu ảnh vào thư mục hoặc cơ sở dữ liệu, tùy vào cách bạn lựa chọn
    # Ở đây chúng ta giả sử bạn lưu vào cơ sở dữ liệu với giá trị kiểu IMAGE
    ret, buf = cv2.imencode('.jpg', image)
    image_bytes = buf.tobytes()

    # Cập nhật ảnh vào cơ sở dữ liệu
    cursor.execute("UPDATE CARD_DATA SET image = ? WHERE card_id = ?", (image_bytes, card_id))
    conn.commit()

# Hàm xử lý khi thẻ vào
def process_entry(card_id):
    global info_text_vao
    try:
        cursor.execute("SELECT status FROM CARD_DATA WHERE card_id = ?", (card_id,))
        status = cursor.fetchone()

        if status and status[0] == 0:
            # Thực hiện các hành động khi thẻ vào
            cursor.execute("UPDATE CARD_DATA SET status = 1 WHERE card_id = ?", (card_id,))
            capture_image(card_id)  # Chụp ảnh và lưu vào trường image của thẻ            
            # Thêm dữ liệu vào bảng Entry
            entry_time = datetime.datetime.now()
            cursor.execute("INSERT INTO Entry (card_id, entry_time) VALUES (?, ?)", (card_id, entry_time))
            info_text_vao = f"Mã thẻ: {card_id}\n\nThời gian vào: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}"
            # Cập nhật thông tin trên các label trong frame_info_vao
            lbl_info_vao.config(text=info_text_vao)
            lbl_info_vao.after(7000, clear_info_label_vao)
        else:
            print("Thẻ không hợp lệ hoặc đã được sử dụng.")
            info_text_vao = "Thẻ không hợp lệ hoặc đã được sử dụng."
            lbl_info_vao.config(text=info_text_vao)  # Cập nhật nội dung của label
            lbl_info_vao.after(7000, clear_info_label_vao)
        conn.commit()
    except Exception as e:
        print("Lỗi khi thao tác với cơ sở dữ liệu:", e)
        info_text_vao = "Đã xảy ra lỗi: " + str(e)
        lbl_info_vao.config(text=info_text_vao)  # Cập nhật nội dung của label
        lbl_info_vao.after(7000, clear_info_label_vao)
        conn.rollback()  # Rollback thay đổi nếu có lỗi

def clear_info_label_vao():
    global info_text_vao
    info_text_vao = ""
    lbl_info_vao.config(text="")
    

# Hàm xử lý khi thẻ ra
def process_exit(card_id):
    global info_text_ra
    global image_label  # Sử dụng biến global image_label
    try:
        cursor.execute("SELECT status, image FROM CARD_DATA WHERE card_id = ?", (card_id,))
        result = cursor.fetchone()

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
#                parent.after(6000, clear_image)

            cursor.execute("UPDATE CARD_DATA SET status = 0, image = NULL WHERE card_id = ?", (card_id,))
            
            # Thêm dữ liệu vào bảng Out
            exit_time = datetime.datetime.now()
            cursor.execute("INSERT INTO Out (card_id, exit_time) VALUES (?, ?)", (card_id, exit_time))

            cursor.execute("SELECT entry_time FROM Entry WHERE card_id = ?", (card_id,))
            entry_time = cursor.fetchone()[0]
            
            info_text_ra = f"Mã thẻ: {card_id}\n\nThời gian vào: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}\nThời gian ra: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}"
            lbl_info_ra.config(text=info_text_ra)
            lbl_info_ra.after(7000, clear_info_label_ra)
        else:
            print("Thẻ không hợp lệ hoặc chưa được sử dụng.")
            info_text_ra = "Thẻ không hợp lệ hoặc chưa được sử dụng."
            lbl_info_ra.config(text=info_text_ra)
            lbl_info_ra.after(7000, clear_info_label_ra)
        conn.commit()
    except Exception as e:
        print("Lỗi khi thao tác với cơ sở dữ liệu:", e)
        info_text_ra = "Đã xảy ra lỗi: " + str(e)
        lbl_info_ra.config(text=info_text_ra)
        lbl_info_ra.after(7000, clear_info_label_ra)
        conn.rollback()  # Rollback thay đổi nếu có lỗi

def clear_info_label_ra():
    global info_text_ra
    info_text_ra = ""
    lbl_info_ra.config(text="")

# Hàm đọc RFID và xử lý thẻ vào
def read_rfid_in():
    global ser3
    if ser3 is None or not ser3.is_open:
        print("Chưa kết nối tới Arduino. Không thể đọc RFID.")
        return
    
    while True:
        rfid_data = ser3.readline().decode().strip()

        if rfid_data.startswith("RFID Detected! Card UID:"):
            card_id = rfid_data.split(":")[1].strip().replace(" ", "")
            process_entry(card_id)
            print(card_id)

# Hàm đọc RFID và xử lý thẻ ra (nếu cần)
def read_rfid_out():
    global ser4
    if ser4 is None or not ser4.is_open:
        print("Chưa kết nối tới Arduino. Không thể đọc RFID.")
        return
    
    while True:
        rfid_data = ser4.readline().decode().strip()

        if rfid_data.startswith("RFID Detected! Card UID:"):
            card_id = rfid_data.split(":")[1].strip().replace(" ", "")
            process_exit(card_id)
            print(card_id)

# Hàm main
def main():
    try:
        # Khởi tạo và chạy các luồng đọc RFID
        thread_in = threading.Thread(target=read_rfid_in)
        thread_in.start()

        # Nếu cần, khởi tạo và chạy luồng đọc RFID ra
        thread_out = threading.Thread(target=read_rfid_out)
        thread_out.start()
        
        #Chờ cho các luồng hoàn thành
        #thread_in.join()
        #thread_out.join()
        
    except KeyboardInterrupt:
        # Ngắt khi nhận phím tắt từ người dùng
        print("Đã dừng bởi người dùng.")

    # Đóng kết nối cơ sở dữ liệu khi kết thúc chương trình
'''
def exit_program(thread_in):
    try:
        # Đóng kết nối cơ sở dữ liệu
        #cursor.close()
        #conn.close()

        # Dừng tất cả các tiến trình hoạt động, ví dụ:
        thread_in.join()
        thread_out.join()
        
        # Đóng cổng Serial
        # arduino_in.close()
        #arduino_out.close()

    except Exception as e:
        print("Lỗi khi thoát chương trình:", e)
'''
def create_gui(parent):
    page_frame = tk.Frame(parent)
    label_font = font.Font(family="Arial", size=20, weight='bold')
    info_font = font.Font(family="Arial", size = 15, weight='bold')
    
    
    ##############################################################################################
    # Tạo pack cổng vào
    frame_vao = tk.Frame(page_frame,borderwidth=1, relief="solid")
    frame_vao.pack(side="left", fill="both", expand=True)

    # Tạo frame lable vao
    frame_label_vao = tk.Frame(frame_vao, bg="white",borderwidth=0, relief="solid")
    frame_label_vao.place(x=0,rely=0.7, relwidth=1, relheight=0.3)    
    # Tạo frame thông tin vao
    frame_thongtin_vao = tk.Frame(frame_vao, bg="white", borderwidth=0, relief="solid")
    frame_thongtin_vao.place(x=0,rely=0.1, relwidth=1, relheight=0.6)
    # Tạo frame button vao
    frame_button_vao = tk.Frame(frame_vao, bg="white", borderwidth=0, relief="solid")
    frame_button_vao.place(x=0,y=0, relwidth= 1, relheight= 0.1)
    #frame info vao
    frame_info_vao = tk.Frame(frame_label_vao,bg="white", borderwidth=1, relief="solid")
    frame_info_vao.place(relx=0.05, rely= 0.3, relheight=0.65, relwidth=0.9)
    # Tạo frame anh vao 
    frame_anh_vao = tk.Frame(frame_thongtin_vao,borderwidth=0,bg="grey", relief="raised")
    frame_anh_vao.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)
    
    # Label thông tin mã thẻ và thời gian vào cho frame_info_vao
    global lbl_info_vao
    lbl_info_vao = tk.Label(frame_info_vao, bg="white", text="", justify="left", wraplength=800, font=info_font)
    lbl_info_vao.place(relx=0.05, rely=0.3)
        
    # Label Cổng vào
    button_start = tk.Button(frame_button_vao,text="Bắt đầu", bg="#00C957", fg="white",command=main, width=10, height=2, font=info_font)
    button_start.pack(side="right",padx=10,pady=10)
    
    button_connect = tk.Button(frame_button_vao,text="Kết nối", bg="#00C957", fg="white", command=connect_both, width=10, height=2, font=info_font)
    button_connect.pack(side="right",padx=10,pady=10)
    
    lbl_congvao = tk.Label(frame_button_vao, bg="white", fg="#00C957",text="CỔNG VÀO", justify="left", wraplength=300, font=label_font)
    lbl_congvao.pack(side="left", padx=20,pady=20)
   
    # Label thông tin cổng vào
    lbl_info_vao2 = tk.Label(frame_label_vao, bg="white", text="Thông tin cổng vào", justify="left", wraplength=300, font=label_font)
    lbl_info_vao2.place(relx = 0.05, rely=0.1)
    
    ################################################################################################
    # Tạo pack cổng ra
    frame_ra = tk.Frame(page_frame,borderwidth=1, relief="solid")
    frame_ra.pack(side="right", fill="both", expand=True)

    # Tạo frame lable ra
    frame_label_ra = tk.Frame(frame_ra, bg="white", borderwidth=0, relief="solid")
    frame_label_ra.place(x=0,rely=0.7, relwidth=1, relheight=0.3)
    # Tạo frame thông tin ra
    frame_thongtin_ra = tk.Frame(frame_ra, bg="white", borderwidth=0, relief="solid")
    frame_thongtin_ra.place(x=0,rely=0.1, relwidth=1, relheight=0.6)
    # Tạo frame button ra
    frame_button_ra = tk.Frame(frame_ra, bg="white", borderwidth=0, relief="solid")
    frame_button_ra.place(x=0,y=0, relwidth= 1, relheight= 0.1)
    #frame info ra
    frame_info_ra = tk.Frame(frame_label_ra, bg="white",borderwidth=1, relief="solid")
    frame_info_ra.place(relx=0.05, rely= 0.3, relheight=0.65, relwidth=0.9)
    # Tạo frame anh ra
    frame_anh_ra = tk.Frame(frame_thongtin_ra,borderwidth=0,bg="grey", relief="raised")
    frame_anh_ra.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)
    global image_label  # Sử dụng biến global image_label
    image_label = tk.Label(frame_anh_ra)
    image_label.pack(fill=tk.BOTH, expand=True)
    
    
    # Label thông tin mã thẻ, thời gian vào và thời gian ra cho frame_info_ra
    global lbl_info_ra  
    lbl_info_ra = tk.Label(frame_info_ra, bg="white", text="", justify="left", wraplength=800, font=info_font)
    lbl_info_ra.place(relx=0.05, rely=0.3)
    
    button_stop = tk.Button(frame_button_ra,text="Đóng kết nối", bg="#FF3030", fg="white", command=end_both, width=10, height=2, font=info_font)
    button_stop.pack(side="right",padx=10,pady=10)
        
    # Label Cổng ra
    lbl_congvao = tk.Label(frame_button_ra, bg="white", fg="#FF3030",text="CỔNG RA", justify="left", wraplength=300, font=label_font)
    lbl_congvao.pack(side="left", padx=20,pady=20)

    # Label thông tin cổng ra
    lbl_info_ra2 = tk.Label(frame_label_ra, bg="white", text="Thông tin cổng ra", justify="left", wraplength=300, font=label_font)
    lbl_info_ra2.place(relx = 0.05, rely=0.1)
    #################################################################################################
    page_frame.pack(fill=tk.BOTH, expand=True)
    return page_frame
    

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quản lý bãi đỗ xe")
    root.geometry("800x600")

    create_gui(root)

    root.mainloop()

