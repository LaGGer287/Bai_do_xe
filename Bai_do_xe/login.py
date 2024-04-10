import tkinter as tk
from tkinter import *
import pyodbc
from tkinter import messagebox
import subprocess
import mainGUI
import picture

def on_enter_username(event):
    user.delete(0, 'end')

def on_leave_username(event):
    if user.get() == "":
        user.insert(0, 'Tài khoản')

def on_enter_password(event):
    password.delete(0, 'end')

def on_leave_password(event):
    if password.get() == "":
        password.insert(0, 'Mật khẩu')

def login():
    # Lấy thông tin từ các ô nhập liệu
    username = user.get()
    password_text = password.get()

    # Kết nối đến cơ sở dữ liệu SQL Server
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAGGER\CHIEN;DATABASE=Python4;Trusted_Connection=yes;')

    # Tạo đối tượng Cursor
    cursor = conn.cursor()

    try:
        # Thực hiện truy vấn kiểm tra tài khoản và mật khẩu
        cursor.execute("SELECT * FROM Account WHERE taikhoan = ? AND matkhau = ?", (username, password_text))
        row = cursor.fetchone()

        if row:
            print("Đăng nhập thành công!")
            # Trả về True nếu đăng nhập thành công
            # Đóng cửa sổ hiện tại của login.py
            root.destroy()
            # Mở file main.py sau khi đăng nhập thành công
            picture.display_image("image1.png")
            mainGUI.main_function()
        else:
            print("Tên đăng nhập hoặc mật khẩu không đúng!")
            messagebox.showerror("Lỗi", "Bạn đã nhập sai tài khoản hoặc mật khẩu!")
            # Trả về False nếu đăng nhập không thành công
            return False
    except Exception as e:
        print("Lỗi khi thực hiện truy vấn:", e)
        return False
    finally:
        # Đóng kết nối sau khi hoàn thành công việc
        cursor.close()
        conn.close()

root = tk.Tk()
root.title("Đăng nhập")
root.resizable(False, False)
root.configure(bg="#fff")
root.geometry("925x500+250+200")

img = PhotoImage(file="logo.png")
Label(root, image=img, bg='white').place(x=50, y=50)

frame = Frame(root, width=350, height=350, bg="white")
frame.place(x=500, y=70)

heading = Label(frame, text="Đăng nhập", fg="#57a1f8", bg="white", font=('Microsoft YeHei UI Light', 23, 'bold'))
heading.place(x=100, y=5)

user = Entry(frame, width=25, fg='black', border=0, bg="white", font=('Microsoft YeHei UI Light', 11))
user.place(x=30, y=80)
user.insert(0, "Tài khoản")
user.bind('<FocusIn>', on_enter_username)
user.bind('<FocusOut>', on_leave_username)
Frame(frame, width=295, height=2, bg='black').place(x=25, y=107)

password = Entry(frame, width=25, fg='black', border=0, bg="white", font=('Microsoft YeHei UI Light', 11),show="*")
password.place(x=30, y=150)
password.insert(0, "Mật khẩu")
password.bind('<FocusIn>', on_enter_password)
password.bind('<FocusOut>', on_leave_password)
Frame(frame, width=295, height=2, bg='black').place(x=25, y=177)

Button(frame, width=39 ,pady=7, text="Đăng nhập", bg='#57a1f8', fg='white', border=0, command=login).place(x=35, y=204)

root.mainloop()
