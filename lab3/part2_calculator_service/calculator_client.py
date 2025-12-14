"""Calculator Service gRPC Client Implementation"""

import grpc
import calculator_pb2
import calculator_pb2_grpc


def run():
    """Demonstrate Calculator Service operations"""
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = calculator_pb2_grpc.CalculatorServiceStub(channel)
        
        print("=== Calculator Service Client Demo ===")
        
        # Test Add operation
        print("\n1. Addition:")
        add_request = calculator_pb2.CalculatorRequest(a=10, b=5)
        add_response = stub.Add(add_request)
        print(f"   {add_request.a} + {add_request.b} = {add_response.result}")
        
        # Test Subtract operation
        print("\n2. Subtraction:")
        subtract_request = calculator_pb2.CalculatorRequest(a=10, b=3)
        subtract_response = stub.Subtract(subtract_request)
        print(f"   {subtract_request.a} - {subtract_request.b} = {subtract_response.result}")
        
        # Test Multiply operation
        print("\n3. Multiplication:")
        multiply_request = calculator_pb2.CalculatorRequest(a=4, b=7)
        multiply_response = stub.Multiply(multiply_request)
        print(f"   {multiply_request.a} * {multiply_request.b} = {multiply_response.result}")
        
        # Test Divide operation (normal case)
        print("\n4. Division (normal case):")
        divide_request = calculator_pb2.CalculatorRequest(a=15, b=3)
        divide_response = stub.Divide(divide_request)
        print(f"   {divide_request.a} / {divide_request.b} = {divide_response.result}")
        
        # Test division by zero (error case)
        print("\n5. Division by zero (error handling):")
        try:
            zero_divide_request = calculator_pb2.CalculatorRequest(a=10, b=0)
            zero_divide_response = stub.Divide(zero_divide_request)
            print(f"   {zero_divide_request.a} / {zero_divide_request.b} = {zero_divide_response.result}")
        except grpc.RpcError as e:
            print(f"   Error: {e.details()}")
        
        print("\n=== Demo Complete ===")


if __name__ == '__main__':
    run()
