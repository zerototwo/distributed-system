"""Calculator Service gRPC Server Implementation"""

from concurrent import futures
import grpc
import calculator_pb2
import calculator_pb2_grpc


class CalculatorService(calculator_pb2_grpc.CalculatorServiceServicer):
    """Calculator Service implementation for arithmetic operations"""
    
    def Add(self, request, context):
        """Add two numbers"""
        result = request.a + request.b
        return calculator_pb2.CalculatorResponse(result=result)

    def Subtract(self, request, context):
        """Subtract two numbers"""
        result = request.a - request.b
        return calculator_pb2.CalculatorResponse(result=result)

    def Multiply(self, request, context):
        """Multiply two numbers"""
        result = request.a * request.b
        return calculator_pb2.CalculatorResponse(result=result)

    def Divide(self, request, context):
        """Divide two numbers with zero-division error handling"""
        if request.b == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Division by zero is not allowed')
            return calculator_pb2.CalculatorResponse()
        
        result = request.a / request.b
        return calculator_pb2.CalculatorResponse(result=result)


def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServiceServicer_to_server(CalculatorService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Calculator Server started on port 50052")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
