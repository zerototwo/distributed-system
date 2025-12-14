# Client
import socket

if __name__ == "__main__":
    HOST = "127.0.0.1"  # Server address (localhost)
    PORT = 65432        # Server port (must match server)

    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server
        s.connect((HOST, PORT))

        # Send a message to the server (as bytes)
        s.sendall(b"Hello, world!")

        # Receive response (up to 1024 bytes)
        data = s.recv(1024)

    # Print the server's reply
    print("Received", repr(data))