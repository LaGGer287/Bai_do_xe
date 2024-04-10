import tkinter as tk
from tkinter import messagebox 
import database
import Qly_baixe
import Qly_bienso
import Thke_xera
import Thke_xevao
import Qly_thexe
import readRFID

def main_function():
    def doSomething():
        print("Đã chọn mục")

    def confirm_exit():
        # Hiện hộp thoại cảnh báo
        result = messagebox.askquestion("Xác nhận", "Bạn có muốn thoát không ?")
        if result == 'yes':
            root.quit()   
        
    frame_created_xeravao = False
    frame_xeravao = None

    frame_created_Qly_bienso = False
    frame_Qly_bienso = None

    frame_created_Qly_baixe = False
    frame_Qly_baixe = None

    frame_created_Thke_xevao = False
    frame_Thke_xevao = None

    frame_created_Thke_xera = False
    frame_Thke_xera = None
    
    frame_created_Qly_thexe = False
    frame_Qly_thexe = None
    
    frame_created_readRFID = False
    frame_readRFID = None

    def show_hethong_xeravao():
        nonlocal frame_created_Qly_bienso, frame_Qly_bienso, frame_created_xeravao, frame_xeravao, frame_created_Qly_baixe, frame_Qly_baixe, frame_created_Thke_xevao, frame_Thke_xevao, frame_created_Thke_xera, frame_Thke_xera, frame_created_Qly_thexe, frame_Qly_thexe, frame_created_readRFID, frame_readRFID
        if not frame_created_xeravao:
            
            frame_xeravao = database.create_gui(root)
            frame_created_xeravao = True
        else:
            frame_xeravao.pack(fill=tk.BOTH, expand=True)
            
        if frame_created_Qly_baixe:
            frame_Qly_baixe.pack_forget()
        if frame_created_Qly_bienso:
            frame_Qly_bienso.pack_forget()
        if frame_created_Thke_xevao:
            frame_Thke_xevao.pack_forget()
        if frame_created_Thke_xera:
            frame_Thke_xera.pack_forget()
        if frame_created_Qly_thexe:
            frame_Qly_thexe.pack_forget()
        if frame_created_readRFID:
            frame_readRFID.pack_forget()

    def show_Qly_bienso():
        nonlocal frame_created_Qly_bienso, frame_Qly_bienso, frame_created_xeravao, frame_xeravao, frame_created_Qly_baixe, frame_Qly_baixe, frame_created_Thke_xevao, frame_Thke_xevao, frame_created_Thke_xera, frame_Thke_xera,frame_created_Qly_thexe, frame_Qly_thexe, frame_created_readRFID, frame_readRFID
        
        if not frame_created_Qly_bienso:
            frame_Qly_bienso = Qly_bienso.createGUI(root)
            frame_created_Qly_bienso = True
        else:
            frame_Qly_bienso.pack(fill=tk.BOTH, expand=True)
            
        if frame_created_xeravao:
            frame_xeravao.pack_forget()
        if frame_created_Qly_baixe:
            frame_Qly_baixe.pack_forget()
        if frame_created_Thke_xevao:
            frame_Thke_xevao.pack_forget()
        if frame_created_Thke_xera:
            frame_Thke_xera.pack_forget()
        if frame_created_Qly_thexe:
            frame_Qly_thexe.pack_forget()
        if frame_created_readRFID:
            frame_readRFID.pack_forget()

    def show_Qly_baixe():
        nonlocal frame_created_Qly_baixe, frame_Qly_baixe, frame_created_xeravao, frame_xeravao, frame_created_Qly_bienso, frame_Qly_bienso, frame_created_Thke_xevao, frame_Thke_xevao, frame_created_Thke_xera, frame_Thke_xera, frame_created_Qly_thexe, frame_Qly_thexe, frame_created_readRFID, frame_readRFID
        
        if not frame_created_Qly_baixe:
            frame_Qly_baixe = Qly_baixe.create_gui(root)
            frame_created_Qly_baixe = True
        else:
            frame_Qly_baixe.pack(fill=tk.BOTH, expand=True)
            
        if frame_created_xeravao:
            frame_xeravao.pack_forget()
        if frame_created_Qly_bienso:
            frame_Qly_bienso.pack_forget()
        if frame_created_Thke_xevao:
            frame_Thke_xevao.pack_forget()
        if frame_created_Thke_xera:
            frame_Thke_xera.pack_forget()
        if frame_created_Qly_thexe:
            frame_Qly_thexe.pack_forget()
        if frame_created_readRFID:
            frame_readRFID.pack_forget()

    def show_Thke_xevao():
        nonlocal frame_created_Qly_baixe, frame_Qly_baixe, frame_created_xeravao, frame_xeravao, frame_created_Qly_bienso, frame_Qly_bienso, frame_created_Thke_xevao, frame_Thke_xevao, frame_created_Thke_xera, frame_Thke_xera, frame_created_Qly_thexe, frame_Qly_thexe, frame_created_readRFID, frame_readRFID
        if not frame_created_Thke_xevao:
            frame_Thke_xevao = Thke_xevao.create_gui(root)
            frame_created_Thke_xevao = True
        else:
            frame_Thke_xevao.pack(fill=tk.BOTH, expand=True)
            
        if frame_created_xeravao:
           frame_xeravao.pack_forget()
        if frame_created_Qly_bienso:
            frame_Qly_bienso.pack_forget()
        if frame_created_Qly_baixe:
            frame_Qly_baixe.pack_forget()
        if frame_created_Thke_xera:
            frame_Thke_xera.pack_forget()
        if frame_created_Qly_thexe:
            frame_Qly_thexe.pack_forget()
        if frame_created_readRFID:
            frame_readRFID.pack_forget()
            
    def show_Thke_xera():
        nonlocal frame_created_Qly_baixe, frame_Qly_baixe, frame_created_xeravao, frame_xeravao, frame_created_Qly_bienso, frame_Qly_bienso, frame_created_Thke_xevao, frame_Thke_xevao, frame_created_Thke_xera, frame_Thke_xera, frame_created_Qly_thexe, frame_Qly_thexe, frame_created_readRFID, frame_readRFID
        if not frame_created_Thke_xera:
            frame_Thke_xera = Thke_xera.create_gui(root)
            frame_created_Thke_xera = True
        else:
            frame_Thke_xera.pack(fill=tk.BOTH, expand=True)
            
        if frame_created_xeravao:
            frame_xeravao.pack_forget()
        if frame_created_Qly_bienso:
            frame_Qly_bienso.pack_forget()
        if frame_created_Qly_baixe:
            frame_Qly_baixe.pack_forget()
        if frame_created_Thke_xevao:
            frame_Thke_xevao.pack_forget()
        if frame_created_Qly_thexe:
            frame_Qly_thexe.pack_forget()
        if frame_created_readRFID:
            frame_readRFID.pack_forget()
            
    def show_Qly_thexe():
        nonlocal frame_created_Qly_baixe, frame_Qly_baixe, frame_created_xeravao, frame_xeravao, frame_created_Qly_bienso, frame_Qly_bienso, frame_created_Thke_xevao, frame_Thke_xevao, frame_created_Thke_xera, frame_Thke_xera, frame_created_Qly_thexe, frame_Qly_thexe, frame_created_readRFID, frame_readRFID
        if not frame_created_Qly_thexe:
            frame_Qly_thexe = Qly_thexe.create_gui(root)
            frame_created_Qly_thexe = True
        else:
            frame_Qly_thexe.pack(fill=tk.BOTH, expand = True)
        
        if frame_created_xeravao:
            frame_xeravao.pack_forget()
        if frame_created_Qly_bienso:
            frame_Qly_bienso.pack_forget()
        if frame_created_Qly_baixe:
            frame_Qly_baixe.pack_forget()
        if frame_created_Thke_xevao:
            frame_Thke_xevao.pack_forget()
        if frame_created_Thke_xera:
            frame_Thke_xera.pack_forget()
        if frame_created_readRFID:
            frame_readRFID.pack_forget()
            
    def show_readRFID():
        nonlocal frame_created_Qly_baixe, frame_Qly_baixe, frame_created_xeravao, frame_xeravao, frame_created_Qly_bienso, frame_Qly_bienso, frame_created_Thke_xevao, frame_Thke_xevao, frame_created_Thke_xera, frame_Thke_xera, frame_created_Qly_thexe, frame_Qly_thexe, frame_created_readRFID, frame_readRFID
        if not frame_created_readRFID:
            frame_readRFID = readRFID.create_gui(root)
            frame_created_readRFID = True
        else:
            frame_readRFID.pack(fill=tk.BOTH, expand = True)
        
        if frame_created_xeravao:
            frame_xeravao.pack_forget()
        if frame_created_Qly_bienso:
            frame_Qly_bienso.pack_forget()
        if frame_created_Qly_baixe:
            frame_Qly_baixe.pack_forget()
        if frame_created_Thke_xevao:
            frame_Thke_xevao.pack_forget()
        if frame_created_Thke_xera:
            frame_Thke_xera.pack_forget()
        if frame_created_Qly_thexe:
            frame_Qly_thexe.pack_forget()            
            
            
    root = tk.Tk()
    root.title("Hệ thống bãi xe thông minh")
    # Tạo một menu chính
    main_menu = tk.Menu(root)
    root.config(menu=main_menu)

    # Tạo các mục trong menu chính
    file_menu = tk.Menu(main_menu, tearoff=False)  # Tearoff để ngăn mục menu bị rời rạc
    main_menu.add_cascade(label="Hệ thống", menu=file_menu)
    file_menu.add_command(label="Cư dân", command=show_hethong_xeravao)
    file_menu.add_command(label="Khách vãng lai", command=show_readRFID)
    file_menu.add_command(label="Thoát", command=confirm_exit)

    edit_menu = tk.Menu(main_menu, tearoff=False)
    main_menu.add_cascade(label="Quản lý", menu=edit_menu)
    edit_menu.add_command(label="Quản lý bãi xe", command=show_Qly_baixe)
    edit_menu.add_command(label="Quản lý biển số", command=show_Qly_bienso)
    edit_menu.add_command(label="Quản lý thẻ xe", command=show_Qly_thexe)

    help_menu = tk.Menu(main_menu, tearoff=False)
    main_menu.add_cascade(label="Thống kê", menu=help_menu)
    help_menu.add_command(label="Thống kê số lượng ra", command=show_Thke_xera)
    help_menu.add_command(label="Thống kê số lượng vào", command=show_Thke_xevao)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.geometry(f"{screen_width}x{screen_height}")  

    # Thêm nhãn "Hệ thống bãi xe thông minh"
    label_system = tk.Label(root, text="HỆ THỐNG BÃI XE THÔNG MINH", font=("Arial", 20, "bold"), bg="#57a1f8",fg='white')
    label_system.pack(fill=tk.X)

    root.mainloop()

# Call the main function when needed
if __name__ == "__main__":
    main_function() 