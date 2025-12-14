package org.example.grpc;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import java.io.IOException;

/**
 * Cross-Language gRPC Server
 * Java server that can be accessed by clients in any language
 */
public class CrossLanguageServer {
    
    /**
     * Start the gRPC server
     */
    public static void main(String[] args) throws IOException, InterruptedException {
        Server server = ServerBuilder
                .forPort(50053)
                .addService(new BookServiceImpl())
                .build();

        System.out.println("Cross-Language Book Server (Java) started on port 50053");
        System.out.println("Ready to accept connections from Python clients...");
        
        server.start();
        server.awaitTermination();
    }
}
