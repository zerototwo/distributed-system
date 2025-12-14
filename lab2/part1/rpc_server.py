from xmlrpc.server import SimpleXMLRPCServer

# 定义远程函数
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y

# 创建服务器
server = SimpleXMLRPCServer(("localhost", 8000))
print("RPC Server listening on port 8000...")

# 注册函数
server.register_function(add, "add")
server.register_function(subtract, "subtract")
server.register_function(multiply, "multiply")
server.register_function(divide, "divide")

# 启动服务
server.serve_forever()