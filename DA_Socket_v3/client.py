import socket
import os
import struct
import tkinter as tk
from tkinter import messagebox, filedialog
import threading  # Import threading module


# Khởi tạo kết nối tới server
TCP_IP = "127.0.0.1"
TCP_PORT = 8080
BUFFER_SIZE = 1024
FORMAT ="utf-8"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Hàm kết nối đến server
def conn():
    try:
        s.connect((TCP_IP, TCP_PORT))
        messagebox.showinfo("Success", "Connected to the server.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect: {e}")

# Hàm tải lên file
def upld():
    #TODO lam 1 ham check loi
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            s.sendall(b"UPLD")
            s.recv(BUFFER_SIZE)
            #send file_size name
            s.sendall(struct.pack("h", len(file_name)))
            s.recv(BUFFER_SIZE)
            # send file_name
            s.sendall(file_name.encode())
            s.recv(BUFFER_SIZE)
            #gui kich thuoc file
            s.sendall(struct.pack("i", file_size))
            s.recv(BUFFER_SIZE)
            # van chuyen du lieu
            with open(file_path, "rb") as f:
                # while (chunk := f.read(BUFFER_SIZE)):
                #     s.sendall(chunk)
                #     s.recv(BUFFER_SIZE)
                data = f.read(BUFFER_SIZE)
                while True:
                    s.sendall(data)
                    data = f.read(BUFFER_SIZE)
                    if not data :
                        break
            #nhan thong bao cho server da ket thuc viec upld
            s.recv(BUFFER_SIZE)

            #nhan thong bao nhan du file cua client
            msg = s.recv(BUFFER_SIZE).decode(FORMAT)
            if(msg == "FULL"):
                messagebox.showinfo("Success", f"File {file_name} uploaded successfully.")
            else:
                messagebox.showinfo("Failure", f"File {file_name} uploaded unsuccessfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error during file upload: {e}")
            s.send(b"ERROR")
def upld_folder():
    dir_path = filedialog.askdirectory(title="Select a Directory")
    

# Hàm liệt kê tệp
def list_files():
    try:
        s.sendall(b"LIST")
        number_of_files = struct.unpack("!i", s.recv(4))[0]
        print(number_of_files)
        file_list.delete(1.0, tk.END)  # Xóa danh sách cũ
        for _ in range(number_of_files):
            file_name_size = struct.unpack("i", s.recv(4))[0]

            s.send("ok".encode(FORMAT))

            file_name = s.recv(file_name_size).decode()

            s.send("ok".encode(FORMAT))
            file_size = struct.unpack("i", s.recv(4))[0]
            file_list.insert(tk.END, f"{file_name} - {file_size} bytes\n")
            s.sendall(b"1")
        total_directory_size = struct.unpack("i", s.recv(4))[0]
        file_list.insert(tk.END, f"Total directory size: {total_directory_size} bytes\n")
        s.sendall(b"1")
    except Exception as e:
        messagebox.showerror("Error", f"Error listing files: {e}")

# Hàm tải xuống file tu server ve client
def dwld():
    file_name = str(file_name_entry.get())
    print(file_name)
      # Lấy tên file từ giao diện người dùng
    if file_name:
        try:
            # Gửi yêu cầu tải xuống tệp
            s.sendall(b"DWLD")
            s.recv(BUFFER_SIZE)  # Nhận tín hiệu đồng bộ từ server
            # s.sendall(struct.pack("h", len(file_name)))  # Gửi độ dài tên file
            s.send(file_name.encode(FORMAT))  # Gửi tên file

            #TODO
            
            # Nhận kích thước file từ server interpret 4 byte dau tien
            buf = b''
            while len(buf) < 4:
                buf += s.recv(4 - len(buf))
            file_size = struct.unpack('!i', buf)[0]

            if file_size == -1:
                messagebox.showerror("Error", f"File {file_name} not found.")
                return
            #gui tb nhan ten file
            s.send("ok".encode(FORMAT))
            # Tạo file mới để ghi dữ liệu đã tải về
            
            print(file_size)
            #nhan file
            bytes_received = 0
            with open(f"downloaded_{file_name}", "wb") as f:
                print("Downloading...")
                while bytes_received < file_size:
                    data = s.recv(BUFFER_SIZE)  # Nhận dữ liệu
                    if not data or data == b"ERROR":
                        break
                    f.write(data)  # Ghi dữ liệu vào file
                    bytes_received += len(data)
            if bytes_received == file_size:
                messagebox.showinfo("Success", f"File {file_name} downloaded successfully.")
                s.send(f"Download {file_name} successful ".encode(FORMAT))
            else:
                s.send(b"ERROR")
        except Exception as e:
            messagebox.showerror("Error", f"Error downloading file: {e}")

