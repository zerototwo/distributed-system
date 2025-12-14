package book;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 * Book service definition
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.56.0)",
    comments = "Source: book.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class BookServiceGrpc {

  private BookServiceGrpc() {}

  public static final String SERVICE_NAME = "book.BookService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<book.BookOuterClass.BookRequest,
      book.BookOuterClass.BookResponse> getGetBookMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetBook",
      requestType = book.BookOuterClass.BookRequest.class,
      responseType = book.BookOuterClass.BookResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<book.BookOuterClass.BookRequest,
      book.BookOuterClass.BookResponse> getGetBookMethod() {
    io.grpc.MethodDescriptor<book.BookOuterClass.BookRequest, book.BookOuterClass.BookResponse> getGetBookMethod;
    if ((getGetBookMethod = BookServiceGrpc.getGetBookMethod) == null) {
      synchronized (BookServiceGrpc.class) {
        if ((getGetBookMethod = BookServiceGrpc.getGetBookMethod) == null) {
          BookServiceGrpc.getGetBookMethod = getGetBookMethod =
              io.grpc.MethodDescriptor.<book.BookOuterClass.BookRequest, book.BookOuterClass.BookResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "GetBook"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  book.BookOuterClass.BookRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  book.BookOuterClass.BookResponse.getDefaultInstance()))
              .setSchemaDescriptor(new BookServiceMethodDescriptorSupplier("GetBook"))
              .build();
        }
      }
    }
    return getGetBookMethod;
  }

  private static volatile io.grpc.MethodDescriptor<book.BookOuterClass.Empty,
      book.BookOuterClass.BookListResponse> getListBooksMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ListBooks",
      requestType = book.BookOuterClass.Empty.class,
      responseType = book.BookOuterClass.BookListResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<book.BookOuterClass.Empty,
      book.BookOuterClass.BookListResponse> getListBooksMethod() {
    io.grpc.MethodDescriptor<book.BookOuterClass.Empty, book.BookOuterClass.BookListResponse> getListBooksMethod;
    if ((getListBooksMethod = BookServiceGrpc.getListBooksMethod) == null) {
      synchronized (BookServiceGrpc.class) {
        if ((getListBooksMethod = BookServiceGrpc.getListBooksMethod) == null) {
          BookServiceGrpc.getListBooksMethod = getListBooksMethod =
              io.grpc.MethodDescriptor.<book.BookOuterClass.Empty, book.BookOuterClass.BookListResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ListBooks"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  book.BookOuterClass.Empty.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  book.BookOuterClass.BookListResponse.getDefaultInstance()))
              .setSchemaDescriptor(new BookServiceMethodDescriptorSupplier("ListBooks"))
              .build();
        }
      }
    }
    return getListBooksMethod;
  }

  private static volatile io.grpc.MethodDescriptor<book.BookOuterClass.NewBookRequest,
      book.BookOuterClass.BookResponse> getAddBookMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "AddBook",
      requestType = book.BookOuterClass.NewBookRequest.class,
      responseType = book.BookOuterClass.BookResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<book.BookOuterClass.NewBookRequest,
      book.BookOuterClass.BookResponse> getAddBookMethod() {
    io.grpc.MethodDescriptor<book.BookOuterClass.NewBookRequest, book.BookOuterClass.BookResponse> getAddBookMethod;
    if ((getAddBookMethod = BookServiceGrpc.getAddBookMethod) == null) {
      synchronized (BookServiceGrpc.class) {
        if ((getAddBookMethod = BookServiceGrpc.getAddBookMethod) == null) {
          BookServiceGrpc.getAddBookMethod = getAddBookMethod =
              io.grpc.MethodDescriptor.<book.BookOuterClass.NewBookRequest, book.BookOuterClass.BookResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "AddBook"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  book.BookOuterClass.NewBookRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  book.BookOuterClass.BookResponse.getDefaultInstance()))
              .setSchemaDescriptor(new BookServiceMethodDescriptorSupplier("AddBook"))
              .build();
        }
      }
    }
    return getAddBookMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static BookServiceStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<BookServiceStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<BookServiceStub>() {
        @java.lang.Override
        public BookServiceStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new BookServiceStub(channel, callOptions);
        }
      };
    return BookServiceStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static BookServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<BookServiceBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<BookServiceBlockingStub>() {
        @java.lang.Override
        public BookServiceBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new BookServiceBlockingStub(channel, callOptions);
        }
      };
    return BookServiceBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static BookServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<BookServiceFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<BookServiceFutureStub>() {
        @java.lang.Override
        public BookServiceFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new BookServiceFutureStub(channel, callOptions);
        }
      };
    return BookServiceFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * Book service definition
   * </pre>
   */
  public interface AsyncService {

    /**
     * <pre>
     * Get a single book by ID
     * </pre>
     */
    default void getBook(book.BookOuterClass.BookRequest request,
        io.grpc.stub.StreamObserver<book.BookOuterClass.BookResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getGetBookMethod(), responseObserver);
    }

    /**
     * <pre>
     * List all books
     * </pre>
     */
    default void listBooks(book.BookOuterClass.Empty request,
        io.grpc.stub.StreamObserver<book.BookOuterClass.BookListResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getListBooksMethod(), responseObserver);
    }

    /**
     * <pre>
     * Add a new book
     * </pre>
     */
    default void addBook(book.BookOuterClass.NewBookRequest request,
        io.grpc.stub.StreamObserver<book.BookOuterClass.BookResponse> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getAddBookMethod(), responseObserver);
    }
  }

  /**
   * Base class for the server implementation of the service BookService.
   * <pre>
   * Book service definition
   * </pre>
   */
  public static abstract class BookServiceImplBase
      implements io.grpc.BindableService, AsyncService {

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return BookServiceGrpc.bindService(this);
    }
  }

  /**
   * A stub to allow clients to do asynchronous rpc calls to service BookService.
   * <pre>
   * Book service definition
   * </pre>
   */
  public static final class BookServiceStub
      extends io.grpc.stub.AbstractAsyncStub<BookServiceStub> {
    private BookServiceStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected BookServiceStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new BookServiceStub(channel, callOptions);
    }

    /**
     * <pre>
     * Get a single book by ID
     * </pre>
     */
    public void getBook(book.BookOuterClass.BookRequest request,
        io.grpc.stub.StreamObserver<book.BookOuterClass.BookResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getGetBookMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * List all books
     * </pre>
     */
    public void listBooks(book.BookOuterClass.Empty request,
        io.grpc.stub.StreamObserver<book.BookOuterClass.BookListResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getListBooksMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     * <pre>
     * Add a new book
     * </pre>
     */
    public void addBook(book.BookOuterClass.NewBookRequest request,
        io.grpc.stub.StreamObserver<book.BookOuterClass.BookResponse> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getAddBookMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * A stub to allow clients to do synchronous rpc calls to service BookService.
   * <pre>
   * Book service definition
   * </pre>
   */
  public static final class BookServiceBlockingStub
      extends io.grpc.stub.AbstractBlockingStub<BookServiceBlockingStub> {
    private BookServiceBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected BookServiceBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new BookServiceBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * Get a single book by ID
     * </pre>
     */
    public book.BookOuterClass.BookResponse getBook(book.BookOuterClass.BookRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getGetBookMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * List all books
     * </pre>
     */
    public book.BookOuterClass.BookListResponse listBooks(book.BookOuterClass.Empty request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getListBooksMethod(), getCallOptions(), request);
    }

    /**
     * <pre>
     * Add a new book
     * </pre>
     */
    public book.BookOuterClass.BookResponse addBook(book.BookOuterClass.NewBookRequest request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getAddBookMethod(), getCallOptions(), request);
    }
  }

  /**
   * A stub to allow clients to do ListenableFuture-style rpc calls to service BookService.
   * <pre>
   * Book service definition
   * </pre>
   */
  public static final class BookServiceFutureStub
      extends io.grpc.stub.AbstractFutureStub<BookServiceFutureStub> {
    private BookServiceFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected BookServiceFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new BookServiceFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     * Get a single book by ID
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<book.BookOuterClass.BookResponse> getBook(
        book.BookOuterClass.BookRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getGetBookMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * List all books
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<book.BookOuterClass.BookListResponse> listBooks(
        book.BookOuterClass.Empty request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getListBooksMethod(), getCallOptions()), request);
    }

    /**
     * <pre>
     * Add a new book
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<book.BookOuterClass.BookResponse> addBook(
        book.BookOuterClass.NewBookRequest request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getAddBookMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_GET_BOOK = 0;
  private static final int METHODID_LIST_BOOKS = 1;
  private static final int METHODID_ADD_BOOK = 2;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final AsyncService serviceImpl;
    private final int methodId;

    MethodHandlers(AsyncService serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_GET_BOOK:
          serviceImpl.getBook((book.BookOuterClass.BookRequest) request,
              (io.grpc.stub.StreamObserver<book.BookOuterClass.BookResponse>) responseObserver);
          break;
        case METHODID_LIST_BOOKS:
          serviceImpl.listBooks((book.BookOuterClass.Empty) request,
              (io.grpc.stub.StreamObserver<book.BookOuterClass.BookListResponse>) responseObserver);
          break;
        case METHODID_ADD_BOOK:
          serviceImpl.addBook((book.BookOuterClass.NewBookRequest) request,
              (io.grpc.stub.StreamObserver<book.BookOuterClass.BookResponse>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        default:
          throw new AssertionError();
      }
    }
  }

  public static final io.grpc.ServerServiceDefinition bindService(AsyncService service) {
    return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
        .addMethod(
          getGetBookMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              book.BookOuterClass.BookRequest,
              book.BookOuterClass.BookResponse>(
                service, METHODID_GET_BOOK)))
        .addMethod(
          getListBooksMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              book.BookOuterClass.Empty,
              book.BookOuterClass.BookListResponse>(
                service, METHODID_LIST_BOOKS)))
        .addMethod(
          getAddBookMethod(),
          io.grpc.stub.ServerCalls.asyncUnaryCall(
            new MethodHandlers<
              book.BookOuterClass.NewBookRequest,
              book.BookOuterClass.BookResponse>(
                service, METHODID_ADD_BOOK)))
        .build();
  }

  private static abstract class BookServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    BookServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return book.BookOuterClass.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("BookService");
    }
  }

  private static final class BookServiceFileDescriptorSupplier
      extends BookServiceBaseDescriptorSupplier {
    BookServiceFileDescriptorSupplier() {}
  }

  private static final class BookServiceMethodDescriptorSupplier
      extends BookServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    BookServiceMethodDescriptorSupplier(String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (BookServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new BookServiceFileDescriptorSupplier())
              .addMethod(getGetBookMethod())
              .addMethod(getListBooksMethod())
              .addMethod(getAddBookMethod())
              .build();
        }
      }
    }
    return result;
  }
}
