"""Book Service gRPC Server Implementation"""

from concurrent import futures
import grpc
import book_pb2
import book_pb2_grpc


class BookService(book_pb2_grpc.BookServiceServicer):
    """Book Service implementation for gRPC requests"""
    
    def __init__(self):
        # Initialize with sample books
        self.books = [
            book_pb2.Book(id=1, title="1984", author="George Orwell"),
            book_pb2.Book(id=2, title="To Kill a Mockingbird", author="Harper Lee"),
        ]
        self.next_id = 3

    def GetBook(self, request, context):
        """Get a book by ID"""
        for book in self.books:
            if book.id == request.id:
                return book_pb2.BookResponse(book=book)
        
        # Book not found
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Book not found')
        return book_pb2.BookResponse()

    def ListBooks(self, request, context):
        """List all books"""
        return book_pb2.BookListResponse(books=self.books)

    def AddBook(self, request, context):
        """Add a new book"""
        new_book = book_pb2.Book(
            id=self.next_id, 
            title=request.title, 
            author=request.author
        )
        self.books.append(new_book)
        self.next_id += 1
        return book_pb2.BookResponse(book=new_book)


def serve():
      # Create a gRPC server with a thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
      # Register our BookService implementation to the gRPC server
    book_pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
      # Listen for incoming connections on port 50051
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
