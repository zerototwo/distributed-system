import socket
import threading

# Function to handle communication with a connected client
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True:
            data = conn.recv(1024)  # Receive up to 1024 bytes
            if not data:
                break
            print(f"[RECEIVED from {addr}] {data.decode()}")
            conn.sendall(data)  # Echo back to client
    except ConnectionResetError:
        print(f"[ERROR] Connection with {addr} lost.")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr} closed connection.")


if __name__ == "__main__":
    HOST = "127.0.0.1"  # Localhost
    PORT = 65432        # Port number

    # 创建tcp socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT} ...")

        while True:
            conn, addr = s.accept()  # 接收 new client
            # 创建线程来出client
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")