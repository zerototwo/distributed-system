package org.example.grpc;

import io.grpc.stub.StreamObserver;
import java.util.ArrayList;
import java.util.List;
import book.BookOuterClass;
import book.BookServiceGrpc;

/**
 * Book Service Implementation for Cross-Language gRPC Demo
 * Java server that can be accessed by clients in any language
 */
public class BookServiceImpl extends BookServiceGrpc.BookServiceImplBase {
    
    private List<BookOuterClass.Book> books = new ArrayList<>();
    private int nextId = 1;

    public BookServiceImpl() {
        // Initialize with sample books
        books.add(BookOuterClass.Book.newBuilder()
                .setId(1)
                .setTitle("1984")
                .setAuthor("George Orwell")
                .build());
        books.add(BookOuterClass.Book.newBuilder()
                .setId(2)
                .setTitle("To Kill a Mockingbird")
                .setAuthor("Harper Lee")
                .build());
        books.add(BookOuterClass.Book.newBuilder()
                .setId(3)
                .setTitle("The Great Gatsby")
                .setAuthor("F. Scott Fitzgerald")
                .build());
        nextId = 4;
    }

    @Override
    public void getBook(BookOuterClass.BookRequest request, StreamObserver<BookOuterClass.BookResponse> responseObserver) {
        int bookId = request.getId();
        
        for (BookOuterClass.Book book : books) {
            if (book.getId() == bookId) {
                BookOuterClass.BookResponse response = BookOuterClass.BookResponse.newBuilder()
                        .setBook(book)
                        .build();
                responseObserver.onNext(response);
                responseObserver.onCompleted();
                return;
            }
        }
        
        responseObserver.onError(new Throwable("Book not found with id: " + bookId));
    }

    @Override
    public void listBooks(BookOuterClass.Empty request, StreamObserver<BookOuterClass.BookListResponse> responseObserver) {
        BookOuterClass.BookListResponse response = BookOuterClass.BookListResponse.newBuilder()
                .addAllBooks(books)
                .build();
        
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void addBook(BookOuterClass.NewBookRequest request, StreamObserver<BookOuterClass.BookResponse> responseObserver) {
        BookOuterClass.Book newBook = BookOuterClass.Book.newBuilder()
                .setId(nextId)
                .setTitle(request.getTitle())
                .setAuthor(request.getAuthor())
                .build();
        
        books.add(newBook);
        nextId++;

        BookOuterClass.BookResponse response = BookOuterClass.BookResponse.newBuilder()
                .setBook(newBook)
                .build();
        
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}
