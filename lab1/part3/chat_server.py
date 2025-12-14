import socket
import threading

clients = []   # 存放所有客户端连接
lock = threading.Lock()

def broadcast(message, sender_conn):
    """向所有客户端广播消息（除了发送者）"""
    with lock:
        for client in clients:
            conn, addr = client
            if conn != sender_conn:  # 不发回给自己
                try:
                    conn.sendall(message)
                except:
                    conn.close()
                    clients.remove(client)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    with lock:
        clients.append((conn, addr))
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = f"[{addr}] {data.decode()}"
            print(msg)
            broadcast(msg.encode(), conn)
    except ConnectionResetError:
        print(f"[ERROR] Connection with {addr} lost.")
    finally:
        with lock:
            clients.remove((conn, addr))
        conn.close()
        print(f"[DISCONNECTED] {addr} closed connection.")


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5555  # 群聊端口（PDF里指定的）

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[CHAT SERVER] Listening on {HOST}:{PORT} ...")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")