# Server
import socket

# Function to handle communication with a connected client
def handle_client(conn, addr):
    while True:
        data = conn.recv(1024)  # Receive up to 1024 bytes from the client
        if not data:  # Break if no more data (client disconnected)
            break
        conn.sendall(data)  # Echo the same data back to the client
    conn.close()


if __name__ == "__main__":
    HOST = "127.0.0.1"  # Localhost (server runs on the same machine)
    PORT = 65432  # Port number (non-privileged, >1024)

    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the host and port
        s.bind((HOST, PORT))
        # Enable server to accept connections
        s.listen()
        print(f"Server listening on {HOST}:{PORT} ...")

        # Main loop: accept new clients
        while True:
            conn, addr = s.accept()  # Accept a client connection
            print("Connected by", addr)
            handle_client(conn, addr)  # Handle communication with this client