import socket
import threading

def receive_messages(sock):
    """接收服务器广播的消息"""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode())
        except:
            print("[ERROR] Connection lost.")
            sock.close()
            break

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5555

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to chat server.")

        # 启动接收线程
        threading.Thread(target=receive_messages, args=(s,), daemon=True).start()

        # 主循环：输入并发送消息
        while True:
            msg = input()
            if msg.lower() == "quit":
                break
            s.sendall(msg.encode())