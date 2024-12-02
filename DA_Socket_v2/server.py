import threading
import os
import socket
HOST = "127.0.0.1" 
SERVER_PORT = 65432 
FORMAT = "utf8"
SIZE = 1024
from tqdm import tqdm

### D:\MMT\DA_Socket_v2\server_file la file mac dinh cua server
def handleClient(conn, addr):
    print("conn:",conn.getsockname())
    
    conn.close()
def recv_file_from_client(conn , addr):
    #lay thong tin ten file va file size cua client
    fileInfo = conn.recv(SIZE).decode(FORMAT)
    fileInfo = fileInfo.rsplit("|",1)
    #fileInfo =  {FILENAME}|{FILESIZE}
    newFile = str(fileInfo[0])
    fileSize  = int(fileInfo[1])
    print(newFile)
    newFile = r"D:\MMT\DA_Socket_v2\server_file"+ "\\" + newFile
    conn.send(f"Success recv {newFile}".encode(FORMAT))

    """transfer file"""
    bar  = tqdm(range(fileSize), f"RECV in {newFile}", unit = "B", unit_scale = True, unit_divisor = fileSize)
    ofile = open(newFile, "wb")
    if  ofile.closed :
        print("cannot open")
    while True:
        data = conn.recv(SIZE)
        if not data : 
                break
        ofile.write(data)
            #send tb nhan thanh cong
        conn.send("data received".encode(FORMAT))
        bar.update(len(data))
    ofile.close()

### yc 2
def send_file_to_client(conn):
    # fileName = r"D:\MMT\DA_Socket_v2\client_file\friends-final.txt"
    #TODO make send file name in here
    fileName  = conn.recv(SIZE).decode(FORMAT)
    path = os.getcwd()
    fileServer = path +"\\server_file" + "\\" + fileName
    # fileServer  = "D:\MMT\DA_Socket_v2\server_file\file1.txt"
    print(f"file server {fileServer}")
    #send file size
    fileSize = -1
    if os.path.isfile(fileServer) == True :

        fileSize = os.path.getsize(fileServer)
        # print(fileSize)
        conn.send(fileSize.encode(FORMAT))
    else:
        print("file not valid")
        conn.send("-1".encode(FORMAT))
        return
    """Data transfer"""
    # bar = tqdm(range(fileSize), f"Sending {fileServer}", unit="B", unit_scale=True, unit_divisor=SIZE)
    # nhan thong bao thanh cong
    print(conn.recv(SIZE).decode(FORMAT))
    #TODO lam 1 cai input file
    ifile = open(fileServer, "rb")
    while True:
        data = ifile.read(SIZE)
        if not data:
            break
        conn.send(data)
        msg = conn.recv(SIZE).decode(FORMAT)
        # cap nhat bar
        # bar.update(len(data))
    print(msg)
    ifile.close()
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    s.bind((HOST, SERVER_PORT))
    s.listen()

    print("SERVER SIDE")
    print("server:", HOST, SERVER_PORT)
    print("Waiting for Client")

    while (True):
        try:
            conn, addr = s.accept()
            #gui tb thanh conng
            #gui response cua client
            conn.send("Succeed connect".encode(FORMAT))
            #lang nghe yeu cau cua client
            request = conn.recv(SIZE).decode(FORMAT)
            print(request)
            # thr = threading.Thread(target=handleClient, args=(conn,addr))
            if(request == "UPLD"):
                 thr = threading.Thread(target= recv_file_from_client, args=(conn,addr))
                 thr.start()
            elif (request == "DOWNLD"):
                # thr = threading.Thread(target = send_file_to_client, agrs =(conn, addr))
                # thr.start()
                send_file_to_client(conn)

        except:
            print("Error")
            break
    print("End")
    conn.close()
    s.close()
if __name__ == "__main__":
    main()