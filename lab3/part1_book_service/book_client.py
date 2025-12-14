"""Book Service gRPC Client Implementation"""

import grpc
import book_pb2
import book_pb2_grpc


def run():
    """Demonstrate Book Service operations"""
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = book_pb2_grpc.BookServiceStub(channel)
        
        print("=== Book Service Client Demo ===")
        
        # Get a book by ID
        print("\n1. Getting book with ID=1:")
        try:
            response = stub.GetBook(book_pb2.BookRequest(id=1))
            print(f"   Found: {response.book.title} by {response.book.author}")
        except grpc.RpcError as e:
            print(f"   Error: {e.details()}")
        
        # List all books
        print("\n2. Listing all books:")
        books = stub.ListBooks(book_pb2.Empty())
        for i, book in enumerate(books.books, 1):
            print(f"   {i}. {book.title} by {book.author}")
        
        # Add a new book
        print("\n3. Adding a new book:")
        new_book_response = stub.AddBook(book_pb2.NewBookRequest(
            title="Brave New World", 
            author="Aldous Huxley"
        ))
        print(f"   Added: {new_book_response.book.title} by {new_book_response.book.author}")
        
        # List books again
        print("\n4. Listing all books after addition:")
        books = stub.ListBooks(book_pb2.Empty())
        for i, book in enumerate(books.books, 1):
            print(f"   {i}. {book.title} by {book.author}")
        
        print("\n=== Demo Complete ===")


if __name__ == '__main__':
    run()
