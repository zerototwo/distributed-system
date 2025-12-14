import socket

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 65432  # 与 multi_server.py

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to server. Type 'quit' to exit.")

        while True:
            # input mesaage
            msg = input("You: ")
            if msg.lower() == "quit":
                print("Closing connection...")
                break

            # send message
            s.sendall(msg.encode())

            # wait message
            data = s.recv(1024)
            if not data:
                print("Server closed the connection.")
                break

            print("Server:", data.decode())