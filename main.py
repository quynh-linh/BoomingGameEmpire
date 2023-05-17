import tkinter as tk
from PIL import ImageTk, Image
import subprocess

server_process = None  # Biến lưu trữ quá trình chạy server

def run_client():
    subprocess.Popen(["python", "client.py"])

def run_server():
    global server_process
    server_process = subprocess.Popen(["python", "server.py"])

def stop_server():
    global server_process
    if server_process:
        server_process.terminate()
        server_process = None

# Khởi tạo cửa sổ chương trình
window = tk.Tk()
window.title("BOOMBERMAN")

# Đặt ảnh nền
background_image = ImageTk.PhotoImage(Image.open("background.jpg").resize((640, 360)))
background_label = tk.Label(window, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Lấy kích thước màn hình
screen_width = 640
screen_height = 360

# Tạo label cho tiêu đề
title_label = tk.Label(window, text="BOOMBERMAN", font=("Arial", 36, "bold"), fg="#FFD700")
title_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

# Tạo button Client
client_button = tk.Button(window, text="Client", width=20, command=run_client, font=("Arial", 18), fg="#FFD700")
client_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

# Tạo button Server
server_button = tk.Button(window, text="Server", width=20, command=run_server, font=("Arial", 18), fg="#FFD700")
server_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Tạo button Stop Server
stop_server_button = tk.Button(window, text="Stop Server", width=20, command=stop_server, font=("Arial", 18), fg="#FFD700")
stop_server_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

# Đặt kích thước và vị trí cửa sổ chương trình
window.geometry(f"{screen_width}x{screen_height}")

# Chạy chương trình
window.mainloop()
