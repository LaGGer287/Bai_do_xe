import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from tkinter import font
from datetime import datetime, timedelta
import time
import locale
locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
# Kết nối đến cơ sở dữ liệu Python3 trên máy chủ LAGGER\CHIEN
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAGGER\CHIEN;DATABASE=Python4;Trusted_Connection=yes;')
cursor = conn.cursor()

global clock_label
global lbl_so_xe_hom_nay
global lbl_so_xe_may_vao
global lbl_so_xe_oto_vao
day_combo = None
month_combo = None
year_combo = None

def get_total_entries_today():
    # Lấy ngày hiện tại
    today_date = datetime.now().date()

    # Truy vấn cơ sở dữ liệu để lấy tổng số lượt vào hôm nay
    query = f"SELECT COUNT(*) FROM XeVao WHERE CAST(ThoiGianVao AS DATE) = '{today_date}'"
    cursor.execute(query)
    total_entries = cursor.fetchone()[0]

    return total_entries

def get_total_motorbike_entries_today():
    # Lấy ngày hiện tại
    today_date = datetime.now().date()

    # Truy vấn cơ sở dữ liệu để lấy tổng số lượt xe máy vào hôm nay
    query = f"""
        SELECT COUNT(*) 
        FROM XeVao 
        JOIN BienSo ON XeVao.MaBien = BienSo.MaBien
        WHERE CAST(XeVao.ThoiGianVao AS DATE) = '{today_date}' AND BienSo.MaLoai = 'XM'
    """
    cursor.execute(query)
    total_motorbike_entries = cursor.fetchone()[0]

    return total_motorbike_entries

def get_total_car_entries_today():
    # Lấy ngày hiện tại
    today_date = datetime.now().date()

    # Truy vấn cơ sở dữ liệu để lấy tổng số lượt ô tô vào hôm nay
    query = f"""
        SELECT COUNT(*) 
        FROM XeVao 
        JOIN BienSo ON XeVao.MaBien = BienSo.MaBien
        WHERE CAST(XeVao.ThoiGianVao AS DATE) = '{today_date}' AND BienSo.MaLoai = 'OT'
    """
    cursor.execute(query)
    total_car_entries = cursor.fetchone()[0]

    return total_car_entries
# Sau khi đã có các hàm trên, bạn có thể gọi chúng từ các nút hoặc hàm chức năng chính và cập nhật các label:
def update_total_entries_labels():
    total_entries = get_total_entries_today()
    total_motorbike_entries = get_total_motorbike_entries_today()
    total_car_entries = get_total_car_entries_today()

    # Sử dụng biến toàn cục để cập nhật label
    global lbl_so_xe_hom_nay
    lbl_so_xe_hom_nay.config(text=f"Số xe vào hôm nay: {total_entries if total_entries > 0 else 0}")

    global lbl_so_xe_may_vao
    lbl_so_xe_may_vao.config(text=f"Số xe máy vào: {total_motorbike_entries if total_motorbike_entries > 0 else 0}")

    global lbl_so_xe_oto_vao
    lbl_so_xe_oto_vao.config(text=f"Số xe ô tô vào: {total_car_entries if total_car_entries > 0 else 0}")