# Hàm xóa file
def delf():
    file_name = file_name_entry.get()
    if file_name:
        try:
            s.sendall(b"DELF")
            s.recv(BUFFER_SIZE)
            s.sendall(struct.pack("h", len(file_name)))
            s.sendall(file_name.encode())

            file_exists = struct.unpack("i", s.recv(4))[0]
            if file_exists == -1:
                messagebox.showerror("Error", f"File {file_name} not found.")
                return

            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {file_name}?")
            if confirm:
                s.sendall(b"Y")
                delete_status = struct.unpack("i", s.recv(4))[0]
                if delete_status == 1:
                    messagebox.showinfo("Success", f"File {file_name} deleted successfully.")
                else:
                    messagebox.showerror("Error", "Error deleting the file.")
            else:
                s.sendall(b"N")
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting file: {e}")

# Hàm thoát kết nối
def quit_app():
    try:
        s.sendall(b"QUIT")
        s.recv(BUFFER_SIZE)
        s.close()
        messagebox.showinfo("Disconnected", "Disconnected from the server.")
        root.quit()
    except Exception as e:
        messagebox.showerror("Error", f"Error during disconnection: {e}")

# Hàm chạy trong một thread riêng biệt cho các thao tác như tải lên, tải xuống
def run_task_in_thread(task_function):
    # task_thread = threading.Thread(target=task_function)
    # task_thread.start()
    task_function()

########
USER_CREDENTIALS = {
    "admin": "1",
    "user1": "1"
}
# Khởi tạo giao diện người dùng
def handle_login():
    username = username_entry.get()
    password = password_entry.get()

    # Check if the username and password are correct
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        messagebox.showinfo("Login Successful", "Welcome to FTP Client!")
        login_window.destroy()  # Close login window
        create_main_window()  # Open main FTP client window
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Function to create main window (FTP Client Interface)
def create_main_window():
    global file_list,file_name_entry,root  # Declare file_list as global here
    
    root = tk.Tk()
    root.title("FTP Client")

    connect_btn = tk.Button(root, text="Connect to Server", command=conn)
    connect_btn.pack(pady=10)

    upload_btn = tk.Button(root, text="Upload File", command=lambda: run_task_in_thread(upld))
    upload_btn.pack(pady=5)

    list_btn = tk.Button(root, text="List Files", command=lambda: run_task_in_thread(list_files))
    list_btn.pack(pady=5)

    download_btn = tk.Button(root, text="Download File", command=lambda: run_task_in_thread(dwld))
    download_btn.pack(pady=5)

    delete_btn = tk.Button(root, text="Delete File", command=lambda: run_task_in_thread(delf))
    delete_btn.pack(pady=5)

    quit_btn = tk.Button(root, text="Quit", command=quit_app)
    quit_btn.pack(pady=10)

    # Entry cho tên file
    file_name_label = tk.Label(root, text="File Name:")
    file_name_label.pack(pady=5)
    file_name_entry = tk.Entry(root)
    file_name_entry.pack(pady=5)

    # Textbox hiển thị danh sách tệp
    file_list_label = tk.Label(root, text="Files on Server:")
    file_list_label.pack(pady=5)
    file_list = tk.Text(root, height=10, width=50)
    file_list.pack(pady=5)

    root.mainloop()

# Function to quit the application
def quit_app():
    root.quit()

def handle_signup():
    username = signup_username_entry.get()
    password = signup_password_entry.get()
    
    if username in USER_CREDENTIALS:
        messagebox.showerror("Sign Up Failed", "Username already exists.")
    else:
        USER_CREDENTIALS[username] = password
        messagebox.showinfo("Sign Up Successful", "Account created successfully!")
        signup_window.destroy()
        login_window.deiconify()

def open_signup_window():
    login_window.withdraw()
    global signup_window, signup_username_entry, signup_password_entry

    signup_window = tk.Tk()
    signup_window.title("Sign Up")

    signup_username_label = tk.Label(signup_window, text="Username:")
    signup_username_label.pack(pady=5)
    signup_username_entry = tk.Entry(signup_window)
    signup_username_entry.pack(pady=5)

    signup_password_label = tk.Label(signup_window, text="Password:")
    signup_password_label.pack(pady=5)
    signup_password_entry = tk.Entry(signup_window, show="*")
    signup_password_entry.pack(pady=5)

    signup_btn = tk.Button(signup_window, text="Sign Up", command=handle_signup)
    signup_btn.pack(pady=10)

    signup_window.mainloop()

def create_login_window():
    global login_window, username_entry, password_entry

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("500x200")
    login_window.resizable(width=False, height=False)

    username_label = tk.Label(login_window, text="Username:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    login_btn = tk.Button(login_window, text="Login", command=handle_login)
    login_btn.pack(pady=5)

    signup_btn = tk.Button(login_window, text="Sign Up", command=open_signup_window)
    signup_btn.pack(pady=5)

    login_window.mainloop()

# Start the application with login window
create_login_window()
