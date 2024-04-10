import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

def kiem_tra_bai_xe(tree):
    try:
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAGGER\CHIEN;DATABASE=Python4;Trusted_Connection=yes;')
        cursor = conn.cursor()

        cursor.execute("SELECT BienSo.SoBien, CONVERT(VARCHAR(19), XeVao.ThoiGianVao, 120) AS ThoiGianVao, CuDan.TenCuDan, CuDan.DiaChi, LoaiXe.TenLoai FROM BienSo JOIN XeVao ON BienSo.MaBien = XeVao.MaBien LEFT JOIN CuDan ON BienSo.MaBien = CuDan.MaBien LEFT JOIN LoaiXe ON BienSo.MaLoai = LoaiXe.MaLoai WHERE BienSo.TrangThai = 1 AND XeVao.ThoiGianVao = (SELECT MAX(ThoiGianVao) FROM XeVao WHERE XeVao.MaBien = BienSo.MaBien)")
        rows = cursor.fetchall()

        # Xóa dữ liệu cũ trong Treeview (nếu có)
        for row in tree.get_children():
            tree.delete(row)

        if rows:
            print("Trong bãi xe có các xe sau:")
            for i, row in enumerate(rows, start=1):
                so_bien = row[0]
                thoi_gian_vao = row[1]
                ten_cu_dan = row[2]
                dia_chi = row[3]
                ten_loai = row[4]

                info_text_check = f"Biển số: {so_bien}, Thời gian vào: {thoi_gian_vao}, Tên chủ xe: {ten_cu_dan}, Địa chỉ: {dia_chi}, Loại xe: {ten_loai}\n"
                print(info_text_check)

                # Thêm dữ liệu mới từ CSDL vào Treeview
                tree.insert("", "end", values=(i, so_bien, thoi_gian_vao, ten_cu_dan, dia_chi, ten_loai))
        else:
            messagebox.showinfo("Thông báo", "Hiện không có xe nào trong bãi!")
            info_text_check = "Hiện không có xe nào trong bãi xe."
            print(info_text_check)

    except Exception as e:
        print('Đã xảy ra lỗi:', e)
        info_text_check = "Đã xảy ra lỗi: " + str(e)

    #lbl_info_check.config(text=info_text_check)

def create_gui(parent):
    # Tạo một Frame mới trong parent
    page_frame = tk.Frame(parent)
    button_font = ("Arial", 12, "bold")
    # Tạo một Frame để chứa tất cả các thành phần khác
    content_frame = tk.Frame(page_frame)
    content_frame.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.95, anchor=tk.CENTER)
    #Label "Danh sách các xe đang ở trong bãi"
    
    lbl_info_check = tk.Label(content_frame, text="DANH SÁCH CÁC XE ĐANG Ở TRONG BÃI", font=("Arial", 15, "bold"))
    lbl_info_check.pack(side="top",pady=(15))  # Thêm khoảng cách từ trên xuống dưới
    # Tạo Treeview
    tree = ttk.Treeview(content_frame, columns=("STT", "SoBien", "ThoiGianVao", "TenCuDan", "DiaChi", "TenLoai"))

    # Đặt tên cho các cột
    tree.heading("#0", text="", anchor=tk.CENTER)
    tree.heading("STT", text="STT")
    tree.heading("SoBien", text="Biển số")
    tree.heading("ThoiGianVao", text="Thời gian vào")
    tree.heading("TenCuDan", text="Tên chủ xe")
    tree.heading("DiaChi", text="Địa chỉ")
    tree.heading("TenLoai", text="Loại xe")

    # Đặt font cho tiêu đề cột
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

    # Ẩn cột "#0"
    tree.column("#0", width=0, stretch=tk.NO)

    # Button để fetch dữ liệu từ CSDL và hiển thị trong Treeview
    fetch_button = tk.Button(content_frame, text="Tải lại", command=lambda: kiem_tra_bai_xe(tree),font=button_font)
    fetch_button.pack(side="bottom", pady=10)

    # Hiển thị Treeview
    tree.pack(expand=True, fill="both")

    # Không cần gọi root.mainloop() ở đây
    # Pack page_frame vào parent
    page_frame.pack(fill=tk.BOTH, expand=True)

    # Trả về page_frame
    return page_frame


# Sử dụng hàm create_gui để tạo GUI từ một tập tin khác
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quản lý bãi đỗ xe")
    root.geometry("800x600")

    create_gui(root)

    root.mainloop()
