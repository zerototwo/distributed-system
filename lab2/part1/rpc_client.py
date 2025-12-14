import xmlrpc.client

# create proxy
server = xmlrpc.client.ServerProxy("http://localhost:8000/")

print("5 + 3 =", server.add(5, 3))
print("5 - 3 =", server.subtract(5, 3))
print("5 * 3 =", server.multiply(5, 3))
print("5 / 0 =", server.divide(5, 0))   # 测试异常