def update_clock(clock_label):
    current_time = time.strftime('%A, %d %B %Y,  %H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000, update_clock, clock_label)  # Gọi lại hàm update_clock sau 1 giây

def load_recent_entries(tree):
    # Xóa dữ liệu cũ trong treeview
    tree.delete(*tree.get_children())

    # Truy vấn dữ liệu từ bảng XeVao với 10 lượt vào gần nhất
    query = """
    SELECT TOP 10 MaXeVao, ThoiGianVao, SoBien 
    FROM XeVao 
    JOIN BienSo ON XeVao.MaBien = BienSo.MaBien 
    ORDER BY ThoiGianVao DESC
    """
    cursor.execute(query)
    xe_vao_data = cursor.fetchall()

    # Hiển thị dữ liệu từ XeVao trong Treeview
    for idx, row in enumerate(xe_vao_data, start=1):
        ma_xe_vao, thoi_gian_vao, so_bien = row
        thoi_gian_vao = thoi_gian_vao.strftime('%Y-%m-%d %H:%M:%S')
        tree.insert('', 'end', values=(idx, so_bien, thoi_gian_vao, ma_xe_vao))

def load_today_entries(tree):
    # Lấy ngày hiện tại
    today_date = datetime.now().date()

    # Lấy lượt vào của hôm nay
    query = f"SELECT MaXeVao, ThoiGianVao, SoBien FROM XeVao JOIN BienSo ON XeVao.MaBien = BienSo.MaBien WHERE CAST(ThoiGianVao AS DATE) = '{today_date}'"
    cursor.execute(query)
    xe_vao_data = cursor.fetchall()

    # Kiểm tra nếu không có lượt vào nào trong ngày hôm nay
    if not xe_vao_data:
        messagebox.showinfo("Thông báo", "Hôm nay chưa có lượt vào nào.")
        return

    # Hiển thị dữ liệu từ XeVao trong Treeview
    tree.delete(*tree.get_children())
    for idx, row in enumerate(xe_vao_data, start=1):
        ma_xe_vao, thoi_gian_vao, so_bien = row
        thoi_gian_vao = thoi_gian_vao.strftime('%Y-%m-%d %H:%M:%S')
        tree.insert('', 'end', values=(idx, so_bien, thoi_gian_vao, ma_xe_vao))

def load_data(xe_vao_tree):
    # Xóa dữ liệu cũ trong treeview
    for row in xe_vao_tree.get_children():
        xe_vao_tree.delete(row)

    # Truy vấn dữ liệu từ bảng XeVao
    cursor.execute("SELECT MaXeVao, ThoiGianVao, SoBien FROM XeVao JOIN BienSo ON XeVao.MaBien = BienSo.MaBien")
    xe_vao_data = cursor.fetchall()

    # Hiển thị dữ liệu từ XeVao trong Treeview
    for idx, row in enumerate(xe_vao_data, start=1):
        ma_xe_vao, thoi_gian_vao, so_bien = row
        # Định dạng lại thời gian với đến giây
        thoi_gian_vao = thoi_gian_vao.strftime('%Y-%m-%d %H:%M:%S')
        # Thêm dữ liệu vào treeview
        xe_vao_tree.insert('', 'end', values=(idx, so_bien, thoi_gian_vao, ma_xe_vao))  

def search_data(entry_value, checkbox_var_1, checkbox_var_2, tree):
    global day_combo, month_combo, year_combo
    query = "SELECT MaXeVao, ThoiGianVao, SoBien FROM XeVao JOIN BienSo ON XeVao.MaBien = BienSo.MaBien"
    if checkbox_var_1.get():
        so_bien = entry_value.get()
        if so_bien == "":
            messagebox.showwarning("Thông báo", "Vui lòng nhập biển số xe.")
            return
        query += f" WHERE SoBien = '{so_bien}'"

    if checkbox_var_2.get():
        if not checkbox_var_1.get():
            query += " WHERE"
        else:
            query += " AND"

        # Lấy giá trị của combobox ngày, tháng, năm
        day = day_combo.get()
        month = month_combo.get()
        year = year_combo.get()

        # Tạo chuỗi ngày tháng năm
        selected_date = f"'{year}-{month}-{day}'"

        # Thêm điều kiện cho ngày vào truy vấn
        query += f" CAST(ThoiGianVao AS DATE) = {selected_date}"

    cursor.execute(query)
    xe_vao_data = cursor.fetchall()

    # Hiển thị dữ liệu từ XeVao trong Treeview
    tree.delete(*tree.get_children())
    for idx, row in enumerate(xe_vao_data, start=1):
        ma_xe_vao, thoi_gian_vao, so_bien = row
        thoi_gian_vao = thoi_gian_vao.strftime('%Y-%m-%d %H:%M:%S')
        tree.insert('', 'end', values=(idx, so_bien, thoi_gian_vao, ma_xe_vao))


def create_gui(parent):
    page_frame = tk.Frame(parent)
    label_font = font.Font(family="Arial", size=14, weight="bold")
    info_font = font.Font(family="Arial", size = 12,weight="bold")
    clock_font = font.Font(family="Arial", size = 14,weight="bold")
    
    # CHIA KHUNG #####
    # Phần 1: Frame chứa thông tin (frame_info)
    frame_info = tk.Frame(page_frame)
    frame_info.grid(row=0, column=0, sticky="nsew", rowspan=4)

    # Phần 2: Frame chứa chức năng (frame_chucnang)
    frame_chucnang = tk.Frame(page_frame)
    frame_chucnang.grid(row=0, column=1, sticky="nsew", rowspan=4)

    # Thiết lập tỷ lệ kích thước cho cột 1 và cột 2
    page_frame.grid_columnconfigure(0, weight=2)
    page_frame.grid_columnconfigure(1, weight=4)

    # Thiết lập tỷ lệ kích thước cho hàng 1, 2, 3, 4
    for i in range(4):
        page_frame.grid_rowconfigure(i, weight=1)
        
    # Phần 1: Frame chứa thông tin (frame_timkiem)
    frame_timkiem = tk.Frame(frame_info)
    frame_timkiem.grid(row=0, column=0, sticky="nsew", columnspan= 4)

    # Phần 2: Frame chứa danh sách (frame_danhsach)
    frame_danhsach = tk.Frame(frame_info)
    frame_danhsach.grid(row=1, column=0, sticky="nsew", columnspan= 4)
    
    # Thiết lập tỷ lệ kích thước cho dòng 1 và dòng 2
    frame_info.grid_rowconfigure(0, weight=1)
    frame_info.grid_rowconfigure(1, weight=17)
    
    # Thiết lập tỷ lệ kích thước cho hàng 1, 2, 3, 4
    for i in range(4):
        frame_info.grid_columnconfigure(i, weight=1)
    
    # Phần 1: Frame chứa thông tin (frame_timkiem)
    frame_labelthongtin = tk.Frame(frame_chucnang)
    frame_labelthongtin.grid(row=0, column=0, sticky="nsew", columnspan= 4)

    # Phần 2: Frame chứa danh sách (frame_danhsach)
    frame_entry = tk.Frame(frame_chucnang)
    frame_entry.grid(row=1, column=0, sticky="nsew", columnspan= 4)
    
    # Thiết lập tỷ lệ kích thước cho dòng 1 và dòng 2
    frame_chucnang.grid_rowconfigure(0, weight=2)
    frame_chucnang.grid_rowconfigure(1, weight=2)
    
    # Thiết lập tỷ lệ kích thước cho hàng 1, 2, 3, 4
    for i in range(4):
        frame_chucnang.grid_columnconfigure(i, weight=1)    
    ###############
    
    ###CHIA Ô#######
    frame_timkiem1 = tk.Frame(frame_timkiem, bg="white",borderwidth=3, relief="ridge")
    frame_timkiem1.pack(fill="both",expand=True,padx=15,pady=15)

    frame_danhsach1 = tk.Frame(frame_danhsach,borderwidth=3, relief="ridge")
    frame_danhsach1.pack(fill="both",expand=True,padx=15,pady=15)

    frame_labelthongtin1 = tk.Frame(frame_labelthongtin, bg="white",borderwidth=3, relief="ridge")
    frame_labelthongtin1.pack(fill="both",expand=True,padx=15,pady=15)
    frame_labelthongtin1.grid_propagate(False)
    frame_entry1 = tk.Frame(frame_entry, bg="white",borderwidth=3, relief="ridge")
    frame_entry1.pack(fill="both",expand=True,padx=15,pady=15)
    frame_entry1.grid_propagate(False)
    ##################
    
    
    #####TÌM KIẾM##############
    # Phần tìm kiếm
    global day_combo, month_combo, year_combo
    lbl_timkiem = tk.Label(frame_timkiem1, bg="white", text="Tìm kiếm thông tin", font=label_font)
    lbl_timkiem.grid(row=0, column=0, padx=(10, 5), pady=(10, 5))

    entry_timkiem = tk.Entry(frame_timkiem1, font=info_font)
    entry_timkiem.grid(row=0, column=1, padx=5, pady=(10, 5))

    btn_timkiem = tk.Button(frame_timkiem1, text="Tìm kiếm", font=info_font, command=lambda: search_data(entry_timkiem, var_tim_bienso,var_tim_ngay,tree))
    btn_timkiem.grid(row=0, column=2, padx=(5, 10), pady=(10, 5))

    # Checkbox "Tìm theo biển số"
    var_tim_bienso = tk.IntVar()
    check_tim_bienso = tk.Checkbutton(frame_timkiem1, bg="white", text="Tìm theo biển số", variable=var_tim_bienso, font=info_font)
    check_tim_bienso.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5)

    # Checkbox "Tìm theo ngày"
    var_tim_ngay = tk.IntVar()
    check_tim_ngay = tk.Checkbutton(frame_timkiem1, bg="white", text="Tìm theo ngày", variable=var_tim_ngay, font=info_font)
    check_tim_ngay.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5)
    
    # Tạo label cho ngày
    label_day = tk.Label(frame_timkiem1, bg="white", text="Ngày:")
    label_day.grid(row=2, column=3, padx=5, pady=5)
    # Tạo Combobox cho ngày
    days = [str(day) for day in range(1, 32)]
    day_combo = ttk.Combobox(frame_timkiem1, values=days, width=2)
    day_combo.grid(row=2, column=4, padx=5, pady=5)

    # Tạo label cho tháng
    label_month = tk.Label(frame_timkiem1, bg="white", text="Tháng:")
    label_month.grid(row=2, column=5, padx=5, pady=5)
    # Tạo Combobox cho tháng
    months = [str(month) for month in range(1, 13)]
    month_combo = ttk.Combobox(frame_timkiem1, values=months, width=2)
    month_combo.grid(row=2, column=6, padx=5, pady=5)
    
    # Tạo label cho năm
    label_year = tk.Label(frame_timkiem1, bg="white", text="Năm:")
    label_year.grid(row=2, column=7, padx=5, pady=5)
    # Tạo Combobox cho năm
    years = [str(year) for year in range(2024, 2025)]
    year_combo = ttk.Combobox(frame_timkiem1, values=years, width=4)
    year_combo.grid(row=2, column=8, padx=5, pady=5)

    btn_referesh = tk.Button(frame_timkiem1, text="Tải lại", font=info_font, command=lambda: load_data(tree))
    btn_referesh.grid(row=3, column=0, padx=5, pady=5)
    ###########################
    
    ########DANH SÁCH##########
    tree = ttk.Treeview(frame_danhsach1, columns=("STT", "BienSo", "ThoiGianVao"))
    tree.heading("#0", text="", anchor=tk.CENTER)
    tree.heading('STT', text='STT')
    tree.heading('BienSo', text='Biển số xe')
    tree.heading('ThoiGianVao', text='Thời gian vào')
    #tree.heading('MaXeVao', text='Mã xe vào')
    # Đặt font cho tiêu đề cột
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    # Ẩn cột STT thứ hai
    tree.column("#0", width=0, stretch=tk.NO)
    tree.pack(fill="both", expand=True)

    # Load dữ liệu
    load_data(tree)
    ###########################
    
    ########LABEL##############
    # Label đồng hồ
    global clock_label
    clock_label = tk.Label(frame_labelthongtin1, font=label_font, bg="white")
    clock_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
    update_clock(clock_label)  # Bắt đầu cập nhật đồng hồ
    global lbl_so_xe_hom_nay
    global lbl_so_xe_may_vao
    global lbl_so_xe_oto_vao
    # Label "Số xe vào hôm nay"
    lbl_so_xe_hom_nay = tk.Label(frame_labelthongtin1, text="Số xe vào hôm nay: ", font=label_font, bg="white")
    lbl_so_xe_hom_nay.place(relx=0.36, rely=0.25, anchor=tk.CENTER)

    # Label "Số xe máy vào"
    lbl_so_xe_may_vao = tk.Label(frame_labelthongtin1, text="Số xe máy vào: ", font=label_font, bg="white")
    lbl_so_xe_may_vao.place(relx=0.3, rely=0.4, anchor=tk.CENTER)

    # Label "Số xe ô tô vào"
    lbl_so_xe_oto_vao = tk.Label(frame_labelthongtin1, text="Số xe ô tô vào: ", font=label_font, bg="white")
    lbl_so_xe_oto_vao.place(relx=0.3, rely=0.55, anchor=tk.CENTER)
    
    # Cập nhật dữ liệu cho các label
    update_total_entries_labels()
    get_total_car_entries_today()
    get_total_motorbike_entries_today()
    
    ###########################
    
    ########ENTRY##########
    # Button "Hiển thị 10 lượt vào gần nhất"
    btn_recent_entries = tk.Button(frame_entry1, text="Hiển thị 10 lượt vào gần nhất",bg='#57a1f8', fg='white', border=1, font=info_font, command=lambda: load_recent_entries(tree), width=30, height=2)
    btn_recent_entries.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

    # Button "Hiển thị toàn bộ lượt vào hôm nay"
    btn_today_entries = tk.Button(frame_entry1, text="Hiển thị toàn bộ lượt vào hôm nay",bg='#57a1f8', fg='white', border=1, font=info_font, command=lambda: load_today_entries(tree), width=30, height=2)
    btn_today_entries.place(relx=0.5, rely=0.25, anchor=tk.CENTER)

    # Button "Hiển thị toàn bộ thông tin"
    btn_all_entries = tk.Button(frame_entry1, text="Hiển thị toàn bộ thông tin", bg='#57a1f8', fg='white', border=1,font=info_font, command=lambda: load_data(tree), width=30, height=2)
    btn_all_entries.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    # Button "Tải lại"
    btn_refresh = tk.Button(frame_entry1, text="Tải lại",bg='#57a1f8', fg='white', border=1 ,font=info_font, command=lambda: load_data(tree), width=30, height=2)
    btn_refresh.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

    ###########################
    
    
    page_frame.pack(fill=tk.BOTH, expand=True)
    return page_frame
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Thống kê xe vào")
    root.geometry("800x600")

    create_gui(root)

    root.mainloop()