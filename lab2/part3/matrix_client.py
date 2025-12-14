import xmlrpc.client

server = xmlrpc.client.ServerProxy("http://localhost:8001/")

A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]

print("Matrix A:", A)
print("Matrix B:", B)
print("Result:", server.multiplyMatrices(A, B))