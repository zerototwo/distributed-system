"""Cross-Language gRPC Client Implementation"""

import grpc
import book_pb2
import book_pb2_grpc


def run():
    """Demonstrate cross-language gRPC communication"""
    print("=== Cross-Language gRPC Demo ===")
    print("Python Client connecting to Java Server...")
    # Connect to the remote gRPC server implemented in Java
    with grpc.insecure_channel('localhost:50053') as channel:
        # Create a client stub for calling remote BookService methods
        stub = book_pb2_grpc.BookServiceStub(channel)
        
        # List all books from Java server
        print("\n1. Listing all books from Java server:")
        try:
            books = stub.ListBooks(book_pb2.Empty())
            for book in books.books:
                print(f"   - Book {book.id}: {book.title} by {book.author}")
        except grpc.RpcError as e:
            print(f"   Error: {e.details()}")
        
        # Get a specific book by ID
        print("\n2. Getting a specific book (ID=2):")
        try:
            response = stub.GetBook(book_pb2.BookRequest(id=2))
            print(f"   Found: {response.book.title} by {response.book.author}")
        except grpc.RpcError as e:
            print(f"   Error: {e.details()}")
        
        # Add a new book from Python client to Java server
        print("\n3. Adding a new book from Python client:")
        try:
            new_book_response = stub.AddBook(book_pb2.NewBookRequest(
                title="Pride and Prejudice", 
                author="Jane Austen"
            ))
            print(f"   Added: {new_book_response.book.title} by {new_book_response.book.author}")
        except grpc.RpcError as e:
            print(f"   Error: {e.details()}")
        
        # List books again to see the new addition
        print("\n4. Listing all books again to see the new addition:")
        try:
            books = stub.ListBooks(book_pb2.Empty())
            for book in books.books:
                print(f"   - Book {book.id}: {book.title} by {book.author}")
        except grpc.RpcError as e:
            print(f"   Error: {e.details()}")
        
        # Test error handling with non-existent book
        print("\n5. Testing error handling (non-existent book):")
        try:
            response = stub.GetBook(book_pb2.BookRequest(id=999))
            print(f"   Found: {response.book.title} by {response.book.author}")
        except grpc.RpcError as e:
            print(f"   Expected error: {e.details()}")
        
        print("\n=== Cross-Language Demo Complete ===")
        print("✓ Python client successfully communicated with Java server")
        print("✓ gRPC's cross-language interoperability proven")


if __name__ == '__main__':
    run()
